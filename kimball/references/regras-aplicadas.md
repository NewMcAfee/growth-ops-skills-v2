# Regras Aplicadas — kimball

Práticas validadas do estado da arte (pesquisa 2020-2026) operacionalizadas como regras concretas do motor. Cada linha: prática → evidência/fonte → como o `kimball` aplica. Consulte ao calibrar thresholds ou justificar uma decisão de desenho.

## A. Resolução de identidade (record linkage)

| Prática validada | Evidência / fonte | → Regra concreta no kimball |
|---|---|---|
| Fellegi-Sunter: peso de match por raridade do campo (m/u), aditivo | Robin Linacre, maths of Fellegi-Sunter; pesos ~-30..+30 | Chave rara/discriminante (email) = aresta forte; nome comum = fraco. `resolve_identity` une só por chave forte exata. |
| Match exato sozinho perde 30-40% das duplicatas | Cognism; digitalapplied 2026 | Normalização determinística **antes** do match (email canônico, E.164) recupera variação de formatação sem fuzzy arriscado. |
| Transitividade via connected components (union-find) | Science Advances "(Almost) all of ER" 2021 | `UnionFind` agrupa clusters; MAS só propaga em aresta forte (email/tel exato), nunca em match fraco. |
| Over-merging por 1 aresta falsa funde 2 clusters legítimos | JDIQ cluster repair 2024 | **Hard-conflict**: telefone igual + 2 emails canônicos distintos → NÃO une (bloqueia + conta no report). |
| Telefone/email compartilhado (recepção, info@) funde pessoas distintas | GOV.UK QA in data linkage | Telefone ligado a ≥`shared_phone_min` emails = compartilhado (não-chave). Email role-based (`contato@`,`sac@`…) nunca é chave. |
| Auto-merge só em tier alto; 0.6-0.95 vai a review | digitalapplied 2026 (tiers 0.95/0.80/0.60) | União automática só em match exato (=1.0). Sinais fracos ficariam como sugestão, nunca merge automático. |
| Survivorship por atributo, não por registro | Data Ladder golden record | `survivorship()` escolhe valor vencedor **por campo** (completude→recência), coalesce do cluster. |

## B. Normalização (boundary hardening)

| Prática validada | Evidência / fonte | → Regra concreta |
|---|---|---|
| Email: dots/+tag são **provider-específicos** (só Gmail) | UserCheck; email-normalize; Artsy | `n_email` remove dots/+tag SÓ em gmail/googlemail; demais providers preservam. Aplicar global = over-merge. |
| Email role-based causa account confusion | UserCheck | `n_email` retorna flag `is_role_based`; excluído como chave de identidade. |
| Telefone → E.164 via libphonenumber, com região default | Toast eng; E.164 máx 15 díg | `n_phone` usa `phonenumbers` se disponível, fallback BR determinístico; região configurável. |
| IDs grandes perdem precisão em float (>15-16 díg) | pyodbc #753; SQLServerCentral | Todo CSV lido com `dtype=str`; IDs nunca numéricos. |
| Número localizado: pt-BR vírgula-decimal vs en-US oposto | John D. Cook 2025 | `to_num` parseia por **locale declarado por fonte**, não inferido linha-a-linha. |
| Data ambígua exige formato declarado | DAMA validity | `to_iso` usa `date_format` da fonte; normaliza tudo pra ISO-8601. |

## C. Modelagem dimensional (Kimball)

| Prática validada | Evidência / fonte | → Regra concreta |
|---|---|---|
| Declarar o grão antes de dimensões/fatos; erro nº1 é grão errado | Kimball Group; Cube.dev | Grão de mídia declarado = `ad×dia` (atômico). Config força o grão; agregação preserva-o. |
| Grão atômico (mais fino) para flexibilidade de re-agregação | AYC Data Kimball 10 tips | Nunca `campanha×mês`. Métricas brutas por ad×dia; re-agrega on-demand. |
| Sub-dimensão (search-term) não soma ao total da campanha | Google Ads Help; Mirach | `aggregate_no_fanout` colapsa search-term→ad×dia e **assert `SUM` pré==pós**. |
| Funil = accumulating snapshot separado do fato de mídia | Kimball; Holistics 3 fact types | `leads_master` = 1 linha/lead com marcos; NÃO colapsado no fato ad×dia. |
| Só átomos aditivos persistidos; KPI = SUM/SUM on-demand | dbt semantic layer; AtScale | Motor nunca grava CTR/CPL/ROAS. Razão calculada no consumo. |
| Receita no grão de deal, não pipeline blended | House of MarTech | `deals` traz valor por deal; `valor_ganho` = soma dos won no grão de deal. |

## D. Qualidade de dados (DAMA) e output

| Prática validada | Evidência / fonte | → Regra concreta |
|---|---|---|
| 6 dimensões: completeness, uniqueness, validity, accuracy, consistency, timeliness | DAMA UK; IBM | `qa_check` emite check binário com threshold por dimensão. |
| Coluna com fill-rate baixo é "morta"; não usar como join/marco | DAMA completeness | `is_dead_column` (fill<50% OU valor único) alerta antes de usar stage como marco. |
| Threshold explícito por check; PASS/WARN/FAIL | DAMA-DMBOK | Completeness ≥99% em joins; uniqueness=100%; accuracy=join integrity. |
| Precision/recall + false-match/false-non-match, não F-measure sozinho | GOV.UK QA | Report expõe uniões bloqueadas (proxy de false-match evitado) e órfãos (proxy de recall). |
| Tidy data: 1 variável/coluna, 1 observação/linha, 1 unidade/tabela | Wickham, R4DS 2e | Output long-format, fato de mídia e funil em tabelas distintas. |

## Síntese dupla (Módulo 3.3 GOD)

O `kimball` **INCORPORA** [Fellegi-Sunter com union-find guardado + normalização provider-específica + grão atômico Kimball com invariante não-fan-out + QA DAMA com threshold binário + tidy data] **E PREENCHE** [a lacuna do crosswalk closed-loop lead→contato→deal→campanha parametrizável por cliente, que Splink/dedupe (só dedup), paid-media-ingestor (só mídia) e newton/darwin (só análise) não fazem], porque **o valor de negócio está no elo fim-a-fim entre gasto e receita — e esse elo, com resolução de identidade segura e QA que denuncia armadilhas (coluna morta, fan-out, over-merge), é exatamente o que nenhuma ferramenta isolada entrega**.
