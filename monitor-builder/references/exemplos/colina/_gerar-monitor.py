# -*- coding: utf-8 -*-
# =============================================================================
# _gerar-monitor.py — Grupo Colina · snapshot determinístico do monitor
# -----------------------------------------------------------------------------
# Lê campanhas-ano-corrente.csv (bd_ads) + crm-ano-corrente.csv (leads_pipeline)
# + contrato-cockpit.yml e emite monitor.json (agregados SEM PII) p/ skills de
# análise (newton/darwin/falconi) consumirem + sanity-check do feed.
#
# Modelo Colina HÍBRIDO (recorrência + TCV): funil de AQUISIÇÃO Lead›MQL›SQL›Ganho,
# recorte BU × canal. Investimento = campanhas (bd_ads); MQL/clientes = CRM (flags).
#   Clientes = CRM (coorte): safra (create_at no mês) × geral (win_at no mês).
#   Receita = PREMISSA (contrato): Planos = mensalidade×LTV 18m · Jazigo/Serviços = TCV.
# Canal vem da coluna `canal` (ad_id manual_* não tem campanha mas conta pelo canal).
# O HTML rico é responsabilidade do _render_monitor.py (roda depois).
# =============================================================================
import csv, json, sys, io
from datetime import datetime
from pathlib import Path

# stdout/stderr utf-8 (Task Scheduler + console Windows cp1252 não quebra em →/ç)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
OUT_JSON = BASE / "monitor.json"
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

DEFAULTS = {
    "fontes": {"campanhas": "campanhas-ano-corrente.csv", "crm": "crm-ano-corrente.csv"},
    "min_ano": 2026,
    "canais_meta": ["paid_meta", "paid_google"],
    "bu_ordem": ["Plano SP", "Jazigo", "Plano RJ", "Serviços"],
    "bu_norm": {}, "bu_outros": "Outros",
    "metas": {}, "periodo": {"inicio": "2026-07-01", "fim": "2026-09-30", "quarter_vigencia": "2026-Q3"},
}

def load_contrato():
    c = {}
    try:
        import yaml
        c = yaml.safe_load(CONTRATO.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"WARN: contrato indisponível ({e}) — usando defaults.", file=sys.stderr)
    bu = c.get("bu", {})
    return {
        "fontes": c.get("fontes", DEFAULTS["fontes"]),
        "min_ano": int(c.get("min_ano", DEFAULTS["min_ano"])),
        "canais_meta": c.get("canais_meta", DEFAULTS["canais_meta"]),
        "bu_col": bu.get("col", "funnel"),
        "bu_ordem": bu.get("ordem", DEFAULTS["bu_ordem"]),
        "bu_norm": bu.get("normaliza", {}) or {},
        "bu_outros": bu.get("outros_label", DEFAULTS["bu_outros"]),
        "metas": (c.get("metas", {}) or {}).get("por_bu", {}) or {},
        "receita": (c.get("receita", {}) or {}).get("por_bu", {}) or {},
        "periodo": c.get("periodo", DEFAULTS["periodo"]),
        "fiscal_dia": int((c.get("mes_fiscal", {}) or {}).get("dia_inicio", 16)),
    }

def pnum(s):
    if s is None: return 0.0
    s = str(s).strip().replace("R$", "").replace(" ", "")
    if not s: return 0.0
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def pdate(s):
    if not s: return None
    s = str(s).strip()
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
              "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try: return datetime.strptime(s, f)
        except ValueError: continue
    return None

def truthy(v):
    return str(v).strip().lower() not in ("", "false", "0", "no", "não", "nao", "none", "0.0")

def rcsv(name):
    p = BASE / name
    if not p.exists():
        print(f"WARN: fonte ausente: {name}", file=sys.stderr); return []
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

C = load_contrato()
MIN_ANO = C["min_ano"]
CANAIS_META = C["canais_meta"]
BU_NORM = C["bu_norm"]
BU_ORDEM = C["bu_ordem"]
BU_OUTROS = C["bu_outros"]
FD = C["fiscal_dia"]   # mês fiscal Colina: dia 16 → dia 15, nomeado pelo mês em que TERMINA

