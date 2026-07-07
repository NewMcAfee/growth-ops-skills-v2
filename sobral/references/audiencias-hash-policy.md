# Audiências Paid + Hash Policy SHA-256 Canônica

> Reference canônica pra Passo A6 do `sobral` v2.0.0 — audiências paid (lookalikes / interesse / comportamento / retargeting / first-party / custom audience CRM / similar audience) + hash policy SHA-256 obrigatória + LGPD compliance + handoff `audience-architect` Fase 2.

---

## Princípio canônico

**Hash policy SHA-256 hex unsalted com normalização canônica** é regra dura cross-plataforma 2024-2026 (Meta CAPI + Google Customer Match + LinkedIn Matched Audiences + TikTok Custom Audience). **PII NUNCA em claro** — anonimização SHA-256 é obrigatória ANTES do upload pra plataforma. Sem isso = LGPD violado + plataforma rejeita upload (validação automática).

> **Regra dura V6 blocker §6:** audiências first-party com hash policy SHA-256 explícita declarada no Plano de Mídia.

---

## 7 tipos canônicos de audiência

### 1. Lookalike (LAL)
**Mecânica:** plataforma encontra usuários similares a um seed audience (custom audience source).

**Por plataforma:**
- **Meta:** Lookalike 1% (+similar — refinado), 2-5% (volume — menos similar), 6-10% (escala — diluído)
- **Google:** Similar Audiences (descontinuado parcial 2024 — substitução por Customer Match + Audience Insights)
- **LinkedIn:** Lookalike (B2B com job title + company match)
- **TikTok:** Custom Audience Lookalike (1-10%)

**Seed canônico:** DealWon últimos 90 dias (não Lead — Lead é diluído com NOICP)

**Tamanho estimado:** Meta 1% = ~2M usuários BR; 5% = ~10M; 10% = ~20M. Volume vs. similaridade trade-off.

### 2. Interesse / Comportamento
**Mecânica:** targeting declarado por interesses + comportamentos.

**Por plataforma:**
- **Meta:** Detailed Targeting (Interesses + Comportamentos + Demographics)
- **Google:** Affinity Audiences + In-Market Audiences + Life Events
- **LinkedIn:** Skills + Job Function + Company Industry + Member Groups
- **TikTok:** Interests + Behaviors + Hashtags

**Cuidado 2024-2026:** Meta + Google reduziram opções de targeting desde Apple ATT (iOS 14.5+) e EU DMA. Advantage+ Audience (Meta) + Smart Bidding (Google) tendem a substituir targeting manual.

### 3. Retargeting
**Mecânica:** audience de quem já interagiu com o site/app/conta.

**Janelas canônicas:**
- 7 dias — high intent (carrinho abandonado)
- 14-30 dias — médio intent (visitou LP)
- 60-90 dias — long-tail
- 180-365 dias — top-of-funnel (re-awareness)

**Cuidado:** Apple ATT + Safari ITP reduziram pixel coverage iOS pra ~30%. CAPI + first-party data compensam.

### 4. First-party (CRM upload)
**Mecânica:** upload de hash de email/phone/CPF do CRM próprio pra criar audience na plataforma.

**Casos canônicos:**
- DealWon → seed pra Lookalike
- DealLost → exclusion (pra não pagar pra retentar quem já recusou)
- Clientes atuais → exclusion (pra não pagar pra quem já compra)
- Trial users → audience de retargeting pra ativação
- Newsletter subscribers → audience pra cross-sell

**Hash policy SHA-256 obrigatória — V6 blocker:**
```
email: lowercase + trim espaços + SHA-256 hex unsalted
  ex: "  Email@EXAMPLE.com  " → "email@example.com" → SHA-256 = "973dfe463ec85785f5f95af5ba3906eedb2d931c24e69824a89ea65dba4e813b"

phone: E.164 normalization (+55 + DDD + número, sem espaços/parênteses) + SHA-256 hex unsalted
  ex: "(11) 98765-4321" → "+5511987654321" → SHA-256 = "..."

CPF: numeric-only (sem hífens/pontos) + SHA-256 hex unsalted
  ex: "123.456.789-00" → "12345678900" → SHA-256 = "..."

CNPJ: numeric-only + SHA-256 hex unsalted
nome completo: drop (não usar) — risco de mismatch
```

