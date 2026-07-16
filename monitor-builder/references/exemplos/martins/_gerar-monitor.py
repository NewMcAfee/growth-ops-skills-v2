# -*- coding: utf-8 -*-
# =============================================================================
# _gerar-monitor.py — Martins Locações · Monitor de Aquisição × Recompra
# -----------------------------------------------------------------------------
# Lê os CSVs do feed + contrato-cockpit.yml (metas em runtime) e gera:
#   - monitor.json  (snapshot determinístico p/ skills de análise — git-ignored se PII)
#   - monitor.html  (dashboard auto-contido com FILTRO DE CANAL ao vivo)
#
# Modelo Martins (≠ Sigo): eixo Aquisição × Recompra. Ganho = bd-buy. 1º ganho do
# lead_id (menor crosed_at no histórico) = AQUISIÇÃO; ganhos seguintes = RECOMPRA.
# Canal do ganho vem de leads-pipeline por deal_id.
#
# KRs do OKR contam SÓ canais_meta (paid_google+paid_meta = Máquina de Aquisição).
# O resto (organic, sem atribuição) aparece na visão geral e no filtro, mas não
# conta pra meta. O HTML agrega no JS conforme os canais marcados (padrão Sigo).
# =============================================================================
import csv, json, sys
from datetime import datetime
from pathlib import Path

csv.field_size_limit(10**7)
BASE = Path(__file__).resolve().parent
OUT_JSON = BASE / "monitor.json"
OUT_HTML = BASE / "monitor.html"
CONTRATO = BASE / "contrato-cockpit.yml"
HOJE = datetime.now()

META_DEFAULT = {
    "quarter_vigencia": "2026-Q2", "inicio": "2026-04-01", "fim": "2026-06-30",
    "canais_meta": ["paid_google", "paid_meta"],
    "aquisicao": {"faturamento": 342000, "clientes": 480, "ticket_medio": 950,
                  "investimento": 114000, "roas_min": 3.0, "cac_max": 239.82},
}
def load_contrato():
    try:
        import yaml
        c = yaml.safe_load(CONTRATO.read_text(encoding="utf-8")) or {}
        p, m = c.get("periodo", {}), c.get("metas", {})
        return {
            "quarter_vigencia": p.get("quarter_vigencia", "2026-Q2"),
            "inicio": p.get("inicio", "2026-04-01"), "fim": p.get("fim", "2026-06-30"),
            "canais_meta": c.get("canais_meta", META_DEFAULT["canais_meta"]),
            "aquisicao": (m.get("aquisicao") or META_DEFAULT["aquisicao"]),
        }
    except Exception as e:
        print(f"WARN: contrato indisponível ({e}) — META default.", file=sys.stderr)
        return dict(META_DEFAULT)

def parse_num(s):
    if s is None: return 0.0
    s = str(s).strip().replace("R$", "").replace(" ", "")
    if not s: return 0.0
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def parse_date(s):
    if not s: return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try: return datetime.strptime(s, fmt)
        except ValueError: continue
    return None

def read_csv(path):
    p = BASE / path
    if not p.exists(): return []
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

C = load_contrato()
META = C["aquisicao"]
CANAIS_META = C["canais_meta"]
INI, FIM = parse_date(C["inicio"]), parse_date(C["fim"])
def no_periodo(dt): return dt is not None and INI <= dt <= FIM

ganhos   = read_csv("bd-buy.csv")
pipeline = read_csv("leads-pipeline.csv")
ads      = read_csv("bd-ads.csv")

canal_por_deal = {}
for r in pipeline:
    did = (r.get("deal_id") or "").strip()
    if did: canal_por_deal[did] = (r.get("canal") or "").strip() or "(sem atribuição)"

# classificação aquisição × recompra (1º ganho lifetime do lead = aquisição)
por_lead = {}
for g in ganhos:
    lid = (g.get("lead_id") or "").strip()
    if lid: por_lead.setdefault(lid, []).append(parse_date(g.get("crosed_at")))
primeiro_ganho = {lid: (min([d for d in ds if d], default=None)) for lid, ds in por_lead.items()}
def classifica(g):
    dt = parse_date(g.get("crosed_at")); pg = primeiro_ganho.get((g.get("lead_id") or "").strip())
    if pg is None or dt is None: return "aq"
    return "aq" if dt <= pg else "rc"

