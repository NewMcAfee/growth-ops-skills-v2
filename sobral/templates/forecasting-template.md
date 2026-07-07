---
output_type: forecasting
ticker: <TICKER>
data_construcao: <YYYY-MM-DD>
horizonte: Q1
status: rascunho
versao: "1.0.0"
modelo_negocio: <enum>
cliente_n0: <true | false>
modo_dado: <real | hipotetico-benchmark>
confidence_geral: <alta | media | baixa>
moeda: BRL
horizonte_meses: 3
cenarios:
  - id: A
    nome: Pessimista
    probabilidade_estimada: 0.25
    descricao: "Premissas piores que benchmark — CPL +30%, CVR -20%, ciclo +30%, win rate -15%"
  - id: B
    nome: Central
    probabilidade_estimada: 0.50
    descricao: "Premissas baseline — Análise Histórica (cliente N1+) ou benchmark Relatório Mercado §3 (cliente N0)"
  - id: C
    nome: Otimista
    probabilidade_estimada: 0.25
    descricao: "Premissas melhores que benchmark — CPL -15%, CVR +25%, ciclo -10%, win rate +15%"
premissas_compartilhadas:
  budget_paid_q1: <float>
  ticket_medio: <float>
  ciclo_venda_dias: <int>
  win_rate_sql_dealwon: <float>
premissas_por_cenario:
  cenario_A:
    cpl: <float>
    cvr_lead_mql: <float>
    cvr_mql_sql: <float>
    cvr_sql_dealwon: <float>
    organic_traffic_share: <float>
  cenario_B:
    cpl: <float>
    cvr_lead_mql: <float>
    cvr_mql_sql: <float>
    cvr_sql_dealwon: <float>
    organic_traffic_share: <float>
  cenario_C:
    cpl: <float>
    cvr_lead_mql: <float>
    cvr_mql_sql: <float>
    cvr_sql_dealwon: <float>
    organic_traffic_share: <float>
projecoes_funil_q1:
  cenario_A:
    m1: { leads: <int>, mql: <int>, sql: <int>, dealwon: <int>, receita: <float> }
    m2: { leads: <int>, mql: <int>, sql: <int>, dealwon: <int>, receita: <float> }
    m3: { leads: <int>, mql: <int>, sql: <int>, dealwon: <int>, receita: <float> }
    total_q1: { leads: <int>, mql: <int>, sql: <int>, dealwon: <int>, receita: <float> }
  cenario_B:
    m1: { ... }
    m2: { ... }
    m3: { ... }
    total_q1: { ... }
  cenario_C:
    m1: { ... }
    m2: { ... }
    m3: { ... }
    total_q1: { ... }
breakeven:
  cenario_A: { meses_estimados: <float | n/a>, mes_calendario: <YYYY-MM> }
  cenario_B: { meses_estimados: <float>, mes_calendario: <YYYY-MM> }
  cenario_C: { meses_estimados: <float>, mes_calendario: <YYYY-MM> }
cash_flow_q1:
  cenario_A: { investimento_paid: <float>, investimento_organic_outro: <float>, receita_estimada: <float>, saldo_q1: <float> }
  cenario_B: { ... }
  cenario_C: { ... }
sensibilidade:
  - variavel: cpl
    impacto_receita_q1: 25  # ±% receita por ±10% na variável
  - variavel: cvr_lead_mql
    impacto_receita_q1: 18
  - variavel: ticket_medio
    impacto_receita_q1: 15
  - variavel: ciclo_venda_dias
    impacto_receita_q1: 8
  - variavel: win_rate_sql_dealwon
    impacto_receita_q1: 12
gatilhos_revisao:
  - sinal: "CPL realizado >= 1.5× CPL alvo cenário B aos 30 dias"
    deadline_revisao: 30
  - sinal: "CVR Lead→MQL realizado < 70% do alvo aos 45 dias"
    deadline_revisao: 45
  - sinal: "Receita acumulada M2 < 50% do esperado cenário B"
    deadline_revisao: 60
recomendacao_meta_q1:
  validacao: <confirma_meta_smart_gtm | recalibra_meta_smart_gtm>
  meta_recalibrada_proposta: "<descrição se recalibragem>"
