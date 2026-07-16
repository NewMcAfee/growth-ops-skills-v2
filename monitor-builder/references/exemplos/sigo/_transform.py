# -*- coding: utf-8 -*-
# =============================================================================
# _transform.py — Sigo ERP · dados-fonte 2.0 · estágio TRANSFORM da cadeia
# Decisão: 30-decisoes/2026-07-09-dados-fonte-v2.md · Manifesto: contrato-dados-fonte.yml
#
# Lê raw/ (só o feed escreve lá) e materializa derivado/ (só ESTE script
# escreve lá; humano nunca edita). Skills e o render consomem derivado/.
#
# Outputs:
#   derivado/fato-ads-enriquecido.csv — bd_ads × index × CRM: os joins que a
#       planilha fazia por fórmula (cortadas na origem em 2026-07-09). Funil
#       por ÂNCORA SAFRA (evento conta no dia de CRIAÇÃO do lead — engenharia
#       reversa da fórmula validada por golden test vs planilha congelada:
#       cli e fat com diferença ZERO). Sem PII -> commitável.
#   derivado/qa-report.json — achados dos gates do contrato (dedups, órfãos,
#       sentinela). Sem PII -> commitável.
#
# WARNs em stdout (stderr mata a cadeia no PS 5.1). Falha aqui NÃO derruba o
# render: o gerador usa o último derivado bom (degrada com WARN).
#
# Este módulo também é a BIBLIOTECA de helpers de parsing (br_num/pdate/...)
# importada pelo _gerar-monitor.py — 1 fonte de verdade, sem drift.
# =============================================================================
import csv, json, re
from datetime import datetime, date, timedelta
from pathlib import Path

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
DERIV = BASE / "derivado"
CAMP = RAW / "campanhas-completo.csv"
INDEX = RAW / "index-anuncios-completo.csv"
CRM = RAW / "crm-completo.csv"
FATO = DERIV / "fato-ads-enriquecido.csv"
DIMCRT = DERIV / "dim-criativo.csv"
QA_OUT = DERIV / "qa-report.json"
TAXONOMIA = BASE.parent.parent / "10-fundacao" / "taxonomia.yml"
MIN_ANO = 2024   # base completa tem outliers de data (1999/2023) — descarta lixo pré-2024

# --- parsing (fonte única — o gerador importa daqui) ---------------------------
def br_num(s):
    if s is None: return 0.0
    s = str(s).strip().replace("R$", "").replace("%", "").replace("\xa0", "")
    s = s.replace(".", "").replace(",", ".").strip()
    if s in ("", "-", "—"): return 0.0
    try: return float(s)
    except ValueError: return 0.0

def br_int(s): return int(round(br_num(s)))

def pdate(s):
    if not s: return None
    s = str(s).strip()
    if not s or s.endswith("%"): return None
    # serial date do Sheets/Excel (epoch 1899-12-30): parte das linhas do
    # leads_pipeline vem como número (ex "46186") em vez de dd/mm/yyyy.
    try:
        n = float(s.replace(",", "."))
        if 30000 <= n <= 80000:
            return date(1899, 12, 30) + timedelta(days=int(n))
    except ValueError:
        pass
    try: return datetime.strptime(s[:10], "%d/%m/%Y").date()
    except ValueError: return None

def iso(d): return d.strftime("%Y-%m-%d") if d else ""

def istrue(s): return str(s or "").strip().upper() == "TRUE"

def canal_norm(c):
    c = (c or "").strip().lower()
    if "meta" in c or "facebook" in c or c in ("fb", "ig", "instagram"): return "meta"
    if "google" in c or "gads" in c or "gdn" in c: return "google"
    if "organic" in c or "orgânico" in c: return "organico"   # index usa "organic"; CSV legado usava "ORGANICO"
    return c or "—"

# --- taxonomia: parser de nomenclatura (F5) --------------------------------------
# Patterns vivem em 10-fundacao/taxonomia.yml (donos: media-buyer-*). Gerações
# em ordem — primeira que casa vence; sem match = geracao "legado" (campos
# vazios, nunca quebra). Sem taxonomia.yml o parse desliga com WARN.
TEMPS = ("Frio", "Morno", "Quente")

