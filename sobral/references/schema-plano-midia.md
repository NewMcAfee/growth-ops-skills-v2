# Schema F1-21a — Plano de Mídia (versão completa)

> Reference canônica do schema do output `plano-midia.md` produzido pelo `sobral` v2.0.0 (Fase A). Espelha o catálogo formal `arquitetura/schemas/fase-1/plano-midia.md` (B7.1b-ii — 2026-05-08).

---

## Path canônico

`30-decisoes/plano-midia.md`

## Metadata canônica

- **Output ID:** F1-21a
- **Categoria:** 3 — Decisão (Princípio 9)
- **Schema version:** 1.0.0
- **Fase:** Fase 1 (Fundação)
- **Subfase:** 1.4.2 (paralelo a Plano de Conteúdo)
- **Cadência:** one-shot baseline (recalibrado em Sprint trimestral via re-execução parcial — schema separado deferido B7.1c)
- **Skill produtora:** `sobral` v2.0.0 (co-produz com Forecasting F1-21b)
- **Linha de Visibilidade:** abaixo (cliente não vê — operador owna execução)

---

## Frontmatter canônico (17+ campos)

```yaml
output_type: plano-midia
ticker: <string>
data_construcao: <YYYY-MM-DD>
horizonte: Q1 | semestre | ano
status: rascunho | revisado-operador | aprovado-cliente
versao: <SemVer>
modelo_negocio: <enum>
cliente_n0: true | false
confidence_geral: alta | media | baixa
budget_total_q1:
  valor: <float>
  moeda: BRL
  distribuicao_mensal:
    m1: <float>
    m2: <float>
    m3: <float>
plataformas:
  - id: meta-ads | google-ads-search | google-ads-pmax | google-ads-display | google-ads-youtube | linkedin-ads | tiktok-ads | x-ads
    budget_q1: <float>
    pct_total: <float>
    bowtie_etapa: attract | engage | convert | expand | nurture
    icp_combinacoes: <list>
    objetivo_canal: leads | conversions | engagement | reach | retention | retargeting
estrutura_conta:
  - plataforma: <id>
    campanhas:
      - nome: <gerado por name-templates.yml>
        objetivo: <plataforma-specific>
        adsets_estimados: <int>
        criativos_iniciais: <int>
        budget_diario: <float>
        bid_strategy: <plataforma-specific>
audiencias:
  - plataforma: <id>
    tipo: lookalike | interesse | comportamento | retargeting | broad | first-party | custom-audience-crm | similar-audience
    tamanho_estimado: <int | range>
    fonte: <string>
    icp_alvo: <combinação ICP×Produto>
criativos:
  - canal: <id>
    formatos: <list>
    angulos: <list>
    quantidade_inicial: <int>
    cadencia_renovacao: weekly | bi-weekly | monthly
cadencia_testes:
  hipoteses_paid_q1:
    - id: H-paid-1
      enunciado: <string>
      metrica: CPL | CPA | ROAS | CVR | CTR
      threshold_validacao: <string>
      threshold_falsificacao: <string>
      deadline: <YYYY-MM-DD>
  cadencia_revisao: semanal | quinzenal
  framework_teste: ab-test | multivariate | hold-out | ramp-up
metricas_alvo_q1:
  cpl_alvo: <float>
  cpa_alvo: <float>
  roas_alvo: <float>
  ctr_alvo: <float>
  cvr_lead_mql: <float>
  cvr_mql_sql: <float>
  share_of_budget_por_canal: <map>
exclusoes_e_pixels:
  exclusoes_audiencia: <list>
  pixels_capi:
    - plataforma: meta | google-ads | linkedin
      eventos_capi: <list>
      hash_policy_email_phone: sha256-canonical
landing_pages:
  - campanha_id: <referência name-templates>
    lp_alvo: <path no vault Fase 2 ou URL externa>
    icp_alvo: <combinação>
    cta: <string>
linkbacks:
  gtm_plan: 30-decisoes/gtm-plan.md
  cenario_baseline: 20-snapshots/YYYY-MM/cenario-baseline.md
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
```

---

## 12 seções obrigatórias

