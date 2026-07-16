# -*- coding: utf-8 -*-
# =============================================================================
# _render_monitor.py · v3 — monitor.html · cockpit do gestor
# Telas (nav vertical à esquerda) + filtros centralizados (Período c/ Semana/Mês
# atual · Canal multi-seleção genérico p/ N canais · Comparativo de período) +
# rótulos nos gráficos + tooltips explicativos + velocidade do funil (tempo
# entre etapas) + Faturamento/Ticket na visão geral.
# Shell estático + engine de agregação em JS. Títulos Archivo · Chart.js CDN.
# =============================================================================
import json

CSS = r"""
:root{
 --v4-red:#E50914;--v4-red-light:#FF4040;--v4-red-dark:#B8000E;--v4-yellow:#FFDD00;
 --white:#fff;--black:#1A1814;--row-odd:#141414;--row-even:#1B1B1B;--border:#333;
 --bg:#121010;--elev:#1E1C1C;--muted:rgba(255,255,255,.62);--subtle:rgba(255,255,255,.40);
 --ok:#2FBF71;--ok-bg:rgba(47,191,113,.12);--warn:#FFC400;--warn-bg:rgba(255,196,0,.12);
 --bad:#E50914;--bad-bg:rgba(229,9,20,.14);--muted-bg:rgba(255,255,255,.05);
 --fdisplay:"Archivo","Arial Black",sans-serif;--fbody:"IBM Plex Sans","Calibri",sans-serif;
 --fmono:"JetBrains Mono","Courier New",monospace;
}
@font-face{font-family:'IBM Plex Sans';src:url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-Regular.ttf') format('truetype');font-weight:400}
@font-face{font-family:'IBM Plex Sans';src:url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-Medium.ttf') format('truetype');font-weight:500}
@font-face{font-family:'IBM Plex Sans';src:url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-SemiBold.ttf') format('truetype');font-weight:600}
@font-face{font-family:'IBM Plex Sans';src:url('../../00-sistema/assets/fontes/IBMPlexSans/IBMPlexSans-Bold.ttf') format('truetype');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--white);font-family:var(--fbody);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
.topbar{height:4px;background:var(--v4-red)}
.wrap{max-width:1340px;margin:0 auto;padding:0 24px 64px}
h1,h2,h3,h4,.disp{font-family:var(--fdisplay);font-weight:800;letter-spacing:.2px}
header.head{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:22px 0 12px;flex-wrap:wrap}
.head h1{font-size:24px;line-height:1.1;letter-spacing:.3px}
.head h1 b{color:var(--v4-red)}
.fresh{font-family:var(--fmono);font-size:11px;color:var(--subtle);text-align:right;line-height:1.7}
.fresh b{color:var(--muted)}
/* filtros estilo Google Ads (date-range picker + multi-select) */
.filterbar{position:sticky;top:0;z-index:40;background:rgba(18,16,16,.92);backdrop-filter:blur(8px);
 border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:11px 0 9px;margin-bottom:4px}
.fb{display:flex;flex-wrap:wrap;gap:11px;align-items:center;justify-content:center}
.fctl{position:relative}
.fbtn{display:inline-flex;align-items:center;gap:9px;background:var(--elev);border:1px solid var(--border);color:var(--white);border-radius:9px;padding:8px 14px;cursor:pointer;font-family:var(--fbody);font-size:13px;transition:border-color .12s}
.fbtn:hover{border-color:var(--v4-red-light)}
.fbtn .cap{color:var(--subtle);font-size:10px;text-transform:uppercase;letter-spacing:.6px;font-weight:600}
.fbtn .val{font-weight:700;font-family:var(--fmono);font-size:12.5px}
.fbtn .cmpv{color:var(--v4-yellow);font-size:11.5px;font-weight:600}
.fbtn .ar{color:var(--muted);font-size:10px}
.pop{position:absolute;top:calc(100% + 7px);left:0;background:var(--elev);border:1px solid var(--border);border-radius:12px;box-shadow:0 20px 54px rgba(0,0,0,.7);z-index:60;display:none}
.pop.on{display:block}.pop.right{left:auto;right:0}
.dpick{display:flex;min-width:576px}
.presets{flex:none;width:182px;border-right:1px solid var(--border);padding:8px;max-height:336px;overflow:auto}
.pset{display:block;width:100%;text-align:left;background:none;border:none;color:var(--muted);padding:8px 11px;border-radius:7px;cursor:pointer;font-family:var(--fbody);font-size:13px}
.pset:hover{background:var(--muted-bg);color:var(--white)}.pset.on{background:var(--v4-red);color:#fff;font-weight:600}
.calwrap{padding:13px 15px}.cals{display:flex;gap:18px}.cal{width:212px}
.calhd{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;font-size:13px;font-weight:700;font-family:var(--fbody)}
.calnav{background:var(--bg);border:1px solid var(--border);color:var(--white);border-radius:6px;width:25px;height:25px;cursor:pointer}.calnav:hover{border-color:var(--v4-red)}
.cgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cgrid .dow{font-size:10px;color:var(--subtle);text-align:center;padding:3px 0;font-weight:600}
.cd{text-align:center;padding:6px 0;font-size:12px;border-radius:6px;cursor:pointer;color:var(--white)}
.cd:hover{background:var(--muted-bg)}.cd.out{color:transparent;cursor:default}.cd.out:hover{background:none}
.cd.sel{background:var(--v4-red);color:#fff;font-weight:700}.cd.inr{background:rgba(229,9,20,.20)}
.cd.cmpr{box-shadow:inset 0 0 0 1px var(--v4-yellow)}
.cmpbar{border-top:1px solid var(--border);margin-top:11px;padding-top:11px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.cmplbl{font-size:12.5px;color:var(--muted)}
.switch{position:relative;width:38px;height:21px;flex:none}.switch input{opacity:0;width:0;height:0}
.sl{position:absolute;inset:0;background:var(--bg);border:1px solid var(--border);border-radius:999px;transition:.2s;cursor:pointer}
.sl:before{content:"";position:absolute;height:15px;width:15px;left:2px;top:2px;background:var(--muted);border-radius:50%;transition:.2s}
.switch input:checked+.sl{background:var(--v4-red);border-color:var(--v4-red)}.switch input:checked+.sl:before{transform:translateX(17px);background:#fff}
.cmpopt{background:var(--bg);border:1px solid var(--border);color:var(--muted);border-radius:7px;padding:5px 11px;cursor:pointer;font-family:var(--fbody);font-size:12.5px}
.cmpopt.on{background:var(--v4-yellow);border-color:var(--v4-yellow);color:#1a1a1a;font-weight:700}
.popfoot{display:flex;justify-content:flex-end;gap:8px;padding:11px 15px;border-top:1px solid var(--border)}
.bt{border:1px solid var(--border);background:var(--bg);color:var(--white);border-radius:7px;padding:7px 16px;cursor:pointer;font-family:var(--fbody);font-size:13px}.bt.pri{background:var(--v4-red);border-color:var(--v4-red);font-weight:600}
.chanpop{min-width:236px;padding:9px}
.chk{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:7px;cursor:pointer;font-size:13px}.chk:hover{background:var(--muted-bg)}
.chk input{accent-color:var(--v4-red);width:15px;height:15px}
.chquick{display:flex;gap:6px;padding:4px 6px 9px;border-bottom:1px solid var(--border);margin-bottom:6px}
.qbtn{flex:1;background:var(--bg);border:1px solid var(--border);color:var(--muted);border-radius:7px;padding:6px;cursor:pointer;font-family:var(--fbody);font-size:12px}.qbtn:hover{border-color:var(--v4-red);color:var(--white)}
.frange{text-align:center;font-family:var(--fmono);font-size:11px;color:var(--subtle);margin-top:9px}
@media(max-width:680px){.dpick{flex-direction:column;min-width:300px}.presets{width:auto;border-right:none;border-bottom:1px solid var(--border);max-height:150px}.cals{flex-direction:column}.cal{width:auto}}
/* layout: nav vertical à esquerda + main */
.layout{display:flex;gap:26px;align-items:flex-start;margin-top:16px}
.sidenav{flex:none;width:182px;position:sticky;top:78px;display:flex;flex-direction:column;gap:3px}
.tab{background:transparent;border:0;border-left:3px solid transparent;color:var(--muted);text-align:left;
 padding:10px 14px;cursor:pointer;font-family:var(--fbody);font-weight:600;font-size:14px;
 letter-spacing:.2px;border-radius:0 7px 7px 0;transition:all .12s}
.tab:hover{color:var(--white);background:var(--muted-bg)}
.tab.on{color:var(--white);border-left-color:var(--v4-red);background:var(--elev)}
.main{flex:1;min-width:0}
.screen{display:none}.screen.on{display:block;animation:fade .2s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
h2.sec{font-size:21px;text-transform:uppercase;margin:24px 0 4px;display:flex;align-items:center;gap:10px}
.main>.screen>h2.sec:first-child{margin-top:0}
h2.sec::before{content:"";width:5px;height:19px;background:var(--v4-red);border-radius:2px}
.sec-desc{color:var(--muted);font-size:13px;margin-bottom:14px}
.grid{display:grid;gap:14px}.g4{grid-template-columns:repeat(4,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g2{grid-template-columns:repeat(2,1fr)}
.card{background:var(--elev);border:1px solid var(--border);border-radius:10px;padding:16px 18px}
.card.accent{border-left:3px solid var(--v4-red)}
.lab{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:600}
.okr .big{font-size:36px;line-height:1;margin:8px 0 2px;font-weight:800}
.okr .meta{font-size:12px;color:var(--subtle)}
.okr .bar{height:7px;border-radius:4px;background:var(--muted-bg);margin:12px 0 8px;overflow:hidden}
.okr .bar>i{display:block;height:100%;border-radius:4px}
.okr .proj{font-size:11.5px;color:var(--muted)}
.pill{display:inline-block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;padding:2px 8px;border-radius:999px}
.s-ok{color:var(--ok)}.s-warn{color:var(--warn)}.s-bad{color:var(--bad)}.s-muted{color:var(--subtle)}
.bg-ok{background:var(--ok-bg);color:var(--ok)}.bg-warn{background:var(--warn-bg);color:var(--warn)}
.bg-bad{background:var(--bad-bg);color:var(--bad)}.bg-muted{background:var(--muted-bg);color:var(--muted)}
.fill-ok{background:var(--ok)}.fill-warn{background:var(--warn)}.fill-bad{background:var(--bad)}
.qkpi{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border)}
.qkpi:last-child{border-bottom:0}.qkpi .v{font-size:22px;font-weight:800}
.tag{font-size:10px;color:var(--subtle);font-family:var(--fmono)}
.kstrip{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.kbox{background:var(--elev);border:1px solid var(--border);border-radius:9px;padding:13px 14px}
.kbox .l{font-size:10.5px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted)}
.kbox .n{font-size:25px;line-height:1.1;margin-top:5px;font-weight:800;font-family:var(--fdisplay)}
.kbox .x{font-size:11px;color:var(--subtle);margin-top:2px}
.kbox .kd{font-size:11px;margin-top:4px;font-weight:600}
.deccol h3{font-size:16px;text-transform:uppercase;display:flex;gap:8px;align-items:center;margin-bottom:10px}
.decitem{background:var(--elev);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin-bottom:8px}
.decitem .nm{font-weight:600;font-size:12.5px;line-height:1.3}.decitem .mo{font-size:11.5px;color:var(--muted);margin-top:3px}
.decitem.bad{border-left:3px solid var(--bad)}.decitem.ok{border-left:3px solid var(--ok)}.decitem.warn{border-left:3px solid var(--warn)}
.empty{color:var(--subtle);font-size:12px;font-style:italic;padding:8px 0}
.funrow{display:flex;align-items:center;gap:14px;margin-bottom:7px}
.funrow .fn{width:130px;font-size:12.5px;color:var(--muted);text-align:right;flex:none}
.funrow .ft{flex:1;background:var(--muted-bg);border-radius:5px;height:34px;position:relative;overflow:hidden}
.funrow .ft>i{display:block;height:100%;background:linear-gradient(90deg,var(--v4-red-dark),var(--v4-red));border-radius:5px}
.funrow .ft .vlabel{position:absolute;left:12px;top:0;height:34px;display:flex;align-items:center;font-weight:800;font-size:18px;font-family:var(--fdisplay)}
.funrow .fr{width:96px;flex:none;font-size:12px;color:var(--muted);font-family:var(--fmono)}.funrow .fr b{color:var(--white)}
.tbl-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:12.5px;min-width:600px}
thead th{background:var(--v4-red);color:#fff;text-align:right;padding:9px 11px;font-weight:600;white-space:nowrap}
thead th:first-child{text-align:left}
tbody td{padding:8px 11px;text-align:right;border-top:1px solid var(--border);white-space:nowrap}
tbody td:first-child{text-align:left;white-space:normal;max-width:360px}
tbody tr:nth-child(odd){background:var(--row-odd)}tbody tr:nth-child(even){background:var(--row-even)}
.bdg{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;white-space:nowrap}
.muted-n{color:var(--subtle)}
.subtabs{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}
.stbtn{background:var(--elev);border:1px solid var(--border);color:var(--muted);padding:7px 16px;border-radius:7px;cursor:pointer;font-family:var(--fbody);font-size:13px;font-weight:600}
.stbtn.on{background:var(--v4-red);color:#fff;border-color:var(--v4-red)}
/* F5.1: sort clicável + filtro do drill + selects do cruzamento */
.tbl-wrap th{cursor:pointer;user-select:none}
.tbl-wrap th[data-dir="desc"]::after{content:" ▼";font-size:9px;color:var(--v4-yellow)}
.tbl-wrap th[data-dir="asc"]::after{content:" ▲";font-size:9px;color:var(--v4-yellow)}
.tfilter{width:100%;max-width:460px;background:var(--elev);border:1px solid var(--border);color:var(--white);border-radius:9px;padding:8px 13px;font-family:var(--fbody);font-size:13px;margin:2px 0 10px}
.tfilter:focus{outline:none;border-color:var(--v4-red-light)}
.hidectx{display:none}
.dbxsel{background:var(--elev);border:1px solid var(--border);color:var(--white);border-radius:8px;padding:7px 11px;font-family:var(--fbody);font-size:13px;cursor:pointer;max-width:100%}
/* F5.2: biblioteca de criativos + popup */
.libgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:13px;margin-top:10px}
.libcard{background:var(--elev);border:1px solid var(--border);border-radius:12px;overflow:hidden;cursor:pointer;transition:border-color .12s,transform .12s}
.libcard:hover{border-color:var(--v4-red-light);transform:translateY(-2px)}
.libcard img{width:100%;height:170px;object-fit:cover;display:block;background:#0c0b0b}
.libph{width:100%;height:170px;display:flex;align-items:center;justify-content:center;color:var(--subtle);font-size:12px;background:#0c0b0b}
.libinfo{padding:9px 12px 11px}
.libname{font-family:var(--fmono);font-size:11px;color:var(--muted);margin-bottom:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.libm{font-size:12px}
.libm b{color:var(--v4-yellow)}
#crtModal{position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:100;display:none;align-items:center;justify-content:center;padding:24px}
#crtModal.on{display:flex}
.crtbox{position:relative;background:var(--elev);border:1px solid var(--border);border-radius:14px;max-width:560px;width:100%;max-height:88vh;overflow:auto;padding:18px}
.crtbox img{width:100%;border-radius:9px;margin-bottom:12px;background:#0c0b0b}
.crtx{position:absolute;top:10px;right:12px;background:var(--bg);border:1px solid var(--border);color:var(--white);border-radius:7px;width:30px;height:30px;cursor:pointer;z-index:2}
.crtname{font-family:var(--fmono);font-size:12px;color:var(--v4-yellow);margin-bottom:8px;word-break:break-all}
.crtline{font-size:13px;margin-bottom:4px;color:var(--muted)}
.crtline b{color:var(--white)}
.crtcopy{white-space:pre-wrap;background:var(--bg);border-radius:8px;padding:10px;font-size:12.5px;margin-top:6px}
.crtlink{color:var(--white);cursor:pointer;text-decoration:underline dotted rgba(255,255,255,.35)}
.crtlink:hover{color:var(--v4-yellow)}
.stpane{display:none}.stpane.on{display:block}
.st2btn{background:var(--elev);border:1px solid var(--border);color:var(--muted);padding:7px 16px;border-radius:7px;cursor:pointer;font-family:var(--fbody);font-size:13px;font-weight:600}
.st2btn.on{background:var(--v4-red);color:#fff;border-color:var(--v4-red)}
.s2pane{display:none}.s2pane.on{display:block}
.st3btn{background:var(--elev);border:1px solid var(--border);color:var(--muted);padding:7px 16px;border-radius:7px;cursor:pointer;font-family:var(--fbody);font-size:13px;font-weight:600}
.st3btn.on{background:var(--v4-red);color:#fff;border-color:var(--v4-red)}
.s3pane{display:none}.s3pane.on{display:block}
table.dre{min-width:900px}
table.dre td:first-child,table.dre th:first-child{position:sticky;left:0;text-align:left;z-index:2}
table.dre tbody td:first-child{background:var(--elev);font-weight:600;color:var(--muted)}
table.dre thead th:first-child{background:var(--v4-red);z-index:3}
.chartbox{background:var(--elev);border:1px solid var(--border);border-radius:10px;padding:16px 18px}
.chartbox h4{font-size:13px;color:var(--muted);font-weight:600;margin-bottom:12px;font-family:var(--fbody)}
.chartbox canvas{max-height:250px}
.chartbox.lg canvas{max-height:380px}
.grid>*{min-width:0}
/* NÃO estilizar <canvas> diretamente (max-width etc.) — quebra o responsive do
   Chart.js (docs oficiais); sizing vem do container. */
.chwrap{position:relative;height:230px}
.vignote{font-size:11px;color:var(--subtle);font-weight:400;text-transform:none;letter-spacing:0}
.ibar{display:inline-block;height:8px;border-radius:3px;background:var(--v4-red);vertical-align:middle;margin-left:8px}
.spark{display:block;margin-top:10px;width:100%;height:34px}
.qask{color:var(--subtle);font-size:12.5px;font-style:italic;font-family:var(--fbody);font-weight:400;text-transform:none;letter-spacing:0}
.expbtn{display:block;width:100%;text-align:center;background:var(--elev);border:1px solid var(--border);border-top:0;color:var(--muted);padding:8px;cursor:pointer;font-family:var(--fbody);font-size:12px;border-radius:0 0 10px 10px}
.expbtn:hover{color:var(--white);border-color:var(--v4-red)}
.heatc{white-space:nowrap}
.note{background:var(--warn-bg);border-left:3px solid var(--warn);border-radius:6px;padding:8px 12px;font-size:11.5px;color:var(--muted);margin-top:10px}
.note b{color:var(--warn)}
/* tooltip explicativo */
[data-tip]{cursor:help;border-bottom:1px dotted var(--subtle)}
.tipwrap{position:relative}
[data-tip]:hover::after{content:attr(data-tip);position:absolute;left:0;top:125%;z-index:70;
 background:#0a0a0a;border:1px solid var(--v4-red);border-radius:7px;padding:8px 11px;font-size:11px;line-height:1.45;
 color:var(--white);width:230px;white-space:normal;font-weight:400;text-transform:none;letter-spacing:0;
 font-family:var(--fbody);box-shadow:0 10px 26px rgba(0,0,0,.7)}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);color:var(--subtle);font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-family:var(--fmono)}
@media(max-width:1080px){.g4,.kstrip{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:1fr}}
@media(max-width:880px){.layout{flex-direction:column}.sidenav{flex-direction:row;width:auto;overflow-x:auto;position:static;top:auto}.tab{border-left:0;border-bottom:3px solid transparent;border-radius:7px 7px 0 0;white-space:nowrap}.tab.on{border-left:0;border-bottom-color:var(--v4-red)}}
@media(max-width:680px){.g4,.g2,.kstrip{grid-template-columns:1fr}.head h1{font-size:28px}.funrow .fn{width:80px}}
"""

