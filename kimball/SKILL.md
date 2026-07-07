---
name: kimball
description: Consolida e cruza dados brutos multi-fonte de marketing+CRM (campanhas de mídia por plataforma, leads, contatos, deals) num dataset de retorno closed-loop — resolve identidade (email/telefone), normaliza no boundary e produz datasets tratados no grão certo + relatório de qualidade DAMA. Use ao receber exports crus (CSVs/planilha) de um cliente e precisar higienizar/deduplicar/cruzar lead→contato→deal→campanha antes da análise; OU, no modo `conformar-export`, quando um export cru de CRM precisa virar staging no schema de um dataset-alvo vivo (aba canônica de planilha/feed) — repara conteúdo (mojibake, colunas mortas, placeholders), deriva campos por precedência com guardas e deduplica por anti-join contra o alvo, gerando -completo/-novos pra append sem duplicar. NÃO use para baixar dados (feed-planilha-vault), analisar/interpretar retorno ou gerar plano (newton/darwin/falconi), nem modelar banco (data-engineer).
allowed-tools: Read,Write,Edit,Bash,Glob,Grep
---

# kimball — Consolidação e Crosswalk de Dados Marketing+CRM

Homenagem a Ralph Kimball (dimensional modeling, conformed dimensions, closed-loop). Esta skill é o **elo que ninguém faz**: costurar exports crus e heterogêneos de mídia paga + leads + CRM num dataset de retorno fim-a-fim (gasto→lead→oportunidade→receita→campanha), pronto pra análise. Não baixa dado, não analisa, não modela banco — **higieniza, normaliza, deduplica por identidade e cruza**, com QA auditável.

## Contexto — por que existe

Toda análise de retorno de um cliente esbarra na mesma pré-condição: os dados chegam sujos, despadronizados, duplicados e em fontes desconectadas (uma planilha de leads sem UTM, um CRM com telefone em 3 formatos, campanhas por plataforma em grãos diferentes). Bibliotecas de record linkage (Splink/dedupe) resolvem só o dedup; ingestores de mídia resolvem só as campanhas; as skills de análise começam **depois** do dataset pronto. O meio — resolver identidade E cruzar lead→CRM→deal→campanha até fechar o retorno — é o buraco que o `kimball` preenche. Ele **incorpora** o estado da arte (Fellegi-Sunter, Kimball, DAMA, tidy data) como regras concretas (ver `references/regras-aplicadas.md`).

## Regra de ouro

**Só átomos aditivos são persistidos** (spend, impressions, clicks, leads, deals, revenue). CTR/CPL/CPA/ROAS **nunca** viram coluna — são `SUM(x)/NULLIF(SUM(y),0)` no ponto de consumo. Razão não é aditiva: média de CPLs ≠ CPL do total. Isso é lei, não preferência.

## Workflow

### Passo 0 — Perfilar e mapear (a generalização mora aqui)
Antes de qualquer transformação, **perfile cada fonte** e escreva o `config.yml`. Nunca assuma schema.
1. Liste os CSVs (`Glob`) e leia o header + 3 linhas de cada.
2. Para cada fonte, detecte e **declare no config** (não infira em runtime):
   - **Locale numérico** (`pt-BR` vírgula-decimal vs `en-US`) — amostrando valores monetários.
   - **Formato de data** por fonte (`%d-%m-%Y`, `%Y-%m-%d`, ISO…) — datas ambíguas EXIGEM formato declarado.
   - **Grão real** de cada fato de mídia — se houver sub-dimensão (search-term, keyword, hora), marque `aggregate: true`.
   - **Prefixos de ID** de plataforma (`ag:`, `c:`, `p:+`) — o motor faz strip; confirme que a chave bate entre fontes.
   - **Chave de identidade** disponível no lead (email? telefone? ambos) e a **chave CRM** (contact_id).
   - **Coluna de stage/ganho** do CRM e seus valores `won`/`lost` — e rode fill-rate: coluna majoritariamente vazia ou de valor único é **morta** (não use sem confirmar).
3. Copie `assets/config.example.yml`, ajuste nomes de arquivo/coluna ao stack do cliente. **Confirme o mapeamento com o operador** antes de rodar (5 min de revisão evita retrabalho).

Referência do schema do config: leia `assets/config.example.yml` (comentado campo a campo).

