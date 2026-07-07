# Referência — Monitor Martins Locações (cockpit estado-da-arte)

Exemplo canônico da biblioteca do **Modo Monitor/Cockpit** (SKILL.md §11). Construído 2026-06-30; **re-sync 2026-07-02** com: metas pro-rata por vigência + pacing (`metaPeriodo()`, `pr()`), frente de negócio (invest×retorno na Mídia + veredito na Atenção + cohort filtrável), detector canal×clickid, toggle Volume↔Receita no Mensal, metas no DRE, charts `chart-lg`. Antes de clonar, leia o **catálogo de componentes** (`../../monitor-biblioteca.md`) e o **blueprint** do modelo de negócio do cliente (`../../blueprints/`).

## Arquivos (código real, pronto pra clonar)

| Arquivo | O que é |
|---|---|
| `_render_monitor.py` | **O coração** — gera o `monitor.html` (cockpit auto-contido, 7 telas). Lê os CSVs do feed + `contrato-cockpit.yml`, embute `DEALS` (dados granulares) e renderiza todas as telas + filtros no cliente. ~1.300 linhas, JS inline. |
| `_gerar-monitor.py` | Snapshot determinístico — emite `monitor.json` (KRs + breakdowns agregados, sem PII) p/ skills de análise consumirem. Roda antes do render. |
| `contrato-cockpit.yml` | Parametrização: metas OKR, `canais_meta` (canais que contam pra meta), FEE mensal, período. Trocar quarter/metas = editar só aqui. |

## Pipeline (no vault do cliente)

`feed (feed-planilha-vault) → _gerar-monitor.py (json) → _render_monitor.py (html) → deploy Cloudflare Pages`, encadeado num wrapper `.ps1` agendado 2×/dia.

## Decisões de design que valeram (replicar)

1. **`DEALS` único filtrável no cliente** — uma estrutura (registros do CRM, strings em dicionário p/ compactar) alimenta todas as telas; o filtro período+canal roda no JS. Evita N fontes desencontradas.
2. **Filtros estilo Google Ads** — date-range com presets + calendário + comparação (Mês/Ano/Período anterior) gerando deltas ▲▼ nos cards. UX que o gestor já conhece.
3. **Telas que contam a história** — Visão Geral (resultado) → Atenção (o que está furado: pontos cegos de dado + veredito) → Funil/Recompra/Mídia/Produtos (drill) → Mensal (DRE + fechamentos). 
4. **Meta condicional + vigência** — KRs só aparecem com barra/meta quando o filtro = canais-meta (mídia paga); metas de volume pro-rateiam por `dias(período ∩ vigência)/dias(vigência)` com tag visível; taxas não escalam; fora da vigência a meta some (esconder > mentir). Pacing projeta o fim do período em andamento.
4b. **Frente de negócio como dimensão analítica, não filtro global** — investimento (campanha→frente por keyword, rateio bi-frente) só existe no grão mensal do drill; um filtro global de frente mentiria no lado do invest diário. Por isso frente vive em tabelas/vereditos/cohort, não na filterbar.
5. **DRE transposta** (métricas nas linhas, meses nas colunas) com header destacado e 1ª coluna fixa — lê como o Excel do cliente.

## Gotchas (não repetir os erros)

- **Chart.js datalabels** = plugin separado (`chartjs-plugin-datalabels` via CDN), passado `plugins:[ChartDataLabels]` **por-chart** (não global, senão polui todos).
- **Popup do filtro fecha sozinho:** o listener "clicou fora → fecha" dispara no re-render (o elemento clicado sai do DOM). Resolver com `onclick="event.stopPropagation()"` no `.pop`.
- **Faturamento por dimensão** (produto/origem/canal): somar **só os ganhos** (`win`), não todos os deals — senão perdidos com valor alto inflam o ticket.
- **Rateio de produto** multi-item: separador `;`, valor ÷ nº de produtos.
- **Ciclo** = **mediana** (não média) de dias entre criação e fechamento das ganhas.
- HTML fica grande (~3 MB com 25k deals embutidos) — aceitável; se precisar enxugar, pré-agregar parte.

## Publicação

Cloudflare Pages — ver memória global `publicar-monitor-cloudflare-pages` (token no settings.json, deploy no wrapper, gotcha do `wrangler login` no Windows).
