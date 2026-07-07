# darwin — Metodologia e evidência (2024-2026)

> Carregado sob demanda. Base de evidência que ancora as decisões do `darwin`. Cada bloco cita fonte.

## §0 — Regras aplicadas (extraídas e validadas da pesquisa — o `darwin` APLICA, não só cita)

Estas são as práticas já validadas no estado da arte que o `darwin` operacionaliza para ser
definitivo. Cada uma deriva da evidência nos §1-§5.

**Análise / tiers:**
- **Tier campeão** = termo `conv>0`; priorize o top ~20% (mais conv / menor CP-conv) para
  reaproveitar em copy + virar grupo dedicado. **Tier perdedor/desperdício** = `conv=0` com gasto
  (ou `0 conv + 3+ cliques` / `CPA > 2× alvo` quando há cliques/alvo) → negativa. (§1)
- **% de gasto produtivo** (efficient spend) = custo em termos `conv>0` ÷ custo total. Reporte
  sempre — é o número que separa gasto produtivo de desperdiçado. (§1)
- **N-gram / cauda longa:** agregue raízes; não descarte termo por baixo volume individual. (§1)
- **Conflict-check** antes de TODA negativa: nunca bloqueie um termo campeão. (§1)

**Estrutura (recomendação no mapa intenção→campanha):**
- Isolar por **intenção/temperatura**; **branded isolado** + brand-negatives em todo o resto;
  1 cluster por concorrente. (§2)
- **tCPA-hint por ICP/segmento** (nunca blended): ≥ CPA observado; ≥30 conv/mês/campanha senão
  use **portfolio** tCPA; não editar tCPA antes de ~3 sem + ~60 conv. (§2)
- **1 campanha de teste** com ângulos novos (além dos campeões).

**PMax (recomendação):** **1 asset group** em baixo volume → fragmentar até **8-12** após >30 conv/30d;
**Brand Exclusion** no go-live (91% das contas canibalizam); search themes com indicador de
"usefulness"; negativas account ≤1.000 / campaign ≤10.000. (§4)

**RSA / copy (guidance entregue ao `media-buyer-google`):**
- **Sentence case > Title Case (3,7× no CPA)** — preferir copy human-like. (§3)
- **Diversidade de assets:** cobrir feature / benefit / prova / CTA, sem redundância; refinar asset
  fraco antes de adicionar novos. (§3)
- **Ad Strength ≠ performance** — não otimizar pra "Excelente" às cegas. (§3)
- **Partial-pin do título #1** é alternativa validada (default = instrução do operador "sem pin"). (§3)
- **Podar título 0-conv** com >500 impressões (reporting por título). (§3)
- **Cadência de refresh por volume:** 8-12 sem (<100k impr/mês) · 6-8 sem (100k-1M) · 4-6 sem (>1M). (§3)
- **Anti-AI-slop:** passe editorial humano; evitar templates ("o melhor", "confiado por milhões",
  "oferta por tempo limitado"). (§3)

**Operação:** cadência de re-análise do `darwin` = **quinzenal** (semanal se Broad Match ou gasto
> R$ 5k/mês). Recomendar **GCLID→CRM / import offline de conversão** quando ausente — fecha o loop
de qualidade do bidding (raiz de desperdício nº4 do GrowthSpree). (§1, §3)

---

## 1. Análise de termos: n-gram + tiers campeão/perdedor

- **N-gram layered analysis (dual scoring).** Segmente termos em 1/2/3-grams; pontue por
  Regular Score (performance geral) E Efficient Score (só termos no CPA/ROAS-alvo) → isola que
  parcela do gasto é produtiva. Milhões de termos → 30-50k n-grams.
  <https://googleadsopenresearch.com/research/advanced-ngram-analysis/>
- **Tiers.** Campeões = top ~20% (conv em baixo custo / CPA < 50% alvo) → reaproveitar em copy +
  criar grupos. Perdedores = bottom ~15% (0 conv + 3+ cliques OU CPA > 2× alvo) → negativas.
  <https://www.revenuehero.io/playbooks/n-gram-analysis-google-ads>
- **7 raízes de desperdício (B2B SaaS).** search-term efficiency · PMax audience quality ·
  attribution window · GCLID-CRM · smart bidding training data · campaign structure · geo.
  Waste = gasto em queries sem conversão + leads que não viram SQL em 90d.
  <https://www.growthspreeofficial.com/blogs/b2b-google-ads-waste-report-11m-lost-43-enterprise-saas-accounts>
- **Cauda longa.** Não rejeitar termo por baixo volume individual: 50 variações × 2 cliques
  convertem juntas (agregação em n-gram revela a gema).
- **Conflict-check.** Nunca adicionar negativa que bloqueie termo de alto valor (ex: "free" mata
  "free trial" 8:1). É o erro nº1 da mineração automática de negativas.

## 2. Estrutura de conta: intenção/temperatura, brand, tCPA

- **STAG/SIAG** (single-theme / single-intention ad group): 5-15 keywords mesma intenção/grupo,
  ad+LP+bidding dedicados. Substituiu SKAG (close variants desde 2018 tornaram SKAG over-fragmentado).
  <https://www.groas.com/post/google-ads-account-structure-in-2026-the-framework-that-actually-works> ·
  <https://oxedent.co.uk/skag-vs-siag-vs-stag-in-google-ads/>
