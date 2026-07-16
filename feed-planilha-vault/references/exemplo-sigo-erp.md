# Exemplo canônico — Sigo ERP (dados-fonte 2.0, 2026-07-09)

Caso vivo completo da camada de extração+orquestração. Use como referência de "como fica um setup 2.0 completo". **Não copie IDs/paths/abas** — são deste projeto; cada feed novo passa pelo Passo 0.

**Pasta:** `...\01_assessoria\Sigo ERP\90-referencias\dados-fonte\`
**Decisão-mãe:** `30-decisoes/2026-07-09-dados-fonte-v2.md`

## Parâmetros

| Campo | Valor |
|---|---|
| Planilha | `1zSuWNzxkB6panHHEdZmHMFg9Asm43NVjK-dj4nQ-DNs` (pública) — 5 abas via `/export?gid=` |
| Abas → raw/ | `bd_ads`→campanhas · `bd_campaing_index`→index-anuncios · `leads_pipeline`→crm (PII) · `leads`→leads (PII, MinBytes=100 — aba em população) · `bd_gads_terms`→termos-google |
| Flow (MCP) | projeto `rthhpf8lb5n2scrlgiowz2et` · Meta `act_826565024135443` · Google `8360288373` — 10 extrações às segundas 07:00 |
| Cadeia | extract → transform → render → publish (Cloudflare `sigo-monitor.pages.dev`) — em `_atualizar-dados.ps1` |
| Notify | grupo "Gestão de Performance" via Evolution API (instância `robson-pessoal`), diário 08:00 |
| Tarefas | `Sigo ERP - Dados Fonte` (07:30+17:30) · `Sigo ERP - Flow Semanal` (seg 07:00) · `Sigo ERP - Report WhatsApp` (08:00) |

## Git-ignored (PII e artefatos)

```
raw/crm-completo.csv · raw/leads-completo.csv        # PII de leads/deals
monitor.html · monitor.json                           # payload carrega CRM analítico
_download.log · _flow.log · _notify-state.json · _dist/ · .wrangler/
```

## Nota histórica (v1, 2026-06-26)

O feed nasceu como "planilha→CSV solto na pasta" (2 abas, 1 tarefa 09:00). O caso v1 deixou as regras R7 (13 colunas formatadas como Porcentagem corrompendo phone/timestamps/ids — correção é **na planilha**, formato da célula, nunca no CSV) e R9/R10 (WebClient timeout 100s → curl; gviz truncando aba com fórmula → export?gid). Em 2026-07-09 o vault migrou pro 2.0 (estrutura `raw/`+cadeia); o `_atualizar-dados.ps1` do Sigo é o orquestrador-modelo **dos estágios da cadeia**.

> ⚠️ **O estágio extract do Sigo é legado pré-motor-genérico:** os `$Targets` são hardcoded no próprio `.ps1` (não usa `_feed-download.ps1`+`feed-config.json` do Passo 3) e **não tem o fallback R11** (export→gviz automático). Setup NOVO usa o motor genérico da skill; o Sigo demonstra a cadeia (estágios/travas/gotchas), não o Passo 3. Retrofit do extract do Sigo = pendência registrada.

## Gotchas que viraram regra (ver regras-aplicadas.md)

- Monitor 2 dias parado por stderr benigno → **R12** (`cmd /c` + exit code).
- Deploy morto por cwd=System32 → **R13** (Push-Location).
- Saldo de conta é snapshot → **R14** (APPEND histórico).
- Sessão MCP resetando no gateway → **R15** (cliente stdlib inicializa por rodada).
- 1º report rejeitado pelo operador → **R16** (bloco compacto multi-projeto).
