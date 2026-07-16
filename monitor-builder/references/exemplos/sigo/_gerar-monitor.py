# -*- coding: utf-8 -*-
# =============================================================================
# _gerar-monitor.py — Sigo ERP · Monitor de Aquisição (cockpit do gestor) · v3
# -----------------------------------------------------------------------------
# Lê os 2 CSVs do feed e gera monitor.html AUTO-CONTIDO com TELAS + FILTROS.
# v2: emite dados GRANULARES (campanha diária sem PII + leads só com campos
# analíticos — sem nome/email/telefone/CNPJ) e a AGREGAÇÃO roda no JS, pra os
# filtros (Período / Canal) recalcularem ao vivo. O OKR do quarter é fixo
# (meta por trimestre, todos os canais) e vai pré-computado.
#
# CRM = verdade (lead -> venda). campanhas = a mesma verdade fatiada por anúncio.
# Saída embute dados do CRM -> git-ignored. Roda no fim do feed.
#
# v3: emite TAMBÉM monitor.json (mesmo payload P do HTML) p/ skills de análise
# consumirem — camada determinística produz o dado, camada cognitiva consome
# (contrato em references/contrato-snapshot.md). Metas lidas em runtime do
# contrato-cockpit.yml (troca de quarter sem tocar código; fallback gracioso
# pro META_DEFAULT se pyyaml/contrato faltarem — o feed nunca quebra).
#
# v4 (retrofit padrão monitor-builder v2.1 — Martins/Colina, 2026-07-02):
#  - VIGÊNCIA de meta: `quarter_vigencia` do contrato define a janela do placar
#    (não mais o quarter civil de hoje). Virada de quarter NÃO trava o render:
#    o placar pro-rateia/esconde meta no cliente (esconder > mentir).
#  - OKR do monitor.json passa a medir a JANELA DE VIGÊNCIA (antes: quarter civil).
#  - Reconciliação CRM×campanhas: eventos de funil do CRM sem match de ad_id
#    (~5%) são distribuídos proporcionalmente às linhas dia×anúncio do mesmo
#    mês×canal, pela participação da linha no evento (fallback: share de
#    investimento; sem base → fica sem alocar). Só canais pagos presentes no
#    campanhas; só VOLUME (sal/demos/clientes) — valor NÃO se reconcilia
#    (fórmulas de valor divergem entre as fontes). Conservação no stdout.
#    Bloco `resid` é ADITIVO no monitor.json (camp.rows continuam crus do CSV).
#  - WARNs informativos vão pra STDOUT (stderr redirecionado vira exceção no
#    PowerShell 5.1 do feed e matava o render). Só erro fatal usa stderr.
#
# Definições canônicas (confirmadas):
#   MQL operacional = SAL (flag `sal`) · `mql` do CRM = qualif. do form.
#   Demo realizada  = show_meeting (data show_meeting_at) · META 92/mês.
#   Close-rate      = Clientes ÷ Demos realizadas. 1 demo/cliente = por lead.
#
# v6 (dados-fonte 2.0 — decisão 30-decisoes/2026-07-09-dados-fonte-v2.md):
#  - As fórmulas de cruzamento do growthpack foram CORTADAS na origem (ELT).
#    O motor reconstrói os 2 joins a partir do bruto:
#    (a) bd_ads × bd_campaing_index por ad_id → canal + nomes (load_index);
#    (b) bd_ads × leads_pipeline por (ad_id, create_at) → funil por linha
#        (derive_funil) — ÂNCORA SAFRA (evento conta no dia de criação do
#        lead), validada por golden test vs planilha congelada @ git HEAD
#        (cli e fat com diferença ZERO; demais eventos diff ≤9 explicado
#        pela evolução do CRM pós-27/06).
#  - QA gates (contrato-dados-fonte.yml): dedup ad_id no index · dedup
#    dia×anúncio no bd_ads · dedup deal_growthpack_id no CRM — keep-first +
#    WARN. Sentinela (ad_id=manual, 12/08/1999) = canário: ALERTA se sumir.
# =============================================================================
import csv, json, sys
from datetime import datetime, date, timedelta
from pathlib import Path

# v6.1: joins/QA vivem no _transform.py (estágio anterior da cadeia); este
# script consome derivado/fato-ads-enriquecido.csv + raw/crm (payload de leads)
# e importa os helpers de parsing de lá (1 fonte de verdade, sem drift).
from _transform import (RAW, DERIV, FATO, MIN_ANO, br_num, br_int, pdate, iso,
                        istrue, canal_norm, load_crm, load_index,
                        taxo_parsers, parse_nome, parse_campanha)

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
TERMS = RAW / "termos-google-completo.csv"
OUT  = BASE / "monitor.html"
OUT_JSON = BASE / "monitor.json"        # snapshot estruturado p/ skills de análise (git-ignored, embute CRM analítico)
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

