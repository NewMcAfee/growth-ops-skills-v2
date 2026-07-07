# Workflow MCP Meta — Caminho A da Skill

Referência operacional pra estruturar campanha Meta Ads via MCP oficial da Meta (lançado em 29-abr-2026, https://mcp.facebook.com/ads). Caminho único da skill (MCP-only) — exige `is_ads_mcp_enabled=true` na conta-alvo.

---

## Pré-requisitos

1. **MCP da Meta conectado na sessão.** Em Claude Code: validar via `claude mcp list` que `meta-ads` aparece como conectado. Se não conectado, instalar via `claude mcp add --scope user --transport http meta-ads https://mcp.facebook.com/ads`.
2. **Conta com flag `is_ads_mcp_enabled=true`.** Validar via `ads_get_ad_accounts` antes de prometer execução. Se false → operador executa manualmente no Ads Manager (esta skill é MCP-only, não gera CSV).
3. **Authorization OAuth completa.** ⚠️ **Bug Anthropic conhecido** ([anthropics/claude-code#37747](https://github.com/anthropics/claude-code/issues/37747)): OAuth do MCP Meta falha em Claude Code com erro `redirect_uris are not registered`. **Workaround:** autenticar via Claude.ai web (que tem redirect_uri pré-registrado), e chamar as tools de lá. Issue da Anthropic, não da Meta.
4. **Plano Sobral aprovado** com decisão clara: padrão DCO (A/B/C), eventos a otimizar, budget shares, exclusões waterfall.

---

## Tools relevantes (29 total no MCP da Meta)

### Discovery / setup
- `ads_get_ad_accounts` — lista contas + flag `is_ads_mcp_enabled`
- `ads_get_pages_for_business` — Pages do FB do business pra associar aos ads
- `ads_get_help_article` — referência da própria Meta

### Criação (CRUD)
- `ads_create_campaign` — cria campanha
- `ads_create_ad_set` — cria conjunto
- `ads_create_ad` — cria anúncio (suporta dynamic_creative=true)
- `ads_update_entity` — edita campos de campanha/conjunto/anúncio
- `ads_activate_entity` — sai de PAUSED → ACTIVE (sempre criar PAUSED, ativar depois)

### Leitura / debug
- `ads_get_ad_entities` — lista entidades existentes
- `ads_get_errors` — diagnóstico de erros recentes
- `ads_get_opportunity_score` — sugestões automáticas da Meta

### Catalog (e-commerce — não usado em B2B Lead Ads tradicional)
- `ads_catalog_*` (10 tools) — pra projetos com catálogo dinâmico

### Dataset / Pixel / CAPI
- `ads_get_dataset_details` — info do Pixel
- `ads_get_dataset_quality` — EMQ score por evento
- `ads_get_dataset_stats` — volume de eventos

### Insights (pra Newton ler depois)
- `ads_insights_advertiser_context`
- `ads_insights_anomaly_signal`
- `ads_insights_auction_ranking_benchmarks`
- `ads_insights_industry_benchmark`
- `ads_insights_performance_trend`

---

## Sequência de execução (criar campanha completa)

### Fase 1 — Discovery (sempre primeiro)

```
1. ads_get_ad_accounts
   → guarde: ad_account_id, business_id, is_ads_mcp_enabled
   → se is_ads_mcp_enabled = false na conta-alvo: PARE — operador executa manualmente no Ads Manager (skill é MCP-only)

2. ads_get_pages_for_business(business_id)
   → guarde: page_id da Page do FB que vai associar aos ads
   → se mais de uma Page: pergunte ao operador qual usar
```

### Fase 2 — Pre-flight tracking (validar antes de criar)

```
3. ads_get_dataset_details(pixel_id)
   → confirma Pixel existe e ativo
   → confirma CAPI status

4. ads_get_dataset_quality(pixel_id)
   → checa EMQ score atual dos eventos relevantes (Lead, MQL, Purchase)
   → se EMQ < 6.0 em eventos críticos: alertar operador antes de subir
```

### Fase 3 — Criação (sempre status PAUSED)

```
5. ads_create_campaign(...)
   → name: EVER_META_MQL_CursoLongo_Frio (taxonomia de entidade Growth IA Ops — Convenção B)
   → objective: OUTCOME_LEADS / OUTCOME_SALES / etc
   → status: PAUSED (sempre)
   → buying_type: AUCTION
   → special_ad_categories: [] (vazio se não aplicável)
   → guarde: campaign_id retornado

6. Pra cada conjunto (loop):
   ads_create_ad_set(campaign_id=..., ...)
   → name: AUD-{N}-{SEQ}_{FUNIL}_{TIPO}_{PUBLICO}_{GEO}_{DEMO}_{FORMATO}
   → daily_budget OU lifetime_budget (não ambos)
   → optimization_goal: LEAD_GENERATION / OFFSITE_CONVERSIONS / etc
   → billing_event: IMPRESSIONS (default Lead Ads)
   → bid_strategy: LOWEST_COST_WITHOUT_CAP (Maximize Leads)
   → targeting: { geo_locations, age_min, age_max, custom_audiences (incluir/excluir) }
   → exclusões waterfall conforme dígito (ver waterfall-exclusions.md)
   → promoted_object: { pixel_id, custom_event_type } se otimizar pra MQL via CAPI
   → status: PAUSED
   → guarde: ad_set_id retornado

7. Pra cada anúncio (loop):
   ads_create_ad(ad_set_id=..., ...)
   → SE single-creative: name AD-{SEQ}_..., creative={creative_id}
   → SE Dynamic Creative: name {DROP}_{SEQ}_..._DCO,
       creative_spec={
         dynamic_creative: true,
         asset_feed_spec: {
           images/videos: [...],
           bodies: [{text: "..."}, ...],     # até 5
           titles: [{text: "..."}, ...],     # até 5
           descriptions: [{text: "..."}, ...], # até 5
           call_to_action_types: [...]
         }
       }
   → status: PAUSED
   → guarde: ad_id retornado
```

### Fase 4 — Validação

```
8. ads_get_ad_entities(filter=campaign_id)
   → confirma estrutura criada
   → checa nomes contra taxonomia (mental ou via diff)

9. Apresenta sumário pro operador:
   - Campanha criada: {name}, {campaign_id}
   - N conjuntos: nomes + budgets + targeting summary
   - N anúncios: nomes + dynamic_creative on/off
   - Status: PAUSED em todos (operador ativa via UI ou ads_activate_entity)
```

### Fase 5 — Handoff

Pra Growth IA Ops: registrar os IDs criados (campanha, conjuntos, anúncios) no pipeline.

---

## Suporte a Dynamic Creative

> Doutrina estratégica do DCO (princípio narrativa-first, hierarquia M×N, regras operacionais, leitura por breakdowns) está em [`estrutura-dco.md`](estrutura-dco.md). Esta seção cobre só a tradução pro payload MCP.

Quando o plano Sobral indicar **Padrão A (DCO por Narrativa — recomendado)** ou Padrão B (DCO por Formato — pouco usado):

1. **Não criar 1 ad por creative** — criar 1 ad container DCO com múltiplos creatives dentro
2. **Naming hierárquico:** ad container = `{DROP}_{SEQ}_{FORMATO}_{NARRATIVA}_{CONSCIÊNCIA}_{GANCHO}_DCO`; criativos individuais = `CRT-*` (ver `taxonomia-entidade-meta.md` seção "Naming hierárquico DCO")
3. **No payload de `ads_create_ad`:** setar `dynamic_creative=true` no `creative_spec` e popular `asset_feed_spec` com os arrays de bodies/titles/descriptions/imagens/vídeos
4. **Ler relatório depois (Newton):** usar `ads_insights_*` com breakdown por `body_asset`, `title_asset`, `description_asset`, `image_asset`, `video_asset`

Único padrão que NÃO usa DCO: **Padrão C (single-creative)** — aí cria 1 ad por creative, naming legacy `AD-*`.

---

## Placement Asset Customization (feature 2026)

Permite customizar qual asset vai pra qual placement dentro do mesmo ad. Útil pra DCO ou single-creative quando o operador tem versões otimizadas por placement (ex: Feed 1:1 + Stories 9:16 do mesmo conceito).

No `asset_feed_spec`, adicionar campo `asset_customization_rules` com regras condicionais por `publisher_platforms` / `placements`. Detalhes na doc Meta.

---

## Anti-padrões MCP

- ❌ Criar ad com `dynamic_creative=true` mas só 1 asset — Meta aceita mas não otimiza nada (precisa ≥2)
- ❌ Pular `ads_get_dataset_quality` antes de subir — descobrir EMQ baixo depois é desperdício de budget
- ❌ Status ACTIVE direto na criação — sempre PAUSED, ativação manual depois pelo operador
- ❌ Usar MCP em conta com `is_ads_mcp_enabled=false` — vai dar 403/erro semântico
- ❌ Ignorar OAuth fail no Claude Code — não fica "tentando até funcionar"; ir pro Claude.ai web

---

## Limitações conhecidas

| Limitação | Mitigação |
|---|---|
| OAuth fail no Claude Code | Usar Claude.ai web pra autenticar |
| Rollout gradual per-account | `ads_get_ad_accounts` + checar `is_ads_mcp_enabled` antes |
| Não cria Custom Audience pelo MCP (lê só) | Operador cria audience no Ads Manager UI manualmente; MCP só referencia pelo ID |
| Não faz upload de creative pelo MCP em alguns casos | Asset Library do operador deve ter `image_hash` / `video_id` pré-existente; MCP referencia por ID |
| Erro 4xx sem detalhe | Use `ads_get_errors` pra ver últimos erros + sugestões |
