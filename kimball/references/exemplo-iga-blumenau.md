# Exemplo end-to-end — IGA Blumenau (caso-gatilho)

Caso real que originou a skill (assessoria V4, escola de gastronomia, jun/2025–jul/2026). Serve como **referência de números esperados e armadilhas** — NÃO é lógica hardcoded; o motor lê tudo do config. Valores em R$ foram arredondados/fictícios pra publicação (contagens de linhas são reais). Reproduza com `assets/config.example.yml` (que espelha este stack).

## Stack de origem
- **Mídia**: Meta Ads, Google Ads (Search + PMax) — exports por ad×dia (Search vinha por search-term).
- **Leads**: `todos_leads` (backup de tráfego pago antes do CRM, sem UTM, com duplicados) + `leads_meta` (form nativo Meta, tem ad_id).
- **CRM**: HubSpot — `contatos` (contact_id) + `deals` (valor/stage).

## Armadilhas encontradas (viraram regra na skill)
1. **Coluna de status morta**: `É negócio fechado` = 100% FALSE. Ganho real em `Etapa do negócio = "Venda Realizada"` (209) vs `"Venda Perdida"` (741). Confiar na flag → reportaria **0 vendas**. → `is_dead_column` alerta isso.
2. **Prefixos de plataforma**: `campanhas_meta` usa Ad ID puro; `leads_meta` usa `ag:...` e phone `p:+55...`. Sem strip, **0 matches**. → `strip_id`/`n_phone`.
3. **Grão de search-term**: `campanhas_google_search` tinha 10.376 linhas / 8 ad_ids (uma linha por termo/dia). Somar ao total infla custo. → `aggregate_no_fanout` (10.377→516, invariante OK).
4. **Número PT-BR**: valores tipo `242,39`, `45,3` (vírgula decimal). → `to_num(locale="pt-BR")`.
5. **Telefone em formato misto** no CRM (`5547...` e `47 99648-0916`). → `n_phone` E.164.
6. **Platform vazia** em todos_leads (0% preenchida) → canal vem 100% do cruzamento.

## Números esperados (motor genérico, com guards da pesquisa)
| Métrica | Valor |
|---|---|
| campanhas_consolidada | 2.747 linhas (meta 2.072 · google_search 516 · pmax 159) |
| spend total | ~R$ 30 mil · 110 ad_ids |
| todos_leads bruto → únicos | 1.589 → 1.232 (357 colapsados) |
| uniões bloqueadas (hard-conflict) | 14 (telefone igual, emails distintos — over-merge evitado) |
| match platform_leads (paid_meta) | 496 / 1.232 |
| match contatos (contact_id) | 1.028 / 1.232 |
| deals: ganho / perdido | 39 / 337 · valor ganho ~R$ 25 mil |
| deals_higienizados / ganhos | 2.443 / 209 (~R$ 120 mil total no CRM) |
| atribuição (utm_source) | paid_meta 998 · paid_google 126 · indefinido 104 · paid_outro 4 |
| attribution_source | platform_match 496 · deals_utm 622 · lead_name 10 · none 104 |
| QA | todos PASS · join integrity ad_id 100% |

## Nota de atribuição (bloco `attribution`)
O lado Google não tem ad_id na origem. O canal é recuperado por precedência (match plataforma → UTM do deal → nome de campanha → default) com regex declaradas no config (`SEARCH|PMAX` → google; `\bABO\b|\bCBO\b|\bLKL\b|META` → meta — padrão de nomes V4). **Regex em YAML exige aspas simples** (`'\bABO\b'`): aspas duplas viram backspace `\x08` e não casam. O motor auto-cura (`\x08`→`\b`), mas o exemplo já vem correto.

> Diferença vs script manual original (1.220 únicos, 38 ganhos): os **guards anti-over-merge + normalização E.164/canônica** do motor genérico são mais corretos — não fundem os 14 hard-conflicts e casam mais por telefone normalizado. Números maiores aqui = menos over-merge, não bug.

## Insight de negócio que emergiu
Ganhos rastreados ao tráfego pago (~R$ 25k / 39 leads) ≠ ganhos totais do CRM (~R$ 120k / 209). O delta são vendas de fontes fora do pago rastreável — e esse gap é material para o diagnóstico (é trabalho de `newton`/`falconi`, não do kimball).