# --- contrato: metas lidas em runtime (troca de quarter sem tocar código) ----
# Fallback gracioso pro META_DEFAULT se pyyaml ou o contrato faltarem (feed nunca quebra).
META_DEFAULT = {
    "demos_real_mes": 92,   "demos_real_q": 276,
    "demos_agend_mes": 114, "demos_agend_q": 342,
    "sql_semana": 31, "clientes_q": 55, "valor_total_q": 122500,
    "sal_sql_rate": 0.55, "show_rate": 0.75, "close_rate": 0.20, "budget_q": 70000,
    "q1": {"sal_sql": 0.452, "show": 0.668, "close": 0.16},
    "quarter_vigencia": None,
}
def load_contrato_raw():
    # WARNs em stdout: o wrapper .ps1 (PS 5.1) converte stderr em exceção e
    # derrubava o render por aviso benigno.
    try:
        import yaml
    except ImportError:
        print("WARN: pyyaml ausente — META default embutido. `pip install pyyaml` p/ ler o contrato.")
        return {}
    if not CONTRATO.exists():
        print(f"WARN: {CONTRATO.name} ausente — META default embutido.")
        return {}
    try:
        return yaml.safe_load(CONTRATO.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"WARN: contrato ilegível ({e}) — META default.")
        return {}
CONTRATO_RAW = load_contrato_raw()
def load_meta():
    m = CONTRATO_RAW.get("metas", {}) or {}
    if not m:
        return dict(META_DEFAULT)
    tx, base = m.get("taxas", {}) or {}, m.get("baseline_q_anterior", {}) or {}
    dmes, dames = m.get("demos_real_mes", 92), m.get("demos_agend_mes", 114)
    return {
        "demos_real_mes": dmes,   "demos_real_q": m.get("demos_real_q", dmes*3),
        "demos_agend_mes": dames, "demos_agend_q": m.get("demos_agend_q", dames*3),
        "sql_semana": m.get("sql_semana", 31),
        "clientes_q": m.get("clientes_q", 55), "valor_total_q": m.get("valor_total_q", 122500),
        "sal_sql_rate": tx.get("sal_sql", 0.55), "show_rate": tx.get("show", 0.75),
        "close_rate": tx.get("close", 0.20), "budget_q": m.get("budget_q", 70000),
        "q1": {"sal_sql": base.get("sal_sql", 0.452), "show": base.get("show", 0.668),
               "close": base.get("close", 0.16)},
        "quarter_vigencia": m.get("quarter_vigencia"),
    }
META = load_meta()
CANAIS_META = CONTRATO_RAW.get("canais_meta")   # null = metas valem pra todos os canais

# --- qualificadores (v5): campos + normalização lidos do contrato ------------
# Valores da origem vêm com variantes de caixa/grafia ("+5 Obras"/"+5 obras");
# o mapa vive no contrato (editável sem código). Fallback: title-case do valor.
QUAL_CAMPOS = (CONTRATO_RAW.get("qualificadores", {}) or {}).get("campos", {}) or {
    "obras": "qualificador_tamanho", "ferramenta": "qualificador_maturidade",
    "cargo": "qualificador_cargo", "segmento": "segmento", "dor": "qualificador_dor"}
QUAL_NORM = {str(k).strip().lower(): v for k, v in
             ((CONTRATO_RAW.get("qualificadores", {}) or {}).get("normalizacao", {}) or {}).items()}
def qual_norm(campo, v):
    v = str(v or "").strip()
    if not v: return ""
    lv = v.lower()
    if lv in QUAL_NORM: return QUAL_NORM[lv]
    # regra de dado: nº de obras às vezes vem numérico cru ("3","5","8") → bucket
    if campo == "obras":
        try:
            n = int(float(lv.replace(",", ".")))
            return "1-2 obras" if n <= 2 else ("3-5 obras" if n <= 5 else "+5 obras")
        except ValueError:
            pass
    return v[:1].upper() + v[1:]
TGT_CUSTO_DEMO = META["budget_q"] / META["demos_real_q"]   # ~R$253
TGT_CAC        = META["budget_q"] / META["clientes_q"]      # ~R$1.272

