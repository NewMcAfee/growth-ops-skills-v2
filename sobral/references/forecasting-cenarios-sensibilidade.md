# Forecasting — 3 Cenários A/B/C + Análise de Sensibilidade

> Reference canônica pra Fase B do `sobral` v2.0.0 — modelagem de Forecasting com 3 cenários A/B/C com premissas explícitas, análise de sensibilidade Tornado, breakeven, cash flow e gatilhos de revisão mid-Q1.

---

## Princípio canônico

**Forecasting estratégico ≠ wishful planning.** 3 cenários A/B/C com **premissas explícitas + fonte rastreável** sustentam validação ou recalibragem da Meta Q1 do GTM Plan §9. Cliente N0 produz Forecasting **qualitativo** (modo `hipotetico-benchmark` + `confidence: baixa`) — checkpoint mensal recalibra com dados reais que vão chegando (Q7 fechada B3).

> **Regra dura V3 blocker §4:** Cenário B (Central) deve conter Meta Q1 do GTM Plan §9 (±10%) OU §9.3 explícita recalibragem proposta com justificativa.

> **Regra V14 alto:** probabilidades dos 3 cenários somam 1.0 (com tolerância ≤0.05).

---

## Estrutura canônica dos 3 cenários

### Cenário A — Pessimista (probabilidade típica ~0.25)
- **Premissas piores que benchmark:** CPL +30%, CVR -20%, ciclo venda +30%, win rate -15%
- **Sinaliza risco:** se realizado se aproxima de A, gatilho de revisão dispara
- **Cash flow:** pode mostrar saldo negativo Q1 — sinaliza necessidade de revisão de runway

### Cenário B — Central (probabilidade típica ~0.50)
- **Premissas baseline:** Análise Histórica (cliente com dados) ou benchmark Relatório Mercado §3 (cliente N0)
- **Cenário de validação da meta GTM Plan §9** — meta SMART deve estar dentro de ±10%
- **Cash flow:** equilíbrio Q1 (saldo zero a positivo modesto)

### Cenário C — Otimista (probabilidade típica ~0.25)
- **Premissas melhores que benchmark:** CPL -15%, CVR +25%, ciclo venda -10%, win rate +15%
- **Testa upside:** quando vale escalar agressivo
- **Cash flow:** saldo positivo significativo — gera capital pra reinvestir Q+1

**Variações por modelo de negócio (probabilidades adaptadas):**
- Cliente N0: A=0.40 / B=0.40 / C=0.20 (mais conservador — incerteza)
- Cliente maduro N3+: A=0.20 / B=0.55 / C=0.25 (mais centrado)
- Cliente com runway curto: A=0.35 / B=0.45 / C=0.20 (menos risco upside)

---

## Premissas canônicas por modelo

### B2B SaaS recurring
- **CPL:** lead gerado paid ou orgânico
- **CVR Lead→MQL:** % MQL qualificado pelo Sistema de Qualificação
- **CVR MQL→SQL:** % SQL com intent demonstrado
- **CVR SQL→DealWon:** win rate
- **MRR Q1 = ΣDealWon × ARPU × meses ativos no Q1**
- **LTV implícito:** ARPU / churn mensal

### B2C Transacional (e-commerce / infoproduto)
- **CPC ou CPM** (modelo bid-based)
- **CTR landing**
- **CVR LP→Checkout**
- **Ticket médio**
- **Receita Q1 = pedidos × ticket médio**
- **ROAS = receita / investimento paid**

### B2B Serviço (consultoria)
- **CPL → CVR Lead→Demo → CVR Demo→Proposta → CVR Proposta→Fechamento**
- **Ciclo venda:** geralmente 30-90 dias (defasagem afeta Q1)
- **Receita Q1 = leads gerados Q1 × CVR × ticket × % ciclo fechado em Q1**
- Ciclo longo: receita Q1 pode subestimar — Q+1 e Q+2 carry-over

### B2C Alto envolvimento (clínica / escola / plano saúde)
- **CPL → CVR Lead→Agendamento → CVR Agendamento→Comparecimento → CVR Compareciment→Fechamento**
- **Ciclo decisão:** 14-90 dias
- **Ticket médio + LTV** (clínica/plano = recurring; escola = one-shot anual)

---

## Análise de sensibilidade — Tornado canônico

**Top 4-5 variáveis com maior impacto na receita Q1** — rank por impacto absoluto a ±10% na variável:

```
Variável: CPL                   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ±25% receita Q1
Variável: CVR Lead→MQL          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ±18% receita Q1
Variável: Ticket médio          ▓▓▓▓▓▓▓▓▓▓▓▓ ±15% receita Q1
Variável: Win rate              ▓▓▓▓▓▓▓▓▓ ±12% receita Q1
Variável: Ciclo venda           ▓▓▓▓▓▓ ±8% receita Q1
```

**Variável de maior alavancagem** = aquela com maior impacto. Identifica onde investir esforço de melhoria em Q1.

**Implementação sugerida:**
- Tornado chart textual ASCII (template acima)
- OU Mermaid bar chart inline
- OU tabela markdown com bar bars Unicode

**Cálculo simplificado canônico:**
```
Impacto receita ±10% na variável V =
  | receita(V × 1.10) - receita(V × 0.90) | / receita(V baseline) × 100
```

---

## Breakeven canônico

Por cenário (A / B / C):
- **Meses estimados pra breakeven:** quanto tempo até receita acumulada = investimento acumulado
- **Mês calendário:** YYYY-MM esperado
- **Impacto runway:** se cenário A não atinge breakeven em runway → risco de fechamento (sinalizar §11 limitações)

