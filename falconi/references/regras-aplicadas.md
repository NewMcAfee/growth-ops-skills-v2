# Regras aplicadas — estado da arte operacionalizado

Práticas **validadas** do benchmarking (Módulo 2 da criação), transformadas em regra concreta. Não são citações decorativas: cada uma é um comportamento exigido da `falconi`. Para a lógica de cada, ver `metodo.md` e `catalogo-causas.md`.

| # | Prática validada | Fonte | Regra na `falconi` |
|---|---|---|---|
| 1 | **MASP/QC-Story** — 8 fases (Identificação→Observação→Análise→Plano→Ação→Verificação→Padronização→Conclusão), ferramenta por fase (Pareto, Ishikawa, 5 porquês, 5W2H) | Falconi/Campos (TQC, 1992); melhorianapratica.com.br | O workflow **é** as fases de diagnóstico do MASP; Verificação/Padronização viram o **Loop** (fase 5) + `aprendizados/`. |
| 2 | **Metric tree = five-whys visual** — recursar a árvore pré-construída; checar temporal/component/influence/dimension/external | Levers Labs; Mixpanel (2024–25) | Estratificação recursa a árvore MECE e **checa as 4 fontes de variância** antes de declarar o agressor. |
| 3 | **Issue tree MECE** (cobertura) + **driver tree** (quantifica contribuição) | McKinsey/MECE; casebasix | A árvore cobre o **funil inteiro** (não só mídia) e usa **contribution analysis** para escolher o agressor por contribuição absoluta. |
| 4 | **Benchmarks de funil B2B SaaS** + diagnostic rules por etapa (MQL→SQL <15% → lead scoring + follow-up; win <25% → qualificação/proposta) | The Digital Bloom; Domestique (2025) | `catalogo-causas.md` traz **red flags + causas prováveis por etapa**; o baseline do próprio cliente prevalece sobre a média de indústria. |
| 5 | **Correlação ≠ causação** — confounders, reverse causality, last-touch não é causal | DataCamp; incrmntal | Toda causa exige **evidência além da correlação**; rótulo [confirmada\|hipótese]; **nunca** concluir de last-touch/co-ocorrência. |
| 6 | **Cohort vs calendar** — agregação por calendário mascara efeitos de ciclo de vida/coorte | Levchuk, "The Metric Tree Trap"; Northbeam | **Meta em calendário, atribuição em safra.** Volume via flag, timing via `_at`; respeitar lag de ciclo. |
| 7 | **Weekly Business Review** — action items carry forward (accountability loop); 60% leading / 40% lagging | Fishman (WBR); Reforge | O **Loop** reconcilia hipóteses do ciclo anterior; ações abertas **carregam**; diagnóstico mistura indicadores leading e lagging. |
| 8 | **"Confident wrong"** — agentes/LLM entregam alucinação com a mesma confiança de fato; falha é system-level | InsightFinder; arXiv 2509.18970 (2025) | Separar **fato de hipótese** é inegociável; toda afirmação ancora num **dado citado**; ausência = "indisponível", não causa. |
| 9 | **Impacto ≠ prioridade** — elasticidade alta não garante ROI; custo importa | "The Metric Tree Trap" | Priorizar 5W2H por **ICE** (impacto × confiança × esforço), não pelo tamanho do gap. |

## Diferencial (o que nenhuma referência costura)

O estado da arte tem cada peça **isolada**: consultoria tem issue tree; RevOps tem benchmarks de funil; observability tem RCA de causa; growth tem ritual de review. **Nenhuma** costura número → causa-com-evidência-**qualitativa** → ação 5W2H **roteada a executores** num diagnóstico de sprint recorrente. A `falconi` preenche isso porque **vive no vault**: lê o snapshot determinístico, cruza com CRM/calls/mensagens para confirmar causa, e roteia para as skills donas — em vez de parar na correlação ou na lista de hipóteses.
