# Schema F1-21b — Forecasting (versão completa)

> Reference canônica do schema do output `forecasting.md` produzido pelo `sobral` v2.0.0 (Fase B). Espelha o catálogo formal `arquitetura/schemas/fase-1/forecasting.md` (B7.1b-ii — 2026-05-08).

---

## Path canônico

`30-decisoes/forecasting.md`

## Metadata canônica

- **Output ID:** F1-21b
- **Categoria:** 3 — Decisão (Princípio 9)
- **Schema version:** 1.0.0
- **Fase:** Fase 1 (Fundação)
- **Subfase:** 1.4.2 (paralelo a Plano de Conteúdo + co-produzido com Plano de Mídia F1-21a)
- **Cadência:** one-shot baseline (recalibrado em Sprint trimestral via re-execução parcial — schema separado deferido B7.1c)
- **Skill produtora:** `sobral` v2.0.0 (mesma skill que F1-21a — bounded contexts disjuntos D-Schema-1)
- **Linha de Visibilidade:** híbrida (cenário B vai pro deck cerimonial; modelo financeiro completo é interno)

---

## Frontmatter canônico (17+ campos)

```yaml
output_type: forecasting
ticker: <string>
data_construcao: <YYYY-MM-DD>
horizonte: Q1 | semestre | ano
status: rascunho | revisado-operador | aprovado-cliente
versao: <SemVer>
modelo_negocio: <enum>
cliente_n0: true | false
modo_dado: real | hipotetico-benchmark
confidence_geral: alta | media | baixa
moeda: BRL
horizonte_meses: 3 | 6 | 12
cenarios:
  - id: A
    nome: Pessimista
    probabilidade_estimada: <float>
    descricao: <string>
  - id: B
    nome: Central
    probabilidade_estimada: <float>
    descricao: <string>
  - id: C
    nome: Otimista
    probabilidade_estimada: <float>
    descricao: <string>
premissas_compartilhadas:
  budget_paid_q1: <float>
  ticket_medio: <float>
  ciclo_venda_dias: <int>
  win_rate_sql_dealwon: <float>
premissas_por_cenario:
  cenario_A: { cpl: <float>, cvr_lead_mql: <float>, cvr_mql_sql: <float>, cvr_sql_dealwon: <float>, organic_traffic_share: <float> }
  cenario_B: { ... }
  cenario_C: { ... }
projecoes_funil_q1:
  cenario_A:
    m1: { leads: <int>, mql: <int>, sql: <int>, dealwon: <int>, receita: <float> }
    m2: { ... }
    m3: { ... }
    total_q1: { ... }
  cenario_B: { ... }
  cenario_C: { ... }
breakeven:
  cenario_A: { meses_estimados: <float | n/a>, mes_calendario: <YYYY-MM> }
  cenario_B: { ... }
  cenario_C: { ... }
cash_flow_q1:
  cenario_A:
    investimento_paid: <float>
    investimento_organic_outro: <float>
    receita_estimada: <float>
    saldo_q1: <float>
  cenario_B: { ... }
  cenario_C: { ... }
sensibilidade:
  - variavel: cpl
    impacto_receita_q1: <float>
  - variavel: cvr_lead_mql
    impacto_receita_q1: <float>
  - variavel: ticket_medio
    impacto_receita_q1: <float>
  - variavel: ciclo_venda_dias
    impacto_receita_q1: <float>
gatilhos_revisao:
  - sinal: <string>
    deadline_revisao: <int dias>
recomendacao_meta_q1:
  validacao: confirma_meta_smart_gtm | recalibra_meta_smart_gtm
  meta_recalibrada_proposta: <string>
linkbacks:
  gtm_plan: 30-decisoes/gtm-plan.md
  plano_midia: 30-decisoes/plano-midia.md
  cenario_baseline: 20-snapshots/YYYY-MM/cenario-baseline.md
  analise_dados_historicos: 20-snapshots/YYYY-MM/analise-dados-historicos.md  # cond.
  relatorio_mercado: 20-snapshots/YYYY-MM/relatorio-mercado.md
  sistema_qualificacao: 10-fundacao/sistema-qualificacao.md
  icp_product_map: 10-fundacao/icp-product-map.md
tags:
  - forecasting
  - decisao
  - <ticker>
  - fase-1
```

---

## 11 seções obrigatórias