def taxo_parsers():
    try:
        import yaml
        t = yaml.safe_load(TAXONOMIA.read_text(encoding="utf-8")) or {}
        ents = t.get("nomenclatura_entidades") or {}
        return {ent: [(g["id"], re.compile(g["pattern"]))
                      for g in (ents.get(ent) or {}).get("geracoes") or [] if g.get("pattern")]
                for ent in ("campanha", "conjunto", "anuncio")}
    except Exception as e:
        print(f"WARN: taxonomia.yml indisponível ({e}) — parse de nomenclatura desligado.")
        return {"campanha": [], "conjunto": [], "anuncio": []}

def parse_nome(patterns, nome):
    nome = (nome or "").strip()
    for gid, rx in patterns:
        m = rx.match(nome)
        if m:
            d = {k: (v or "") for k, v in m.groupdict().items()}
            d["geracao"] = gid
            return d
    return {"geracao": "legado"}

def parse_campanha(patterns, nome):
    """campo5 da campanha só vira `temp` se ∈ vocab; senão é `variante` +
    marca fora-de-vocab (feedback pro media-buyer via qa-report)."""
    d = parse_nome(patterns, nome)
    c5 = d.pop("campo5", "")
    if c5 in TEMPS:
        d["temp"] = c5
    elif c5:
        d["variante"], d["temp_fora_vocab"] = c5, True
    return d

# --- QA (gates do contrato-dados-fonte.yml) ------------------------------------
_QA = []
def qa(nivel, check, msg, **extra):
    _QA.append({"nivel": nivel, "check": check, "msg": msg, **extra})
    print(f"{'WARN QA' if nivel == 'warn' else 'QA'}: {msg}")