# agregação por canal × eixo, com sub-breakdowns (mes, produto) p/ o filtro JS
def novo(): return {"g": 0, "f": 0.0, "mes": {}, "prod": {}}
canais = {}   # canal -> {"aq": {...}, "rc": {...}, "inv": 0.0}
def bucket(canal): return canais.setdefault(canal, {"aq": novo(), "rc": novo(), "inv": 0.0})

for g in ganhos:
    dt = parse_date(g.get("crosed_at"))
    if not no_periodo(dt): continue
    eixo = classifica(g); val = parse_num(g.get("total_value"))
    canal = canal_por_deal.get((g.get("deal_id") or "").strip(), "(sem atribuição)")
    prod = (g.get("product_cart") or "—").strip() or "—"; mes = dt.strftime("%Y-%m")
    e = bucket(canal)[eixo]
    e["g"] += 1; e["f"] += val
    e["mes"].setdefault(mes, {"g": 0, "f": 0.0}); e["mes"][mes]["g"] += 1; e["mes"][mes]["f"] += val
    e["prod"].setdefault(prod, {"g": 0, "f": 0.0}); e["prod"][prod]["g"] += 1; e["prod"][prod]["f"] += val

for r in ads:
    dt = parse_date(r.get("data"))
    if not no_periodo(dt): continue
    inv = parse_num(r.get("investimento"))
    if inv <= 0: continue
    bucket((r.get("canal") or "(sem atribuição)").strip() or "(sem atribuição)")["inv"] += inv

# ----- KRs sobre canais_meta (a verdade do OKR) -----
def agrega(lista_canais):
    aqg = aqf = rcg = rcf = inv = 0.0
    for c in lista_canais:
        b = canais.get(c)
        if not b: continue
        aqg += b["aq"]["g"]; aqf += b["aq"]["f"]; rcg += b["rc"]["g"]; rcf += b["rc"]["f"]; inv += b["inv"]
    return aqg, aqf, rcg, rcf, inv

aqg, aqf, rcg, rcf, inv = agrega(CANAIS_META)
ticket = (aqf / aqg) if aqg else 0.0
roas = (aqf / inv) if inv else 0.0
cac = (inv / aqg) if aqg else 0.0
dias_tot = (FIM - INI).days + 1
dias_dec = max(1, min(dias_tot, (HOJE - INI).days + 1))

def kr(real, meta, maior=True):
    pct = (real / meta) if meta else None
    if maior: st = "ok" if (pct and pct >= 1) else ("warn" if (pct and pct >= 0.8) else "off")
    else: st = "ok" if (0 < real <= meta) else "off"
    return {"realizado": round(real, 2), "meta": meta, "pct": round(pct, 4) if pct else None, "status": st}

# totais gerais (todos os canais) p/ contexto
g_aqg, g_aqf, g_rcg, g_rcf, g_inv = agrega(list(canais.keys()))