linkbacks:
  gtm_plan: 30-decisoes/gtm-plan.md
  plano_midia: 30-decisoes/plano-midia.md
  cenario_baseline: 20-snapshots/<YYYY-MM>/cenario-baseline.md
  analise_dados_historicos: 20-snapshots/<YYYY-MM>/analise-dados-historicos.md  # cond.
  relatorio_mercado: 20-snapshots/<YYYY-MM>/relatorio-mercado.md
  sistema_qualificacao: 10-fundacao/sistema-qualificacao.md
  icp_product_map: 10-fundacao/icp-product-map.md
tags:
  - forecasting
  - decisao
  - <ticker>
  - fase-1
---

# Forecasting — <Cliente> · Q1 <YYYY>

## 1. Sumário executivo

<4-6 parágrafos endereçando os 5 elementos:>
- 3 cenários A/B/C com receita Q1 estimada
- Breakeven cenário B
- Validação ou recalibragem da meta GTM Plan §9
- Variável de maior sensibilidade
- Gatilhos de revisão

---

## 2. Premissas compartilhadas (cross-cenário)

| Premissa | Valor | Fonte | Confidence |
|---|---|---|---|
| Budget paid Q1 | R$ <float> | Plano de Mídia §3 | alta |
| Ticket médio | R$ <float> | ICP Product Map | <alta/média/baixa> |
| Ciclo de venda (dias) | <int> | <Análise Histórica §X | benchmark> | <...> |
| Win rate SQL→DealWon | <%> | <Sistema de Qualificação | benchmark> | <...> |
| Organic traffic share alvo | <%> | <benchmark | premissa operador> | <...> |

---

## 3. Cenário A — Pessimista (probabilidade ~25%)

### 3.1 Premissas divergentes
- **CPL:** R$ <valor> (+30% vs. benchmark)
- **CVR Lead→MQL:** <%> (-20% vs. benchmark)
- **CVR MQL→SQL:** <%>
- **CVR SQL→DealWon:** <%>
- **Justificativa:** <por que cenário pessimista é plausível>

### 3.2 Funil mensal M1/M2/M3

| Mês | Leads | MQL | SQL | DealWon | Receita |
|---|---|---|---|---|---|
| M1 | <int> | <int> | <int> | <int> | R$ <float> |
| M2 | <int> | <int> | <int> | <int> | R$ <float> |
| M3 | <int> | <int> | <int> | <int> | R$ <float> |
| **Total Q1** | <int> | <int> | <int> | <int> | **R$ <float>** |

### 3.3 Receita Q1: R$ <float>

### 3.4 Cash flow + saldo
- Investimento paid: R$ <float>
- Investimento orgânico/outro: R$ <float>
- Receita estimada: R$ <float>
- **Saldo Q1: R$ <float>** ⚠ (cenário negativo sinaliza risco runway)

### 3.5 Probabilidade estimada: 0.25

---

## 4. Cenário B — Central (probabilidade ~50%)

> **Cenário B = validação da meta GTM Plan §9** — meta SMART deve estar dentro de ±10%.

### 4.1 Premissas divergentes
- **CPL:** R$ <valor> (baseline)
- **CVR Lead→MQL:** <%> (baseline)
- **CVR MQL→SQL:** <%>
- **CVR SQL→DealWon:** <%>
- **Justificativa:** <derivação Análise Histórica ou benchmark Relatório Mercado §3>

### 4.2 Funil mensal M1/M2/M3
<mesma estrutura cenário A>

### 4.3 Receita Q1: R$ <float>

### 4.4 Cash flow + saldo
<mesma estrutura cenário A>

### 4.5 Probabilidade estimada: 0.50

---

## 5. Cenário C — Otimista (probabilidade ~25%)

### 5.1 Premissas divergentes
- **CPL:** R$ <valor> (-15% vs. benchmark)
- **CVR Lead→MQL:** <%> (+25% vs. benchmark)
- **CVR MQL→SQL:** <%>
- **CVR SQL→DealWon:** <%>
- **Justificativa:** <upside plausível — quando vale escalar agressivo>

### 5.2 Funil mensal M1/M2/M3
<mesma estrutura>

### 5.3 Receita Q1: R$ <float>

### 5.4 Cash flow + saldo
<mesma estrutura>

### 5.5 Probabilidade estimada: 0.25

---

## 6. Comparativo cross-cenário