def fm_key(d):
    """chave YYYY-MM do mês FISCAL da data (16/jun–15/jul → '2026-07')."""
    if d.day >= FD:
        if d.month == 12: return f"{d.year + 1:04d}-01"
        return f"{d.year:04d}-{d.month + 1:02d}"
    return f"{d.year:04d}-{d.month:02d}"

def norm_bu(v):
    v = (v or "").strip()
    if v in BU_NORM: return BU_NORM[v]
    if v in BU_ORDEM: return v
    return BU_OUTROS

def bu_crm(r):
    """BU no CRM: `origem` é a fonte primária; `funnel` é fallback (operador 2026-07-02)."""
    return norm_bu((r.get("origem") or "").strip() or r.get("funnel"))

def norm_canal(v):
    return (v or "").strip() or "(sem canal)"

ads = rcsv(C["fontes"]["campanhas"])
crm = rcsv(C["fontes"]["crm"])

# ---- rateio manual_zendesk → paid_meta/paid_google (regra do operador 2026-07-02) ----
# manual_zendesk NÃO é canal de aquisição — divide entre os pagos pela taxa observada
# de manual_* com canal pago conhecido (por BU; fallback global; fallback 50/50).
_mm = {}
for r in crm:
    cd = pdate(r.get("create_at"))
    if not cd or cd.year < MIN_ANO: continue
    if not (r.get("ad_id") or "").strip().startswith("manual"): continue
    ch = (r.get("canal") or "").strip()
    if ch in ("paid_meta", "paid_google"):
        v = _mm.setdefault(bu_crm(r), [0, 0])
        v[0 if ch == "paid_meta" else 1] += 1
_tm = sum(v[0] for v in _mm.values()); _tg = sum(v[1] for v in _mm.values())
FRAC_GLOBAL = _tm / (_tm + _tg) if (_tm + _tg) else 0.5
FRAC_BU = {bu: (v[0] / (v[0] + v[1]) if (v[0] + v[1]) else FRAC_GLOBAL) for bu, v in _mm.items()}

# ---- agregação campanhas (bd_ads): por BU × canal × mês ----
def novo_ad(): return {"inv": 0.0, "mql": 0.0, "win": 0.0, "lead": 0.0, "sql": 0.0, "impr": 0.0, "clk": 0.0}
ADS = {}   # (bu, canal, mes) -> dict
for r in ads:
    d = pdate(r.get("data"))
    if not d or d.year < MIN_ANO: continue
    bu, canal, mes = norm_bu(r.get("funnel")), norm_canal(r.get("canal")), fm_key(d)
    if canal == "manual_zendesk":   # mesmo rateio do CRM (fracionário)
        f = FRAC_BU.get(bu, FRAC_GLOBAL)
        parts = [("paid_meta", f), ("paid_google", 1 - f)]
    else:
        parts = [(canal, 1.0)]
    for cn, w in parts:
        a = ADS.setdefault((bu, cn, mes), novo_ad())
        a["inv"] += pnum(r.get("investimento")) * w; a["mql"] += pnum(r.get("mql")) * w
        a["win"] += pnum(r.get("win")) * w; a["lead"] += pnum(r.get("lead")) * w; a["sql"] += pnum(r.get("sql")) * w
        a["impr"] += pnum(r.get("impressões")) * w; a["clk"] += pnum(r.get("ad_clicks")) * w

# ---- agregação CRM (leads_pipeline): funil + coorte por BU × canal × mês ----
# (pesos fracionários por causa do rateio manual_zendesk → arredonda na saída)
def novo_crm(): return {"lead": 0, "mql": 0, "sql": 0, "ganho": 0, "perdido": 0,
                        "cli_safra": 0, "cli_geral": 0, "valor_ganho": 0.0}
