# -*- coding: utf-8 -*-
# =============================================================================
# _render_monitor.py — Grupo Colina · Cockpit híbrido recorrência + TCV (7 telas)
# -----------------------------------------------------------------------------
# Gera monitor.html: cockpit auto-contido, tema dark-colina (verde esmeralda +
# dourado ipê), filtros GLOBAIS estilo Google Ads (date-range picker + BU + canal
# multi-select + comparação Δ%). Roda DEPOIS do _gerar-monitor.py.
#
# Modelo Colina (contrato-cockpit.yml, lido em runtime):
#   Investimento/tráfego = bd_ads (única fonte de gasto), por BU × canal × dia.
#   Funil Lead›MQL›SQL›Ganho + coorte = CRM (flag, canal incl. manual_*), por BU.
#   RECEITA = PREMISSA (total_value vazio no CRM): Planos = mensalidade × LTV 18m
#   (recorrência); Jazigo/Serviços = TCV cheio (one-time, mesmo parcelado).
#   Metas MENSAIS por BU escalam por dias no range; metas/pacing SÓ aparecem com
#   filtro de canal = canais_meta (a meta mede a Máquina de Aquisição paga).
#   PII nunca entra no payload (só datas/flags/BU/canal).
# =============================================================================
import csv, json, sys, collections
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
OUT = BASE / "monitor.html"
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

def load_contrato():
    d = {"fontes": {"campanhas": "campanhas-ano-corrente.csv", "crm": "crm-ano-corrente.csv"},
         "min_ano": 2026, "canais_meta": ["paid_meta", "paid_google"],
         "bu_ordem": ["Plano SP", "Jazigo", "Plano RJ", "Serviços"], "bu_norm": {}, "bu_outros": "Outros",
         "metas": {}, "receita": {}, "inicio": "2026-06-16", "fim": "2026-09-15", "quarter": "2026-Q3",
         "fiscal_dia": 16}
    try:
        import yaml
        c = yaml.safe_load(CONTRATO.read_text(encoding="utf-8")) or {}
        bu = c.get("bu", {}); p = c.get("periodo", {}); m = c.get("metas", {})
        d["fontes"] = c.get("fontes", d["fontes"]); d["min_ano"] = int(c.get("min_ano", d["min_ano"]))
        d["canais_meta"] = c.get("canais_meta", d["canais_meta"])
        d["bu_ordem"] = bu.get("ordem", d["bu_ordem"]); d["bu_norm"] = bu.get("normaliza", {}) or {}
        d["bu_outros"] = bu.get("outros_label", d["bu_outros"])
        d["metas"] = (m.get("por_bu", {}) or {})
        d["receita"] = (c.get("receita", {}) or {}).get("por_bu", {}) or {}
        d["inicio"] = p.get("inicio", d["inicio"]); d["fim"] = p.get("fim", d["fim"])
        d["quarter"] = p.get("quarter_vigencia", d["quarter"])
        d["fiscal_dia"] = int((c.get("mes_fiscal", {}) or {}).get("dia_inicio", 16))
    except Exception as e:
        print(f"WARN: contrato — {e}; default.", file=sys.stderr)
    return d

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
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try: return datetime.strptime(s, f)
        except ValueError: continue
    return None

def truthy(v): return str(v).strip().lower() not in ("", "false", "0", "no", "não", "nao", "none", "0.0")
def rcsv(name):
    p = BASE / name
    if not p.exists(): print(f"WARN: fonte ausente: {name}", file=sys.stderr); return []
    with open(p, encoding="utf-8-sig", newline="") as fh: return list(csv.DictReader(fh))
def iso(d): return d.strftime("%Y-%m-%d")

C = load_contrato()
MIN_ANO = C["min_ano"]; BU_NORM = C["bu_norm"]; BU_ORDEM = C["bu_ordem"]; BU_OUTROS = C["bu_outros"]
def norm_bu(v):
    v = (v or "").strip()
    if v in BU_NORM: return BU_NORM[v]
    if v in BU_ORDEM: return v
    return BU_OUTROS
def bu_crm(r):
    """BU no CRM: `origem` é a fonte primária; `funnel` é fallback (operador 2026-07-02)."""
    return norm_bu((r.get("origem") or "").strip() or r.get("funnel"))
def norm_canal(v): return (v or "").strip() or "(sem canal)"

ads = rcsv(C["fontes"]["campanhas"]); crm = rcsv(C["fontes"]["crm"])

FD = C["fiscal_dia"]   # mês fiscal Colina: 16→15, nomeado pelo mês em que TERMINA
def fm_key(d):
    """chave YYYY-MM do mês FISCAL da data (16/jun–15/jul → '2026-07')."""
    if d.day >= FD:
        if d.month == 12: return f"{d.year + 1:04d}-01"
        return f"{d.year:04d}-{d.month + 1:02d}"
    return f"{d.year:04d}-{d.month:02d}"

# ---- interning de strings (canal) p/ payload compacto ----
STR = {}
def si(s):
    s = (s or "").strip() or "Desconhecido"
    if s not in STR: STR[s] = len(STR)
    return STR[s]
BUL = list(BU_ORDEM) + [BU_OUTROS]
BUI = {b: i for i, b in enumerate(BUL)}
def bui(v): return BUI[norm_bu(v)]

# ---- rateio manual_zendesk → paid_meta/paid_google (regra do operador 2026-07-02) ----
# manual_zendesk NÃO é canal de aquisição — divide entre os pagos pela taxa observada
# de manual_* com canal pago conhecido (por BU; fallback global; fallback 50/50).
_mm = collections.defaultdict(lambda: [0, 0])   # bu -> [manual+paid_meta, manual+paid_google]
for r in crm:
    cd = pdate(r.get("create_at"))
    if not cd or cd.year < MIN_ANO: continue
    if not (r.get("ad_id") or "").strip().startswith("manual"): continue
    ch = (r.get("canal") or "").strip()
    if ch == "paid_meta": _mm[bu_crm(r)][0] += 1
    elif ch == "paid_google": _mm[bu_crm(r)][1] += 1
_tm = sum(v[0] for v in _mm.values()); _tg = sum(v[1] for v in _mm.values())
FRAC_GLOBAL = _tm / (_tm + _tg) if (_tm + _tg) else 0.5
FRAC_BU = {bu: (v[0] / (v[0] + v[1]) if (v[0] + v[1]) else FRAC_GLOBAL) for bu, v in _mm.items()}
_rz = {}
def rateia_mz(bu):
    """assign determinístico proporcional — mantém a fração meta/google da BU no agregado."""
    f = FRAC_BU.get(bu, FRAC_GLOBAL)
    st = _rz.setdefault(bu, [0, 0])
    st[1] += 1
    if st[0] + 1e-9 < f * st[1]:
        st[0] += 1; return "paid_meta"
    return "paid_google"

# ---- CRM → DEALS (funil, coorte, perdas, qualidade) ----
DEALS = []
# Eventos p/ atribuição ao drill (MQL/SQL/Ganho), ancorados no mês fiscal do LEAD
# (create_at) — alinha o resultado ao mês em que a campanha gastou (CAC de safra da
# campanha; evita "campanha sem investimento com ganho" por lag de fechamento).
EV_MQL, EV_SQL, EV_WIN = [], [], []
for r in crm:
    cd = pdate(r.get("create_at"))
    if not cd or cd.year < MIN_ANO: continue
    w = 1 if truthy(r.get("win")) else 0
    l = 1 if truthy(r.get("lost")) else 0
    wd = pdate(r.get("win_at")) if w else None
    ld = pdate(r.get("lost_at")) if l else None
    md = pdate(r.get("mql_at")); sd = pdate(r.get("sql_at"))
    bu_n = bu_crm(r)
    canal = norm_canal(r.get("canal"))
    z = 0
    if canal == "manual_zendesk":
        canal = rateia_mz(bu_n); z = 1
    # detector canal × clickid divergente (lição Martins): canal diz uma plataforma,
    # clickid/ad_id dizem outra
    gcl = (r.get("gclid") or "").strip(); fbc = (r.get("fbclid") or "").strip()
    aid = (r.get("ad_id") or "").strip()
    sus = 0
    if canal == "paid_google" and ((len(fbc) > 10 and "{" not in fbc)
                                   or (aid.isdigit() and len(aid) >= 15 and aid.startswith("120"))):
        sus = 1
    elif canal == "paid_meta" and len(gcl) > 20 and "{" not in gcl:
        sus = 1
    def _dd(a, b):
        return round((b - a).total_seconds() / 86400, 2) if (a and b and b >= a) else None
    row = {
        "cd": iso(cd), "wd": (iso(wd) if (wd and wd.year >= MIN_ANO) else ""),
        "b": BUI[bu_n], "c": si(canal),
        "mql": 1 if truthy(r.get("mql")) else 0, "sql": 1 if truthy(r.get("sql")) else 0,
        "w": w, "l": l, "v": round(pnum(r.get("total_value")), 2),
        "ci": _dd(cd, wd), "cl": _dd(cd, ld),
    }
    # tempos entre etapas (timing via _at — esparso; omitidos quando ausentes p/ payload leve)
    for k_, v_ in (("tm", _dd(cd, md)), ("ts", _dd(md, sd)), ("tw", _dd(sd, wd))):
        if v_ is not None: row[k_] = v_
    if sus: row["s"] = 1
    if z: row["z"] = 1
    DEALS.append(row)
    _ev = (fm_key(cd), BUI[bu_n], si(canal), aid)
    if row["mql"]: EV_MQL.append(_ev)
    if row["sql"]: EV_SQL.append(_ev)
    if w: EV_WIN.append(_ev)
perdas = collections.Counter((r.get("lost_reason") or "").strip() for r in crm
                             if truthy(r.get("lost")) and (r.get("lost_reason") or "").strip())
PERDAS = [{"motivo": m, "n": n} for m, n in perdas.most_common(12)]

# ---- bd_ads → ADSDAY (inv/impr/clk/mql diário por BU×canal) + DRILL mensal ----
ADSAGG = collections.defaultdict(lambda: {"inv": 0.0, "impr": 0.0, "clk": 0.0, "mq": 0.0})
camps, conjs, anuns = {}, {}, {}
def idx(d, k):
    k = (k or "—").strip() or "—"
    if k not in d: d[k] = len(d)
    return d[k]
DR = collections.defaultdict(lambda: {"inv": 0.0, "impr": 0.0, "clk": 0.0, "mq": 0.0})
AD2CRE = {}   # ad_id → (campanha, conjunto, anúncio) — atribuição direta de fechados
for r in ads:
    d = pdate(r.get("data"))
    if not d or d.year < MIN_ANO: continue
    bu_nm = norm_bu(r.get("funnel")); b = BUI[bu_nm]
    canal = norm_canal(r.get("canal"))
    # mesmo rateio manual_zendesk do CRM (aqui fracionário — linhas já são agregado)
    if canal == "manual_zendesk":
        f = FRAC_BU.get(bu_nm, FRAC_GLOBAL)
        parts = [("paid_meta", f), ("paid_google", 1 - f)]
    else:
        parts = [(canal, 1.0)]
    inv, impr, clk, mq = pnum(r.get("investimento")), pnum(r.get("impressões")), pnum(r.get("ad_clicks")), pnum(r.get("mql"))
    ci, ji, ai = idx(camps, r.get("nome_campanha")), idx(conjs, r.get("nome_conjunto")), idx(anuns, r.get("nome_anuncio"))
    aid = (r.get("ad_id") or "").strip()
    if aid.isdigit(): AD2CRE[aid] = (ci, ji, ai)
    for cn, w in parts:
        c = si(cn)
        k = (iso(d), b, c); n = ADSAGG[k]; n["inv"] += inv * w; n["impr"] += impr * w; n["clk"] += clk * w; n["mq"] += mq * w
        dk = (fm_key(d), b, c, ci, ji, ai); dn = DR[dk]; dn["inv"] += inv * w; dn["impr"] += impr * w; dn["clk"] += clk * w; dn["mq"] += mq * w