# --- cargas --------------------------------------------------------------------
def load_index(verbose=True):
    """Dimensão de anúncios (bd_campaing_index): ad_id -> canal + nomes.
    Gate: ad_id duplicado explodiria o join. Dup IDÊNTICO = benigno (index
    legado tem linha por keyword); dup DIVERGENTE = conflito real -> WARN.
    verbose=False p/ consumo do gerador (QA já registrado pelo transform)."""
    idx, benign, conflict = {}, 0, set()
    if not INDEX.exists():
        if verbose:
            qa("warn", "index_ausente", "index-anuncios-completo.csv ausente — nomes/canal só pelo fallback do CSV legado.")
        return idx
    with open(INDEX, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ad = (r.get("ad_id") or "").strip()
            if not ad: continue
            row = {"canal": canal_norm(r.get("canal")),
                   "campanha": (r.get("nome_campanha") or "—").strip() or "—",
                   "conjunto": (r.get("nome_conjunto") or "—").strip() or "—",
                   "anuncio": (r.get("nome_anuncio") or "—").strip() or "—"}
            if ad in idx:
                if row == idx[ad]: benign += 1
                else: conflict.add(ad)
                continue
            idx[ad] = row
    if conflict and verbose:
        qa("warn", "index_ad_id_conflitante",
           f"{len(conflict)} ad_id com variantes CONFLITANTES no index (keep-first) — corrigir na origem.",
           ad_ids=sorted(conflict)[:20])
    if benign and verbose:
        qa("info", "index_dup_identico", f"{benign} linha(s) duplicada(s) idêntica(s) no index (benigno, keep-first).")
    return idx

def load_crm(verbose=True):
    """CRM (leads_pipeline). Gate: deal_growthpack_id duplicado infla
    funil/receita -> keep-first. verbose=False p/ consumo do gerador
    (o achado já foi registrado pelo transform na mesma rodada)."""
    rows, seen, dups = [], set(), []
    with open(CRM, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (r.get("deal_growthpack_id") or "").strip()
            if k:
                if k in seen:
                    dups.append(k); continue
                seen.add(k)
            rows.append(r)
    if dups and verbose:
        qa("warn", "crm_deal_duplicado",
           f"{len(dups)} deal_growthpack_id duplicado(s) no CRM (keep-first) — corrigir na origem.",
           deals=dups[:20])
    return rows

def derive_funil(crm):
    """Reconstrói o cruzamento bd_ads × leads_pipeline (fórmula cortada
    2026-07-09): eventos por (ad_id, data de CRIAÇÃO do lead) — ÂNCORA SAFRA.
    fat = total_value cru dos wins, igual à fórmula (valor limpo mens+impl
    vive no bloco `vendas` do monitor.json)."""
    m = {}
    for r in crm:
        cd = pdate(r.get("create_at"))
        if not cd or cd.year < MIN_ANO: continue
        k = ((r.get("ad_id") or "").strip(), cd)
        e = m.setdefault(k, {"lead": 0, "sal": 0, "sql": 0, "demo_ag": 0,
                             "demo_re": 0, "cli": 0, "fat": 0.0})
        e["lead"] += 1
        if istrue(r.get("sal")): e["sal"] += 1
        if istrue(r.get("sql")): e["sql"] += 1
        if istrue(r.get("scheduled_meeting")): e["demo_ag"] += 1
        if istrue(r.get("show_meeting")): e["demo_re"] += 1
        if istrue(r.get("win")):
            e["cli"] += 1
            e["fat"] += br_num(r.get("total_value"))
    return m

def build_fato(idx, funil):
    """bd_ads (métricas nativas) + index (nomes/canal) + funil (safra).
    Gates: dia×anúncio duplicado (keep-first) · órfão de index (fallback CSV
    legado) · sentinela 12/08/1999 (canário do export — ALERTA se sumir)."""
    rows, seen = [], set()
    dup = orf = 0
    sentinela = False
    with open(CAMP, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ad = (r.get("ad_id") or "").strip()
            d = pdate(r.get("data"))
            if ad == "manual" and d and d.year == 1999:
                sentinela = True
            if not d or d.year < MIN_ANO: continue
            if (ad, d) in seen:
                dup += 1; continue
            seen.add((ad, d))
            ix = idx.get(ad)
            if ix is None:
                orf += 1
                ix = {"canal": canal_norm(r.get("canal")),
                      "campanha": (r.get("nome_campanha") or "—").strip() or "—",
                      "conjunto": (r.get("nome_conjunto") or "—").strip() or "—",
                      "anuncio": (r.get("nome_anuncio") or "—").strip() or "—"}
            fu = funil.get((ad, d), {})
            rows.append({
                "data": iso(d), "ad_id": ad,
                "canal": ix["canal"], "campanha": ix["campanha"],
                "conjunto": ix["conjunto"], "anuncio": ix["anuncio"],
                "investimento": round(br_num(r.get("investimento")), 2),
                "impressoes": br_int(r.get("impressões") or r.get("impressoes")),
                "clicks": br_int(r.get("ad_clicks")),
                "alcance": br_int(r.get("alcance")),
                "lead": fu.get("lead", 0),
                "sal": fu.get("sal", 0),
                "sql": fu.get("sql", 0),
                "demo_ag": fu.get("demo_ag", 0),
                "demo_re": fu.get("demo_re", 0),
                "cli": fu.get("cli", 0),
                "fat": round(fu.get("fat", 0.0), 2),
            })
    if not sentinela:
        qa("warn", "sentinela_ausente",
           "linha-sentinela (ad_id=manual, 1999) AUSENTE do bd_ads — checar export/planilha na origem!")
    if dup:
        qa("warn", "bd_ads_dia_anuncio_duplicado",
           f"{dup} linha(s) dia×anúncio duplicada(s) no bd_ads (keep-first) — corrigir na origem.")
    if orf:
        qa("info", "bd_ads_orfao_index", f"{orf} linha(s) com ad_id órfão de index (fallback CSV legado).")
    return rows

FATO_COLS = ["data", "ad_id", "canal", "campanha", "conjunto", "anuncio",
             "investimento", "impressoes", "clicks", "alcance",
             "lead", "sal", "sql", "demo_ag", "demo_re", "cli", "fat"]

# --- dim-criativo (F5): atributos parseados + copy/CTA do flow --------------------
DIMCRT_COLS = ["ad_id", "canal", "nome_campanha", "nome_conjunto", "nome_anuncio",
               "geracao", "seq", "formato", "consciencia", "gancho", "avatar", "variacao",
               "narrativa", "drop", "placement",
               "conj_funil", "conj_tipo", "conj_publico", "conj_geo", "conj_demo",
               "camp_status", "camp_obj", "camp_produto", "camp_temp", "camp_variante",
               "creative_id", "copy_title", "copy_body", "copy_cta"]

def _load_flow_copy():
    """ad_id -> {creative_id, title, body, cta} via flow-meta-ads + flow-meta-criativos.
    Arquivos opcionais (extração das segundas); dedup do criativo = keep-LAST
    (Nekt guarda versões; a última linha é a mais recente)."""
    ads_f, crt_f = RAW / "flow-meta-ads.csv", RAW / "flow-meta-criativos.csv"
    if not ads_f.exists():
        return {}
    crt = {}
    if crt_f.exists():
        with open(crt_f, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cid = (r.get("creative_id") or "").strip()
                if cid:
                    crt[cid] = r   # keep-last
    out = {}
    with open(ads_f, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ad = (r.get("ad_id") or "").strip()
            cid = (r.get("creative_id") or "").strip()
            if not ad: continue
            c = crt.get(cid, {})
            out[ad] = {"creative_id": cid, "copy_title": (c.get("title") or "").strip(),
                       "copy_body": (c.get("body") or "").strip()[:500],
                       "copy_cta": (c.get("call_to_action_type") or "").strip()}
    return out

def build_dim_criativo(idx):
    """Materializa derivado/dim-criativo.csv: 1 linha por ad_id do index, com
    atributos parseados da nomenclatura (taxonomia gia-v2) + copy do flow.
    QA: cobertura por geração + campanhas com temperatura fora de vocab."""
    taxo = taxo_parsers()
    fcopy = _load_flow_copy()
    rows, ger = [], {}
    fora_vocab = set()
    for ad, ix in idx.items():
        an = parse_nome(taxo["anuncio"], ix["anuncio"])
        cj = parse_nome(taxo["conjunto"], ix["conjunto"])
        cp = parse_campanha(taxo["campanha"], ix["campanha"])
        ger[an["geracao"]] = ger.get(an["geracao"], 0) + 1
        if cp.pop("temp_fora_vocab", False):
            fora_vocab.add(ix["campanha"])
        fc = fcopy.get(ad, {})
        rows.append({
            "ad_id": ad, "canal": ix["canal"],
            "nome_campanha": ix["campanha"], "nome_conjunto": ix["conjunto"], "nome_anuncio": ix["anuncio"],
            "geracao": an.get("geracao", ""), "seq": an.get("seq", ""), "formato": an.get("formato", ""),
            "consciencia": an.get("consciencia", ""), "gancho": an.get("gancho", ""),
            "avatar": an.get("avatar", ""), "variacao": an.get("variacao", ""),
            "narrativa": an.get("narrativa", ""), "drop": an.get("drop", ""), "placement": an.get("placement", ""),
            "conj_funil": cj.get("funil", ""), "conj_tipo": cj.get("tipo", ""),
            "conj_publico": cj.get("publico", ""), "conj_geo": cj.get("geo", ""), "conj_demo": cj.get("demo", ""),
            "camp_status": cp.get("status", ""), "camp_obj": cp.get("obj", ""),
            "camp_produto": cp.get("produto", ""), "camp_temp": cp.get("temp", ""),
            "camp_variante": cp.get("variante", ""),
            "creative_id": fc.get("creative_id", ""), "copy_title": fc.get("copy_title", ""),
            "copy_body": fc.get("copy_body", ""), "copy_cta": fc.get("copy_cta", ""),
        })
    parseados = sum(v for k, v in ger.items() if k != "legado")
    qa("info", "dim_criativo_cobertura",
       f"dim-criativo: {len(rows)} ads · parseados {parseados} ({ger}) · copy do flow em {sum(1 for r in rows if r['creative_id'])}.")
    if fora_vocab:
        qa("warn", "campanha_temp_fora_vocab",
           f"{len(fora_vocab)} campanha(s) gia-v2 com 5º campo fora do vocab de temperatura (tema no lugar de Frio/Morno/Quente) — corrigir naming (media-buyer).",
           campanhas=sorted(fora_vocab)[:10])
    return rows

def main():
    if not CAMP.exists() or not CRM.exists():
        print("ERRO transform: raw/ incompleto (campanhas/crm ausente). Rode o feed primeiro.")
        raise SystemExit(1)
    DERIV.mkdir(exist_ok=True)
    crm = load_crm(verbose=True)
    idx = load_index()
    rows = build_fato(idx, derive_funil(crm))
    with open(FATO, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FATO_COLS)
        w.writeheader()
        w.writerows(rows)
    dim = build_dim_criativo(idx)
    with open(DIMCRT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=DIMCRT_COLS)
        w.writeheader()
        w.writerows(dim)
    QA_OUT.write_text(json.dumps(
        {"gerado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "linhas_fato": len(rows), "achados": _QA},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"transform ok · {len(rows)} linhas fato · {len(dim)} ads na dim-criativo · {len(_QA)} achado(s) QA · {FATO.name} + {DIMCRT.name} + {QA_OUT.name}")

if __name__ == "__main__":
    main()