### Passo 1 — Consolidar mídia (fato ad×dia)
Rode o motor; ele normaliza cada plataforma, faz strip de prefixo, **agrega sub-grão com invariante não-fan-out** (`SUM` pré==pós), e faz union das plataformas num só fato `ad×dia`. O grão é atômico e declarado antes de tudo (Kimball). Se precisar de search-term, é **fato separado** — nunca coluna do fato ad×dia.

### Passo 2 — Higienizar e resolver identidade (leads)
Normalização determinística no boundary (email canônico provider-específico, telefone E.164, unicode-fold nas chaves preservando o raw). Dedup por **union-find só em aresta forte** (email/telefone exato pós-normalização), com **guards anti-over-merge**: telefone compartilhado ignorado, email role-based não-chave, hard-conflict (2 emails distintos via mesmo telefone) bloqueia a união. Golden record por **survivorship field-level** (completude→recência), não "registro mais recente vence".

### Passo 3 — Crosswalk (lead → plataforma → contato → deal)
Cruza em cadeia: `platform_leads` (form nativo) recupera ad_id/canal → `contatos` traz contact_id → `deals` via contact_id traz receita/stage. Isso é o **accumulating snapshot** do funil: 1 linha por lead com os marcos. Receita no **grão de deal** (nunca pipeline agregado).

### Passo 4 — Atribuição enriquecida (config-driven)
`utm_source` derivado por precedência: (1) match em plataforma → canal daquela plataforma; (2) UTM do CRM (deal); (3) nome de campanha no lead; (4) default. As regras de canal são **regex declaradas no config** (`attribution.channel_rules`) — o padrão de nomenclatura do cliente, **nunca hardcoded**. Recupera o canal do lado sem ad_id (ex: Google). A coluna `attribution_source` deixa cada caso auditável (`platform_match`/`deals_utm`/`lead_name`/`none`) — heurística nunca silenciosa. Regex em YAML: **use aspas simples** (`'\bABO\b'`); aspas duplas convertem `\b` em backspace (o motor auto-cura, mas o exemplo já vem correto).

### Passo 5 — QA report (6 dimensões DAMA)
O motor emite `relatorio_qualidade.md` com checks **binários e com threshold explícito**: completeness ≥99% em chaves de join, uniqueness = 0 duplicata de grão, accuracy = join integrity (% ad_id que casa), validity = % parseável, + alerta de coluna morta. **PASS/WARN/FAIL** por check. QA sem threshold declarado é opinião, não QA.

## Modo `conformar-export` — export cru → staging de um alvo vivo

Quando o destino NÃO é o dataset analítico do kimball, e sim **um dataset canônico que já
existe e continua vivo** (aba de planilha alimentando um feed, tabela de vault) — "higieniza
esse export pra eu colar na aba X mantendo o padrão" — siga
`references/modo-conformar-export.md`. Difere do modo default em 3 pontos: (1) o **schema e
as convenções do alvo são o contrato** (observados em linhas reais dele, nunca assumidos);
(2) **dedupe é anti-join contra o alvo** por chave, emitindo staging `-completo` + `-novos`;
(3) o staging **nunca é aplicado direto** — o append é do operador/pipeline. Reusa as
doutrinas do modo default: fill-rate → coluna morta, normalização no boundary, derivação
por precedência declarada com guardas + trilha de auditoria, QA com contagens reconciliadas.
Validado no caso Martins Locações 2026-07 (números no reference).

## Como rodar

```bash
py scripts/consolidate.py <config.yml>
```
Saídas em `out_dir`: `campanhas_consolidada.csv`, `leads_master.csv`, `deals_higienizados.csv` + `deals_ganhos.csv` (se CRM deals presente), `relatorio_qualidade.md`.

Para casos fora do padrão do motor, **componha com as primitivas** de `scripts/lib_kimball.py` (normalizadores, `resolve_identity`, `aggregate_no_fanout`, `survivorship`, checks DAMA) num script ad-hoc — não force o config a cobrir o que ele não modela.

## Loop de feedback (obrigatório antes de entregar)