ADSDAY = [{"d": k[0], "b": k[1], "c": k[2], "inv": round(v["inv"], 2), "impr": int(v["impr"]), "clk": int(v["clk"]), "mq": int(v["mq"])}
          for k, v in ADSAGG.items()]
DRILL = {"camps": list(camps), "conjs": list(conjs), "anuns": list(anuns),
         "rows": [{"m": k[0], "b": k[1], "c": k[2], "ci": k[3], "ji": k[4], "ai": k[5],
                   "inv": round(v["inv"], 2), "impr": int(v["impr"]), "clk": int(v["clk"]), "mq": int(v["mq"])}
                  for k, v in DR.items() if v["inv"] > 0]}

# ---- funil atribuído ao drill (regra do operador 2026-07-02) ------------------------
# MQL/SQL/Ganho do CRM, MESMO motor pros 3 eventos, ancorados no mês fiscal do LEAD:
#   1. ad_id rastreável E criativo com investimento no mês → atribuição DIRETA;
#   2. senão → distribuído PROPORCIONALMENTE aos rastreáveis do mesmo (mês×BU×canal);
#   3. sem rastreável no recorte → proporcional ao share de INVESTIMENTO do (m,b,c);
#   4. sem nenhuma base → fica sem atribuição (não inventa).
# Por construção, nenhum evento assenta em criativo-mês sem investimento.
def _atribui(events):
    T = collections.defaultdict(float); U = collections.defaultdict(float)
    for m, b, c, aid in events:
        cre = AD2CRE.get(aid)
        k = ((m, b, c) + cre) if cre else None
        if k is not None and DR.get(k, {}).get("inv", 0) > 0: T[k] += 1.0
        else: U[(m, b, c)] += 1.0
    por = collections.defaultdict(list)
    for k, v in list(T.items()): por[k[:3]].append((k, v))
    for mbc, u in U.items():
        base = por.get(mbc)
        if base:
            tot = sum(v for _, v in base)
            for k, v in base: T[k] += u * v / tot
        else:
            drows = [(k, dv["inv"]) for k, dv in DR.items() if k[:3] == mbc and dv["inv"] > 0]
            tot = sum(iv for _, iv in drows)
            if tot:
                for k, iv in drows: T[k] += u * iv / tot
    return T
A_MQL, A_SQL, A_WIN = _atribui(EV_MQL), _atribui(EV_SQL), _atribui(EV_WIN)
EVR = {}
for src, fld in ((A_MQL, "mq"), (A_SQL, "sq"), (A_WIN, "w")):
    for k, v in src.items():
        if v > 0: EVR.setdefault(k, {"mq": 0, "sq": 0, "w": 0})[fld] = round(v, 3)
DRILL["ev"] = [{"m": k[0], "b": k[1], "c": k[2], "ci": k[3], "ji": k[4], "ai": k[5], **v} for k, v in EVR.items()]
print(f"atribuição drill: MQL {sum(A_MQL.values()):.0f}/{len(EV_MQL)} · SQL {sum(A_SQL.values()):.0f}/{len(EV_SQL)} · Ganho {sum(A_WIN.values()):.0f}/{len(EV_WIN)}")
STRS = list(STR)

# ---- receita premissa por BU (contrato → payload compacto) ----
RECEITA = {}
for bu, r in C["receita"].items():
    if (r or {}).get("modelo") == "recorrente":
        RECEITA[bu] = {"t": "rec", "m": float(r.get("mensalidade", 0)), "n": int(r.get("ltv_meses", 0))}
    elif r:
        RECEITA[bu] = {"t": "tcv", "v": float(r.get("valor", 0))}

datas = [x["d"] for x in ADSDAY] + [d["cd"] for d in DEALS]
dmin, dmax = (min(datas), max(datas)) if datas else (C["inicio"], C["fim"])

DADOS = {
    "quarter": C["quarter"], "qini": C["inicio"], "qfim": C["fim"], "fiscal_dia": FD,
    "today": iso(HOJE), "dmin": dmin, "dmax": dmax, "gerado_em": HOJE.strftime("%Y-%m-%d %H:%M"),
    "bul": BUL, "bu_ordem": BU_ORDEM, "canais_meta": C["canais_meta"], "metas": C["metas"],
    "receita": RECEITA,
    "strs": STRS, "deals": DEALS, "adsday": ADSDAY, "drill": DRILL, "perdas": PERDAS,
}

