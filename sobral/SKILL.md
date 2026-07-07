---
name: sobral
description: Estrategista sênior de mídia paga da Fundação Growth IA Ops v2.0 — produz
2 outputs canônicos co-produzidos na Subfase 1.4.2 (paralelo a
`content-planner` orgânico). (1) `30-decisoes/plano-midia.md` (F1-21a Categoria
3 Decisão) — alocação por canal × ICP×Produto × etapa funil + estrutura de
conta com pattern UTM canônico Growth IA Ops + audiências SHA-256 + criativos
direção Q1 + cadência de testes + métricas-alvo + exclusões CAPI + LPs
mapeadas. (2) `30-decisoes/forecasting.md` (F1-21b Categoria 3 Decisão) —
projeção financeira 3 cenários A/B/C com premissas explícitas + breakeven +
cash flow Q1 + análise de sensibilidade (Tornado) + gatilhos revisão mid-Q1
+ validação ou recalibragem da meta GTM Plan §9. Bounded context — produz 2
outputs com bounded contexts disjuntos (Plano de Mídia = direção tática;
Forecasting = projeção financeira). Modo `padrao` único (default Subfase
1.4.2). Recalibragem trimestral em Sprint deferida pra schemas separados B7.1c.
Cliente N0 produz Forecasting qualitativo (modo_dado: hipotetico-benchmark +
confidence: baixa) com cenários derivados de benchmark Relatório Mercado §3.
Pattern UTM canônico (D-B4.5d-1) consumido da Taxonomia: utm_source=canal ·
utm_campaign=campaign_id · utm_medium=adset_id · utm_content=ad_id (IDs
nativos plataformas — não V4 OS hierárquico). Triple mode SDK/MCP/CSV
referenciado (D-MCP-12 v2 + D-MCP-20) — handoff downstream pra família
`media-buyer-*` Fase 2 (`media-buyer-meta` v3 SDK-first + `media-buyer-google`
v3 + `media-buyer-linkedin` v3 + `media-buyer-tiktok` v3). Ative quando o
operador disser construir Plano de Mídia, plano paid, alocação canais SEM +
Social, Forecasting, projeção financeira 3 cenários, ou produzir 1.4.2 paid
da Fundação. NÃO ative para GTM Plan estratégico (use cesar upstream — input
formal blocker), Plano de Conteúdo orgânico (use content-planner paralelo),
executar campanhas nas plataformas (use família media-buyer-* Fase 2 — cesar
NÃO executa, só estrutura), criar copy de anúncio (use famílias copy-* Fase
2), criar criativo design (use famílias ad-design-* Fase 2), análise de
dados históricos (use newton upstream cond.), análise de campeões de Google
Ads (use darwin upstream cond. — sobral consome a Análise de Campeões, não a produz). Modo `realocacao` (v2.2.0) — recorrente e data-driven, distinto do `padrao` da Fundação — ative quando o operador pedir realocar ou redistribuir o orçamento de mídia de um período (mês ou semana) a partir de orçamento + indicador-alvo + período, otimizando a alocação por retorno marginal sobre o feed de performance real (metodologia Gestão de Portfólio de Mídia orientada a indicador). NÃO use realocacao para o plano trimestral greenfield da Fundação (use padrao).
type: reference
diataxis: reference
versao: 2.2.0
data: 2026-06-26
operador: V4 Company
status: stable
schemas_id: [F1-21a, F1-21b]
schema_version: 1.0.0
outputs_canonicos:
  - 30-decisoes/plano-midia.md
  - 30-decisoes/forecasting.md
categoria_output: 3-Decisao
linha_visibilidade: hibrida
fase: fase-1
subfase: 1.4.2
modos_canonicos:
  - padrao
  - realocacao  # v2.2.0 — recorrente, data-driven; Gestão de Portfólio de Mídia (ver references/modo-realocacao-portfolio.md)
modos_deferidos:
  - recalibragem-sprint  # Sprint trimestral — schemas separados B7.1c
metodologia_realocacao:
  tese: "C:/Users/mcafe/OneDrive/Documentos/Claude/Projects/04_estudos/Gestão de Portfólio de Mídia/tese-portfolio-midia-v0.1.md"
  motor: "C:/Users/mcafe/OneDrive/Documentos/Claude/Projects/04_estudos/Gestão de Portfólio de Mídia/motor-portfolio-v0.3.ps1"
  versao_metodologia: "0.1"
gates:
  entrada: G1.4 componente — GTM Plan §11.1 + §7 + §9 + §10 prontos
  saida: 2 outputs co-produzidos validados (V1-V14 cada) + cross-link bidirecional GTM Plan + Plano Conteúdo + Manifest v1.0
linkbacks_upstream:
  - gtm_plan: 30-decisoes/gtm-plan.md
  - cenario_baseline: 20-snapshots/YYYY-MM/cenario-baseline.md
  - taxonomia: 10-fundacao/taxonomia.md
  - taxonomia_yml: 10-fundacao/taxonomia.yml
  - measurement_plan: 10-fundacao/measurement-plan.md
  - icp_product_map: 10-fundacao/icp-product-map.md
  - icm: 10-fundacao/icm.md  # consumo canônico: Perfil Base (Firmographics + Geografia) pra segmentação audiences + Anti-ICP operacional pra exclusion audiences (Meta/Google/LinkedIn) — denominação por conceito conforme michelangelo/references/cross-skill-mapping.md v2.2.0; nunca citar número de seção
  - direcao_arte: 10-fundacao/direcao-arte.md
  - design_system: 10-fundacao/design-system.md
  - copy_system: 10-fundacao/copy-system.md
  - relatorio_mercado: 20-snapshots/YYYY-MM/relatorio-mercado.md
  - analise_dados_historicos_cond: 20-snapshots/YYYY-MM/analise-dados-historicos.md
  - champion_analysis_cond: "champion-analysis.{md,yml}"  # darwin — campeões Google Ads (cond., quando há histórico Google Ads); fonte real primária p/ estrutura/alocação/criativo/negativas do bloco Google
  - sistema_qualificacao: 10-fundacao/sistema-qualificacao.md  # Forecasting only — taxas conversão por etapa
