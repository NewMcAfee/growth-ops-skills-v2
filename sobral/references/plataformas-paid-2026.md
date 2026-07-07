# Plataformas Paid 2024-2026 — Características Canônicas

> Reference canônica pra Passo A4 do `sobral` v2.0.0 — guia de plataformas paid SEM + Social Ads com objetivos canônicos, bid strategies, benchmarks de delivery 2024-2026 e critérios de seleção × ICP × modelo.

---

## Princípio canônico

**Cada plataforma serve etapas distintas do funil Bowtie.** Misturar plataformas sem coerência de objetivo gera diluição. Plano de Mídia define alocação por plataforma + objetivo coerente com alavanca Q1 do GTM Plan §4 + restrição principal subordinada do Cenário Baseline §2.

> **Regra dura V2 blocker §2:** alinhamento com GTM Plan §11.1 (canais paid priorizados batem). Não inventar plataforma fora do GTM Plan sem justificativa explícita.

---

## Meta Ads (Facebook + Instagram + Audience Network + Threads)

**Forças 2026:**
- Maior arsenal de targeting (interest + behavior + custom audiences + lookalikes 1-10%)
- CAPI maduro + EMQ scoring
- Advantage+ Shopping (catalog) + Advantage+ App Campaign + Advantage+ Audience (broad targeting AI)
- Reels weighting alto (formato dominante 2024-2026)

**Objetivos canônicos:**
| Objetivo Meta | Etapa Bowtie | ICP típico |
|---|---|---|
| Lead Gen | Engage / Convert | B2B + B2C alto envolvimento (form qualificador) |
| Sales (Conversions) | Convert | B2C transacional + e-commerce |
| Traffic | Attract | B2C + brand awareness com objetivo CTR |
| Awareness | Attract | Brand campaigns top-funnel |
| Engagement | Attract | B2C com community focus |
| App Promotion | Convert | Apps mobile |
| Catalog Sales | Convert | E-commerce com catálogo |
| Messages | Engage | B2B serviço local + WhatsApp Business API |

**Bid strategies canônicas:**
- Highest Volume (Auto) — default learning phase
- Cost Cap — controle CPL/CPA com ceiling
- Bid Cap — controle de leilão (avançado)
- ROAS Goal — modelo transacional com pixel de Purchase

**Benchmarks BR 2024-2026 (consenso WordStream + Meta + cases):**
- CPM: R$15-R$45 (B2C) / R$25-R$80 (B2B)
- CTR: 1.0-2.5% (Feed) / 0.8-1.5% (Stories) / 1.5-3.5% (Reels)
- CVR (Lead Gen → form complete): 3-12% (varia muito por nicho)

**Quando NÃO usar:**
- B2B Enterprise nichado (LinkedIn entrega melhor)
- Vertical regulado farmacêutico/financeiro restrito (compliance + restrições delivery)

---

## Google Ads — Search

**Forças 2026:**
- Intent-based (busca declarada — bottom-funnel natural)
- Brand keywords protection
- Long-tail SEO complementar
- Smart Bidding (Target CPA / Target ROAS / Maximize Conversions)

**Objetivos canônicos:**
- Search Conversions (default — direcionar tráfego pra LP qualificadora)
- Brand Search (defesa de marca)
- Competitor Search (ataque a competidor — controverso)

**Bid strategies canônicas:**
- Target CPA (default — cliente com pixel de conversão treinado)
- Target ROAS (modelo transacional)
- Maximize Conversions (learning phase)
- Manual CPC (legacy — operador experiente)

**Benchmarks BR 2024-2026:**
- CPC: R$0.80-R$8.00 (B2C) / R$3.00-R$25.00 (B2B competitivo)
- CTR Search: 5-12% (palavras-chave bottom-funnel) / 2-5% (mid-funnel)
- CVR: 5-15% (LP qualificadora bem feita) / 1-5% (LP genérica)

**Quando NÃO usar:**
- Cliente N0 sem nenhum search volume (Oraculo confirma volume <100 buscas/mês na keyword principal)
- Categoria nova sem keyword crystallized

---

## Google Ads — PMax (Performance Max)

**Forças 2026:**
- ML cross-canal (Search + Display + YouTube + Shopping + Discover + Maps)
- Asset groups com automação
- Catalog-driven (e-commerce)

**Cuidados 2024-2026:**
- Cliente sem dados base: PMax aprende mal (audience signal fraco)
- Black-box: limitada visibilidade de breakdowns
- ad_id forçado = `campaign_id` (PMax não expõe ad_id real — pattern UTM canônico Growth IA Ops respeita)

**Quando usar:**
- E-commerce com catálogo + ≥30 conversões/mês acumuladas
- Cliente com pixel maduro (90+ dias treinamento)
- Cliente quer escala max sem micro-gestão

**Quando NÃO usar:**
- Cliente N0 (PMax canibaliza Search Brand sem learning)
- Cliente quer controle granular (PMax = entregar à máquina)

---

## Google Ads — Display + YouTube

**Display:**
- Top-funnel (alcance)
- Remarketing pós-Search
- CPM baixo + CTR baixo (0.05-0.5%)

**YouTube:**
- Top-funnel (alcance vídeo)
- Mid-funnel (consideração via long-form)
- TrueView InStream (skippable após 5s) — pago só se visto ≥30s ou clicked
- Bumper Ads (6s não-skippable) — brand recall
- YouTube Shorts (formato vertical 2024-2026)

**Quando usar:**
- Brand awareness + reach top-funnel
- Remarketing visual (Display)
- Educação consultiva long-form (YouTube TrueView)

---

## LinkedIn Ads