| # | Seção | Conteúdo | Critério completude |
|---|---|---|---|
| 1 | `## Sumário executivo` | 3 cenários A/B/C com receita Q1 · breakeven cenário B · validação ou recalibragem da meta · variável de maior sensibilidade · gatilhos | Endereça 5 elementos |
| 2 | `## Premissas compartilhadas (cross-cenário)` | 2.1 Budget paid · 2.2 Ticket médio · 2.3 Ciclo venda · 2.4 Win rate SQL→DealWon · 2.5 Organic share. Cada premissa com fonte + confidence | Premissas com fonte; confidence calibrado |
| 3 | `## Cenário A — Pessimista` | 3.1 Premissas divergentes · 3.2 Funil mensal M1/M2/M3 · 3.3 Receita Q1 · 3.4 Cash flow + saldo · 3.5 Probabilidade | Funil quantificado; números coerentes |
| 4 | `## Cenário B — Central` | Mesma estrutura. **Cenário B contém Meta GTM Plan §9 ±10%** | V3 blocker — Meta dentro de ±10% |
| 5 | `## Cenário C — Otimista` | Mesma estrutura | Funil quantificado |
| 6 | `## Comparativo cross-cenário` | Tabela: receita Q1 · CAC realizado · LTV/CAC · breakeven · ROAS por cenário. Visualização (ASCII bar chart ou Mermaid) | Tabela completa; visualização |
| 7 | `## Análise de sensibilidade` | Top 4-5 variáveis: CPL · CVR Lead→MQL · ticket médio · ciclo venda · win rate. Tornado chart. Variável de maior alavancagem identificada | ≥4 variáveis; alavanca principal identificada |
| 8 | `## Breakeven e cash flow` | 8.1 Breakeven mensal por cenário · 8.2 Cash flow Q1 · 8.3 Runway impacto cenário A · 8.4 Cross-link Cenário Baseline §5 | 4 sub-seções; coerência viabilidade |
| 9 | `## Validação ou recalibragem da meta Q1 (GTM Plan §9)` | 9.1 Meta SMART vs. cenário B · 9.2 Validação OU 9.3 Recalibragem proposta + justificativa · 9.4 Comunicação operador | V10 blocker — validação ou recalibragem com justificativa |
| 10 | `## Gatilhos de revisão mid-Q1` | Lista 3-5 sinais quantitativos com threshold + deadline | ≥3 gatilhos com threshold + deadline |
| 11 | `## Riscos e premissas de modelagem` | 11.1 Top 3 riscos do modelo · 11.2 Premissas críticas com confidence · 11.3 Limitações Forecasting | Riscos + premissas + limitações |

---

## Critérios de validação V1-V14

| # | Critério | Severidade |
|---|---|---|
| V1 | Frontmatter parseável + 11 seções | **blocker** |
| V2 | 3 cenários A/B/C com funil mensal M1/M2/M3 quantificado | **blocker** |
| V3 | Cenário B contém Meta Q1 GTM Plan §9 ±10% — OU §9.3 explícita recalibragem proposta | **blocker** |
| V4 | Premissas compartilhadas com fonte explícita | **blocker** |
| V5 | Cliente com dados (`modo_dado: real`): premissas derivam Análise Histórica | **blocker** (cond. há dados) |
| V6 | Cliente N0 (`modo_dado: hipotetico-benchmark`): premissas derivam Relatório Mercado §3 com fonte; `confidence: baixa` declarado | **blocker** (cond. cliente N0) |
| V7 | §6 comparativo cross-cenário com tabela completa | alto |
| V8 | §7 análise de sensibilidade com ≥4 variáveis; variável de maior alavancagem identificada | alto |
| V9 | §8 breakeven calculado por cenário (ou explicitamente "n/a — cenário não atinge breakeven em Q1") | **blocker** |
| V10 | §9 validação ou recalibragem da meta GTM Plan §9 com justificativa | **blocker** |
| V11 | §10 ≥3 gatilhos quantitativos com threshold + deadline | alto |
| V12 | §11 ≥3 riscos + ≥3 premissas com confidence | médio |
| V13 | Cross-link bidirecional GTM Plan §9 + Plano de Mídia §9 + Manifest v1.0 | **blocker** |
| V14 | Probabilidades cenários A+B+C somam 1.0 ±0.05 | alto |

---

## 8 edge cases canônicos

