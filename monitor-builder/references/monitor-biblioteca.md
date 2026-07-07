# Biblioteca de componentes do Modo Monitor — catálogo canônico

> **Fonte da verdade visual/UX/racional: `exemplos/martins/`** (re-sync 2026-07-02).
> Cada entrada aponta identificadores estáveis (funções JS, classes CSS, funções Python)
> no `_render_monitor.py` do exemplo — copie DE LÁ, não de memória. O que muda por
> modelo de negócio mora nos **blueprints** (`blueprints/*.md`); o que está aqui é
> agnóstico de modelo.
>
> **Kit físico (Fase 2 — pendente):** quando o 2º monitor for construído com este
> catálogo, extrair os componentes estáveis pra `assets/monitor-kit/` (css+js vendorados
> com `KIT_VERSION` no projeto; sub-modo `atualizar-kit` re-sincroniza). Extração
> dirigida por uso — não extrair especulativamente.

## Como usar

1. Escolha o **blueprint** pelo modelo de negócio do cliente → ele dita telas, KPIs e o cruzamento do `_gerar-monitor.py`.
2. Componha as telas com os componentes abaixo, clonando do exemplo martins.
3. Ao terminar, rode o **passo de colheita** (`modo-monitor-workflow.md` Passo 6).

## Camada de estrutura e filtros

| Componente | Identificadores no exemplo | Contrato de dados | Notas / variação |
|---|---|---|---|
| Shell do cockpit (topbar gradiente, header, sidebar de telas, main) | CSS `.topbar .head .layout .sidenav .tab`; JS `SCR`, `go()`, `renderAll()` | `SCR` = lista [id, label] das telas (vem do blueprint) | Sidebar vira wrap horizontal ≤920px |
| Date-range picker (presets + calendário duplo + comparação) | JS `PRESETS`, `FILT`, `DRAFT`, `buildPicker()`, `cmpRange()`, `applyPeriod()`; CSS `.dpick .presets .cal .cmpbar` | `D.qini/qfim` (vigência), `D.dmin/dmax`, `D.today` | Presets "Este trimestre" recortam pela vigência do contrato |
| Canal multi-select | JS `SELCH`, `buildChan()`, `chMeta()/chAll()`, `periodMeta()`; CSS `.chanpop .chk` | `D.canais_meta` + canais descobertos dos dados | `periodMeta()` = gate de exibição de metas. Variante `canais_meta: null` (sigo): meta é da operação toda → gate vira `allCh()` |
| Popups (não fechar no re-render) | `togPop()/closePop()` + `onclick="event.stopPropagation()"` no `.pop` | — | Gotcha clássico: listener global fecha popup cujo elemento saiu do DOM |
| Subtabs de alternância | CSS `.subtabs .stbtn`; padrão `let KEY=...; function setKEY(k){...;renderAll()}` | — | Usado em cohort taxa/valor, drill, Volume↔Receita, frente do cohort |

## Camada de calendário e economia (exemplo canônico: `exemplos/colina/`)

