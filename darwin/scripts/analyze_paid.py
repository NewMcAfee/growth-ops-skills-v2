# -*- coding: utf-8 -*-
"""
darwin/analyze_paid.py — motor determinístico de análise de campeões Google Ads.

Princípio: o LLM NÃO processa dado bruto. Este script faz parse + agregação +
ranking + extração de DNA de anúncio, e emite um JSON COMPACTO que o darwin (LLM)
lê para fazer a camada SEMÂNTICA (clustering de intenção, curadoria de negativas,
narrativa de campeões, mapa intenção→campanha). NÃO classifica clusters nem decide
negativas finais — isso é trabalho do LLM.

Uso:
  python analyze_paid.py --terms <termos.csv> [--ads <anuncios.csv>] --out <champion-raw.json>
                         [--conv-col "Conversões"] [--top 40]

Robusto a: encoding (UTF-8 / UTF-8-BOM / Latin-1), formato numérico BR
(decimal vírgula, milhar ponto), variação de nomes de coluna PT do Google Ads,
relatórios grandes (streaming por linha).
"""
import csv, json, re, argparse, sys, io
from collections import defaultdict, Counter

# ---------------- parsing helpers ----------------
def read_rows(path):
    """Lê CSV detectando encoding. Retorna (headers, list[dict])."""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with io.open(path, "r", encoding=enc, newline="") as f:
                sample = f.read(4096); f.seek(0)
                # alguns exports usam ; — detecta
                delim = ";" if (sample.count(";") > sample.count(",")) else ","
                rdr = csv.DictReader(f, delimiter=delim)
                rows = [dict(r) for r in rdr]
            # sucesso se não houver caractere de replacement em massa
            if not any("�" in (k or "") for k in (rows[0].keys() if rows else [])):
                return (list(rows[0].keys()) if rows else []), rows
        except (UnicodeDecodeError, LookupError):
            continue
    # fallback final
    with io.open(path, "r", encoding="latin-1", newline="") as f:
        rdr = csv.DictReader(f)
        rows = [dict(r) for r in rdr]
    return (list(rows[0].keys()) if rows else []), rows

def num(s):
    if s is None: return 0.0
    t = str(s).strip()
    if t in ("", "--", "-", "—"): return 0.0
    t = t.replace("R$", "").replace("%", "").strip()
    # BR: ponto = milhar, vírgula = decimal -> remove pontos, vírgula->ponto
    t = t.replace(".", "").replace(",", ".")
    t = re.sub(r"[^0-9.\-]", "", t)
    try: return float(t) if t not in ("", "-", ".") else 0.0
    except ValueError: return 0.0

def find_col(headers, *needles):
    """Retorna o 1º header que contém (case-insensitive) qualquer needle."""
    low = {h: (h or "").lower() for h in headers}
    for n in needles:
        n = n.lower()
        for h in headers:
            if n in low[h]: return h
    return None

# regex de hints de desperdício (apenas SUGESTÕES — LLM cura o final)
WASTE_HINTS = {
    "free_intent": re.compile(r"\b(gr[áa]tis|gratuito|gratis|free|planilha|excel|modelo|download|baixar|pdf|apostila)\b", re.I),
    "login_cliente": re.compile(r"\b(login|entrar|acessar|acesso|painel|portal)\b", re.I),
    "emprego": re.compile(r"\b(vaga|vagas|emprego|sal[áa]rio|curr[íi]culo|trabalhe)\b", re.I),
    "pirata": re.compile(r"\b(crack|crackeado|pirat|torrent|serial|ativador)\b", re.I),
    "info_pura": re.compile(r"\b(o que [ée]|como funciona|significado|wikipedia|reclame aqui)\b", re.I),
}

# ---------------- terms ----------------
def analyze_terms(path, conv_col_override=None, top=40):
    headers, rows = read_rows(path)
    c_term = find_col(headers, "termo de pesquisa", "termo", "search term", "keyword")
    c_cost = find_col(headers, "custo", "cost")
    c_conv = conv_col_override or find_col(headers, "conversõ", "converso", "conversi", "conv.")
    c_impr = find_col(headers, "impr")
    c_match = find_col(headers, "tipo de corresp", "match type", "corresp")
    c_camp = find_col(headers, "campanha", "campaign")
    if not c_term:
        raise SystemExit("ERRO: coluna de termo não encontrada. Headers: %s" % headers)

    agg = defaultdict(lambda: {"cost":0.0,"conv":0.0,"impr":0.0,"n":0,"match":Counter(),"camp":Counter()})
    tot = {"cost":0.0,"conv":0.0,"impr":0.0,"rows":0}
    for r in rows:
        term = (r.get(c_term) or "").strip().lower()
        if not term: continue
        cost=num(r.get(c_cost)); conv=num(r.get(c_conv)); impr=num(r.get(c_impr))
        a=agg[term]; a["cost"]+=cost; a["conv"]+=conv; a["impr"]+=impr; a["n"]+=1
        if c_match and r.get(c_match): a["match"][r[c_match].strip()]+=1
        if c_camp and r.get(c_camp): a["camp"][r[c_camp].strip()[:60]]+=1
        tot["cost"]+=cost; tot["conv"]+=conv; tot["impr"]+=impr; tot["rows"]+=1

    terms=[]
    for t,a in agg.items():
        cpa=(a["cost"]/a["conv"]) if a["conv"]>0 else None
        hints=[k for k,rx in WASTE_HINTS.items() if rx.search(t)]
        terms.append({"term":t,"cost":round(a["cost"],2),"conv":round(a["conv"],2),
                      "cpa":round(cpa,2) if cpa else None,"impr":int(a["impr"]),
                      "match":a["match"].most_common(1)[0][0] if a["match"] else None,
                      "campaign":a["camp"].most_common(1)[0][0] if a["camp"] else None,
                      "waste_hints":hints})
    prod_cost=sum(t["cost"] for t in terms if t["conv"]>0)
    champions=sorted([t for t in terms if t["conv"]>0], key=lambda x:(-x["conv"],-(x["cost"])))
    waste=sorted([t for t in terms if t["conv"]==0 and t["cost"]>0], key=lambda x:-x["cost"])
    waste_total=round(sum(t["cost"] for t in waste),2)
    match_break=Counter()
    for a in agg.values():
        for m,c in a["match"].items(): match_break[m]+=c
    return {
        "blended":{"cost":round(tot["cost"],2),"conv":round(tot["conv"],2),
                   "cp_conv":round(tot["cost"]/tot["conv"],2) if tot["conv"]>0 else None,
                   "impr":int(tot["impr"]),"unique_terms":len(agg),"rows":tot["rows"],
                   "productive_spend":round(prod_cost,2),
                   "productive_spend_pct":round(100*prod_cost/tot["cost"],1) if tot["cost"]>0 else 0},
        "champions_top":champions[:top],
        "waste_top":waste[:top],
        "waste_total":waste_total,
        "waste_pct":round(100*waste_total/tot["cost"],1) if tot["cost"]>0 else 0,
        "match_breakdown":dict(match_break),
        "columns_used":{"term":c_term,"cost":c_cost,"conv":c_conv,"impr":c_impr,"match":c_match},
    }