1. Rode o motor e **leia o `relatorio_qualidade.md`**.
2. Verifique os invariantes: join integrity ≥99%? uniqueness 100%? algum FAIL?
3. Se houver alerta de **coluna morta** (ex: flag booleana sempre FALSE), pare e confirme com o operador qual é o campo real de ganho antes de seguir.
4. Reconcilie um número contra a fonte (ex: `SUM(spend)` do consolidado ≈ total da plataforma).
5. Só entregue quando os checks passam e os órfãos estão explicados. Órfão silencioso = dado perdido sem rastro.

## Padrões de output

- **Tidy data**: long-format (métrica em coluna, dimensão em coluna, valor na célula), uma unidade observacional por tabela, IDs como string, datas ISO, schema tipado estável.
- **leads_master**: grão = 1 lead único; colunas de identidade, origem (canal/ad_id/campanha + `attribution_source`), CRM (contact_id), funil (status_deal, valor_ganho, marcos).
- **campanhas_consolidada**: grão = ad×dia; só átomos aditivos.
- **relatorio_qualidade.md**: trilha de auditoria (contagens in/out, invariantes, checks DAMA, armadilhas detectadas).

## Anti-patterns (rejeitar)

- ❌ **Persistir CTR/CPL/ROAS** — razão não-aditiva; calcule on-demand.
- ❌ **ID em coluna numérica** — IDs de 15-19 dígitos perdem precisão em float; sempre string.
- ❌ **Inferir locale/data linha-a-linha** — declare por fonte no config.
- ❌ **Transitividade cega** — fundir clusters por match fraco/telefone compartilhado gera over-merge irreversível de clientes distintos.
- ❌ **Aplicar regra de email do Gmail globalmente** — dots/+tag são provider-específicos; global = over-merge silencioso.
- ❌ **Confiar em coluna de status sem fill-rate** — flag morta contamina o funil (foi o `É negócio fechado` do Iga).
- ❌ **Join que multiplica o grão** — search-term/keyword infla custo; cheque não-fan-out.
- ❌ **Hardcodar nomes de coluna/arquivo do cliente no motor** — tudo vem do config; cliente é exemplo em `references/`.
- ❌ **Regex com `\b` em YAML de aspas duplas** — vira BACKSPACE (`\x08`) e nunca casa; use aspas simples. O motor auto-cura, mas não confie nisso.

## Arquivos da skill

- `scripts/lib_kimball.py` — primitivas testadas (normalização, identidade, agregação, QA).
- `scripts/consolidate.py` — orquestrador config-driven.
- `assets/config.example.yml` — schema do mapeamento, comentado (o Passo 0 preenche isto).
- `references/regras-aplicadas.md` — práticas validadas da pesquisa → regras concretas (leia ao calibrar thresholds).
- `references/exemplo-iga-blumenau.md` — caso real end-to-end (números esperados, armadilhas encontradas).
- `references/modo-conformar-export.md` — modo conformar-export: workflow 6 passos + anti-patterns + caso Martins.

## Cenários de avaliação

**Cenário 1 — Consolidação completa.** Input: pasta com abas Meta/Google/leads/contatos/deals crus + config mapeado. Esperado: gera os 5 CSVs; QA todo PASS; join integrity ad_id ≥99%; relatório lista dedup N→M.

**Cenário 2 — Coluna de status morta.** Input: CRM cujo campo booleano de "fechado" é 100% FALSE, com ganho real em outra coluna de stage. Esperado: a skill **detecta e alerta** a coluna morta no Passo 0/QA e usa a coluna de stage real (não reporta 0 vendas silenciosamente).

**Cenário 3 — Telefone compartilhado / hard-conflict.** Input: leads onde um mesmo telefone (recepção) liga pessoas com emails distintos. Esperado: a skill **não funde** esses leads (bloqueia união por hard-conflict / telefone compartilhado) e reporta a contagem de bloqueios — em vez de colapsar clientes distintos num só.

**Cenário 4 — Conformar export a alvo vivo.** Input: export sujo de deals do CRM (coluna 100% `#ERROR!`, canal fixo errado, emojis, placeholders UTM) + duas abas canônicas de planilha como destino. Esperado: detecta o modo `conformar-export`; observa convenções do alvo em linhas reais (datas BR, decimal vírgula, chave = telefone sem DDI); deriva o campo morto por precedência com guarda; emite staging `-completo` + `-novos` (anti-join contra o alvo atual) por aba; relata overlap, colunas descartadas e correções semânticas com original preservado — e **não** cola nada no alvo.