| Componente | Identificadores no exemplo colina | Contrato de dados | Notas / variação |
|---|---|---|---|
| **Mês fiscal customizado** (ex. 16→15, nomeado pelo fim) | Python `fm_key()`; JS `FD`, `fmKey()/fmStart()/fmEnd()/fmAdd()` | contrato `mes_fiscal{dia_inicio, nomeia_por}` | Substitui o mês civil em metas, presets ("Este mês" = fiscal vigente), série mensal, safras e payback; vigência do quarter também fiscal. Forecast do preset que termina em hoje projeta até `fmEnd(fmKey(today))` |
| **Receita PREMISSA híbrida rec+TCV por BU** | Python `RECEITA`; JS `RC`, `contratoVal()/mensalVal()/receitaK()`, `PREM_TXT`, pill `.prem` | contrato `receita.por_bu{modelo: recorrente\|tcv, mensalidade, ltv_meses, valor}` + `fonte: premissa\|crm` | Quando o campo de receita do CRM está vazio: valores da fundação com **selo PREMISSA visível**; metas de receita derivam de `clientes_meta × valor_contrato`. Trocar `fonte` quando o dado real chegar — sem tocar código |
| **Rateio de canal indireto** (receptivo → pagos) | Python `FRAC_BU/FRAC_GLOBAL`, `rateia_mz()` | taxa observada de leads rastreáveis com canal pago, POR segmento | Determinístico no grão deal (streaming proporcional); fracionário nos agregados e no lado bd_ads. **Silencioso na UI** (decisão de modelo, não nota de rodapé) |
| **Atribuição de funil ao drill** (MQL/SQL/Ganho → campanha/conjunto/anúncio) | Python `AD2CRE`, `EV_MQL/EV_SQL/EV_WIN`, `_atribui()`, `DRILL["ev"]` | eventos do CRM ancorados no **mês fiscal do LEAD** | Motor ÚNICO pros 3 eventos: ad_id rastreável E criativo com invest no mês → direto; senão proporcional aos rastreáveis do mês×BU×canal; fallback share de invest; sem base → sem atribuição. Trava: **nunca assenta em criativo-mês sem investimento**. Conservação impressa no stdout. Valores fracionados by design |
| **Snapshot analítico anexado pelo renderer** | Python bloco `funil_atribuido_campanha_mes` no fim do `_render_monitor.py` | append ao `monitor.json` após o HTML | Produtor da visão = produtor do dado analítico (zero duplicação de motor entre gerador e renderer); wrapper roda gerar→render, o bloco sobrevive a toda rodada |
| **Semáforo de meta parametrizado** | JS `pctMeta()/stPct()` | thresholds do operador (Colina: ≥70% ok · 60–70 warn · <60 bad) | Métrica de CUSTO (CPMQL/CAC) usa conta **inversa** `meta/realizado` — o % exibido, a barra e o status |
| **Cohort 3 visões** (taxa · clientes · CAC da safra) | JS `SAFKEY/setSaf()`, `cohortConv()`, `rSafra()` | subtabs sobre o mesmo triângulo M0–Mn | CAC da safra = invest do mês ÷ clientes acumulados até M+k (cai com a maturação — esperado). **Tela ignora o filtro de período** (todas as safras; BU/canal aplicam) |

## Camada de metas e KPIs

| Componente | Identificadores | Contrato de dados | Notas / variação |
|---|---|---|---|
| **Meta pro-rata por vigência** | JS `metaPeriodo()`, `nDays()` | contrato: `periodo{inicio,fim}` + `metas` (volume: faturamento/clientes/investimento; taxa: ticket/roas/cac) | **Princípio**: volume pro-rateia por `dias(período∩vigência)/dias(vigência)` com tag "metas pro-rata: N de M dias"; taxa NÃO escala; sem interseção → meta some (esconder > mentir) |
| **Pacing** | JS `pr()` dentro de `rGeral()`; CSS `.proj` | `FILT`, `D.today` | Só período em andamento (contém hoje); projeta `real/dias decorridos × dias totais` vs meta pro-rata do range completo |
| Card OKR (big number + barra de meta + delta + pacing) | JS `card()` em `rGeral()`; CSS `.card.okr .big .bar` | `{meta, metaTxt, pct, st, sub, delta, proj}` | Status ok/warn/bad em 100%/80%; métricas "menor é melhor" (CAC) invertem via `st(...,false)` |
| KPI box compacto | JS `kb()`; CSS `.kbox` | label + número + subtexto + delta | Pra telas de apoio |
| Deltas de comparação ▲▼ | JS `delta()`, `cmpK()` | par de KPIs (atual, espelho) | Espelho: período/mês/ano anterior via `cmpRange()` |

## Camada de tabelas