TEMPLATE = r"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor — Grupo Colina</title>
<meta name="source-feed" content="campanhas-ano-corrente.csv + crm-ano-corrente.csv">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
:root{--bg:#0b0f0d;--card:#131916;--elev:#1a221e;--bd:#26302b;--mut:#8ba093;--sub:#5d6b62;
--grn:#1fb083;--grnd:#157a5c;--gold:#d9a441;--red:#e5484d;--amb:#f5a623;--blue:#5b9bd5;--txt:#eef3f0}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--bg);color:var(--txt);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
.topbar{height:4px;background:linear-gradient(90deg,var(--grnd),var(--grn),var(--gold))}
.head{display:flex;justify-content:space-between;align-items:center;max-width:1320px;margin:0 auto;padding:18px 24px 6px}
.head h1{font-size:22px;font-weight:800;margin:0}.head h1 span{color:var(--grn)}.head .ts{color:var(--sub);font-size:12px;font-family:ui-monospace,monospace}
.filterbar{position:sticky;top:0;z-index:40;background:rgba(11,15,13,.88);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd)}
.fb{max-width:1320px;margin:0 auto;padding:11px 24px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center}
.fctl{position:relative}
.fbtn{display:inline-flex;align-items:center;gap:8px;background:var(--elev);border:1px solid var(--bd);color:var(--txt);border-radius:9px;padding:7px 13px;cursor:pointer;font-size:13px}
.fbtn:hover{border-color:var(--grn)}.fbtn .cap{color:var(--sub);font-size:10.5px;text-transform:uppercase;letter-spacing:.5px}
.fbtn .val{font-weight:600}.fbtn .ar{color:var(--mut);font-size:10px}
.pop{position:absolute;top:calc(100% + 6px);left:0;background:var(--card);border:1px solid var(--bd);border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.6);z-index:60;display:none}
.pop.on{display:block}.pop.right{left:auto;right:0}
.dpick{display:flex;min-width:560px}
.presets{flex:none;width:172px;border-right:1px solid var(--bd);padding:8px;max-height:330px;overflow:auto}
.pset{display:block;width:100%;text-align:left;background:none;border:none;color:var(--mut);padding:7px 10px;border-radius:7px;cursor:pointer;font-size:13px}
.pset:hover{background:var(--elev);color:var(--txt)}.pset.on{background:var(--grn);color:#04130d}
.calwrap{padding:12px 14px}.cals{display:flex;gap:18px}.cal{width:210px}
.calhd{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:13px;font-weight:600}
.calnav{background:var(--elev);border:1px solid var(--bd);color:var(--txt);border-radius:6px;width:24px;height:24px;cursor:pointer}
.cgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cgrid .dow{font-size:10px;color:var(--sub);text-align:center;padding:3px 0}
.cd{text-align:center;padding:5px 0;font-size:12px;border-radius:6px;cursor:pointer;color:var(--txt)}
.cd:hover{background:var(--elev)}.cd.out{color:var(--sub);cursor:default}.cd.out:hover{background:none}
.cd.sel{background:var(--grn);color:#04130d;font-weight:700}.cd.inr{background:rgba(31,176,131,.18)}
.cd.cmpr{box-shadow:inset 0 0 0 1px var(--gold)}
.cmpbar{border-top:1px solid var(--bd);margin-top:10px;padding-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.switch{position:relative;width:38px;height:21px;flex:none}.switch input{opacity:0;width:0;height:0}
.sl{position:absolute;inset:0;background:var(--elev);border:1px solid var(--bd);border-radius:999px;transition:.2s}
.sl:before{content:"";position:absolute;height:15px;width:15px;left:2px;top:2px;background:var(--mut);border-radius:50%;transition:.2s}
.switch input:checked+.sl{background:var(--grn);border-color:var(--grn)}.switch input:checked+.sl:before{transform:translateX(17px);background:#fff}
.cmpopt{background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:7px;padding:5px 10px;cursor:pointer;font-size:12.5px}
.cmpopt.on{background:var(--gold);border-color:var(--gold);color:#1a1a1a;font-weight:600}
.popfoot{display:flex;justify-content:flex-end;gap:8px;padding:10px 14px;border-top:1px solid var(--bd)}
.bt{border:1px solid var(--bd);background:var(--elev);color:var(--txt);border-radius:7px;padding:6px 14px;cursor:pointer;font-size:13px}.bt.pri{background:var(--grn);border-color:var(--grn);color:#04130d}
.mspop{min-width:230px;padding:8px}
.chk{display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:7px;cursor:pointer;font-size:13px}.chk:hover{background:var(--elev)}
.chk input{accent-color:var(--grn);width:15px;height:15px}.chquick{display:flex;gap:6px;padding:4px 6px 8px;border-bottom:1px solid var(--bd);margin-bottom:6px}
.qbtn{flex:1;background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:7px;padding:5px;cursor:pointer;font-size:12px}.qbtn:hover{border-color:var(--grn);color:var(--txt)}
.layout{display:flex;gap:24px;max-width:1320px;margin:0 auto;padding:16px 24px 64px}
.sidenav{flex:none;width:176px;position:sticky;top:64px;align-self:flex-start;display:flex;flex-direction:column;gap:3px}
.tab{text-align:left;background:none;border:none;border-left:3px solid transparent;color:var(--mut);padding:9px 12px;border-radius:0 8px 8px 0;cursor:pointer;font-size:13.5px;transition:all .12s}
.tab:hover{background:var(--card);color:var(--txt)}.tab.on{background:var(--card);border-left-color:var(--grn);color:#fff;font-weight:600}
.main{flex:1;min-width:0}
h2{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:26px 0 12px;font-weight:700}h2:first-child{margin-top:4px}
h2 .soft{color:var(--sub);font-weight:400;text-transform:none;letter-spacing:0}
.grid{display:grid;gap:13px}.grid>*{min-width:0}.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.card canvas{max-width:100%}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px}
.okr .t{font-size:11.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}.okr .big{font-size:28px;font-weight:800;margin:5px 0 1px}.okr .m{font-size:12px;color:var(--mut)}
.bar{height:7px;background:#0a120e;border-radius:4px;overflow:hidden;margin:9px 0 5px}.bar>i{display:block;height:100%;border-radius:4px}
.proj{font-size:11.5px;color:var(--sub)}
.s-ok{color:var(--grn)}.s-warn{color:var(--amb)}.s-bad{color:var(--red)}.s-mut{color:var(--sub)}
.kbox{background:var(--card);border:1px solid var(--bd);border-radius:11px;padding:13px 15px}.kbox .l{font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.kbox .n{font-size:23px;font-weight:800;margin:4px 0 1px}.kbox .x{font-size:11.5px;color:var(--sub)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:8px 10px;border-bottom:1px solid var(--bd);text-align:right}th:first-child,td:first-child{text-align:left}
th{color:var(--mut);font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;font-weight:700}tbody tr:hover{background:var(--elev)}
.tw{overflow-x:auto;border:1px solid var(--bd);border-radius:12px}
.funrow{display:flex;align-items:center;gap:12px;margin:7px 0}.fn{width:90px;text-align:right;font-size:13px;color:var(--mut)}
.ft{flex:1;height:32px;background:#0a120e;border-radius:6px;position:relative;overflow:hidden}.ft>i{display:block;height:100%;background:linear-gradient(90deg,var(--grnd),var(--grn));border-radius:6px}
.ft .v{position:absolute;left:10px;top:50%;transform:translateY(-50%);font-weight:800;font-size:14px;color:var(--txt);text-shadow:0 1px 2px rgba(0,0,0,.7)}.fr{width:120px;font-size:12px;color:var(--mut);font-family:ui-monospace,monospace}
.subtabs{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}.stbtn{background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:8px;padding:5px 13px;cursor:pointer;font-size:12.5px}.stbtn.on{background:var(--grn);border-color:var(--grn);color:#04130d}
.deccol h3{font-size:14px;margin:0 0 10px}.decitem{border-left:3px solid var(--bd);padding:7px 11px;margin-bottom:8px;background:var(--elev);border-radius:0 8px 8px 0}.decitem .nm{font-weight:600;font-size:13px}.decitem .mo{font-size:11.5px;color:var(--mut)}
.heat td{text-align:center}.heat td:first-child{text-align:left;position:sticky;left:0;background:var(--card)}
.dre thead th{background:var(--grnd);color:#fff}.dre td:first-child,.dre th:first-child{position:sticky;left:0;text-align:left;font-weight:600;z-index:1;background:var(--card)}.dre thead th:first-child{background:var(--grnd);z-index:2}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700}
.prem{background:rgba(217,164,65,.12);border:1px solid rgba(217,164,65,.4);color:var(--gold)}
canvas{max-height:280px}.chart-lg canvas{max-height:400px;min-height:330px}.chart-sm canvas{max-height:170px;min-height:150px}.note{font-size:12px;color:var(--sub);margin-top:8px}.qlabel{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);margin-bottom:10px;font-weight:700}
.bub{font-size:10.5px;color:var(--sub);text-align:center;max-width:1320px;margin:8px auto 0;padding:0 24px}
@media(max-width:920px){.layout{flex-direction:column}.sidenav{flex-direction:row;flex-wrap:wrap;width:auto;position:static}.tab{border-left:none;border-radius:8px}.g2,.g3{grid-template-columns:1fr}.dpick{flex-direction:column;min-width:300px}.presets{width:auto;border-right:none;border-bottom:1px solid var(--bd)}}
</style></head><body>
<div class="topbar"></div>
<div class="head"><h1>Monitor · <span>Grupo Colina</span></h1><span class="ts" id="ts"></span></div>
<div class="filterbar"><div class="fb">
  <div class="fctl"><button class="fbtn" id="bPeriod" onclick="togPop('popPeriod')"><span class="cap">Período</span><span class="val" id="vPeriod"></span><span class="ar">▾</span></button>
    <div class="pop" id="popPeriod" onclick="event.stopPropagation()"><div class="dpick">
      <div class="presets" id="presets"></div>
      <div class="calwrap"><div class="cals"><div class="cal" id="calA"></div><div class="cal" id="calB"></div></div>
        <div class="cmpbar"><label class="switch"><input type="checkbox" id="cmpTog" onchange="onCmpTog()"><span class="sl"></span></label>
          <span style="font-size:12.5px;color:var(--mut)">Comparar</span><span id="cmpOpts"></span></div></div></div>
      <div class="popfoot"><button class="bt" onclick="closePop()">Cancelar</button><button class="bt pri" onclick="applyPeriod()">Aplicar</button></div></div>
  </div>
  <div class="fctl"><button class="fbtn" id="bBU" onclick="togPop('popBU')"><span class="cap">BU</span><span class="val" id="vBU"></span><span class="ar">▾</span></button>
    <div class="pop mspop" id="popBU" onclick="event.stopPropagation()"><div class="chquick"><button class="qbtn" onclick="buMeta()">só c/ meta</button><button class="qbtn" onclick="buAll()">todas</button></div><div id="buList"></div></div>
  </div>
  <div class="fctl"><button class="fbtn" id="bChan" onclick="togPop('popChan')"><span class="cap">Canal</span><span class="val" id="vChan"></span><span class="ar">▾</span></button>
    <div class="pop right mspop" id="popChan" onclick="event.stopPropagation()"><div class="chquick"><button class="qbtn" onclick="chMeta()">só pagos</button><button class="qbtn" onclick="chAll()">todos</button></div><div id="chanList"></div></div>
  </div>
</div></div>
<p class="bub" id="bub"></p>
<div class="layout"><nav class="sidenav" id="nav"></nav><div class="main" id="main"></div></div>
<script>
const D = __DADOS__;
const SCR=[["geral","Visão Geral"],["bu","Por BU"],["atencao","Atenção"],["funil","Funil & Perdas"],
  ["safra","Safra & Payback"],["midia","Mídia"],["mensal","Mensal"]];
const STRS=D.strs, BUL=D.bul, BU_ORDEM=D.bu_ordem, RC=D.receita;
const CHANNELS=(()=>{let s=new Set();D.deals.forEach(d=>s.add(STRS[d.c]));D.adsday.forEach(x=>s.add(STRS[x.c]));return [...s].sort();})();
let SELCH=new Set(D.canais_meta.filter(c=>CHANNELS.includes(c)));   // default: só pagos (recorte da meta)
let SELBU=new Set(BU_ORDEM);                                        // default: BUs com meta
const fmt=v=>"R$ "+Math.round(v||0).toLocaleString("pt-BR");
const fmt1=v=>(v||0).toLocaleString("pt-BR",{maximumFractionDigits:1});
const n0=v=>Math.round(v||0).toLocaleString("pt-BR");
const pctn=(a,b)=>b?Math.round(a/b*100):0;
const COR={ok:"#1fb083",warn:"#f5a623",bad:"#e5484d"};
// ---- receita premissa ----
function contratoVal(bu){const r=RC[bu];if(!r)return 0;return r.t==="rec"?r.m*r.n:r.v;}
function mensalVal(bu){const r=RC[bu];return (r&&r.t==="rec")?r.m:0;}
const PREM_TXT=BU_ORDEM.filter(b=>RC[b]).map(b=>{const r=RC[b];return r.t==="rec"?`${b} R$ ${r.m}/mês × ${r.n}m`:`${b} R$ ${n0(r.v)} TCV`;}).join(" · ");
// ---- datas ----
const DD=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d);};
const SD=dt=>dt.getFullYear()+"-"+String(dt.getMonth()+1).padStart(2,"0")+"-"+String(dt.getDate()).padStart(2,"0");
const addD=(s,n)=>{const d=DD(s);d.setDate(d.getDate()+n);return SD(d);};
const addM=(s,n)=>{const d=DD(s);d.setMonth(d.getMonth()+n);return SD(d);};
const MES_PT=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
const fmtRange=(a,b)=>{const da=DD(a),db=DD(b);return da.getTime()===db.getTime()?`${da.getDate()} ${MES_PT[da.getMonth()]} ${da.getFullYear()}`
  :`${da.getDate()} ${MES_PT[da.getMonth()]} – ${db.getDate()} ${MES_PT[db.getMonth()]} ${db.getFullYear()}`;};
const today=D.today;
const monthStart=s=>s.slice(0,7)+"-01";
const monthEnd=s=>{const d=DD(s);return SD(new Date(d.getFullYear(),d.getMonth()+1,0));};
const nDays=(a,b)=>Math.round((DD(b)-DD(a))/864e5)+1;
const mIdx=s=>+s.slice(0,4)*12+(+s.slice(5,7)-1);
// ---- MÊS FISCAL Colina: dia 16 → dia 15, NOMEADO pelo mês em que TERMINA ----
// ("julho" = 16/jun–15/jul). Metas, série mensal, safras e payback usam este calendário.
const FD=D.fiscal_dia;
const fmKey=s=>{const y=+s.slice(0,4),m=+s.slice(5,7),d=+s.slice(8,10);
  if(d>=FD)return m===12?(y+1)+"-01":y+"-"+String(m+1).padStart(2,"0");
  return s.slice(0,7);};
const fmStart=k=>{const y=+k.slice(0,4),m=+k.slice(5,7),pm=m===1?12:m-1,py=m===1?y-1:y;
  return py+"-"+String(pm).padStart(2,"0")+"-"+String(FD).padStart(2,"0");};
const fmEnd=k=>k+"-"+String(FD-1).padStart(2,"0");
const fmAdd=(k,n)=>{let y=+k.slice(0,4),m=+k.slice(5,7)+n;while(m>12){m-=12;y++;}while(m<1){m+=12;y--;}return y+"-"+String(m).padStart(2,"0");};
const PRESETS=[
  ["Hoje",()=>[today,today]],["Ontem",()=>[addD(today,-1),addD(today,-1)]],
  ["Últimos 7 dias",()=>[addD(today,-6),today]],["Últimos 14 dias",()=>[addD(today,-13),today]],
  ["Últimos 30 dias",()=>[addD(today,-29),today]],["Este mês",()=>[fmStart(fmKey(today)),today]],
  ["Mês passado",()=>{const p=fmAdd(fmKey(today),-1);return [fmStart(p),fmEnd(p)];}],
  ["Este trimestre",()=>[D.qini,today<D.qfim?today:D.qfim]],
  ["Trimestre passado",()=>[addM(D.qini,-3),addD(D.qini,-1)]],
  ["Este ano",()=>[today.slice(0,4)+"-01-01",today]],["Todo o período",()=>[D.dmin,D.dmax]],
];
let FILT={ini:fmStart(fmKey(today)),fim:today,preset:"Este mês",cmpOn:false,cmpMode:"prev"};   // default: mês fiscal vigente
let DRAFT={...FILT};let calAnchor=monthStart(FILT.ini);let pickStage=0;

// ---- gate de meta: metas medem a Máquina de Aquisição (canais pagos) ----
// Só aparecem quando o filtro de canal == canais_meta exatamente (esconder > mentir).
function periodMeta(){return SELCH.size===D.canais_meta.length&&D.canais_meta.every(c=>SELCH.has(c));}
// ---- META escalonada por dias no range sobre o MÊS FISCAL 16→15 ----
// (meta_mês × dias_no_mês_fiscal_dentro_do_range / dias_do_mês_fiscal)
function metaFactor(ini,fim){
  let f=0,k=fmKey(ini);
  while(fmStart(k)<=fim){const s=fmStart(k),e=fmEnd(k),lo=s>ini?s:ini,hi=e<fim?e:fim;
    if(lo<=hi)f+=nDays(lo,hi)/nDays(s,e);
    k=fmAdd(k,1);}
  return f;
}
function metaBU(bu,campo,factor){const m=(D.metas[bu]||{});return (m[campo]||0)*factor;}
function metaSel(campo,factor){let t=0;for(const bu of SELBU)t+=metaBU(bu,campo,factor);return t;}
function metaRec(factor){let mrr=0,contr=0;
  for(const bu of SELBU){const cg=metaBU(bu,"clientes_geral",factor);mrr+=cg*mensalVal(bu);contr+=cg*contratoVal(bu);}
  return{mrr,contr};}

// ---- agregações filtrando range + BU + canal ----
function inR(d,a,b){return d>=a&&d<=b;}
function dealsCreate(ini,fim){return D.deals.filter(d=>inR(d.cd,ini,fim)&&SELBU.has(BUL[d.b])&&SELCH.has(STRS[d.c]));}
function sumFunil(ini,fim){const ds=dealsCreate(ini,fim);let o={lead:0,mql:0,sql:0,ganho:0,perdido:0,cli_safra:0,ciclos:[],ciclosL:[]};
  for(const d of ds){o.lead++;o.mql+=d.mql;o.sql+=d.sql;o.ganho+=d.w;o.perdido+=d.l;
    if(d.w){o.cli_safra++;if(d.ci!=null)o.ciclos.push(d.ci);}
    if(d.l&&d.cl!=null)o.ciclosL.push(d.cl);}return o;}
function winsBu(ini,fim){const out={};for(const d of D.deals){if(!d.w||!d.wd)continue;const bu=BUL[d.b];
  if(inR(d.wd,ini,fim)&&SELBU.has(bu)&&SELCH.has(STRS[d.c]))out[bu]=(out[bu]||0)+1;}return out;}
function receitaK(ini,fim){const w=winsBu(ini,fim);let mrr=0,contr=0,nw=0;
  for(const bu in w){nw+=w[bu];const r=RC[bu];if(!r)continue;
    if(r.t==="rec"){mrr+=w[bu]*r.m;contr+=w[bu]*r.m*r.n;}else contr+=w[bu]*r.v;}
  return{mrr,contr,nw};}
function sumAds(ini,fim){let o={inv:0,impr:0,clk:0,mq:0};for(const x of D.adsday){if(inR(x.d,ini,fim)&&SELBU.has(BUL[x.b])&&SELCH.has(STRS[x.c])){o.inv+=x.inv;o.impr+=x.impr;o.clk+=x.clk;o.mq+=x.mq;}}return o;}
function median(a){if(!a.length)return 0;const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;}
// KPIs do período (blended das BUs/canais selecionados)
function kpi(ini,fim){const F=sumFunil(ini,fim),A=sumAds(ini,fim),R=receitaK(ini,fim);
  return {...F,...A,cli_geral:R.nw,mrr:R.mrr,contr:R.contr,
    cpmql:F.mql?A.inv/F.mql:0, cpl:F.lead?A.inv/F.lead:0,
    tx_conv:F.mql?F.cli_safra/F.mql:0, cac_safra:F.cli_safra?A.inv/F.cli_safra:0, cac_geral:R.nw?A.inv/R.nw:0,
    ltv_cac:A.inv?R.contr/A.inv:0,
    ciclo:median(F.ciclos),
    ctr:A.impr?A.clk/A.impr*100:0, cpc:A.clk?A.inv/A.clk:0};}
function curK(){return kpi(FILT.ini,FILT.fim);}
function cmpRange(ini,fim,mode){if(mode==="prev"){const days=Math.round((DD(fim)-DD(ini))/864e5)+1;return [addD(ini,-days),addD(ini,-1)];}
  if(mode==="month")return [addM(ini,-1),addM(fim,-1)];if(mode==="year")return [addM(ini,-12),addM(fim,-12)];return null;}
function cmpK(){if(!FILT.cmpOn)return null;const r=cmpRange(FILT.ini,FILT.fim,FILT.cmpMode);return r?kpi(r[0],r[1]):null;}
function mesesRange(){let s=new Set();const a=FILT.ini,b=FILT.fim;
  D.deals.forEach(d=>{if(inR(d.cd,a,b))s.add(fmKey(d.cd));});
  D.adsday.forEach(x=>{if(inR(x.d,a,b))s.add(fmKey(x.d));});return [...s].sort();}
function mesesAll(){let s=new Set();
  D.deals.forEach(d=>s.add(fmKey(d.cd)));
  D.adsday.forEach(x=>s.add(fmKey(x.d)));return [...s].sort();}
function delta(cur,prev,inv){if(prev==null||!isFinite(prev)||prev===0)return"";const d=(cur-prev)/prev*100;
  let up=d>=0;if(inv)up=!up;const cls=up?"s-ok":"s-bad",ar=d>=0?"▲":"▼";return ` <span class="kd ${cls}" style="font-size:12px;font-weight:700">${ar} ${Math.abs(Math.round(d))}%</span>`;}

let CH={};function destroy(){Object.values(CH).forEach(c=>{try{c.destroy()}catch(e){}});CH={};}
const cOpt=ex=>Object.assign({responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:"#8ba093",font:{size:11}}}},scales:{x:{ticks:{color:"#8ba093",font:{size:10}},grid:{color:"#26302b"}},y:{ticks:{color:"#8ba093",font:{size:10}},grid:{color:"#26302b"}}}},ex||{});

// ================= TELAS =================
let FSCR="geral";
// Semáforo (operador 2026-07-02): ≥70% da meta = verde · 60–70% = amarelo · <60% = vermelho.
// Métrica de CUSTO (CPMQL/CAC — menor é melhor): % = meta/realizado (conta inversa).
function pctMeta(real,meta,custo){if(!meta)return 0;return custo?(real>0?meta/real:0):real/meta;}
function stPct(real,meta,custo){const p=pctMeta(real,meta,custo);return p>=.7?"ok":p>=.6?"warn":"bad";}
function okrCard(t,val,o){o=o||{};let body,cor="";
  if(o.meta!=null){const w=Math.min(100,Math.round((o.pct||0)*100));cor="s-"+o.st;
    body=`<div class="m">meta ${o.metaTxt} · ${Math.round((o.pct||0)*100)}%</div><div class="bar"><i style="width:${w}%;background:${COR[o.st]}"></i></div>${o.proj||""}`;}
  else body=`<div class="m">${o.sub||"&nbsp;"}</div>`;
  return `<div class="card okr"><div class="t">${t}</div><div class="big ${cor}">${val}${o.delta||""}</div>${body}</div>`;}
// pacing: período em andamento (contém hoje) → projeta o fim do período no ritmo atual
function prj(real,metaFull,fm){if(today<=FILT.ini||today>FILT.fim)return"";
  const el=nDays(FILT.ini,today),tt=nDays(FILT.ini,FILT.fim);if(el>=tt||!real)return"";
  const p=real/el*tt,pc=metaFull?Math.round(p/metaFull*100):0;
  return `<div class="proj">ritmo → ${fm(p)}${metaFull?` · ${pc}% da meta no fim do período`:""}</div>`;}
function rGeral(){const K=curK(),P=cmpK(),f=metaFactor(FILT.ini,FILT.fim),SM=periodMeta();
  const mInv=SM?metaSel("investimento",f):null,mMql=SM?metaSel("mql",f):null,
        mCs=SM?metaSel("clientes_safra",f):null,mCg=SM?metaSel("clientes_geral",f):null;
  const mCpmql=SM&&mMql?mInv/mMql:null,mCacS=SM&&mCs?mInv/mCs:null,mCacG=SM&&mCg?mInv/mCg:null,mTx=SM&&mMql?mCs/mMql:null;
  const MR=SM?metaRec(f):null;
  const dl=(a,b,inv)=>(P&&b!=null)?delta(a,b,inv):"";
  const M=(meta,txt,pct,st,proj)=>SM&&meta?{meta,metaTxt:txt,pct,st,proj}:{};
  let h=`<h2>OKR do período — realizado${SM?" vs meta":""}${P?` <span class="soft">· vs ${({prev:"período ant.",month:"mês ant.",year:"ano ant."}[FILT.cmpMode])}</span>`:""}</h2><div class="grid g4">`;
  h+=okrCard("Investimento",fmt(K.inv),{...M(mInv,fmt(mInv),pctMeta(K.inv,mInv),stPct(K.inv,mInv),prj(K.inv,mInv,fmt)),delta:dl(K.inv,P&&P.inv),sub:"mídia paga"});
  h+=okrCard("MQL",n0(K.mql),{...M(mMql,n0(mMql),pctMeta(K.mql,mMql),stPct(K.mql,mMql),prj(K.mql,mMql,n0)),delta:dl(K.mql,P&&P.mql),sub:"CRM (flag)"});
  h+=okrCard("CPMQL",K.mql?fmt(K.cpmql):"—",{...M(mCpmql,fmt(mCpmql),pctMeta(K.cpmql,mCpmql,true),stPct(K.cpmql,mCpmql,true)),delta:dl(K.cpmql,P&&P.cpmql,true),sub:"invest ÷ MQL"});
  h+=okrCard("Novos Clientes (Safra)",n0(K.cli_safra),{...M(mCs,n0(mCs),pctMeta(K.cli_safra,mCs),stPct(K.cli_safra,mCs),prj(K.cli_safra,mCs,n0)),delta:dl(K.cli_safra,P&&P.cli_safra),sub:"lead do período que fechou"});
  h+=okrCard("Fechados no Período",n0(K.cli_geral),{...M(mCg,n0(mCg),pctMeta(K.cli_geral,mCg),stPct(K.cli_geral,mCg),prj(K.cli_geral,mCg,n0)),delta:dl(K.cli_geral,P&&P.cli_geral),sub:"ganhos no período (win_at)"});
  h+=okrCard("CAC (Safra)",K.cli_safra?fmt(K.cac_safra):"—",{...M(mCacS,fmt(mCacS),pctMeta(K.cac_safra,mCacS,true),stPct(K.cac_safra,mCacS,true)),delta:dl(K.cac_safra,P&&P.cac_safra,true),sub:"invest ÷ cli. safra"});
  h+=okrCard("CAC (Fechados)",K.cli_geral?fmt(K.cac_geral):"—",{...M(mCacG,fmt(mCacG),pctMeta(K.cac_geral,mCacG,true),stPct(K.cac_geral,mCacG,true)),delta:dl(K.cac_geral,P&&P.cac_geral,true),sub:"invest ÷ fechados"});
  h+=okrCard("Taxa de Conversão",fmt1(K.tx_conv*100)+"%",{...M(mTx,fmt1((mTx||0)*100)+"%",pctMeta(K.tx_conv,mTx),stPct(K.tx_conv,mTx)),delta:dl(K.tx_conv,P&&P.tx_conv),sub:"cli. safra ÷ MQL"});
  h+=`</div>
  <h2>Receita do modelo <span class="pill prem">premissa</span> <span class="soft">· ${PREM_TXT} — total_value vazio no CRM</span></h2><div class="grid g4">`;
  h+=okrCard("MRR Novo",fmt(K.mrr),{...M(MR&&MR.mrr,fmt(MR&&MR.mrr),K.mrr/((MR&&MR.mrr)||1),stPct(K.mrr,MR&&MR.mrr),prj(K.mrr,MR&&MR.mrr,fmt)),delta:dl(K.mrr,P&&P.mrr),sub:"planos ganhos × mensalidade"});
  h+=okrCard("Receita Contratada",fmt(K.contr),{...M(MR&&MR.contr,fmt(MR&&MR.contr),K.contr/((MR&&MR.contr)||1),stPct(K.contr,MR&&MR.contr),prj(K.contr,MR&&MR.contr,fmt)),delta:dl(K.contr,P&&P.contr),sub:"LTV planos + TCV one-time"});
  h+=okrCard("LTV:CAC",K.inv?fmt1(K.ltv_cac)+"×":"—",{...M(SM&&mInv&&MR?MR.contr/mInv:null,SM&&mInv&&MR?fmt1(MR.contr/mInv)+"×":"",K.ltv_cac/((SM&&mInv&&MR?MR.contr/mInv:0)||1),stPct(K.ltv_cac,SM&&mInv&&MR?MR.contr/mInv:null)),delta:dl(K.ltv_cac,P&&P.ltv_cac),sub:"receita contratada ÷ invest"});
  h+=okrCard("Contrato Médio",K.cli_geral?fmt(K.contr/K.cli_geral):"—",{sub:"receita contratada ÷ cliente",delta:dl(K.cli_geral?K.contr/K.cli_geral:0,P&&P.cli_geral?P.contr/P.cli_geral:null)});
  h+=`</div>
   <h2>Investimento × Novos Clientes × CAC Safra (por mês fiscal) <span class="soft">· mês Colina = dia 16 → dia 15, nomeado pelo mês em que termina</span></h2><div class="card chart-lg"><canvas id="cGeral"></canvas></div>
   <h2>Funil do período — volume · ritmo · forecast</h2><div class="grid g3">${funVolCard(K)}${ritmoCard()}${forecastCard(K)}</div>`;
  return h;}
function funVolCard(K){const fimEf=today<FILT.fim?(today>FILT.ini?today:FILT.ini):FILT.fim;
  const el=Math.max(1,nDays(FILT.ini,fimEf));
  const steps=[["Lead",K.lead],["MQL",K.mql],["SQL",K.sql],["Ganho",K.ganho]];
  const max=Math.max(1,K.lead);let rows="";
  steps.forEach((s,i)=>{const prev=i?steps[i-1][1]:s[1];const conv=prev?Math.round(s[1]/prev*100):0;
    rows+=`<div class="funrow"><div class="fn" style="width:48px">${s[0]}</div><div class="ft"><i style="width:${Math.max(2,Math.round(s[1]/max*100))}%"></i><span class="v">${n0(s[1])}</span></div><div class="fr" style="width:40px">${i?conv+"%":"&nbsp;"}</div></div>`;});
  return `<div class="card"><div class="qlabel">Volume — Lead › MQL › SQL › Ganho</div>${rows}
    <div class="note">média/dia: ${fmt1(K.lead/el)} leads · ${fmt1(K.mql/el)} MQL · ${fmt1(K.cli_safra/el)} clientes</div></div>`;}
// Velocidade do funil: janela FIXA de 180 dias (tiragem do período selecionado é curta
// demais p/ mediana de tempo) · comparativo = os 180 dias anteriores.
const RITMO_D=180;
function stageTimes(ini,fim){const a={tm:[],ts:[],tw:[],ci:[]};
  for(const d of D.deals){if(d.cd<ini||d.cd>fim)continue;
    if(!SELBU.has(BUL[d.b])||!SELCH.has(STRS[d.c]))continue;
    if(d.tm!=null)a.tm.push(d.tm);if(d.ts!=null)a.ts.push(d.ts);if(d.tw!=null)a.tw.push(d.tw);if(d.ci!=null)a.ci.push(d.ci);}
  return a;}
function ritmoWins(){return{T:stageTimes(addD(today,-(RITMO_D-1)),today),P:stageTimes(addD(today,-(2*RITMO_D-1)),addD(today,-RITMO_D))};}
const fmtDur=v=>v<1?Math.round(v*24)+"h":fmt1(v)+"d";
function ritmoCard(){const{T,P}=ritmoWins();
  const li=(lbl,arr,parr)=>{const d=(arr.length&&parr.length)?delta(median(arr),median(parr),true):"";
    return `<div class="funrow"><div class="fn" style="width:110px">${lbl}</div><div style="font-weight:800;font-size:17px">${arr.length?fmtDur(median(arr)):"—"}${d}</div><div class="fr" style="width:auto;font-family:inherit"><span class="s-mut" style="font-size:11px">n=${n0(arr.length)}</span></div></div>`;};
  return `<div class="card"><div class="qlabel">Ritmo — mediana entre etapas (últimos ${RITMO_D}d vs ${RITMO_D}d anteriores)</div>`+
    li("Lead → MQL",T.tm,P.tm)+li("MQL → SQL",T.ts,P.ts)+li("SQL → Ganho",T.tw,P.tw)+li("Lead → Ganho",T.ci,P.ci)+`</div>`;}
function forecastCard(K){
  // "Este mês" termina em HOJE → o forecast projeta até o FIM do mês fiscal vigente.
  const mesVig=FILT.ini===fmStart(fmKey(today))&&FILT.fim===today;
  const natEnd=mesVig?fmEnd(fmKey(today)):FILT.fim;
  const tt=nDays(FILT.ini,natEnd),elReal=nDays(FILT.ini,(today<FILT.fim?today:FILT.fim));
  const ativo=today>FILT.ini&&today<=natEnd&&elReal<tt;
  if(!ativo)return `<div class="card"><div class="qlabel">Forecast do período</div><div class="note">Período encerrado (ou futuro) — forecast só aparece em período em andamento.</div></div>`;
  const el=elReal,f=tt/el,SM=periodMeta();
  const fFull=metaFactor(FILT.ini,natEnd);
  const mInv=SM?metaSel("investimento",fFull):null,mMql=SM?metaSel("mql",fFull):null,
        mCs=SM?metaSel("clientes_safra",fFull):null,mCg=SM?metaSel("clientes_geral",fFull):null;
  const pInv=K.inv*f,pMql=K.mql*f,pCli=K.cli_safra*f,pCliG=K.cli_geral*f,pCac=pCli?pInv/pCli:0;
  const li=(lbl,val,meta,fm,menor)=>{const pc=SM&&meta?Math.round(pctMeta(val,meta,menor)*100):null;
    const st=pc==null?"":pc>=70?"ok":pc>=60?"warn":"bad";
    return `<div class="funrow"><div class="fn" style="width:118px">${lbl}</div><div style="font-weight:800;font-size:17px">${fm(val)}</div><div class="fr" style="width:auto;font-family:inherit">${pc!=null?`<span class="s-${st}">${pc}% da meta</span>`:""}</div></div>`;};
  return `<div class="card"><div class="qlabel">Forecast ${mesVig?"do mês fiscal":"do período"} (${el}/${tt} dias · até ${fmtRange(natEnd,natEnd)})</div>`+
    li("Investimento",pInv,mInv,fmt,true)+
    li("MQL",pMql,mMql,v=>n0(v),false)+
    li("Clientes (Safra)",pCli,mCs,v=>fmt1(v),false)+
    li("Clientes Fechados",pCliG,mCg,v=>fmt1(v),false)+
    li("CAC (Safra)",pCac,(SM&&mCs&&mInv)?mInv/mCs:null,fmt,true)+
    `<div class="note">projeção linear no ritmo atual</div></div>`;}
function funilHTML(K){const steps=[["Lead",K.lead],["MQL",K.mql],["SQL",K.sql],["Ganho",K.ganho]];
  const max=Math.max(1,K.lead);let h="";
  steps.forEach((s,i)=>{const prev=i?steps[i-1][1]:s[1];const conv=prev?Math.round(s[1]/prev*100):0;
    h+=`<div class="funrow"><div class="fn">${s[0]}</div><div class="ft"><i style="width:${Math.max(2,Math.round(s[1]/max*100))}%"></i><span class="v">${n0(s[1])}</span></div><div class="fr">${i?conv+"% do passo ant.":"&nbsp;"}</div></div>`;});
  const lw=K.lead?Math.round(K.ganho/K.lead*100):0;
  h+=`<div class="note">Lead→Ganho: ${lw}% · MQL→Ganho: ${K.mql?Math.round(K.ganho/K.mql*100):0}% · ciclo mediano ${fmt1(K.ciclo)}d · <span class="s-mut">receita = premissa (total_value vazio no CRM)</span></div>`;return h;}
function buAgg(ini,fim){const sc=SELBU;const out=[];
  for(const bu of [...BU_ORDEM,BUL[BUL.length-1]]){SELBU=new Set([bu]);const k=kpi(ini,fim);out.push({bu,...k});}
  SELBU=sc;return out;}
function rBU(){const f=metaFactor(FILT.ini,FILT.fim),SM=periodMeta();
  const rows=buAgg(FILT.ini,FILT.fim).filter(r=>BU_ORDEM.includes(r.bu)||r.inv>0||r.lead>0);
  let h=`<h2>Resultado por BU — período selecionado</h2><div class="tw"><table><thead><tr>
    <th>BU</th><th>Investimento</th><th>MQL</th><th>CPMQL</th><th>Tx Conv</th><th>Cli. Safra</th><th>Fechados</th><th>CAC (Fechados)</th><th>Receita Contratada*</th><th>LTV:CAC*</th></tr></thead><tbody>`;
  const cellMeta=(real,meta,inv)=>{if(!SM||!meta)return "";const p=real/meta,st=stPct(real,meta,inv);return ` <span class="s-${st}" style="font-size:11px">${Math.round(p*100)}%</span>`;};
  rows.forEach(r=>{const m=D.metas[r.bu]||{},comMeta=BU_ORDEM.includes(r.bu);
    const mi=(m.investimento||0)*f,mm=(m.mql||0)*f,mcs=(m.clientes_safra||0)*f,mcg=(m.clientes_geral||0)*f;
    h+=`<tr><td><strong>${r.bu}</strong>${RC[r.bu]?(RC[r.bu].t==="rec"?' <span class="s-mut" style="font-size:10px">rec</span>':' <span class="s-mut" style="font-size:10px">tcv</span>'):''}</td>
      <td>${fmt(r.inv)}${comMeta?cellMeta(r.inv,mi):""}</td>
      <td>${n0(r.mql)}${comMeta?cellMeta(r.mql,mm):""}</td>
      <td>${r.mql?fmt(r.cpmql):"—"}</td>
      <td>${fmt1(r.tx_conv*100)}%</td>
      <td>${n0(r.cli_safra)}${comMeta?cellMeta(r.cli_safra,mcs):""}</td>
      <td>${n0(r.cli_geral)}${comMeta?cellMeta(r.cli_geral,mcg):""}</td>
      <td>${r.cli_geral?fmt(r.cac_geral):"—"}</td>
      <td>${fmt(r.contr)}</td>
      <td>${r.inv?fmt1(r.ltv_cac)+"×":"—"}</td></tr>`;});
  h+=`</tbody></table></div><p class="note">* receita/LTV = <span class="pill prem">premissa</span> ${PREM_TXT}. `+
     (SM?`% = realizado vs meta (escalada p/ ${fmt1(f)} mês-equivalente do range).`:`Metas ocultas — o recorte de canal difere dos canais da meta (${D.canais_meta.join(" + ")}).`)+`</p>`;
  h+=`<h2>Mídia × funil por BU <span class="soft">· um gráfico por métrica — escalas independentes</span></h2><div class="grid g3">`+
    [["cBu0","Investimento"],["cBu1","MQL"],["cBu2","CPMQL"],["cBu3","Novos Clientes (Safra)"],["cBu4","CAC (Safra)"],["cBu5","LTV:CAC (premissa)"]]
      .map(([id,lb])=>`<div class="card chart-sm"><div class="qlabel">${lb}</div><canvas id="${id}"></canvas></div>`).join("")+`</div>`;
  return h;}
// ---- Atenção: pontos cegos de dado + veredito por canal e por BU ----
function canalAgg(all){const sc=SELCH;const lista=all?CHANNELS:CHANNELS.filter(c=>SELCH.has(c));
  const out=lista.map(c=>{SELCH=new Set([c]);const A=sumAds(FILT.ini,FILT.fim),F=sumFunil(FILT.ini,FILT.fim),R=receitaK(FILT.ini,FILT.fim);SELCH=sc;
    return {c,inv:A.inv,impr:A.impr,clk:A.clk,mqAds:A.mq,mql:F.mql,lead:F.lead,sql:F.sql,ganho:F.ganho,cli_geral:R.nw,contr:R.contr,
      cpmql:F.mql?A.inv/F.mql:0,cac:R.nw?A.inv/R.nw:0,ltv_cac:A.inv?R.contr/A.inv:0,
      ctr:A.impr?A.clk/A.impr*100:0,cpc:A.clk?A.inv/A.clk:0};});
  SELCH=sc;return out.sort((a,b)=>b.inv-a.inv);}
function rAtencao(){const ds=dealsCreate(FILT.ini,FILT.fim),n=ds.length||1;
  const wins=ds.filter(d=>d.w),nw=wins.length||1;
  const semCanal=ds.filter(d=>STRS[d.c]==="(sem canal)").length;
  const outros=ds.filter(d=>BUL[d.b]===BUL[BUL.length-1]).length;
  const semValor=wins.filter(d=>d.v<=0).length;
  const sus=ds.filter(d=>d.s).length;
  const kb=(l,val,sub,bad)=>`<div class="kbox"><div class="l">${l}</div><div class="n ${bad?'s-bad':''}">${val}</div><div class="x">${sub}</div></div>`;
  let h=`<h2>Pontos cegos — qualidade do dado (período · recorte atual)</h2><div class="grid g4">`;
  h+=kb("Leads sem canal",n0(semCanal),pctn(semCanal,n)+"% dos leads",semCanal/n>.15);
  h+=kb("Leads fora das BUs de meta",n0(outros),pctn(outros,n)+"% (Outros/Receptivo)",false);
  h+=kb("Ganhos sem total_value",n0(semValor),pctn(semValor,nw)+"% — backfill growthpack pendente; receita segue premissa",semValor/nw>.5);
  h+=kb("Canal × clickid divergentes",n0(sus),pctn(sus,n)+"% — canal diz uma plataforma, gclid/fbclid/ad_id dizem outra",sus/n>.03);
  h+=`</div>`;
  // veredito por canal (só pagos com invest) — CPMQL e CAC vs meta derivada do recorte
  const f=metaFactor(FILT.ini,FILT.fim),SM=periodMeta();
  const mInv=metaSel("investimento",f),mMql=metaSel("mql",f),mCg=metaSel("clientes_geral",f);
  const mCpmql=mMql?mInv/mMql:0,mCacG=mCg?mInv/mCg:0;
  const rows=canalAgg(true).filter(r=>r.inv>0);
  const score=r=>{if(!mCpmql)return 1;return r.mql?r.cpmql/mCpmql:99;};
  const cortar=rows.filter(r=>score(r)>=1.5),escalar=rows.filter(r=>score(r)<=1),inv=rows.filter(r=>score(r)>1&&score(r)<1.5);
  const item=r=>`<div class="decitem" style="border-left-color:${COR[score(r)<=1?'ok':score(r)<1.5?'warn':'bad']}"><div class="nm">${r.c}</div><div class="mo">CPMQL ${r.mql?fmt(r.cpmql):"—"} (meta ${fmt(mCpmql)}) · CAC ${r.cli_geral?fmt(r.cac):"—"} (meta ${fmt(mCacG)}) · inv ${fmt(r.inv)}</div></div>`;
  const col=(t,cls,ic,arr)=>`<div class="card deccol"><h3 class="s-${cls}">${ic} ${t}</h3>`+(arr.length?arr.map(item).join(""):'<div class="mo s-mut">—</div>')+`</div>`;
  h+=`<h2>Veredito por canal — CPMQL vs meta <span class="soft">· BUs selecionadas</span></h2><div class="grid g3">${col("Cortar","bad","✂",cortar)}${col("Escalar","ok","▲",escalar)}${col("Investigar","warn","◉",inv)}</div>`;
  // veredito por BU (meta própria)
  const bur=buAgg(FILT.ini,FILT.fim).filter(r=>BU_ORDEM.includes(r.bu)&&(r.inv>0||r.mql>0));
  const scoreB=r=>{const m=D.metas[r.bu]||{};const mc=(m.mql||0)*f?((m.investimento||0)*f)/((m.mql||0)*f):0;return mc&&r.mql?r.cpmql/mc:99;};
  const itemB=r=>{const m=D.metas[r.bu]||{};const mc=(m.mql||0)*f?((m.investimento||0)*f)/((m.mql||0)*f):0;
    return `<div class="decitem" style="border-left-color:${COR[scoreB(r)<=1?'ok':scoreB(r)<1.5?'warn':'bad']}"><div class="nm">${r.bu}</div><div class="mo">CPMQL ${r.mql?fmt(r.cpmql):"—"} (meta ${fmt(mc)}) · MQL ${n0(r.mql)}/${n0((m.mql||0)*f)} · LTV:CAC ${r.inv?fmt1(r.ltv_cac)+"×":"—"}</div></div>`;};
  const bC=bur.filter(r=>scoreB(r)>=1.5),bE=bur.filter(r=>scoreB(r)<=1),bI=bur.filter(r=>scoreB(r)>1&&scoreB(r)<1.5);
  const colB=(t,cls,ic,arr)=>`<div class="card deccol"><h3 class="s-${cls}">${ic} ${t}</h3>`+(arr.length?arr.map(itemB).join(""):'<div class="mo s-mut">—</div>')+`</div>`;
  h+=`<h2>Veredito por BU — CPMQL vs meta da BU</h2><div class="grid g3">${colB("Cortar","bad","✂",bC)}${colB("Escalar","ok","▲",bE)}${colB("Investigar","warn","◉",bI)}</div>`;
  h+=`<div class="note">${SM?"":"⚠ recorte de canal difere dos canais da meta — vereditos usam a meta cheia como referência aproximada. "}Jazigo/Serviços têm n pequeno e ciclo longo (TCV) — confirmar em janela maior (preset "Este trimestre") antes de cortar.</div>`;
  return h;}
function velHTML(){const ini=addD(today,-(RITMO_D-1)),fim=today,ci=[],cl=[];
  for(const d of D.deals){if(d.cd<ini||d.cd>fim)continue;
    if(!SELBU.has(BUL[d.b])||!SELCH.has(STRS[d.c]))continue;
    if(d.w&&d.ci!=null)ci.push(d.ci);if(d.l&&d.cl!=null)cl.push(d.cl);}
  const stat=a=>{if(!a.length)return{med:0,avg:0,p25:0,p75:0,n:0};const s=[...a].sort((x,y)=>x-y),q=f=>s[Math.min(s.length-1,Math.floor(f*s.length))];return{med:median(a),avg:a.reduce((x,y)=>x+y,0)/a.length,p25:q(.25),p75:q(.75),n:a.length};};
  const G=stat(ci),P=stat(cl);
  const card=(t,s,cor)=>`<div class="card" style="border-left:3px solid ${cor}"><div class="qlabel">${t} — mediana</div><div style="font-size:27px;font-weight:800">${fmtDur(s.med)}</div><div class="s-mut" style="font-size:12px">média ${fmt1(s.avg)}d · P25 ${fmt1(s.p25)}d · P75 ${fmt1(s.p75)}d · n=${n0(s.n)}</div></div>`;
  return `<div class="grid g2">${card("Ganhas (create → win)",G,"#d9a441")}${card("Perdidas (create → lost)",P,"#e5484d")}</div>`;}
function rFunil(){
  let h=`<h2>Funil de aquisição (período)</h2><div class="card" id="funbox2"></div>`;
  const{T,P}=ritmoWins();
  h+=`<h2>Velocidade entre etapas — mediana (últimos ${RITMO_D}d vs ${RITMO_D}d anteriores)</h2><div class="grid g4">`;
  [["Lead → MQL",T.tm,P.tm],["MQL → SQL",T.ts,P.ts],["SQL → Ganho",T.tw,P.tw],["Lead → Ganho",T.ci,P.ci]].forEach(([lb,arr,parr])=>{
    const d=(arr.length&&parr.length)?delta(median(arr),median(parr),true):"";
    h+=`<div class="kbox"><div class="l">${lb}</div><div class="n">${arr.length?fmtDur(median(arr)):"—"}${d}</div><div class="x">n=${n0(arr.length)} (timing via _at, esparso)</div></div>`;});
  h+=`</div>`;
  h+=`<h2>Velocidade — criação → fechamento (últimos ${RITMO_D}d)</h2>`+velHTML();
  const totp=D.perdas.reduce((a,b)=>a+b.n,0)||1;
  h+=`<h2>Motivos de perda (top 12 · base total)</h2><div class="tw"><table><thead><tr><th>Motivo</th><th>Qtd</th><th>%</th></tr></thead><tbody>`+
     D.perdas.map(p=>`<tr><td>${p.motivo}</td><td>${n0(p.n)}</td><td>${pctn(p.n,totp)}%</td></tr>`).join("")+`</tbody></table></div>`;
  return h;}
// ---- Safra & Payback (SEMPRE todas as safras — período global não recorta esta tela;
// filtros de BU e canal aplicam) ----
function cohortConv(){const base={},mat={},maxoff=6;
  for(const d of D.deals){const bu=BUL[d.b];if(!SELBU.has(bu)||!SELCH.has(STRS[d.c]))continue;
    const s=fmKey(d.cd);base[s]=(base[s]||0)+1;
    if(d.w&&d.wd){const off=Math.max(0,mIdx(fmKey(d.wd))-mIdx(s));
      if(off<=maxoff){(mat[s]=mat[s]||{});mat[s][off]=(mat[s][off]||0)+1;}}}
  return{base,mat,maxoff,safras:Object.keys(base).sort()};}
function paybackRows(){const safras={};
  for(const d of D.deals){if(!d.w||!d.wd)continue;const bu=BUL[d.b];
    if(!SELBU.has(bu)||!SELCH.has(STRS[d.c]))continue;
    const m=fmKey(d.wd);(safras[m]=safras[m]||{})[bu]=(safras[m][bu]||0)+1;}
  const meses=Object.keys(safras).sort();
  return meses.map(m=>{const w=safras[m];
    const sc=SELBU;const inv=sumAds(fmStart(m),fmEnd(m)).inv;
    const nw=Object.values(w).reduce((a,b)=>a+b,0);
    const cum=k=>{let c=0;for(const bu in w){const r=RC[bu];if(!r)continue;
      c+=r.t==="rec"?w[bu]*r.m*Math.min(k+1,r.n):w[bu]*r.v;}return c;};
    const maxN=Math.max(1,...Object.keys(w).map(bu=>RC[bu]&&RC[bu].t==="rec"?RC[bu].n:1));
    let pb=null;for(let k=0;k<maxN;k++){if(inv>0&&cum(k)>=inv){pb=k;break;}}
    return{m,inv,nw,cums:[0,1,2,3,4,5,6].map(cum),pb,pago:inv>0&&cum(maxN-1)>=inv};});}
let SAFKEY="taxa";
function setSaf(k){SAFKEY=k;renderAll();}
function rSafra(){const co=cohortConv();
  // máximo de clientes acumulados (p/ intensidade da visão Clientes)
  let maxAcc=1;co.safras.forEach(s=>{let a=0;for(let k=0;k<=co.maxoff;k++)a+=(co.mat[s]||{})[k]||0;if(a>maxAcc)maxAcc=a;});
  const VIS={taxa:"Taxa de conversão",cli:"Clientes",cac:"CAC da safra"};
  let h=`<h2>Maturação da safra — ${VIS[SAFKEY]} até M+k <span class="soft">· safra = mês FISCAL (16→15) do lead · TODAS as safras (o período global não recorta esta tela) · filtros de BU e canal aplicam</span></h2>
    <div class="subtabs">${Object.entries(VIS).map(([k,l])=>`<button class="stbtn ${SAFKEY===k?'on':''}" onclick="setSaf('${k}')">${l}</button>`).join("")}</div>
    <div class="tw"><table class="heat"><thead><tr><th>Safra</th><th>Leads</th><th>Invest.</th>`;
  for(let k=0;k<=co.maxoff;k++)h+=`<th>M+${k}</th>`;h+=`</tr></thead><tbody>`;
  co.safras.forEach(s=>{const b=co.base[s]||0;if(b<5)return;
    const inv=sumAds(fmStart(s),fmEnd(s)).inv;
    h+=`<tr><td>${s}</td><td>${n0(b)}</td><td>${fmt(inv)}</td>`;
    let acc=0;
    for(let k=0;k<=co.maxoff;k++){const cell=(co.mat[s]||{})[k]||0;acc+=cell;
      const fut=mIdx(s)+k>mIdx(fmKey(today));
      if(fut){h+=`<td class="s-mut">·</td>`;continue;}
      if(SAFKEY==="taxa"){const p=b?acc/b:0;
        h+=`<td style="background:rgba(31,176,131,${(p?0.08+Math.min(0.62,p*4):0).toFixed(2)})">${p?fmt1(p*100)+"%":"·"}</td>`;}
      else if(SAFKEY==="cli"){
        h+=`<td style="background:rgba(31,176,131,${(acc?0.08+Math.min(0.62,acc/maxAcc*0.62):0).toFixed(2)})">${acc?n0(acc):"·"}</td>`;}
      else{const cac=(acc&&inv>0)?inv/acc:null;
        h+=`<td style="background:rgba(217,164,65,${(cac?0.08+Math.min(0.55,acc/b*3):0).toFixed(2)})">${cac?fmt(cac):"·"}</td>`;}}
    h+=`</tr>`;});
  const NOTA={taxa:"Célula = % da safra que virou cliente até M+k (win_at).",
    cli:"Célula = clientes acumulados da safra até M+k — mostra o volume da safra crescendo com a maturação.",
    cac:"Célula = investimento do mês da safra ÷ clientes acumulados até M+k — mostra o CAC da safra caindo conforme ela matura."};
  h+=`</tbody></table></div><div class="note">${NOTA[SAFKEY]} "·" = futuro ou zero. Base &lt;5 leads omitida.</div>`;
  const rows=paybackRows();
  h+=`<h2>Payback de mídia por safra de fechamento <span class="pill prem">premissa</span> <span class="soft">· safra = mês FISCAL (16→15) do win · TODAS as safras · receita acumulada vs investimento do mês · ${PREM_TXT}</span></h2>
    <div class="tw"><table class="heat"><thead><tr><th>Safra (win)</th><th>Invest.</th><th>Clientes</th>`;
  for(let k=0;k<=6;k++)h+=`<th>M+${k}</th>`;h+=`<th>Payback</th></tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr><td>${r.m}</td><td>${fmt(r.inv)}</td><td>${n0(r.nw)}</td>`;
    for(let k=0;k<=6;k++){const c=r.cums[k],ok=r.inv>0&&c>=r.inv;
      h+=`<td style="background:rgba(${ok?'31,176,131':'217,164,65'},${Math.min(0.55,(r.inv?c/r.inv:0)*0.35+0.06).toFixed(2)})">${fmt(c)}</td>`;}
    const badge=r.pb!=null?`<span class="s-ok">M+${r.pb}</span>`:(r.inv>0?(r.pago?`<span class="s-warn">&gt; M+6</span>`:`<span class="s-bad">não paga em 18m</span>`):"—");
    h+=`<td>${badge}</td></tr>`;});
  h+=`</tbody></table></div>
  <div class="note">Receita acumulada da safra: planos = clientes × mensalidade × meses decorridos (teto 18m); Jazigo/Serviços = TCV cheio no M0 (contrato conta inteiro mesmo parcelado). Investimento = mídia do mês da safra no recorte atual (sem FEE — decisão 2026-07-02). Meses M+k além de hoje são projeção da premissa de permanência. Retenção real (churn) desligada — sem dado no feed.</div>`;
  return h;}
let DRILLKEY="camp";
function rMidia(){const rows=canalAgg(false);
  let h=`<h2>Investimento por canal (período · BUs selecionadas)</h2><div class="tw"><table><thead><tr><th>Canal</th><th>Invest</th><th>Impr</th><th>Cliques</th><th>CTR</th><th>CPC</th><th>MQL</th><th>CPMQL</th><th>Fechados</th><th>CAC</th><th>LTV:CAC*</th></tr></thead><tbody>`;
  h+=rows.filter(r=>r.inv>0||r.lead>0).map(r=>`<tr><td>${r.c}${D.canais_meta.includes(r.c)?' <span class="s-ok">●</span>':''}</td><td>${fmt(r.inv)}</td><td>${n0(r.impr)}</td><td>${n0(r.clk)}</td><td>${fmt1(r.ctr)}%</td><td>${fmt(r.cpc)}</td><td>${n0(r.mql)}</td><td>${r.mql?fmt(r.cpmql):"—"}</td><td>${n0(r.cli_geral)}</td><td>${r.cli_geral?fmt(r.cac):"—"}</td><td>${r.inv?fmt1(r.ltv_cac)+"×":"—"}</td></tr>`).join("");
  h+=`</tbody></table></div><p class="note">* LTV:CAC = receita contratada (premissa) ÷ investimento.</p>`;
  h+=`<h2>Funil por canal de origem (período)</h2><div class="tw"><table><thead><tr><th>Canal</th><th>Leads</th><th>MQL</th><th>SQL</th><th>Ganhos</th><th>Tx Lead→Ganho</th></tr></thead><tbody>`;
  const sc=SELCH;
  h+=CHANNELS.filter(c=>SELCH.has(c)).map(c=>{SELCH=new Set([c]);const F=sumFunil(FILT.ini,FILT.fim);SELCH=sc;
    return {c,...F};}).filter(r=>r.lead>0).sort((a,b)=>b.lead-a.lead).map(r=>
    `<tr><td>${r.c}${D.canais_meta.includes(r.c)?' <span class="s-ok">●</span>':''}</td><td>${n0(r.lead)}</td><td>${n0(r.mql)}</td><td>${n0(r.sql)}</td><td>${n0(r.ganho)}</td><td>${fmt1(r.lead?r.ganho/r.lead*100:0)}%</td></tr>`).join("");
  SELCH=sc;
  h+=`</tbody></table></div>
    <h2>Drill de mídia (top 25 por investimento)</h2>
    <div class="subtabs"><button class="stbtn on" data-dl="camp" onclick="setDrill('camp')">Campanhas</button><button class="stbtn" data-dl="conj" onclick="setDrill('conj')">Conjuntos</button><button class="stbtn" data-dl="anun" onclick="setDrill('anun')">Anúncios</button></div><div id="drillbox"></div>`;
  return h;}
function setDrill(k){DRILLKEY=k;document.querySelectorAll("[data-dl]").forEach(b=>b.classList.toggle("on",b.dataset.dl===k));renderDrill();}
function renderDrill(){const dr=D.drill,arr={camp:dr.camps,conj:dr.conjs,anun:dr.anuns}[DRILLKEY],fld={camp:"ci",conj:"ji",anun:"ai"}[DRILLKEY];
  const meses=new Set(mesesRange());const agg={};
  dr.rows.forEach(r=>{if(!meses.has(r.m)||!SELCH.has(STRS[r.c])||!SELBU.has(BUL[r.b]))return;const name=arr[r[fld]];agg[name]=agg[name]||{inv:0,impr:0,clk:0,mql:0,sq:0,w:0};agg[name].inv+=r.inv;agg[name].impr+=r.impr;agg[name].clk+=r.clk;});
  (dr.ev||[]).forEach(r=>{if(!meses.has(r.m)||!SELCH.has(STRS[r.c])||!SELBU.has(BUL[r.b]))return;const name=arr[r[fld]];const a=(agg[name]=agg[name]||{inv:0,impr:0,clk:0,mql:0,sq:0,w:0});a.mql+=r.mq;a.sq+=r.sq;a.w+=r.w;});
  const rows=Object.entries(agg).filter(([,v])=>v.inv>0).sort((a,b)=>b[1].inv-a[1].inv).slice(0,25);
  let h=`<div class="tw"><table><thead><tr><th>${ {camp:"Campanha",conj:"Conjunto",anun:"Anúncio"}[DRILLKEY] }</th><th>Invest</th><th>Impr</th><th>Cliques</th><th>CTR</th><th>CPC</th><th>MQL</th><th>CPMQL</th><th>SQL</th><th>Clientes</th><th>CAC</th></tr></thead><tbody>`;
  h+=rows.map(([k,v])=>{const ctr=(v.impr&&v.clk<=v.impr)?fmt1(v.clk/v.impr*100)+"%":"—";
    return `<tr><td>${k}</td><td>${fmt(v.inv)}</td><td>${n0(v.impr)}</td><td>${n0(v.clk)}</td><td>${ctr}</td><td>${fmt(v.clk?v.inv/v.clk:0)}</td><td>${v.mql?n0(v.mql):"—"}</td><td>${v.mql?fmt(v.inv/v.mql):"—"}</td><td>${v.sq?n0(v.sq):"—"}</td><td>${v.w?fmt1(v.w):"—"}</td><td>${v.w?fmt(v.inv/v.w):"—"}</td></tr>`;}).join("");
  h+=`</tbody></table></div>`+(rows.length?"":`<p class="note">Sem mídia paga no recorte (canais manual_/orgânico não têm investimento).</p>`);
  const el=document.getElementById("drillbox");if(el)el.innerHTML=h;}
function metaMes(m){if(!periodMeta())return null;const f=metaFactor(fmStart(m),fmEnd(m));
  return{inv:metaSel("investimento",f),mql:metaSel("mql",f),rec:metaRec(f)};}
function rMensal(){const M=mesesAll();
  const KS=M.map(m=>kpi(fmStart(m),fmEnd(m)));
  const lin=(lbl,fn,strong)=>`<tr${strong?' style="font-weight:700"':''}><td>${lbl}</td>`+KS.map((x,i)=>`<td>${fn(x,M[i])}</td>`).join("")+`</tr>`;
  const linM=(lbl,fn)=>`<tr style="color:var(--mut);font-style:italic"><td>${lbl}</td>`+M.map((m,i)=>{const mm=metaMes(m);return `<td>${mm?fn(mm,KS[i]):"—"}</td>`;}).join("")+`</tr>`;
  let h=`<h2>Série mensal fiscal <span class="soft">· mês Colina = 16 → 15 ("jul" = 16/jun–15/jul) · TODOS os meses com dado (o período global não recorta esta tela) · filtros de BU e canal aplicam</span></h2><div class="tw"><table class="dre"><thead><tr><th>Métrica</th>`+M.map(m=>`<th>${m.slice(5)}/${m.slice(2,4)}</th>`).join("")+`</tr></thead><tbody>`;
  h+=lin("Investimento",x=>fmt(x.inv),true);
  if(periodMeta())h+=linM("Budget mídia (meta mês)",(mm,x)=>`${fmt(mm.inv)} · ${pctn(x.inv,mm.inv)}%`);
  h+=lin("Impressões",x=>n0(x.impr));
  h+=lin("Cliques",x=>n0(x.clk));
  h+=lin("CTR",x=>fmt1(x.ctr)+"%");
  h+=lin("CPC",x=>x.clk?fmt(x.cpc):"—");
  h+=lin("Leads",x=>n0(x.lead));
  h+=lin("MQL",x=>n0(x.mql),true);
  if(periodMeta())h+=linM("Meta MQL",(mm,x)=>`${n0(mm.mql)} · <span class="s-${stPct(x.mql,mm.mql)}">${pctn(x.mql,mm.mql)}%</span>`);
  h+=lin("CPMQL",x=>x.mql?fmt(x.cpmql):"—");
  h+=lin("SQL",x=>n0(x.sql));
  h+=lin("Novos Clientes (Safra)",x=>n0(x.cli_safra));
  h+=lin("CAC (Safra)",x=>x.cli_safra?fmt(x.cac_safra):"—");
  h+=lin("Fechados no Período",x=>n0(x.cli_geral),true);
  h+=lin("CAC (Fechados)",x=>x.cli_geral?fmt(x.cac_geral):"—");
  h+=lin("Taxa de Conversão",x=>fmt1(x.tx_conv*100)+"%");
  h+=lin("Ciclo mediano",x=>x.ciclo?fmt1(x.ciclo)+"d":"—");
  h+=lin("MRR Novo (premissa)",x=>fmt(x.mrr),true);
  h+=lin("Receita Contratada (premissa)",x=>fmt(x.contr),true);
  if(periodMeta())h+=linM("Meta receita contratada",(mm,x)=>`${fmt(mm.rec.contr)} · <span class="s-${stPct(x.contr,mm.rec.contr)}">${pctn(x.contr,mm.rec.contr)}%</span>`);
  h+=lin("LTV:CAC (premissa)",x=>x.inv?fmt1(x.ltv_cac)+"×":"—");
  h+=lin("Saldo contratado − mídia",x=>`<span class="${x.contr-x.inv>=0?'s-ok':'s-bad'}">${fmt(x.contr-x.inv)}</span>`,true);
  return h+`</tbody></table></div><p class="note">Meses FISCAIS 16→15 nomeados pelo mês em que terminam. Coorte: Clientes (Safra) no mês fiscal do lead; (Geral) no mês fiscal do ganho. Receita = <span class="pill prem">premissa</span> ${PREM_TXT} — vira dado real quando o total_value chegar no feed. Saldo usa só mídia (sem FEE).</p>`;}

const RENDER={geral:rGeral,bu:rBU,atencao:rAtencao,funil:rFunil,safra:rSafra,midia:rMidia,mensal:rMensal};
function drawCharts(){const M=mesesRange();
  if(FSCR==="geral"){
    if(document.getElementById("cGeral")){const A=M.map(m=>kpi(fmStart(m),fmEnd(m)));
      CH.g=new Chart(cGeral,{data:{labels:M,datasets:[
        {type:"bar",label:"Investimento",data:A.map(x=>x.inv),backgroundColor:"#157a5c",yAxisID:"y",datalabels:{anchor:"end",align:"end",color:"#8ba093",font:{size:10},formatter:v=>v?"R$"+Math.round(v/1000)+"k":""}},
        {type:"bar",label:"Novos Clientes (Safra)",data:A.map(x=>x.cli_safra),backgroundColor:"#d9a441",yAxisID:"y1",datalabels:{anchor:"end",align:"end",color:"#d9a441",font:{size:10,weight:"bold"},formatter:v=>v?n0(v):""}},
        {type:"line",label:"CAC (Safra)",data:A.map(x=>x.cac_safra),borderColor:"#5b9bd5",yAxisID:"y2",tension:.3,datalabels:{display:false}}]},
        options:cOpt({layout:{padding:{top:26}},plugins:{legend:{position:"top",align:"end",labels:{color:"#8ba093",font:{size:11},boxWidth:14,padding:14}},
          tooltip:{callbacks:{label:c=>c.dataset.label+": "+(c.datasetIndex===1?n0(c.parsed.y):fmt(c.parsed.y))}}},
          scales:{y:{grace:"15%",ticks:{color:"#8ba093",callback:v=>"R$"+Math.round(v/1000)+"k"},grid:{color:"#26302b"}},
          y1:{position:"right",grace:"15%",ticks:{color:"#d9a441"},grid:{display:false}},
          y2:{display:false}}}),plugins:[ChartDataLabels]});}}
  if(FSCR==="funil"){const fb=document.getElementById("funbox2");if(fb)fb.innerHTML=funilHTML(curK());}
  if(FSCR==="bu"){const rows=buAgg(FILT.ini,FILT.fim).filter(r=>BU_ORDEM.includes(r.bu));
    const mini=(id,data,fm,color)=>{const el=document.getElementById(id);if(!el)return;
      CH[id]=new Chart(el,{type:"bar",data:{labels:rows.map(r=>r.bu),datasets:[{data,backgroundColor:color,
        datalabels:{anchor:"end",align:"end",color:"#eef3f0",font:{size:11,weight:"bold"},formatter:v=>v?fm(v):"—"}}]},
        options:cOpt({indexAxis:"y",layout:{padding:{right:58}},plugins:{legend:{display:false}},
          scales:{x:{grace:"25%",ticks:{display:false},grid:{color:"#26302b"}},y:{ticks:{color:"#8ba093",font:{size:12}},grid:{display:false}}}}),
        plugins:[ChartDataLabels]});};
    mini("cBu0",rows.map(r=>r.inv),v=>"R$ "+Math.round(v/1000)+"k","#157a5c");
    mini("cBu1",rows.map(r=>r.mql),n0,"#1fb083");
    mini("cBu2",rows.map(r=>r.mql?r.cpmql:0),fmt,"#d9a441");
    mini("cBu3",rows.map(r=>r.cli_safra),n0,"#1fb083");
    mini("cBu4",rows.map(r=>r.cli_safra?r.cac_safra:0),fmt,"#d9a441");
    mini("cBu5",rows.map(r=>r.inv?r.ltv_cac:0),v=>fmt1(v)+"×","#5b9bd5");}}
function renderAll(){destroy();document.getElementById("main").innerHTML=RENDER[FSCR]();if(FSCR==="midia")renderDrill();drawCharts();updBub();}
function go(s){FSCR=s;document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on",t.dataset.s===s));renderAll();}
function updBub(){const nb=SELBU.size,nc=SELCH.size,SM=periodMeta();
  document.getElementById("bub").textContent=`Recorte: ${fmtRange(FILT.ini,FILT.fim)} · ${nb===BU_ORDEM.length?"BUs c/ meta":nb+" BU(s)"} · ${SM?"canais da meta (pagos)":nc===CHANNELS.length?"todos os canais":nc+" canal(is)"} · ${SM?`metas escaladas p/ ${fmt1(metaFactor(FILT.ini,FILT.fim))} mês-fiscal-equiv.`:"metas ocultas (recorte ≠ canais da meta)"} · mês fiscal 16→15 · receita premissa`;}

// ---- POPUPS ----
function togPop(id){const p=document.getElementById(id);const open=p.classList.contains("on");document.querySelectorAll(".pop").forEach(x=>x.classList.remove("on"));if(!open){p.classList.add("on");if(id==="popPeriod"){DRAFT={...FILT};calAnchor=monthStart(DRAFT.ini);pickStage=0;buildPicker();}}}
function closePop(){document.querySelectorAll(".pop").forEach(x=>x.classList.remove("on"));}
document.addEventListener("click",e=>{if(!e.target.closest(".fctl"))closePop();});
function buildPresets(){document.getElementById("presets").innerHTML=PRESETS.map(([n])=>`<button class="pset ${DRAFT.preset===n?'on':''}" onclick="pickPreset('${n}')">${n}</button>`).join("")+`<button class="pset ${DRAFT.preset==='custom'?'on':''}" onclick="pickPreset('custom')">Personalizar</button>`;}
function pickPreset(n){if(n==="custom"){DRAFT.preset="custom";pickStage=0;buildPicker();return;}const f=PRESETS.find(p=>p[0]===n)[1]();DRAFT.ini=f[0];DRAFT.fim=f[1];DRAFT.preset=n;FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function buildCal(elId,anchor){const d0=DD(anchor),y=d0.getFullYear(),mo=d0.getMonth(),first=new Date(y,mo,1),start=first.getDay(),dim=new Date(y,mo+1,0).getDate();
  let h=`<div class="calhd"><button class="calnav" onclick="navCal(-1)">‹</button><span>${MES_PT[mo]} ${y}</span><button class="calnav" onclick="navCal(1)">›</button></div><div class="cgrid">`+["D","S","T","Q","Q","S","S"].map(x=>`<div class="dow">${x}</div>`).join("");
  for(let i=0;i<start;i++)h+=`<div class="cd out"></div>`;
  const cmp=DRAFT.cmpOn?cmpRange(DRAFT.ini,DRAFT.fim,DRAFT.cmpMode):null;
  for(let dn=1;dn<=dim;dn++){const ds=SD(new Date(y,mo,dn));let cls="cd";if(ds===DRAFT.ini||ds===DRAFT.fim)cls+=" sel";else if(ds>DRAFT.ini&&ds<DRAFT.fim)cls+=" inr";if(cmp&&ds>=cmp[0]&&ds<=cmp[1])cls+=" cmpr";h+=`<div class="${cls}" onclick="pickDay('${ds}')">${dn}</div>`;}
  document.getElementById(elId).innerHTML=h+`</div>`;}
function navCal(n){calAnchor=addM(calAnchor,n);buildPicker();}
function pickDay(ds){DRAFT.preset="custom";if(pickStage===0){DRAFT.ini=ds;DRAFT.fim=ds;pickStage=1;}else{if(ds<DRAFT.ini){DRAFT.fim=DRAFT.ini;DRAFT.ini=ds;}else DRAFT.fim=ds;pickStage=0;}buildPicker();}
function buildCmp(){document.getElementById("cmpTog").checked=DRAFT.cmpOn;document.getElementById("cmpOpts").innerHTML=DRAFT.cmpOn?[["month","Mês anterior"],["year","Ano anterior"],["prev","Período anterior"]].map(([k,l])=>`<button class="cmpopt ${DRAFT.cmpMode===k?'on':''}" onclick="setCmpMode('${k}')">${l}</button>`).join(" "):"";}
function onCmpTog(){DRAFT.cmpOn=document.getElementById("cmpTog").checked;if(DRAFT.cmpOn&&!DRAFT.cmpMode)DRAFT.cmpMode="month";FILT.cmpOn=DRAFT.cmpOn;FILT.cmpMode=DRAFT.cmpMode;buildPicker();renderAll();}
function setCmpMode(k){DRAFT.cmpMode=k;FILT.cmpMode=k;FILT.cmpOn=DRAFT.cmpOn;buildPicker();renderAll();}
function buildPicker(){buildPresets();buildCal("calA",calAnchor);buildCal("calB",addM(calAnchor,1));buildCmp();}
function applyPeriod(){FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function updPeriodLabel(){document.getElementById("vPeriod").textContent=fmtRange(FILT.ini,FILT.fim);}

// ---- BU multi-select ----
function buildBU(){document.getElementById("buList").innerHTML=BU_ORDEM.concat([BUL[BUL.length-1]]).map(b=>`<label class="chk"><input type="checkbox" ${SELBU.has(b)?'checked':''} onchange="tgbu('${b.replace(/'/g,"\\'")}')"><span>${b}${RC[b]?(RC[b].t==="rec"?' <span class="s-mut" style="font-size:10px">rec</span>':' <span class="s-mut" style="font-size:10px">tcv</span>'):''}</span></label>`).join("");updBuLabel();}
function updBuLabel(){document.getElementById("vBU").textContent=SELBU.size===BU_ORDEM.length&&BU_ORDEM.every(b=>SELBU.has(b))?"Todas c/ meta":SELBU.size+" BU(s)";}
function tgbu(b){SELBU.has(b)?SELBU.delete(b):SELBU.add(b);buildBU();renderAll();}
function buAll(){SELBU=new Set(BUL);buildBU();renderAll();}
function buMeta(){SELBU=new Set(BU_ORDEM);buildBU();renderAll();}
// ---- CANAL multi-select ----
function buildChan(){document.getElementById("chanList").innerHTML=CHANNELS.map(c=>`<label class="chk"><input type="checkbox" ${SELCH.has(c)?'checked':''} onchange="tgch('${c.replace(/'/g,"\\'")}')"><span>${c}${D.canais_meta.includes(c)?' <span class="s-ok">●</span>':''}</span></label>`).join("");updChanLabel();}
function updChanLabel(){document.getElementById("vChan").textContent=periodMeta()?"Só pagos":SELCH.size===CHANNELS.length?"Todos":SELCH.size+" canal(is)";}
function tgch(c){SELCH.has(c)?SELCH.delete(c):SELCH.add(c);buildChan();renderAll();}
function chMeta(){SELCH=new Set(D.canais_meta.filter(c=>CHANNELS.includes(c)));buildChan();renderAll();}
function chAll(){SELCH=new Set(CHANNELS);buildChan();renderAll();}

document.getElementById("nav").innerHTML=SCR.map(([k,l])=>`<button class="tab ${k==='geral'?'on':''}" data-s="${k}" onclick="go('${k}')">${l}</button>`).join("");
document.getElementById("ts").textContent="atualizado "+D.gerado_em;
updPeriodLabel();buildBU();buildChan();renderAll();
</script></body></html>"""
html = TEMPLATE.replace("__DADOS__", json.dumps(DADOS, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"OK monitor.html — {len(html):,} bytes · {len(DEALS)} deals · {len(ADSDAY)} adsday · {len(DRILL['rows'])} drill · {len(STRS)} strs · receita premissa {len(RECEITA)} BUs")

# ---- anexa o funil atribuído por campanha ao monitor.json (p/ skills de análise) -----
# O renderer é quem computa a atribuição (motor único MQL/SQL/Ganho ancorado no mês
# fiscal do lead); anexar aqui evita duplicar o motor no gerador. Roda DEPOIS do
# _gerar-monitor.py no wrapper — o bloco sobrevive à regeneração do snapshot base.
OUT_JSON = BASE / "monitor.json"
try:
    CAMPL = DRILL["camps"]
    _agg = collections.defaultdict(lambda: {"investimento": 0.0, "impressoes": 0, "cliques": 0,
                                            "mql": 0.0, "sql": 0.0, "clientes": 0.0})
    for k, v in DR.items():
        if v["inv"] <= 0: continue
        a = _agg[(k[0], k[1], k[2], k[3])]
        a["investimento"] += v["inv"]; a["impressoes"] += int(v["impr"]); a["cliques"] += int(v["clk"])
    for k, v in EVR.items():
        a = _agg[(k[0], k[1], k[2], k[3])]
        a["mql"] += v["mq"]; a["sql"] += v["sq"]; a["clientes"] += v["w"]
    linhas = []
    for (m, b, c, ci), a in sorted(_agg.items()):
        if a["investimento"] <= 0: continue
        linhas.append({"mes_fiscal": m, "bu": BUL[b], "canal": STRS[c], "campanha": CAMPL[ci],
                       "investimento": round(a["investimento"], 2), "impressoes": a["impressoes"],
                       "cliques": a["cliques"], "mql": round(a["mql"], 2), "sql": round(a["sql"], 2),
                       "clientes": round(a["clientes"], 2),
                       "cac": round(a["investimento"] / a["clientes"], 2) if a["clientes"] else None})
    snap = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
    snap["funil_atribuido_campanha_mes"] = {
        "nota": ("MQL/SQL/Clientes do CRM atribuídos por campanha, ancorados no mês FISCAL do lead "
                 "(create_at). ad_id rastreável + criativo com invest no mês → direto; senão proporcional "
                 "aos rastreáveis do mesmo mês×BU×canal; fallback share de investimento. Valores fracionados "
                 "by design. Grão anúncio/conjunto disponível só no monitor.html."),
        "linhas": linhas,
    }
    OUT_JSON.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK monitor.json += funil_atribuido_campanha_mes ({len(linhas)} linhas campanha×mês)")
except Exception as e:
    print(f"WARN: funil atribuído não anexado ao monitor.json — {e}", file=sys.stderr)
