---
output_type: plano-midia
ticker: <TICKER>
data_construcao: <YYYY-MM-DD>
horizonte: Q1
status: rascunho
versao: "1.0.0"
modelo_negocio: <enum>
cliente_n0: <true | false>
confidence_geral: <alta | media | baixa>
budget_total_q1:
  valor: <float>
  moeda: BRL
  distribuicao_mensal:
    m1: <float>
    m2: <float>
    m3: <float>
plataformas:
  - id: meta-ads
    budget_q1: <float>
    pct_total: <float>
    bowtie_etapa: <attract | engage | convert | expand | nurture>
    icp_combinacoes: [<combinação 1>]
    objetivo_canal: <leads | conversions | engagement | reach | retention | retargeting>
  - id: google-ads-search
    budget_q1: <float>
    pct_total: <float>
    bowtie_etapa: <...>
    icp_combinacoes: [<...>]
    objetivo_canal: <...>
estrutura_conta:
  - plataforma: meta-ads
    campanhas:
      - nome: "<gerado por name-templates.yml — ex: 'meta-leadgen-icp1-q1-2026'>"
        objetivo: "Lead Gen"
        adsets_estimados: <int>
        criativos_iniciais: <int>
        budget_diario: <float>
        bid_strategy: "Highest Volume"
audiencias:
  - plataforma: meta-ads
    tipo: lookalike
    tamanho_estimado: "1% = ~2M usuários BR"
    fonte: "Lookalike 1% de DealWon últimos 90d"
    icp_alvo: "<combinação 1>"
  - plataforma: meta-ads
    tipo: first-party
    tamanho_estimado: <int>
    fonte: "CRM upload — DealWon últimos 365d"
    icp_alvo: "<combinação 1>"
    hash_policy: sha256-canonical
criativos:
  - canal: meta-ads
    formatos: [single-image, carousel, video-15s, reels]
    angulos: [dor, ganho, social-proof, comparacao]
    quantidade_inicial: <int>  # Por ICP × ângulo
    cadencia_renovacao: weekly
cadencia_testes:
  hipoteses_paid_q1:
    - id: H-paid-1
      enunciado: "Se aumentamos investimento Meta Ads (R$X/mês) com criativo focado em ICP-1 ângulo dor, então geramos ≥120 leads/mês com CPL ≤R$80"
      metrica: CPL
      threshold_validacao: ">= 120 leads/mês AND CPL <= R$80"
      threshold_falsificacao: "< 80 leads/mês OR CPL > R$120"
      deadline: <YYYY-MM-DD>
    - id: H-paid-2
      enunciado: "..."
      metrica: <CPL | CPA | ROAS | CVR | CTR>
      threshold_validacao: "..."
      threshold_falsificacao: "..."
      deadline: <YYYY-MM-DD>
  cadencia_revisao: semanal
  framework_teste: ab-test
metricas_alvo_q1:
  cpl_alvo: <float>
  cpa_alvo: <float>
  roas_alvo: <float>  # cond. modelo transacional
  ctr_alvo: <float>
  cvr_lead_mql: <float>
  cvr_mql_sql: <float>
  share_of_budget_por_canal:
    meta-ads: <%>
    google-ads-search: <%>
exclusoes_e_pixels:
  exclusoes_audiencia:
    - clientes_atuais
    - leads_60d
    - dealLost_90d
    - funcionarios_internos
  pixels_capi:
    - plataforma: meta
      eventos_capi: [PageView, Lead, MQL, DealWon]
      hash_policy_email_phone: sha256-canonical
    - plataforma: google-ads
      eventos_capi: [conversion_lead, conversion_dealwon]
      hash_policy_email_phone: sha256-canonical
landing_pages:
  - campanha_id: "<referência name-templates>"
    lp_alvo: "<path no vault Fase 2 ou URL externa>"
    icp_alvo: "<combinação 1>"
    cta: "<CTA da LP>"
linkbacks:
  gtm_plan: 30-decisoes/gtm-plan.md
  cenario_baseline: 20-snapshots/<YYYY-MM>/cenario-baseline.md
  taxonomia_md: 10-fundacao/taxonomia.md
  taxonomia_yml: 10-fundacao/taxonomia.yml
  measurement_plan: 10-fundacao/measurement-plan.md
  icp_product_map: 10-fundacao/icp-product-map.md
  forecasting: 30-decisoes/forecasting.md
  plano_conteudo: 30-decisoes/plano-conteudo.md
tags:
  - plano-midia
  - decisao
  - <ticker>
  - fase-1
---

# Plano de Mídia — <Cliente> · Q1 <YYYY>

## 1. Sumário executivo

