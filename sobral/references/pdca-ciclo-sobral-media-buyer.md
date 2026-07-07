# PDCA: Ciclo Sobral → Media Buyer — Primeiro Lançamento de Projeto

> Aprendizados destilados do piloto Grupo Manchester (2026-04-16), transformados em padrão reusável para o ciclo Sobral → Media Buyer em qualquer projeto de mídia paga.

## Objetivo do ciclo

Transformar inputs estratégicos (ICM, PUV, Arquimedes, contexto do negócio) em **1 campanha-piloto subida na plataforma com tracking amarrado, critérios GO/NO-GO objetivos e sem retrabalho**, no menor tempo possível. Evitar: campanha subida que não mede nada, keywords por adivinhação, CSVs rejeitados no import.

## As 5 etapas do ciclo (com gates de qualidade)

### Etapa 1 — Plano V1 (Sobral Modo 2, versão inicial)

**O que fazer:** O Sobral produz a primeira versão do plano com base nos inputs upstream (Michelangelo, Da Vinci, Arquimedes, contexto). Inclui estrutura de campanhas, clusters de intenção, keywords-semente, negativas base, RSAs rascunho.

**Gate 1 — Plano V1 aprovado internamente?**
- Estrutura de silos faz sentido pro ICP × Produto?
- Negativas cobrem os 7 tiers?
- RSAs respeitam 6 Pilares (títulos) + 4 Pilares (descrições)?

Se sim, avança pra Etapa 2. Se não, itera.

---

### Etapa 2 — Validação via pesquisa SERP (NÃO PULAR)

**O que fazer:** Rodar WebSearch em cada termo-âncora dos clusters. Descobrir:
- Quem rankeia orgânico (competitive landscape real)
- Se há anúncios pagos visíveis (SEM competition)
- Autocompletes e variações que pessoas realmente digitam
- Long-tails descobertas (ex: bitolas específicas, termos de objeção, qualificadores CNPJ)
- Termos-negativos adicionais (produtos adjacentes fora do escopo, branded-rivals, geo fora do alcance)
- Calibração de CPC provável (mercado disputado vs limpo)

**Output:** Plano V2 com keywords com flags ✅/🔵/⚠️, negativas expandidas, observações de mercado, ajuste de expectativa de CPC.

**Gate 2 — Todas as keywords passaram por validação?**
- Nenhuma keyword marcada com ⚠️ sem justificativa de manter
- Pelo menos 1 long-tail 🔵 descoberta por cluster
- Negativas Tier 6 (fora escopo do cliente específico) e Tier 7 (branded-rival) preenchidas

> ⚠️ **Lição do Manchester:** sem esta etapa, a lista de keywords é um vocabulário interno que não reflete como o mercado busca. A inferência do ICP + PUV não substitui a pesquisa.

---

### Etapa 3 — Pre-Flight Tracking-Aware

**O que fazer:** Amarrar o plano à instrumentação real do cliente, verificando com o tracking-engineer/instrumentation-engineer ou documentação do projeto:

**Para Google Ads:**
- [ ] Conversão primária existe na conta e aponta pro evento correto (MQL se há pedágio de qualificação, Lead genérico se não)
- [ ] Auto-tagging `On` na conta
- [ ] Enhanced Conversions ativado
- [ ] Cookie `_gcl_aw` é setado (Conversion Linker funcionando)
- [ ] Tracking Template com UTMs + `{gclid}`
- [ ] Final URL aponta pra página com popup/formulário ativo

**Para Meta Ads:**
- [ ] Pixel disparando Lead com `eventID`
- [ ] CAPI configurada (se disponível)
- [ ] Enhanced Matching ativo
- [ ] Cookie `_fbp` setado
- [ ] Conversion window alinhado com ciclo de decisão do ICP

**Gate 3 — Tracking validado em ambiente real?**
- Todos os checks acima passaram via Tag Assistant / Pixel Helper / Test Events reais, não em staging
- Se algum falhou, documentar como bloqueante da Fase 0 — não liberar CSV até resolver

> ⚠️ **Lição do Manchester:** o plano V1 prometia conversão em MQL, mas a tag de conversão do Google Ads tinha trigger no MQL do GTM — só funciona se o popup disparar MQL em produção. Sem validação, toda a estratégia de Smart Bidding cai no vazio.

---

### Etapa 4 — Handoff Sobral → Media Buyer + Geração de CSV

**O que o Sobral entrega pro Media Buyer:**
- Plano V2 consolidado (com seções 1–8 + seção 9 "Pre-Flight Tracking-Aware" + seção 10 "Handoff")
- Lista de keywords com flags e ranking de match types
- Lista de negativas em 7 tiers
- RSAs com char count validado
- IDs de plataforma (Google Ads Conversion ID + Label, Pixel ID, etc.)
- Naming convention Dante mapeada
- Decisão Piloto vs Escala explícita

**O que o Media Buyer produz:**
- Para Google Ads: **5 CSVs separados** no formato Web Bulk Upload — `01_campaigns.csv`, `02_ad_groups.csv`, `03_keywords.csv`, `04_negative_keywords.csv`, `05_ads.csv` (ver `media-buyer-google/references/csv-search.md`)
- Para Meta: CSV bulk import com exclusões waterfall aplicadas
- Documento explicativo de estrutura + passo-a-passo no Editor/UI com ajustes manuais obrigatórios
- Handoff Guardião do Log estruturado aguardando IDs pós-upload