snapshot = {
    "projeto": "martins-locacoes", "gerado_em": HOJE.strftime("%Y-%m-%d %H:%M:%S"),
    "quarter_vigencia": C["quarter_vigencia"],
    "periodo": {"inicio": C["inicio"], "fim": C["fim"], "dias_decorridos": dias_dec,
                "dias_totais": dias_tot, "pace": round(dias_dec / dias_tot, 4)},
    "canais_meta": CANAIS_META,
    "aquisicao_meta": {   # ← o que conta pro OKR (só canais pagos)
        "faturamento": kr(aqf, META["faturamento"]), "clientes": kr(aqg, META["clientes"]),
        "ticket_medio": kr(ticket, META["ticket_medio"]), "investimento": kr(inv, META["investimento"]),
        "roas": {"realizado": round(roas, 2), "meta": META["roas_min"], "status": "ok" if roas >= META["roas_min"] else "off"},
        "cac": kr(cac, META["cac_max"], maior=False),
    },
    "recompra_meta": {"ganhos": rcg, "faturamento": round(rcf, 2),
                      "ticket_medio": round(rcf / rcg, 2) if rcg else 0.0},
    "geral_todos_canais": {"aquisicao_ganhos": int(g_aqg), "aquisicao_faturamento": round(g_aqf, 2),
                           "recompra_ganhos": int(g_rcg), "recompra_faturamento": round(g_rcf, 2),
                           "investimento": round(g_inv, 2)},
    "por_canal": {c: {"aq_ganhos": b["aq"]["g"], "aq_faturamento": round(b["aq"]["f"], 2),
                      "rc_ganhos": b["rc"]["g"], "rc_faturamento": round(b["rc"]["f"], 2),
                      "investimento": round(b["inv"], 2), "conta_meta": c in CANAIS_META}
                  for c, b in canais.items()},
}
OUT_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK monitor.json | META(pagos): aq {int(aqg)} ganhos / R$ {aqf:,.0f} | invest R$ {inv:,.0f} | ROAS {roas:.2f} | CAC R$ {cac:,.0f}")
print(f"   GERAL(todos): aq {int(g_aqg)} ganhos / R$ {g_aqf:,.0f}")
sys.exit(0)  # HTML rico (9 telas) é responsabilidade do _render_monitor.py

