# Extração de warehouse flow via MCP JSON-RPC (stdlib, zero-Claude)

> Como extrair dados de um warehouse exposto por MCP (flow/Nekt via gateway, ex.
> `flow_media_query`) num script Python puro agendado — sem sessão de Claude na
> cadeia. Modelo vivo: `_extrair-flow.py` do vault Sigo ERP.

## Por que um cliente próprio (e não o harness MCP)

O harness só existe dentro de uma sessão; a cadeia é zero-Claude. E o gateway derruba sessões MCP (proxy reinicia → "missing mcp-session-id") sem re-inicializar — um cliente próprio **inicializa a própria sessão a cada rodada** e o problema desaparece.

## O cliente (streamable HTTP, stdlib pura)

Padrão da classe `Flow` (clonar do exemplo Sigo):
1. **Credenciais da fonte canônica** — `~/.claude.json → mcpServers.<nome>` (`url` + `headers`). Nunca copiar token pro script.
2. **Handshake**: POST `initialize` (protocolVersion `2025-03-26`) → guardar o header `Mcp-Session-Id` da resposta → POST `notifications/initialized`. Sem session-id devolvido = erro, aborta.
3. **Toda chamada** repassa `Mcp-Session-Id`; resposta pode vir `text/event-stream` → parsear linhas `data:` e usar a **última**.
4. **`tools/call`** com a tool de query do gateway; o resultado útil vem em `result.content[0].text` (JSON string → `data.rows`).
5. **Paginação** `LIMIT/OFFSET` (página ~5000) — o SQL **precisa de ORDER BY estável**, senão páginas se sobrepõem.

## Gotchas do warehouse via gateway (todos empíricos, Sigo 2026-07-09)

| Gotcha | Sintoma | Contorno |
|---|---|---|
| `date_start` é **STRING** | `FORMAT_DATE` explode | `SUBSTR(date_start,1,7)` pra mês; `SUBSTR(CAST(date AS STRING),1,10)` no Google |
| Google usa naming **GAQL** | `impressions` não existe | `metrics_impressions`, `metrics_clicks`, `metrics_cost_micros` (÷1e6), `metrics_conversions` |
| **UNNEST bloqueado** pelo allowlist | coluna ARRAY (ex. `actions` do Meta) inacessível | lacuna aceita e declarada no contrato — breakdowns Meta só custo/volume; conversão por dimensão só onde é coluna plana (Google) |
| **INFORMATION_SCHEMA bloqueado** | não dá pra listar colunas | descoberta por tentativa — o erro do gateway sugere nomes de coluna próximos |
| UNION ALL multi-linha **trunca** | query corta silenciosa | subselects numa linha só; preferir 1 extração por arquivo |
| Sessão MCP reseta (proxy 502) | "missing mcp-session-id" | cliente inicializa a própria sessão por rodada (ver acima) |
| CSVs do warehouse usam **ponto decimal** | parser BR lê `2.0` como `20` | consumidores usam `float()` puro nesses arquivos (não `br_num`) |
| Console agendado é **cp1252** | emoji/seta quebra o script | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` + sem emoji no log |

## Escrita em raw/ (mesmas travas do feed)

- **Sobrescrita com trava**: `min_rows` por extração + novo ≥ 50% das linhas do atual + `.tmp` → `replace` atômico. Fonte com erro **nunca destrói dado bom** — loga WARN e mantém.
- **APPEND para fontes-snapshot** (R14): fonte que só tem o estado atual (ex. saldo de conta) vira **histórico local** — append com coluna `data`, header só na criação. É a única exceção ao padrão sobrescrever.
- **Semântica de saldo** (declarar no `config-financeiro.yml`, não no script): Meta pós-paga → `balance`/100 = consumido não faturado; Google pré-paga → (`adjusted_spending_limit_micros` − `amount_served_micros`)/1e6 = o que resta.
- Exit code: 0 = tudo OK; 1 = houve falha (a tarefa agendada expõe via `LastTaskResult`).

## Cadência e agendamento

Extração semanal **às segundas, ANTES do feed diário** (ex. 07:00 vs feed 07:30) — a semana começa com dado fresco e a cadeia diária consome o que estiver em `raw/`.

## O que extrair (cardápio validado — grão DIA + ad_id desde 2026-07-10)

Dims (**commitáveis**): ads (ad_id→nomes/creative_id) · criativos (title/body/CTA/image_hash) · imagens (hash→URL CDN — URLs renovam a cada extração) · **geotargets Google** (dim manual: CSV oficial de `developers.google.com/google-ads/api/data/geotargets` filtrado pro país — o extrator resolve `geoTargetConstants/NNN`→nome no geo Google, preservando `*_id`; sem a dim, ids crus + WARN).
Fatos Meta (**dia × ad_id — git-ignored**, volume; reproduzíveis do warehouse): geo por região · demo idade×gênero · device · hora do dia (ad_id + campaign_name).
Fatos Google (**dia, com conversões — git-ignored**): keywords (campanha id+nome × grupo id+nome × keyword × match — **cruzamento com mídia por CONJUNTO/ad_group**; keyword não tem ad_id) · geo (campanha id+nome × região × cidade — **API não desce de campanha**, sondado).
Snapshot→histórico (**commitável** — o histórico só existe local!): saldo por conta (APPEND).
Sem stream: demografia Google (lacuna declarada no contrato).

**Consumidor mensal agrega client-side:** o render-prep do monitor (load_brk) agrega dia→mês pro payload (`mes = data[:7]`, tolerando arquivos legados mensais) — o grão dia fica no raw pra análise; o payload do monitor não incha.