**Gate 4 — CSVs validáveis no primeiro import?**
- Todos os valores seguem os templates oficiais das plataformas (não reference desatualizada de skill)
- Char counts validados programaticamente antes de escrever
- Negativas sem `Keyword status` (Google rejeita)
- Campaign type `Search` (não `Search Network`); Networks `Google search`; Type `Phrase match`/`Exact match`
- EU political ads `No` na linha de campanha

> ⚠️ **Lição do Manchester:** a reference da skill `media-buyer-google` usava formato de Editor Desktop obsoleto. Os templates oficiais do Google Ads web (disponíveis em Bulk Actions > Uploads > Templates) são a única fonte de verdade. Sempre baixar antes de gerar.

---

### Etapa 5 — Upload, Ajustes Manuais e Go-Live

**Ordem de upload** (Google Ads web Bulk Actions > Uploads):
1. `01_campaigns.csv` → preview → Apply
2. `02_ad_groups.csv` → preview → Apply
3. `03_keywords.csv` → preview → Apply
4. `04_negative_keywords.csv` → preview → Apply
5. `05_ads.csv` → preview → Apply

**Ajustes manuais obrigatórios pós-upload (campanha fica Paused até terminar):**
- Location targeting (cidades específicas, setting Presence)
- Bid strategy Max CPC Bid Limit
- Ad schedule
- Networks: desmarcar Search Partners e Display Network
- Conversion goals override pra conversão específica
- Tracking Template da conta
- Final URL expansion OFF
- Audience observation (In-market relevante)
- Sitelinks, Callouts, Structured Snippets, Call, Business Name, Logo
- Lista de negativas promovida pra shared library (opcional)

**QA final antes de ligar:**
- Preview do RSA em mobile sem truncamento
- Índice de Qualidade ≥ 5 em keywords principais
- Tag Assistant mostra conversão disparando em teste real
- Navegar pela LP com `?gclid=test` e confirmar que `_gcl_aw` é setado

**Gate 5 — GO no piloto?**
Só ligar a campanha (status Paused → Enabled) depois que todos os checks da QA passam. Campanha ligada = começa a contar o relógio do piloto (30 dias OU 30 conversões pro GO/NO-GO).

---

## Loops de retroalimentação

- **Loop curto (semanal durante piloto):** Search Terms Report toda segunda → adicionar 5–10 negativas/semana; revisar Índice de Qualidade; ajustar pins do RSA se alguma combinação estiver bombando.
- **Loop médio (30 dias):** Decisão GO/NO-GO baseada nos 4 critérios do piloto. Se GO, ativar próximo silo. Se NO-GO, revisão profunda (problema pode ser fora de mídia).
- **Loop longo (mês 2+):** Integração com Guardião do Log (IDs da plataforma no Supabase) + Data Miner (ingestão de performance_metrics) + Growth Lead (análise estruturada por icp_product_map).

## Armadilhas transversais do ciclo (evitar)

1. **Pular validação SERP** — keywords viram adivinhação, CPL real surpreende
2. **Subir campanha sem pre-flight tracking** — conversão zerada, piloto perde 1 semana até descobrir
3. **Abrir todos os silos simultaneamente com budget baixo** — dilui sinal abaixo do threshold de Smart Bidding
4. **Usar reference desatualizada da skill pra gerar CSV** — import rejeitado, retrabalho
5. **Não definir critério GO/NO-GO antes do piloto** — "vamos esperar mais um pouco" vira inércia sem fim
6. **Contar vírgulas manualmente em CSV** — sempre usar `csv.DictWriter` em Python
7. **Assumir que templates oficiais são 100% fiéis** — alguns valores listados como válidos são rejeitados na prática (ex: `Keyword status: Enabled` em negativas). Registrar exceções em `pitfalls.md`

## Timing de referência (piloto ideal)

| Fase | Duração | Output |
|---|---|---|
| Etapa 1: Plano V1 | 1–2h | Plano Sobral inicial em `.md` |
| Etapa 2: Validação SERP | 30–60min | Plano V2 com flags + observações de mercado |
| Etapa 3: Pre-Flight Tracking | 30min–2h (depende do operador confirmar com dev) | Checklist preenchido; bloqueios documentados |
| Etapa 4: CSVs Media Buyer | 30–60min | 5 CSVs + doc explicativa + handoff Guardião |
| Etapa 5: Upload + Ajustes | 1–2h | Campanha Paused na plataforma pronta pra ligar |
| **Total do ciclo** | **~4–7h úteis** | **Piloto no ar** |

Comparação com ciclo SEM padronização (Manchester, pré-PDCA): 3 tentativas de import falhadas, ~2h de retrabalho em debugging de CSV, 2 rodadas adicionais de correção. Este PDCA economiza essas 2–3h e elimina o retrabalho.

---

*Registro derivado do incidente e aprendizado do projeto Grupo Manchester (2026-04-16).*
*Ver também:*
- `references/framework-sem.md` — estrutura de conta Google Ads
- `references/framework-meta-ads.md` — estrutura de conta Meta
- `references/piloto-vs-escala.md` — decisão de modo piloto
- `media-buyer-google/references/csv-search.md` — formato CSV oficial
- `media-buyer-google/references/pitfalls.md` — armadilhas descobertas em produção
