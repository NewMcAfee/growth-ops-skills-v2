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
#   Demo realizada  = show_meeting (data show_meeting_at) · META 100/mês.
#   Close-rate      = Clientes ÷ Demos realizadas. 1 demo/cliente = por lead.
# =============================================================================
import csv, json, sys
from datetime import datetime, date, timedelta
from pathlib import Path

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
CAMP = BASE / "campanhas-completo.csv"
CRM  = BASE / "crm-completo.csv"
TERMS = BASE / "termos-google-completo.csv"
OUT  = BASE / "monitor.html"
OUT_JSON = BASE / "monitor.json"        # snapshot estruturado p/ skills de análise (git-ignored, embute CRM analítico)
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

# --- contrato: metas lidas em runtime (troca de quarter sem tocar código) ----
# Fallback gracioso pro META_DEFAULT se pyyaml ou o contrato faltarem (feed nunca quebra).
META_DEFAULT = {
    "demos_real_mes": 100,  "demos_real_q": 300,
    "demos_agend_mes": 120, "demos_agend_q": 360,
    "sql_semana": 25, "clientes_q": 40, "valor_total_q": 100000,
    "sal_sql_rate": 0.50, "show_rate": 0.70, "close_rate": 0.20, "budget_q": 50000,
    "q1": {"sal_sql": 0.40, "show": 0.60, "close": 0.15},
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
    dmes, dames = m.get("demos_real_mes", 100), m.get("demos_agend_mes", 120)
    return {
        "demos_real_mes": dmes,   "demos_real_q": m.get("demos_real_q", dmes*3),
        "demos_agend_mes": dames, "demos_agend_q": m.get("demos_agend_q", dames*3),
        "sql_semana": m.get("sql_semana", 25),
        "clientes_q": m.get("clientes_q", 40), "valor_total_q": m.get("valor_total_q", 100000),
        "sal_sql_rate": tx.get("sal_sql", 0.50), "show_rate": tx.get("show", 0.70),
        "close_rate": tx.get("close", 0.20), "budget_q": m.get("budget_q", 50000),
        "q1": {"sal_sql": base.get("sal_sql", 0.40), "show": base.get("show", 0.60),
               "close": base.get("close", 0.15)},
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
TGT_CUSTO_DEMO = META["budget_q"] / META["demos_real_q"]   # ~R$167
TGT_CAC        = META["budget_q"] / META["clientes_q"]      # ~R$1.250
MIN_ANO = 2024   # base completa tem outliers de data (1999/2023) — descarta lixo pré-2024

# --- parsing -----------------------------------------------------------------
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
    # leads_pipeline vem como número (ex "46186") em vez de dd/mm/yyyy. O range
    # guard (~1982..2119) evita confundir com IDs ou contadores pequenos.
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
    return c or "—"

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
def load_campanhas():
    # Schema bd_ads (snake_case, funil granular por linha dia×anúncio).
    # 'sal' (evento de conversão por anúncio) ← coluna `mql` do bd_ads (= o "MQL"
    # antigo que o operador definiu como SAL). Demo agendada/realizada/cliente
    # ← scheduled_meeting/show_meeting/win. Faturamento ← total_value.
    rows = []
    with open(CAMP, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = pdate(r.get("data"))
            if not d or d.year < MIN_ANO: continue
            rows.append({
                "data": d, "ad_id": (r.get("ad_id") or "").strip(),
                "canal": canal_norm(r.get("canal")),
                "campanha": (r.get("nome_campanha") or "—").strip() or "—",
                "conjunto": (r.get("nome_conjunto") or "—").strip() or "—",
                "anuncio": (r.get("nome_anuncio") or "—").strip() or "—",
                "inv": br_num(r.get("investimento")),
                "sal": br_int(r.get("mql")),
                "demo_ag": br_int(r.get("scheduled_meeting")),
                "demo_re": br_int(r.get("show_meeting")),
                "cli": br_int(r.get("win")),
                "fat": br_num(r.get("total_value")),
                "impr": br_int(r.get("impressões") or r.get("impressoes")),
                "clicks": br_int(r.get("ad_clicks")),
                # v5: funil completo por anúncio (CPL, lead→SAL) + alcance (frequência)
                "lead": br_int(r.get("lead")),
                "sql": br_int(r.get("sql")),
                "alcance": br_int(r.get("alcance")),
            })
    return rows
def load_crm():
    with open(CRM, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_config_fin():
    """Config financeiro manual do vault (commitável, sem PII). 1 linha por mês.
    Colunas: mes(YYYY-MM), fee, margem(0-1 ou %), tcv_meses, outras_receitas, outros_custos."""
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
        "fin": load_config_fin(),
        "tcv_default": 6,
        "termos": load_termos(),
    }

def main():
    if not CAMP.exists() or not CRM.exists():
        print("ERRO: CSV(s) ausente(s). Rode o feed primeiro.", file=sys.stderr); sys.exit(1)
    P = build_payload(load_campanhas(), load_crm())
    from _render_monitor import render
    OUT.write_text(render(P), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(P, ensure_ascii=False), encoding="utf-8")   # snapshot p/ skills de análise
    o=P["okr"]
    print(f"monitor v4 · vigência {VLABEL} · demos {o['demos_real']['real']:.0f}/{o['demos_real']['meta']}"
          f" · clientes {o['clientes']['real']:.0f}/{o['clientes']['meta']}"
          f" · {len(P['camp']['rows'])} linhas camp · {len(P['leads']['rows'])} leads"
          f" · {OUT.name} + {OUT_JSON.name}")

if __name__ == "__main__":
    main()