CRM = {}
for r in crm:
    cd = pdate(r.get("create_at"))
    if not cd or cd.year < MIN_ANO: continue
    bu, canal = bu_crm(r), norm_canal(r.get("canal"))
    win = truthy(r.get("win")); val = pnum(r.get("total_value"))
    wd = pdate(r.get("win_at"))
    mes_cd = fm_key(cd)
    if canal == "manual_zendesk":
        f = FRAC_BU.get(bu, FRAC_GLOBAL)
        parts = [("paid_meta", f), ("paid_google", 1 - f)]
    else:
        parts = [(canal, 1.0)]
    for cn, w in parts:
        c = CRM.setdefault((bu, cn, mes_cd), novo_crm())
        c["lead"] += w
        if truthy(r.get("mql")): c["mql"] += w
        if truthy(r.get("sql")): c["sql"] += w
        if truthy(r.get("lost")): c["perdido"] += w
        if win:
            c["ganho"] += w; c["valor_ganho"] += val * w
            c["cli_safra"] += w   # coorte: cliente cujo lead nasceu neste mês
            # cliente geral é contado no mês FISCAL do win_at:
            mes_win = fm_key(wd) if (wd and wd.year >= MIN_ANO) else mes_cd
            CRM.setdefault((bu, cn, mes_win), novo_crm())["cli_geral"] += w

# ---- período de OKR (contrato) — meses FISCAIS cobertos pela vigência ----
ini = pdate(C["periodo"].get("inicio")) or datetime(HOJE.year, HOJE.month, 1)
fim = pdate(C["periodo"].get("fim")) or HOJE
meses_periodo = set()
ka, kb = fm_key(ini), fm_key(fim)
y, m = int(ka[:4]), int(ka[5:7])
while f"{y:04d}-{m:02d}" <= kb:
    meses_periodo.add(f"{y:04d}-{m:02d}")
    m += 1
    if m > 12: m = 1; y += 1

def somar(dic, campos, so_canais_meta=False):
    """soma campos por BU dentro do período (blended por canal por default;
    so_canais_meta=True restringe a paid_meta+paid_google p/ contexto)."""
    out = {}
    for (bu, canal, mes), v in dic.items():
        if mes not in meses_periodo: continue
        if so_canais_meta and canal not in CANAIS_META: continue
        o = out.setdefault(bu, {c: 0.0 for c in campos})
        for c in campos: o[c] += v.get(c, 0)
    return out

# Investimento/tráfego = bd_ads (única fonte de gasto). Volume de funil/coorte = CRM
# (flag, atribuído por canal incl. manual_*). OKR restrito a canais_meta (contrato:
# "Máquina de Aquisição" = só pagos contam pra meta — coerente com o gate do monitor.html).
ads_bu = somar(ADS, ["inv", "win", "lead", "sql", "impr", "clk"], so_canais_meta=True)
crm_bu = somar(CRM, ["cli_safra", "cli_geral", "ganho", "lead", "mql", "sql", "perdido", "valor_ganho"], so_canais_meta=True)

n_meses = max(1, len(meses_periodo))
def meta_periodo(bu, campo):
    mm = C["metas"].get(bu, {})
    return mm.get(campo, 0) * n_meses

# ---- receita PREMISSA por BU (contrato: recorrente = mensalidade×ltv_meses · tcv = valor cheio) ----
def receita_bu(bu, n_clientes):
    r = C["receita"].get(bu) or {}
    if r.get("modelo") == "recorrente":
        m = float(r.get("mensalidade", 0)); n = int(r.get("ltv_meses", 0))
        return {"mrr_novo": n_clientes * m, "receita_contratada": n_clientes * m * n}
    if r:
        return {"mrr_novo": 0.0, "receita_contratada": n_clientes * float(r.get("valor", 0))}
    return {"mrr_novo": 0.0, "receita_contratada": 0.0}