# ------------------------------------------------------------------ HTML c/ filtro JS
DADOS_JS = {
    "metas": {"faturamento": META["faturamento"], "clientes": META["clientes"], "ticket": META["ticket_medio"],
              "investimento": META["investimento"], "roas": META["roas_min"], "cac": META["cac_max"]},
    "canais_meta": CANAIS_META, "periodo": snapshot["periodo"], "quarter": C["quarter_vigencia"],
    "canais": {c: {
        "aq": {"g": b["aq"]["g"], "f": round(b["aq"]["f"], 2), "mes": b["aq"]["mes"], "prod": b["aq"]["prod"]},
        "rc": {"g": b["rc"]["g"], "f": round(b["rc"]["f"], 2), "mes": b["rc"]["mes"], "prod": b["rc"]["prod"]},
        "inv": round(b["inv"], 2)} for c, b in canais.items()},
}
html = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor — Martins Locações</title><style>
:root{--bg:#0a0a0f;--card:#15151f;--bd:#26263a;--mut:#8b8b9e;--red:#ef4444;--grn:#22c55e;--amb:#f59e0b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#f5f5f7;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1140px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:30px;margin:0 0 4px;font-weight:800}.sub{color:var(--mut);margin:0 0 2px}
.obj{background:linear-gradient(135deg,#1a0c0f,#15151f);border:1px solid var(--bd);border-left:4px solid var(--red);border-radius:12px;padding:16px 20px;margin:16px 0 22px}
h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:32px 0 12px}
.filtro{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px 18px;margin-bottom:8px}
.filtro label{display:inline-flex;align-items:center;gap:6px;margin:4px 14px 4px 0;font-size:14px;cursor:pointer}
.filtro .quick{margin-right:16px}.btn{background:#202033;border:1px solid var(--bd);color:#f5f5f7;border-radius:8px;padding:5px 12px;cursor:pointer;font-size:13px;margin-right:8px}
.btn:hover{border-color:var(--red)}
.viewbadge{font-size:13px;color:var(--mut);margin:6px 0 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px}
.ct{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
.cv{font-size:27px;font-weight:800;margin:6px 0 2px}.cm{font-size:13px;color:var(--mut)}.cs{font-size:12px;color:var(--mut);margin-top:4px}
table{width:100%;border-collapse:collapse;margin-top:6px;font-size:14px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--bd)}
th{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td:not(:first-child),th:not(:first-child){text-align:right}
tr.meta td:first-child::after{content:" ●";color:var(--grn)}
.foot{color:var(--mut);font-size:12px;margin-top:40px;border-top:1px solid var(--bd);padding-top:14px}
</style></head><body><div class="wrap">
<h1>Monitor de Aquisição × Recompra</h1>
<p class="sub" id="periodo"></p>
<div class="obj"><strong>Objetivo Q2:</strong> Validar a Máquina de Aquisição — R$ 342.000 em faturamento de novos clientes com ROAS &gt; 3. <em>Só canais pagos contam pro OKR.</em></div>
<div class="filtro">
  <span class="quick"><button class="btn" onclick="setMeta()">Só meta (pagos)</button><button class="btn" onclick="setTodos()">Geral (todos)</button></span>
  <span id="checks"></span>
</div>
<p class="viewbadge" id="badge"></p>
<h2>KRs — Aquisição (canais selecionados)</h2>
<div class="grid" id="cards"></div>
<h2>Recompra (só realizado — sem meta)</h2>
<div class="grid" id="rccards"></div>
<h2>Por canal (sempre todos — ● conta pro OKR)</h2>
<table id="tcanal"><thead><tr><th>Canal</th><th>Ganhos aq</th><th>Fat. aq</th><th>Invest</th><th>CAC</th><th>ROAS</th></tr></thead><tbody></tbody></table>
<h2>Por produto (canais selecionados, top 15)</h2>
<table id="tprod"><thead><tr><th>Produto</th><th>Aquisição</th><th>Recompra</th><th>Faturamento</th></tr></thead><tbody></tbody></table>
<h2>Série mensal (canais selecionados)</h2>
<table id="tmes"><thead><tr><th>Mês</th><th>Ganhos aq</th><th>Fat. aq</th><th>Ganhos rc</th><th>Fat. rc</th></tr></thead><tbody></tbody></table>
<p class="foot">Snapshot determinístico em <code>monitor.json</code>. Classificação: 1º ganho do lead_id = aquisição. KRs do OKR contam só <code>paid_google</code>+<code>paid_meta</code>; o filtro permite ver o geral. Fonte: feed growthpack 2×/dia.</p>
<script>
const D = __DADOS__;
const fmt = v => "R$ " + Math.round(v).toLocaleString("pt-BR");
const COR = {ok:"#22c55e",warn:"#f59e0b",off:"#ef4444"};
const CANAIS = Object.keys(D.canais).sort((a,b)=>(D.canais[b].aq.f)-(D.canais[a].aq.f));
let sel = new Set(D.canais_meta.filter(c=>D.canais[c]));
document.getElementById("periodo").textContent = `Martins Locações · ${D.quarter} (${D.periodo.inicio} → ${D.periodo.fim}) · pace ${Math.round(D.periodo.pace*100)}%`;

function renderChecks(){
  document.getElementById("checks").innerHTML = CANAIS.map(c=>{
    const on = sel.has(c) ? "checked":"";
    const meta = D.canais_meta.includes(c) ? " ●":"";
    return `<label><input type="checkbox" ${on} onchange="toggle('${c}')">${c}${meta} <span style="color:#8b8b9e">(${D.canais[c].aq.g})</span></label>`;
  }).join("");
}
function toggle(c){ sel.has(c)?sel.delete(c):sel.add(c); render(); }
function setMeta(){ sel = new Set(D.canais_meta.filter(c=>D.canais[c])); render(); }
function setTodos(){ sel = new Set(CANAIS); render(); }

function agrega(){
  let a={g:0,f:0},r={g:0,f:0},inv=0,mes={},prod={};
  for(const c of sel){ const b=D.canais[c]; if(!b)continue;
    a.g+=b.aq.g; a.f+=b.aq.f; r.g+=b.rc.g; r.f+=b.rc.f; inv+=b.inv;
    for(const m in b.aq.mes){ mes[m]=mes[m]||{ag:0,af:0,rg:0,rf:0}; mes[m].ag+=b.aq.mes[m].g; mes[m].af+=b.aq.mes[m].f; }
    for(const m in b.rc.mes){ mes[m]=mes[m]||{ag:0,af:0,rg:0,rf:0}; mes[m].rg+=b.rc.mes[m].g; mes[m].rf+=b.rc.mes[m].f; }
    for(const p in b.aq.prod){ prod[p]=prod[p]||{aq:0,rc:0,f:0}; prod[p].aq+=b.aq.prod[p].g; prod[p].f+=b.aq.prod[p].f; }
    for(const p in b.rc.prod){ prod[p]=prod[p]||{aq:0,rc:0,f:0}; prod[p].rc+=b.rc.prod[p].g; }
  }
  return {a,r,inv,mes,prod};
}
function card(t,val,meta,st,sub){ return `<div class="card"><div class="ct">${t}</div><div class="cv" style="color:${COR[st]||'#fff'}">${val}</div><div class="cm">${meta}</div><div class="cs">${sub||''}</div></div>`; }
function stPct(real,meta){ const p=meta?real/meta:null; return p==null?'warn':(p>=1?'ok':(p>=0.8?'warn':'off')); }

function render(){
  const X = agrega(), M = D.metas;
  const ticket = X.a.g?X.a.f/X.a.g:0, roas=X.inv?X.a.f/X.inv:0, cac=X.a.g?X.inv/X.a.g:0;
  const ehMeta = sel.size===D.canais_meta.length && D.canais_meta.every(c=>sel.has(c));
  document.getElementById("badge").innerHTML = ehMeta
    ? "Visão: <strong style='color:#22c55e'>META (canais pagos)</strong> — realizado vs OKR."
    : `Visão: <strong style='color:#f59e0b'>filtro custom</strong> (${sel.size} canais) — fora do recorte oficial do OKR.`;
  const pc = p => p==null?'—':Math.round(p*100)+'% da meta';
  document.getElementById("cards").innerHTML =
    card("Faturamento — novos", fmt(X.a.f), "meta "+fmt(M.faturamento), stPct(X.a.f,M.faturamento), pc(X.a.f/M.faturamento)) +
    card("Novos clientes", X.a.g, "meta "+M.clientes, stPct(X.a.g,M.clientes), pc(X.a.g/M.clientes)) +
    card("Ticket médio", fmt(ticket), "meta "+fmt(M.ticket), stPct(ticket,M.ticket), pc(ticket/M.ticket)) +
    card("Investimento", fmt(X.inv), "meta "+fmt(M.investimento), 'warn', pc(X.inv/M.investimento)) +
    card("ROAS", roas.toFixed(2), "meta > "+M.roas, roas>=M.roas?'ok':'off', "faturamento ÷ investimento") +
    card("CAC blended", X.a.g?fmt(cac):'—', "meta < "+fmt(M.cac), (cac>0&&cac<=M.cac)?'ok':'off', "investimento ÷ clientes");
  document.getElementById("rccards").innerHTML =
    card("Recompras", X.r.g, "sem meta", 'warn', "clientes recorrentes") +
    card("Faturamento recompra", fmt(X.r.f), "sem meta", 'warn', "") +
    card("Ticket médio recompra", X.r.g?fmt(X.r.f/X.r.g):'—', "sem meta", 'warn', "");
  document.querySelector("#tcanal tbody").innerHTML = CANAIS.map(c=>{ const b=D.canais[c];
    const cac=b.aq.g?b.inv/b.aq.g:0, roas=b.inv?b.aq.f/b.inv:0;
    const cls=D.canais_meta.includes(c)?' class="meta"':'';
    return `<tr${cls}><td>${c}</td><td>${b.aq.g}</td><td>${fmt(b.aq.f)}</td><td>${fmt(b.inv)}</td><td>${b.aq.g?fmt(cac):'—'}</td><td>${b.inv?roas.toFixed(2):'—'}</td></tr>`;
  }).join("");
  const prods=Object.entries(X.prod).sort((a,b)=>b[1].f-a[1].f).slice(0,15);
  document.querySelector("#tprod tbody").innerHTML = prods.map(([p,d])=>`<tr><td>${p}</td><td>${d.aq}</td><td>${d.rc}</td><td>${fmt(d.f)}</td></tr>`).join("");
  const meses=Object.keys(X.mes).sort();
  document.querySelector("#tmes tbody").innerHTML = meses.map(m=>{const d=X.mes[m];return `<tr><td>${m}</td><td>${d.ag}</td><td>${fmt(d.af)}</td><td>${d.rg}</td><td>${fmt(d.rf)}</td></tr>`;}).join("");
}
renderChecks(); render();
</script></div></body></html>"""
html = html.replace("__DADOS__", json.dumps(DADOS_JS, ensure_ascii=False))
OUT_HTML.write_text(html, encoding="utf-8")
print(f"OK monitor.html — {len(html)} bytes (filtro de canal ativo)")