| Cenário | Receita Q1 | CAC realizado | LTV/CAC | Breakeven (meses) | ROAS (cond.) |
|---|---|---|---|---|---|
| A — Pessimista | R$ <float> | R$ <float> | <ratio> | <float | n/a> | <ratio> |
| B — Central | R$ <float> | R$ <float> | <ratio> | <float> | <ratio> |
| C — Otimista | R$ <float> | R$ <float> | <ratio> | <float> | <ratio> |

**Visualização:**
```
Cenário A: ▓▓▓▓▓▓ R$ <X>
Cenário B: ▓▓▓▓▓▓▓▓▓▓▓ R$ <Y>  ← Meta GTM Plan §9
Cenário C: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ R$ <Z>
```

---

## 7. Análise de sensibilidade

**Top 4-5 variáveis com maior impacto na receita Q1 (Tornado chart):**

```
Variável: CPL                   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ±25% receita Q1
Variável: CVR Lead→MQL          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ±18% receita Q1
Variável: Ticket médio          ▓▓▓▓▓▓▓▓▓▓▓▓ ±15% receita Q1
Variável: Win rate              ▓▓▓▓▓▓▓▓▓ ±12% receita Q1
Variável: Ciclo venda           ▓▓▓▓▓▓ ±8% receita Q1
```

**Variável de maior alavancagem:** `<CPL>` — investir esforço Q1 em otimizar essa variável tem o maior payoff esperado.

---

## 8. Breakeven e cash flow

### 8.1 Breakeven mensal por cenário

| Cenário | Meses estimados | Mês calendário |
|---|---|---|
| A | <float | n/a> | <YYYY-MM | "Não atinge Q1"> |
| B | <float> | <YYYY-MM> |
| C | <float> | <YYYY-MM> |

### 8.2 Cash flow Q1
<tabela investimento × receita por cenário>

### 8.3 Runway impacto cenário A
<se cenário A = saldo negativo + runway curto = sinaliza necessidade revisão>

### 8.4 Cross-link com Cenário Baseline §5
<coerência viabilidade financeira — runway atual + burn rate>

---

## 9. Validação ou recalibragem da meta Q1 (GTM Plan §9)

### 9.1 Meta Q1 SMART do GTM Plan vs. cenário B

- **Meta GTM Plan §9:** <enunciado>
- **Cenário B receita:** R$ <float>
- **Diferença:** <% diferença vs. meta>

### 9.2 Validação (se diferença ≤ 10%)
✅ Forecasting **valida** a meta. Operador reporta validação ao cliente na Apresentação cerimonial (1.5).

### 9.3 Recalibragem proposta (se diferença > 10%)
⚠ Forecasting **propõe recalibragem** da meta:
- **Meta atual:** <enunciado>
- **Meta recalibrada:** <novo enunciado>
- **Justificativa:** <por que recalibrar (cenário B aponta divergência sustentada)>
- **Caminho:** <recalibrar pra baixo / pra cima>

### 9.4 Comunicação ao operador
<como comunicar à Apresentação cerimonial — narrativa transparente sobre recalibragem ou validação>

---

## 10. Gatilhos de revisão mid-Q1

| # | Sinal | Threshold | Deadline (dias) |
|---|---|---|---|
| 1 | "CPL realizado >= 1.5× CPL alvo cenário B" | <threshold> | 30 |
| 2 | "CVR Lead→MQL realizado < 70% do alvo" | <threshold> | 45 |
| 3 | "Receita acumulada M2 < 50% do esperado cenário B" | <threshold> | 60 |

---

## 11. Riscos e premissas de modelagem

### 11.1 Top 3 riscos do modelo

| Risco | Severidade | Mitigação |
|---|---|---|
| Ciclo venda mais longo que assumido | <alta/média/baixa> | <mitigação> |
| Sazonalidade não considerada | <...> | <...> |
| Cliente N0: premissas hipotéticas | <...> | <recalibragem mensal D+30> |

### 11.2 Premissas críticas com confidence

| Premissa | Confidence | Fonte |
|---|---|---|
| CPL alvo cenário B | <alta/média/baixa> | <Análise Histórica §X | benchmark> |
| Win rate SQL→DealWon | <...> | <Sistema Qualificação | benchmark> |

### 11.3 Limitações do Forecasting

- Modelo não modela explicitamente <churn / sazonalidade / concorrência>
- Cliente N0: forecasting hipotético — primeiros 30-45 dias = calibrar premissas
- Defasagem temporal (modelo B2B ciclo longo): receita Q1 subestimada — Q+1/Q+2 carry-over
