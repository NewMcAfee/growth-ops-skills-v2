# Referência — Monitor Sigo ERP (cockpit SaaS B2B recorrente)

Exemplo canônico do blueprint **`recorrencia`** (SaaS com funil demo/SDR, safra de
mensalidade, DRE de payback). Foi o **1º monitor do padrão** (jun/2026) e recebeu
**retrofit completo em 2026-07-02** pro estado-da-arte do catálogo (Martins re-sync +
lições Colina) — o visual/filtros/metas agora seguem o mesmo padrão dos demais exemplos.

## Arquivos (código real, pronto pra clonar)

| Arquivo | O que é |
|---|---|
| `_render_monitor.py` | Cockpit 8 telas (Visão Geral OKR · KPIs · Decisão · Funil & Qualidade · Safra · Mídia · Mensal/DRE · Segmentos), filtros Google-Ads-style, metas client-side por vigência. |
| `_gerar-monitor.py` | Payload interned sem PII + `monitor.json` p/ skills de análise + OKR da vigência + **reconciliação CRM×campanhas** (resíduo do join ad_id). |
| `contrato-cockpit.yml` | Funil (MQL=SAL), metas OKR c/ `quarter_vigencia`, `canais_meta`, TCV recorrente (6×mens+impl). |
| `config-financeiro.csv` | FEE/margem/tcv_meses por mês (DRE de payback). |

> **v5 (2026-07-02, mesma data — revisão geral aprovada pelo operador):** IA de 7 telas
> decision-first (cada tela declara a pergunta que responde no subtítulo — `.qask`),
> tela KPIs-wall e Segmentos MORTAS (conteúdo redistribuído), tela **Atenção**
> (pontos cegos + reconciliação campanhas×CRM + veredito) e tela **Qualificadores**
> nova (ver §componentes abaixo).

## O que este exemplo demonstra (e os outros não)

1. **Backend `recorrencia`** — safra de mensalidade (MRR persiste), triângulo de maturação M0–Mn com métrica trocável, DRE de competência + payback acumulado, TCV só no DRE (6× mensalidade + implementação; nas demais abas faturamento = 1 mensalidade + impl).
2. **Metas client-side com vigência** (`metaPeriodo()` + `periodMeta()` + `pacing()`) — placar OKR reage a período+canal; pro-rata por `dias(período∩vigência)/dias(vigência)` com tag visível; taxas não escalam; fora da vigência a meta some. **Virada de quarter não trava o feed** — o gerador segue regenerando e só o placar reage.
3. **`canais_meta: null`** — variante em que a meta é da OPERAÇÃO (todos os canais), não só da mídia paga: o gate `periodMeta()` vira `allCh()`.
4. **Reconciliação CRM×campanhas no grão dia×anúncio** — excedente de eventos do CRM sobre o campanhas (leads sem match de ad_id) distribuído fracionado por mês×canal proporcional ao próprio evento (fallback: share de invest). Merge no `CAMP` do JS → drill/canais/séries/veredito reconciliam sem código extra. Bloco `resid` é ADITIVO no monitor.json (camp.rows continuam cruas). Conservação no stdout. Só volume — valor não se reconcilia (fórmulas divergem). Veredito arredonda cli/dre (fração de resíduo não vira evento real).
5. **Velocidade do funil** em janela fixa 180d vs 180d anteriores (mediana, Δ de tendência) — não reage ao filtro de período.
6. **OKR no monitor.json mede a VIGÊNCIA** (não o quarter civil) — semântica estável pra skills consumidoras (falconi/growth-review).
7. **Tela Qualificadores** (`rQuals` + `qualAgg`/`qualEvo`/`sdrAgg` + bloco `qualificadores` no contrato): funil fatiado pelas respostas do form (heatmap por coluna), subtabs por dimensão, evolução mensal stacked, **funil por SDR** (SAL→agendamento por pessoa — localizou o gargalo da fila genérica no 1º render). Normalização de valores no contrato (`qualificadores.normalizacao`), não no código.
8. **KPI-card 3 camadas de contexto** (Δ + meta bullet + **sparkline 8 semanas** — `drawSpark`/`sparkSeries`) e **sales velocity** (`velocityCard`: SQL × win-rate × ticket ÷ ciclo mediano).
9. **Top-N expansível** (`expWrap`/`togExp`) nas tabelas de drill/termos — progressive disclosure; **rótulo em todo chart** (`lastDL` = valor no último ponto das linhas; total no topo de stacked).
10. **Termos com impression share** (Impr. Top % ponderado por impressões) — headroom de escala; **frequência aproximada** (impr÷alcance) no drill como proxy de fadiga.
11. **Vendas atribuídas por ad_id** (`ad_map`/`VEND`, v5.1): ganho do CRM ligado ao criativo → faturamento LIMPO (mens+impl), MRR e ROAS no grão de mídia (canal/campanha/conjunto/anúncio), pela data do ganho, sem rateio (match 178/181 no Sigo). Substitui o `total_value` cru do lado-campanha nas visões de resultado.
12. **Detector de ganhos em lote** (`rAtencao`): win_at concentrado num único dia (≥5 e >30% do período) = atualização em massa no CRM → card vermelho na Atenção (no Sigo: 26 ganhos em 24/06 inflaram junho — o monitor mostra fiel e SINALIZA, não esconde).
13. **Gotcha subtabs**: dois grupos de subtabs com a MESMA classe → o bind genérico `querySelectorAll('.stbtn')` sobrescreve o onclick inline do segundo grupo. Bind só em `.stbtn[data-st]`.

## Gotchas (não repetir)

- **PS 5.1 + stderr do python**: `& $py $gen 2>&1` com `ErrorActionPreference=Stop` converte QUALQUER linha de stderr em exceção — um WARN benigno derrubou o render por 2 dias na virada Q2→Q3. Rodar via `cmd /c "python ... 2>&1"` e decidir sucesso pelo exit code; WARNs informativos do gerador vão pra STDOUT.
- **Console do feed é cp1252**: não printar `→` (UnicodeEncodeError); usar ASCII/`·`.
- **Origem pode SUPERCONTAR**: campanhas do Sigo tem mais demos que o CRM (linhas de placement duplicam evento). Reconciliação só completa faltantes, nunca desconta — a nota da UI diz "se aproximam do CRM", não "batem"; divergência monitorada na conservação do stdout e reportada à origem.
- **Meta mensal no DRE** só nos meses da vigência (`inVig()`) — mostrar meta contra mês fora da vigência mente.
- **NÃO estilizar `<canvas>` via CSS** (`canvas{max-width:100%}` global quebrou o responsive — docs do Chart.js avisam); sizing vem do container (`.chwrap{position:relative;height:...}` + `maintainAspectRatio:false`).
- **Chart criado em aba `display:none` fica no tamanho fallback** e o ResizeObserver não corrige sozinho na troca de aba → no handler das tabs, `requestAnimationFrame(()=>Object.values(CH).forEach(c=>c.resize()))`. (Só apareceu quando o cPipe migrou da Visão Geral — visível no boot — pra aba Funil.)
