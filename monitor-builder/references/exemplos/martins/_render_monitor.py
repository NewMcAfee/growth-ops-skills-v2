# -*- coding: utf-8 -*-
# =============================================================================
# _render_monitor.py — Martins Locações · Monitor (9 telas, Chart.js)
# -----------------------------------------------------------------------------
# Gera monitor.html: cockpit auto-contido com DS Martins (dark #0a0a0f /
# vermelho #ef4444), Chart.js, sidebar 9 telas e filtros GLOBAIS estilo Google
# Ads: date-range picker (presets + calendário 2 meses + comparação Mês/Ano
# anterior) e canal como multi-select. Granularidade DIÁRIA (filtra por range).
# Roda depois do _gerar-monitor.py. Fontes: bd-buy (ganhos/produto/cohort),
# leads-pipeline (funil/perdas, canal via deal_id), bd-ads (mídia por campanha).
# =============================================================================
import csv, json, sys, collections
from datetime import datetime
from pathlib import Path

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
OUT = BASE / "monitor.html"
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

def load_contrato():
    d = {"quarter": "2026-Q2", "inicio": "2026-04-01", "fim": "2026-06-30",
         "canais_meta": ["paid_google", "paid_meta"], "fee": {"default": 0, "por_mes": {}},
         "metas": {"faturamento": 342000, "clientes": 480, "ticket_medio": 950,
                   "investimento": 114000, "roas_min": 3.0, "cac_max": 239.82}}
    try:
        import yaml
        c = yaml.safe_load(CONTRATO.read_text(encoding="utf-8")) or {}
        p = c.get("periodo", {}); m = c.get("metas", {})
        d["quarter"] = p.get("quarter_vigencia", d["quarter"])
        d["inicio"] = p.get("inicio", d["inicio"]); d["fim"] = p.get("fim", d["fim"])
        d["canais_meta"] = c.get("canais_meta", d["canais_meta"])
        d["fee"] = c.get("fee", d["fee"])
        if m.get("aquisicao"): d["metas"] = m["aquisicao"]
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

def truthy(v): return str(v).strip().lower() not in ("", "false", "0", "no", "não", "nao", "none")

# --- Frentes de negócio (tela Mídia) ---------------------------------------
# Investimento: nome da campanha → frente por keyword (bi-frente rateia).
# Faturamento: funnel do deal quando preenchido; senão product_cart → frente.
import unicodedata as _ud
def _norm(s): return _ud.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()
FRENTES = ["Caçamba de Entulho", "Andaimes", "Betoneira", "Terraplanagem", "Areia e Brita",
           "Limpa Fossa", "Preparação de Canteiro", "Compactador de Solo", "Containers",
           "Escoramentos", "Plataforma Elevatória", "Institucional / Geral", "(outras frentes)"]
FR_KW = [("cacamba", 0), ("andaime", 1), ("betoneira", 2), ("terraplanagem", 3),
         ("equipamentos pesados", 3), ("areia", 4), ("fossa", 5), ("canteiro", 6),
         ("compactador", 7), ("container", 8), ("escoramento", 9), ("plataforma", 10)]
def classify_frente(texto):
    """Lista de índices de FRENTES por keyword; [] se nada casa."""
    n = _norm(texto)
    return sorted({fi for kw, fi in FR_KW if kw in n})
PROD2FR = {"locacao: cacambas": 0, "locacao: cacamba sobradinho": 0, "locacao: roll on/off": 0,
           "locacao: andaimes e acessorios": 1, "locacao: betoneiras": 2,
           "servicos: terraplanagem": 3, "vendas: martins ambiental (attr)": 4,
           "servicos: limpa fossa": 5, "locacao: containers": 8, "locacao: escoramentos": 9,
           "locacao: plataforma elevatoria": 10}
def rcsv(p):
    fp = BASE / p
    if not fp.exists(): return []
    with open(fp, encoding="utf-8-sig", newline="") as fh: return list(csv.DictReader(fh))
def iso(d): return d.strftime("%Y-%m-%d")

C = load_contrato()
META = C["metas"]; CANAIS_META = C["canais_meta"]
ganhos, pipeline, ads = rcsv("bd-buy.csv"), rcsv("leads-pipeline.csv"), rcsv("bd-ads.csv")
canal_por_deal = {(r.get("deal_id") or "").strip(): ((r.get("canal") or "").strip() or "(sem atribuição)")
                  for r in pipeline if (r.get("deal_id") or "").strip()}

# classificação aq×rc (1º ganho lifetime do lead)
por_lead = {}
for g in ganhos:
    lid = (g.get("lead_id") or "").strip()
    if lid: por_lead.setdefault(lid, []).append(pdate(g.get("crosed_at")))
prim = {lid: min([d for d in ds if d], default=None) for lid, ds in por_lead.items()}

# GANHOS diário (lista compacta) — com lead_idx p/ reconstruir cohort no cliente
GAN = []; LEADIDX = {}
for g in ganhos:
    d = pdate(g.get("crosed_at"))
    if not d: continue
    canal = canal_por_deal.get((g.get("deal_id") or "").strip(), "(sem atribuição)")
    lid = (g.get("lead_id") or "").strip(); pg = prim.get(lid)
    if lid and lid not in LEADIDX: LEADIDX[lid] = len(LEADIDX)
    frg = sorted({PROD2FR[_norm(p.strip())] for p in (g.get("product_cart") or "").split(";")
                  if p.strip() and _norm(p.strip()) in PROD2FR})
    GAN.append({"d": iso(d), "c": canal, "e": ("rc" if (pg and d > pg) else "aq"),
                "v": round(pnum(g.get("total_value")), 2), "p": (g.get("product_cart") or "—").strip() or "—",
                "li": LEADIDX.get(lid, -1), "f": frg})

# INVDAY diário canal-level (bd-ads) + DRILL mensal com dict de strings
INV = collections.defaultdict(lambda: {"inv": 0.0, "impr": 0.0, "clk": 0.0})
camps, conjs, anuns = {}, {}, {}
def idx(d, k): return d.setdefault(k, len(d))
DR = collections.defaultdict(lambda: {"inv": 0.0, "impr": 0.0, "clk": 0.0})
for r in ads:
    d = pdate(r.get("data"))
    if not d: continue
    canal = (r.get("canal") or "(sem atribuição)").strip() or "(sem atribuição)"
    inv, impr, clk = pnum(r.get("investimento")), pnum(r.get("impressões")), pnum(r.get("ad_clicks"))
    k = (iso(d), canal); n = INV[k]; n["inv"] += inv; n["impr"] += impr; n["clk"] += clk
    ci = idx(camps, (r.get("nome_campanha") or "—").strip() or "—")
    ji = idx(conjs, (r.get("nome_conjunto") or "—").strip() or "—")
    ai = idx(anuns, (r.get("nome_anuncio") or "—").strip() or "—")
    dk = (d.strftime("%Y-%m"), canal, ci, ji, ai); dn = DR[dk]; dn["inv"] += inv; dn["impr"] += impr; dn["clk"] += clk
INVDAY = [{"d": k[0], "c": k[1], "inv": round(v["inv"], 2), "impr": int(v["impr"]), "clk": int(v["clk"])} for k, v in INV.items()]
CAMPFR = [classify_frente(n) or [11] for n in camps]   # frente(s) de cada campanha; sem match → Institucional/Geral
DRILL = {"camps": list(camps), "conjs": list(conjs), "anuns": list(anuns),
         "rows": [{"m": k[0], "c": k[1], "ci": k[2], "ji": k[3], "ai": k[4],
                   "inv": round(v["inv"], 2), "impr": int(v["impr"]), "clk": int(v["clk"])} for k, v in DR.items() if v["inv"] > 0]}

# DEALS: deals do leads-pipeline — fonte única das visões analíticas (funil, produto,
# origem, canal, qualificadores, velocidade, ticket). Strings em dicionário (STRS) p/ compactar.
QUAL_FIELDS = [("esta_obra", "qualificador_esta-em-obra", "Está em obra?"),
               ("tipo_obra", "qualificador_tipo-de-obra", "Tipo de obra"),
               ("fase_obra", "qualificador_fase-da-obra-acquisition", "Fase da obra"),
               ("porte_obra", "qualificador_tamanho-da-obra", "Porte da obra")]
STR = {}
def _si(s):
    s = (s or "").strip() or "Desconhecido"
    if s not in STR: STR[s] = len(STR)
    return STR[s]
DEALS = []
for r in pipeline:
    cd = pdate(r.get("create_at"))
    if not cd: continue
    w = 1 if truthy(r.get("win")) else 0
    l = 1 if truthy(r.get("lost")) else 0
    v = pnum(r.get("total_value"))
    close = pdate(r.get("win_at")) if w else (pdate(r.get("lost_at")) if l else None)
    dias = round((close - cd).total_seconds() / 86400, 4) if (close and close >= cd) else None
    prods = [_si(p) for p in (r.get("product_cart") or "").split(";") if p.strip()]
    q = [_si(r.get(col)) for _, col, _ in QUAL_FIELDS]
    canal = (r.get("canal") or "").strip() or "(sem atribuição)"
    fr = classify_frente(r.get("funnel") or "")
    if not fr:
        fr = sorted({PROD2FR[_norm(p.strip())] for p in (r.get("product_cart") or "").split(";")
                     if p.strip() and _norm(p.strip()) in PROD2FR})
    # canal suspeito: clickid/ad_id da outra plataforma (contaminação vista no export do CRM)
    gcl = (r.get("gclid") or "").strip(); fbc = (r.get("fbclid") or "").strip(); aid = (r.get("ad_id") or "").strip()
    sus = 0
    if canal == "paid_google" and ((len(fbc) > 10 and "{" not in fbc)
                                   or (aid.isdigit() and len(aid) >= 15 and aid.startswith("120"))):
        sus = 1
    elif canal == "paid_meta" and len(gcl) > 20 and "{" not in gcl:
        sus = 1
    row = {"cd": iso(cd), "c": _si(canal), "o": _si(r.get("origem")),
           "p": prods, "q": q, "w": w, "l": l, "v": round(v, 2), "d": dias,
           "f": fr or [12]}
    if sus: row["s"] = 1
    DEALS.append(row)