| Componente | Identificadores | Contrato de dados | Notas / variação |
|---|---|---|---|
| Dim-table (win rate, faturamento c/ barra inline, share, ticket, ciclo) | JS `dimTable()`, `byDim()`, `wbar()` | lista `{k,total,win,lost,wr,fat,share,ticket,ciclo}` | **Faturamento = só ganhos**; rateio multi-valor `1/n`; ciclo = **mediana** |
| DRE transposta (métricas nas linhas, meses nas colunas) | JS `rMensal()`, `dreMes()`, `lin()/linM()`; CSS `.dre` | fatos mensais + `fee.por_mes` + `metaMes()` | Linhas de meta/budget pro-rata só quando `periodMeta()`; 1ª coluna sticky |
| Heatmap de cohort | JS `cohortBuild()`, `rRecompra()`; CSS `.heat` | ganhos com `li` (lead index) + `f` (frentes) | Safra = mês da 1ª compra; intensidade por taxa ou valor; base <5 omitida; filtrável por frente da 1ª compra (`FRSEL`) |
| Veredito 3 colunas (Cortar/Escalar/Investigar) | JS `col()/frCol()` em `rDecisao()`; CSS `.deccol .decitem` | linhas com `roas` + threshold `D.meta.roas` | Parametrizado por dimensão (canal, frente); cortar ROAS<1, escalar ≥meta |
| Pontos cegos de qualidade de dado | JS `rDecisao()` cards | contagens de campos vazios + `d.s` (canal×clickid divergente) | Threshold de alerta por card; detector de clickid cruzado é lição Martins |

## Camada de gráficos (Chart.js)

| Componente | Identificadores | Notas |
|---|---|---|
| Defaults dark + opções base | JS `cOpt()`, `COR`, `QPAL` | Grid `#26263a`, ticks `#8b8b9e` |
| Combo invest × faturamento empilhado × linha ROAS | `CH.g` em `drawCharts()` | Legenda `position:top,align:end`; `grace:"18%"` no y; card `chart-lg` (360–420px) — senão espreme |
| Volume aq×rc + linha de taxa | `CH.vg` | Mesmas regras de respiro |
| Funil vertical (volume e valor) | `CH.fvol/fval` | Datalabels com % do topo |
| Toggle Volume↔Receita | `FECHKEY`, `setFech()` em `rMensal()` | Mesmo chart, agregador `rec?g.v:1`; cor muda (verde volume, âmbar receita) |
| Datalabels | plugin por-chart: `plugins:[ChartDataLabels]` | **Nunca** global — polui todos os charts |

## Camada de dados (payload + backend)

| Componente | Identificadores | Notas / variação |
|---|---|---|
| Payload interned (strings em dicionário) | Python `_si()`, `STR/STRS`; JS `STRS` | 25k deals em ~3,5MB; sem isso o HTML explode |
| `DEALS` único filtrável no cliente | Python bloco DEALS; JS `dealsFilt()` | Uma estrutura alimenta todas as telas analíticas; PII nunca entra |
| Classificação aquisição×recompra | Python `por_lead/prim`; campo `e` | **Só blueprint aquisicao-recompra** — 1º ganho lifetime do lead = aquisição |
| Frente/linha de negócio | Python `classify_frente()`, `PROD2FR`, `CAMPFR`; JS `porFrenteRows()` | Campanha→frente por keyword (bi-frente rateia 50/50); deal→frente por funil de LP com fallback produto; **dimensão analítica, não filtro global** (invest só existe no grão mensal do drill) |
| Detector canal×clickid | Python flag `s` no DEALS | gclid em deal Meta / fbclid+ad_id 120… em deal Google |
| Contrato do projeto lido em runtime | Python `load_contrato()` | Metas/quarter/FEE/canais trocam sem tocar código; fallback gracioso se yaml faltar |
| Snapshot determinístico p/ análise | `_gerar-monitor.py` → `monitor.json` | Camada determinística produz, cognitiva consome (`monitor-contrato-snapshot.md`) |
| Reconciliação CRM×campanhas (resíduo ad_id) | Python `compute_resid()`; JS merge no `CAMP` via `RES` (exemplo sigo) | Excedente do CRM por mês×canal distribuído fracionado no grão dia×anúncio, proporcional ao próprio evento (fallback: share de invest) → drill/canais/séries/veredito reconciliam sem código extra. Bloco `resid` ADITIVO no monitor.json (camp.rows continuam cruas); só completa faltantes (nunca desconta supercontagem da origem); conservação no stdout; veredito arredonda frações |
| Vendas atribuídas por ad_id (receita limpa na mídia) | Python `ad_map`/`vend_rows`; JS `VEND`/`vendIn()` (exemplo sigo) | Ganho do CRM → criativo via ad_id, data do ganho, SEM rateio: faturamento com fórmula canônica (mens+impl) + MRR + ROAS no drill/canal — em vez do `total_value` cru da planilha de campanhas. Taxa de match no stdout |
| Detector de ganhos em lote | JS em `rAtencao` (exemplo sigo) | win_at concentrado num único dia (≥5 e >30% do período) = atualização em massa no CRM → card vermelho; séries ficam distorcidas — sinalizar, não esconder |