JS = r"""
const P = __PAYLOAD__;
const CC=P.camp.campanhas,CJ=P.camp.conjuntos,CA=P.camp.anuncios;
// resíduo da reconciliação CRM×campanhas (gerador) somado direto no grão
// dia×anúncio → todas as agregações de mídia (drill, canais, séries, veredito)
// saem reconciliadas com o CRM sem código extra.
const RES=(()=>{const m={};((P.resid&&P.resid.rows)||[]).forEach(r=>m[r[0]]=r);return m;})();
const RECON=(P.resid&&P.resid.recon)||null;
const CAMP=P.camp.rows.map((r,i)=>{const x=RES[i]||[0,0,0,0,0];return{data:r[0],canal:r[1],camp:CC[r[2]],conj:CJ[r[3]],anun:CA[r[4]],
  ci:r[2],ji:r[3],ai:r[4],   // índices dos interns — lookup dos atributos (P.dim) na tela Debriefing
  inv:r[5],sal:r[6]+x[1],demo_ag:r[7]+x[2],demo_re:r[8]+x[3],cli:r[9]+x[4],fat:r[10],impr:r[11],clicks:r[12],
  lead:r[13]||0,sqlc:r[14]||0,alc:r[15]||0};});
// atributos parseados da nomenclatura (taxonomia gia-v2) — paralelos aos interns
const DIM=P.dim||null;
const IC=P.leads.icms,RZ=P.leads.reasons;
const QL=P.leads.quals||{},SDRS=P.leads.sdrs||[],STAGES=P.leads.stages||[];
const LEAD=P.leads.rows.map(r=>({canal:r[0],icm:IC[r[1]],create_at:r[2],sal:r[3],sal_at:r[4],
  sql:r[5],sql_at:r[6],mqlform:r[7],sched_at:r[8],show_at:r[9],win:r[10],win_at:r[11],
  lost:r[12],reason:RZ[r[13]],value:r[14],neg:r[15],mens:r[16],impl:r[17],
  qo:(QL.obras||[])[r[18]]||'',qf:(QL.ferramenta||[])[r[19]]||'',qc:(QL.cargo||[])[r[20]]||'',
  qs:(QL.segmento||[])[r[21]]||'',qd:(QL.dor||[])[r[22]]||'',
  sdr:SDRS[r[23]]||'',stage:STAGES[r[24]]||'',lost_at:r[25]||'',sflag:r[26]||0}));
// vendas atribuídas via ad_id (faturamento LIMPO mens+impl no grão de mídia)
const VEND=((P.vendas&&P.vendas.rows)||[]).map(r=>({data:r[0],canal:r[1],camp:CC[r[2]],conj:CJ[r[3]],anun:CA[r[4]],fat2:r[5],mens:r[6]}));
function vendIn(a,b){return VEND.filter(v=>cMatch(v.canal)&&inR(v.data,a,b));}
const TGT_CD=P.alvos.custo_demo,TGT_CAC=P.alvos.cac,M=P.meta;
const TM=P.termos;const TCAMP=TM?TM.campaigns:[],TADG=TM?TM.adgroups:[];
const TERMS=TM?TM.rows.map(r=>({camp:TCAMP[r[0]],adg:TADG[r[1]],kw:r[2],clicks:r[3],impr:r[4],cost:r[5],conv:r[6],top:r[7]||0})):[];
const FIN=P.fin||{},TCVM=P.tcv_default||6;
function tcvOf(l,m){const meses=(FIN[m]&&FIN[m].tcv_meses)||TCVM;return meses*(l.mens||0)+(l.impl||0);} // TCV só no DRE
function fatOf(l){return (l.mens||0)+(l.impl||0);}   // faturamento = 1 mensalidade + implementação (default fora do DRE)
function mensOf(l){return (l.mens||0);}              // mensalidade sozinha (MRR)
function monthsBetween(a,b){return (+b.slice(0,4)-+a.slice(0,4))*12+(+b.slice(5,7)-+a.slice(5,7));}
const fM=v=>v==null?'—':'R$ '+Math.round(v).toLocaleString('pt-BR');
const fI=v=>v==null?'—':Math.round(v).toLocaleString('pt-BR');
const fP=(v,d=0)=>v==null?'—':(v*100).toFixed(d).replace('.',',')+'%';
const fR=v=>v==null?'—':v.toFixed(2).replace('.',',');
const fD=v=>v==null?'—':v.toFixed(1).replace('.',',')+'d';
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const tr=(s,n=58)=>{s=String(s);return s.length<=n?s:s.slice(0,n-1)+'…';};
const pct=(n,d)=>d?n/d:0;
// canais disponíveis (genérico p/ N canais)
const CHCOUNT=(()=>{const m={};CAMP.forEach(c=>m[c.canal]=(m[c.canal]||0)+1);LEAD.forEach(l=>m[l.canal]=(m[l.canal]||0)+1);return m;})();
const CHANNELS=Object.entries(CHCOUNT).filter(([k,v])=>k&&k!=='—'&&v>=5).sort((a,b)=>b[1]-a[1]).map(([k])=>k);
const CHNAME=c=>({meta:'Meta',google:'Google',seo:'SEO',direct:'Direct'}[c]||c.charAt(0).toUpperCase()+c.slice(1));
let SELCH=new Set(CHANNELS);
const allCh=()=>SELCH.size===0||SELCH.size===CHANNELS.length;
const cMatch=c=>allCh()?true:SELCH.has(c);
// helpers de calendário (TZ-safe, p/ o date-range picker)
const DD=s=>{const[y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);};
const SD=dt=>dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0');
const addM=(s,n)=>{const d=DD(s);d.setMonth(d.getMonth()+n);return SD(d);};
const monthEndStr=s=>SD(new Date(+s.slice(0,4),+s.slice(5,7),0));
const MES_PT=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
const fmtRange=(a,b)=>{const da=DD(a),db=DD(b);return da.getTime()===db.getTime()
  ?`${da.getDate()} ${MES_PT[da.getMonth()]} ${da.getFullYear()}`
  :`${da.getDate()} ${MES_PT[da.getMonth()]} – ${db.getDate()} ${MES_PT[db.getMonth()]} ${db.getFullYear()}`;};
const HOJE=P.hoje;
const MINDATA=(()=>{let m=P.hoje;CAMP.forEach(c=>{if(c.data&&c.data<m)m=c.data;});LEAD.forEach(l=>{if(l.create_at&&l.create_at<m)m=l.create_at;});return m;})();
const PRESETS=[
 ['Hoje',()=>[HOJE,HOJE]],
 ['Ontem',()=>[addDays(HOJE,-1),addDays(HOJE,-1)]],
 ['Últimos 7 dias',()=>[addDays(HOJE,-6),HOJE]],
 ['Últimos 30 dias',()=>[addDays(HOJE,-29),HOJE]],
 ['Últimos 90 dias',()=>[addDays(HOJE,-89),HOJE]],
 ['Esta semana',()=>[weekStart(HOJE),HOJE]],
 ['Este mês',()=>[HOJE.slice(0,7)+'-01',HOJE]],
 ['Mês passado',()=>{const p=addM(HOJE.slice(0,7)+'-01',-1);return [p,monthEndStr(p)];}],
 ['Este trimestre',()=>[P.quarter.start,P.quarter.end<HOJE?P.quarter.end:HOJE]],
 ['Trimestre passado',()=>[addM(P.quarter.start,-3),addDays(P.quarter.start,-1)]],
 ['Este ano (YTD)',()=>[P.quarter.ano+'-01-01',HOJE]],
 ['Todo o período',()=>[MINDATA,HOJE]],
];
const PAID_CH=CHANNELS.filter(c=>c==='meta'||c==='google');
let FILT={ini:P.quarter.start,fim:(P.quarter.end<P.hoje?P.quarter.end:P.hoje),preset:'Este trimestre',cmp:'none'};
let DRAFT={...FILT};let calAnchor=FILT.ini.slice(0,7)+'-01';let pickStage=0;
function curRange(){return [FILT.ini,FILT.fim];}
// datas
const ymd=d=>d.toISOString().slice(0,10);
const addDays=(s,n)=>{const d=new Date(s+'T00:00:00');d.setDate(d.getDate()+n);return ymd(d);};
const shiftMonth=(s,n)=>{const d=new Date(s+'T00:00:00');d.setMonth(d.getMonth()+n);return ymd(d);};
const shiftYear=(s,n)=>{const d=new Date(s+'T00:00:00');d.setFullYear(d.getFullYear()+n);return ymd(d);};
const daysLen=(a,b)=>Math.round((new Date(b)-new Date(a))/864e5)+1;
const weekStart=ds=>{const d=new Date(ds+'T00:00:00');const w=(d.getDay()+6)%7;d.setDate(d.getDate()-w);return ymd(d);};
function rangeOf(p){const end=P.hoje;
  if(p==='sem')return[weekStart(end),end];
  if(p==='mes')return[end.slice(0,7)+'-01',end];
  if(p==='7d')return[addDays(end,-6),end];
  if(p==='30d')return[addDays(end,-29),end];
  if(p==='90d')return[addDays(end,-89),end];
  if(p==='q')return[P.quarter.start,P.quarter.end];
  return[P.quarter.ano+'-01-01',end];}
function compRange(a,b,mode){if(mode==='prev'){const nb=addDays(a,-1);return[addDays(nb,-(daysLen(a,b)-1)),nb];}
  if(mode==='month')return[shiftMonth(a,-1),shiftMonth(b,-1)];
  if(mode==='year')return[shiftYear(a,-1),shiftYear(b,-1)];return[null,null];}
const CMPLAB={prev:'período anterior',month:'mês anterior',year:'ano passado'};
const inR=(d,a,b)=>d!==''&&d>=a&&d<=b;
// ---- metas por vigência (padrão monitor-builder v2.1 — Martins) ----
const VIG=P.vigencia||{label:P.quarter.label,start:P.quarter.start,end:P.quarter.end};
const CANAIS_META=P.canais_meta||null; // null = metas valem pra todos os canais
function periodMeta(){return CANAIS_META?(SELCH.size===CANAIS_META.length&&CANAIS_META.every(c=>SELCH.has(c))):allCh();}
// Meta do contrato vale pra VIGÊNCIA. Pro-rata pela interseção do período
// selecionado com a vigência; TAXAS não escalam; sem interseção → null
// (meta some — esconder > mentir).
function metaPeriodo(i,f){const pi=i||FILT.ini,pf=f||FILT.fim;
  const a=pi>VIG.start?pi:VIG.start,b=pf<VIG.end?pf:VIG.end;
  if(a>b)return null;
  const dq=daysLen(VIG.start,VIG.end),dp=daysLen(a,b),fr=dp/dq;
  return{demos_real:M.demos_real_q*fr,demos_agend:M.demos_agend_q*fr,clientes:M.clientes_q*fr,
    valor:M.valor_total_q*fr,budget:M.budget_q*fr,
    sal_sql:M.sal_sql_rate,show:M.show_rate,close:M.close_rate,f:fr,dp,dq};}
// semáforo: métrica de CUSTO usa conta inversa meta/realizado (lição Colina)
function pctMeta(real,meta,custo){if(!meta)return 0;return custo?(real>0?meta/real:0):real/meta;}
function stMeta(real,meta,custo){const p=pctMeta(real,meta,custo);return p>=1?'ok':p>=.85?'warn':'bad';}
// preset que termina em HOJE projeta até o fim NATURAL do recorte (lição Colina)
function natEnd(){if(FILT.preset==='Este trimestre')return P.quarter.end;
  if(FILT.preset==='Este mês')return monthEndStr(FILT.ini);
  if(FILT.preset==='Esta semana')return addDays(weekStart(HOJE),6);
  if(FILT.preset==='Este ano (YTD)')return P.quarter.ano+'-12-31';
  return FILT.fim;}
// pacing: período em andamento (contém hoje) projeta o fim no ritmo atual
function pacing(real,metaOf,fm,custo){const ne=natEnd();if(HOJE<=FILT.ini||HOJE>ne)return '';
  const el=daysLen(FILT.ini,HOJE<FILT.fim?HOJE:FILT.fim),tt=daysLen(FILT.ini,ne);
  if(el>=tt||!real)return '';
  const p=real/el*tt,MT=metaPeriodo(FILT.ini,ne),mv=(MT&&metaOf)?metaOf(MT):null;
  const st=mv?stMeta(p,mv,custo):null;
  return `<div class="proj">ritmo → <b class="${st?'s-'+st:''}">${fm(p)}</b>${mv?` · ${Math.round(pctMeta(p,mv,custo)*100)}% da meta no fim do período`:''}</div>`;}
function median(arr){if(!arr.length)return null;const s=[...arr].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;}
// ---- progressive disclosure: tabelas abrem top-N, botão expande ----
let EXP={};function togExp(id){EXP[id]=!EXP[id];renderAll();}
function expWrap(id,arr,rowFn,head,n=10,cls=''){const open=!!EXP[id];const rows=(open?arr:arr.slice(0,n)).map(rowFn).join('');
  const btn=arr.length>n?`<button class="expbtn" onclick="togExp('${id}')">${open?'▲ mostrar só top '+n:'▼ mostrar todas ('+arr.length+')'}</button>`:'';
  return `<div class="tbl-wrap" style="${btn?'border-radius:10px 10px 0 0':''}"><table${cls?' class="'+cls+'"':''}><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>${btn}`;}
// ---- sparkline: série semanal (últimas 8 semanas, respeita canal) ----
function sparkSeries(valf){const m={};LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{const r=valf(l);if(!r)return;const w=weekStart(r[0]);m[w]=(m[w]||0)+r[1];});
  const ws=[...Array(8)].map((_,i)=>weekStart(addDays(HOJE,-7*(7-i))));return ws.map(w=>+(m[w]||0).toFixed(1));}
// ---- realizado do funil no range (CRM = verdade; respeita canal) ----
function realiz(ra,rb){const L=LEAD.filter(l=>cMatch(l.canal));
  const lead=L.filter(l=>inR(l.create_at,ra,rb)).length;
  const dre=L.filter(l=>inR(l.show_at,ra,rb)).length,dag=L.filter(l=>inR(l.sched_at,ra,rb)).length;
  const wins=L.filter(l=>l.win&&inR(l.win_at,ra,rb));
  const sal=L.filter(l=>l.sal&&inR(l.sal_at||l.create_at,ra,rb)).length;
  const sql=L.filter(l=>l.sql&&inR(l.sql_at||l.create_at,ra,rb)).length;
  return{lead,dre,dag,cli:wins.length,valor:wins.reduce((s,l)=>s+fatOf(l),0),sal,sql};}
// ---- trio Volume · Ritmo · Forecast (padrão Colina) ----
function funVolCard(R){const fimEf=HOJE<FILT.fim?(HOJE>FILT.ini?HOJE:FILT.ini):FILT.fim;
  const el=Math.max(1,daysLen(FILT.ini,fimEf));
  const steps=[['Lead',R.lead],['SAL',R.sal],['SQL',R.sql],['Demo ag.',R.dag],['Demo real.',R.dre],['Cliente',R.cli]];
  const mx=Math.max(1,R.lead);let rows='';
  steps.forEach((s,i)=>{const prev=i?steps[i-1][1]:s[1];const cv=prev?Math.round(s[1]/prev*100):0;
    rows+=`<div class="funrow"><div class="fn" style="width:74px">${s[0]}</div><div class="ft" style="height:24px"><i style="width:${Math.max(2,Math.round(s[1]/mx*100))}%"></i><span class="vlabel" style="height:24px;font-size:14px">${fI(s[1])}</span></div><div class="fr" style="width:44px">${i?cv+'%':'&nbsp;'}</div></div>`;});
  return `<div class="card"><div class="lab" style="margin-bottom:10px">Volume — funil do período</div>${rows}
    <div class="tag" style="margin-top:8px">média/dia: ${fR(R.lead/el)} leads · ${fR(R.sal/el)} SAL · ${fR(R.dre/el)} demos</div></div>`;}
function ritmoCard(ve){const li=(lab,cur,prev)=>{const d=(cur.med!=null&&prev&&prev.med>0)?(()=>{const p=(cur.med-prev.med)/prev.med,up=p>=0;
    return ` <span class="s-${up?'bad':'ok'}" style="font-size:10.5px">${up?'▲':'▼'}${fP(Math.abs(p))}</span>`;})():'';
    return `<div class="qkpi"><div class="tag">${lab}</div><div style="text-align:right"><b style="font-size:16px">${fD(cur.med)}</b>${d} <span class="muted-n" style="font-size:10px">n=${cur.n}</span></div></div>`;};
  return `<div class="card"><div class="lab" style="margin-bottom:6px"><span data-tip="Mediana de dias entre etapas, janela fixa de ${RITMO_D}d vs os ${RITMO_D}d anteriores. Não reage ao filtro de período (recorte curto engana); canal aplica.">Ritmo — medianas ${RITMO_D}d</span></div>
    ${li('Lead → SAL',ve.T.lead_sal,ve.Pv.lead_sal)}${li('SQL → Demo agendada',ve.T.sql_dag,ve.Pv.sql_dag)}${li('Agendada → realizada',ve.T.dag_dre,ve.Pv.dag_dre)}${li('Demo → Cliente',ve.T.dre_cli,ve.Pv.dre_cli)}${li('Lead → Cliente',ve.T.lead_cli,ve.Pv.lead_cli)}</div>`;}
function forecastCard(R){const ne=natEnd();
  const ativo=HOJE>FILT.ini&&HOJE<=ne&&daysLen(FILT.ini,HOJE<FILT.fim?HOJE:FILT.fim)<daysLen(FILT.ini,ne);
  if(!ativo)return `<div class="card"><div class="lab" style="margin-bottom:6px">Forecast do período</div><div class="empty">Período encerrado (ou futuro) — forecast só aparece em período em andamento.</div></div>`;
  const el=daysLen(FILT.ini,HOJE<FILT.fim?HOJE:FILT.fim),tt=daysLen(FILT.ini,ne),f=tt/el;
  const SM=periodMeta(),MT=SM?metaPeriodo(FILT.ini,ne):null;
  const li=(lab,val,mv,fm)=>{const pc=mv?Math.round(pctMeta(val,mv)*100):null;const st=pc==null?'':pc>=100?'ok':pc>=85?'warn':'bad';
    return `<div class="qkpi"><div class="tag">${lab}</div><div style="text-align:right"><b style="font-size:16px">${fm(val)}</b>${pc!=null?` <span class="s-${st}" style="font-size:11px">${pc}% da meta</span>`:''}</div></div>`;};
  return `<div class="card"><div class="lab" style="margin-bottom:6px"><span data-tip="Projeta o FIM NATURAL do recorte filtrado (mês filtrado projeta o mês; trimestre projeta o trimestre; semana, a semana) no ritmo atual, vs meta pro-rata da mesma janela.">Forecast (${el}/${tt}d · até ${ne.slice(8,10)}/${ne.slice(5,7)})</span></div>
    ${li('Demos realizadas',R.dre*f,MT&&MT.demos_real,v=>fI(Math.round(v)))}
    ${li('Demos agendadas',R.dag*f,MT&&MT.demos_agend,v=>fI(Math.round(v)))}
    ${li('Clientes',R.cli*f,MT&&MT.clientes,v=>fI(Math.round(v)))}
    ${li('Valor',R.valor*f,MT&&MT.valor,fM)}</div>`;}
function velocityCard(R,ve){const c=ve.T.lead_cli.med;
  const win=R.sql?R.cli/R.sql:0,ticket=R.cli?R.valor/R.cli:0;
  const v=(c&&R.sql)?R.sql*win*ticket/c:null;
  return `<div class="card accent"><div class="lab"><span data-tip="Sales velocity = SQLs do período × win-rate (cliente÷SQL) × ticket médio ÷ ciclo mediano Lead→Ganho (180d). Momentum do pipeline em R$/dia — nº único board-level.">Sales velocity</span></div>
    <div class="big" style="font-size:28px;margin-top:8px">${v==null?'—':fM(v)+'<span style="font-size:13px;color:var(--subtle)">/dia</span>'}</div>
    <div class="tag" style="margin-top:4px">${fI(R.sql)} SQL · win ${fP(win)} · ticket ${fM(ticket||null)} · ciclo ${fD(c)}</div></div>`;}
// agregações
function campIn(a,b){return CAMP.filter(c=>cMatch(c.canal)&&inR(c.data,a,b));}
function campF(){const[a,b]=curRange();return campIn(a,b);}
function kpis(rows){let o={inv:0,sal:0,demo_ag:0,demo_re:0,cli:0,fat:0};
  rows.forEach(c=>{o.inv+=c.inv;o.sal+=c.sal;o.demo_ag+=c.demo_ag;o.demo_re+=c.demo_re;o.cli+=c.cli;o.fat+=c.fat;});
  o.cp_sal=o.sal?o.inv/o.sal:null;o.custo_demo=o.demo_re?o.inv/o.demo_re:null;
  o.cac=o.cli?o.inv/o.cli:null;o.roas=o.inv?o.fat/o.inv:null;o.ticket=o.cli?o.fat/o.cli:null;return o;}
function funilRange(a,b){const L=LEAD.filter(l=>cMatch(l.canal));
  const lead=L.filter(l=>inR(l.create_at,a,b)).length,sal=L.filter(l=>l.sal&&inR(l.sal_at||l.create_at,a,b)).length,
   sql=L.filter(l=>l.sql&&inR(l.sql_at||l.create_at,a,b)).length,dag=L.filter(l=>inR(l.sched_at,a,b)).length,
   dre=L.filter(l=>inR(l.show_at,a,b)).length,cli=L.filter(l=>l.win&&inR(l.win_at||l.create_at,a,b)).length;
  return[['Lead',lead],['MQL (SAL)',sal],['SQL',sql],['Demo agendada',dag],['Demo realizada',dre],['Cliente',cli]];}
function funil(){const[a,b]=curRange();let prev=null,out=[];
  funilRange(a,b).forEach(([n,v])=>{out.push({n,v,taxa:prev?pct(v,prev):1,top:prev===null});prev=v;});return out;}
function funilComp(){if(FILT.cmp==='none')return null;const[a,b]=curRange();const[ca,cb]=compRange(a,b,FILT.cmp);
  if(!ca)return null;const m={};funilRange(ca,cb).forEach(([n,v])=>m[n]=v);return m;}
// pipeline aberto pelo stage REAL do CRM (stage_pipeline, 100% preenchido) —
// não mais derivado de flags. Ganho/Perdido ficam de fora (não é pipeline).
function pipelineAberto(){const m={};
  LEAD.filter(l=>cMatch(l.canal)&&!l.win&&!l.lost&&l.stage&&l.stage!=='5. GANHO'&&l.stage!=='PERDIDO')
    .forEach(l=>{m[l.stage]=(m[l.stage]||0)+1;});
  const labels=Object.keys(m).sort();
  return{labels,vals:labels.map(o=>m[o])};}
function cohort(){const months={};
  LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(!l.create_at)return;const mm=l.create_at.slice(0,7);
    const c=months[mm]||(months[mm]={m:mm,leads:0,sal:0,sql:0,dag:0,dre:0,cli:0,valor:0,mrr:0,gd:[]});
    c.leads++;if(l.sal)c.sal++;if(l.sql)c.sql++;if(l.sched_at)c.dag++;if(l.show_at)c.dre++;
    if(l.win){c.cli++;c.valor+=fatOf(l);c.mrr+=mensOf(l);if(l.win_at){const d=(new Date(l.win_at)-new Date(l.create_at))/864e5;if(d>=0&&d<500)c.gd.push(d);}}});
  const inv={};CAMP.filter(c=>cMatch(c.canal)).forEach(c=>{const mm=c.data.slice(0,7);inv[mm]=(inv[mm]||0)+c.inv;});
  return Object.values(months).sort((a,b)=>a.m<b.m?1:-1).slice(0,10).map(c=>({...c,inv:inv[c.m]||0,
    p_sal:pct(c.sal,c.leads),p_sql:pct(c.sql,c.leads),p_dag:pct(c.dag,c.leads),p_dre:pct(c.dre,c.leads),p_cli:pct(c.cli,c.leads),
    cac:c.cli?(inv[c.m]||0)/c.cli:null,cpdr:c.dre?(inv[c.m]||0)/c.dre:null,ticket:c.cli?c.valor/c.cli:null,
    tg:median(c.gd)}));}
function cohortTri(metric){const co={};
  LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(!l.create_at)return;const cm=l.create_at.slice(0,7);
    const c=co[cm]||(co[cm]={m:cm,leads:0,wins:[]});c.leads++;
    if(l.win&&l.win_at){const ms=Math.max(0,monthsBetween(cm+'-01',l.win_at.slice(0,7)+'-01'));
      const days=(new Date(l.win_at)-new Date(l.create_at))/864e5;c.wins.push({ms,fat:fatOf(l),mens:mensOf(l),days});}});
  const inv={};CAMP.filter(c=>cMatch(c.canal)).forEach(c=>{const m=c.data.slice(0,7);inv[m]=(inv[m]||0)+c.inv;});
  const nowM=P.hoje.slice(0,7),MAXM=11;
  const rows=Object.values(co).sort((a,b)=>a.m<b.m?1:-1).slice(0,10).map(c=>{const cells=[];
    for(let k=0;k<=MAXM;k++){if(monthsBetween(c.m+'-01',nowM+'-01')<k){cells.push(undefined);continue;}
      const w=c.wins.filter(x=>x.ms<=k),n=w.length;let v=null;
      if(metric==='conv')v=c.leads?n/c.leads:0;
      else if(metric==='cac')v=n?(inv[c.m]||0)/n:null;
      else if(metric==='fat')v=w.reduce((s,x)=>s+x.fat,0);
      else if(metric==='mens')v=w.reduce((s,x)=>s+x.mens,0);
      else{const dd=w.map(x=>x.days).filter(d=>d>=0&&d<400);v=median(dd);}
      cells.push(v);}
    return{m:c.m,leads:c.leads,inv:inv[c.m]||0,cells};});
  return{rows,MAXM};}
function triTable(metric){const{rows,MAXM}=cohortTri(metric);
  const fmt=metric==='conv'?(v=>fP(v,0)):metric==='tempo'?(v=>fD(v)):(v=>fM(v));
  const heat=(metric==='conv'||metric==='fat'||metric==='mens');let mx=0;rows.forEach(r=>r.cells.forEach(v=>{if(v!=null&&v>mx)mx=v;}));
  let head='<th>Safra</th><th>Invest.</th><th>Leads</th>';for(let k=0;k<=MAXM;k++)head+='<th>M'+k+'</th>';
  const body=rows.map(r=>{let t=`<td>${r.m.slice(5,7)}/${r.m.slice(0,4)}</td><td>${fM(r.inv)}</td><td>${fI(r.leads)}</td>`;
    r.cells.forEach(v=>{if(v===undefined)t+='<td class="muted-n">·</td>';else if(v==null)t+='<td class="muted-n">—</td>';
      else{const st=heat&&mx?`background:rgba(47,191,113,${(0.05+Math.min(v/mx,1)*0.55).toFixed(2)})`:'';t+=`<td style="${st}">${fmt(v)}</td>`;}});
    return `<tr>${t}</tr>`;}).join('');
  return `<div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;}
// Velocidade do funil — MEDIANA em janela FIXA 180d vs 180d anteriores (lição
// Colina: mediana em recorte curto engana). Respeita canal, ignora período.
const RITMO_D=180;
function stageTimes(a,b){const L=LEAD.filter(l=>cMatch(l.canal));
  function med(ff,tf){const arr=[];L.forEach(l=>{const t=l[tf];if(!t||!inR(t,a,b))return;const f=l[ff];if(!f)return;
    const d=(new Date(t)-new Date(f))/864e5;if(d>=0&&d<400)arr.push(d);});
    return{med:median(arr),n:arr.length};}
  return{lead_sal:med('create_at','sal_at'),lead_sql:med('create_at','sql_at'),lead_dag:med('create_at','sched_at'),
    lead_dre:med('create_at','show_at'),lead_cli:med('create_at','win_at'),
    sal_sql:med('sal_at','sql_at'),sql_dag:med('sql_at','sched_at'),dag_dre:med('sched_at','show_at'),dre_cli:med('show_at','win_at')};}
function velocidade(){return{T:stageTimes(addDays(HOJE,-(RITMO_D-1)),HOJE),
  Pv:stageTimes(addDays(HOJE,-(2*RITMO_D-1)),addDays(HOJE,-RITMO_D))};}
function qualidade(){const[a,b]=curRange();const L=LEAD.filter(l=>cMatch(l.canal)&&inR(l.create_at,a,b));
  const n=L.length,fm=L.filter(l=>l.mqlform).length;
  return{leads:n,lead_mql:pct(fm,n),lead_sal:pct(L.filter(l=>l.sal).length,n),lead_sql:pct(L.filter(l=>l.sql).length,n),
    form_prec:pct(L.filter(l=>l.mqlform&&l.sal).length,fm)};}
// perdas ancoradas na data da PERDA (lost_at, 48,7% preenchido; fallback create_at)
function perdas(){const[a,b]=curRange();const m={};let t=0;
  LEAD.filter(l=>cMatch(l.canal)&&l.lost&&inR(l.lost_at||l.create_at,a,b)).forEach(l=>{m[l.reason]=(m[l.reason]||0)+1;t++;});
  return{rows:Object.entries(m).sort((x,y)=>y[1]-x[1]).slice(0,8).map(([motivo,v])=>({motivo,v,pct:pct(v,t)})),total:t};}
function canais(){const m={};campF().forEach(c=>{const a=m[c.canal]||(m[c.canal]={canal:c.canal,inv:0,sal:0,demo_ag:0,demo_re:0,cli:0,fat2:0,mens:0});
   a.inv+=c.inv;a.sal+=c.sal;a.demo_ag+=c.demo_ag;a.demo_re+=c.demo_re;a.cli+=c.cli;});
  const[a,b]=curRange();vendIn(a,b).forEach(v=>{const x=m[v.canal];if(x){x.fat2+=v.fat2;x.mens+=v.mens;}});
  return Object.values(m).map(a=>({...a,cp_sal:a.sal?a.inv/a.sal:null,custo_demo:a.demo_re?a.inv/a.demo_re:null,
    cac:a.cli?a.inv/a.cli:null,roas:a.inv?a.fat2/a.inv:null})).sort((x,y)=>y.inv-x.inv);}
function trendMap(keyf){const m={},h=new Date(P.hoje+'T00:00:00');
  CAMP.forEach(c=>{const k=keyf(c);const a=m[k]||(m[k]={ir:0,sr:0,io:0,so:0});
    const age=Math.round((h-new Date(c.data+'T00:00:00'))/864e5);
    if(age<=28){a.ir+=c.inv;a.sr+=c.sal;}else if(age<=56){a.io+=c.inv;a.so+=c.sal;}});return m;}
// cli/dre arredondados: fração de resíduo (<0,5 evento) não conta como evento
// real — senão nenhuma campanha cai em "cortar".
function veredito(a,t){const inv=a.inv,cli=Math.round(a.cli),dre=Math.round(a.demo_re);const cd=dre?inv/dre:null,cac=cli?inv/cli:null;
  const cr=t&&t.sr?t.ir/t.sr:null,co=t&&t.so?t.io/t.so:null,pior=(cr!=null&&co!=null&&cr>co*1.25);
  if(inv<200)return['neutro','volume baixo'];
  if(cli===0&&dre===0&&inv>=800)return['cortar',fM(inv)+' sem demo nem cliente'];
  if(cd!=null&&cd>2*TGT_CD&&dre<=1)return['cortar','custo/demo '+fM(cd)+' (alvo '+fM(TGT_CD)+')'];
  if(cli>0&&cac!=null&&cac<=TGT_CAC&&dre>=2)return['escalar','CAC '+fM(cac)+' ≤ alvo · '+cli+' cliente(s)'];
  if(dre>=3&&cd!=null&&cd<=TGT_CD)return['escalar','custo/demo '+fM(cd)+' ≤ alvo · '+dre+' demos'];
  if(pior)return['investigar','CP-SAL subiu p/ '+fM(cr)+' (era '+fM(co)+')'];
  if(cd!=null&&cd>TGT_CD*1.4)return['reduzir','custo/demo '+fM(cd)+' acima do alvo'];
  return['neutro','dentro da média'];}
// F5.2: seleção por SELECT (campanha -> conjunto) aplicada só no drill
let SELCAMP='',SELCONJ='';
function setSelCamp(v){SELCAMP=v;SELCONJ='';renderAll();}
function setSelConj(v){SELCONJ=v;renderAll();}
function drillF(){return campF().filter(c=>(!SELCAMP||c.camp===SELCAMP)&&(!SELCONJ||c.conj===SELCONJ));}
function drill(keyf){const tm=trendMap(keyf);const m={};
  drillF().forEach(c=>{const k=keyf(c);const a=m[k]||(m[k]={nome:k,canal:c.canal,inv:0,sal:0,demo_ag:0,demo_re:0,cli:0,fat2:0,lead:0,sqlc:0,impr:0,alc:0,cx:new Set()});
   a.inv+=c.inv;a.sal+=c.sal;a.demo_ag+=c.demo_ag;a.demo_re+=c.demo_re;a.cli+=c.cli;
   a.lead+=c.lead;a.sqlc+=c.sqlc;a.impr+=c.impr;a.alc+=c.alc;a.cx.add(c.camp);});
  const[ra,rb]=curRange();vendIn(ra,rb).forEach(v=>{const x=m[keyf(v)];if(x)x.fat2+=v.fat2;});
  return Object.values(m).map(a=>{const[v,mo]=veredito(a,tm[a.nome]);
   return{...a,cp_sal:a.sal?a.inv/a.sal:null,custo_demo:a.demo_re?a.inv/a.demo_re:null,cac:a.cli?a.inv/a.cli:null,
    cpl:a.lead?a.inv/a.lead:null,freq:a.alc?a.impr/a.alc:null,roas:a.inv?a.fat2/a.inv:null,vered:v,motivo:mo};})
   .filter(x=>x.inv>0).sort((x,y)=>y.inv-x.inv);}
// ---- Qualificadores (tela "Quem converte melhor?") ----
// Safra do lead (create_at no período) atravessando o funil, fatiada pelo
// qualificador. Faturamento = só ganhos (fatOf); ciclo = mediana create→win.
let QKEY='qo';
const QDIMS=[['qo','Nº de obras'],['qf','Ferramenta atual'],['qc','Cargo'],['qs','Segmento'],['qd','Dor declarada'],['icm','ICM (produto)']];
function setQ(k){QKEY=k;renderAll();}
function qualAgg(field){const[a,b]=curRange();const m={};
  LEAD.filter(l=>cMatch(l.canal)&&inR(l.create_at,a,b)).forEach(l=>{const v=l[field]||'(não informado)';
    const s=m[v]||(m[v]={k:v,leads:0,sal:0,dre:0,cli:0,valor:0,gd:[]});
    s.leads++;if(l.sal)s.sal++;if(l.show_at)s.dre++;if(l.win){s.cli++;s.valor+=fatOf(l);
      if(l.win_at&&l.create_at){const d=(new Date(l.win_at)-new Date(l.create_at))/864e5;if(d>=0&&d<500)s.gd.push(d);}}});
  return Object.values(m).map(s=>({...s,p_sal:pct(s.sal,s.leads),p_dre:pct(s.dre,s.leads),p_cli:pct(s.cli,s.leads),
    ticket:s.cli?s.valor/s.cli:null,ciclo:median(s.gd)})).sort((x,y)=>y.leads-x.leads);}
function qualEvo(){const cnt={},vals={};
  LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(!l.create_at)return;const m=l.create_at.slice(0,7);const v=l[QKEY]||'(não informado)';
    (cnt[m]=cnt[m]||{})[v]=(cnt[m][v]||0)+1;vals[v]=(vals[v]||0)+1;});
  const ms=Object.keys(cnt).sort().slice(-12);
  const top=Object.entries(vals).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([k])=>k);
  return{labels:ms.map(m=>m.slice(5,7)+'/'+m.slice(2,4)),
    series:top.map(v=>({v,data:ms.map(m=>cnt[m][v]||0)})),
    outros:ms.map(m=>Object.entries(cnt[m]).filter(([k])=>!top.includes(k)).reduce((s,[,n])=>s+n,0))};}
function sdrAgg(){const[a,b]=curRange();const m={};
  LEAD.filter(l=>cMatch(l.canal)&&l.sdr).forEach(l=>{
    const s=m[l.sdr]||(m[l.sdr]={k:l.sdr,sal:0,dag:0,dre:0,cli:0});
    if(l.sal&&inR(l.sal_at||l.create_at,a,b))s.sal++;
    if(inR(l.sched_at,a,b))s.dag++;if(inR(l.show_at,a,b))s.dre++;
    if(l.win&&inR(l.win_at,a,b))s.cli++;});
  return Object.values(m).filter(s=>s.sal+s.dag+s.dre>0).map(s=>({...s,p_ag:pct(s.dag,s.sal),p_show:pct(s.dre,s.dag)})).sort((x,y)=>y.sal-x.sal);}
function rQuals(){const dims=QDIMS.filter(([k])=>k!=='qd'||LEAD.some(l=>l.qd));
  const rows=qualAgg(QKEY);
  const mx={sal:Math.max(...rows.map(r=>r.p_sal),0.001),dre:Math.max(...rows.map(r=>r.p_dre),0.001),cli:Math.max(...rows.map(r=>r.p_cli),0.001)};
  const heat=(v,m)=>`class="heatc" style="background:rgba(47,191,113,${(0.04+Math.min(v/m,1)*0.5).toFixed(2)})"`;
  const body=rows.slice(0,12).map(r=>`<tr><td>${esc(r.k)}</td><td>${fI(r.leads)}</td>
    <td ${heat(r.p_sal,mx.sal)}>${fP(r.p_sal,0)}</td><td ${heat(r.p_dre,mx.dre)}>${fP(r.p_dre,1)}</td><td ${heat(r.p_cli,mx.cli)}>${fP(r.p_cli,1)}</td>
    <td>${fI(r.cli)}</td><td>${fM(r.ticket)}</td><td>${r.ciclo==null?'<span class="muted-n">—</span>':fD(r.ciclo)}</td></tr>`).join('');
  const sd=sdrAgg();
  const sbody=sd.map(s=>`<tr><td>${esc(s.k)}</td><td>${fI(s.sal)}</td><td>${fI(s.dag)}</td><td>${fP(s.p_ag,0)}</td><td>${fI(s.dre)}</td><td>${fP(s.p_show,0)}</td><td>${fI(s.cli)}</td></tr>`).join('');
  return `<h2 class="sec">Qualificadores <span class="qask">— quem converte melhor?</span></h2>
   <div class="sec-desc">Funil por resposta do form (safra do lead no período/canal). Heatmap = conversão relativa ao melhor valor da coluna. Fonte: qualificadores do CRM (~85% preenchidos; urgência/orçamento vêm vazios da origem — ver Atenção).</div>
   <div class="subtabs">${dims.map(([k,l])=>`<button class="stbtn ${QKEY===k?'on':''}" onclick="setQ('${k}')">${l}</button>`).join('')}</div>
   <div class="tbl-wrap"><table><thead><tr><th>${(dims.find(([k])=>k===QKEY)||[,''])[1]}</th><th>Leads</th><th>%SAL</th><th>%Demo real.</th><th>%Cliente</th><th>Clientes</th><th>Ticket</th><th>Ciclo</th></tr></thead><tbody>${body}</tbody></table></div>
   <div class="grid g2" style="margin-top:14px">
     <div class="chartbox lg"><h4>Evolução — leads/mês por ${((dims.find(([k])=>k===QKEY)||[,''])[1]).toLowerCase()}</h4><canvas id="cQualEvo"></canvas></div>
     <div class="chartbox lg"><h4>Conversão Lead→Cliente por valor (período)</h4><canvas id="cQualConv"></canvas></div></div>
   <h2 class="sec">Funil por SDR <span class="tag" style="font-size:11px">(eventos no período · respeita canal)</span></h2>
   <div class="sec-desc">SAL validados, agendamentos e shows por SDR — onde a passagem SAL→agendamento trava, e com quem. Campo <code>sdr</code> preenchido em ~45% dos leads.</div>
   <div class="tbl-wrap"><table style="min-width:auto"><thead><tr><th>SDR</th><th>SAL</th><th>Demo agend.</th><th>SAL→Agend.</th><th>Demo real.</th><th>Show-rate</th><th>Clientes</th></tr></thead><tbody>${sbody}</tbody></table></div>`;}
// séries (respeitam Canal, não Período)
function serieDemosMes(){const m={};LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(l.show_at&&l.show_at.slice(0,4)==String(P.quarter.ano)){const k=l.show_at.slice(0,7);m[k]=(m[k]||0)+1;}});
  const ks=Object.keys(m).sort();return{labels:ks,vals:ks.map(k=>m[k]),meta:M.demos_real_mes};}
function serieVolume(){const lk={},sk={},dk={};LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{
   if(l.create_at)lk[weekStart(l.create_at)]=(lk[weekStart(l.create_at)]||0)+1;
   if(l.sal_at)sk[weekStart(l.sal_at)]=(sk[weekStart(l.sal_at)]||0)+1;
   if(l.show_at)dk[weekStart(l.show_at)]=(dk[weekStart(l.show_at)]||0)+1;});
  const ws=Object.keys(lk).sort().slice(-16);
  return{labels:ws.map(w=>w.slice(8,10)+'/'+w.slice(5,7)),leads:ws.map(w=>lk[w]||0),sal:ws.map(w=>sk[w]||0),demos:ws.map(w=>dk[w]||0)};}
function serieEfic(){const iv={},sl={},dr={};CAMP.filter(c=>cMatch(c.canal)).forEach(c=>{const w=weekStart(c.data);
   iv[w]=(iv[w]||0)+c.inv;sl[w]=(sl[w]||0)+c.sal;dr[w]=(dr[w]||0)+c.demo_re;});
  const ws=Object.keys(iv).sort().slice(-16);
  return{labels:ws.map(w=>w.slice(8,10)+'/'+w.slice(5,7)),custo_demo:ws.map(w=>dr[w]?+(iv[w]/dr[w]).toFixed(2):null),cp_sal:ws.map(w=>sl[w]?+(iv[w]/sl[w]).toFixed(2):null)};}
const VERED={cortar:['bad','✂ Cortar'],escalar:['ok','▲ Escalar'],reduzir:['warn','▼ Reduzir'],investigar:['warn','◉ Investigar'],neutro:['muted','• Manter']};
function paceSt(pp){return pp>=1?'ok':(pp>=.85?'warn':'bad');}
function kpiSt(r,m,hi=true){const x=m?r/m:0;return hi?(r>=m?'ok':(x>=.85?'warn':'bad')):(r<=m?'ok':(x<=1.15?'warn':'bad'));}
function kbox(l,n,x,tip,d,neutral){const dl=d&&d.comp!=null&&d.comp!==0?(()=>{const p=(d.cur-d.comp)/d.comp,up=p>=0;
   const cls=neutral?'muted':(up?'ok':'bad');
   return `<div class="kd s-${cls}">${up?'▲':'▼'} ${fP(Math.abs(p))} <span class="muted-n">vs ${CMPLAB[FILT.cmp]}</span></div>`;})():'';
  const ll=tip?`<span data-tip="${esc(tip)}">${l}</span>`:l;
  return `<div class="kbox"><div class="l">${ll}</div><div class="n">${n}</div><div class="x">${x}</div>${dl}</div>`;}
// TELAS
function rGeral(){const SM=periodMeta(),MTany=metaPeriodo(),MT=(SM&&MTany)?MTany:null;
  const[a,b]=curRange();
  const R=realiz(a,b);let RC=null;
  if(FILT.cmp!=='none'){const[ca,cb]=compRange(a,b,FILT.cmp);if(ca)RC=realiz(ca,cb);}
  const dlv=(cur,cmp)=>(RC&&cmp!=null&&cmp!==0)?(()=>{const p=(cur-cmp)/cmp,up=p>=0;
    return `<span class="s-${up?'ok':'bad'}" style="font-size:13px;font-weight:600"> ${up?'▲':'▼'}${fP(Math.abs(p))}</span>`;})():'';
  // card OKR: nº grande + Δ + bullet bar + pacing + sparkline 8 sem (3 camadas de contexto)
  function okrCard(lab,real,mv,fmt,tip,partial,dl,metaOf,sparkId){const seal=partial?' <span class="pill bg-warn">dado parcial</span>':'';
    const spark=sparkId?`<canvas class="spark" id="${sparkId}" width="200" height="34"></canvas>`:'';
    if(!(mv>0))return `<div class="card okr"><div class="lab"><span data-tip="${esc(tip)}">${lab}</span>${seal}</div>
      <div class="big">${fmt(real)}${dl||''}</div><div class="meta">sem meta neste recorte</div>${spark}</div>`;
    const st=stMeta(real,mv),w=Math.min(100,pctMeta(real,mv)*100);
    return `<div class="card okr"><div class="lab"><span data-tip="${esc(tip)}">${lab}</span>${seal}</div>
      <div class="big s-${st}">${fmt(real)}${dl||''}</div><div class="meta">meta ${fmt(mv)} · ${fP(pctMeta(real,mv))} atingido</div>
      <div class="bar"><i class="fill-${st}" style="width:${w.toFixed(0)}%"></i></div>
      ${metaOf?pacing(real,metaOf,fmt):''}${spark}</div>`;}
  const rate=(n,d)=>d?n/d:null;
  function qk(lab,real,mv,base,tip){const st=(real!=null&&mv!=null)?stMeta(real,mv):'muted';
    return `<div class="qkpi"><div><div class="tag"><span data-tip="${esc(tip)}">${lab}</span></div>
    <div class="v s-${st}">${fP(real,1)}</div></div><div style="text-align:right"><div class="tag">${mv!=null?'meta '+fP(mv,0):'—'}</div><div class="tag">Q1: ${fP(base,1)}</div></div></div>`;}
  const k=kpis(campF());const ks=kpiSet(a,b);let comp=null,ksC=null;
  if(FILT.cmp!=='none'){const[ca,cb]=compRange(a,b,FILT.cmp);if(ca){comp=kpis(campIn(ca,cb));ksC=kpiSet(ca,cb);}}
  const ve=velocidade();
  // card compacto: nº + Δ + alvo com semáforo (custo = conta inversa)
  function mCard(lab,val,sub,tip,cur,cmp,inv,alvo){const st=(alvo!=null&&cur!=null)?stMeta(cur,alvo,inv):null;
    const dl=(cmp!=null&&cmp!==0&&cur!=null)?(()=>{const p=(cur-cmp)/cmp,up=p>=0,good=inv?!up:up;
      return `<div class="kd s-${good?'ok':'bad'}">${up?'▲':'▼'} ${fP(Math.abs(p))} <span class="muted-n">vs ${CMPLAB[FILT.cmp]}</span></div>`;})():'';
    return `<div class="kbox"><div class="l"><span data-tip="${esc(tip)}">${lab}</span></div>
      <div class="n ${st?'s-'+st:''}">${val}</div><div class="x">${sub}${alvo!=null?' · alvo '+fM(alvo):''}</div>${dl}</div>`;}
  const proTag=(MT&&MT.f<0.999)?` <span class="vignote">· metas pro-rata: ${MT.dp} de ${MT.dq} dias do ${VIG.label}</span>`:'';
  const offTag=!MTany?` <span class="vignote">· período fora da vigência das metas (${VIG.label}) — metas ocultas</span>`
    :(!SM?` <span class="vignote">· metas ocultas — valem pro recorte de ${CANAIS_META?'canais de meta':'todos os canais'}</span>`:'');
  return `<h2 class="sec">Placar OKR · vigência ${VIG.label} <span class="qask">— estou no ritmo da meta?</span>${proTag}${offTag}</h2>
   <div class="sec-desc">Realizado no <b>período/canal filtrado</b> (CRM = verdade). Recorte parcial usa <b>meta pro-rata</b>; taxas não escalam; fora da vigência a meta some. Sparkline = últimas 8 semanas.</div>
   <div class="grid g4">
     ${okrCard('Demos realizadas ★',R.dre,MT&&MT.demos_real,v=>fI(Math.round(v)),'Métrica-estrela: reuniões de demonstração realizadas (show_meeting), por lead único.',false,dlv(R.dre,RC&&RC.dre),MT?(t=>t.demos_real):null,'spk-dre')}
     ${okrCard('Demos agendadas',R.dag,MT&&MT.demos_agend,v=>fI(Math.round(v)),'Reuniões agendadas (scheduled_meeting), por lead único.',false,dlv(R.dag,RC&&RC.dag),MT?(t=>t.demos_agend):null,'spk-dag')}
     ${okrCard('Clientes novos',R.cli,MT&&MT.clientes,v=>fI(Math.round(v)),'Negócios ganhos (win) no período filtrado.',false,dlv(R.cli,RC&&RC.cli),MT?(t=>t.clientes):null,'spk-cli')}
     ${okrCard('Valor total',R.valor,MT&&MT.valor,fM,'Faturamento (1 mensalidade + implementação) dos ganhos no período. Campo ainda esparso no CRM → dado parcial.',true,dlv(R.valor,RC&&RC.valor),MT?(t=>t.valor):null,'spk-val')}</div>
   <h2 class="sec">Volume · Ritmo · Forecast</h2>
   <div class="sec-desc">O funil do recorte, a velocidade estrutural e onde o período termina no ritmo atual.</div>
   <div class="grid g3">${funVolCard(R)}${ritmoCard(ve)}${forecastCard(R)}</div>
   <div class="grid g2" style="margin-top:14px">
     <div class="card accent"><div class="lab" style="margin-bottom:6px">Qualidade do funil (período filtrado)</div>
       ${qk('SAL → SQL',rate(R.sql,R.sal),SM?M.sal_sql_rate:null,M.q1.sal_sql,'SQL ÷ SAL — quanto do lead validado pelo SDR vira oportunidade qualificada. Meta de taxa vale em qualquer recorte (não pro-rateia).')}
       ${qk('Show-rate (agend→real)',rate(R.dre,R.dag),SM?M.show_rate:null,M.q1.show,'Demos realizadas ÷ demos agendadas — taxa de comparecimento.')}
       ${qk('Close-rate (real→cliente)',rate(R.cli,R.dre),SM?M.close_rate:null,M.q1.close,'Clientes ÷ demos realizadas — taxa de fechamento.')}
       <div style="margin-top:10px">${velocityCard(R,ve)}</div></div>
     <div class="card"><div class="lab" style="margin-bottom:10px">Demos realizadas por mês vs meta ${M.demos_real_mes}${allCh()?'':' · filtrado'}</div><canvas id="cDemosMes"></canvas></div>
   </div>
   <h2 class="sec">Resultado de mídia <span class="tag" style="font-size:11px;margin-left:6px">(filtro ativo · reconciliado c/ CRM)</span></h2>
   ${(()=>{const vd=vendIn(a,b);const fat2=vd.reduce((s,v)=>s+v.fat2,0),mrr=vd.reduce((s,v)=>s+v.mens,0);
     let fat2C=null,mrrC=null;if(FILT.cmp!=='none'){const[ca,cb]=compRange(a,b,FILT.cmp);
       if(ca){const vc=vendIn(ca,cb);fat2C=vc.reduce((s,v)=>s+v.fat2,0);mrrC=vc.reduce((s,v)=>s+v.mens,0);}}
     return `<div class="kstrip">
     ${mCard('Investimento',fM(k.inv),'mídia no período','Soma do investimento em mídia no período/canal filtrado.',k.inv,comp&&comp.inv,true)}
     ${mCard('Faturamento',fM(fat2),'1 mens + impl · atribuído (ad_id)','Faturamento LIMPO (1 mensalidade + implementação) dos ganhos ligados a anúncio via ad_id, pela data do ganho.',fat2,fat2C,false)}
     ${mCard('MRR novo',fM(mrr),'mensalidades · atribuído (ad_id)','Soma das mensalidades (MRR) dos ganhos atribuídos via ad_id no período.',mrr,mrrC,false)}
     ${mCard('ROAS',fR(k.inv?fat2/k.inv:null),'faturamento÷invest','Faturamento atribuído ÷ investimento de mídia do recorte.',k.inv?fat2/k.inv:null,(comp&&comp.inv&&fat2C!=null)?fat2C/comp.inv:null,false)}</div>`;})()}
   <div class="kstrip" style="margin-top:12px">
     ${mCard('CPL',fM(ks.cpl),'invest÷leads','Custo por lead do período (funil CRM).',ks.cpl,ksC&&ksC.cpl,true)}
     ${mCard('CP-SAL',fM(ks.cpsal),'invest÷MQL operacional','Custo por SAL — o MQL da operação.',ks.cpsal,ksC&&ksC.cpsal,true)}
     ${mCard('Custo/demo',fM(ks.cpdr),'invest÷demos realizadas','Custo por demo realizada.',ks.cpdr,ksC&&ksC.cpdr,true,TGT_CD)}
     ${mCard('CAC',fM(ks.cac),'invest÷clientes','Custo de aquisição por cliente ganho.',ks.cac,ksC&&ksC.cac,true,TGT_CAC)}</div>
   <div class="note">Mídia (este bloco e a aba <b>Mídia</b>) = campanhas via ad_id <b>+ resíduo do CRM distribuído por mês×canal</b> — totais se aproximam do CRM (a verdade das demais abas). Divergência restante vem da origem e aparece na aba <b>Atenção</b>. <b>Valor Total ainda é dado parcial</b> (receita registrada só a partir de 2026).</div>`;}
function rAtencao(){const[a,b]=curRange();
  const L=LEAD.filter(l=>cMatch(l.canal)&&inR(l.create_at,a,b));const n=L.length||1;
  const wins=L.filter(l=>l.win);const nw=wins.length||1;
  const semCanal=L.filter(l=>!l.canal||l.canal==='—').length;
  const semQual=L.filter(l=>!l.qo&&!l.qf&&!l.qc&&!l.qs).length;
  const vSemValor=wins.filter(l=>fatOf(l)<=0).length;
  const sus=L.filter(l=>l.sflag).length;
  const fm=L.filter(l=>l.mqlform).length,fprec=fm?L.filter(l=>l.mqlform&&l.sal).length/fm:null;
  // detector de ganhos em lote: win_at concentrado num único dia = atualização
  // em massa no CRM (distorce série mensal/semanal — ex.: 26 ganhos em 24/06)
  const winD={};LEAD.filter(l=>cMatch(l.canal)&&l.win&&l.win_at&&inR(l.win_at,a,b)).forEach(l=>{winD[l.win_at]=(winD[l.win_at]||0)+1;});
  const wTot=Object.values(winD).reduce((s,x)=>s+x,0);
  const wMax=Object.entries(winD).sort((x,y)=>y[1]-x[1])[0]||null;
  const lote=wMax&&wMax[1]>=5&&wMax[1]/wTot>.3;
  const kb=(l,val,sub,bad,tip)=>`<div class="kbox"><div class="l"><span data-tip="${esc(tip||'')}">${l}</span></div><div class="n ${bad?'s-bad':''}">${val}</div><div class="x">${sub}</div></div>`;
  let h=`<h2 class="sec">Atenção <span class="qask">— o que precisa de ação agora?</span></h2>
   <div class="sec-desc">Qualidade do dado no período/canal filtrado + veredito de mídia. Dado furado aqui = decisão cega nas outras telas.</div>
   <h2 class="sec" style="font-size:16px">Pontos cegos — qualidade do dado</h2>
   <div class="kstrip">
     ${kb('Leads sem canal',fI(semCanal),fP(semCanal/n,0)+' dos leads',semCanal/n>.15,'Lead sem canal identificado não entra em nenhuma análise de mídia.')}
     ${kb('Sem nenhum qualificador',fI(semQual),fP(semQual/n,0)+' (obras+ferramenta+cargo+segmento vazios)',semQual/n>.3,'Lead que não respondeu nenhum dos 4 qualificadores fortes do form.')}
     ${kb('Vendas sem valor',fI(vSemValor),fP(vSemValor/nw,0)+' dos ganhos',vSemValor/nw>.1,'Ganho sem value_mensalidade/implementação — furo no faturamento e no DRE.')}
     ${kb('Canal × clickid divergente',fI(sus),fP(sus/n,1)+' — canal diz uma plataforma, gclid/fbclid diz outra',sus/n>.03,'Detector: lead marcado meta com gclid (ou google com fbclid) — tagueamento errado na origem.')}</div>
   <div class="kstrip" style="margin-top:12px">
     ${kb('Precisão do form (MQL→SAL)',fprec==null?'—':fP(fprec),'dos MQL automáticos, confirmados pelo SDR',fprec!=null&&fprec<.5,'Qualidade da qualificação automática do formulário.')}
     ${kb('Qualificadores 100% vazios','4 campos','urgência · orçamento · interesse · comitê',true,'Campos existem no CRM mas nunca são preenchidos — qualificação cega nesses eixos (BANT incompleto).')}
     ${kb('Ganhos em lote',lote?fI(wMax[1])+' em '+wMax[0].split('-').reverse().join('/'):'—',lote?fP(wMax[1]/wTot,0)+' dos ganhos do período num único dia — atualização em massa no CRM distorce as séries':'sem concentração anômala no período',lote,'win_at concentrado num único dia = fechamentos em lote no CRM (não vendas reais daquele dia). Corrigir hábito na origem; séries mensais/semanais ficam distorcidas.')}</div>`;
  if(RECON){const evl=[['SAL','sal'],['Demo agendada','demo_ag'],['Demo realizada','demo_re'],['Cliente','cli']];
    h+=`<h2 class="sec" style="font-size:16px">Reconciliação campanhas × CRM <span class="tag" style="font-size:11px">(base toda · canais pagos)</span></h2>
    <div class="sec-desc">CRM é a verdade. Faltante (sem match de ad_id) é redistribuído no drill; <b>excedente</b> = supercontagem na planilha de campanhas (linha por placement) — corrigir na origem.</div>
    <div class="kstrip">${evl.map(([lb,k])=>{const r=RECON[k];const exc=r.camp>r.crm;
      return kb(lb,fI(r.crm)+' CRM',exc?('campanhas '+fI(r.camp)+' — EXCEDE em '+fI(r.camp-r.crm)):('campanhas '+fI(r.camp)+' + '+fI(r.alloc)+' redistribuído'),exc,'Totais da base completa por evento: CRM vs planilha de campanhas.');}).join('')}</div>`;}
  const camp=drill(c=>c.camp);
  const cortar=camp.filter(x=>x.vered==='cortar').slice(0,8),escalar=camp.filter(x=>x.vered==='escalar').slice(0,8),
    invs=camp.filter(x=>x.vered==='investigar'||x.vered==='reduzir').slice(0,8),desp=cortar.reduce((s,x)=>s+x.inv,0);
  const col=(t,ic,css,it,vz)=>`<div class="deccol"><h3 class="s-${css}">${ic} ${t}</h3>${it.map(x=>`<div class="decitem ${css}"><div class="nm">${esc(tr(x.nome,52))}</div><div class="mo">${esc(x.motivo)} · <span class="muted-n">${esc(x.canal)}</span></div></div>`).join('')||'<div class="empty">'+vz+'</div>'}</div>`;
  h+=`<h2 class="sec" style="font-size:16px">Veredito de mídia — cortar, escalar, investigar</h2>
   <div class="sec-desc">Por campanha no período/canal filtrado (alvo custo/demo ${fM(TGT_CD)} · alvo CAC ${fM(TGT_CAC)}). Desperdício (cortar): <b class="s-bad">${fM(desp)}</b>.</div>
   <div class="grid g3">${col('Cortar','✂','bad',cortar,'nada gritante')}${col('Escalar','▲','ok',escalar,'sem vencedor claro')}${col('Investigar / Reduzir','◉','warn',invs,'sem alertas')}</div>`;
  return h;}
function rFunil(){const fu=funil(),fmax=Math.max(...fu.map(x=>x.v),1),q=qualidade(),pe=perdas(),ve=velocidade(),cmp=funilComp();
  const fr=fu.map(x=>{const w=Math.max(2,x.v/fmax*100);
    const dl=cmp&&cmp[x.n]?(()=>{const p=(x.v-cmp[x.n])/cmp[x.n],up=p>=0;return ` <span class="s-${up?'ok':'bad'}" style="font-size:10.5px">${up?'▲':'▼'}${fP(Math.abs(p))}</span>`;})():'';
    const taxa=`<span class="fr">${x.top?'':'conv. <b>'+fP(x.taxa)+'</b>'}${dl}</span>`;
    return `<div class="funrow"><div class="fn">${x.n}</div><div class="ft"><i style="width:${w.toFixed(0)}%"></i><span class="vlabel">${fI(x.v)}</span></div>${taxa}</div>`;}).join('');
  const vrow=(lab,cur,prev)=>{const d=(cur.med!=null&&prev&&prev.med>0)?(()=>{const p=(cur.med-prev.med)/prev.med,up=p>=0;
    return ` <span class="s-${up?'bad':'ok'}" style="font-size:10.5px">${up?'▲':'▼'}${fP(Math.abs(p))}</span>`;})():'';
    return `<tr><td>${lab}</td><td>${fD(cur.med)}${d}</td><td>${cur.n?fI(cur.n):'<span class="muted-n">—</span>'}</td></tr>`;};
  const pr=pe.rows.map(r=>`<tr><td title="${esc(r.motivo)}">${esc(tr(r.motivo,46))}</td><td>${fI(r.v)}</td><td>${fP(r.pct,0)}</td></tr>`).join('');
  return `<h2 class="sec">Funil de conversão <span class="qask">— onde o funil trava?</span></h2>
   <div class="sec-desc">Lead → MQL(SAL) → SQL → Demo agendada → Demo realizada → Cliente · por lead único no período/canal. Conversão = etapa ÷ etapa anterior na janela; em períodos curtos pode passar de 100% (o evento cai na janela mas o lead nasceu antes).</div>
   <div class="card">${fr}</div>
   <h2 class="sec">Pipeline em aberto por etapa <span class="tag" style="font-size:11px;margin-left:6px">(snapshot atual · stage real do CRM · respeita canal)</span></h2>
   <div class="sec-desc">Negócios abertos hoje (nem ganhos nem perdidos), na etapa atual do <code>stage_pipeline</code>. Mostra onde o pipeline está represado.</div>
   <div class="card"><div class="chwrap"><canvas id="cPipe"></canvas></div></div>
   <div class="chartbox" style="margin-top:14px"><h4>Leads por semana, por status (Aberto / Perdido / Ganho)</h4><canvas id="cLeadsStatus"></canvas></div>
   <h2 class="sec">Velocidade do funil <span class="tag" style="font-size:11px">(mediana · últimos ${RITMO_D}d vs ${RITMO_D}d anteriores · respeita canal, ignora período)</span></h2>
   <div class="sec-desc">Mediana de dias entre etapas em <b>janela fixa de ${RITMO_D} dias</b> (recorte curto engana). ▲ = ficou mais lento vs janela anterior. Etapas de meio de funil têm menos datas na origem → amostra (n) menor.</div>
   <div class="grid g2">
     <div class="card"><div class="lab" style="margin-bottom:8px">Do Lead até cada etapa</div>
       <div class="tbl-wrap" style="border:0"><table style="min-width:auto"><thead><tr><th>Transição</th><th>Dias (mediana)</th><th>n</th></tr></thead><tbody>
       ${vrow('Lead → MQL (SAL)',ve.T.lead_sal,ve.Pv.lead_sal)}${vrow('Lead → SQL',ve.T.lead_sql,ve.Pv.lead_sql)}${vrow('Lead → Demo agendada',ve.T.lead_dag,ve.Pv.lead_dag)}${vrow('Lead → Demo realizada',ve.T.lead_dre,ve.Pv.lead_dre)}${vrow('Lead → Cliente',ve.T.lead_cli,ve.Pv.lead_cli)}</tbody></table></div></div>
     <div class="card"><div class="lab" style="margin-bottom:8px">Etapa a etapa</div>
       <div class="tbl-wrap" style="border:0"><table style="min-width:auto"><thead><tr><th>Transição</th><th>Dias (mediana)</th><th>n</th></tr></thead><tbody>
       ${vrow('SAL → SQL',ve.T.sal_sql,ve.Pv.sal_sql)}${vrow('SQL → Demo agendada',ve.T.sql_dag,ve.Pv.sql_dag)}${vrow('Demo agend. → realizada',ve.T.dag_dre,ve.Pv.dag_dre)}${vrow('Demo realizada → Cliente',ve.T.dre_cli,ve.Pv.dre_cli)}</tbody></table></div></div></div>
   <h2 class="sec">Motivos de perda <span class="tag" style="font-size:11px">(${fI(pe.total)} · ancorado na data da perda)</span></h2>
   <div class="tbl-wrap"><table style="min-width:auto"><thead><tr><th>Motivo</th><th>Qtd</th><th>%</th></tr></thead><tbody>${pr}</tbody></table></div>`;}
function rMidia(){const cn=canais();const tinv=cn.reduce((s,c)=>s+c.inv,0)||1;
  const cr=cn.map(c=>`<tr><td>${esc(CHNAME(c.canal))}</td><td>${fM(c.inv)}<i class="ibar" style="width:${Math.max(2,c.inv/tinv*70).toFixed(0)}px"></i></td><td>${fP(c.inv/tinv,0)}</td><td>${fI(c.sal)}</td><td>${fM(c.cp_sal)}</td><td>${fI(c.demo_re)}</td><td>${fM(c.custo_demo)}</td><td>${fI(c.cli)}</td><td>${fM(c.cac)}</td><td>${fM(c.fat2)}</td><td>${fM(c.mens)}</td><td>${fR(c.roas)}</td></tr>`).join('');
  const dtbl=(rows,nc,eid,click)=>expWrap(eid,rows,
    x=>{const[cs,lb]=VERED[x.vered];const cxs=x.cx?[...x.cx].filter(c=>c!==x.nome):[];
      const ai=click?ANIDX[x.nome]:null;
      const nomeCell=ai!=null?`<a class="crtlink" onclick="showCrt(${ai})">${esc(tr(x.nome))}</a>`:esc(tr(x.nome));
      return `<tr><td title="${esc(x.nome)}${cxs.length?' · campanha(s): '+esc(cxs.join(' | ')):''}">${nomeCell}${cxs.length?`<span class="hidectx">${esc(cxs.join(' '))}</span>`:''}</td><td>${fM(x.inv)}</td><td>${fI(x.lead)}</td><td>${fM(x.cpl)}</td><td>${fI(x.sal)}</td><td>${fM(x.cp_sal)}</td><td>${fI(x.demo_re)}</td><td>${fM(x.custo_demo)}</td><td>${fI(x.cli)}</td><td>${fM(x.cac)}</td><td>${x.fat2?fM(x.fat2):'—'}</td><td>${x.roas?fR(x.roas):'—'}</td><td>${x.freq?fR(x.freq):'—'}</td><td><span class="bdg bg-${cs}">${lb}</span></td></tr>`;},
    `<th>${nc}</th><th>Invest.</th><th>Lead</th><th>CPL</th><th>SAL</th><th>CP-SAL</th><th>Demo real.</th><th>Custo/demo</th><th>Clientes</th><th>CAC</th><th title="1 mensalidade + implementação dos ganhos atribuídos via ad_id">Fat.*</th><th>ROAS</th><th title="Frequência aprox. = impressões ÷ alcance somado por dia — proxy de fadiga de criativo">Freq*</th><th>Ação</th>`);
  return `<h2 class="sec">Performance por canal <span class="qask">— onde o dinheiro trabalha?</span></h2>
   <div class="tbl-wrap"><table><thead><tr><th>Canal</th><th>Invest.</th><th>Share</th><th>SAL</th><th>CP-SAL</th><th>Demo real.</th><th>Custo/demo</th><th>Clientes</th><th>CAC</th><th title="1 mensalidade + implementação dos ganhos atribuídos via ad_id (data do ganho)">Fat.*</th><th title="Mensalidades (MRR) dos ganhos atribuídos">MRR*</th><th>ROAS</th></tr></thead><tbody>${cr}</tbody></table></div>
   <h2 class="sec">Volume &amp; velocidade <span class="tag" style="font-size:11px">(série · respeita canal)</span></h2>
   <div class="grid g2"><div class="chartbox lg"><h4>Leads, SAL e demos realizadas por semana</h4><canvas id="cVolume"></canvas></div>
     <div class="chartbox lg"><h4>Eficiência por semana — custo/demo &amp; CP-SAL</h4><canvas id="cEfic"></canvas></div></div>
   <div class="grid g3" style="margin-top:14px">
     <div class="chartbox"><h4>CP-SAL por semana por canal</h4><canvas id="cCpsalCanal"></canvas></div>
     <div class="chartbox"><h4>Custo/demo agendada por semana por canal</h4><canvas id="cCpdaCanal"></canvas></div>
     <div class="chartbox"><h4>Custo/demo realizada por semana por canal</h4><canvas id="cCpdrCanal"></canvas></div></div>
   <h2 class="sec">Campanhas · Conjuntos · Anúncios</h2>
   <div class="sec-desc">Drill com veredito acionável no período/canal filtrado. <b>Selecione a campanha</b> (e o conjunto) nos seletores — as tabelas mostram só os filhos. Cabeçalhos ordenam; o campo de texto busca nas linhas exibidas. Clicar no <b>nome do anúncio</b> abre o criativo (preview + copy).</div>
   ${(()=>{const camps=[...new Set(campF().map(c=>c.camp))].sort();
     const conjs=SELCAMP?[...new Set(campF().filter(c=>c.camp===SELCAMP).map(c=>c.conj))].sort():[];
     return `<div style="display:flex;gap:10px;margin:2px 0 10px;flex-wrap:wrap">
      <select class="dbxsel" style="max-width:420px" onchange="setSelCamp(this.value)"><option value="">Todas as campanhas (${camps.length})</option>${camps.map(c=>`<option value="${esc(c)}" ${SELCAMP===c?'selected':''}>${esc(tr(c,64))}</option>`).join('')}</select>
      ${SELCAMP?`<select class="dbxsel" style="max-width:380px" onchange="setSelConj(this.value)"><option value="">Todos os conjuntos (${conjs.length})</option>${conjs.map(c=>`<option value="${esc(c)}" ${SELCONJ===c?'selected':''}>${esc(tr(c,58))}</option>`).join('')}</select>`:''}
      <input class="tfilter" style="margin:0;flex:1;min-width:200px" placeholder="🔎 buscar texto…" oninput="tfilt(this)"></div>`;})()}
   <div class="subtabs"><button class="stbtn on" data-st="camp">Campanhas</button><button class="stbtn" data-st="conj">Conjuntos</button><button class="stbtn" data-st="anun">Anúncios</button></div>
   <div class="stpane on" id="sp-camp">${dtbl(drill(c=>c.camp),'Campanha','xp-camp')}</div>
   <div class="stpane" id="sp-conj">${dtbl(drill(c=>c.conj),'Conjunto','xp-conj')}</div>
   <div class="stpane" id="sp-anun">${dtbl(drill(c=>c.anun),'Anúncio','xp-anun',true)}</div>
   ${TERMS.length?`<h2 class="sec">Termos de busca (Google Search) <span class="tag" style="font-size:11px">(snapshot · independe dos filtros)</span></h2>
   <div class="sec-desc">Performance por termo de busca. Conv = MQL (atribuição Google). Desperdício (custo com 0 MQL → candidatos a negativa): <b class="s-bad">${fM(TERMS.filter(t=>t.conv<1).reduce((s,t)=>s+t.cost,0))}</b>. Análise profunda (clusters intenção×ICP, negativas estruturadas) = skill <code>darwin</code>.</div>
   <div class="subtabs"><button class="st3btn on" data-s3="kw">Termos</button><button class="st3btn" data-s3="adg">Grupos</button><button class="st3btn" data-s3="camp">Campanhas</button></div>
   <div class="s3pane on" id="s3-kw">${termosTable('kw')}</div>
   <div class="s3pane" id="s3-adg">${termosTable('adg')}</div>
   <div class="s3pane" id="s3-camp">${termosTable('camp')}</div>`:''}`;}
function rSafra(){const co=cohort();const heat=p=>`background:rgba(47,191,113,${(0.05+Math.min(p,1)*0.55).toFixed(2)})`;
  const rows=co.map(c=>`<tr><td>${c.m.slice(5,7)}/${c.m.slice(0,4)}</td><td>${fI(c.leads)}</td>
    <td style="${heat(c.p_sal)}">${fP(c.p_sal,0)}</td><td style="${heat(c.p_sql)}">${fP(c.p_sql,0)}</td>
    <td style="${heat(c.p_dag)}">${fP(c.p_dag,0)}</td><td style="${heat(c.p_dre)}">${fP(c.p_dre,0)}</td>
    <td style="${heat(c.p_cli)}">${fP(c.p_cli,1)}</td><td>${fM(c.cac)}</td><td>${fM(c.cpdr)}</td>
    <td>${fM(c.valor)}</td><td>${fM(c.mrr)}</td><td>${fM(c.ticket)}</td><td>${c.tg==null?'<span class="muted-n">—</span>':fD(c.tg)}</td></tr>`).join('');
  return `<h2 class="sec">Safra — triângulo de maturação <span class="qask">— as coortes maturam?</span></h2>
   <div class="sec-desc">Linha = safra (mês de entrada do lead). Colunas <b>M0,M1,M2…</b> = meses desde a entrada; célula = métrica acumulada até aquela maturidade. Safra recente só tem M0 preenchido; <b class="muted-n">·</b> = mês ainda não decorrido. Métrica trocável abaixo. Respeita canal.</div>
   <div class="subtabs"><button class="st2btn on" data-s2="conv">Conversão→Deal</button><button class="st2btn" data-s2="cac">CAC</button><button class="st2btn" data-s2="fat">Faturamento</button><button class="st2btn" data-s2="mens">Mensalidade</button><button class="st2btn" data-s2="tempo">Tempo→Ganho</button></div>
   <div class="s2pane on" id="s2-conv">${triTable('conv')}</div>
   <div class="s2pane" id="s2-cac">${triTable('cac')}</div>
   <div class="s2pane" id="s2-fat">${triTable('fat')}</div>
   <div class="s2pane" id="s2-mens">${triTable('mens')}</div>
   <div class="s2pane" id="s2-tempo">${triTable('tempo')}</div>
   <h2 class="sec">Resumo por safra</h2>
   <div class="sec-desc">Conversão por etapa (heatmap) + CAC/CPDR + <b>Faturamento (1 mensalidade + implementação)</b> + <b>Mensalidade (MRR)</b> + Ticket + tempo Lead→Ganho. TCV (${TCVM}×) só no DRE. Respeita canal.</div>
   <div class="tbl-wrap"><table><thead><tr><th>Safra</th><th>Leads</th>
     <th><span data-tip="% da safra que o SDR validou como SAL (MQL operacional).">%SAL</span></th>
     <th><span data-tip="% da safra que chegou a SQL.">%SQL</span></th>
     <th>%D.agend</th><th>%D.real</th>
     <th><span data-tip="% da safra que virou cliente (ganho).">%Cliente</span></th>
     <th><span data-tip="Mídia investida no mês da safra ÷ clientes dessa safra.">CAC</span></th>
     <th><span data-tip="Mídia investida no mês ÷ demos realizadas da safra.">CPDR</span></th>
     <th><span data-tip="1 mensalidade + implementação dos ganhos da safra.">Faturamento</span></th>
     <th><span data-tip="Soma das mensalidades (MRR) dos ganhos da safra.">Mensalidade</span></th><th>Ticket</th>
     <th><span data-tip="Dias médios da entrada do lead até o ganho, para clientes dessa safra.">Lead→Ganho</span></th></tr></thead><tbody>${rows}</tbody></table></div>
   <div class="note"><b>Leitura:</b> safra recente com %Cliente baixo pode ainda maturar (Lead→Ganho roda ~46 dias). %SAL/%SQL altos com %Cliente baixo = gargalo no fechamento, não no topo.</div>`;}
function termosAgg(level){const key=level==='kw'?(t=>t.kw):level==='adg'?(t=>t.adg):(t=>t.camp);
  const m={};TERMS.forEach(t=>{const k=key(t);const a=m[k]||(m[k]={nome:k,cost:0,clicks:0,impr:0,conv:0,topw:0});a.cost+=t.cost;a.clicks+=t.clicks;a.impr+=t.impr;a.conv+=t.conv;a.topw+=(t.top||0)*t.impr;});
  const tot=TERMS.reduce((s,t)=>s+t.cost,0),totc=TERMS.reduce((s,t)=>s+t.conv,0),bl=totc?tot/totc:0;
  return Object.values(m).map(a=>{const cp=a.conv>=1?a.cost/a.conv:null;let v,mo;
    if(a.cost<50){v='neutro';mo='volume baixo';}
    else if(a.conv<1&&a.cost>=200){v='cortar';mo=fM(a.cost)+' sem MQL → negativar';}
    else if(a.conv>=1&&cp<=bl){v='escalar';mo='CP-MQL '+fM(cp)+' ≤ média';}
    else if(a.conv>=1&&cp>bl*1.5){v='reduzir';mo='CP-MQL '+fM(cp)+' alto';}
    else{v='neutro';mo='na média';}
    return{...a,ctr:(a.impr&&a.clicks<=a.impr)?a.clicks/a.impr:null,top:a.impr?a.topw/a.impr/100:null,cpmql:cp,vered:v,motivo:mo};}).sort((x,y)=>y.cost-x.cost);}
function termosTable(level){const rows=termosAgg(level),lab=level==='kw'?'Termo':level==='adg'?'Grupo de anúncio':'Campanha';
  return expWrap('xp-t'+level,rows,
    x=>{const[cs,lb]=VERED[x.vered];
      return `<tr><td title="${esc(x.nome)}">${esc(tr(x.nome,52))}</td><td>${fM(x.cost)}</td><td>${fI(x.clicks)}</td><td>${fP(x.ctr,2)}</td><td>${fR(x.conv)}</td><td>${fM(x.cpmql)}</td><td>${x.top!=null?fP(x.top,0):'—'}</td><td><span class="bdg bg-${cs}">${lb}</span></td></tr>`;},
    `<th>${lab}</th><th>Custo</th><th>Cliques</th><th>CTR</th><th>Conv (MQL)</th><th>CP-MQL</th><th title="Impression share no topo da página (média ponderada por impressões) — % alto com CP-MQL bom = pouco headroom; % baixo em termo campeão = espaço pra escalar">Impr. topo</th><th>Ação</th>`);}
function dlt(cur,comp,goodUp){if(comp==null||comp===0||cur==null)return '';const p=(cur-comp)/comp,up=p>=0,good=goodUp?up:!up;
  return `<div class="kd s-${good?'ok':'bad'}">${up?'▲':'▼'} ${fP(Math.abs(p))} <span class="muted-n">vs ${CMPLAB[FILT.cmp]}</span></div>`;}
function kpiSet(a,b){const camp=CAMP.filter(c=>cMatch(c.canal)&&inR(c.data,a,b));
  let inv=0,impr=0,clk=0;camp.forEach(c=>{inv+=c.inv;impr+=c.impr;clk+=c.clicks;});
  const L=LEAD.filter(l=>cMatch(l.canal));
  const lead=L.filter(l=>inR(l.create_at,a,b)).length,sal=L.filter(l=>l.sal&&inR(l.sal_at||l.create_at,a,b)).length,
    rm=L.filter(l=>inR(l.sched_at,a,b)).length,rr=L.filter(l=>inR(l.show_at,a,b)).length,
    wins=L.filter(l=>l.win&&inR(l.win_at,a,b)),deal=wins.length;
  const fat=wins.reduce((s,l)=>s+fatOf(l),0),mens=wins.reduce((s,l)=>s+mensOf(l),0);
  return{inv,impr,clk,lead,sal,rm,rr,deal,fat,mens,roas:inv?fat/inv:null,cac:deal?inv/deal:null,
    // guard métrica impossível (cliques>impressões na origem → "—", lição Colina)
    ctr:(impr&&clk<=impr)?clk/impr:null,cliquelead:clk?lead/clk:null,leadmql:lead?sal/lead:null,mqlrm:sal?rm/sal:null,
    rmrr:rm?rr/rm:null,rrdeal:rr?deal/rr:null,cpm:impr?inv/impr*1000:null,cpc:clk?inv/clk:null,
    cpl:lead?inv/lead:null,cpsal:sal?inv/sal:null,cpda:rm?inv/rm:null,cpdr:rr?inv/rr:null};}
function serieInvRec(){const iv={},rc={};
  CAMP.filter(c=>cMatch(c.canal)).forEach(c=>{const w=weekStart(c.data);iv[w]=(iv[w]||0)+c.inv;});
  LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(l.win&&l.win_at){const w=weekStart(l.win_at);rc[w]=(rc[w]||0)+fatOf(l);}});
  const ws=Object.keys(iv).sort().slice(-16);
  return{labels:ws.map(w=>w.slice(8,10)+'/'+w.slice(5,7)),inv:ws.map(w=>iv[w]||0),rec:ws.map(w=>rc[w]||0),roas:ws.map(w=>iv[w]?+((rc[w]||0)/iv[w]).toFixed(2):null)};}
function serieLeadsStatus(){const ab={},pe={},ga={};LEAD.filter(l=>cMatch(l.canal)).forEach(l=>{if(!l.create_at)return;const w=weekStart(l.create_at);
  if(l.win)ga[w]=(ga[w]||0)+1;else if(l.lost)pe[w]=(pe[w]||0)+1;else ab[w]=(ab[w]||0)+1;});
  const ws=Object.keys(Object.assign({},ab,pe,ga)).sort().slice(-16);
  return{labels:ws.map(w=>w.slice(8,10)+'/'+w.slice(5,7)),ab:ws.map(w=>ab[w]||0),pe:ws.map(w=>pe[w]||0),ga:ws.map(w=>ga[w]||0)};}
// custo por evento, por semana, por canal (small multiples: 1 métrica/escala por chart)
function serieCustoCanal(ev){const chs=allCh()?CHANNELS.filter(c=>c==='meta'||c==='google'):[...SELCH];
  const byc={};CAMP.forEach(c=>{if(chs.indexOf(c.canal)<0)return;const w=weekStart(c.data);(byc[c.canal]=byc[c.canal]||{});byc[c.canal][w]=byc[c.canal][w]||{inv:0,n:0};byc[c.canal][w].inv+=c.inv;byc[c.canal][w].n+=c[ev];});
  const allw=new Set();Object.values(byc).forEach(o=>Object.keys(o).forEach(w=>allw.add(w)));const ws=[...allw].sort().slice(-16);
  return{labels:ws.map(w=>w.slice(8,10)+'/'+w.slice(5,7)),series:chs.map(c=>({canal:c,data:ws.map(w=>byc[c]&&byc[c][w]&&byc[c][w].n?+(byc[c][w].inv/byc[c][w].n).toFixed(2):null)}))};}
// fechamentos (projeto inteiro — ignora filtros)
function fechadosMes(){const m={};LEAD.forEach(l=>{if(l.win&&l.win_at){const k=l.win_at.slice(0,7);m[k]=(m[k]||0)+1;}});
  const ks=Object.keys(m).sort().slice(-18);return{labels:ks.map(k=>k.slice(5,7)+'/'+k.slice(2,4)),vals:ks.map(k=>m[k])};}
function fechadosAno(){const m={};LEAD.forEach(l=>{if(l.win&&l.win_at){const k=l.win_at.slice(0,4);m[k]=(m[k]||0)+1;}});
  const ks=Object.keys(m).sort();return{labels:ks,vals:ks.map(k=>m[k])};}
// DRE mensal (projeto inteiro, todos os canais — ignora filtros Período/Canal)
function dreData(){const months=Object.keys(FIN).sort();
  const inv={},impr={},clk={};CAMP.forEach(c=>{const m=c.data.slice(0,7);inv[m]=(inv[m]||0)+c.inv;impr[m]=(impr[m]||0)+c.impr;clk[m]=(clk[m]||0)+c.clicks;});
  const leads={},sal={},rm={},rr={},deals={},tcv={};
  LEAD.forEach(l=>{if(l.create_at){const m=l.create_at.slice(0,7);leads[m]=(leads[m]||0)+1;if(l.sal){const sm=(l.sal_at||l.create_at).slice(0,7);sal[sm]=(sal[sm]||0)+1;}}
    if(l.sched_at){const m=l.sched_at.slice(0,7);rm[m]=(rm[m]||0)+1;}
    if(l.show_at){const m=l.show_at.slice(0,7);rr[m]=(rr[m]||0)+1;}
    if(l.win&&l.win_at){const m=l.win_at.slice(0,7);deals[m]=(deals[m]||0)+1;tcv[m]=(tcv[m]||0)+tcvOf(l,m);}});
  let acc=0;const rows=months.map(m=>{const cfg=FIN[m]||{};const im=inv[m]||0,fee=cfg.fee||0,it=im+fee;
    const tc=tcv[m]||0,mg=cfg.margem||0,mc=tc*mg+(cfg.outras_receitas||0);
    const lucro=mc-it-(cfg.outros_custos||0);acc+=lucro;const d=deals[m]||0;
    return{m,inv:im,fee,it,impr:impr[m]||0,clk:clk[m]||0,leads:leads[m]||0,sal:sal[m]||0,rm:rm[m]||0,rr:rr[m]||0,
      deals:d,tcv:tc,ticket:d?tc/d:null,roas:im?tc/im:null,cac:d?it/d:null,mc,lucro,acc,bev:lucro>=0,pago:acc>=0,norev:(tc===0&&d>0)};});
  return{months,rows,hasImpr:Object.values(impr).some(v=>v>0)};}
function rMensal(){const D=dreData(),ms=D.rows;
  const head='<th>Métrica</th>'+ms.map(r=>`<th>${r.m.slice(5,7)}/${r.m.slice(2,4)}</th>`).join('');
  const line=(lab,fn,cls)=>`<tr><td>${lab}</td>${ms.map(r=>`<td class="${cls?cls(r):''}">${fn(r)}</td>`).join('')}</tr>`;
  let b='';
  b+=line('Investimento (mídia)',r=>fM(r.inv));b+=line('FEE',r=>fM(r.fee));b+=line('Investimento Total',r=>fM(r.it));
  if(D.hasImpr){b+=line('Impressões',r=>fI(r.impr));b+=line('Cliques',r=>fI(r.clk));b+=line('CPM',r=>r.impr?fM(r.inv/r.impr*1000):'—');b+=line('CTR',r=>(r.impr&&r.clk<=r.impr)?fP(r.clk/r.impr,2):'—');}
  b+=line('Leads',r=>fI(r.leads));b+=line('SAL (MQL)',r=>fI(r.sal));b+=line('RM (demo agend.)',r=>fI(r.rm));b+=line('RR (demo real.)',r=>fI(r.rr));
  b+=line('CPL',r=>r.leads?fM(r.inv/r.leads):'—');b+=line('CP-SAL',r=>r.sal?fM(r.inv/r.sal):'—');
  b+=line('Custo/demo agend.',r=>r.rm?fM(r.inv/r.rm):'—');b+=line('Custo/demo real.',r=>r.rr?fM(r.inv/r.rr):'—');
  const inVig=m=>m>=VIG.start.slice(0,7)&&m<=VIG.end.slice(0,7);
  b+=line(`Meta demos real. (${fI(M.demos_real_mes)}/mês)`,r=>inVig(r.m)?`<span class="s-${stMeta(r.rr,M.demos_real_mes)}">${Math.round(r.rr/M.demos_real_mes*100)}%</span>`:'<span class="muted-n">—</span>');
  b+=line('Deals',r=>fI(r.deals));
  b+=line('TCV',r=>fM(r.tcv));b+=line('Ticket (TCV)',r=>fM(r.ticket));b+=line('ROAS',r=>fR(r.roas));b+=line('CAC (c/ FEE)',r=>fM(r.cac));
  b+=line('Margem Contribuição',r=>fM(r.mc));
  b+=line('Lucro Competência',r=>fM(r.lucro),r=>r.lucro>=0?'s-ok':'s-bad');
  b+=line('Status Competência',r=>r.norev?'<span class="muted-n">s/ receita</span>':(r.bev?'✓ Breakeven':'Faltou '+fM(-r.lucro)),r=>r.norev?'':(r.bev?'s-ok':'s-bad'));
  b+=line('Resultado Acumulado',r=>fM(r.acc),r=>r.acc>=0?'s-ok':'s-bad');
  b+=line('Status Payback',r=>r.pago?'✓ Pago':'Falta '+fM(-r.acc),r=>r.pago?'s-ok':'s-bad');
  return `<h2 class="sec">Resultados — fechamentos <span class="qask">— o projeto se paga?</span></h2>
   <div class="grid g2"><div class="chartbox"><h4>Fechados por mês</h4><canvas id="cFechMes"></canvas></div>
     <div class="chartbox"><h4>Fechados por ano</h4><canvas id="cFechAno"></canvas></div></div>
   <h2 class="sec">DRE mensal — competência &amp; payback</h2>
   <div class="sec-desc"><b>Projeto inteiro, todos os canais</b> (não reage aos filtros). <b>⚠️ Âncora: MÊS DO EVENTO (calendário)</b> — lead conta no mês em que foi criado, SAL/demos no mês em que aconteceram, deal no mês do ganho. <b>NÃO é visão safra</b> (essa vive na aba Safra): os leads de um mês não são os que geraram as demos daquele mês, então CPL/CP-SAL/custo-demo daqui divergem — de propósito — dos números por safra. <b>Breakeven na competência</b> = Margem Contribuição (TCV×margem) cobre o Investimento Total (mídia+FEE) do mês. <b>Payback</b> = Resultado Acumulado ≥ 0 desde o início (jan/2025). TCV = ${TCVM}× mensalidade + implementação, reconhecido no mês do ganho — <b>só o DRE usa TCV</b>.</div>
   <div class="tbl-wrap"><table class="dre"><thead><tr>${head}</tr></thead><tbody>${b}</tbody></table></div>
   <div class="note"><b>Receita só registrada a partir de 2026:</b> <code>value_mensalidade</code> está preenchido só nos ganhos de 2026 — os de 2025 vêm zerados, então breakeven/payback de 2025 saem como <span class="muted-n">s/ receita</span> (não é prejuízo, é dado faltando). <b>Backfill da mensalidade de 2025 no CRM corrige o histórico</b> e o Resultado Acumulado passa a refletir o payback real.</div>`;}
// ---- sort clicável (F5.1): qualquer th dentro de .tbl-wrap ordena a tabela ----
function sortVal(td){if(!td)return -Infinity;const t=td.textContent.trim();
  if(!t||t==='—'||t==='·')return -Infinity;
  const n=parseFloat(t.replace(/R\$\s?/,'').replace(/\./g,'').replace(',','.').replace('%',''));
  return isNaN(n)?t.toLowerCase():n;}
document.addEventListener('click',e=>{const th=e.target.closest('.tbl-wrap th');if(!th)return;
  const tbl=th.closest('table'),tb=tbl&&tbl.tBodies[0];if(!tb)return;
  const i=[...th.parentNode.children].indexOf(th);
  const dir=th.dataset.dir==='desc'?'asc':'desc';
  tbl.querySelectorAll('th').forEach(x=>{delete x.dataset.dir;});th.dataset.dir=dir;
  [...tb.rows].map(r=>[sortVal(r.cells[i]),r])
   .sort((a,b)=>{const x=a[0],y=b[0];
     const c=(typeof x==='string'||typeof y==='string')?String(x).localeCompare(String(y),'pt'):x-y;
     return dir==='asc'?c:-c;})
   .forEach(([,r])=>tb.appendChild(r));});
// ---- filtro de texto do drill (F5.1): filtra as linhas EXIBIDAS da tela Mídia ----
function tfilt(inp){const q=inp.value.trim().toLowerCase();
  document.querySelectorAll('#scr-midia .stpane table tbody tr').forEach(r=>{
    r.style.display=!q||r.textContent.toLowerCase().includes(q)?'':'none';});}

// ---- Dimensões (F5.1): breakdowns mensais do flow (P.brk) ----
const BRK=P.brk||null;
const GEN_LBL={f:'Fem',m:'Masc',u:'—'};
function brkMeses(){if(!BRK)return new Set();const a=FILT.ini.slice(0,7),b=FILT.fim.slice(0,7);
  const s=new Set();BRK.meses.forEach((m,i)=>{if(m>=a&&m<=b)s.add(i);});return s;}
function brkAgg(rows,keyFn,o){const ms=brkMeses();const m={};
  rows.forEach(r=>{if(!ms.has(r[o.mi]))return;const k=keyFn(r);if(k==null||k==='')return;
    const a=m[k]||(m[k]={nome:k,inv:0,impr:0,clk:0,conv:0});
    a.inv+=r[o.inv]||0;a.impr+=r[o.impr]||0;a.clk+=r[o.clk]||0;if(o.conv!=null)a.conv+=r[o.conv]||0;});
  return Object.values(m).sort((x,y)=>y.inv-x.inv);}
function dimsTable(titulo,arr,temConv,tip){if(!arr.length)return '';
  return `<div class="chartbox"><h4>${titulo}${tip?` <span class="qask">— ${tip}</span>`:''}</h4><div class="tbl-wrap"><table><thead><tr>
   <th></th><th>Invest.</th><th>Impr.</th><th>Cliques</th><th>CTR</th>${temConv?'<th>Conv</th><th>Custo/conv</th>':''}</tr></thead><tbody>${
   arr.slice(0,14).map(r=>`<tr><td title="${esc(r.nome)}">${esc(tr(r.nome,26))}</td><td>${fM(r.inv)}</td><td>${fI(r.impr)}</td><td>${fI(r.clk)}</td><td>${(r.impr&&r.clk<=r.impr)?fP(r.clk/r.impr,2):'—'}</td>${temConv?`<td>${fR(r.conv)}</td><td>${fM(r.conv>=1?r.inv/r.conv:null)}</td>`:''}</tr>`).join('')
  }</tbody></table></div></div>`;}
// F5.2: UMA tabela full-width com seletor de dimensão + funil ESTIMADO (rateio)
// nas dimensões de entrega Meta; Google traz conversões reais; hora sem funil
// (o grão é campanha, não anúncio — rateio não aplica).
let DIMV='geo-meta';
function setDimv(v){DIMV=v;renderAll();}
const DIMV_OPTS=[['geo-meta','Geografia Meta'],['geo-google','Geografia Google'],['cidades','Cidades (Google)'],
                 ['idade','Idade'],['genero','Gênero'],['device','Device'],['hora','Hora do dia']];
function dimvTable(){
  const est=v=>v>0.05?fR(v):'<span class="muted-n">·</span>';
  const head=(extra)=>`<th></th><th>Invest.</th><th>Impr.</th><th>Cliques</th><th>CTR</th>${extra}`;
  const rowBase=r=>`<td title="${esc(r.nome)}">${esc(tr(r.nome,36))}</td><td>${fM(r.inv)}</td><td>${fI(r.impr)}</td><td>${fI(r.clk)}</td><td>${(r.impr&&r.clk<=r.impr)?fP(r.clk/r.impr,2):'—'}</td>`;
  const wrap=(h,b)=>`<div class="tbl-wrap"><table><thead><tr>${h}</tr></thead><tbody>${b}</tbody></table></div>`;
  if(DIMV==='geo-google'){
    const rows=deliveryAgg(BRK.ggeo.rows,{mi:1,inv:3,impr:4,clk:5,conv:6},r=>BRK.ggeo.regs[r[2]],gFunil());
    return wrap(head('<th>Conv</th><th>SAL*</th><th>CP-SAL*</th><th>D.ag*</th><th>D.real*</th><th>Ganho*</th><th>Fat*</th>'),
      rows.slice(0,20).map(r=>`<tr>${rowBase(r)}<td>${fR(r.conv)}</td><td>${est(r.sal)}</td><td>${fM(r.sal>0.05?r.inv/r.sal:null)}</td><td>${est(r.dag)}</td><td>${est(r.dre)}</td><td>${est(r.cli)}</td><td>${r.fat>1?fM(r.fat):'<span class="muted-n">·</span>'}</td></tr>`).join(''))
      +'<div class="note" style="margin-top:8px">Funil* Google: rateio por <b>campanha</b> (a API não desce de campanha no geo) — grão mais grosso que o rateio por anúncio do Meta.</div>';}
  if(DIMV==='cidades'){
    return wrap('<th>Cidade</th><th>Região</th><th>Invest.</th><th>Impr.</th><th>Cliques</th><th>Conv</th><th>SAL*</th><th>CP-SAL*</th><th>D.real*</th><th>Ganho*</th><th>Fat*</th>',
      BRK.gcid.rows.slice(0,25).map(r=>`<tr><td>${esc(r[0])}</td><td>${esc(tr(r[1],22))}</td><td>${fM(r[2])}</td><td>${fI(r[3])}</td><td>${fI(r[4])}</td><td>${fR(r[5])}</td><td>${est(r[7])}</td><td>${fM(r[7]>0.05?r[2]/r[7]:null)}</td><td>${est(r[9])}</td><td>${est(r[10])}</td><td>${r[11]>1?fM(r[11]):'<span class="muted-n">·</span>'}</td></tr>`).join(''))
      +'<div class="note" style="margin-top:8px">Cidades: todo o período (independe do filtro de data). Funil* por rateio de campanha.</div>';}
  if(DIMV==='hora'){
    const hh=deliveryAgg(BRK.hora.rows,{mi:1,inv:3,impr:4,clk:5},r=>r[2]+'h');hh.sort((a,b)=>parseInt(a.nome)-parseInt(b.nome));
    const hmax=Math.max(...hh.map(h=>h.inv),1);
    return wrap('<th>Hora</th><th>Invest.</th><th>Cliques</th><th>CTR</th><th>SAL*</th><th>CP-SAL*</th><th>D.real*</th>',
      hh.map(h=>`<tr><td>${h.nome}</td><td>${fM(h.inv)}<i class="ibar" style="width:${Math.max(2,h.inv/hmax*70).toFixed(0)}px"></i></td><td>${fI(h.clk)}</td><td>${(h.impr&&h.clk<=h.impr)?fP(h.clk/h.impr,2):'—'}</td><td>${est(h.sal)}</td><td>${fM(h.sal>0.05?h.inv/h.sal:null)}</td><td>${est(h.dre)}</td></tr>`).join(''))
      +'<div class="note" style="margin-top:8px">Hora por <b>anúncio</b> (F7.2): funil* = evento do ad no mês × share do invest naquela hora — estima o turno que gera SAL/demo, não o horário do evento em si.</div>';}
  const src=DIMV==='geo-meta'?[BRK.geo.rows,{mi:1,inv:3,impr:4,clk:5},r=>BRK.geo.regs[r[2]]]
    :DIMV==='idade'?[BRK.demo.rows,{mi:1,inv:4,impr:5,clk:6},r=>BRK.demo.ages[r[2]]]
    :DIMV==='genero'?[BRK.demo.rows,{mi:1,inv:4,impr:5,clk:6},r=>GEN_LBL[r[3]]||'—']
    :[BRK.dev.rows,{mi:1,inv:3,impr:4,clk:5},r=>BRK.dev.devs[r[2]]];
  const rows=deliveryAgg(src[0],src[1],src[2]);
  return wrap(head('<th>Leads*</th><th>SAL*</th><th>CP-SAL*</th><th>D.real*</th>'),
    rows.slice(0,20).map(r=>`<tr>${rowBase(r)}<td>${est(r.lead)}</td><td>${est(r.sal)}</td><td>${fM(r.sal>0.05?r.inv/r.sal:null)}</td><td>${est(r.dre)}</td></tr>`).join(''));}
function rDims(){
  if(!BRK)return `<h2 class="sec">Dimensões</h2><div class="note">Sem breakdowns do flow ainda — a extração roda às <b>segundas 07:00</b> (raw/flow-*.csv). Depois da 1ª rodada esta tela popula sozinha.</div>`;
  const subtabs=DIMV_OPTS.map(([k,l])=>`<button class="stbtn ${DIMV===k?'on':''}" onclick="setDimv('${k}')">${l}</button>`).join('');
  return `<h2 class="sec">Dimensões <span class="qask">— onde, pra quem e quando o anúncio roda?</span></h2>
   <div class="sec-desc"><b>Exibição mensal</b> (o filtro de período casa por mês cheio; o raw guarda o grão DIA) · fonte: extração do flow às segundas. Colunas com <b>*</b> = <b>funil/faturamento estimado por rateio</b> do investimento (nenhuma API dá conversão por breakdown): Meta rateia por <b>anúncio</b>, Google por <b>campanha</b> (geo não desce de campanha na API); a coluna Conv do Google é real da plataforma. Cabeçalhos ordenam. Respeita Período + Canal.</div>
   <div class="subtabs">${subtabs}</div>
   ${dimvTable()}
   <div class="note">Grão fino (ad×mês×dimensão, cidade a cidade, campanha×hora) vive em <code>raw/flow-*.csv</code>; o diário pleno segue no warehouse do flow (ad-hoc via MCP). Funil por dimensão do lado do CRM chega quando a aba <code>leads</code> popular (geo do form + device por user_agent).</div>`;}

// ---- rateio (F5.2): funil por (ad×mês) distribuído pela share de investimento ----
// da dimensão de entrega. A API Meta não dá conversão por breakdown — o funil
// por região/idade/gênero/device é ESTIMADO: evento(ad,mês) × share_spend(dim).
function brkFunil(){const m={};(BRK&&BRK.funil||[]).forEach(r=>{m[r[0]+'|'+r[1]]=r;});return m;}
function gFunil(){const m={};(BRK&&BRK.gfun||[]).forEach(r=>{m[r[0]+'|'+r[1]]=r;});return m;}
function deliveryAgg(rows,o,keyFn,FN){const ms=brkMeses();FN=FN||brkFunil();
  const den={};rows.forEach(r=>{if(!ms.has(r[o.mi]))return;const k=r[0]+'|'+r[o.mi];den[k]=(den[k]||0)+(r[o.inv]||0);});
  const m={};
  rows.forEach(r=>{if(!ms.has(r[o.mi]))return;const k=keyFn(r);if(k==null||k==='')return;
    const a=m[k]||(m[k]={nome:k,inv:0,impr:0,clk:0,conv:0,lead:0,sal:0,dag:0,dre:0,cli:0,fat:0});
    const inv=r[o.inv]||0;a.inv+=inv;a.impr+=r[o.impr]||0;a.clk+=r[o.clk]||0;if(o.conv!=null)a.conv+=r[o.conv]||0;
    const fk2=r[0]+'|'+r[o.mi],fn=FN[fk2],d=den[fk2];
    if(fn&&d>0){const sh=inv/d;a.lead+=fn[2]*sh;a.sal+=fn[3]*sh;a.dag+=fn[4]*sh;a.dre+=fn[5]*sh;a.cli+=fn[6]*sh;a.fat+=(fn[7]||0)*sh;}});
  return Object.values(m).sort((x,y)=>y.inv-x.inv);}

// ---- Cruzamento único (F5.2): mensagem × público/entrega × MÉTRICA escolhida ----
let CRZ={lin:'h',col:'publico',met:'sal'};
function setCrz(k,v){CRZ[k]=v;renderAll();}
const CRZ_LIN=[['c','Consciência'],['h','Gancho'],['a','Avatar'],['f','Formato']];
const CRZ_COL=[['publico','Público (conjunto)'],['tipo','Tipo de público'],['funil','Funil (COLD/WARM/HOT)'],['temp','Temperatura da campanha'],['consciencia','Consciência'],['gancho','Gancho'],
               ['regiao','Região (entrega*)'],['idade','Idade (entrega*)'],['genero','Gênero (entrega*)'],['device','Device (entrega*)']];
const CRZ_MET=[['inv','Investimento'],['lead','Leads'],['sal','SAL'],['dag','Demo agendada'],['dre','Demo realizada'],['cli','Clientes'],['cp_sal','CP-SAL'],['cp_dre','Custo/demo real.']];
function crzCell(c,met){if(!c)return null;
  if(met==='cp_sal')return c.sal>0.05?c.inv/c.sal:null;
  if(met==='cp_dre')return c.dre>0.05?c.inv/c.dre:null;
  return c[met];}
function crzFmt(v,met){if(v==null)return '<span class="muted-n">·</span>';
  return (met==='inv'||met==='cp_sal'||met==='cp_dre')?fM(v):(Number.isInteger(v)?fI(v):fR(v));}
function crzSection(){
  const A=i=>DIM.anun[i]||{};
  const isDeliv=['regiao','idade','genero','device'].includes(CRZ.col);
  const cell={},colTot={};
  const add=(lin,col,vals)=>{if(!lin||col==null||col==='')return;
    colTot[col]=(colTot[col]||0)+vals.inv;
    const k=lin+'|'+col;const c=cell[k]||(cell[k]={inv:0,lead:0,sal:0,dag:0,dre:0,cli:0});
    for(const m in vals)c[m]+=vals[m];};
  if(isDeliv){
    if(!BRK)return '<div class="note">Sem breakdowns do flow ainda (extração das segundas).</div>';
    const AT=i=>BRK.attrs[i]||{};
    const src=CRZ.col==='regiao'?[BRK.geo.rows,{mi:1,inv:3,impr:4,clk:5},r=>BRK.geo.regs[r[2]]]
      :CRZ.col==='idade'?[BRK.demo.rows,{mi:1,inv:4,impr:5,clk:6},r=>BRK.demo.ages[r[2]]]
      :CRZ.col==='genero'?[BRK.demo.rows,{mi:1,inv:4,impr:5,clk:6},r=>GEN_LBL[r[3]]||'—']
      :[BRK.dev.rows,{mi:1,inv:3,impr:4,clk:5},r=>BRK.dev.devs[r[2]]];
    const ms=brkMeses(),FN=brkFunil(),o=src[1];
    const den={};src[0].forEach(r=>{if(!ms.has(r[o.mi]))return;const k=r[0]+'|'+r[o.mi];den[k]=(den[k]||0)+(r[o.inv]||0);});
    src[0].forEach(r=>{if(!ms.has(r[o.mi]))return;
      const lin=AT(r[0])[CRZ.lin];if(!lin)return;
      const inv=r[o.inv]||0,fk2=r[0]+'|'+r[o.mi],fn=FN[fk2],d=den[fk2],sh=(fn&&d>0)?inv/d:0;
      add(lin,src[2](r),{inv,lead:fn?fn[2]*sh:0,sal:fn?fn[3]*sh:0,dag:fn?fn[4]*sh:0,dre:fn?fn[5]*sh:0,cli:fn?fn[6]*sh:0});});
  }else{
    const J=i=>DIM.conj[i]||{},C2=i=>DIM.camp[i]||{};
    const colOf=c=>CRZ.col==='publico'?(J(c.ji).publico||null):CRZ.col==='tipo'?(J(c.ji).tipo||null)
      :CRZ.col==='funil'?(J(c.ji).funil||null):CRZ.col==='temp'?(C2(c.ci).temp||null)
      :CRZ.col==='consciencia'?(A(c.ai).consciencia?(CONSC_LBL[A(c.ai).consciencia]||A(c.ai).consciencia):null)
      :(A(c.ai).gancho||null);
    dbRows().forEach(c=>{const lin=A(c.ai)[{c:'consciencia',h:'gancho',a:'avatar',f:'formato'}[CRZ.lin]];
      add(lin,colOf(c),{inv:c.inv,lead:c.lead,sal:c.sal,dag:c.demo_ag,dre:c.demo_re,cli:c.cli});});}
  const cols=Object.entries(colTot).sort((a,b)=>b[1]-a[1]).slice(0,9).map(([k])=>k);
  const lins=[...new Set(Object.keys(cell).map(k=>k.split('|')[0]))].sort();
  const lbl=CRZ.lin==='c'?(v=>CONSC_LBL[v]||v):(v=>v);
  const body=lins.map(l=>`<tr><td><b>${esc(lbl(l))}</b></td>${cols.map(cv=>`<td>${crzFmt(crzCell(cell[l+'|'+cv],CRZ.met),CRZ.met)}</td>`).join('')}</tr>`).join('');
  const sel=(k,opts)=>`<select class="dbxsel" onchange="setCrz('${k}',this.value)">${opts.map(([v,l])=>`<option value="${v}" ${CRZ[k]===v?'selected':''}>${l}</option>`).join('')}</select>`;
  return `<h2 class="sec">Cruzamento <span class="qask">— a mensagem certa pro público certo?</span></h2>
   <div class="sec-desc">Linha = atributo da mensagem · coluna = público ou entrega · célula = <b>a métrica escolhida</b>. Colunas de público/atributo usam o <b>funil real</b> (reconciliado); colunas de <b>entrega*</b> (região/idade/gênero/device) usam <b>funil estimado por rateio</b> do investimento (grão mensal — a API Meta não dá conversão por breakdown). Respeita Período + Canal.</div>
   <div style="display:flex;gap:10px;margin:6px 0 10px;flex-wrap:wrap">${sel('lin',CRZ_LIN)} <span style="align-self:center;color:var(--muted)">×</span> ${sel('col',CRZ_COL)} <span style="align-self:center;color:var(--muted)">·</span> ${sel('met',CRZ_MET)}</div>
   <div class="tbl-wrap"><table><thead><tr><th></th>${cols.map(c=>`<th>${esc(tr(c,16))}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></div>`;}

// ---- Biblioteca de criativos (F5.2): cards com preview + popup ----
const LIB=P.lib||null;
const ANIDX=(()=>{const m={};CA.forEach((n,i)=>m[n]=i);return m;})();
let LIBSORT='sal';
function setLibSort(v){LIBSORT=v;renderAll();}
function rCriativos(){
  if(!LIB)return '<h2 class="sec">Criativos</h2><div class="note">Sem assets do flow ainda — a extração roda às segundas.</div>';
  const m={};dbRows().forEach(c=>{const a=m[c.ai]||(m[c.ai]={ai:c.ai,nome:c.anun,inv:0,lead:0,sal:0,dre:0,cli:0});
    a.inv+=c.inv;a.lead+=c.lead;a.sal+=c.sal;a.dre+=c.demo_re;a.cli+=c.cli;});
  const cards=Object.values(m).filter(a=>a.inv>0);
  const key={sal:a=>a.sal,inv:a=>a.inv,cpsal:a=>a.sal?-a.inv/a.sal:-1e12,dre:a=>a.dre,cli:a=>a.cli}[LIBSORT];
  cards.sort((x,y)=>key(y)-key(x));
  const open=!!EXP['lib'];const shown=open?cards:cards.slice(0,24);
  const html=shown.map(a=>{const L=LIB[a.ai]||0;const img=L&&L[0];
    return `<div class="libcard" onclick="showCrt(${a.ai})">
      ${img?`<img loading="lazy" src="${esc(img)}" onerror="this.outerHTML='<div class=&quot;libph&quot;>sem preview</div>'">`:`<div class="libph">sem preview</div>`}
      <div class="libinfo"><div class="libname" title="${esc(a.nome)}">${esc(tr(a.nome,46))}</div>
      <div class="libm">${fM(a.inv)} · <b>${fI(a.sal)} SAL</b> · CP ${fM(a.sal?a.inv/a.sal:null)}${a.dre?` · ${fI(a.dre)} demo`:''}${a.cli?` · ${fI(a.cli)} cli`:''}</div></div></div>`;}).join('');
  const sel=`<select class="dbxsel" onchange="setLibSort(this.value)">${[['sal','mais SAL'],['inv','mais investimento'],['cpsal','melhor CP-SAL'],['dre','mais demos'],['cli','mais clientes']].map(([v,l])=>`<option value="${v}" ${LIBSORT===v?'selected':''}>${l}</option>`).join('')}</select>`;
  return `<h2 class="sec">Biblioteca de criativos <span class="qask">— o que roda e o que performa?</span></h2>
   <div class="sec-desc">Agrupado por <b>nome de anúncio</b> (mesmo criativo em N conjuntos/placements = 1 card) · métricas do período/canal filtrados · preview via flow (URLs do CDN renovam na extração das segundas). Clique no card pra ampliar com a copy. Ordenar por ${sel}</div>
   <div class="libgrid">${html||'<div class="empty">Nenhum anúncio com investimento no período.</div>'}</div>
   ${cards.length>24?`<button class="expbtn" onclick="togExp('lib')">${open?'▲ mostrar só top 24':'▼ mostrar todos ('+cards.length+')'}</button>`:''}`;}
function showCrt(ai){if(ai==null)return;const L=(LIB&&LIB[ai])||0;const nome=CA[ai]||'';
  const m={inv:0,lead:0,sal:0,dre:0,cli:0};dbRows().forEach(c=>{if(c.ai===ai){m.inv+=c.inv;m.lead+=c.lead;m.sal+=c.sal;m.dre+=c.demo_re;m.cli+=c.cli;}});
  document.getElementById('crtBody').innerHTML=
    (L&&L[0]?`<img src="${esc(L[0])}" onerror="this.style.display='none'">`:'<div class="libph" style="height:180px">sem preview (asset não sincronizado)</div>')+
    `<div class="crtname">${esc(nome)}</div>`+
    (L&&L[1]?`<div class="crtline"><b>Headline:</b> ${esc(L[1])}</div>`:'')+
    (L&&L[2]?`<div class="crtline"><b>CTA:</b> ${esc(L[2])}</div>`:'')+
    (L&&L[3]?`<div class="crtline crtcopy">${esc(L[3])}</div>`:'')+
    `<div class="crtline" style="margin-top:9px;border-top:1px solid var(--border);padding-top:9px"><b>No período:</b> ${fM(m.inv)} · ${fI(m.lead)} leads · ${fI(m.sal)} SAL (CP ${fM(m.sal?m.inv/m.sal:null)}) · ${fI(m.dre)} demos · ${fI(m.cli)} clientes</div>`;
  document.getElementById('crtModal').classList.add('on');}
function closeCrt(e){if(!e||e.target.id==='crtModal'||e.target.classList.contains('crtx'))document.getElementById('crtModal').classList.remove('on');}

// ---- Debriefing de criativos (F5): funil reconciliado agregado por ATRIBUTO ----
// da nomenclatura (P.dim — parseado pela taxonomia gia-v2 de 10-fundacao/taxonomia.yml).
// Cobertura parcial por design: gerações legadas (pré-taxonomia) não têm atributos.
const CONSC_LBL={UNC:'Unaware',PRB:'Problema',SOL:'Solução',PRO:'Produto',MIX:'Mix (DCO)'};
const FUNIL_LBL={COLD:'Frio (COLD)',WARM:'Morno (WARM)',HOT:'Quente (HOT)'};
function dbRows(){return CAMP.filter(c=>cMatch(c.canal)&&inR(c.data,FILT.ini,FILT.fim));}
function dbAgg(keyFn){const m={};dbRows().forEach(c=>{const k=keyFn(c);if(!k)return;
  const a=m[k]||(m[k]={nome:k,inv:0,lead:0,sal:0,rr:0,cli:0});
  a.inv+=c.inv;a.lead+=c.lead;a.sal+=c.sal;a.rr+=c.demo_re;a.cli+=c.cli;});
  return Object.values(m).sort((x,y)=>y.inv-x.inv);}
function dbTable(id,titulo,keyFn,tip){const rows=dbAgg(keyFn);if(!rows.length)return '<div class="empty">Sem dado com este atributo no período (geração legada não tem atributos).</div>';
  const ti=rows.reduce((s,r)=>s+r.inv,0),ts=rows.reduce((s,r)=>s+r.sal,0);const bl=ts?ti/ts:null;
  const N=12;
  const tbl=`<div class="tbl-wrap"><table><thead><tr>
    <th></th><th>Invest.</th><th>Leads</th><th>CPL</th><th>SAL</th><th>CP-SAL</th><th>D.real</th><th>CP-DR</th><th>Cli</th></tr></thead><tbody>${
    expRowsDb(id,rows,bl,N)}</tbody></table></div>${rows.length>N?`<button class="expbtn" onclick="togExp('${id}')">${EXP[id]?'▲ mostrar só top '+N:'▼ mostrar todas ('+rows.length+')'}</button>`:''}`;
  return titulo?`<div class="chartbox"><h4>${titulo}${tip?` <span class="qask">— ${tip}</span>`:''}</h4>${tbl}</div>`:tbl;}
function expRowsDb(id,rows,bl,N=12){return (EXP[id]?rows:rows.slice(0,N)).map(r=>{
  const cps=r.sal?r.inv/r.sal:null,st=cps==null?'':(bl&&cps<=bl?' class="s-ok"':(bl&&cps>bl*1.5?' class="s-bad"':''));
  return `<tr><td title="${esc(r.nome)}">${esc(tr(r.nome,40))}</td><td>${fM(r.inv)}</td><td>${fI(r.lead)}</td><td>${fM(r.lead?r.inv/r.lead:null)}</td><td>${fI(r.sal)}</td><td${st}>${fM(cps)}</td><td>${fI(r.rr)}</td><td>${fM(r.rr?r.inv/r.rr:null)}</td><td>${fI(r.cli)}</td></tr>`;}).join('');}
// F5.2: 1 tabela FULL-WIDTH por grupo, com subtabs escolhendo a dimensão
// (acaba com a grade de tabelinhas espremidas com scroll horizontal).
let DBSEL={msg:'consc',pub:'publico'};
function setDbsel(k,v){DBSEL[k]=v;renderAll();}
const DB_MSG=[['consc','Consciência'],['gancho','Gancho'],['avatar','Avatar'],['formato','Formato'],['tema','Tema']];
const DB_PUB=[['publico','Público'],['tipo','Tipo de público'],['funil','Funil'],['temp','Temperatura'],['obj','Evento otimizado']];
function dbKey(k){const A=i=>DIM.anun[i]||{},J=i=>DIM.conj[i]||{},C2=i=>DIM.camp[i]||{};
  return {consc:c=>{const a=A(c.ai);return a.consciencia?(CONSC_LBL[a.consciencia]||a.consciencia):null;},
    gancho:c=>A(c.ai).gancho||null, avatar:c=>A(c.ai).avatar||null, formato:c=>A(c.ai).formato||null,
    tema:c=>{const a=A(c.ai);return a.narrativa||a.variacao||null;},
    publico:c=>J(c.ji).publico||null, tipo:c=>J(c.ji).tipo||null,
    funil:c=>{const j=J(c.ji);return j.funil?(FUNIL_LBL[j.funil]||j.funil):null;},
    temp:c=>C2(c.ci).temp||null, obj:c=>C2(c.ci).obj||null}[k];}
function dbGroup(id,grupo,opts,selKey){
  const subtabs=opts.map(([k,l])=>`<button class="stbtn ${DBSEL[selKey]===k?'on':''}" onclick="setDbsel('${selKey}','${k}')">${l}</button>`).join('');
  return `<h2 class="sec">${grupo}</h2>
   <div class="subtabs">${subtabs}</div>
   ${dbTable(id+DBSEL[selKey],'',dbKey(DBSEL[selKey]))}`;}
function rDebrief(){
  if(!DIM)return '<div class="note">Payload sem bloco <b>dim</b> — regere o monitor.</div>';
  const A=i=>DIM.anun[i]||{};
  const rows=dbRows();const tot=rows.reduce((s,c)=>s+c.inv,0);
  const cov=rows.reduce((s,c)=>s+((A(c.ai).geracao&&A(c.ai).geracao!=='legado')?c.inv:0),0);
  return `<h2 class="sec">Debriefing de criativos <span class="qask">— qual mensagem vende?</span></h2>
   <div class="sec-desc">Funil <b>reconciliado</b> agregado pelos <b>atributos da nomenclatura</b> (taxonomia gia-v2 — <code>10-fundacao/taxonomia.yml</code>). <b>Cobertura: ${fP(tot?cov/tot:0)} do investimento do período tem atributos</b> — o resto é geração legada (pré-taxonomia, antes de mai/2026). CP-SAL <span class="s-ok">verde</span> = melhor que o blended; <span class="s-bad">vermelho</span> = &gt;1,5×. Cabeçalhos ordenam. Respeita Período + Canal.</div>
   ${dbGroup('dbm','Mensagem',DB_MSG,'msg')}
   ${dbGroup('dbp','Público &amp; segmentação',DB_PUB,'pub')}
   ${crzSection()}
   <div class="note"><b>Loop de qualidade:</b> nome fora do padrão não entra aqui — aparece no <code>derivado/qa-report.json</code> e é tarefa de correção do media-buyer (convenção em <code>10-fundacao/taxonomia.yml</code>). Atributos por anúncio (com copy/CTA do flow): <code>derivado/dim-criativo.csv</code>.</div>`;}
// charts
let CH={};
function destroyCharts(){Object.values(CH).forEach(c=>{try{c.destroy();}catch(e){}});CH={};}
function drawCharts(){if(!window.Chart)return;const DL=window.ChartDataLabels;
  const RED='#E50914',REDL='#FF4040',YEL='#FFDD00',GRY='rgba(255,255,255,.5)',GRID='rgba(255,255,255,.07)';
  Chart.defaults.color=GRY;Chart.defaults.font.family='IBM Plex Sans, sans-serif';Chart.defaults.font.size=11;
  if(DL)Chart.defaults.plugins.datalabels={display:false};
  const ax={grid:{color:GRID},ticks:{color:GRY}};const brl=v=>'R$ '+Number(v).toLocaleString('pt-BR',{maximumFractionDigits:0});
  // rótulo no ÚLTIMO ponto das séries (linha com label em todo ponto = ruído)
  const lastDL=(fmt,color)=>({display:c=>{const d=c.dataset.data;let li=d.length-1;while(li>=0&&d[li]==null)li--;return c.dataIndex===li;},
    align:'top',anchor:'end',color:color||'#fff',font:{family:'Archivo',weight:'700',size:11},formatter:fmt||(v=>fI(v)),clip:false});
  const dm=serieDemosMes(),el=document.getElementById('cDemosMes');
  if(el)CH.dm=new Chart(el,{type:'bar',data:{labels:dm.labels,datasets:[
    {label:'Realizadas',data:dm.vals,backgroundColor:RED,borderRadius:4,order:2,
     datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:12},formatter:v=>fI(v)}},
    {type:'line',label:'Meta '+dm.meta,data:dm.labels.map(()=>dm.meta),borderColor:YEL,borderDash:[6,4],borderWidth:2,pointRadius:0,order:1}]},
    options:{responsive:true,layout:{padding:{top:18}},plugins:{legend:{labels:{boxWidth:12}}},scales:{x:ax,y:{...ax,beginAtZero:true,suggestedMax:Math.max(dm.meta, ...dm.vals)*1.15}}},plugins:DL?[DL]:[]});
  const pp=pipelineAberto(), epp=document.getElementById('cPipe');
  if(epp)CH.p=new Chart(epp,{type:'bar',data:{labels:pp.labels,datasets:[{label:'Em aberto',data:pp.vals,backgroundColor:'rgba(255,255,255,.32)',borderRadius:4,
    datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:12},formatter:v=>fI(v)}}]},
    options:{responsive:true,maintainAspectRatio:false,layout:{padding:{top:18}},plugins:{legend:{display:false}},scales:{x:ax,y:{...ax,beginAtZero:true}}},plugins:DL?[DL]:[]});
  const fmes=fechadosMes(),efmes=document.getElementById('cFechMes');
  if(efmes)CH.fm=new Chart(efmes,{type:'bar',data:{labels:fmes.labels,datasets:[{label:'Ganhos',data:fmes.vals,backgroundColor:'#2FBF71',borderRadius:4,
    datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:11},formatter:v=>fI(v)}}]},
    options:{responsive:true,layout:{padding:{top:18}},plugins:{legend:{display:false}},scales:{x:ax,y:{...ax,beginAtZero:true}}},plugins:DL?[DL]:[]});
  const fano=fechadosAno(),efano=document.getElementById('cFechAno');
  if(efano)CH.fa=new Chart(efano,{type:'bar',data:{labels:fano.labels,datasets:[{label:'Ganhos',data:fano.vals,backgroundColor:'#2FBF71',borderRadius:4,
    datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:13},formatter:v=>fI(v)}}]},
    options:{responsive:true,layout:{padding:{top:18}},plugins:{legend:{display:false}},scales:{x:ax,y:{...ax,beginAtZero:true}}},plugins:DL?[DL]:[]});
  const v=serieVolume(),ev=document.getElementById('cVolume');
  if(ev)CH.v=new Chart(ev,{type:'line',data:{labels:v.labels,datasets:[
    {label:'Leads',data:v.leads,borderColor:GRY,tension:.3,pointRadius:0,borderWidth:1.5,datalabels:lastDL(null,GRY)},
    {label:'SAL',data:v.sal,borderColor:REDL,tension:.3,pointRadius:0,borderWidth:2,datalabels:lastDL(null,REDL)},
    {label:'Demos realizadas',data:v.demos,borderColor:RED,backgroundColor:'rgba(229,9,20,.10)',fill:true,tension:.3,pointRadius:0,borderWidth:2,datalabels:lastDL(null,'#fff')}]},
    options:{responsive:true,layout:{padding:{top:16,right:26}},interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:12}}},scales:{x:ax,y:{...ax,beginAtZero:true}}},plugins:DL?[DL]:[]});
  const e=serieEfic(),ee=document.getElementById('cEfic');
  if(ee)CH.e=new Chart(ee,{type:'line',data:{labels:e.labels,datasets:[
    {label:'Custo/demo',data:e.custo_demo,borderColor:RED,tension:.3,pointRadius:0,borderWidth:2,spanGaps:true,datalabels:lastDL(brl,'#fff')},
    {label:'CP-SAL',data:e.cp_sal,borderColor:YEL,tension:.3,pointRadius:0,borderWidth:2,spanGaps:true,datalabels:lastDL(brl,YEL)}]},
    options:{responsive:true,layout:{padding:{top:16,right:34}},interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:12}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+brl(c.parsed.y)}}},scales:{x:ax,y:{...ax,beginAtZero:true,ticks:{color:GRY,callback:v=>brl(v)}}}},plugins:DL?[DL]:[]});
  const CHCOL={meta:'#FF4040',google:'#FFC400',seo:'#2FBF71',direct:'#5BA3D0'},PAL=['#FF4040','#FFC400','#2FBF71','#5BA3D0','#B388FF','#FF9F40'];
  // small multiples de custo por etapa (1 métrica/escala por chart)
  const custoCanal=(id,ev)=>{const el=document.getElementById(id);if(!el)return;const d=serieCustoCanal(ev);
    CH[id]=new Chart(el,{type:'line',data:{labels:d.labels,datasets:d.series.map((s,i)=>({label:CHNAME(s.canal),data:s.data,borderColor:CHCOL[s.canal]||PAL[i%PAL.length],borderWidth:2,pointRadius:0,tension:.3,spanGaps:true,datalabels:lastDL(brl,CHCOL[s.canal]||PAL[i%PAL.length])}))},
      options:{responsive:true,layout:{padding:{top:16,right:34}},interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:12}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+brl(c.parsed.y)}}},scales:{x:ax,y:{...ax,beginAtZero:true,ticks:{color:GRY,callback:v=>brl(v)}}}},plugins:DL?[DL]:[]});};
  custoCanal('cCpsalCanal','sal');custoCanal('cCpdaCanal','demo_ag');custoCanal('cCpdrCanal','demo_re');
  const ls=serieLeadsStatus(),els=document.getElementById('cLeadsStatus');
  if(els)CH.ls=new Chart(els,{type:'bar',data:{labels:ls.labels,datasets:[
    {label:'Aberto',data:ls.ab,backgroundColor:'rgba(255,255,255,.30)',datalabels:{display:false}},
    {label:'Perdido',data:ls.pe,backgroundColor:RED,datalabels:{display:false}},
    {label:'Ganho',data:ls.ga,backgroundColor:'#2FBF71',
     datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:10},clip:false,
       formatter:(v,c)=>fI(ls.ab[c.dataIndex]+ls.pe[c.dataIndex]+ls.ga[c.dataIndex])}}]},
    options:{responsive:true,layout:{padding:{top:16}},plugins:{legend:{labels:{boxWidth:12}}},scales:{x:{...ax,stacked:true},y:{...ax,stacked:true,beginAtZero:true}}},plugins:DL?[DL]:[]});
  // ---- sparklines dos cards OKR (últimas 8 semanas · respeita canal) ----
  function drawSpark(id,data){const el=document.getElementById(id);if(!el)return;
    CH[id]=new Chart(el,{type:'line',data:{labels:data.map((_,i)=>i),datasets:[{data,borderColor:REDL,borderWidth:1.5,pointRadius:0,tension:.35,fill:'origin',backgroundColor:'rgba(229,9,20,.08)'}]},
      options:{responsive:false,animation:false,plugins:{legend:{display:false},tooltip:{enabled:false}},scales:{x:{display:false},y:{display:false,beginAtZero:true}}}});}
  drawSpark('spk-dre',sparkSeries(l=>l.show_at?[l.show_at,1]:null));
  drawSpark('spk-dag',sparkSeries(l=>l.sched_at?[l.sched_at,1]:null));
  drawSpark('spk-cli',sparkSeries(l=>(l.win&&l.win_at)?[l.win_at,1]:null));
  drawSpark('spk-val',sparkSeries(l=>(l.win&&l.win_at)?[l.win_at,fatOf(l)]:null));
  // ---- Qualificadores: evolução (stacked) + conversão por valor ----
  const eqe=document.getElementById('cQualEvo');
  if(eqe){const qe=qualEvo();
    CH.qe=new Chart(eqe,{type:'bar',data:{labels:qe.labels,datasets:[...qe.series.map((s,i)=>({label:tr(s.v,22),data:s.data,backgroundColor:PAL[i%PAL.length],datalabels:{display:false}})),
      {label:'Outros',data:qe.outros,backgroundColor:'rgba(255,255,255,.22)',
       datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:10},clip:false,
         formatter:(v,c)=>fI(qe.series.reduce((s,sr)=>s+sr.data[c.dataIndex],0)+qe.outros[c.dataIndex])}}]},
      options:{responsive:true,layout:{padding:{top:16}},plugins:{legend:{labels:{boxWidth:12}}},scales:{x:{...ax,stacked:true},y:{...ax,stacked:true,beginAtZero:true}}},plugins:DL?[DL]:[]});}
  const eqc=document.getElementById('cQualConv');
  if(eqc){const rows=qualAgg(QKEY).slice(0,8);
    CH.qc=new Chart(eqc,{type:'bar',data:{labels:rows.map(r=>tr(r.k,26)),datasets:[{label:'Lead→Cliente',data:rows.map(r=>+(r.p_cli*100).toFixed(2)),backgroundColor:RED,borderRadius:4,
      datalabels:{display:true,anchor:'end',align:'end',color:'#fff',font:{family:'Archivo',weight:'700',size:11},clip:false,formatter:v=>fR(v)+'%'}}]},
      options:{indexAxis:'y',responsive:true,layout:{padding:{right:36}},plugins:{legend:{display:false}},scales:{x:{...ax,beginAtZero:true,ticks:{color:GRY,callback:v=>v+'%'}},y:ax}},plugins:DL?[DL]:[]});}
}
function renderAll(){destroyCharts();
  document.getElementById('scr-geral').innerHTML=rGeral();
  document.getElementById('scr-atencao').innerHTML=rAtencao();
  document.getElementById('scr-funil').innerHTML=rFunil();
  document.getElementById('scr-quals').innerHTML=rQuals();
  document.getElementById('scr-safra').innerHTML=rSafra();
  document.getElementById('scr-midia').innerHTML=rMidia();
  document.getElementById('scr-lib').innerHTML=rCriativos();
  document.getElementById('scr-debrief').innerHTML=rDebrief();
  document.getElementById('scr-dims').innerHTML=rDims();
  document.getElementById('scr-mensal').innerHTML=rMensal();
  // só os subtabs COM data-st (drill da Mídia) — os Qualificadores usam a mesma
  // classe visual mas onclick inline próprio (setQ); .onclick aqui sobrescreveria
  document.querySelectorAll('.stbtn[data-st]').forEach(b=>b.onclick=()=>{document.querySelectorAll('.stbtn[data-st]').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.stpane').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById('sp-'+b.dataset.st).classList.add('on');});
  document.querySelectorAll('.st2btn').forEach(b=>b.onclick=()=>{document.querySelectorAll('.st2btn').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.s2pane').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById('s2-'+b.dataset.s2).classList.add('on');});
  document.querySelectorAll('.st3btn').forEach(b=>b.onclick=()=>{document.querySelectorAll('.st3btn').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.s3pane').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.getElementById('s3-'+b.dataset.s3).classList.add('on');});
  drawCharts();const[a,b]=curRange();
  let rl=a.split('-').reverse().join('/')+' → '+b.split('-').reverse().join('/');
  if(FILT.cmp!=='none'){const[ca,cb]=compRange(a,b,FILT.cmp);if(ca)rl+='  ·  vs '+ca.split('-').reverse().join('/')+' → '+cb.split('-').reverse().join('/');}
  document.getElementById('frange').textContent=rl;}
// ---- date-range picker (estilo Google Ads) ----
function togPop(id){const p=document.getElementById(id);const open=p.classList.contains('on');
  document.querySelectorAll('.pop').forEach(x=>x.classList.remove('on'));
  if(!open){p.classList.add('on');if(id==='popPeriod'){DRAFT={...FILT};calAnchor=DRAFT.ini.slice(0,7)+'-01';pickStage=0;buildPicker();}if(id==='popChan')buildChan();}}
function closePop(){document.querySelectorAll('.pop').forEach(x=>x.classList.remove('on'));}
document.addEventListener('click',e=>{if(!e.target.closest('.fctl'))closePop();});
function buildPresets(){document.getElementById('presets').innerHTML=PRESETS.map(([n])=>`<button class="pset ${DRAFT.preset===n?'on':''}" onclick="pickPreset('${n}')">${n}</button>`).join('')+`<button class="pset ${DRAFT.preset==='custom'?'on':''}" onclick="pickPreset('custom')">Personalizar</button>`;}
function pickPreset(n){if(n==='custom'){DRAFT.preset='custom';pickStage=0;buildPicker();return;}const f=PRESETS.find(p=>p[0]===n)[1]();DRAFT.ini=f[0];DRAFT.fim=f[1];DRAFT.preset=n;FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function buildCal(elId,anchor){const d0=DD(anchor),y=d0.getFullYear(),mo=d0.getMonth(),first=new Date(y,mo,1),start=first.getDay(),dim=new Date(y,mo+1,0).getDate();
  let h=`<div class="calhd"><button class="calnav" onclick="navCal(-1)">‹</button><span>${MES_PT[mo]} ${y}</span><button class="calnav" onclick="navCal(1)">›</button></div><div class="cgrid">`+['D','S','T','Q','Q','S','S'].map(x=>`<div class="dow">${x}</div>`).join('');
  for(let i=0;i<start;i++)h+=`<div class="cd out"></div>`;
  const cmp=DRAFT.cmp!=='none'?compRange(DRAFT.ini,DRAFT.fim,DRAFT.cmp):null;
  for(let dn=1;dn<=dim;dn++){const ds=SD(new Date(y,mo,dn));let cls='cd';if(ds===DRAFT.ini||ds===DRAFT.fim)cls+=' sel';else if(ds>DRAFT.ini&&ds<DRAFT.fim)cls+=' inr';if(cmp&&cmp[0]&&ds>=cmp[0]&&ds<=cmp[1])cls+=' cmpr';h+=`<div class="${cls}" onclick="pickDay('${ds}')">${dn}</div>`;}
  document.getElementById(elId).innerHTML=h+`</div>`;}
function navCal(n){calAnchor=addM(calAnchor,n);buildPicker();}
function pickDay(ds){DRAFT.preset='custom';if(pickStage===0){DRAFT.ini=ds;DRAFT.fim=ds;pickStage=1;}else{if(ds<DRAFT.ini){DRAFT.fim=DRAFT.ini;DRAFT.ini=ds;}else DRAFT.fim=ds;pickStage=0;}buildPicker();}
function buildCmp(){document.getElementById('cmpTog').checked=DRAFT.cmp!=='none';
  document.getElementById('cmpOpts').innerHTML=DRAFT.cmp!=='none'?[['month','Mês anterior'],['year','Ano anterior'],['prev','Período anterior']].map(([k,l])=>`<button class="cmpopt ${DRAFT.cmp===k?'on':''}" onclick="setCmpMode('${k}')">${l}</button>`).join(' '):'';}
function onCmpTog(){DRAFT.cmp=document.getElementById('cmpTog').checked?'month':'none';FILT.cmp=DRAFT.cmp;buildPicker();updPeriodLabel();renderAll();}
function setCmpMode(k){DRAFT.cmp=k;FILT.cmp=k;buildPicker();updPeriodLabel();renderAll();}
function buildPicker(){buildPresets();buildCal('calA',calAnchor);buildCal('calB',addM(calAnchor,1));buildCmp();}
function applyPeriod(){FILT={...DRAFT};updPeriodLabel();closePop();renderAll();}
function updPeriodLabel(){document.getElementById('vPeriod').textContent=fmtRange(FILT.ini,FILT.fim);
  document.getElementById('vCmp').textContent=FILT.cmp==='none'?'':'vs '+CMPLAB[FILT.cmp];}
// ---- canal multi-select ----
function buildChan(){document.getElementById('chanList').innerHTML=CHANNELS.map(c=>`<label class="chk"><input type="checkbox" ${SELCH.has(c)?'checked':''} onchange="tgch('${c}')"><span>${CHNAME(c)}${PAID_CH.includes(c)?' <span class="s-ok">●</span>':''}</span></label>`).join('');updChanLabel();}
function updChanLabel(){const el=document.getElementById('vChan');if(!el)return;
  el.textContent=(PAID_CH.length&&SELCH.size===PAID_CH.length&&PAID_CH.every(c=>SELCH.has(c)))?'Só pagos':allCh()?'Todos os canais':SELCH.size+' canais';}
function tgch(c){SELCH.has(c)?SELCH.delete(c):SELCH.add(c);if(SELCH.size===0)SELCH=new Set(CHANNELS);buildChan();renderAll();}
function chMeta(){SELCH=new Set(PAID_CH.length?PAID_CH:CHANNELS);buildChan();renderAll();}
function chAll(){SELCH=new Set(CHANNELS);buildChan();renderAll();}
function boot(){const f=P.freshness;
  document.getElementById('fresh').innerHTML=`dados CRM até <b>${f.crm_ate}</b><br>campanhas até <b>${f.camp_ate}</b><br>gerado ${f.gerado}`;
  updPeriodLabel();buildChan();
  document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.screen').forEach(x=>x.classList.remove('on'));t.classList.add('on');document.getElementById(t.dataset.scr).classList.add('on');
    // charts criados em aba display:none ficam no tamanho fallback — força resize ao exibir
    requestAnimationFrame(()=>Object.values(CH).forEach(c=>{try{c.resize();}catch(e){}}));});
  renderAll();}
if(document.readyState!=='loading')boot();else document.addEventListener('DOMContentLoaded',boot);
"""