**Forças 2026:**
- Targeting B2B único (job title + company + industry + seniority + skills)
- ICP B2B Enterprise + ABM (Account-Based Marketing)
- Lead Gen Forms nativos (form pre-fill via perfil)

**Objetivos canônicos:**
- Lead Generation (form nativo)
- Website Visits / Conversions
- Sponsored Messaging (InMail) — alto custo
- Document Ads (PDF nativo)
- Thought Leader Ads (post pago de Champion)

**Bid strategies:**
- Maximum Delivery (default)
- Cost Cap
- Manual CPC

**Benchmarks BR 2024-2026:**
- CPM: R$80-R$200 (premium vs Meta R$25-R$80)
- CPL Lead Gen: R$80-R$400 (B2B alto ticket sustenta CPL alto)
- CTR: 0.3-1.0% (audiência pequena + CPM alto = volume baixo)

**Quando usar:**
- B2B Enterprise ticket alto (sustenta CPL premium)
- ABM com lista de target accounts (Matched Audiences)
- Champion identification (Thought Leader Ads)

**Quando NÃO usar:**
- B2C (audiência errada)
- B2B SMB ticket baixo (CPL não sustenta)
- Cliente sem ICP nichado claro (LinkedIn rewards nichagem)

---

## TikTok Ads

**Forças 2026:**
- Algoritmo for-you-page (alcance orgânico extra)
- Audiência jovem (Gen Z + Millennial dominantes)
- Format vertical full-screen (immersive)
- Spark Ads (pagar pra promover post orgânico próprio ou de creator)

**Objetivos canônicos:**
- Web Conversions
- App Install
- Lead Generation
- Reach
- Catalog Sales (e-commerce)
- Community Interaction

**Benchmarks BR 2024-2026:**
- CPM: R$8-R$25
- CVR Lead Gen: 2-8%
- CPL: R$10-R$60 (B2C)

**Quando usar:**
- B2C consumer (especialmente jovens 16-35)
- Brands com creative arsenal forte (formato pede produção criativa)
- E-commerce com produto visual
- Influencer + Spark Ads (combo)

**Quando NÃO usar:**
- B2B Enterprise (audiência errada)
- Marca conservadora sem capacidade criativa pro formato
- Vertical regulado restrito (categoria farmacêutica/financeira tem alta moderação)

---

## X (Twitter) Ads

**Status 2024-2026:**
- Plataforma instável pós-acquisition (delivery oscilante)
- Audience inflada com bots (post-Musk)
- Targeting reduzido vs antigo Twitter
- Considerar **com cautela** + budget pequeno (≤R$3k/mês teste)

**Quando considerar:**
- Brand sócio-cultural + ICP tech / política / mídia
- Audience Twitter já testada com fit comprovado

**Quando NÃO usar:**
- Default — não está no top 5 plataformas paid 2024-2026 pra maioria das verticais

---

## Plataformas exóticas (TikTok B2B / Reddit / Twitch / Spotify / Podcast Ads / Quora)

Considerar caso a caso. §4 do Plano de Mídia ganha sub-seção justificando inclusão (audiência aderente ao ICP demonstrada via Análise Histórica ou Relatório Mercado). §5 estrutura de conta documenta limitações de tracking nativo. §10 CAPI pode não estar disponível — fallback código promocional ou survey-based attribution.

---

## Critérios de seleção × ICP × modelo

| Modelo | Plataforma #1 | Plataforma #2 | Plataforma #3 cond. |
|---|---|---|---|
| B2B SaaS Enterprise | LinkedIn | Google Search Brand+Competitor | Meta (retargeting) |
| B2B SaaS PLG | Google Search | Meta + LinkedIn (split) | YouTube TrueView |
| B2B Serviço (consultoria) | LinkedIn | Google Search | Meta (retargeting) |
| B2C Recurring (clube) | Meta | TikTok | Google Search Brand |
| B2C Transacional (e-commerce) | Meta | Google Shopping + PMax | TikTok |
| B2C Alto envolvimento (clínica/escola) | Google Search | Meta | LinkedIn (cond. premium) |
| Híbrido (PLG + Sales-led) | Google Search | LinkedIn | Meta |

---

## Anti-patterns (recusar)

- ❌ Inventar plataforma fora do GTM Plan §11.1 (V2 blocker)
- ❌ Misturar 5+ plataformas Q1 sem dados pra dispersão (foco em 2-3 plataformas-âncora)
- ❌ LinkedIn Ads em B2C (audiência errada)
- ❌ TikTok em B2B Enterprise (audiência errada)
- ❌ PMax em cliente N0 sem learning (canibaliza Brand sem signal)
- ❌ X Ads com budget grande Q1 (instabilidade — restrito a budget pequeno teste)
- ❌ Listar plataforma sem justificativa estratégica (§4.X.5 do template)

---

## Linkbacks

- Schema F1-21a §4 (Plataformas e canais)
- GTM Plan §11.1 (Canais paid priorizados — input formal blocker)
- 4 Fits do GTM Plan §3.2 (Product-Channel Fit — coerência canal × ICP)
- Cenário Baseline §3 (CAC benchmark — referência pra benchmark de plataforma)
- Família `media-buyer-*` v3 Fase 2 (executa nas plataformas — handoff downstream)

---

## Fontes

- Meta Ads Help Center (atualizado 2024-2026)
- Google Ads Help + Google Ads Editor (release notes 2024-2026)
- LinkedIn Ads Insights (B2B benchmarks 2024-2026)
- WordStream Industry Benchmarks (atualizado 2024-2026)
- TikTok for Business (case studies 2024-2026)
- Reforge Paid Acquisition curriculum (2024-2026)