# --- quarter -----------------------------------------------------------------
def quarter_bounds(dt):
    q = (dt.month - 1) // 3
    start = date(dt.year, q*3+1, 1)
    em = q*3+3
    nm = date(dt.year + (em//12), (em % 12)+1, 1)
    end = nm - timedelta(days=1)
    return start, end, f"Q{q+1} {dt.year}"
QSTART, QEND, QLABEL = quarter_bounds(HOJE)   # trimestre CIVIL de hoje (presets/rótulos)
QDAYS = (QEND-QSTART).days+1
QELAPSED = max(1, (min(HOJE.date(), QEND)-QSTART).days+1)

# --- vigência das metas (dirigida pelo contrato, não pelo calendário) ---------
# O placar OKR mede a janela de `quarter_vigencia`. Virada de quarter civil não
# bloqueia nada: se o período filtrado não intersecta a vigência, o RENDERER
# esconde a meta (esconder > mentir). Só avisa em stdout quando a vigência venceu.
def parse_quarter_key(k):
    try:
        y, q = str(k).split("-Q"); y, q = int(y), int(q)
    except (ValueError, AttributeError):
        return None
    start = date(y, (q-1)*3+1, 1)
    em = (q-1)*3+3
    nm = date(y + em//12, (em % 12)+1, 1)
    return start, nm - timedelta(days=1), f"Q{q} {y}"
_v = parse_quarter_key(META.get("quarter_vigencia")) or (QSTART, QEND, QLABEL)
VSTART, VEND, VLABEL = _v
VDAYS = (VEND-VSTART).days+1
VELAPSED = min(max(0, (min(HOJE.date(), VEND)-VSTART).days+1), VDAYS)
if HOJE.date() > VEND:
    print(f"INFO: vigência das metas ({VLABEL}) encerrada — placar segue medindo {VLABEL}; "
          f"defina as metas do quarter novo em metas.quarter_vigencia no contrato-cockpit.yml.")
def in_v(d): return d is not None and VSTART <= d <= VEND

# --- carga -------------------------------------------------------------------
def load_fato():
    """Consome derivado/fato-ads-enriquecido.csv — materializado pelo
    _transform.py (joins bd_ads × index × CRM com âncora safra + QA gates).
    Datas ISO e números com ponto (formato do derivado, não da origem BR)."""
    rows = []
    with open(FATO, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "data": datetime.strptime(r["data"], "%Y-%m-%d").date(),
                "ad_id": r["ad_id"], "canal": r["canal"],
                "campanha": r["campanha"], "conjunto": r["conjunto"],
                "anuncio": r["anuncio"],
                "inv": float(r["investimento"] or 0),
                "sal": int(r["sal"] or 0),
                "demo_ag": int(r["demo_ag"] or 0),
                "demo_re": int(r["demo_re"] or 0),
                "cli": int(r["cli"] or 0),
                "fat": float(r["fat"] or 0),
                "impr": int(r["impressoes"] or 0),
                "clicks": int(r["clicks"] or 0),
                "lead": int(r["lead"] or 0),
                "sql": int(r["sql"] or 0),
                "alcance": int(r["alcance"] or 0),
            })
    return rows

def load_config_fin():
    """Config financeiro DECLARADO (F3 — dados-fonte 2.0): config-financeiro.yml
    com blocos de VIGÊNCIA (`de: YYYY-MM` + valores; edita 1 bloco no reajuste).
    O motor expande pra dict mensal — shape do payload `fin` inalterado (render
    não muda). Fallback: config-financeiro.csv legado (1 linha/mês). Regra de
    ouro: aqui só entra o que NÃO existe em nenhum dado (fee, margem, regras);
    o que dá pra calcular do dado é derivado, não config."""
    py_cfg = BASE / "config-financeiro.yml"
    if py_cfg.exists():
        try:
            import yaml
            cfg = yaml.safe_load(py_cfg.read_text(encoding="utf-8")) or {}
            vigs = sorted(cfg.get("vigencias") or [], key=lambda v: str(v.get("de")))
            if vigs:
                fin, cur, i = {}, None, 0
                first = str(vigs[0]["de"])[:7]
                y, m = int(first[:4]), int(first[5:7])
                while (y, m) <= (HOJE.year, HOJE.month):
                    key = f"{y:04d}-{m:02d}"
                    while i < len(vigs) and str(vigs[i]["de"])[:7] <= key:
                        cur = vigs[i]; i += 1
                    mg = float(cur.get("margem") or 0)
                    if mg > 1: mg /= 100.0   # operador digitou em %
                    # custo_tech (CRM, construtor de páginas…) soma nos outros_custos
                    # do DRE — campo separado no YAML pra ficar declarado por nome.
                    oc = float(cur.get("outros_custos") or 0) + float(cur.get("custo_tech") or 0)
                    fin[key] = {"fee": float(cur.get("fee") or 0), "margem": mg,
                                "tcv_meses": float(cur.get("tcv_meses") or 6),
                                "outras_receitas": float(cur.get("outras_receitas") or 0),
                                "outros_custos": oc}
                    m += 1
                    if m > 12: m, y = 1, y + 1
                return fin
        except Exception as e:
            print(f"WARN: config-financeiro.yml ilegível ({e}) — fallback CSV.")
    p = BASE / "config-financeiro.csv"
    fin = {}
    if not p.exists():
        return fin
    with open(p, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m = (r.get("mes") or "").strip()
            if not m:
                continue
            mg = br_num(r.get("margem"))
            if mg > 1:  # operador digitou em %
                mg /= 100.0
            fin[m] = {"fee": br_num(r.get("fee")), "margem": mg,
                      "tcv_meses": br_num(r.get("tcv_meses")) or 6,
                      "outras_receitas": br_num(r.get("outras_receitas")),
                      "outros_custos": br_num(r.get("outros_custos"))}
    return fin

class Interner:
    def __init__(self): self.l=[]; self.m={}
    def idx(self, s):
        if s not in self.m: self.m[s]=len(self.l); self.l.append(s)
        return self.m[s]

def load_termos():
    """Relatório de termos de busca Google Ads (agregado, sem PII, commitável).
    Tolerante: se o arquivo não existe, a seção do monitor some."""
    if not TERMS.exists():
        return None
    cI, aI = Interner(), Interner()
    rows = []
    with open(TERMS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            kw = (r.get("Search keyword") or "").strip()
            if not kw:
                continue
            rows.append([cI.idx((r.get("Campaign Name") or "—").strip()),
                         aI.idx((r.get("Ad Group Name") or "—").strip()), kw,
                         br_int(r.get("Clicks")), br_int(r.get("Impressions")),
                         round(br_num(r.get("Cost (Spend)")), 2), round(br_num(r.get("Conversions")), 1),
                         round(br_num(r.get("Impr. (Top) %")), 2)])   # v5: impression share topo (headroom de escala)
    if not rows:
        return None
    return {"campaigns": cI.l, "adgroups": aI.l,
            "cols": ["camp", "adg", "kw", "clicks", "impr", "cost", "conv", "top"], "rows": rows}

# --- OKR da vigência (janela do contrato, todos canais) -----------------------
# Mantido no monitor.json p/ skills de análise (falconi/growth-review); o placar
# do HTML recalcula no cliente (pro-rata por período/canal filtrado).
def pct(n, d): return (n/d) if d else 0.0
def compute_okr(crm):
    def distinct(field_at):
        seen=set()
        for r in crm:
            d=pdate(r.get(field_at))
            if in_v(d): seen.add((r.get("lead_id") or r.get("deal_growthpack_id") or "").strip())
        seen.discard(""); return len(seen)
    def flagcount(flag, at):
        return sum(1 for r in crm if istrue(r.get(flag)) and in_v(pdate(r.get(at))))
    demos_re=distinct("show_meeting_at"); demos_ag=distinct("scheduled_meeting_at")
    cli=distinct("win_at"); sql=distinct("sql_at")
    # faturamento = 1 mensalidade + implementação (campos limpos; total_value cru vem sujo).
    # TCV (6× mensalidade) só no DRE.
    valor=sum(br_num(r.get("value_mensalidade"))+br_num(r.get("value_implementação") or r.get("value_implementacao"))
              for r in crm if in_v(pdate(r.get("win_at"))))
    sal=flagcount("sal","sal_at") or distinct("sal_at")
    def pace(real, meta):
        proj=real/VELAPSED*VDAYS if VELAPSED else 0.0
        return {"real":real,"meta":meta,"pct":pct(real,meta),"proj":proj,"proj_pct":pct(proj,meta)}
    return {
        "demos_real":pace(demos_re,META["demos_real_q"]),
        "demos_agend":pace(demos_ag,META["demos_agend_q"]),
        "clientes":pace(cli,META["clientes_q"]),
        "valor":pace(valor,META["valor_total_q"]),
        "q_show":{"real":pct(demos_re,demos_ag),"meta":META["show_rate"],"q1":META["q1"]["show"]},
        "q_close":{"real":pct(cli,demos_re),"meta":META["close_rate"],"q1":META["q1"]["close"]},
        "q_salsql":{"real":pct(sql,sal),"meta":META["sal_sql_rate"],"q1":META["q1"]["sal_sql"]},
    }

# --- reconciliação CRM×campanhas (resíduo do join ad_id) ----------------------
# Metodologia (cozinha — fica aqui, nunca em nota no HTML): pra cada mês×canal
# pago, o excedente de eventos do CRM sobre o campanhas (leads sem match de
# ad_id, ~5%) é distribuído FRACIONADO entre as linhas dia×anúncio daquele
# mês×canal, proporcional à participação da linha no próprio evento; se o
# mês×canal não tem nenhum evento atribuído, cai pro share de investimento; sem
# investimento também → fica sem alocar (aparece na conservação do stdout).
# Âncora temporal = data do EVENTO no CRM (mesmo grão do campanhas). Excedente
# negativo (campanhas > CRM) não desconta nada — só volume soma. Valor (R$) não
# se reconcilia: as fórmulas de valor divergem entre as fontes.
def compute_resid(campanhas, crm):
    from collections import defaultdict
    EVK = ["sal", "demo_ag", "demo_re", "cli"]
    camp_mc = defaultdict(lambda: [0.0]*4); inv_mc = defaultdict(float); rows_mc = defaultdict(list)
    for i, c in enumerate(campanhas):
        key = (c["data"].strftime("%Y-%m"), c["canal"])
        s = camp_mc[key]
        for e, k in enumerate(EVK): s[e] += c[k]
        inv_mc[key] += c["inv"]; rows_mc[key].append(i)
    paid = {c["canal"] for c in campanhas if c["inv"] > 0}
    crm_mc = defaultdict(lambda: [0.0]*4)
    for r in crm:
        cd = pdate(r.get("create_at"))
        if cd and cd.year < MIN_ANO: continue
        ch = canal_norm(r.get("canal"))
        if ch not in paid: continue
        if istrue(r.get("sal")):
            d = pdate(r.get("sal_at")) or cd
            if d: crm_mc[(d.strftime("%Y-%m"), ch)][0] += 1
        d = pdate(r.get("scheduled_meeting_at"))
        if d: crm_mc[(d.strftime("%Y-%m"), ch)][1] += 1
        d = pdate(r.get("show_meeting_at"))
        if d: crm_mc[(d.strftime("%Y-%m"), ch)][2] += 1
        if istrue(r.get("win")):
            d = pdate(r.get("win_at"))
            if d: crm_mc[(d.strftime("%Y-%m"), ch)][3] += 1
    add = defaultdict(lambda: [0.0]*4)
    tot_crm = [0.0]*4; tot_camp = [0.0]*4; tot_alloc = [0.0]*4; tot_resid = [0.0]*4
    for key, crm_v in crm_mc.items():
        camp_v = camp_mc.get(key, [0.0]*4); idxs = rows_mc.get(key, [])
        for e in range(4):
            tot_crm[e] += crm_v[e]; tot_camp[e] += camp_v[e]
            resid = crm_v[e] - camp_v[e]
            if resid <= 0: continue
            tot_resid[e] += resid
            if not idxs: continue
            if camp_v[e] > 0:
                shares = [(i, campanhas[i][EVK[e]]/camp_v[e]) for i in idxs if campanhas[i][EVK[e]] > 0]
            elif inv_mc[key] > 0:
                shares = [(i, campanhas[i]["inv"]/inv_mc[key]) for i in idxs if campanhas[i]["inv"] > 0]
            else:
                continue
            for i, sh in shares: add[i][e] += resid*sh
            tot_alloc[e] += resid
    rows = [[i]+[round(v, 3) for v in vals] for i, vals in sorted(add.items()) if any(v > 0.0005 for v in vals)]
    cons = " · ".join(f"{k}: crm {tot_crm[e]:.0f} = camp {tot_camp[e]:.0f} + resid {tot_alloc[e]:.1f}"
                      + (f" (não alocado {tot_resid[e]-tot_alloc[e]:.1f})" if tot_resid[e]-tot_alloc[e] > 0.05 else "")
                      for e, k in enumerate(EVK))
    print(f"reconciliação ad_id: {cons}")   # sem '→' — console do feed é cp1252
    # resumo pro cockpit (tela Atenção): CRM vs campanhas por evento, incl. supercontagem
    recon = {k: {"crm": round(tot_crm[e]), "camp": round(tot_camp[e]), "alloc": round(tot_alloc[e], 1)}
             for e, k in enumerate(EVK)}
    return {"rows": rows, "cols": ["row", "sal", "demo_ag", "demo_re", "cli"], "recon": recon}

# --- breakdowns do flow (F5.1): geo/idade×gênero/device/hora + geo Google ------
# Fonte: raw/flow-*.csv (extração das segundas, GRÃO MENSAL). Opcionais — sem
# eles a tela Dimensões avisa. Interned; atributos do anúncio (taxonomia)
# parseados por ad_id p/ o cruzamento Debriefing×Dimensão (só Meta: os nomes
# gia-v2 vivem lá; conversões por breakdown Meta não existem — lacuna UNNEST).
def _rd_flow(name):
    p = RAW / name
    if not p.exists(): return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_lib(aI):
    """Biblioteca de criativos (F5.2): array PARALELO ao intern de anúncios —
    [img, title, cta, body] por NOME de anúncio (1º ad com asset vence).
    img: creative.image_hash -> adimages.url (full-size); fallback thumbnail_url.
    URLs do CDN do Meta expiram (~semanas) — a extração das segundas renova."""
    ads_f, crt_f, img_f = _rd_flow("flow-meta-ads.csv"), _rd_flow("flow-meta-criativos.csv"), _rd_flow("flow-meta-imagens.csv")
    if not ads_f: return None
    imgs = {(r.get("id") or "").split(":")[-1]: (r.get("url") or "") for r in img_f}
    crt = {}
    for r in crt_f:
        cid = (r.get("creative_id") or "").strip()
        if cid: crt[cid] = r    # keep-last (versão mais recente)
    ad_asset = {}
    for r in ads_f:
        c = crt.get((r.get("creative_id") or "").strip(), {})
        img = imgs.get((c.get("image_hash") or "").strip(), "") or (c.get("thumbnail_url") or "")
        ad_asset[(r.get("ad_id") or "").strip()] = [img, (c.get("title") or "").strip(),
                                                    (c.get("call_to_action_type") or "").strip(),
                                                    (c.get("body") or "").strip()[:280]]
    # nome do anúncio -> asset (via index ad_id->nome; 1º com imagem vence)
    idx = load_index(verbose=False)
    by_name = {}
    for ad, ix in idx.items():
        a = ad_asset.get(ad)
        if not a: continue
        cur = by_name.get(ix["anuncio"])
        if cur is None or (not cur[0] and a[0]):
            by_name[ix["anuncio"]] = a
    return [by_name.get(n) or 0 for n in aI.l]

def load_brk(taxo, campanhas):
    rd = _rd_flow
    geo, demo, dev, hora, ggeo = (rd("flow-meta-geo.csv"), rd("flow-meta-demo.csv"),
                                  rd("flow-meta-device.csv"), rd("flow-meta-hora.csv"),
                                  rd("flow-google-geo.csv"))
    if not (geo or demo or dev or hora or ggeo):
        return None
    def num(r, k): return round(float(r.get(k) or 0), 2)
    def n0(r, k): return int(float(r.get(k) or 0))
    # raw do flow é DIA desde 2026-07-10 (era mensal) — o payload segue MENSAL:
    # agrega aqui (mes = data[:7]; tolera os dois formatos). Grão dia mora no raw.
    def mes(r): return ((r.get("mes") or r.get("data") or ""))[:7]
    def agg3(rows, key_fn):
        m = {}
        for r in rows:
            a = m.setdefault(key_fn(r), [0.0, 0, 0])
            a[0] += num(r, "spend"); a[1] += n0(r, "impressions"); a[2] += n0(r, "clicks")
        return [[*k, round(v[0], 2), v[1], v[2]] for k, v in m.items()]
    adI, mI = Interner(), Interner()
    regI, ageI, devI, hcI, gcI, grI = Interner(), Interner(), Interner(), Interner(), Interner(), Interner()
    g_rows = agg3(geo, lambda r: (adI.idx(r["ad_id"]), mI.idx(mes(r)), regI.idx(r["region"])))
    d_rows = agg3(demo, lambda r: (adI.idx(r["ad_id"]), mI.idx(mes(r)), ageI.idx(r["age"]),
                                   (r.get("gender") or "u")[:1]))
    v_rows = agg3(dev, lambda r: (adI.idx(r["ad_id"]), mI.idx(mes(r)), devI.idx(r["device_platform"])))
    # hora por AD (F7.2: stream tem ad_id) — habilita o rateio de funil por hora;
    # fallback pro formato legado (campanha) via hcI se ad_id ausente
    h_rows = agg3(hora, lambda r: (adI.idx(r["ad_id"]) if r.get("ad_id") else
                                   -1 - hcI.idx(r.get("campaign_name") or "—"),
                                   mI.idx(mes(r)), (r.get("hora") or "")[:2]))
    # google geo: payload no nível REGIÃO (cidade fica no raw + top cidades full-period)
    greg, gcid = {}, {}
    for r in ggeo:
        k = (gcI.idx(r.get("campaign_name") or "—"), mI.idx(mes(r)), grI.idx(r.get("regiao") or "—"))
        a = greg.setdefault(k, [0.0, 0, 0, 0.0])
        a[0] += num(r, "cost"); a[1] += n0(r, "impressions"); a[2] += n0(r, "clicks"); a[3] += float(r.get("conversions") or 0)
    gg_rows = [[k[0], k[1], k[2], round(v[0], 2), v[1], v[2], round(v[3], 1)] for k, v in greg.items()]
    # atributos do anúncio por ad_id (nome vem do index; parse pela taxonomia)
    idx = load_index(verbose=False)
    attrs = []
    for ad in adI.l:
        an = parse_nome(taxo["anuncio"], (idx.get(ad) or {}).get("anuncio", ""))
        attrs.append({"g": an.get("geracao", "legado"), "c": an.get("consciencia", ""),
                      "h": an.get("gancho", ""), "a": an.get("avatar", ""), "f": an.get("formato", "")})
    # funil por (ad × mês) do fato — base do RATEIO por share de investimento
    # (funil estimado por dimensão de entrega: a API não dá conversão por breakdown)
    fun = {}
    known = set(adI.m)
    for c in campanhas:
        if c["ad_id"] not in known: continue
        k = (adI.idx(c["ad_id"]), mI.idx(c["data"].strftime("%Y-%m")))
        f = fun.setdefault(k, [0, 0, 0, 0, 0, 0.0, 0.0])
        f[0] += c["lead"]; f[1] += c["sal"]; f[2] += c["demo_ag"]
        f[3] += c["demo_re"]; f[4] += c["cli"]; f[5] += c["fat"]; f[6] += c["inv"]
    fun_rows = [[k[0], k[1], v[0], v[1], v[2], v[3], v[4], round(v[5], 2), round(v[6], 2)]
                for k, v in fun.items()]
    # F7.3: funil por CAMPANHA×mês (rateio dos breakdowns Google — geo não desce
    # de campanha na API; chave = nome, igual nos dois lados via API do Google)
    gfun = {}
    for c in campanhas:
        if c["canal"] != "google": continue
        k = (gcI.idx(c["campanha"]), mI.idx(c["data"].strftime("%Y-%m")))
        f = gfun.setdefault(k, [0, 0, 0, 0, 0, 0.0])
        f[0] += c["lead"]; f[1] += c["sal"]; f[2] += c["demo_ag"]
        f[3] += c["demo_re"]; f[4] += c["cli"]; f[5] += c["fat"]
    gfun_rows = [[k[0], k[1], v[0], v[1], v[2], v[3], v[4], round(v[5], 2)] for k, v in gfun.items()]
    # cidades (full-period, top 300 por custo) COM funil estimado por rateio:
    # evento(campanha,mês) × share do custo da cidade no custo da campanha no mês
    gden = {}
    for r in ggeo:
        k = (gcI.idx(r.get("campaign_name") or "—"), mI.idx(mes(r)))
        gden[k] = gden.get(k, 0.0) + num(r, "cost")
    gcid = {}
    for r in ggeo:
        cid = (r.get("cidade") or "").strip()
        if not cid: continue
        k = (gcI.idx(r.get("campaign_name") or "—"), mI.idx(mes(r)))
        cost = num(r, "cost")
        c = gcid.setdefault((cid, r.get("regiao") or ""), [0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        c[0] += cost; c[1] += n0(r, "impressions"); c[2] += n0(r, "clicks"); c[3] += float(r.get("conversions") or 0)
        fn, d = gfun.get(k), gden.get(k, 0.0)
        if fn and d > 0:
            sh = cost / d
            for i, ev in enumerate(fn):
                c[4 + i] += ev * sh
    top_cid = sorted(gcid.items(), key=lambda kv: -kv[1][0])[:300]
    gc_rows = [[c, reg, round(v[0], 2), v[1], v[2], round(v[3], 1),
                round(v[4], 1), round(v[5], 1), round(v[6], 1), round(v[7], 1),
                round(v[8], 2), round(v[9], 2)] for (c, reg), v in top_cid]
    return {"meses": mI.l, "attrs": attrs, "funil": fun_rows, "gfun": gfun_rows,
            "geo": {"regs": regI.l, "rows": g_rows},
            "demo": {"ages": ageI.l, "rows": d_rows},
            "dev": {"devs": devI.l, "rows": v_rows},
            "hora": {"camps": hcI.l, "rows": h_rows},
            "ggeo": {"camps": gcI.l, "regs": grI.l, "rows": gg_rows},
            "gcid": {"rows": gc_rows}}

# --- payload granular --------------------------------------------------------
def build_payload(campanhas, crm):
    crm_max=max((pdate(r.get("create_at")) for r in crm if pdate(r.get("create_at"))), default=None)
    camp_max=max((c["data"] for c in campanhas), default=None)

    # campanhas (interned). v5: colunas novas SÓ NO FIM (índices 0-12 estáveis —
    # contrato do monitor.json com skills consumidoras é append-only).
    cI, jI, aI = Interner(), Interner(), Interner()
    camp_rows=[]
    for c in campanhas:
        camp_rows.append([iso(c["data"]), c["canal"], cI.idx(c["campanha"]),
            jI.idx(c["conjunto"]), aI.idx(c["anuncio"]),
            round(c["inv"],2), c["sal"], c["demo_ag"], c["demo_re"], c["cli"], round(c["fat"],2),
            c["impr"], c["clicks"], c["lead"], c["sql"], c["alcance"]])

    # leads (interned, sem PII direta). v5: campos novos SÓ NO FIM (índices 0-17
    # estáveis) — qualificadores normalizados + sdr + stage_pipeline + lost_at +
    # flag clickid (canal declarado × evidência gclid/fbclid — detector Martins).
    icmI, rzI = Interner(), Interner()
    qI = {k: Interner() for k in QUAL_CAMPOS}
    sdrI, stI = Interner(), Interner()
    lead_rows=[]
    for r in crm:
        _cda = pdate(r.get("create_at"))
        if _cda and _cda.year < MIN_ANO:   # descarta outliers de data (1999/2023)
            continue
        canal = canal_norm(r.get("canal"))
        # clickid: gclid/gbraid/wbraid = evidência google; fbclid = evidência meta
        # (fbp NÃO conta — pixel seta em qualquer visita, não é clique)
        has_g = bool((r.get("gclid") or "").strip() or (r.get("gbraid") or "").strip() or (r.get("wbraid") or "").strip())
        has_f = bool((r.get("fbclid") or "").strip())
        sflag = 1 if ((canal == "meta" and has_g and not has_f) or
                      (canal == "google" and has_f and not has_g) or
                      (canal not in ("meta", "google") and (has_g or has_f))) else 0
        lead_rows.append([
            canal,
            icmI.idx((r.get("icm_product_map") or "—").strip() or "—"),
            iso(pdate(r.get("create_at"))),
            1 if istrue(r.get("sal")) else 0, iso(pdate(r.get("sal_at"))),
            1 if istrue(r.get("sql")) else 0, iso(pdate(r.get("sql_at"))),
            1 if istrue(r.get("mql")) else 0,
            iso(pdate(r.get("scheduled_meeting_at"))),
            iso(pdate(r.get("show_meeting_at"))),
            1 if istrue(r.get("win")) else 0, iso(pdate(r.get("win_at"))),
            1 if istrue(r.get("lost")) else 0,
            rzI.idx((r.get("lost_reason") or "—").strip() or "—"),
            round(br_num(r.get("total_value")),2),
            1 if istrue(r.get("in_negotiation")) else 0,
            round(br_num(r.get("value_mensalidade")),2),
            round(br_num(r.get("value_implementação") or r.get("value_implementacao")),2),
            # ---- v5 (18+) ----
            qI["obras"].idx(qual_norm("obras", r.get(QUAL_CAMPOS["obras"]))),
            qI["ferramenta"].idx(qual_norm("ferramenta", r.get(QUAL_CAMPOS["ferramenta"]))),
            qI["cargo"].idx(qual_norm("cargo", r.get(QUAL_CAMPOS["cargo"]))),
            qI["segmento"].idx(qual_norm("segmento", r.get(QUAL_CAMPOS["segmento"]))),
            qI["dor"].idx(qual_norm("dor", r.get(QUAL_CAMPOS["dor"]))),
            sdrI.idx((r.get("sdr") or "").strip()),
            stI.idx((r.get("stage_pipeline") or "").strip()),
            iso(pdate(r.get("lost_at"))),
            sflag,
        ])

    # vendas atribuídas via ad_id (v5.1): ganho do CRM ligado ao criativo pelo
    # ad_id → faturamento LIMPO (mens+impl) e MRR no grão de mídia. Sem match
    # de ad_id a venda não entra aqui (aparece só nas visões de CRM) — é
    # atribuição direta, sem rateio; taxa de match impressa no stdout.
    ad_map = {}
    for i, c in enumerate(campanhas):
        if c["ad_id"]: ad_map[c["ad_id"]] = (c["canal"], camp_rows[i][2], camp_rows[i][3], camp_rows[i][4])
    vend_rows = []; v_tot = 0; v_match = 0
    for r in crm:
        if not istrue(r.get("win")): continue
        wd = pdate(r.get("win_at"))
        if not wd or wd.year < MIN_ANO: continue
        v_tot += 1
        am = ad_map.get((r.get("ad_id") or "").strip())
        if not am: continue
        v_match += 1
        f2 = br_num(r.get("value_mensalidade")) + br_num(r.get("value_implementação") or r.get("value_implementacao"))
        vend_rows.append([iso(wd), am[0], am[1], am[2], am[3],
                          round(f2, 2), round(br_num(r.get("value_mensalidade")), 2)])
    print(f"vendas atribuídas via ad_id: {v_match}/{v_tot} ganhos com match")

    # dim (v6.2/F5): atributos da nomenclatura (taxonomia gia-v2) em arrays
    # PARALELOS aos interns (campanhas/conjuntos/anuncios) — a tela Debriefing
    # agrega o funil reconciliado por atributo no cliente. Fonte dos patterns:
    # 10-fundacao/taxonomia.yml (donos: media-buyer-*).
    TAXO = taxo_parsers()
    dim = {"camp": [parse_campanha(TAXO["campanha"], n) for n in cI.l],
           "conj": [parse_nome(TAXO["conjunto"], n) for n in jI.l],
           "anun": [parse_nome(TAXO["anuncio"], n) for n in aI.l]}

    return {
        "freshness": {"gerado":HOJE.strftime("%d/%m/%Y %H:%M"),
            "crm_ate":crm_max.strftime("%d/%m/%Y") if crm_max else "—",
            "camp_ate":camp_max.strftime("%d/%m/%Y") if camp_max else "—"},
        "quarter": {"label":QLABEL,"ini":QSTART.strftime("%d/%m"),"fim":QEND.strftime("%d/%m/%Y"),
            "elapsed":QELAPSED,"days":QDAYS,"start":iso(QSTART),"end":iso(QEND),
            "ano":HOJE.year},
        "vigencia": {"label":VLABEL,"start":iso(VSTART),"end":iso(VEND),
            "days":VDAYS,"elapsed":VELAPSED},
        "canais_meta": CANAIS_META,
        "hoje": iso(HOJE.date()),
        "meta": META, "alvos": {"custo_demo":TGT_CUSTO_DEMO,"cac":TGT_CAC},
        "okr": compute_okr(crm),
        "resid": compute_resid(campanhas, crm),
        "camp": {"campanhas":cI.l,"conjuntos":jI.l,"anuncios":aI.l,"rows":camp_rows,
            "cols":["data","canal","camp","conj","anun","inv","sal","demo_ag","demo_re","cli","fat","impr","clicks",
                    "lead","sql","alcance"]},
        "leads": {"icms":icmI.l,"reasons":rzI.l,"rows":lead_rows,
            "quals":{k: qI[k].l for k in QUAL_CAMPOS}, "sdrs":sdrI.l, "stages":stI.l,
            "cols":["canal","icm","create_at","sal","sal_at","sql","sql_at","mqlform",
                    "sched_at","show_at","win","win_at","lost","reason","value","neg","mens","impl",
                    "q_obras","q_ferramenta","q_cargo","q_segmento","q_dor","sdr","stage","lost_at","sflag"]},
        "vendas": {"rows": vend_rows, "cols": ["data","canal","camp","conj","anun","fat2","mens"]},
        "dim": dim,
        "brk": load_brk(TAXO, campanhas),
        "lib": load_lib(aI),
        "fin": load_config_fin(),
        "tcv_default": 6,
        "termos": load_termos(),
    }

def main():
    if not FATO.exists():
        print("ERRO: derivado/fato-ads-enriquecido.csv ausente. Rode _transform.py primeiro.", file=sys.stderr); sys.exit(1)
    crm = load_crm(verbose=False)   # QA do CRM já registrado pelo transform nesta rodada
    P = build_payload(load_fato(), crm)
    from _render_monitor import render
    OUT.write_text(render(P), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(P, ensure_ascii=False), encoding="utf-8")   # snapshot p/ skills de análise
    o=P["okr"]
    print(f"monitor v6 · vigência {VLABEL} · demos {o['demos_real']['real']:.0f}/{o['demos_real']['meta']}"
          f" · clientes {o['clientes']['real']:.0f}/{o['clientes']['meta']}"
          f" · {len(P['camp']['rows'])} linhas camp · {len(P['leads']['rows'])} leads"
          f" · {OUT.name} + {OUT_JSON.name}")

if __name__ == "__main__":
    main()