## Camada de UX e telas analíticas (lições Sigo v5, 2026-07-02 — exemplo: `exemplos/sigo/`)

| Componente | Identificadores no exemplo sigo | Contrato de dados | Notas / variação |
|---|---|---|---|
| **Tela Qualificadores** ("quem converte melhor?") | JS `rQuals()`, `qualAgg()`, `qualEvo()`, `sdrAgg()`; Python `qual_norm()`; contrato `qualificadores{campos,normalizacao}` | qualificadores do CRM interned no lead row; normalização de variantes no CONTRATO (editável sem código) | Funil fatiado por resposta do form c/ heatmap por coluna + subtabs por dimensão + evolução mensal + funil por SDR. Só dimensões com fill relevante viram tela; campo 100% vazio vira ponto cego na Atenção |
| KPI-card 3 camadas de contexto | JS `okrCard` c/ `sparkSeries()`/`drawSpark()` | série semanal 8 sem da métrica | Δ vs espelho + meta bullet + sparkline — "é bom?" respondido no próprio card |
| Sales velocity | JS `velocityCard()` | SQL, win-rate, ticket, ciclo mediano 180d | Nº único de momentum (R$/dia), board-level |
| Top-N expansível | JS `expWrap()`/`togExp()`; CSS `.expbtn` | qualquer lista de linhas | Progressive disclosure: tabela abre top-10, botão expande; estado `EXP` sobrevive re-render |
| Rótulo no último ponto (linhas) | JS `lastDL()` | — | Datalabel em todo ponto de linha = ruído; último ponto + tooltip cobre. Stacked: total no dataset do topo |
| Pergunta da tela (decision-first) | CSS `.qask` no `<h2>` | — | Cada tela declara a pergunta que responde ("estou no ritmo?", "o que precisa de ação?") |

## Regras transversais (valem pra qualquer monitor)

1. PII **nunca** no HTML/JSON; artefatos git-ignored quando embutem dado de CRM.
2. Single-file: CSS/JS inline, só Chart.js via CDN; abre com duplo-clique e publica no Cloudflare Pages.
3. Meta só aparece no recorte que ela mede (`periodMeta()` + vigência) — nunca meta cheia contra recorte parcial.
4. Toda agregação por dimensão soma **só ganhos** e usa rateio `1/n` em multi-valor.
5. Convenções do feed se observam nos CSVs reais (datas BR, vírgula decimal), nunca se assumem.
6. **Nunca estilizar `<canvas>` via CSS** (quebra o responsive do Chart.js) — sizing pelo container (`.chwrap` + `maintainAspectRatio:false`); e chart criado em aba oculta precisa de `c.resize()` no handler de troca de aba (lição Sigo v5).
6. **Cozinha não vai pro cliente**: metodologia (atribuição, rateio, premissa) vive em comentário Python — nunca em nota no HTML nem em comentário JS do template (viaja no view-source do publicado).
7. **Métrica impossível** (ex. cliques > impressões na origem) → exibir "—" e reportar ao dono do dado; nunca imprimir o número.
8. **Telas de referência** (safra/cohort, série mensal/DRE) ignoram o filtro de período (mostrar tudo > recortar histórico); filtros de segmento/canal aplicam. **Medianas de tempo** (ciclo, entre-etapas) em janela FIXA (ex. 180d vs 180d anteriores) — recorte curto engana.
9. Charts multi-métrica por dimensão com escalas díspares → **mini-charts horizontais, 1 métrica/escala cada** (grid `g3` + `.chart-sm`); grid+Chart.js exige `.grid>*{min-width:0}` e `canvas{max-width:100%}`.