# ---- OKR por BU (investimento=ads · MQL/clientes=CRM · derivados calculados) ----
okr_bu = {}
for bu in BU_ORDEM:
    a = ads_bu.get(bu, {}); cm = crm_bu.get(bu, {})
    inv = a.get("inv", 0.0); mql = cm.get("mql", 0.0)
    cli_s = cm.get("cli_safra", 0); cli_g = cm.get("cli_geral", 0)
    rec = receita_bu(bu, cli_g)
    okr_bu[bu] = {
        "investimento": round(inv, 2), "investimento_meta": meta_periodo(bu, "investimento"),
        "mql": round(mql), "mql_meta": meta_periodo(bu, "mql"),
        "cpmql": round(inv / mql, 2) if mql else None,
        "clientes_safra": round(cli_s, 1), "clientes_safra_meta": meta_periodo(bu, "clientes_safra"),
        "clientes_geral": round(cli_g, 1), "clientes_geral_meta": meta_periodo(bu, "clientes_geral"),
        "taxa_conversao": round(cli_s / mql, 4) if mql else None,
        "cac_safra": round(inv / cli_s, 2) if cli_s else None,
        "cac_geral": round(inv / cli_g, 2) if cli_g else None,
        "mrr_novo_premissa": round(rec["mrr_novo"], 2),
        "receita_contratada_premissa": round(rec["receita_contratada"], 2),
        "ltv_cac_premissa": round(rec["receita_contratada"] / inv, 2) if inv else None,
    }

tot = {k: 0.0 for k in ["investimento", "investimento_meta", "mql", "mql_meta",
                        "clientes_safra", "clientes_safra_meta", "clientes_geral", "clientes_geral_meta",
                        "mrr_novo_premissa", "receita_contratada_premissa"]}
for bu, o in okr_bu.items():
    for k in tot: tot[k] += o.get(k) or 0
tot["cpmql"] = round(tot["investimento"] / tot["mql"], 2) if tot["mql"] else None
tot["taxa_conversao"] = round(tot["clientes_safra"] / tot["mql"], 4) if tot["mql"] else None
tot["cac_safra"] = round(tot["investimento"] / tot["clientes_safra"], 2) if tot["clientes_safra"] else None
tot["cac_geral"] = round(tot["investimento"] / tot["clientes_geral"], 2) if tot["clientes_geral"] else None
tot["ltv_cac_premissa"] = round(tot["receita_contratada_premissa"] / tot["investimento"], 2) if tot["investimento"] else None

snapshot = {
    "projeto": "grupo-colina",
    "gerado_em": HOJE.strftime("%Y-%m-%d %H:%M:%S"),
    "periodo_okr": {"inicio": C["periodo"].get("inicio"), "fim": C["periodo"].get("fim"),
                    "meses": sorted(meses_periodo), "n_meses": n_meses},
    "canais_meta": CANAIS_META,
    "receita_premissa": C["receita"],   # modelo híbrido: recorrente (mensalidade×ltv) + tcv (valor cheio)
    "okr_total": tot,
    "okr_por_bu": okr_bu,
    "por_canal": {},   # contexto (todos os canais, todas as BUs, período)
}
# breakdown por canal (todas BUs, período, todos canais) p/ contexto
canal_ctx = {}
for (bu, canal, mes), v in ADS.items():
    if mes not in meses_periodo: continue
    o = canal_ctx.setdefault(canal, {"inv": 0.0, "mql": 0.0, "win": 0.0})
    o["inv"] += v["inv"]; o["mql"] += v["mql"]; o["win"] += v["win"]
snapshot["por_canal"] = {c: {"investimento": round(v["inv"], 2), "mql": round(v["mql"]),
                             "win": round(v["win"]), "conta_meta": c in CANAIS_META}
                         for c, v in sorted(canal_ctx.items(), key=lambda x: -x[1]["inv"])}

OUT_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK monitor.json | período {snapshot['periodo_okr']['inicio']}→{snapshot['periodo_okr']['fim']} "
      f"({n_meses}m) | META(pagos, c/ rateio manual_zendesk): inv R$ {tot['investimento']:,.0f} / MQL {round(tot['mql'])} "
      f"/ cli safra {tot['clientes_safra']:.1f} / cli geral {tot['clientes_geral']:.1f}")
sys.exit(0)