**Fórmula simplificada:**
```
Breakeven (meses) = Investimento total Q1 / Receita média mensal projetada
```

Para SaaS recurring: ajustado por churn (LTV ajustado).

---

## Cash flow Q1 canônico

Por cenário (A / B / C):

| Componente | Valor |
|---|---|
| Investimento paid (Plano Mídia §3) | R$ X |
| Investimento orgânico/outro (cond.) | R$ Y |
| Receita estimada (cenário) | R$ Z |
| **Saldo Q1** | **R$ Z - X - Y** |

**Sinalizar quando saldo A < 0:** risco de runway esgotar antes de Q+1.

---

## Gatilhos de revisão mid-Q1

≥3 sinais quantitativos com threshold + deadline:
1. "CPL realizado >= 1.5× CPL alvo cenário B aos 30 dias = recalibrar"
2. "CVR Lead→MQL realizado < 70% do alvo aos 45 dias = recalibrar"
3. "Receita acumulada M2 < 50% do esperado cenário B = recalibrar + emit Decision Doc cont/pivot"

**Cliente com runway curto:** gatilhos mais sensíveis (revisão aos 15 dias com qualquer desvio >20%).

---

## Validação ou recalibragem da meta Q1

Cenário B é a referência. 2 caminhos:

### Caminho A — Validação
- Meta GTM Plan §9 está dentro de ±10% do cenário B
- §9 Forecasting **valida** a meta sem mudança
- Comunicação: operador reporta validação ao cliente na Apresentação cerimonial

### Caminho B — Recalibragem
- Meta GTM Plan §9 está fora de ±10% do cenário B
- §9 Forecasting **propõe recalibragem** com justificativa explícita
- Caminho B-1 — recalibrar pra baixo (cenário B é menor que meta original)
- Caminho B-2 — recalibrar pra cima (cenário B é maior — meta original conservadora demais)
- Comunicação: operador discute recalibragem com cliente (Apresentação cerimonial 1.5)
- GTM Plan §9 atualizado pós-Apresentação (Manifest v1.0.1 patch cond.)

---

## Cliente N0 — modelo `hipotetico-benchmark`

Premissas derivam:
- **CPL:** Relatório Mercado §3 (CAC benchmark vertical) + ICP Product Map (LTV teórico)
- **CVR:** benchmarks WordStream + Meta + Google + LinkedIn 2024-2026 por vertical
- **Ticket médio:** ICP Product Map (definição operador)
- **Ciclo venda:** ICP Product Map ou Cenário Baseline §6 (estimativa)

**§11 Forecasting cliente N0 — ressalva forte canônica:**
> "Forecasting hipotético — primeiros 30-45 dias = calibrar premissas; recalibragem prevista no drop M1. Cenário B = pondera benchmark vertical com tolerância ampla; meta Q1 deve ser interpretada como hipótese a validar, não compromisso financeiro firmemente projetado."

---

## Anti-patterns (recusar)

- ❌ 3 cenários A/B/C com premissas idênticas (cenários iguais = não há cenários)
- ❌ Cenário B fora de ±10% da meta GTM Plan §9 sem §9.3 recalibragem proposta (V3 blocker)
- ❌ Probabilidades A+B+C ≠ 1.0 ±0.05 (V14 alto)
- ❌ Premissas sem fonte (V4 blocker — Análise Histórica / Relatório Mercado / ICP Product Map)
- ❌ Cliente N0 sem `cliente_n0: true` + `confidence: baixa` (V6 blocker cond.)
- ❌ Sensibilidade com <4 variáveis (V8 alto)
- ❌ Breakeven n/a sem justificativa (V9 blocker — explicitar "cenário não atinge breakeven em Q1")
- ❌ Gatilhos qualitativos ("se as coisas piorarem") — sem threshold quantitativo (V11 alto)
- ❌ Ignorar churn em modelo recurring SaaS (cenário B sem churn modelado = breakeven irreal)
- ❌ Modelar cenário C como upside otimista de fé (sem premissa rastreável que justifique)

---

## Linkbacks

- Schema F1-21b (Forecasting) §3-§5 (3 cenários) + §7 (sensibilidade) + §9 (validação/recalibragem)
- GTM Plan §9 (Meta Q1 SMART — referência da validação)
- Cenário Baseline §4 (Unit Economics — premissas baseline) + §5 (Viabilidade — breakeven baseline)
- Plano de Mídia §3 (Budget — input direto Forecasting) + §9 (Métricas-alvo — premissas baseline)
- Análise de Dados Históricos §4 (Performance por canal — calibração premissas reais cliente N1+)
- Relatório de Mercado §3 (CAC benchmark — calibração cliente N0)
- F3-3 Performance-Drop (compara realizado vs. Forecasting cenário B mensal)
- F3-6 Performance-Sprint (consolida Q1 e dispara recalibragem trimestral)

---

## Fontes

- Eric Ries — *The Lean Startup* (Forecasting com hipóteses e validação)
- Geoffrey Moore — *Crossing the Chasm* (Forecasting de adoção em curva)
- Sean Ellis — *Hacking Growth* (Forecasting baseado em loops + experimentação)
- Reforge Forecasting curriculum (2024-2026)
- Winning by Design — *Revenue Architecture* (Forecasting recurring + breakeven)
- WordStream Industry Benchmarks (calibração CPL/CTR/CVR cliente N0 — atualizado 2024-2026)