| # | Seção | Conteúdo | Critério completude |
|---|---|---|---|
| 1 | `## Sumário executivo` | budget · canais · objetivos · meta CPL/CPA/ROAS · cadência testes (4-6 parágrafos) | Endereça 5 elementos |
| 2 | `## Alinhamento com GTM Plan` | 2.1 Restrição subordinada · 2.2 Loops paid alimenta · 2.3 ICP×Produto servidas · 2.4 Anti-canais | 4 sub-seções; subordinação explícita |
| 3 | `## Budget e alocação` | 3.1 Budget Q1 + distribuição mensal · 3.2 Por plataforma (% + valor) · 3.3 Por etapa Bowtie · 3.4 Por ICP×Produto | 4 sub-seções; soma = 100% |
| 4 | `## Plataformas e canais` | Por plataforma (≥2): objetivo + ICP servidas + Bowtie + tipo + justificativa | ≥2 plataformas; coerência 4 Fits |
| 5 | `## Estrutura de conta` | Por plataforma: campanhas (name-templates) + adsets + criativos + budget diário + bid strategy | Pattern UTM canônico Growth IA Ops |
| 6 | `## Audiências` | Por plataforma + tipo: LAL + interesse + retargeting + first-party (hash SHA-256) + exclusões | Tamanhos estimados; hash policy explícita |
| 7 | `## Criativos — direção Q1` | 7.1 Formatos · 7.2 Ângulos · 7.3 Quantidade ICP×ângulo · 7.4 Cadência renovação · 7.5 Diretrizes Direção Arte + Copy System (handoff Fase 2) | ≥3 ângulos; cadência declarada |
| 8 | `## Cadência de testes` | 8.1 Hipóteses paid Q1 · 8.2 Framework · 8.3 Cadência revisão · 8.4 Kill criteria · 8.5 Scale criteria | ≥2 hipóteses paid falsificáveis |
| 9 | `## Métricas-alvo Q1` | CPL · CPA · ROAS · CTR · CVR Lead→MQL · CVR MQL→SQL · Share-of-budget | ≥5 métricas com valor numérico |
| 10 | `## Exclusões, pixels e CAPI` | 10.1 Exclusões audiência · 10.2 Pixels CAPI · 10.3 Eventos CAPI ativos · 10.4 Hash SHA-256 · 10.5 Event ID UUID v4 | Coerência Measurement Plan |
| 11 | `## Landing Pages e jornadas` | Mapeamento campanha × LP × ICP × CTA | LP por campanha; CTA coerente Bowtie |
| 12 | `## Riscos e premissas paid` | 12.1 Top 3 riscos + mitigação · 12.2 Premissas críticas (CTR/CVR fonte) · 12.3 Sinais reavaliação | Riscos + premissas + sinais |

---

## Critérios de validação V1-V14

| # | Critério | Severidade |
|---|---|---|
| V1 | Frontmatter parseável + 12 seções | **blocker** |
| V2 | §2 alinhamento GTM Plan §11.1 (canais paid batem) | **blocker** |
| V3 | §3 soma % por plataforma = 100% ±1% | **blocker** |
| V4 | Pattern UTM canônico Growth IA Ops respeitado (não V4 OS hierárquico) | **blocker** |
| V5 | §5 nomes seguem `name-templates.yml` da Taxonomia | **blocker** |
| V6 | §6 audiências first-party com hash SHA-256 explícita | **blocker** |
| V7 | §7 ≥3 ângulos criativos por ICP — não copy-paste cross-ICP | alto |
| V8 | §8 ≥2 hipóteses paid falsificáveis com thresholds quantitativos | **blocker** |
| V9 | §9 métricas-alvo com valor numérico (cliente N0 = benchmark com fonte) | **blocker** |
| V10 | §10 pixels CAPI listados coerentes com Measurement Plan | **blocker** |
| V11 | §11 toda campanha tem LP mapeada (ou justificativa "campanha sem LP") | alto |
| V12 | §12 ≥3 riscos + ≥3 premissas com confidence | médio |
| V13 | Cross-link bidirecional GTM Plan + Forecasting + Manifest v1.0 | **blocker** |
| V14 | Cliente N0: `cliente_n0: true` + `confidence: baixa` + benchmarks com fonte | **blocker** (cond.) |

---

## 8 edge cases canônicos

### 5.1 Cliente N0
`cliente_n0: true` + `confidence: baixa`. §9 métricas com benchmark Relatório Mercado §3 (não inventadas). §3 budget conservador (Q1 = "calibrar"; Q2 = "escalar"). §8 hipóteses testam premissas básicas. §12 risco crítico: "Métricas são hipóteses; primeiros 30-45 dias = calibrar".

### 5.2 Cliente com runway curto (<6 meses)
§3 budget enxuto + foco bottom-funnel (retargeting + paid search bottom-funnel). §4 plataformas reduzidas (1-2 canais máximo). §7 criativos focados em conversão direta. §8 cadência mais agressiva (revisão semanal + kill rápido). §9 ROAS alvo > LTV/CAC unitário do Cenário Baseline.