linkbacks_downstream:
  - plano_conteudo_paralelo: 30-decisoes/plano-conteudo.md
  - manifest_baseline: 80-versoes/manifest.md
  - gtm_deck: 40-comunicacoes/YYYY-MM-DD-apresentacao-fundacao/gtm-deck.md
  - media_buyer_meta_v3: ~/.claude/skills/media-buyer-meta/SKILL.md
  - media_buyer_google_v3: ~/.claude/skills/media-buyer-google/SKILL.md
  - media_buyer_linkedin_v3: ~/.claude/skills/media-buyer-linkedin/SKILL.md
  - media_buyer_tiktok_v3: ~/.claude/skills/media-buyer-tiktok/SKILL.md
  - audience_architect: ~/.claude/skills/audience-architect/SKILL.md
  - lp_builder_b2b: ~/.claude/skills/lp-builder-b2b/SKILL.md
  - lp_builder_b2c: ~/.claude/skills/lp-builder-b2c/SKILL.md
  - data_snapshot_builder_performance_drop: ~/.claude/skills/data-snapshot-builder/SKILL.md
principios_incidentes:
  - P1
  - P3
  - P5
  - P9
  - P11
confidence: alta
mcp_requerido_input: nenhum
mcp_requerido_output: nenhum
aplicacao_externa_destino: vault (md no path canônico)
formato_output_principal: md
fallback_documentado: cliente N0 Forecasting qualitativo modo_dado=hipotetico-benchmark + confidence_geral=baixa
bibliotecas_consumidas:
  - python-frontmatter
mecanismos_claude_code:
  - PostEdit hook opt-in (Pydantic schema validation pós-publicação)
allowed-tools: Read,Write,Glob,Grep
---

# `sobral` v2.1.0 — Plano de Mídia + Forecasting (Subfase 1.4.2 Fundação Growth IA Ops)

> **Skill nav layer** — produz **2 outputs canônicos co-produzidos** na Subfase 1.4.2 paralelo a `content-planner` (orgânico): (1) **Plano de Mídia** (F1-21a — alocação tática paid SEM + Social) + (2) **Forecasting** (F1-21b — projeção financeira 3 cenários A/B/C com sensibilidade). Subordinado ao GTM Plan (`cesar` 1.4.1 — input formal blocker) — consume §11.1 canais paid priorizados + §7 alavancas + §6 ICP + §9 meta + §10 sequência drops.

> **Sequência canônica:** GTM Plan (1.4.1 — `cesar`) → **Plano de Mídia + Forecasting (1.4.2 paid — `sobral`)** + Plano de Conteúdo (1.4.2 orgânico — `content-planner` paralelo) → Manifest v1.0 (1.4.3 — `system-manifest-builder` baseline) → Apresentação cerimonial (1.5).

> **Mudança vs v1 Dante:** v1 produzia Plano de Mídia integrado (sem Forecasting formal). **v2 formaliza Forecasting como output explícito** — 2 outputs com schemas distintos (D-Schema-1: schemas separados; mesma skill). Cliente N0 produz Forecasting qualitativo (modo `hipotetico-benchmark` + `confidence: baixa`). Sequência canônica corrigida (v1 listava Sobral como input do César; v2 coloca Sobral como **downstream** 1.4.2 — GTM Plan é input formal blocker). Pattern UTM canônico Growth IA Ops (D-B4.5d-1) substitui pattern V4 OS hierárquico v1. Triple mode SDK/MCP/CSV referenciado downstream (D-MCP-12 v2 + D-MCP-20).

> **NÃO executa nas plataformas** — `sobral` pensa, estrutura e direciona. Execução fica com família `media-buyer-*` v3 Fase 2 (SDK-first via `--via=sdk-python` default + MCP opt-in via `--via=mcp` + CSV bulk fallback via `--via=csv-bulk`).