STRS = list(STR)

perdas = collections.Counter((r.get("lost_reason") or "").strip() for r in pipeline if (r.get("lost_reason") or "").strip())
PERDAS = [{"motivo": m, "n": n} for m, n in perdas.most_common(10)]

datas = [g["d"] for g in GAN] + [x["d"] for x in INVDAY]
dmin, dmax = (min(datas), max(datas)) if datas else (C["inicio"], C["fim"])
DADOS = {
    "meta": {"faturamento": META["faturamento"], "clientes": META["clientes"], "ticket": META["ticket_medio"],
             "investimento": META["investimento"], "roas": META["roas_min"], "cac": META["cac_max"]},
    "canais_meta": CANAIS_META, "quarter": C["quarter"], "qini": C["inicio"], "qfim": C["fim"], "fee": C["fee"],
    "today": iso(HOJE), "dmin": dmin, "dmax": dmax, "gerado_em": HOJE.strftime("%Y-%m-%d %H:%M"),
    "gan": GAN, "invday": INVDAY, "drill": DRILL, "deals": DEALS, "strs": STRS, "perdas": PERDAS,
    "frentes": FRENTES, "campfr": CAMPFR,
    "qualfields": [[i, lbl] for i, (k, _, lbl) in enumerate(QUAL_FIELDS)],
}