### 5.3 Modelo recurring vs. transacional vs. híbrido
§9 métricas divergem: SaaS = CPL + CVR Lead→MQL→SAL→DealWon + LTV implícito; Transacional = CPA + ROAS + AOV; Híbrido = ambas em sub-tabelas separadas. §6 audiências divergem: SaaS valoriza LinkedIn/job titles; Transacional valoriza Meta lookalike + interesse + compras anteriores.

### 5.4 Cliente B2B com ciclo longo (3-6 meses)
§9 métricas mais leading: CPL + CVR Lead→MQL (não CPA imediato). §11 LPs viram conteúdo + form qualificador (não checkout). §6 audiências valorizam first-party CRM upload (lookalike de DealWon histórico). Forecasting (1.4.2 separado) lida com defasagem temporal.

### 5.5 Cliente B2C alto envolvimento (clínica, escola, plano saúde, financeiro premium)
§11 LPs com qualificação (form 3-5 perguntas) + agendamento. §6 retargeting com janelas longas (30-90 dias). §7 ângulos com prova social forte (depoimentos + selos + urgência). §8 hipóteses incluem "qual ângulo converte melhor pro ICP X" (educacional vs. urgência vs. desejo).

### 5.6 Vertical regulado (saúde, fintech, jurídico, farmacêutica)
§4 plataformas com restrições documentadas (anúncio farmacêutico Meta exige certificação; CFM proíbe certas claims; CONAR + ANVISA). §7 criativos passam por Claim Audit (linka Da Vinci §5). §10 hash policy + LGPD compliance (consent strings). §12 risco crítico: rejeição anúncios + multa regulatória.

### 5.7 Plataforma exótica (TikTok B2B, Twitch, podcast ads, OOH)
§4 ganha sub-seção justificando inclusão (audiência aderente ao ICP demonstrada via Análise Histórica ou Relatório Mercado). §5 estrutura de conta documenta limitações de tracking nativo. §10 CAPI pode não estar disponível — fallback OOH/podcast usa códigos promocionais ou survey-based attribution.

### 5.8 Re-execução parcial em Sprint trimestral
`versao` SemVer bump (1.0.0 → 1.1.0+). Adendo `## Recalibragem Sprint Q?` agregado preservando histórico. Métricas-alvo Q+1 declaradas com base no realizado Q. Hipóteses paid fechadas viram §13 com status final. Schema separado `fase-3/plano-midia-recalibragem-sprint.md` deferido B7.1c.

---

## Linkbacks bidirecionais

### Upstream
- F1-20 GTM Plan (§11.1 + §6 + §7 + §9 — input formal blocker)
- F1-19 Cenário Baseline (§3-4 + §6 funil — input blocker)
- F1-15 Taxonomia (UTM + name-templates + extensions — input blocker)
- F1-17a-b Measurement Plan + Contrato de Dados (CAPI + eventos — input blocker)
- F1-10b ICP Product Map (input blocker)
- F1-7 Relatório Mercado (CAC benchmark — input alto)
- F1-18 Análise Histórica cond. (input alto cliente N1+)
- F1-11 Direção de Arte + F1-12 Design System + F1-13 Copy System (input alto)

### Downstream
- F1-21b Forecasting (consome §3 + §9 + §8 hipóteses paid — co-produção mesma skill)
- F1-22 Plano de Conteúdo (sinergia paid+orgânico — paralelo)
- F1-23 Manifest v1.0 (consome inteiro)
- F1-25 GTM Deck cond. (sumário paid no deck)
- F2 família `media-buyer-*` v3 (consome §5 estrutura conta — execução nas plataformas)
- F2 família `ad-design-*` (consome §7 direção criativa)
- F2 família `ad-copy-*` (consome §7 ângulos)
- F2 família `lp-builder-*` (consome §11 LPs mapeadas)
- F2 `audience-architect` (consome §6 audiências)

### Princípios incidentes
- **P1** (Especialização — Plano Mídia ≠ Plano Conteúdo ≠ Forecasting; bounded contexts disjuntos)
- **P3** (Workflow — handoff formal pra família `media-buyer-*` Fase 2)
- **P9** (Estado vs. Decisão — Plano de Mídia é Decisão)
- **P5** (Camadas — direciona Framework→Skill→MCP→App pra família tracking-* + media-buyer-*)

---

## Histórico de schema

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 2026-05-08 | Schema inicial (B7.1b-ii) — alocação por canal × ICP×Produto + estrutura conta com pattern UTM canônico Growth IA Ops + audiências com hash SHA-256 + criativos com handoff família `ad-design-*`/`ad-copy-*` + cadência testes com hipóteses falsificáveis paid; recalibragem Sprint trimestral mapeada (schema separado deferido B7.1c) |