- **Isolamento de branded.** Branded ROAS ~1299% vs non-branded ~68%; conversão 2-4× maior.
  Campanha de marca separada + lista "Brand Negatives" aplicada a todo o resto (evita competição interna).
  <https://www.echelonn.io/post/google-ads-campaign-structure-why-95-of-brands-waste-budget-on-mixed-traffic>
- **Portfolio tCPA por economia.** Não misture brand (CPA natural baixa) com não-brand competitivo
  (CPA alta) no mesmo portfolio/campanha → distorce o algoritmo. Cada ICP/segmento com CPA natural
  distinto = seu próprio tCPA. <https://30chars.com/blog/target-cpa/>
- **Thresholds.** tCPA exige ≥30 conv/mês/campanha (tROAS ≥50). **Não lance tCPA abaixo do CPA
  observado** (afoga impressão antes de aprender). **Não edite tCPA antes de ~3 semanas + ~60 conv.**
  <https://support.google.com/google-ads/answer/6268632>

## 3. RSA: o que a evidência diz (refina nosso padrão)

- **Ad Strength NÃO correlaciona com performance.** Optmyzr 20k contas: Average AS = melhor CPA
  ($12,43); Excellent AS = pior CPA ($28,68). Ad Strength = completude estrutural (diagnóstico),
  não preditor de eficácia. → não otimizar pra "Excelente" às cegas.
  <https://www.optmyzr.com/blog/google-rsa-performance-study/>
- **Partial pinning (só título #1) ≥ full-unpinned.** CPA $13,68 · CTR 11,88% · ROAS 365% —
  supera full-pin E no-pin. Garante a mensagem-core sem matar combinações.
  <https://kioskagency.com/blog/paid-media/google-ads-headlines-to-pin-or-not-to-pin/>
  > **Nota de governança:** o operador definiu "sem pin" (preserva Ad Strength). `darwin` documenta
  > o achado de partial-pin como ALTERNATIVA baseada em evidência; o default segue a instrução do operador.
- **Sentence case > Title Case (3,7× CPA).** Sentence case: CPA $7,46 · CVR 12,5%. Title case:
  CPA $27,47. Copy human-like supera tom corporativo. → preferir sentence case nas RSAs.
  <https://hawksem.com/blog/rsas-responsive-search-ads/>
- **Diversidade de assets.** 15 títulos + 4 descrições = ~45k combinações; cobrir feature/benefit/
  prova/CTA, sem redundância; asset fraco puxa a média (refine antes de adicionar novos).
  <https://support.google.com/google-ads/answer/11894820>
- **Reporting por título** (2024): pode-se podar título 0-conv com >500 impressões.
  <https://support.google.com/google-ads/answer/9564897>
- **AI-slop (política Google 2026).** Conteúdo gerado por IA sem disclosure = risco de compliance;
  Google detecta padrões generativos. Exigir passe editorial humano; evitar templates ("o melhor",
  "confiado por milhões", "oferta por tempo limitado"). <https://www.groas.com/post/google-ads-ai-generated-content-label-requirement-2026-compliance-guide>

## 4. Performance Max

- **Asset groups.** Google moveu de 3-5 para **8-12** asset groups (34% melhor) — MAS gated por
  volume: não crie mais campanhas/grupos que o volume de conversão sustenta (30-50 conv/mês = 1-2).
  Por isso, em conta de baixo volume, **1 asset group amplo no go-live** e fragmentar depois.
  <https://www.groas.ai/post/performance-max-updates-november-2025-week-3---complete-changes-optimization-guide>
- **Search themes:** até 50/asset group (era 25), com indicador de "usefulness".
  <https://support.google.com/google-ads/answer/14528220>
- **Learning:** 20-30 conv/mês = mínimo p/ sair do learning (4-6 sem); 50+ ideal.
  <https://www.groas.com/post/google-ads-learning-phase-explained-why-your-campaigns-need-2-weeks-to-work-and-how-to-stop-resetting-it>
- **Negativas:** account-level máx 1.000 (support/login/free/salary); campaign-level **10.000**
  (era 100 até Mar/2025). <https://groas.ai/post/performance-max-negative-keywords-2025-complete-guide-to-the-10-000-keyword-limit>
- **Canibalização:** 91,45% das contas têm overlap Search×PMax (Optmyzr, 503 contas). Search ganha
  CVR 84% quando ambos elegíveis → Search prioritário; **Brand Exclusion** no PMax; exata + account
  negatives p/ queries do Search. <https://www.optmyzr.com/blog/is-pmax-cannibalizing-search/>

## 5. Output de auditoria PPC excelente (traços)

Segmentado por intent (não blended) · campeões = top 20% com rec de bid-up + novo grupo · perdedores =
bottom 15% com negativas prontas pra one-click · análise layered (1-gram → drill 2/3-gram) ·
conflict detection · transparência de metodologia (thresholds, janela, volume analisado) ·
exportável (CSV/YAML) e acionável ("26 negativas prontas", "novo grupo para n-gram X").
Fontes: RevenueHero, Optmyzr, PPC Hero, Search Engine Land (ver §1-§4).

## 6. A lacuna que darwin preenche

Nenhuma fonte conecta **n-gram de termos campeões ↔ DNA de copy campeã ↔ mapa de campanha**.
Tools fazem n-gram OU auditoria de waste OU stats de RSA — isoladamente. `darwin` é a ponte:
termo que sobreviveu (conv>0) + anúncio que sobreviveu (DNA) → nova campanha (campeão + 2 variações +
1 teste), pronta pro `sobral`/`media-buyer-google`. Premissa: conversão = evento acordado (MQL ≠ lead).