def render(P):
    f = P["freshness"]; q = P["quarter"]
    shell = """<!DOCTYPE html><html lang="pt-BR" data-theme="dark"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor · Sigo ERP · __QLABEL__</title>
<meta name="description" content="Cockpit de aquisição · OKR __QLABEL__ · CRM + campanhas">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&display=swap" rel="stylesheet">
<style>__CSS__</style></head><body>
<div class="topbar"></div>
<div class="wrap">
 <header class="head">
   <h1>Monitor · <b>Sigo ERP</b></h1>
   <div class="fresh" id="fresh"></div>
 </header>
 <div class="filterbar">
   <div class="fb">
     <div class="fctl">
       <button class="fbtn" onclick="togPop('popPeriod')"><span class="cap">Período</span><span class="val" id="vPeriod"></span><span class="cmpv" id="vCmp"></span><span class="ar">▾</span></button>
       <div class="pop" id="popPeriod" onclick="event.stopPropagation()">
         <div class="dpick">
           <div class="presets" id="presets"></div>
           <div class="calwrap">
             <div class="cals"><div class="cal" id="calA"></div><div class="cal" id="calB"></div></div>
             <div class="cmpbar"><label class="switch"><input type="checkbox" id="cmpTog" onchange="onCmpTog()"><span class="sl"></span></label>
               <span class="cmplbl">Comparar</span><span id="cmpOpts"></span></div>
           </div>
         </div>
         <div class="popfoot"><button class="bt" onclick="closePop()">Cancelar</button><button class="bt pri" onclick="applyPeriod()">Aplicar</button></div>
       </div>
     </div>
     <div class="fctl">
       <button class="fbtn" onclick="togPop('popChan')"><span class="cap">Canal</span><span class="val" id="vChan"></span><span class="ar">▾</span></button>
       <div class="pop right chanpop" id="popChan" onclick="event.stopPropagation()">
         <div class="chquick"><button class="qbtn" onclick="chMeta()">só pagos</button><button class="qbtn" onclick="chAll()">todos</button></div>
         <div id="chanList"></div>
       </div>
     </div>
   </div>
   <div class="frange" id="frange"></div>
 </div>
 <div class="layout">
   <nav class="sidenav">
     <button class="tab on" data-scr="scr-geral">Visão Geral</button>
     <button class="tab" data-scr="scr-atencao">Atenção</button>
     <button class="tab" data-scr="scr-funil">Funil &amp; Pipeline</button>
     <button class="tab" data-scr="scr-quals">Qualificadores</button>
     <button class="tab" data-scr="scr-safra">Safra</button>
     <button class="tab" data-scr="scr-midia">Mídia</button>
     <button class="tab" data-scr="scr-lib">Criativos</button>
     <button class="tab" data-scr="scr-debrief">Debriefing</button>
     <button class="tab" data-scr="scr-dims">Dimensões</button>
     <button class="tab" data-scr="scr-mensal">Mensal / DRE</button>
   </nav>
   <div class="main">
     <section class="screen on" id="scr-geral"></section>
     <section class="screen" id="scr-atencao"></section>
     <section class="screen" id="scr-funil"></section>
     <section class="screen" id="scr-quals"></section>
     <section class="screen" id="scr-safra"></section>
     <section class="screen" id="scr-midia"></section>
     <section class="screen" id="scr-lib"></section>
     <section class="screen" id="scr-debrief"></section>
     <section class="screen" id="scr-dims"></section>
     <section class="screen" id="scr-mensal"></section>
   </div>
 </div>
 <div id="crtModal" onclick="closeCrt(event)"><div class="crtbox"><button class="crtx" onclick="closeCrt()">✕</button><div id="crtBody"></div></div></div>
 <footer>
   <div>Monitor · Sigo ERP · fonte: CRM (verdade) + campanhas (join ad_id, reconciliado) · metas vigência __VIGL__ · gerado __GERADO__</div>
   <div>Growth IA Ops v2.0 · V4 Colli&amp;Co</div>
 </footer>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script>__JS__</script>
</body></html>"""
    js = JS.replace("__PAYLOAD__", json.dumps(P, ensure_ascii=False))
    vig = (P.get("vigencia") or {}).get("label", q["label"])
    return (shell.replace("__CSS__", CSS).replace("__JS__", js)
            .replace("__QLABEL__", q["label"]).replace("__VIGL__", vig)
            .replace("__GERADO__", f["gerado"]))