### 5.1 Cliente N0 (sem dados pra calibrar)
`modo_dado: hipotetico-benchmark` + `confidence_geral: baixa`. Premissas derivam Relatório Mercado §3 (CAC benchmark) + ICP Product Map (LTV teórico) + premissas operador. §11 ressalva forte: "Forecasting hipotético — primeiros 30-45 dias = calibrar premissas; recalibragem prevista no drop M1". §10 gatilhos mais sensíveis (revisão aos 30 dias com qualquer desvio >20%).

### 5.2 Cliente com dados parciais (operação <6 meses ou só 1 canal)
`modo_dado: real` parcial. Premissas que existem na Análise Histórica usam dado real; premissas faltantes (ex: novo canal a testar) usam benchmark. §11 documenta hibridismo. §7 sensibilidade ganha peso maior nas premissas hipotéticas.

### 5.3 Cliente com runway curto (<6 meses)
§8 cash flow ganha urgência — saldo negativo cenário A pode ser fatal. §10 gatilhos mais agressivos (revisão em 15 dias + kill rápido). §11 risco crítico: "Cenário A pode levar a fechamento da operação — gatilho de pivot precisa ser claro". §9 meta Q1 pode ser ajustada pra "obter saldo positivo Q1" ao invés de meta ambiciosa.

### 5.4 Modelo recurring (SaaS)
Receita Q1 = MRR × meses ativos no Q1 (não receita única). LTV calculado em meses. Breakeven leva em conta retenção: cenário B com churn alto pode não atingir breakeven. §11 ganha sub-seção churn explicitamente modelado.

### 5.5 Modelo transacional (e-commerce, infoproduto)
Receita Q1 = pedidos × ticket médio. ROAS é métrica primária. §3-5 cenários podem ter sazonalidade explícita. §7 sensibilidade ao ticket médio é alta.

### 5.6 Modelo B2B com ciclo longo (3-6 meses)
§4 cenário B reconhece que receita Q1 = leads gerados Q1 × CVR × ticket × % ciclo fechado em Q1 (defasagem). Forecasting Q+1 e Q+2 fica parcial. §8 cash flow Q1 pode ser muito negativo (investimento sem receita) — §11 ressalva crítica.

### 5.7 Múltiplos canais com performances divergentes esperadas
§2-5 premissas por canal (sub-tabelas). §7 sensibilidade considera mix de canais. §6 comparativo pode incluir variante "cenário B com mix realocado".

### 5.8 Recalibragem em Sprint trimestral
`versao` SemVer bump (1.0.0 → 1.1.0). Adendo `## Recalibragem Sprint Q?` agregado. Premissas Q+1 derivadas Performance-Sprint do Loop trimestral. §9 valida ou recalibra meta Q+1 do GTM Plan revisado.

---

## Linkbacks bidirecionais

### Upstream
- F1-20 GTM Plan (§9 meta + §10 sequência — input formal blocker)
- F1-21a Plano de Mídia (§3 budget + §9 métricas-alvo paid — input blocker; co-produção mesma skill)
- F1-19 Cenário Baseline (§4-5-6 — input blocker)
- F1-18 Análise Histórica cond. (input alto — calibração premissas)
- F1-7 Relatório Mercado (§3 CAC benchmark — input alto, especialmente cliente N0)
- F1-16b Sistema Qualificação (taxas conversão — input alto)
- F1-10b ICP Product Map (LTV + ticket por combinação — input blocker)

### Downstream
- F1-23 Manifest v1.0 (consome inteiro)
- F1-25 GTM Deck (cenário B é o número da apresentação cerimonial)
- F3 `data-snapshot-builder` modo `performance-drop` (compara Forecasting × realizado mensal)
- F3 `data-snapshot-builder` modo `performance-sprint` (compara Forecasting × realizado trimestral)

### Princípios incidentes
- **P1** (Especialização — Forecasting ≠ Plano de Mídia)
- **P9** (Estado vs. Decisão — Forecasting é Decisão)
- **P8** (Vault como Camada de Estado — premissas tornam-se infra rastreável; mudanças de premissa = bump SemVer)
- **P11** (CODE — Express: comunica risco financeiro em formato auditável)

---

## Histórico de schema

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 2026-05-08 | Schema inicial (B7.1b-ii) — 3 cenários A/B/C com premissas explícitas + funil mensal quantificado + breakeven + cash flow + sensibilidade tornado + gatilhos de revisão + validação/recalibragem da meta GTM Plan; cliente N0 com benchmark; recalibragem Sprint trimestral mapeada |