TEMPLATE = r"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor — Martins Locações</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
:root{--bg:#0a0a0f;--card:#15151f;--elev:#1b1b29;--bd:#26263a;--mut:#8b8b9e;--sub:#5d5d70;
--red:#ef4444;--redd:#b91c1c;--grn:#22c55e;--amb:#f59e0b;--txt:#f5f5f7}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--bg);color:var(--txt);font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
.topbar{height:4px;background:linear-gradient(90deg,var(--redd),var(--red))}
.head{display:flex;justify-content:space-between;align-items:center;max-width:1300px;margin:0 auto;padding:18px 24px 6px}
.head h1{font-size:22px;font-weight:800;margin:0}.head .ts{color:var(--sub);font-size:12px;font-family:ui-monospace,monospace}
.filterbar{position:sticky;top:0;z-index:40;background:rgba(10,10,15,.86);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd)}
.fb{max-width:1300px;margin:0 auto;padding:11px 24px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center}
.fctl{position:relative}
.fbtn{display:inline-flex;align-items:center;gap:8px;background:var(--elev);border:1px solid var(--bd);color:var(--txt);border-radius:9px;padding:7px 13px;cursor:pointer;font-size:13px}
.fbtn:hover{border-color:var(--red)}.fbtn .cap{color:var(--sub);font-size:10.5px;text-transform:uppercase;letter-spacing:.5px}
.fbtn .val{font-weight:600}.fbtn .ar{color:var(--mut);font-size:10px}
.pop{position:absolute;top:calc(100% + 6px);left:0;background:var(--card);border:1px solid var(--bd);border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.6);z-index:60;display:none}
.pop.on{display:block}.pop.right{left:auto;right:0}
.dpick{display:flex;min-width:560px}
.presets{flex:none;width:172px;border-right:1px solid var(--bd);padding:8px;max-height:330px;overflow:auto}
.pset{display:block;width:100%;text-align:left;background:none;border:none;color:var(--mut);padding:7px 10px;border-radius:7px;cursor:pointer;font-size:13px}
.pset:hover{background:var(--elev);color:var(--txt)}.pset.on{background:var(--red);color:#fff}
.calwrap{padding:12px 14px}.cals{display:flex;gap:18px}.cal{width:210px}
.calhd{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:13px;font-weight:600}
.calnav{background:var(--elev);border:1px solid var(--bd);color:var(--txt);border-radius:6px;width:24px;height:24px;cursor:pointer}
.cgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cgrid .dow{font-size:10px;color:var(--sub);text-align:center;padding:3px 0}
.cd{text-align:center;padding:5px 0;font-size:12px;border-radius:6px;cursor:pointer;color:var(--txt)}
.cd:hover{background:var(--elev)}.cd.out{color:var(--sub);cursor:default}.cd.out:hover{background:none}
.cd.sel{background:var(--red);color:#fff;font-weight:700}.cd.inr{background:rgba(239,68,68,.18)}
.cd.cmpr{box-shadow:inset 0 0 0 1px var(--amb)}
.cmpbar{border-top:1px solid var(--bd);margin-top:10px;padding-top:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.switch{position:relative;width:38px;height:21px;flex:none}.switch input{opacity:0;width:0;height:0}
.sl{position:absolute;inset:0;background:var(--elev);border:1px solid var(--bd);border-radius:999px;transition:.2s}
.sl:before{content:"";position:absolute;height:15px;width:15px;left:2px;top:2px;background:var(--mut);border-radius:50%;transition:.2s}
.switch input:checked+.sl{background:var(--red);border-color:var(--red)}.switch input:checked+.sl:before{transform:translateX(17px);background:#fff}
.cmpopt{background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:7px;padding:5px 10px;cursor:pointer;font-size:12.5px}
.cmpopt.on{background:var(--amb);border-color:var(--amb);color:#1a1a1a;font-weight:600}
.popfoot{display:flex;justify-content:flex-end;gap:8px;padding:10px 14px;border-top:1px solid var(--bd)}
.bt{border:1px solid var(--bd);background:var(--elev);color:var(--txt);border-radius:7px;padding:6px 14px;cursor:pointer;font-size:13px}.bt.pri{background:var(--red);border-color:var(--red)}
.chanpop{min-width:230px;padding:8px}
.chk{display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:7px;cursor:pointer;font-size:13px}.chk:hover{background:var(--elev)}
.chk input{accent-color:var(--red);width:15px;height:15px}.chquick{display:flex;gap:6px;padding:4px 6px 8px;border-bottom:1px solid var(--bd);margin-bottom:6px}
.qbtn{flex:1;background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:7px;padding:5px;cursor:pointer;font-size:12px}.qbtn:hover{border-color:var(--red);color:var(--txt)}
.badge-view{font-size:12.5px;color:var(--mut);text-align:center;max-width:1300px;margin:8px auto 0;padding:0 24px}
.layout{display:flex;gap:24px;max-width:1300px;margin:0 auto;padding:16px 24px 64px}
.sidenav{flex:none;width:172px;position:sticky;top:64px;align-self:flex-start;display:flex;flex-direction:column;gap:3px}
.tab{text-align:left;background:none;border:none;border-left:3px solid transparent;color:var(--mut);padding:9px 12px;border-radius:0 8px 8px 0;cursor:pointer;font-size:13.5px;transition:all .12s}
.tab:hover{background:var(--card);color:var(--txt)}.tab.on{background:var(--card);border-left-color:var(--red);color:#fff;font-weight:600}
.main{flex:1;min-width:0}
h2{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:26px 0 12px;font-weight:700}h2:first-child{margin-top:4px}
.grid{display:grid;gap:13px}.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(auto-fit,minmax(195px,1fr))}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px}
.okr .t{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}.okr .big{font-size:30px;font-weight:800;margin:5px 0 1px}.okr .m{font-size:12.5px;color:var(--mut)}
.bar{height:7px;background:#0a0a12;border-radius:4px;overflow:hidden;margin:9px 0 5px}.bar>i{display:block;height:100%;border-radius:4px}.proj{font-size:11.5px;color:var(--sub)}
.kbox{background:var(--card);border:1px solid var(--bd);border-radius:11px;padding:13px 15px}.kbox .l{font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.kbox .n{font-size:23px;font-weight:800;margin:4px 0 1px}.kbox .x{font-size:11.5px;color:var(--sub)}
.kd{font-size:11.5px;font-weight:600}.s-ok{color:var(--grn)}.s-warn{color:var(--amb)}.s-bad{color:var(--red)}.s-mut{color:var(--sub)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:8px 10px;border-bottom:1px solid var(--bd);text-align:right}th:first-child,td:first-child{text-align:left}
th{color:var(--mut);font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;font-weight:700}tbody tr:hover{background:var(--elev)}.tw{overflow-x:auto;border:1px solid var(--bd);border-radius:12px}
.funrow{display:flex;align-items:center;gap:12px;margin:7px 0}.fn{width:135px;text-align:right;font-size:13px;color:var(--mut)}
.ft{flex:1;height:30px;background:#0a0a12;border-radius:6px;position:relative;overflow:hidden}.ft>i{display:block;height:100%;background:linear-gradient(90deg,var(--redd),var(--red));border-radius:6px}
.ft .v{position:absolute;left:10px;top:50%;transform:translateY(-50%);font-weight:800;font-size:14px}.fr{width:150px;font-size:12px;color:var(--mut);font-family:ui-monospace,monospace}
.deccol h3{font-size:14px;margin:0 0 10px}.decitem{border-left:3px solid var(--bd);padding:7px 11px;margin-bottom:8px;background:var(--elev);border-radius:0 8px 8px 0}.decitem .nm{font-weight:600;font-size:13px}.decitem .mo{font-size:11.5px;color:var(--mut)}
.subtabs{display:flex;gap:6px;margin-bottom:12px}.stbtn{background:var(--elev);border:1px solid var(--bd);color:var(--mut);border-radius:8px;padding:5px 13px;cursor:pointer;font-size:12.5px}.stbtn.on{background:var(--red);border-color:var(--red);color:#fff}
.heat td{text-align:center}.heat td:first-child{text-align:left;position:sticky;left:0;background:var(--card)}
.dre thead th{background:var(--red);color:#fff}.dre td:first-child,.dre th:first-child{position:sticky;left:0;text-align:left;font-weight:600;z-index:1;background:var(--card)}.dre thead th:first-child{background:var(--red);z-index:2}
canvas{max-height:260px}.chart-lg{padding:20px 22px}.chart-lg canvas{max-height:420px;min-height:360px}.note{font-size:12px;color:var(--sub);margin-top:8px}.qlabel{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);margin-bottom:10px;font-weight:700}
@media(max-width:920px){.layout{flex-direction:column}.sidenav{flex-direction:row;flex-wrap:wrap;width:auto;position:static}.tab{border-left:none;border-radius:8px}.g2,.g3{grid-template-columns:1fr}.dpick{flex-direction:column;min-width:300px}.presets{width:auto;border-right:none;border-bottom:1px solid var(--bd)}}
</style></head><body>
<div class="topbar"></div>
<div class="head"><h1>Monitor · Martins Locações</h1><span class="ts" id="ts"></span></div>
<div class="filterbar"><div class="fb">
  <div class="fctl"><button class="fbtn" id="bPeriod" onclick="togPop('popPeriod')"><span class="cap">Período</span><span class="val" id="vPeriod"></span><span class="ar">▾</span></button>
    <div class="pop" id="popPeriod" onclick="event.stopPropagation()"><div class="dpick">
      <div class="presets" id="presets"></div>
      <div class="calwrap"><div class="cals"><div class="cal" id="calA"></div><div class="cal" id="calB"></div></div>
        <div class="cmpbar"><label class="switch"><input type="checkbox" id="cmpTog" onchange="onCmpTog()"><span class="sl"></span></label>
          <span style="font-size:12.5px;color:var(--mut)">Comparar</span><span id="cmpOpts"></span></div></div></div>
      <div class="popfoot"><button class="bt" onclick="closePop()">Cancelar</button><button class="bt pri" onclick="applyPeriod()">Aplicar</button></div></div>
  </div>
  <div class="fctl"><button class="fbtn" id="bChan" onclick="togPop('popChan')"><span class="cap">Canal</span><span class="val" id="vChan"></span><span class="ar">▾</span></button>
    <div class="pop right chanpop" id="popChan" onclick="event.stopPropagation()"><div class="chquick"><button class="qbtn" onclick="chMeta()">só pagos</button><button class="qbtn" onclick="chAll()">todos</button></div><div id="chanList"></div></div>
  </div>
</div></div>
<div class="layout"><nav class="sidenav" id="nav"></nav><div class="main" id="main"></div></div>
<script>
const D = __DADOS__;
const SCR=[["geral","Visão Geral"],["decisao","Atenção"],["funil","Funil & Perdas"],
  ["recompra","Recompra"],["midia","Mídia"],["produtos","Produtos"],["mensal","Mensal"]];
const CHANNELS=(()=>{let s=new Set();D.gan.forEach(g=>s.add(g.c));D.invday.forEach(x=>s.add(x.c));D.deals.forEach(d=>s.add(D.strs[d.c]));return [...s].sort();})();
let SELCH=new Set(D.canais_meta.filter(c=>CHANNELS.includes(c)));
const fmt=v=>"R$ "+Math.round(v||0).toLocaleString("pt-BR");
const fmt1=v=>(v||0).toLocaleString("pt-BR",{maximumFractionDigits:1});
const pctn=(a,b)=>b?Math.round(a/b*100):0;
const COR={ok:"#22c55e",warn:"#f59e0b",bad:"#ef4444"};
// ---- datas ----
const DD=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d);};
const SD=dt=>dt.getFullYear()+"-"+String(dt.getMonth()+1).padStart(2,"0")+"-"+String(dt.getDate()).padStart(2,"0");
const addD=(s,n)=>{const d=DD(s);d.setDate(d.getDate()+n);return SD(d);};
const addM=(s,n)=>{const d=DD(s);d.setMonth(d.getMonth()+n);return SD(d);};
const MES_PT=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
const fmtRange=(a,b)=>{const da=DD(a),db=DD(b);return da.getTime()===db.getTime()?`${da.getDate()} ${MES_PT[da.getMonth()]} ${da.getFullYear()}`
  :`${da.getDate()} ${MES_PT[da.getMonth()]} – ${db.getDate()} ${MES_PT[db.getMonth()]} ${db.getFullYear()}`;};
const today=D.today;
function monthStart(s){return s.slice(0,7)+"-01";}
function monthEnd(s){const d=DD(s);return SD(new Date(d.getFullYear(),d.getMonth()+1,0));}
// presets
const PRESETS=[
  ["Hoje",()=>[today,today]],["Ontem",()=>[addD(today,-1),addD(today,-1)]],
  ["Últimos 7 dias",()=>[addD(today,-6),today]],["Últimos 14 dias",()=>[addD(today,-13),today]],
  ["Últimos 30 dias",()=>[addD(today,-29),today]],["Este mês",()=>[monthStart(today),today]],
  ["Mês passado",()=>{const p=addM(monthStart(today),-1);return [p,monthEnd(p)];}],
  ["Este trimestre",()=>[D.qini,today<D.qfim?today:D.qfim]],
  ["Trimestre passado",()=>[addM(D.qini,-3),addD(D.qini,-1)]],
  ["Este ano",()=>[today.slice(0,4)+"-01-01",today]],["Todo o período",()=>[D.dmin,D.dmax]],
];
let FILT={ini:D.qini,fim:(today<D.qfim?today:D.qfim),preset:"Este trimestre",cmpOn:false,cmpMode:"prev"};
let DRAFT={...FILT};let calAnchor=monthStart(FILT.ini);let pickStage=0;

function periodMeta(){return SELCH.size===D.canais_meta.length&&D.canais_meta.every(c=>SELCH.has(c));}
const nDays=(a,b)=>Math.round((DD(b)-DD(a))/864e5)+1;
// Metas do contrato valem pro QUARTER de vigência. Pro-rata pela interseção do período
// selecionado com a vigência (mês ≈ 1/3, semana ≈ 7/91, dia ≈ 1/91). Taxas (ticket/ROAS/CAC)
// NÃO escalam — alvo de taxa vale em qualquer granularidade. Sem interseção → null (sem meta).
function metaPeriodo(){
  const a=FILT.ini>D.qini?FILT.ini:D.qini, b=FILT.fim<D.qfim?FILT.fim:D.qfim;
  if(a>b)return null;
  const dq=nDays(D.qini,D.qfim), dp=nDays(a,b), f=dp/dq, T=D.meta;
  return {faturamento:T.faturamento*f, clientes:T.clientes*f, investimento:T.investimento*f,
          ticket:T.ticket, roas:T.roas, cac:T.cac, f, dp, dq};
}
// comparação: range espelho
function cmpRange(ini,fim,mode){
  if(mode==="prev"){const days=Math.round((DD(fim)-DD(ini))/864e5)+1;return [addD(ini,-days),addD(ini,-1)];}
  if(mode==="month")return [addM(ini,-1),addM(fim,-1)];
  if(mode==="year")return [addM(ini,-12),addM(fim,-12)];
  return null;
}
// agregações filtrando por range+canais
function sumGan(ini,fim){let o={aqg:0,aqf:0,rcg:0,rcf:0,paq:{},prc:{}};
  for(const g of D.gan){if(g.d<ini||g.d>fim||!SELCH.has(g.c))continue;o[g.e+"g"]++;o[g.e+"f"]+=g.v;
    const pk=g.e==="aq"?"paq":"prc";o[pk][g.p]=o[pk][g.p]||{g:0,f:0};o[pk][g.p].g++;o[pk][g.p].f+=g.v;}return o;}
function sumInv(ini,fim){let o={inv:0,impr:0,clk:0};for(const x of D.invday){if(x.d<ini||x.d>fim||!SELCH.has(x.c))continue;o.inv+=x.inv;o.impr+=x.impr;o.clk+=x.clk;}return o;}
function kpi(ini,fim){const g=sumGan(ini,fim),i=sumInv(ini,fim);return{...g,...i,ticket:g.aqg?g.aqf/g.aqg:0,roas:i.inv?g.aqf/i.inv:0,cac:g.aqg?i.inv/g.aqg:0,rctk:g.rcg?g.rcf/g.rcg:0,ctr:i.impr?i.clk/i.impr*100:0,cpc:i.clk?i.inv/i.clk:0};}
function curK(){return kpi(FILT.ini,FILT.fim);}
function cmpK(){if(!FILT.cmpOn)return null;const r=cmpRange(FILT.ini,FILT.fim,FILT.cmpMode);return r?kpi(r[0],r[1]):null;}
// meses no range (p/ séries)
function mesesRange(){let s=new Set();for(const g of D.gan)if(g.d>=FILT.ini&&g.d<=FILT.fim)s.add(g.d.slice(0,7));for(const x of D.invday)if(x.d>=FILT.ini&&x.d<=FILT.fim)s.add(x.d.slice(0,7));return [...s].sort();}
function kpiMes(m){return kpi(m+"-01",monthEnd(m+"-01"));}
const STRS=D.strs;
function dealsFilt(){return D.deals.filter(d=>d.cd>=FILT.ini&&d.cd<=FILT.fim&&SELCH.has(STRS[d.c]));}
function funAgg(){const ds=dealsFilt();let o={lead:0,win:0,lost:0,vorc:0,vwin:0,vlost:0};
  for(const d of ds){o.lead++;o.win+=d.w;o.lost+=d.l;o.vorc+=d.v;if(d.w)o.vwin+=d.v;if(d.l)o.vlost+=d.v;}return o;}
function qualDist(i){const ds=dealsFilt(),acc={};for(const d of ds){const v=STRS[d.q[i]];acc[v]=(acc[v]||0)+1;}return Object.entries(acc).sort((a,b)=>b[1]-a[1]);}
function qualMensal(i){const ds=dealsFilt(),acc={};for(const d of ds){const m=d.cd.slice(0,7),v=STRS[d.q[i]];(acc[m]=acc[m]||{})[v]=(acc[m][v]||0)+1;}return acc;}
function mesesQual(){const s=new Set();for(const d of dealsFilt())s.add(d.cd.slice(0,7));return [...s].sort();}
const QPAL=["#ef4444","#22c55e","#f59e0b","#60a5fa","#a78bfa","#8b8b9e","#ec4899","#14b8a6"];
function median(arr){if(!arr.length)return 0;const s=[...arr].sort((a,b)=>a-b),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;}
function byDim(kind){const ds=(kind==='canal')?D.deals.filter(d=>d.cd>=FILT.ini&&d.cd<=FILT.fim):dealsFilt();const acc={};
  for(const d of ds){let keys,rate=1;
    if(kind==='prod'){if(!d.p.length)continue;keys=d.p.map(pi=>STRS[pi]);rate=1/d.p.length;}
    else if(kind==='orig')keys=[STRS[d.o]];else keys=[STRS[d.c]];
    keys.forEach(k=>{const a=acc[k]||(acc[k]={total:0,win:0,lost:0,fat:0,dias:[]});a.total++;a.win+=d.w;a.lost+=d.l;if(d.w)a.fat+=d.v*rate;if(d.w&&d.d!=null)a.dias.push(d.d);});}
  const tot=Object.values(acc).reduce((s,a)=>s+a.fat,0);
  return Object.entries(acc).map(([k,a])=>({k,total:a.total,win:a.win,lost:a.lost,wr:a.total?a.win/a.total:0,fat:a.fat,share:tot?a.fat/tot:0,ticket:a.win?a.fat/a.win:0,ciclo:median(a.dias)})).sort((x,y)=>y.fat-x.fat);}
function velocidade(){const ds=dealsFilt(),g=[],p=[];for(const d of ds){if(d.d==null)continue;if(d.w)g.push(d.d);else if(d.l)p.push(d.d);}
  const stat=a=>{if(!a.length)return{med:0,avg:0,p25:0,p75:0,n:0};const s=[...a].sort((x,y)=>x-y),q=f=>s[Math.min(s.length-1,Math.floor(f*s.length))];return{med:median(a),avg:a.reduce((x,y)=>x+y,0)/a.length,p25:q(.25),p75:q(.75),n:a.length};};
  const fx=[["< 1h",0,1/24],["1–6h",1/24,.25],["6–24h",.25,1],["1–3 dias",1,3],["3–7 dias",3,7],["> 7 dias",7,1e9]];
  return{g:stat(g),p:stat(p),dist:fx.map(([lb,a,b])=>({lb,g:g.filter(x=>x>=a&&x<b).length,p:p.filter(x=>x>=a&&x<b).length}))};}
function ticketDist(){const ds=dealsFilt(),w=ds.filter(d=>d.w),fx=[["até R$ 300",0,300],["R$ 300–600",300,600],["R$ 600–1k",600,1000],["R$ 1k–2k",1000,2000],["R$ 2k–5k",2000,5000],["> R$ 5k",5000,1e12]];
  return{tot:w.length,faixas:fx.map(([lb,a,b])=>({lb,n:w.filter(d=>d.v>=a&&d.v<b).length}))};}
let FRSEL=-1; // -1 = todas as frentes (cohort filtra pela frente da 1ª compra do lead)
function setFrCoh(i){FRSEL=i;renderAll();}
function frentesRecompra(){const first={};for(const g of D.gan){if(g.li<0||!SELCH.has(g.c))continue;const cur=first[g.li];if(!cur||g.d<cur.d)first[g.li]=g;}
  const cnt={};Object.values(first).forEach(g=>(g.f||[]).forEach(fi=>cnt[fi]=(cnt[fi]||0)+1));
  return Object.entries(cnt).filter(([,n])=>n>=30).sort((a,b)=>b[1]-a[1]).map(([fi])=>+fi);}
function cohortBuild(){const byLead={};for(const g of D.gan){if(g.li<0||!SELCH.has(g.c))continue;(byLead[g.li]=byLead[g.li]||[]).push(g);}
  const base={},mat={},mi=s=>{const a=s.split("-");return +a[0]*12+(+a[1]-1);},maxoff=8;
  for(const li in byLead){const arr=byLead[li].sort((a,b)=>a.d<b.d?-1:1),s=arr[0],safra=s.d.slice(0,7),si=mi(s.d);
    if(FRSEL>=0&&!(s.f||[]).includes(FRSEL))continue;
    base[safra]=(base[safra]||0)+1;
    for(let j=1;j<arr.length;j++){const off=mi(arr[j].d)-si;if(off<1||off>maxoff)continue;(mat[safra]=mat[safra]||{});(mat[safra][off]=mat[safra][off]||{n:0,v:0});mat[safra][off].n++;mat[safra][off].v+=arr[j].v;}}
  return{base,mat,maxoff,safras:Object.keys(base).sort()};}
function delta(cur,prev){if(prev==null||!isFinite(prev)||prev===0)return"";const d=(cur-prev)/prev*100,cls=d>=0?"s-ok":"s-bad",ar=d>=0?"▲":"▼";return ` <span class="kd ${cls}">${ar} ${Math.abs(Math.round(d))}%</span>`;}

let CH={};function destroy(){Object.values(CH).forEach(c=>{try{c.destroy()}catch(e){}});CH={};}
const cOpt=ex=>Object.assign({responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:"#8b8b9e",font:{size:11}}}},scales:{x:{ticks:{color:"#8b8b9e",font:{size:10}},grid:{color:"#26263a"}},y:{ticks:{color:"#8b8b9e",font:{size:10}},grid:{color:"#26263a"}}}},ex||{});

// ---------- TELAS ----------
let FSCR="geral";
function rGeral(){const K=curK(),MT=metaPeriodo(),T=MT||D.meta,showMeta=periodMeta()&&!!MT,P=cmpK();
  const fatTotal=K.aqf+K.rcf,roasT=K.inv?fatTotal/K.inv:0,txRec=(K.aqg+K.rcg)?K.rcg/(K.aqg+K.rcg):0;
  const F=funAgg(),hit=F.lead?F.win/F.lead:0;
  const fatTP=P?P.aqf+P.rcf:0,roasTP=P&&P.inv?fatTP/P.inv:0,txRecP=P&&(P.aqg+P.rcg)?P.rcg/(P.aqg+P.rcg):0;
  const dl=(now,prev)=>(P&&prev!=null)?delta(now,prev):"";
  const st=(real,meta,maior=true)=>{const p=meta?real/meta:0;return maior?(p>=1?"ok":p>=.8?"warn":"bad"):(real>0&&real<=meta?"ok":"bad");};
  // pacing: período em andamento (contém hoje) → projeta o fim do período no ritmo atual
  const pr=(real,metaFull,fm)=>{if(!showMeta||today<=FILT.ini||today>FILT.fim)return"";
    const el=nDays(FILT.ini,today),tt=nDays(FILT.ini,FILT.fim);if(el>=tt||!real)return"";
    const p=real/el*tt,pc=metaFull?Math.round(p/metaFull*100):0;
    return `<div class="proj">ritmo → ${fm(p)} · ${pc}% da meta no fim do período</div>`;};
  function card(t,val,o){o=o||{};const hasMeta=o.meta!=null&&showMeta;let body,cor="";
    if(hasMeta){const w=Math.min(100,Math.round(o.pct*100));cor="s-"+o.st;
      body=`<div class="m">meta ${o.metaTxt} · ${Math.round(o.pct*100)}%</div><div class="bar"><i style="width:${w}%;background:${COR[o.st]}"></i></div>${o.proj||""}`;}
    else body=`<div class="m">${o.sub||"&nbsp;"}</div>`;
    return `<div class="card okr"><div class="t">${t}</div><div class="big ${cor}">${val}<span style="font-size:13px;font-weight:600">${o.delta||""}</span></div>${body}</div>`;}
  const proTag=(showMeta&&MT.f<0.999)?` <span style="color:var(--sub);font-weight:400;text-transform:none;letter-spacing:0">· metas pro-rata: ${MT.dp} de ${MT.dq} dias do ${D.quarter}</span>`:'';
  let h=`<h2>Visão Geral${proTag}${P?' <span style="color:var(--sub);font-weight:400;text-transform:none;letter-spacing:0">· vs '+({prev:"período ant.",month:"mês ant.",year:"ano ant."}[FILT.cmpMode])+'</span>':''}</h2><div class="grid g4">`;
  h+=card("Faturamento — Primeira Compra",fmt(K.aqf),{meta:T.faturamento,metaTxt:fmt(T.faturamento),pct:K.aqf/T.faturamento,st:st(K.aqf,T.faturamento),sub:"novos clientes",delta:dl(K.aqf,P&&P.aqf),proj:pr(K.aqf,T.faturamento,fmt)});
  h+=card("Ticket Médio — Primeira Compra",fmt(K.ticket),{meta:T.ticket,metaTxt:fmt(T.ticket),pct:K.ticket/T.ticket,st:st(K.ticket,T.ticket),sub:"por novo cliente",delta:dl(K.ticket,P&&P.ticket)});
  h+=card("Faturamento — Recompra",fmt(K.rcf),{sub:"clientes recorrentes",delta:dl(K.rcf,P&&P.rcf)});
  h+=card("Ticket Médio — Recompra",fmt(K.rctk),{sub:"por recompra",delta:dl(K.rctk,P&&P.rctk)});
  h+=card("Investimento",fmt(K.inv),{meta:T.investimento,metaTxt:fmt(T.investimento),pct:K.inv/T.investimento,st:st(K.inv,T.investimento),sub:"budget",delta:dl(K.inv,P&&P.inv),proj:pr(K.inv,T.investimento,fmt)});
  h+=card("Novos Clientes",K.aqg.toLocaleString("pt-BR"),{meta:T.clientes,metaTxt:Math.round(T.clientes).toLocaleString("pt-BR"),pct:K.aqg/T.clientes,st:st(K.aqg,T.clientes),sub:"aquisição",delta:dl(K.aqg,P&&P.aqg),proj:pr(K.aqg,T.clientes,v=>Math.round(v).toLocaleString("pt-BR"))});
  h+=card("CAC",fmt(K.cac),{meta:T.cac,metaTxt:fmt(T.cac),pct:K.cac/T.cac,st:st(K.cac,T.cac,false),sub:"custo/cliente",delta:dl(K.cac,P&&P.cac)});
  h+=card("Recompras",K.rcg.toLocaleString("pt-BR"),{sub:"ganhos recorrentes",delta:dl(K.rcg,P&&P.rcg)});
  h+=card("Faturamento Total",fmt(fatTotal),{sub:"1ª compra + recompra",delta:dl(fatTotal,P?fatTP:null)});
  h+=card("ROAS",K.inv?fmt1(roasT)+"×":"—",{meta:T.roas,metaTxt:T.roas+"×",pct:roasT/T.roas,st:roasT>=T.roas?"ok":(roasT>=T.roas*.8?"warn":"bad"),sub:"fat. total ÷ invest",delta:dl(roasT,P?roasTP:null)});
  h+=card("Hit-rate",fmt1(hit*100)+"%",{sub:"lead → compra"});
  h+=card("Taxa de Recompra",fmt1(txRec*100)+"%",{sub:"recompras ÷ ganhos",delta:dl(txRec,P?txRecP:null)});
  h+=`</div><h2>Investimento × Faturamento Total × ROAS (safra mês)</h2><div class="card chart-lg"><canvas id="cGeral"></canvas></div>
    <h2>Volume mensal — aquisição vs recompra</h2><div class="card chart-lg"><canvas id="cVolG"></canvas></div>`;
  return h;}
function rKpis(){const K=curK(),P=cmpK(),T=metaPeriodo()||D.meta;
  const kb=(l,n,x,d)=>`<div class="kbox"><div class="l">${l}</div><div class="n">${n}${d||""}</div><div class="x">${x}</div></div>`;
  let h=`<h2>KPIs do período${P?' (Δ vs comparação)':''}</h2><div class="grid g4">`;
  h+=kb("Faturamento aq",fmt(K.aqf),"meta "+fmt(T.faturamento),P?delta(K.aqf,P.aqf):"");
  h+=kb("Clientes aq",K.aqg,"meta "+Math.round(T.clientes),P?delta(K.aqg,P.aqg):"");
  h+=kb("Ticket médio",fmt(K.ticket),"meta "+fmt(T.ticket),P?delta(K.ticket,P.ticket):"");
  h+=kb("Investimento",fmt(K.inv),"budget "+fmt(T.investimento),P?delta(K.inv,P.inv):"");
  h+=kb("ROAS",fmt1(K.roas)+"×","meta "+T.roas+"×",P?delta(K.roas,P.roas):"");
  h+=kb("CAC",fmt(K.cac),"teto "+fmt(T.cac),P?delta(K.cac,P.cac):"");
  h+=kb("Recompras",K.rcg,fmt(K.rcf),P?delta(K.rcg,P.rcg):"");
  h+=kb("Impressões",Math.round(K.impr).toLocaleString("pt-BR"),"tráfego","");
  h+=kb("Cliques",Math.round(K.clk).toLocaleString("pt-BR"),"CTR "+fmt1(K.ctr)+"%","");
  h+=kb("CPC",fmt(K.cpc),"custo/clique","");
  h+=`</div><h2>Volume mensal — aquisição vs recompra</h2><div class="card"><canvas id="cVol"></canvas></div>`;return h;}
function porCanalRows(){return CHANNELS.map(c=>{const sc=SELCH;SELCH=new Set([c]);const k=kpi(FILT.ini,FILT.fim);SELCH=sc;return{c,...k};});}
function rDecisao(){
  const ds=D.deals.filter(d=>d.cd>=FILT.ini&&d.cd<=FILT.fim),n=ds.length||1,wins=ds.filter(d=>d.w),nw=wins.length||1;
  const semCanal=ds.filter(d=>STRS[d.c]==='(sem atribuição)').length;
  const semOrigem=ds.filter(d=>STRS[d.o]==='Desconhecido').length;
  const semQual=ds.filter(d=>d.q.every(qi=>STRS[qi]==='Desconhecido')).length;
  const vSemValor=wins.filter(d=>d.v<=0).length;
  const vSemProd=wins.filter(d=>!d.p.length).length;
  const susCanal=ds.filter(d=>d.s).length;
  const kb=(l,val,sub,bad)=>`<div class="kbox"><div class="l">${l}</div><div class="n ${bad?'s-bad':''}">${val.toLocaleString("pt-BR")}</div><div class="x">${sub}</div></div>`;
  let h=`<h2>Pontos cegos — qualidade do dado (período)</h2><div class="grid g4">`;
  h+=kb("Negócios sem canal",semCanal,pctn(semCanal,n)+"% dos negócios",semCanal/n>.3);
  h+=kb("Negócios sem origem",semOrigem,pctn(semOrigem,n)+"% dos negócios",semOrigem/n>.3);
  h+=kb("Sem qualificadores de obra",semQual,pctn(semQual,n)+"% (4 campos vazios)",semQual/n>.3);
  h+=kb("Vendas sem valor",vSemValor,pctn(vSemValor,nw)+"% das vendas",vSemValor/nw>.1);
  h+=kb("Vendas sem produto",vSemProd,pctn(vSemProd,nw)+"% das vendas",vSemProd/nw>.3);
  h+=kb("Canal × clickid divergentes",susCanal,pctn(susCanal,n)+"% — canal diz uma plataforma, gclid/fbclid/ad_id dizem outra",susCanal/n>.03);
  h+=`</div>`;
  const rows=porCanalRows().filter(r=>r.inv>0||r.aqg>0);
  const cortar=rows.filter(r=>r.inv>0&&r.roas<1),escalar=rows.filter(r=>r.roas>=D.meta.roas),inv=rows.filter(r=>r.roas>=1&&r.roas<D.meta.roas);
  const col=(t,cls,ic,arr)=>`<div class="card deccol"><h3 class="s-${cls}">${ic} ${t}</h3>`+(arr.length?arr.map(r=>`<div class="decitem" style="border-left-color:${COR[cls]}"><div class="nm">${r.c}</div><div class="mo">ROAS ${fmt1(r.roas)}× · CAC ${fmt(r.cac)} · inv ${fmt(r.inv)}</div></div>`).join(""):'<div class="mo s-mut">—</div>')+`</div>`;
  h+=`<h2>Decisão por canal — veredito ROAS/CAC</h2><div class="grid g3">${col("Cortar","bad","✂",cortar)}${col("Escalar","ok","▲",escalar)}${col("Investigar","warn","◉",inv)}</div>`;
  const fr=porFrenteRows().filter(r=>r.inv>0);
  const frCol=(t,cls,ic,arr)=>`<div class="card deccol"><h3 class="s-${cls}">${ic} ${t}</h3>`+(arr.length?arr.map(r=>`<div class="decitem" style="border-left-color:${COR[cls]}"><div class="nm">${r.k}</div><div class="mo">ROAS ${fmt1(r.roas)}× · fat ${fmt(r.fat)} · inv ${fmt(r.inv)}</div></div>`).join(""):'<div class="mo s-mut">—</div>')+`</div>`;
  const frCortar=fr.filter(r=>r.roas<1),frEscalar=fr.filter(r=>r.roas>=D.meta.roas),frInv=fr.filter(r=>r.roas>=1&&r.roas<D.meta.roas);
  h+=`<h2>Decisão por frente de negócio — veredito ROAS</h2><div class="grid g3">${frCol("Cortar","bad","✂",frCortar)}${frCol("Escalar","ok","▲",frEscalar)}${frCol("Investigar","warn","◉",frInv)}</div>
  <div class="note">Frentes de ticket alto e ciclo longo (terraplanagem, preparação de canteiro) podem converter fora do período — confirmar em janela maior antes de cortar. Atribuição: mesma regra da tela Mídia.</div>`;
  return h;}
const wbar=(pct,cor)=>`<span style="display:inline-block;width:50px;height:7px;background:#0a0a12;border-radius:4px;vertical-align:middle;margin-right:6px"><span style="display:block;height:100%;width:${Math.max(2,Math.round(pct*100))}%;background:${cor};border-radius:4px"></span></span>`;
function dimTable(rows,dimLabel){const maxFat=Math.max(1,...rows.map(r=>r.fat));
  let h=`<div class="tw"><table><thead><tr><th>${dimLabel}</th><th>Total</th><th>Ganhas</th><th>Perdidas</th><th>Win rate</th><th>Faturamento</th><th>Share</th><th>Ticket méd.</th><th>Ciclo</th></tr></thead><tbody>`;
  h+=rows.map(r=>{const wc=r.wr>=.3?'#22c55e':r.wr>=.15?'#f59e0b':'#60a5fa';
    return `<tr><td>${r.k}</td><td>${r.total}</td><td>${r.win}</td><td>${r.lost}</td><td>${wbar(r.wr,wc)}${fmt1(r.wr*100)}%</td><td>${fmt(r.fat)} ${wbar(r.fat/maxFat,'#ef4444')}</td><td>${Math.round(r.share*100)}%</td><td>${fmt(r.ticket)}</td><td>${r.ciclo?fmt1(r.ciclo)+'d':'—'}</td></tr>`;}).join("");
  return h+`</tbody></table></div>`;}
function velHTML(){const V=velocidade();
  const card=(t,s,cor)=>`<div class="card" style="border-left:3px solid ${cor}"><div class="qlabel">${t} — mediana</div><div style="font-size:27px;font-weight:800">${fmt1(s.med)} dias</div><div class="s-mut" style="font-size:12px">média ${fmt1(s.avg)}d · P25 ${fmt1(s.p25)}d · P75 ${fmt1(s.p75)}d · n=${s.n}</div></div>`;
  let h=`<div class="grid g2">${card("Ganhas",V.g,'#f59e0b')}${card("Perdidas",V.p,'#ef4444')}</div>`;
  h+=`<div class="tw" style="margin-top:13px"><table><thead><tr><th>Faixa de tempo</th><th>Ganhas</th><th>%</th><th>Perdidas</th><th>%</th></tr></thead><tbody>`;
  h+=V.dist.map(f=>`<tr><td>${f.lb}</td><td>${f.g}</td><td>${pctn(f.g,V.g.n)}%</td><td>${f.p}</td><td>${pctn(f.p,V.p.n)}%</td></tr>`).join("");
  return h+`</tbody></table></div>`;}
function rFunil(){
  let h=`<div class="grid g2">
    <div class="card"><div class="qlabel">Funil — Lead → Ganho / Perdido</div><canvas id="cFunVol"></canvas></div>
    <div class="card"><div class="qlabel">Funil de valor — Orçado → Ganho / Perdido</div><canvas id="cFunVal"></canvas></div></div>`;
  const totp=D.perdas.reduce((a,b)=>a+b.n,0);
  h+=`<h2>Motivos de perda (top 10)</h2><div class="tw"><table><thead><tr><th>Motivo</th><th>Qtd</th><th>%</th></tr></thead><tbody>`+D.perdas.map(p=>`<tr><td>${p.motivo}</td><td>${p.n.toLocaleString("pt-BR")}</td><td>${pctn(p.n,totp)}%</td></tr>`).join("")+`</tbody></table></div>`;
  h+=`<h2>Velocidade — tempo entre criação e fechamento</h2>`+velHTML();
  h+=`<h2>Por origem do negócio</h2>`+dimTable(byDim('orig'),'Origem');
  h+=`<h2>Por canal de origem</h2>`+dimTable(byDim('canal'),'Canal');
  h+=`<h2>Qualificadores de obra ao longo do tempo</h2><div class="grid g2">`;
  D.qualfields.forEach(([i,lbl])=>{h+=`<div class="card"><div class="qlabel">${lbl}</div><canvas id="cQual${i}"></canvas></div>`;});
  h+=`</div>`;
  return h;}
let COHKEY="taxa";
function setCoh(k){COHKEY=k;renderAll();}
function rRecompra(){const co=cohortBuild(),mi=FILT.ini.slice(0,7),mf=FILT.fim.slice(0,7);
  const safras=co.safras.filter(s=>s>=mi&&s<=mf);
  const maxV=Math.max(1,...safras.flatMap(s=>Object.values(co.mat[s]||{}).map(c=>c.v)));
  const frtabs=frentesRecompra();
  let h=`<h2>Recompra — cohort por safra de 1ª compra</h2>
    <div class="subtabs"><button class="stbtn ${COHKEY==='taxa'?'on':''}" onclick="setCoh('taxa')">Taxa de recompra</button><button class="stbtn ${COHKEY==='valor'?'on':''}" onclick="setCoh('valor')">Valor de recompra</button></div>
    <div class="subtabs" style="flex-wrap:wrap"><button class="stbtn ${FRSEL===-1?'on':''}" onclick="setFrCoh(-1)">Todas as frentes</button>${frtabs.map(fi=>`<button class="stbtn ${FRSEL===fi?'on':''}" onclick="setFrCoh(${fi})">${D.frentes[fi]}</button>`).join("")}</div>
    ${FRSEL>=0?`<div class="note" style="margin:-4px 0 10px">Safra = clientes cuja <b>1ª compra</b> foi de ${D.frentes[FRSEL]}; as recompras contam qualquer frente.</div>`:''}
    <div class="tw"><table class="heat"><thead><tr><th>Safra</th><th>Clientes</th>`;
  for(let k=1;k<=co.maxoff;k++)h+=`<th>M+${k}</th>`;h+=`</tr></thead><tbody>`;
  safras.forEach(s=>{const b=co.base[s]||0;if(b<5)return;h+=`<tr><td>${s}</td><td>${b}</td>`;
    for(let k=1;k<=co.maxoff;k++){const cell=(co.mat[s]||{})[k];
      if(!cell){h+=`<td>·</td>`;continue;}
      if(COHKEY==='taxa'){const p=b?cell.n/b:0;h+=`<td style="background:rgba(34,197,94,${(0.08+p*0.7).toFixed(2)})">${Math.round(p*100)}%</td>`;}
      else h+=`<td style="background:rgba(245,158,11,${Math.min(0.7,cell.v/maxV*0.62+0.08).toFixed(2)})">${fmt(cell.v)}</td>`;}
    h+=`</tr>`;});
  h+=`</tbody></table></div>`;
  return h;}
let DRILLKEY="camp";
// Frente de negócio: invest = campanhas classificadas por keyword (bi-frente rateia);
// retorno = ganhos pagos do período por funnel (LP) ou product_cart (rateio multiproduto).
function porFrenteRows(){const meses=new Set(mesesRange());
  const acc=D.frentes.map(()=>({inv:0,impr:0,clk:0,g:0,fat:0}));
  D.drill.rows.forEach(r=>{if(!meses.has(r.m)||!SELCH.has(r.c))return;const fs=D.campfr[r.ci]||[11];const w=1/fs.length;
    fs.forEach(fi=>{acc[fi].inv+=r.inv*w;acc[fi].impr+=r.impr*w;acc[fi].clk+=r.clk*w;});});
  for(const d of dealsFilt()){if(!d.w)continue;const w=1/d.f.length;
    d.f.forEach(fi=>{acc[fi].g+=w;acc[fi].fat+=d.v*w;});}
  return acc.map((a,i)=>({k:D.frentes[i],...a,ctr:a.impr?a.clk/a.impr*100:0,cpc:a.clk?a.inv/a.clk:0,
    cac:a.g?a.inv/a.g:0,roas:a.inv?a.fat/a.inv:0})).filter(a=>a.inv>0||a.fat>0).sort((x,y)=>y.inv-x.inv);}
function rFrentes(){const rows=porFrenteRows();
  let h=`<h2>Investimento × retorno por frente de negócio</h2><div class="tw"><table><thead><tr><th>Frente</th><th>Invest</th><th>Impr</th><th>Cliques</th><th>CTR</th><th>CPC</th><th>Ganhos</th><th>Faturamento</th><th>CAC</th><th>ROAS</th></tr></thead><tbody>`;
  h+=rows.map(r=>{const roasCls=r.inv?(r.roas>=D.meta.roas?'s-ok':r.roas>=1?'s-warn':'s-bad'):'';
    return `<tr><td>${r.k}</td><td>${r.inv?fmt(r.inv):"—"}</td><td>${Math.round(r.impr).toLocaleString("pt-BR")}</td><td>${Math.round(r.clk).toLocaleString("pt-BR")}</td><td>${fmt1(r.ctr)}%</td><td>${r.clk?fmt(r.cpc):"—"}</td><td>${Math.round(r.g).toLocaleString("pt-BR")}</td><td>${fmt(r.fat)}</td><td>${r.g&&r.inv?fmt(r.cac):"—"}</td><td>${r.inv?`<span class="${roasCls}">${fmt1(r.roas)}×</span>`:"—"}</td></tr>`;}).join("");
  h+=`</tbody></table></div><div class="note">Invest: campanha → frente por keyword do nome (campanha bi-frente, ex. "Betoneira &amp; Andaime", rateia 50/50; branded/institucional/site → Institucional / Geral). Ganhos/Faturamento: negócios ganhos criados no período e canais selecionados, frente via funil da LP quando preenchido, senão via produto (multiproduto rateia). Frente com invest "—" = venda paga sem campanha dedicada.</div>`;
  return h;}
function rMidia(){const rows=porCanalRows().filter(r=>r.inv>0).sort((a,b)=>b.inv-a.inv);
  let h=`<h2>Investimento por canal</h2><div class="tw"><table><thead><tr><th>Canal</th><th>Invest</th><th>Impr</th><th>Cliques</th><th>CTR</th><th>CPC</th><th>Ganhos</th><th>CAC</th><th>ROAS</th></tr></thead><tbody>`;
  h+=rows.map(r=>`<tr><td>${r.c}</td><td>${fmt(r.inv)}</td><td>${Math.round(r.impr).toLocaleString("pt-BR")}</td><td>${Math.round(r.clk).toLocaleString("pt-BR")}</td><td>${fmt1(r.ctr)}%</td><td>${fmt(r.cpc)}</td><td>${r.aqg}</td><td>${r.aqg?fmt(r.cac):"—"}</td><td>${r.inv?fmt1(r.roas)+"×":"—"}</td></tr>`).join("");
  h+=`</tbody></table></div>`;
  h+=rFrentes();
  h+=`<h2>Drill</h2><div class="subtabs"><button class="stbtn on" data-dl="camp" onclick="setDrill('camp')">Campanhas</button><button class="stbtn" data-dl="conj" onclick="setDrill('conj')">Conjuntos</button><button class="stbtn" data-dl="anun" onclick="setDrill('anun')">Anúncios</button></div><div id="drillbox"></div>`;return h;}
function setDrill(k){DRILLKEY=k;document.querySelectorAll("[data-dl]").forEach(b=>b.classList.toggle("on",b.dataset.dl===k));renderDrill();}
function renderDrill(){const dr=D.drill,arr={camp:dr.camps,conj:dr.conjs,anun:dr.anuns}[DRILLKEY],fld={camp:"ci",conj:"ji",anun:"ai"}[DRILLKEY];
  const meses=new Set(mesesRange());const agg={};
  dr.rows.forEach(r=>{if(!meses.has(r.m)||!SELCH.has(r.c))return;const name=arr[r[fld]];agg[name]=agg[name]||{inv:0,impr:0,clk:0};agg[name].inv+=r.inv;agg[name].impr+=r.impr;agg[name].clk+=r.clk;});
  const rows=Object.entries(agg).sort((a,b)=>b[1].inv-a[1].inv).slice(0,25);
  let h=`<div class="tw"><table><thead><tr><th>${ {camp:"Campanha",conj:"Conjunto",anun:"Anúncio"}[DRILLKEY] }</th><th>Invest</th><th>Impr</th><th>Cliques</th><th>CTR</th><th>CPC</th></tr></thead><tbody>`;
  h+=rows.map(([k,v])=>`<tr><td>${k}</td><td>${fmt(v.inv)}</td><td>${Math.round(v.impr).toLocaleString("pt-BR")}</td><td>${v.clk.toLocaleString("pt-BR")}</td><td>${fmt1(v.impr?v.clk/v.impr*100:0)}%</td><td>${fmt(v.clk?v.inv/v.clk:0)}</td></tr>`).join("");
  h+=`</tbody></table></div>`;
  const el=document.getElementById("drillbox");if(el)el.innerHTML=h;}
function rProdutos(){const rows=byDim('prod'),td=ticketDist();
  let h=`<h2>Por produto</h2>`;
  h+=dimTable(rows,'Produto');
  h+=`<h2>Distribuição de ticket (vendas ganhas)</h2><div class="card">`;
  const mx=Math.max(1,...td.faixas.map(f=>f.n));
  td.faixas.forEach(f=>{h+=`<div style="margin:7px 0"><div style="display:flex;justify-content:space-between;font-size:12.5px"><span>${f.lb}</span><span class="s-mut">${f.n} · ${pctn(f.n,td.tot)}%</span></div><div class="bar"><i style="width:${Math.round(f.n/mx*100)}%;background:var(--amb)"></i></div></div>`;});
  h+=`</div>`;
  return h;}
function feeMes(m){const f=D.fee||{};return (f.por_mes&&f.por_mes[m]!=null)?f.por_mes[m]:(f.default||0);}
function dreMes(m){const ini=m+"-01",fim=monthEnd(m+"-01"),iv=sumInv(ini,fim);
  const leads=D.deals.filter(d=>d.cd>=ini&&d.cd<=fim&&SELCH.has(STRS[d.c])).length;
  let orc=0;for(const d of D.deals){if(d.cd>=ini&&d.cd<=fim&&SELCH.has(STRS[d.c]))orc+=d.v;}
  let nAq=0,nRc=0,fAq=0,fRc=0;
  for(const g of D.gan){if(g.d<ini||g.d>fim||!SELCH.has(g.c))continue;if(g.e==='aq'){nAq++;fAq+=g.v;}else{nRc++;fRc+=g.v;}}
  const fee=feeMes(m),midia=iv.inv,total=midia+fee,gan=nAq+nRc,fat=fAq+fRc;
  return{midia,fee,total,impr:iv.impr,clk:iv.clk,cpm:iv.impr?midia/iv.impr*1000:0,ctr:iv.impr?iv.clk/iv.impr*100:0,
    leads,nAq,nRc,gan,wr:leads?gan/leads:0,orc,orcConv:orc?fat/orc:0,fAq,fRc,fat,
    ticket:gan?fat/gan:0,roas:midia?fat/midia:0,cac:gan?total/gan:0,cpl:leads?total/leads:0,saldo:fat-total};}
function mesesDRE(){return mesesRange().map(m=>[m,dreMes(m)]).filter(([m,x])=>x.fat>0||x.leads>0);}
// meta pro-rata do mês (interseção do mês com a vigência do quarter); null fora da vigência
function metaMes(m){if(!periodMeta())return null;const ini=m+"-01",fim=monthEnd(ini);
  const a=ini>D.qini?ini:D.qini,b=fim<D.qfim?fim:D.qfim;if(a>b)return null;
  const f=nDays(a,b)/nDays(D.qini,D.qfim);return{fat:D.meta.faturamento*f,inv:D.meta.investimento*f};}
let FECHKEY="vol";
function setFech(k){FECHKEY=k;renderAll();}
function rMensal(){const MX=mesesDRE(),M=MX.map(x=>x[0]),A=MX.map(x=>x[1]);
  let h=`<h2>Resultados — fechamentos</h2>
    <div class="subtabs"><button class="stbtn ${FECHKEY==='vol'?'on':''}" onclick="setFech('vol')">Volume (ganhos)</button><button class="stbtn ${FECHKEY==='rec'?'on':''}" onclick="setFech('rec')">Receita (R$)</button></div>
    <div class="grid g2"><div class="card"><div class="qlabel">Fechados por mês${FECHKEY==='rec'?' — receita':''}</div><canvas id="cFechMes"></canvas></div><div class="card"><div class="qlabel">Fechados por ano${FECHKEY==='rec'?' — receita':''}</div><canvas id="cFechAno"></canvas></div></div>`;
  const lin=(lbl,fn,strong)=>`<tr${strong?' style="font-weight:700"':''}><td>${lbl}</td>`+A.map(x=>`<td>${fn(x)}</td>`).join("")+`</tr>`;
  h+=`<h2>DRE mensal</h2><div class="tw"><table class="dre"><thead><tr><th>Métrica</th>`+M.map(m=>`<th>${m}</th>`).join("")+`</tr></thead><tbody>`;
  const linM=(lbl,fn)=>`<tr style="color:var(--mut);font-style:italic"><td>${lbl}</td>`+MX.map(([m,x])=>{const mm=metaMes(m);return `<td>${mm?fn(mm,x):"—"}</td>`;}).join("")+`</tr>`;
  h+=lin("Investimento (mídia)",x=>fmt(x.midia));
  if(periodMeta())h+=linM("Budget mídia (pro-rata)",(mm,x)=>`${fmt(mm.inv)} · ${Math.round(x.midia/mm.inv*100)}%`);
  h+=lin("FEE",x=>fmt(x.fee));
  h+=lin("Investimento Total",x=>fmt(x.total),true);
  h+=lin("Impressões",x=>Math.round(x.impr).toLocaleString("pt-BR"));
  h+=lin("Cliques",x=>Math.round(x.clk).toLocaleString("pt-BR"));
  h+=lin("CPM",x=>fmt(x.cpm));
  h+=lin("CTR",x=>fmt1(x.ctr)+"%");
  h+=lin("Leads",x=>x.leads.toLocaleString("pt-BR"));
  h+=lin("Novos clientes",x=>x.nAq.toLocaleString("pt-BR"));
  h+=lin("Recompras",x=>x.nRc.toLocaleString("pt-BR"));
  h+=lin("Ganhos (total)",x=>x.gan.toLocaleString("pt-BR"),true);
  h+=lin("Win rate",x=>fmt1(x.wr*100)+"%");
  h+=lin("Orçamento gerado",x=>fmt(x.orc));
  h+=lin("Orçamento convertido",x=>fmt1(x.orcConv*100)+"%");
  h+=lin("Faturamento novos",x=>fmt(x.fAq));
  h+=lin("Faturamento recompra",x=>fmt(x.fRc));
  h+=lin("Faturamento total",x=>fmt(x.fat),true);
  if(periodMeta())h+=linM("Meta faturamento (pro-rata)",(mm,x)=>`${fmt(mm.fat)} · <span class="${x.fat/mm.fat>=1?'s-ok':x.fat/mm.fat>=.8?'s-warn':'s-bad'}">${Math.round(x.fat/mm.fat*100)}%</span>`);
  h+=lin("Ticket médio",x=>fmt(x.ticket));
  h+=lin("ROAS",x=>x.midia?fmt1(x.roas)+"×":"—");
  h+=lin("CAC",x=>x.gan?fmt(x.cac):"—");
  h+=lin("CPL",x=>x.leads?fmt(x.cpl):"—");
  h+=lin("Saldo (fat − custo total)",x=>`<span class="${x.saldo>=0?'s-ok':'s-bad'}">${fmt(x.saldo)}</span>`,true);
  return h+`</tbody></table></div>`;}
const RENDER={geral:rGeral,decisao:rDecisao,funil:rFunil,recompra:rRecompra,midia:rMidia,produtos:rProdutos,mensal:rMensal};
function drawCharts(){const M=mesesRange();
  if(FSCR==="geral"&&document.getElementById("cGeral")){const A=M.map(kpiMes);
    const fatT=A.map(x=>x.aqf+x.rcf),roas=A.map(x=>x.inv?(x.aqf+x.rcf)/x.inv:0);
    CH.g=new Chart(cGeral,{data:{labels:M,datasets:[
      {type:"bar",label:"Investimento",data:A.map(x=>x.inv),backgroundColor:"#3b3b55",stack:"inv",datalabels:{anchor:"end",align:"end",color:"#aab",font:{size:10},formatter:v=>v?fmt(v):""}},
      {type:"bar",label:"Fat. 1ª compra",data:A.map(x=>x.aqf),backgroundColor:"#ef4444",stack:"fat",datalabels:{display:false}},
      {type:"bar",label:"Fat. recompra",data:A.map(x=>x.rcf),backgroundColor:"#f59e0b",stack:"fat",datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:10,weight:"bold"},formatter:(v,ctx)=>fatT[ctx.dataIndex]?fmt(fatT[ctx.dataIndex]):""}},
      {type:"line",label:"ROAS",data:roas,yAxisID:"y1",borderColor:"#22c55e",tension:.3,datalabels:{display:false}}]},
      options:cOpt({layout:{padding:{top:34}},plugins:{legend:{position:"top",align:"end",labels:{color:"#8b8b9e",font:{size:11},boxWidth:14,padding:14}}},scales:{y:{stacked:true,grace:"18%",ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}},y1:{position:"right",ticks:{color:"#8b8b9e",callback:v=>v+"×"},grid:{display:false}},x:{stacked:true,ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}}}}),plugins:[ChartDataLabels]});}
  if(FSCR==="geral"&&document.getElementById("cVolG")){const A=M.map(kpiMes);
    const txr=A.map(x=>(x.aqg+x.rcg)?x.rcg/(x.aqg+x.rcg)*100:0);
    CH.vg=new Chart(cVolG,{data:{labels:M,datasets:[
      {type:"bar",label:"Aquisição",data:A.map(x=>x.aqg),backgroundColor:"#ef4444",datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:10,weight:"bold"},formatter:v=>v||""}},
      {type:"bar",label:"Recompra",data:A.map(x=>x.rcg),backgroundColor:"#f59e0b",datalabels:{anchor:"end",align:"end",color:"#f59e0b",font:{size:10,weight:"bold"},formatter:v=>v||""}},
      {type:"line",label:"Taxa recompra",data:txr,yAxisID:"y1",borderColor:"#60a5fa",tension:.3,datalabels:{display:false}}]},
      options:cOpt({layout:{padding:{top:34}},plugins:{legend:{position:"top",align:"end",labels:{color:"#8b8b9e",font:{size:11},boxWidth:14,padding:14}}},scales:{y:{grace:"18%",ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}},y1:{position:"right",ticks:{color:"#8b8b9e",callback:v=>Math.round(v)+"%"},grid:{display:false}},x:{ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}}}}),plugins:[ChartDataLabels]});}
  if(FSCR==="funil"){const F=funAgg();
    if(document.getElementById("cFunVol")){const ab=Math.max(0,F.lead-F.win-F.lost),pc=v=>(F.lead?Math.round(v/F.lead*100):0)+"%";
      CH.fvol=new Chart(cFunVol,{type:"bar",data:{labels:["Leads","Ganho","Perdido","Em aberto"],datasets:[{data:[F.lead,F.win,F.lost,ab],backgroundColor:["#ef4444","#22c55e","#7f1d1d","#3b3b55"],datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:11,weight:"bold"},formatter:v=>[v.toLocaleString("pt-BR"),pc(v)]}}]},options:cOpt({layout:{padding:{top:26}},plugins:{legend:{display:false}}}),plugins:[ChartDataLabels]});}
    if(document.getElementById("cFunVal")){const va=Math.max(0,F.vorc-F.vwin-F.vlost),pc=v=>(F.vorc?Math.round(v/F.vorc*100):0)+"%";
      CH.fval=new Chart(cFunVal,{type:"bar",data:{labels:["Orçado","Ganho","Perdido","Em aberto"],datasets:[{data:[F.vorc,F.vwin,F.vlost,va],backgroundColor:["#5b5b85","#22c55e","#7f1d1d","#3b3b55"],datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:9,weight:"bold"},formatter:v=>[fmt(v),pc(v)]}}]},options:cOpt({layout:{padding:{top:26}},plugins:{legend:{display:false}}}),plugins:[ChartDataLabels]});}
    D.qualfields.forEach(([i,lbl])=>{const el=document.getElementById("cQual"+i);if(!el)return;
      const meses=mesesQual(),qm=qualMensal(i),vals=qualDist(i).slice(0,6).map(x=>x[0]);
      const totMes=meses.map(m=>Object.values(qm[m]||{}).reduce((a,b)=>a+b,0));
      const ds=vals.map((v,vi)=>({label:v,data:meses.map(m=>(qm[m]||{})[v]||0),borderColor:QPAL[vi%QPAL.length],backgroundColor:QPAL[vi%QPAL.length],tension:.3,fill:false,pointRadius:2}));
      CH["q"+i]=new Chart(el,{type:"line",data:{labels:meses,datasets:ds},options:cOpt({interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{color:"#8b8b9e",font:{size:10},boxWidth:10}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y} · ${totMes[ctx.dataIndex]?Math.round(ctx.parsed.y/totMes[ctx.dataIndex]*100):0}%`}}}})});});}
  if(FSCR==="mensal"){const porMes={},porAno={};const rec=FECHKEY==="rec";
    for(const g of D.gan){if(g.d<FILT.ini||g.d>FILT.fim||!SELCH.has(g.c))continue;const mm=g.d.slice(0,7),yy=g.d.slice(0,4),val=rec?g.v:1;porMes[mm]=(porMes[mm]||0)+val;porAno[yy]=(porAno[yy]||0)+val;}
    const mk=Object.keys(porMes).sort(),yk=Object.keys(porAno).sort();
    const fmv=v=>rec?fmt(v):v.toLocaleString("pt-BR");
    if(document.getElementById("cFechMes"))CH.fm=new Chart(cFechMes,{type:"bar",data:{labels:mk.map(m=>m.slice(5)+"/"+m.slice(2,4)),datasets:[{data:mk.map(m=>porMes[m]),backgroundColor:rec?"#f59e0b":"#22c55e",datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:9,weight:"bold"},formatter:fmv}}]},options:cOpt({layout:{padding:{top:16}},plugins:{legend:{display:false}},scales:{y:{grace:"10%",ticks:{color:"#8b8b9e",callback:v=>rec?fmt(v):v},grid:{color:"#26263a"}},x:{ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}}}}),plugins:[ChartDataLabels]});
    if(document.getElementById("cFechAno"))CH.fa=new Chart(cFechAno,{type:"bar",data:{labels:yk,datasets:[{data:yk.map(y=>porAno[y]),backgroundColor:rec?"#f59e0b":"#22c55e",datalabels:{anchor:"end",align:"end",color:"#fff",font:{size:12,weight:"bold"},formatter:fmv}}]},options:cOpt({layout:{padding:{top:18}},plugins:{legend:{display:false}},scales:{y:{grace:"10%",ticks:{color:"#8b8b9e",callback:v=>rec?fmt(v):v},grid:{color:"#26263a"}},x:{ticks:{color:"#8b8b9e"},grid:{color:"#26263a"}}}}),plugins:[ChartDataLabels]});}}
function renderAll(){destroy();document.getElementById("main").innerHTML=RENDER[FSCR]();if(FSCR==="midia")renderDrill();drawCharts();}
function go(s){FSCR=s;document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on",t.dataset.s===s));renderAll();}

// ---- POPUPS ----
function togPop(id){const p=document.getElementById(id);const open=p.classList.contains("on");document.querySelectorAll(".pop").forEach(x=>x.classList.remove("on"));if(!open){p.classList.add("on");if(id==="popPeriod"){DRAFT={...FILT};calAnchor=monthStart(DRAFT.ini);pickStage=0;buildPicker();}}}
function closePop(){document.querySelectorAll(".pop").forEach(x=>x.classList.remove("on"));}
document.addEventListener("click",e=>{if(!e.target.closest(".fctl"))closePop();});
function buildPresets(){document.getElementById("presets").innerHTML=PRESETS.map(([n])=>`<button class="pset ${DRAFT.preset===n?'on':''}" onclick="pickPreset('${n}')">${n}</button>`).join("")+`<button class="pset ${DRAFT.preset==='custom'?'on':''}" onclick="pickPreset('custom')">Personalizar</button>`;}
function pickPreset(n){if(n==="custom"){DRAFT.preset="custom";pickStage=0;buildPicker();return;}const f=PRESETS.find(p=>p[0]===n)[1]();DRAFT.ini=f[0];DRAFT.fim=f[1];DRAFT.preset=n;FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function buildCal(elId,anchor){const d0=DD(anchor),y=d0.getFullYear(),mo=d0.getMonth();const first=new Date(y,mo,1),start=(first.getDay());const dim=new Date(y,mo+1,0).getDate();
  let h=`<div class="calhd"><button class="calnav" onclick="navCal(-1)">‹</button><span>${MES_PT[mo]} ${y}</span><button class="calnav" onclick="navCal(1)">›</button></div><div class="cgrid">`+["D","S","T","Q","Q","S","S"].map(x=>`<div class="dow">${x}</div>`).join("");
  for(let i=0;i<start;i++)h+=`<div class="cd out"></div>`;
  const cmp=DRAFT.cmpOn?cmpRange(DRAFT.ini,DRAFT.fim,DRAFT.cmpMode):null;
  for(let dn=1;dn<=dim;dn++){const ds=SD(new Date(y,mo,dn));let cls="cd";if(ds===DRAFT.ini||ds===DRAFT.fim)cls+=" sel";else if(ds>DRAFT.ini&&ds<DRAFT.fim)cls+=" inr";if(cmp&&ds>=cmp[0]&&ds<=cmp[1])cls+=" cmpr";h+=`<div class="${cls}" onclick="pickDay('${ds}')">${dn}</div>`;}
  document.getElementById(elId).innerHTML=h+`</div>`;}
function navCal(n){calAnchor=addM(calAnchor,n);buildPicker();}
function pickDay(ds){DRAFT.preset="custom";if(pickStage===0){DRAFT.ini=ds;DRAFT.fim=ds;pickStage=1;}else{if(ds<DRAFT.ini){DRAFT.fim=DRAFT.ini;DRAFT.ini=ds;}else DRAFT.fim=ds;pickStage=0;}buildPicker();}
function buildCmp(){document.getElementById("cmpTog").checked=DRAFT.cmpOn;
  document.getElementById("cmpOpts").innerHTML=DRAFT.cmpOn?[["month","Mês anterior"],["year","Ano anterior"],["prev","Período anterior"]].map(([k,l])=>`<button class="cmpopt ${DRAFT.cmpMode===k?'on':''}" onclick="setCmpMode('${k}')">${l}</button>`).join(" "):"";}
function onCmpTog(){DRAFT.cmpOn=document.getElementById("cmpTog").checked;if(DRAFT.cmpOn&&!DRAFT.cmpMode)DRAFT.cmpMode="month";FILT.cmpOn=DRAFT.cmpOn;FILT.cmpMode=DRAFT.cmpMode;buildPicker();renderAll();}
function setCmpMode(k){DRAFT.cmpMode=k;FILT.cmpMode=k;FILT.cmpOn=DRAFT.cmpOn;buildPicker();renderAll();}
function buildPicker(){buildPresets();buildCal("calA",calAnchor);buildCal("calB",addM(calAnchor,1));buildCmp();}
function applyPeriod(){FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function updPeriodLabel(){document.getElementById("vPeriod").textContent=fmtRange(FILT.ini,FILT.fim);}

// ---- CANAL multi-select ----
function buildChan(){document.getElementById("chanList").innerHTML=CHANNELS.map(c=>`<label class="chk"><input type="checkbox" ${SELCH.has(c)?'checked':''} onchange="tgch('${c}')"><span>${c}${D.canais_meta.includes(c)?' <span class="s-ok">●</span>':''}</span></label>`).join("");updChanLabel();}
function updChanLabel(){document.getElementById("vChan").textContent=periodMeta()?"Só pagos":SELCH.size===CHANNELS.length?"Todos":SELCH.size+" canais";}
function tgch(c){SELCH.has(c)?SELCH.delete(c):SELCH.add(c);buildChan();renderAll();}
function chMeta(){SELCH=new Set(D.canais_meta.filter(c=>CHANNELS.includes(c)));buildChan();renderAll();}
function chAll(){SELCH=new Set(CHANNELS);buildChan();renderAll();}

document.getElementById("nav").innerHTML=SCR.map(([k,l])=>`<button class="tab ${k==='geral'?'on':''}" data-s="${k}" onclick="go('${k}')">${l}</button>`).join("");
document.getElementById("ts").textContent="atualizado "+D.gerado_em;
updPeriodLabel();buildChan();renderAll();
</script></body></html>"""
html = TEMPLATE.replace("__DADOS__", json.dumps(DADOS, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"OK monitor.html — {len(html):,} bytes · {len(GAN)} ganhos · {len(INVDAY)} invday · {len(DRILL['rows'])} drill")