**LGPD compliance:**
- Lei 13.709 Art. 5º (PII anonimizada por hash não-reversível = dado não-pessoal pra propósitos de matching)
- Consent strings ativas (CMP — Consent Management Platform — IAB TCF v2.2 ou Google Consent Mode v2)
- Manter base de unsubscribed exclusions (não retargetar quem optou-out)

### 5. Custom Audience CRM (engagement-based)
**Mecânica:** audience baseada em comportamento dentro da plataforma (vídeo views, page engagement, lead form opens).

**Por plataforma:**
- **Meta:** Custom Audience from Engagement (vídeo 25%/50%/75%/95% + Page Likes + Lead Form abandonadas)
- **LinkedIn:** Page Engagement + Video Engagement
- **TikTok:** Engagement Audience (visualizações + interações)

**Janela:** 30-365 dias.

### 6. Similar Audience (deprecating)
Google deprecou Similar Audiences in-market 2024. Substituído por:
- Customer Match (upload first-party)
- Optimized Targeting (ML inferred audience)
- Audience signals dentro de PMax

### 7. Broad targeting (Advantage+ / Smart)
**Mecânica:** plataforma decide audience via ML (sem targeting manual ou com audience signal mínimo).

**Quando usar:**
- Cliente com pixel maduro (90+ dias treinamento)
- Cliente com ≥30 conversões/mês
- Quando targeting manual está saturado

**Quando NÃO usar:**
- Cliente N0 sem signal
- Cliente com vertical ultra-nichado (broad dilui)

---

## Exclusões canônicas (§6.X.5 + §10.1 do Plano de Mídia)

Lista exclusion audience por plataforma:
- **Clientes atuais** (CRM upload exclusion)
- **Leads <60 dias** (já em nutrição CRM — não pagar pra re-engajar)
- **Funcionários internos** (UTM tagging + IP exclusion)
- **DealLost <90 dias** (já recusou — não pagar pra retentar imediato)
- **Geográfica** (estados/cidades fora do ICP)
- **Demográfica** (idade fora do ICP — ex: clínica estética só 18+)
- **Behavioral** (Anti-ICP — herdado ICM §X)

---

## Anti-patterns (recusar)

- ❌ PII em claro no Plano de Mídia (V6 blocker — sempre SHA-256)
- ❌ Hash de email não-lowercase ou com espaços não-trimados (mismatch — plataforma rejeita)
- ❌ Hash de phone não-E.164 (Brasil = +55 + DDD + número)
- ❌ Salt no hash SHA-256 (cross-plataforma exige unsalted)
- ❌ Lookalike de Lead (não DealWon) — seed diluído com NOICP
- ❌ Lookalike 10% como default (volume sem similaridade)
- ❌ Sem exclusões declaradas (V6 alto — exclusões são guardrail de eficiência)
- ❌ Retargeting longo demais (>365d) sem justificativa (audience stale)
- ❌ First-party upload sem CMP/consent (LGPD violation)

---

## Linkbacks

- Schema F1-21a §6 (Audiências) + §10.1 (Exclusões)
- Taxonomia (`10-fundacao/taxonomia.md`) — canonização do hash policy SHA-256 cross-skill
- Measurement Plan (`10-fundacao/measurement-plan.md`) — define eventos CAPI que feedam audience engagement
- Contrato de Dados (`10-fundacao/contrato-de-dados.md`) — schema dos campos PII
- ICM (`10-fundacao/icm.md`) — Anti-ICP é input pras exclusões
- `audience-architect` Fase 2 — handoff downstream (escala audience strategy operacionalmente)

---

## Fontes

- Meta Business Help Center — Customer Lists + CAPI hash specifications (atualizado 2024-2026)
- Google Ads Help — Customer Match data hashing requirements (atualizado 2024-2026)
- LinkedIn Marketing Solutions — Matched Audiences specifications
- TikTok for Business — Custom Audience hashing
- IAB TCF v2.2 — Consent string spec
- LGPD Lei 13.709 (especialmente Art. 5º + Art. 7º + Art. 18º)
- Apple ATT (iOS 14.5+) + EU DMA (Digital Markets Act 2024)