<4-6 parágrafos endereçando os 5 elementos:>
- Budget Q1 total + distribuição mensal
- Canais priorizados
- Objetivos por canal
- Meta CPL/CPA/ROAS
- Cadência de testes

---

## 2. Alinhamento com GTM Plan

### 2.1 Restrição principal subordinada
<Cenário Baseline §2 → GTM Plan §4 → como Plano de Mídia ataca>

### 2.2 Loops priorizados que paid alimenta
<subset GTM Plan §5 — quais loops paid sustenta>

### 2.3 ICP×Produto canônicas servidas
<combinações herdadas GTM Plan §6>

### 2.4 Anti-canais (descartados explicitamente)
- <anti-canal 1 + justificativa>
- <anti-canal 2 + justificativa>

---

## 3. Budget e alocação

### 3.1 Budget total Q1 + distribuição mensal

| Mês | Valor (R$) | % do Q1 |
|---|---|---|
| M1 | <valor> | <%> |
| M2 | <valor> | <%> |
| M3 | <valor> | <%> |
| **Total Q1** | **<valor>** | **100%** |

### 3.2 Alocação por plataforma

| Plataforma | Budget Q1 (R$) | % do total |
|---|---|---|
| Meta Ads | <valor> | <%> |
| Google Ads Search | <valor> | <%> |
| <plataforma N> | <valor> | <%> |
| **Total** | **<valor>** | **100%** |

### 3.3 Alocação por etapa Bowtie

| Etapa | % do budget |
|---|---|
| Attract | <%> |
| Engage | <%> |
| Convert | <%> |
| Expand | <%> |
| Nurture | <%> |

### 3.4 Alocação por ICP×Produto

| Combinação ICP×Produto | % do budget |
|---|---|
| <combinação principal> | <%> |
| <combinação secundária 1> | <%> |
| <combinação secundária 2 cond.> | <%> |

---

## 4. Plataformas e canais

### 4.1 Meta Ads
- **Objetivo:** <Lead Gen / Sales / etc.>
- **ICP×Produto servidas:** <lista>
- **Etapa Bowtie:** <attract/engage/convert>
- **Tipo de campanha:** <Lead Gen / Conversions / etc.>
- **Justificativa estratégica:** <por que Meta pra esse ICP>

### 4.2 Google Ads Search
- **Objetivo:** <Search Conversions / Brand Search>
- **ICP×Produto servidas:** <lista>
- **Etapa Bowtie:** <convert>
- **Tipo de campanha:** <Search>
- **Justificativa estratégica:** <intent-based bottom-funnel>

### 4.X (plataformas adicionais)
<mesma estrutura>

---

## 5. Estrutura de conta

### 5.1 Meta Ads

| Campanha | Objetivo | Adsets | Criativos | Budget diário | Bid strategy |
|---|---|---|---|---|---|
| <nome name-template> | Lead Gen | <int> | <int> | R$<float> | Highest Volume |
| <nome name-template> | Conversions | <int> | <int> | R$<float> | Cost Cap |

**Pattern UTM canônico Growth IA Ops:**
- `utm_source=meta`
- `utm_campaign=<campaign_id>` (ID nativo)
- `utm_medium=<adset_id>` (ID nativo)
- `utm_content=<ad_id>` (ID nativo)

### 5.2 Google Ads Search
<mesma estrutura>

### 5.X (plataformas adicionais)
<mesma estrutura>

---

## 6. Audiências

### 6.1 Meta Ads

#### 6.1.1 Lookalikes
- **LAL 1% DealWon 90d:** ~2M usuários BR — ICP-1
- **LAL 3% DealWon 90d:** ~6M usuários BR — ICP-2

#### 6.1.2 Interesse / Comportamento
- <Detailed Targeting interesses + comportamentos>

#### 6.1.3 Retargeting
- 7d carrinho abandonado
- 30d visitou LP
- 90d engagement page

#### 6.1.4 First-party (CRM upload — hash SHA-256 obrigatória)
- **DealWon 365d** → seed pra LAL
- **Email format:** lowercase + trim + SHA-256 hex unsalted
- **Phone format:** E.164 + SHA-256 hex unsalted
- **CPF format:** numeric-only + SHA-256 hex unsalted

#### 6.1.5 Exclusões
- Clientes atuais (CRM upload exclusion)
- Leads <60d (em nutrição)
- DealLost <90d
- Funcionários internos

### 6.2 Google Ads Search
<mesma estrutura>

### 6.X (plataformas adicionais)
<mesma estrutura>

---

## 7. Criativos — direção Q1

### 7.1 Formatos por canal

| Canal | Formatos |
|---|---|
| Meta | single-image, carousel, video-15s, reels |
| Google Search | RSA (Responsive Search Ads) |
| LinkedIn | single-image, carousel, video, document |