# ---------------- ads ----------------
def analyze_ads(path, conv_col_override=None, top=15):
    headers, rows = read_rows(path)
    c_cost=find_col(headers,"custo","cost"); c_conv=conv_col_override or find_col(headers,"conversõ","converso","conv.")
    c_clk=find_col(headers,"cliques","clicks"); c_impr=find_col(headers,"impr"); c_ctr=find_col(headers,"ctr")
    c_status=find_col(headers,"status do anúncio","status do anuncio","ad status","status")
    c_camp=find_col(headers,"campanha","campaign"); c_ag=find_col(headers,"grupo de anúncio","grupo de anuncio","ad group")
    c_url=find_col(headers,"url final","final url")
    h_cols=[h for h in headers if re.match(r"^t[íi]tulo\s*\d+$", (h or "").strip(), re.I) or re.match(r"^headline\s*\d+$",(h or "").strip(),re.I)]
    d_cols=[h for h in headers if re.match(r"^descri[çc][ãa]o\s*\d+$",(h or "").strip(),re.I) or re.match(r"^description\s*\d+$",(h or "").strip(),re.I)]

    ads=[]; head_freq=Counter(); desc_freq=Counter()
    for r in rows:
        cost=num(r.get(c_cost)); conv=num(r.get(c_conv))
        heads=[(r.get(h) or "").strip() for h in h_cols if (r.get(h) or "").strip() not in ("","--")]
        descs=[(r.get(d) or "").strip() for d in d_cols if (r.get(d) or "").strip() not in ("","--")]
        ad={"status":(r.get(c_status) or "").strip(),"campaign":(r.get(c_camp) or "").strip()[:50],
            "ad_group":(r.get(c_ag) or "").strip(),"cost":round(cost,2),"conv":round(conv,2),
            "cpa":round(cost/conv,2) if conv>0 else None,"ctr":r.get(c_ctr,""),
            "clicks":int(num(r.get(c_clk))),"impr":int(num(r.get(c_impr))),
            "url":(r.get(c_url) or "").strip(),"headlines":heads,"descriptions":descs}
        ads.append(ad)
        if conv>0:  # DNA = só de anúncios que converteram
            for h in heads: head_freq[h]+=1
            for d in descs: desc_freq[d]+=1
    champions=sorted([a for a in ads if a["conv"]>0], key=lambda x:(-x["conv"], x["cpa"] or 9e9))
    return {
        "total_ads":len(ads),
        "champions_top":champions[:top],
        "dna_headlines":[{"text":t,"freq":n} for t,n in head_freq.most_common(25)],
        "dna_descriptions":[{"text":t,"freq":n} for t,n in desc_freq.most_common(15)],
        "columns_used":{"cost":c_cost,"conv":c_conv,"headline_cols":len(h_cols),"desc_cols":len(d_cols)},
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--terms",required=True); ap.add_argument("--ads",default=None)
    ap.add_argument("--out",required=True); ap.add_argument("--conv-col",default=None)
    ap.add_argument("--top",type=int,default=40)
    a=ap.parse_args()
    out={"terms":analyze_terms(a.terms,a.conv_col,a.top)}
    if a.ads: out["ads"]=analyze_ads(a.ads,a.conv_col)
    with io.open(a.out,"w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=1)
    b=out["terms"]["blended"]
    print(f"OK termos: {b['unique_terms']} únicos | gasto R$ {b['cost']:.2f} | conv {b['conv']:.1f} | "
          f"CP-conv R$ {b['cp_conv']} | desperdício {out['terms']['waste_pct']}% (R$ {out['terms']['waste_total']:.2f})")
    if "ads" in out:
        print(f"OK anúncios: {out['ads']['total_ads']} | DNA: {len(out['ads']['dna_headlines'])} títulos + {len(out['ads']['dna_descriptions'])} descrições recorrentes")
    print(f"-> {a.out}")

if __name__=="__main__": main()