> **Mudança v2.1.0 (extensão additive):** `sobral` passa a consumir a **Análise de Campeões** (`darwin`) como fonte de dado real primária do bloco Google quando o cliente tem histórico de Google Ads — input condicional de alta severidade no modo `padrao` (NÃO é modo novo; análogo ao consumo condicional do `newton`). Ver [Inputs](#inputs-gate-de-entrada--pré-condições) + [Consumo da Análise de Campeões](#consumo-da-análise-de-campeões-darwin--cond-cliente-com-histórico-google-ads). Nada removido — V1-V14 e modo `padrao` preservados.

> **Mudança v2.2.0 (extensão additive — modo novo):** adicionado o modo **`realocacao`** — alocação **recorrente e data-driven** de orçamento de mídia orientada a um **indicador-alvo**, pela metodologia **Gestão de Portfólio de Mídia** (trata budget como fundo, aloca por retorno marginal/equimarginal sobre o feed real, com piso por temperatura e calibração por back-test). Distinto do `padrao` (greenfield/trimestral da Fundação): parte de **orçamento + indicador-alvo + período**, lê o feed de performance real e produz uma **decisão datada** de realocação. Doutrina + workflow em [Modo `realocacao`](#modo-realocacao--gestão-de-portfólio-de-mídia-v22) + `references/modo-realocacao-portfolio.md` (+ tese cross-projeto e motor em `04_estudos/Gestão de Portfólio de Mídia/`). Nada removido — modo `padrao`, V1-V14, schemas F1-21a/b preservados.

---

## Quando ativar

### Triggers canônicos
- "Construir Plano de Mídia"
- "Plano paid Q1"
- "Alocação canais SEM + Social"
- "Forecasting"
- "Projeção financeira 3 cenários"
- "Subfase 1.4.2 paid"
- "GTM Plan pronto — agora montar plano paid"
- "Strategy Meta Ads + Google Ads do projeto"

### Triggers modo `realocacao` (recorrente, data-driven)
- "Realocar o orçamento de mídia do mês"
- "Como distribuir R$ X para maximizar [indicador] no período Y"
- "Redistribuir budget entre campanhas/canais com base no histórico"
- "Plano de mídia mensal data-driven / por indicador"
- "Rebalanceamento mensal (entre canais) ou semanal (dentro do canal)"
- "Aplicar a metodologia de Portfólio de Mídia"

### NÃO ative para
- GTM Plan estratégico → `cesar` (upstream — input formal blocker `gtm-plan.md`)
- Cenário Baseline → `arquimedes` (upstream — input alto)
- Análise de Dados Históricos → `newton` (upstream cond. — calibra premissas)
- Análise de campeões de Google Ads (clusters/negativas/ad-DNA/mapa intenção→campanha) → `darwin` (upstream cond. — `sobral` CONSOME a Análise de Campeões, não a produz)
- Plano de Conteúdo orgânico → `content-planner` (paralelo na Subfase 1.4.2 — bounded context disjunto)
- Executar campanhas nas plataformas → família `media-buyer-*` v3 Fase 2 (downstream — `sobral` NÃO executa)
- Criar copy de anúncio → famílias `copy-*` Fase 2 (`ad-copy-meta`/`google-rsa`/`linkedin`/`tiktok` — downstream)
- Criar criativo design → famílias `ad-design-*` Fase 2 (`ad-design-image`/`video`/`carousel`/etc. — downstream)
- LP de campanha → família `lp-builder-*` Fase 2 (downstream — Plano de Mídia §11 só mapeia LPs por campanha)
- Audience operacional → `audience-architect` Fase 2 (downstream — Plano §6 só descreve audiências; audience-architect detalha)
- Performance-Drop / Performance-Sprint → `data-snapshot-builder` Fase 3 (downstream — compara realizado vs. baseline mensal/trimestral)

---

## Inputs (gate de entrada — pré-condições)

### Para Plano de Mídia (F1-21a)

| # | Pré-condição | Onde verificar | Severidade |
|---|---|---|---|
| 1 | GTM Plan completo (§11.1 canais paid + §6 ICP + §7 alavancas + §9 meta) | `30-decisoes/gtm-plan.md` | **blocker** |
| 2 | Cenário Baseline §3 (NSM) + §4 (CAC atual) + §6 (funil baseline) | `20-snapshots/YYYY-MM/cenario-baseline.md` | **blocker** |
| 3 | Taxonomia (pattern UTM + name-templates + extensions custom) | `10-fundacao/taxonomia.md` + `taxonomia.yml` | **blocker** |
| 4 | Measurement Plan (eventos + plataformas + CAPI) | `10-fundacao/measurement-plan.md` | **blocker** |
| 5 | ICP Product Map (combinações canônicas) | `10-fundacao/icp-product-map.md` | **blocker** |
| 6 | Direção de Arte + Design System + Copy System (consumo downstream pelos criativos) | `10-fundacao/{direcao-arte,design-system,copy-system}.md` | alto |
| 7 | Relatório de Mercado §3 (CAC benchmark + canais aderentes ao ICP) | `20-snapshots/YYYY-MM/relatorio-mercado.md` | alto |
| 8 | Análise de Dados Históricos (cond.) — calibra CPL/CTR/CVR esperados | `20-snapshots/YYYY-MM/analise-dados-historicos.md` | alto (se houver dados) |
| 9 | **Análise de Campeões (cond.) — `darwin`** — dado real Google Ads: CP-conv blended + % gasto produtivo + clusters intenção×ICP + tCPA-hint por segmento + DNA anúncios campeões + negativas (conflict-check) + mapa intenção→campanha | `champion-analysis.{md,yml}` | alto (se cliente tem histórico Google Ads) |

### Para Forecasting (F1-21b) — pré-condições adicionais

| # | Pré-condição | Onde verificar | Severidade |
|---|---|---|---|
| 1 | Plano de Mídia §3 (Budget total + alocação) + §9 (Métricas-alvo paid) | `30-decisoes/plano-midia.md` | **blocker** |
| 2 | Cenário Baseline §4 (Unit Economics) + §5 (Viabilidade) + §6 (Funil) | `20-snapshots/YYYY-MM/cenario-baseline.md` | **blocker** |
| 3 | Sistema de Qualificação (taxas conversão por etapa Bowtie) | `10-fundacao/sistema-qualificacao.md` | alto |
| 4 | ICP Product Map (LTV + ticket por combinação) | `10-fundacao/icp-product-map.md` | **blocker** |
| 5 | Análise de Dados Históricos (cond.) — calibra premissas com sinal real | `20-snapshots/YYYY-MM/analise-dados-historicos.md` | alto (se houver dados) |
| 6 | Relatório de Mercado §3 (CAC benchmark) | `20-snapshots/YYYY-MM/relatorio-mercado.md` | alto (especialmente cliente N0) |
| 7 | **Análise de Campeões (cond.) — `darwin`** — CP-conv real Google calibra premissas (precede benchmark) | `champion-analysis.{md,yml}` | alto (se há histórico Google Ads) |

**Cliente N0 (handling):**
- Plano de Mídia: §9 métricas-alvo com benchmark Relatório Mercado §3 (não números inventados); §3 budget conservador (Q1 = "calibrar"); §12 risco crítico: "Métricas-alvo são hipóteses; primeiros 30-45 dias = calibrar"
- Forecasting: `cliente_n0: true` + `modo_dado: hipotetico-benchmark` + `confidence_geral: baixa`. Premissas derivam Relatório Mercado §3 + ICP Product Map (LTV teórico). §11 ressalva forte: "Forecasting hipotético — primeiros 30-45 dias = calibrar premissas; recalibragem prevista no drop M1"
- **NÃO recusar fechar** com cliente N0 (Q7 fechada B3 — Forecasting é produzido sempre)

### Consumo da Análise de Campeões (`darwin`) — cond., cliente com histórico Google Ads

Quando existe `champion-analysis.{md,yml}` (output do `darwin`), ela é a **fonte de dado real primária do bloco Google** — precede benchmark. Mapa de consumo:
- **Métricas blended** (CP-conv real, % gasto produtivo) → §A9 (caminho "cliente com dados", não benchmark).
- **Clusters por intenção×ICP + tCPA-hint por segmento** → §A2.3 (ICP×Produto), §A3.4 (alocação por ICP), §A5 (estrutura — campanhas isoladas por intenção), §A8 (hipóteses/cadência).
- **Mapa intenção→campanha + 1 campanha de teste** → §A5 (estrutura de conta Google).
- **DNA dos anúncios campeões** → §A7 (direção: DNA validado como CONTROLE + 2 variações de ângulo novo; guidance validada — sentence case, sem-pin default / partial-pin alternativa).
- **Baldes de desperdício→negativas (conflict-check já feito pelo `darwin`)** → §A10 + §A5 (negativas compartilhadas).

> **Distinção vs `newton`:** newton = baseline multi-canal → premissas/arquimedes; darwin = campeões Google Ads → estrutura/alocação/criativo. Podem coexistir. Se ambos ausentes e cliente sem dados → caminho N0 (benchmark) inalterado.

---

## Workflow (modo `padrao` — default Subfase 1.4.2)

### Fase A — Plano de Mídia (F1-21a — 12 seções obrigatórias)

#### Passo 0 — Iniciação Plano de Mídia
- Confirmar com operador que GTM Plan está aprovado (§11.1 + §7 + §6 + §9 estáveis)
- Validar Taxonomia disponível (pattern UTM + `name-templates.yml` da Subfase 1.3.0 — escopo: tracking; naming de entidade vem da taxonomia da `media-buyer-meta`, ver Passo A5)
- Cliente N0? confirmar com operador antes de proceder

#### Passo A1 — Sumário executivo (4-6 parágrafos)
Endereçar 5 elementos: budget Q1 total · canais priorizados · objetivos por canal · meta CPL/CPA/ROAS · cadência de testes.

#### Passo A2 — Alinhamento com GTM Plan
- 2.1 Restrição principal subordinada (Cenário Baseline §2 → GTM Plan §4)
- 2.2 Loops priorizados que paid alimenta (subset GTM Plan §5)
- 2.3 ICP×Produto canônicas servidas (GTM Plan §6)
- 2.4 Anti-canais (descartados explicitamente com justificativa)

#### Passo A3 — Budget e alocação
- 3.1 Budget total Q1 + distribuição mensal M1/M2/M3
- 3.2 Alocação por plataforma (% + valor absoluto — soma 100%)
- 3.3 Alocação por etapa Bowtie (attract/engage/convert/expand/nurture)
- 3.4 Alocação por ICP×Produto

#### Passo A4 — Plataformas e canais (4-7 plataformas Q1)
Por plataforma (`references/plataformas-paid-2026.md`):
- Objetivo + ICP×Produto servidas + Etapa Bowtie + Tipo de campanha + Justificativa estratégica

#### Passo A5 — Estrutura de conta
Por plataforma:
- Campanhas — **nomes de ENTIDADE (Gerenciador) seguem a Taxonomia de Entidade Meta** (fonte vigente: `media-buyer-meta/SKILL.md` §Naming, validada viva na conta Sigo jun/26 — ex. `EVER_META_SAL_SigoERP_Frio` — V5 blocker): campanha `{STATUS}_{CANAL}_{OBJ}_{PRODUTO}_{TEMP}` (STATUS: HALL/TEST/EVER · **OBJ = evento de conversão/estágio de funil que a campanha otimiza**, ex. `MQL`/`SAL`/`LEAD` — NÃO assumir `LEAD` por default · **TEMP = temperatura**: `Frio`/`Morno`/`Quente`) · conjunto `AUD-{HIERARQUIA}-{ID_SEQ}_{FUNIL}_{TIPO}_{PÚBLICO}_{GEO}_{DEMO}_{FORMATO}` (HIERARQUIA = dígito 0–9 da cascata waterfall; DEMO = `{idade-min}-{idade-max}-{M/F/HM}`) · anúncio `AD-{ID_SEQ}_{FORMATO}_{CONSCIÊNCIA}_{GANCHO}_{AVATAR}_{VARIAÇÃO}` (container DCO: `{DROP}_..._DCO`).
  - ⚠️ **Duas armadilhas (ambas custaram rodadas no caso IGA Blumenau 2026-07-02):** (a) **entidade × tracking** — o `name-templates.yml`/`taxonomia.yml` do `taxonomy-builder` rege UTM/tracking (bloco abaixo), NÃO o nome da entidade; (b) **fonte do naming** — o arquivo `media-buyer-meta/referencias/taxonomia-entidade-meta.md` traz uma sintaxe de campanha desatualizada (`..._{PRODUTO}_{DESTINO}` + OBJ enum LEAD/SALES); a fonte correta é o **SKILL.md** da skill (`..._{PRODUTO}_{TEMP}` + OBJ = estágio de conversão real).
- Adsets estimados + Criativos iniciais + Budget diário + Bid strategy

**Pattern UTM canônico Growth IA Ops** (D-B4.5d-1 — V4 blocker):
- `utm_source=canal` (lowercase: meta, google-search, google-pmax, linkedin, tiktok)
- `utm_campaign=campaign_id` (ID nativo plataforma — não nome)
- `utm_medium=adset_id` (ID nativo)
- `utm_content=ad_id` (ID nativo)
- Regras especiais: PMax força `campaign_id` em ad_id; orgânico força nome canal lowercase; direct=direct; manual=manual

#### Passo A6 — Audiências (`references/audiencias-hash-policy.md`)
Por plataforma + tipo:
- Lookalikes (fonte + tamanho)
- Interesse/comportamento
- Retargeting (janelas de retenção)
- First-party (CRM upload — hash policy SHA-256 obrigatória — V6 blocker)
- Exclusões

**Hash policy canônica V6 blocker:**
- Email: lowercase + trim + SHA-256 hex unsalted
- Phone: E.164 normalization + SHA-256 hex unsalted
- CPF/CNPJ: numeric-only + SHA-256 hex unsalted (sem hífens/pontos)

#### Passo A7 — Criativos — direção Q1
- 7.1 Formatos por canal (single-image / carousel / video-15s / video-60s / RSA)
- 7.2 Ângulos (dor / ganho / social-proof / comparação / educacional)
- 7.3 Quantidade inicial (por ICP × ângulo)
- 7.4 Cadência de renovação (weekly/bi-weekly/monthly)
- 7.5 Diretrizes de Direção de Arte + Copy System (handoff Fase 2 família `ad-design-*` + `ad-copy-*` — explícito)
- 7.6 **Se há Análise de Campeões (`darwin`):** reaproveitar o **DNA dos anúncios campeões como CONTROLE** + 2 variações de ângulo novo; aplicar guidance validada (sentence case > title case; sem-pin default / partial-pin como alternativa). Handoff `media-buyer-google` mantém o padrão (3 RSAs unpinned, char limits, naming).

#### Passo A8 — Cadência de testes
- 8.1 Hipóteses paid Q1 (subset GTM Plan §8)
- 8.2 Framework de teste (A/B vs multivariate vs hold-out vs ramp-up)
- 8.3 Cadência de revisão (semanal/quinzenal)
- 8.4 Critério de kill (custo de oportunidade + threshold mínimo)
- 8.5 Critério de scale (escalada de budget)

#### Passo A9 — Métricas-alvo Q1
Tabela: CPL alvo · CPA alvo · ROAS alvo (cond.) · CTR · CVR Lead→MQL · CVR MQL→SQL · Share-of-budget por canal.

**V9 blocker:** valor numérico (cliente N0 = benchmark mercado com fonte; cliente com dados = derivados Análise Histórica OU **Análise de Campeões `darwin`** — CP-conv blended + % gasto produtivo reais, preferidos a benchmark no bloco Google).

#### Passo A10 — Exclusões, pixels e CAPI
- 10.1 Exclusões de audiência (clientes atuais, leads 60d, etc.)
- 10.2 Pixels CAPI por plataforma
- 10.3 Eventos CAPI ativos (linka Measurement Plan)
- 10.4 Hash policy SHA-256 canônica
- 10.5 Event ID dedup UUID v4

#### Passo A11 — Landing Pages e jornadas
Mapeamento campanha × LP × ICP × CTA. LP por campanha; CTA coerente com etapa Bowtie. Sinaliza LPs a produzir Fase 2 (família `lp-builder-*`).

#### Passo A12 — Riscos e premissas paid
- 12.1 Top 3 riscos paid + mitigação (leilão saturado, queda delivery, mudança algoritmo)
- 12.2 Premissas críticas (CTR/CVR esperados — fonte Análise Histórica ou benchmark)
- 12.3 Sinais de reavaliação

#### Passo A13 — Validações V1-V14 Plano de Mídia
Aplicar checklist em `references/schema-plano-midia.md`:
- V1 frontmatter parseável + 12 seções (blocker)
- V2 §2 alinhamento com GTM Plan §11.1 (blocker)
- V3 §3 soma % por plataforma = 100% ±1% (blocker)
- V4 pattern UTM canônico Growth IA Ops respeitado (blocker)
- V5 nomes de entidade (campanha/conjunto/anúncio) seguem a Taxonomia de Entidade Meta/Google (`media-buyer-meta/referencias/taxonomia-entidade-meta.md`); UTMs seguem `name-templates.yml` — não trocar as fontes (blocker)
- V6 audiências first-party com hash SHA-256 (blocker)
- V7 ≥3 ângulos por ICP (alto)
- V8 ≥2 hipóteses paid falsificáveis (blocker)
- V9 métricas-alvo com valor numérico (blocker)
- V10 pixels CAPI listados coerentes Measurement Plan (blocker)
- V11 toda campanha tem LP mapeada (alto)
- V12 ≥3 riscos + ≥3 premissas com confidence (médio)
- V13 cross-link bidirecional GTM Plan + Forecasting + Manifest v1.0 (blocker)
- V14 cliente N0: `cliente_n0: true` + `confidence: baixa` + benchmarks com fonte (blocker cond.)

#### Passo A14 — Publicar Plano de Mídia
- Path canônico: `30-decisoes/plano-midia.md`
- Frontmatter completo (17+ campos — pattern Onda 2/3/4a/4b/4c)
- Ao concluir, atualize a seção «Decisões em vigor» de `10-fundacao/contexto.md` via Edit — 2-5 linhas + ponteiro [[plano-midia]], sem duplicar; toque `updated_at` + changelog.

---

### Fase B — Forecasting (F1-21b — 11 seções obrigatórias)

#### Passo 0 — Iniciação Forecasting
- Confirmar Plano de Mídia §3 + §9 estáveis
- Cliente N0? definir `modo_dado: hipotetico-benchmark` + `confidence: baixa`

#### Passo B1 — Sumário executivo (4-6 parágrafos)
Endereçar 5 elementos: 3 cenários A/B/C com receita Q1 estimada · breakeven cenário B · validação ou recalibragem da meta GTM Plan §9 · variável de maior sensibilidade · gatilhos de revisão.

#### Passo B2 — Premissas compartilhadas (cross-cenário)
- 2.1 Budget paid Q1 (herda Plano §3)
- 2.2 Ticket médio (herda ICP Product Map ou Cenário Baseline)
- 2.3 Ciclo de venda
- 2.4 Win rate SQL→DealWon (cond.)
- 2.5 Organic traffic share alvo

Cada premissa com fonte explícita + confidence calibrado.

#### Passo B3 — Cenário A — Pessimista
- 3.1 Premissas divergentes (CPL pior, CVR menor) com justificativa
- 3.2 Funil mensal M1/M2/M3 (leads → MQL → SQL → DealWon)
- 3.3 Receita Q1
- 3.4 Cash flow + saldo
- 3.5 Probabilidade estimada

#### Passo B4 — Cenário B — Central (cenário de validação da meta GTM Plan §9)
Mesma estrutura. **V3 blocker — meta SMART do GTM Plan §9 deve estar dentro do cenário B (±10%)** OU §9.3 explícita recalibragem proposta.

#### Passo B5 — Cenário C — Otimista
Mesma estrutura. Testa upside — quando vale escalar agressivo.

#### Passo B6 — Comparativo cross-cenário
Tabela: receita Q1 · CAC realizado · LTV/CAC · breakeven · ROAS (cond.) por cenário A/B/C. Visualização (ASCII bar chart ou Mermaid).

#### Passo B7 — Análise de sensibilidade (`references/forecasting-cenarios-sensibilidade.md`)
Top 4-5 variáveis com maior impacto na receita Q1: CPL, CVR Lead→MQL, ticket médio, ciclo venda, win rate. Tornado chart (textual ou Mermaid). Identifica variável de maior alavancagem.

#### Passo B8 — Breakeven e cash flow
- 8.1 Breakeven mensal por cenário
- 8.2 Cash flow Q1 (investimento × receita estimada)
- 8.3 Runway impacto no cenário A
- 8.4 Cross-link com Cenário Baseline §5

#### Passo B9 — Validação ou recalibragem da meta Q1 (GTM Plan §9)
- 9.1 Meta Q1 SMART do GTM Plan vs. cenário B
- 9.2 Validação OU 9.3 Recalibragem proposta + justificativa
- 9.4 Comunicação ao operador (e cliente cond. via Apresentação)

**V10 blocker:** validação ou recalibragem com justificativa explícita.

#### Passo B10 — Gatilhos de revisão mid-Q1
Lista ≥3 sinais quantitativos que disparam recalibragem do Forecasting antes do fim do Q1 (ex: "CPL realizado >= 1.5× CPL alvo cenário B aos 30 dias = recalibrar"). Inclui deadline de revisão.

#### Passo B11 — Riscos e premissas de modelagem
- 11.1 Top 3 riscos do modelo (ex: ciclo venda mais longo, sazonalidade não considerada)
- 11.2 Premissas críticas com confidence calibrado
- 11.3 Limitações do Forecasting (ex: não modela churn explicitamente em SaaS)

#### Passo B12 — Validações V1-V14 Forecasting
Aplicar checklist em `references/schema-forecasting.md`:
- V1 frontmatter + 11 seções (blocker)
- V2 3 cenários A/B/C com funil mensal M1/M2/M3 quantificado (blocker)
- V3 cenário B contém meta GTM Plan §9 ±10% OU §9.3 recalibragem (blocker)
- V4 premissas compartilhadas com fonte explícita (blocker)
- V5 cliente com dados: premissas derivam Análise Histórica (blocker cond.)
- V6 cliente N0: premissas derivam Relatório Mercado §3 com fonte; `confidence: baixa` (blocker cond.)
- V7 §6 comparativo cross-cenário com tabela (alto)
- V8 §7 análise de sensibilidade ≥4 variáveis (alto)
- V9 §8 breakeven calculado por cenário (blocker)
- V10 §9 validação ou recalibragem da meta (blocker)
- V11 §10 ≥3 gatilhos quantitativos (alto)
- V12 §11 ≥3 riscos + ≥3 premissas (médio)
- V13 cross-link bidirecional GTM Plan §9 + Plano de Mídia §9 + Manifest v1.0 (blocker)
- V14 probabilidades cenários somam 1.0 ±0.05 (alto)

#### Passo B13 — Publicar Forecasting
- Path canônico: `30-decisoes/forecasting.md`
- Frontmatter completo (17+ campos)

---

## Modo `realocacao` — Gestão de Portfólio de Mídia (v2.2)

> Modo **recorrente e data-driven**, distinto do `padrao` (Fundação/greenfield). Trata o budget como um **fundo de investimento**: aloca capital entre **pools** (canal × temperatura × campanha × conjunto) para maximizar um **indicador-alvo**, por **retorno marginal** (equimarginal/water-filling). Doutrina + workflow detalhado em **`references/modo-realocacao-portfolio.md`**; doutrina canônica completa + motor de cálculo em `04_estudos/Gestão de Portfólio de Mídia/` (tese v0.1 + `motor-portfolio-v0.3.ps1`).

**Inputs (3 params do operador + feed):** orçamento · indicador-alvo (lead/mql/sal/sql/demo_agendada/demo_realizada/novos_clientes/roas/faturamento) · período · **feed de performance real** (CSV granular dia×anúncio).

**Workflow (8 passos — motor + julgamento):** 0 normalizar/dedup → 1 sinal por pool (janelas ponderadas) → 1.5 maturação de safra (descontar coortes imaturas) → 2 marginal & saturação (`cp_base×(1+over)^β`, β=1, morde só acima do gasto provado) → 3 piso por temperatura (limitado por capacidade) → 4 water-filling equimarginal dentro de cada temperatura → 5 100% alocado (sem reserva) → 6 pisos de learning → 7 forecast em faixa (cenário = swing exógeno). Detalhe: ver reference.

**Calibração obrigatória (back-test):** a projeção da estrutura **não pode ser menor que o realizado recente** (piso). Falhou → recalibrar β/Ref antes de publicar.

**Cadência (D4):** mensal **entre canais** (janela dia 25→1) · semanal **dentro do canal** (substitui reserva de exploração).

**Output:** decisão datada `30-decisoes/YYYY-MM-DD-realocacao-<periodo>.md` (Decision Doc Template). **NÃO revoga** o Plano de Mídia/Forecasting trimestral — é complementar.

**Roadmap (v0.1, NÃO implementar agora):** ponderação de qualidade no mandato; curva de maturação com dado limpo; refino dos % de temperatura por capacidade; regra de graduação de teste; evolução p/ MMM/incrementalidade.

---

## Outputs canônicos (2 outputs co-produzidos)

### Output 1: Plano de Mídia
- **Path:** `30-decisoes/plano-midia.md`
- **Schema:** F1-21a v1.0.0
- **Categoria:** 3 — Decisão
- **Cadência:** one-shot baseline (recalibrado em Sprint trimestral via re-execução parcial — schema separado deferido B7.1c)

### Output 2: Forecasting
- **Path:** `30-decisoes/forecasting.md`
- **Schema:** F1-21b v1.0.0
- **Categoria:** 3 — Decisão
- **Cadência:** one-shot baseline (recalibragem trimestral em Sprint — handoff com `data-snapshot-builder` modo `performance-sprint`)

---

## Anti-patterns (recusar)

- ❌ Pattern UTM V4 OS hierárquico no Plano de Mídia (V4 blocker — pattern canônico Growth IA Ops é `utm_source=canal · utm_campaign=campaign_id · utm_medium=adset_id · utm_content=ad_id`)
- ❌ Hash policy custom em audiências first-party (V6 blocker — SHA-256 hex unsalted obrigatório com normalização canônica email/phone/CPF/CNPJ)
- ❌ Métricas-alvo inventadas sem fonte (V9 blocker — cliente N0 = benchmark com fonte rastreável; cliente com dados = derivado Análise Histórica)
- ❌ Forecasting sem cenário B contendo meta GTM Plan §9 ±10% (V3 blocker Forecasting — ou §9.3 recalibragem proposta explícita)
- ❌ Premissas Forecasting sem fonte (V4 blocker Forecasting — Análise Histórica / Relatório Mercado / ICP Product Map)
- ❌ Soma % alocação por plataforma ≠ 100% ±1% (V3 blocker Plano de Mídia)
- ❌ Nome de entidade (campanha/conjunto/anúncio) fora da Taxonomia de Entidade Meta/Google — ou nomeado pelo `name-templates.yml` do `taxonomy-builder`, que é UTM/tracking, não entidade (V5 blocker Plano de Mídia)
- ❌ Cliente N0 sem `cliente_n0: true` + `confidence: baixa` no Forecasting (V14 blocker Plano + V6 blocker Forecasting)
- ❌ Executar campanhas (escopo família `media-buyer-*` v3 Fase 2 — `sobral` NÃO executa)
- ❌ Criar copy literal de anúncio (escopo famílias `copy-*` Fase 2 — `sobral` direciona ângulos + formatos)
- ❌ Criar criativo design (escopo famílias `ad-design-*` Fase 2 — `sobral` direciona formatos + diretrizes)
- ❌ Modo `recalibragem-sprint` Sprint trimestral nesta skill v2 (deferido pra schemas F3 separados B7.1c)

---

## References

- `references/plataformas-paid-2026.md` — Plataformas paid 2024-2026 detalhadas (Meta + Google Ads Search + PMax + Display + YouTube + LinkedIn + TikTok + X) + objetivos canônicos por plataforma + bid strategies + benchmarks de delivery + critérios de seleção × ICP × modelo
- `references/forecasting-cenarios-sensibilidade.md` — Modelagem 3 cenários A/B/C com premissas explícitas + análise de sensibilidade Tornado chart (4-5 variáveis canônicas: CPL / CVR Lead→MQL / ticket médio / ciclo venda / win rate) + breakeven por cenário + cash flow + handling cliente N0 com benchmark + Sean Ellis Forecasting + WBD Revenue Architecture
- `references/audiencias-hash-policy.md` — Audiências canônicas paid (lookalikes / interesse / comportamento / retargeting / first-party / custom audience CRM / similar audience) + hash policy SHA-256 obrigatória com normalização canônica (lowercase email + E.164 phone + numeric-only CPF/CNPJ) + janelas retenção + LGPD compliance + handoff `audience-architect` Fase 2
- `references/schema-plano-midia.md` — Schema F1-21a completo (frontmatter 17+ campos + 12 seções obrigatórias + V1-V14 critérios validação + 8 edge cases canônicos cliente-N0/runway-curto/recurring-vs-transacional/B2B-ciclo-longo/B2C-alto-envolvimento/regulado/plataforma-exotica/recalibragem-sprint + linkbacks bidirecionais upstream+downstream + handoff família `media-buyer-*` v3 + `audience-architect` + `lp-builder-*`)
- `references/modo-realocacao-portfolio.md` — Modo `realocacao` (v2.2): metodologia Gestão de Portfólio de Mídia — mandato/indicador-alvo, inputs, workflow 8 passos, saturação/marginal, piso por temperatura, calibração back-test, cadência, output e roadmap. Aponta para a tese canônica + motor em `04_estudos/Gestão de Portfólio de Mídia/`.
- `references/schema-forecasting.md` — Schema F1-21b completo (frontmatter 17+ campos + 11 seções obrigatórias + V1-V14 critérios validação + 8 edge cases canônicos cliente-N0-sem-dados/dados-parciais/runway-curto/recurring-SaaS/transacional/B2B-ciclo-longo/multi-canais-divergentes/recalibragem-sprint + linkbacks bidirecionais + handoff `data-snapshot-builder` Fase 3)

---

## Templates

- `templates/plano-midia-template.md` — Esqueleto 12 seções com placeholders + frontmatter 17+ campos pré-preenchido + tabelas estruturadas pra Budget alocação + Plataformas + Estrutura conta + Audiências + Criativos + Cadência testes + Métricas-alvo + Exclusões CAPI + LPs mapeadas + Riscos
- `templates/forecasting-template.md` — Esqueleto 11 seções com placeholders + frontmatter 17+ campos pré-preenchido + tabelas estruturadas pra 3 cenários A/B/C com premissas + funil mensal + breakeven + cash flow + Sensibilidade Tornado + Gatilhos revisão + Riscos modelagem

---

## Modularização futura mapeada (deferida)

> Não materializar agora. v2 cobre escopo Fundação. Mapeamento §8 auditoria registra extração futura.

| Sub-skill candidata | Bounded context | Quando avaliar |
|---|---|---|
| `sem-strategist` | Estratégia Google Ads/SEM standalone | Cliente search-heavy + demanda recorrente deep dive |
| `social-ads-strategist` | Estratégia Meta Ads / outras social standalone | Cliente social-heavy + demanda recorrente |
| `forecaster` | Forecasting standalone | **Forte candidata** — Forecasting tem repertório próprio (scenario planning + Monte Carlo + sensitivity analysis) e cardinalidade recorrente (mensal Fase 2+); pode virar utilitário cross-fase |
| `programmatic-ads-strategist` | Display/programmatic ads | Cliente demanda programmatic — extensão escopo |

**Quando avaliar:** B7 ou Bloco C+1. **`forecaster` é candidata mais provável** de extração precoce.

---

## Histórico de versão

| Versão | Data | Mudança |
|---|---|---|
| 2.2.1 | 2026-07-02 | **Ajuste — fonte do naming de entidade (Passo A5 + V5 + anti-pattern + Passo 0).** Nomes de campanha/conjunto/anúncio no Gerenciador seguem a **Taxonomia de Entidade Meta/Google** (`media-buyer-meta/referencias/taxonomia-entidade-meta.md` — campanha `STATUS_CANAL_OBJETIVO_PRODUTO_DESTINO` · conjunto `AUD-{waterfall 0-9}-...` · anúncio `AD-*`/DCO), NÃO o `name-templates.yml` do `taxonomy-builder` (escopo: UTM/tracking). Distinção entidade × tracking explicitada; pattern UTM inalterado. Origem: caso IGA Blumenau 2026-07-02 (2 rodadas de nomes inválidos por fonte trocada). Nada removido. |
| 2.2.0 | 2026-06-26 | **Extensão additive — modo novo `realocacao`** (Gestão de Portfólio de Mídia orientada a indicador). Recorrente/data-driven: orçamento + indicador-alvo + período → alocação por retorno marginal (equimarginal/water-filling) sobre feed real, com saturação que morde só acima do gasto provado (β=1), piso por temperatura limitado por capacidade, 100% alocado + rebalanceamento (mensal entre canais 25→1 / semanal dentro), calibração por back-test (projeção ≥ realizado recente) e cenário como faixa exógena. Output = decisão datada `30-decisoes/YYYY-MM-DD-realocacao-*.md` (não revoga planos trimestrais). Novo `references/modo-realocacao-portfolio.md`; doutrina + motor em `04_estudos/Gestão de Portfólio de Mídia/`. Modo `padrao`, V1-V14 e schemas preservados. |
| 2.0.0 | 2026-05-10 | Refator leve a média Dante v1 → v2 escopo formal Fundação Subfase 1.4.2. **Forecasting formalizado como output explícito** (v1 = 1 output integrado; v2 = 2 outputs separados D-Schema-1: schemas distintos mesma skill). Sequência canônica corrigida (v1 = Sobral input do César; v2 = Sobral downstream 1.4.2 — GTM Plan input formal blocker). Pattern UTM canônico Growth IA Ops (D-B4.5d-1) substitui pattern V4 OS hierárquico v1. Triple mode SDK/MCP/CSV referenciado downstream (D-MCP-12 v2 + D-MCP-20). Cliente N0 produz Forecasting qualitativo (modo `hipotetico-benchmark` + `confidence: baixa`) — **NÃO recusa fechar** (Q7 fechada B3). Schemas F1-21a + F1-21b alinhados com catálogo formal B7.1b-ii. Modos `padrao` único (recalibragem-sprint deferida B7.1c). 14 validações V1-V14 cada output (8 blockers + 5 altos + 1 médio). 8 edge cases canônicos cada. Frontmatter pattern 17+ campos consistente Onda 2/3/4a/4b/4c. |
| 1.0.0 | (Dante v1) | Snapshot v1 documentado em `arquitetura/skills/auditoria/fundacao/sobral.md` pra arqueologia. |