### 7.2 Ângulos canônicos

| Ângulo | Descrição |
|---|---|
| Dor | Foco no problema do ICP (Schwartz problem-aware) |
| Ganho | Foco no resultado desejado |
| Social-proof | Depoimentos + logos clientes + cases |
| Comparação | Vs. status quo OU vs. competidor |
| Educacional | Long-form / how-to (ICP solution-aware) |

### 7.3 Quantidade inicial (por ICP × ângulo)

| ICP | Ângulo | Quantidade inicial |
|---|---|---|
| ICP-1 | Dor | <int> |
| ICP-1 | Ganho | <int> |
| ICP-1 | Social-proof | <int> |

### 7.4 Cadência de renovação
<weekly | bi-weekly | monthly>

### 7.5 Diretrizes de Direção de Arte + Copy System (handoff Fase 2)
- **Direção Arte:** seguir caminho visual aprovado (`10-fundacao/direcao-arte.md`)
- **Copy System:** seguir vocabulário canônico (`10-fundacao/copy-system.md`)
- **Família downstream Fase 2:**
  - `ad-design-image` (Camada Design IA — produz peça final)
  - `ad-design-video` (idem)
  - `ad-copy-meta` (Camada W-1 — produz copy)
  - `ad-copy-google-rsa` (idem)
  - `ad-copy-linkedin` (idem)

---

## 8. Cadência de testes

### 8.1 Hipóteses paid Q1 (subset GTM Plan §8)

#### H-paid-1
- **Enunciado:** "Se <X> então <Y>"
- **Métrica:** <CPL | CPA | ROAS | CVR | CTR>
- **Threshold validação:** "<X >= valor>"
- **Threshold falsificação:** "<X < valor>"
- **Deadline:** <YYYY-MM-DD>

#### H-paid-2
<mesma estrutura>

### 8.2 Framework de teste
<ab-test | multivariate | hold-out | ramp-up>

### 8.3 Cadência de revisão
<semanal | quinzenal>

### 8.4 Critério de kill
<custo de oportunidade + threshold mínimo>

### 8.5 Critério de scale
<critério de escalada de budget>

---

## 9. Métricas-alvo Q1

| Métrica | Valor alvo | Fonte (benchmark / Análise Histórica) |
|---|---|---|
| CPL alvo | R$ <valor> | <fonte> |
| CPA alvo | R$ <valor> | <fonte> |
| ROAS alvo | <valor> | <fonte> |
| CTR alvo | <%> | <fonte> |
| CVR Lead→MQL | <%> | <fonte> |
| CVR MQL→SQL | <%> | <fonte> |

**Cliente N0:** todas com benchmark Relatório Mercado §3 + ressalva de calibragem Q1.

---

## 10. Exclusões, pixels e CAPI

### 10.1 Exclusões de audiência
<lista>

### 10.2 Pixels CAPI por plataforma

| Plataforma | Eventos CAPI ativos |
|---|---|
| Meta | PageView, Lead, MQL, DealWon |
| Google Ads | conversion_lead, conversion_dealwon |
| LinkedIn | Lead Gen Form Submit, Site Visit, Conversion |

### 10.3 Eventos CAPI ativos (linka Measurement Plan §X)

### 10.4 Hash policy SHA-256 canônica
- Email: lowercase + trim + SHA-256 hex unsalted
- Phone: E.164 + SHA-256 hex unsalted
- CPF/CNPJ: numeric-only + SHA-256 hex unsalted

### 10.5 Event ID dedup UUID v4 (client + server)

---

## 11. Landing Pages e jornadas

| Campanha | LP alvo | ICP alvo | CTA |
|---|---|---|---|
| <campanha 1> | <path/URL> | <combinação> | <CTA> |
| <campanha 2> | <...> | <...> | <...> |

**Sinaliza LPs a produzir Fase 2 (família `lp-builder-*`):**
- LP-001: <descrição> — `lp-builder-b2b` ou `lp-builder-b2c`

---

## 12. Riscos e premissas paid

### 12.1 Top 3 riscos paid

| Risco | Severidade | Mitigação |
|---|---|---|
| Leilão saturado / CPM disparar | <alta/média/baixa> | <mitigação> |
| Queda de delivery | <...> | <...> |
| Mudança de algoritmo (iOS ATT / EU DMA) | <...> | <...> |

### 12.2 Premissas críticas com confidence

| Premissa | Confidence | Fonte |
|---|---|---|
| CTR esperado Meta = <%> | <alta/média/baixa> | <Análise Histórica §X | benchmark> |
| CVR Lead→MQL = <%> | <...> | <...> |

### 12.3 Sinais de reavaliação

- <sinal 1 com threshold quantitativo>
- <sinal 2>
- <sinal 3>
