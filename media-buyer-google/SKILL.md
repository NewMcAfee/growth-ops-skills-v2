---
name: media-buyer-google
description: Estrutura campanhas Google Ads (Search + PMax) executáveis a partir da Análise de Campeões do `darwin` e/ou da estratégia do `sobral`, e gera os CSVs prontos pra importar — no dialeto da UI de destino: Web Bulk Upload (5 arquivos separados, web) OU Google Ads Editor desktop (1 CSV combinado) — + doc explicativo + handoff. Pergunta qual UI ANTES de gerar (dialetos não são intercambiáveis: match type, negativas e encoding mudam). Padrão de qualidade cravado — 3 RSAs por grupo (1 controle do DNA campeão + 2 variações de ângulo novo), 15 títulos + 4 descrições SEM pin (default), sentence case, char limits validados em Python, naming Dante+tempero (ICP foco + nome PT), negativas compartilhadas + governança cross-campanha, PMax 1 asset group + Brand Exclusion, 1 campanha de teste. Consome `champion-analysis.yml` (darwin) como fonte primária; `icp_product_map`/Supabase é OPCIONAL (fallback MANUAL-PENDING). Ative quando o sobral entregou a estratégia Google Ads e/ou há uma Análise de Campeões pronta pra virar estrutura/CSV. NÃO use para definir estratégia/budget/alocação (use sobral), analisar campeões/termos (use darwin), estruturar campanhas em Meta/LinkedIn/TikTok (use media-buyer-meta/-linkedin/-tiktok), criar copy nova fora do DNA campeão, ou subir campanhas nas plataformas.
allowed-tools: Read,Write,Bash
---

## Posição no Ecossistema Dante

**Workflow / Fase:** Growth IA — Subfase 3 (Lançamento)
**Papel no sistema:** Traduz estratégia Google Ads do Sobral em estrutura de conta executável — CSV para Google Ads Editor + registro no Supabase via Guardião do Log.

### Recebe de
| Origem | O que recebe | Formato |
|--------|-------------|---------|
| **darwin** (primária) | **Análise de Campeões** — clusters→grupos, ad_dna→RSA controle, negatives_shared (conflict-check), campaign_map→campanhas+teste, tCPA-hint | `champion-analysis.yml` |
| Sobral | Plano de Mídia: alocação, tCPA por segmento, canais, budget | Documento .md |
| Supabase / Operador (**opcional**) | Combinações icp_product_map SE existir — senão `MANUAL-PENDING` | UUIDs ou `MANUAL-PENDING` |
| Operador | URL da LP, budget diário por campanha, geo/idioma | Texto |

### Entrega para
| Destino | O que entrega | Formato |
|---------|--------------|---------|
| Operador | CSVs no **dialeto da UI escolhida**: Web Bulk = 5 arquivos (`01_campaigns`…`05_ads`) · Editor = 1 CSV combinado (`editor_import.csv`) | Arquivos .csv |
| Operador | Documento explicativo de estrutura | .md |
| Guardião do Log | JSON de campanhas/grupos/anúncios para registro | Handoff estruturado |

### Contratos inegociáveis
- Cada grupo mapeado a um **cluster de intenção** (da Análise de Campeões) OU a uma combinação `icp_product_map` (fallback `MANUAL-PENDING`)
- Nomenclatura **Dante+tempero** (ICP foco + nome PT — ver Padrão de Qualidade v2)
- Search: 10-15 keywords por grupo, **só Exact + Phrase** (sem Broad sem histórico)
- RSA: **3 anúncios por grupo (1 controle DNA campeão + 2 variações), 15 títulos + 4 descrições, SEM pin (default)** — ver Padrão de Qualidade v2
- CSVs **no dialeto da UI** (Web Bulk = 5 arquivos · Editor = 1 CSV; ver `csv-search.md` vs `csv-editor.md`) com char limits ≤30/≤90/≤15 **validados em Python** — sem erro de formato
- Não define estratégia, não cria copy nova fora do DNA campeão, não executa na plataforma

---

# Media Buyer Google

## Padrão de Qualidade v2 (cravado — consome `darwin`, RSAs definitivas)

> Contrato de qualidade. **Supera** menções antigas de "mínimo 8 títulos" / "Editor Desktop".

**Fonte primária = Análise de Campeões (`darwin`).** De `champion-analysis.yml`: `clusters`→grupos (1 por cluster, ICP foco no nome) · `ad_dna`→RSA **controle** · `negatives_shared` (conflict-check já feito)→negativas · `campaign_map`→campanhas isoladas por intenção + **1 campanha de teste** · `tCPA-hint` por segmento. Sem Supabase → `MANUAL-PENDING` (não travar).

**Anúncios (RSA) — por grupo:**
- **3 RSAs** = 1 **controle** (DNA campeão do darwin) + 2 **variações de ângulo novo** distintas entre si e do controle.
- **15 títulos (≤30) + 4 descrições (≤90)**, paths ≤15. **SEM pin (default)** — Ad Strength ≠ performance (Optmyzr 20k contas); partial-pin do título #1 é alternativa validada que o operador pode pedir.
- **Sentence case > Title Case** (validado 3,7× CPA) — copy human-like, não corporativa.
- **Diversidade:** feature / benefit / prova / CTA, sem redundância (≥12 títulos distintos por RSA).
- **Anti-AI-slop:** sem "o melhor"/"confiado por milhões"/"oferta por tempo limitado"; passe editorial.

**Validação programática (Python, ANTES de escrever o CSV):** char limits ≤30/≤90/≤15 + restauração de acentos PT-BR + checagem de distinção. NÃO confiar no LLM contar caracteres.

**Naming Dante+tempero:**
- Campanha: `STATUS_GOOG_OBJETIVO_PRODUTO_TEMA` (ex: `TEST_GOOG_LEAD_SigoERP_Concorrentes`)
- Grupo: `GRP-[ICPFOCO]-[PROD]_[INTENCAO]-[NomePT]_[NNN]` (ex: `GRP-GRANDES-SIGO_CONC-Sienge_001`)
- Asset group PMax: `AGP-[ICPFOCO]-[PROD]_[TEMA]_[NNN]`

**Negativas:** `negatives_shared` do darwin (conflict-check feito) no nível campanha + **governança cross-campanha** — negativar marca em não-branded; termos prioritários de cada ICP em **match Exata** pra vencer a prioridade do PMax.

**PMax:** **1 asset group** no go-live (fragmentar até 8-12 só após >30 conv/30d) + **Brand Exclusion obrigatória** + search themes (do `champion-analysis`).

**Saída (dialeto = UI escolhida no Passo 1):**
- **Web Bulk Upload** (Dialeto B) → **5 CSVs** (`01_campaigns`…`05_ads`), UTF-8, `Row Type`/`Action`, `Phrase match`. Ver `references/csv-search.md`.
- **Google Ads Editor** (Dialeto A) → **1 CSV combinado** (`editor_import.csv`), **UTF-8 com BOM** (`utf-8-sig`), `Type=phrase/exact`, negativas na coluna `Keyword`. Ver `references/csv-editor.md`.
- Em ambos: Python `csv.DictWriter` (`QUOTE_MINIMAL`) + char limits validados antes de escrever. Ver `pitfalls.md`.

---

## Antes de Começar

Leia estes arquivos antes de qualquer output:
- `~/dante/DANTE.md` — princípios do sistema
- `~/dante/docs/taxonomia.md` — contrato de nomenclatura
- `~/.claude/skills/sobral/references/framework-sem.md` — estrutura de conta Google Ads
- `~/.claude/skills/media-buyer-google/references/csv-search.md` — **Web Bulk Upload (Dialeto B)** — 5 CSVs separados
- `~/.claude/skills/media-buyer-google/references/csv-editor.md` — **Google Ads Editor (Dialeto A)** — 1 CSV combinado + encoding BOM
- `~/.claude/skills/media-buyer-google/references/pitfalls.md` — **armadilhas conhecidas** (leitura obrigatória antes de gerar CSV)
- `~/.claude/skills/media-buyer-google/references/csv-pmax.md` — colunas exatas PMax
- `~/.claude/skills/media-buyer-google/references/pmax-operacao.md` — **operação do PMax já no ar** (asset group ≠ ad set / não separa formato · criativo 0-conv é normal · segmentação só via geo · Brand Exclusion) — campo Sigo 2026
- `~/.claude/skills/media-buyer-google/references/templates-oficiais/` — os 6 CSVs oficiais do Google (referência de verdade do Dialeto B)

> **DOIS dialetos de CSV, NÃO intercambiáveis** (incidente Manchester-2026-04-16 + Martins 2026-06-18). O destino decide: **Web Bulk Upload** (web) = Dialeto B, 5 arquivos · **Editor desktop** (app) = Dialeto A, 1 CSV combinado + valores próprios (`Type=phrase` sem "match", negativas na col `Keyword`, `utf-8-sig`). Gerar o dialeto errado pro destino **quebra o import**. Por isso o Passo 1 PERGUNTA qual UI antes de gerar.

---

## Workflow

### Passo 1 — Coleta de Contexto

Colete ou confirme os seguintes dados antes de avançar:

**Obrigatórios:**
0. **UI de destino — PERGUNTE ANTES DE GERAR:** *"Você vai subir por qual UI: Web Bulk Upload (web, Tools > Bulk Actions > Uploads) ou Google Ads Editor (app desktop, Account > Import)?"* Isso **define o dialeto** do CSV — não são intercambiáveis (match type, negativas, encoding mudam). Web → **Dialeto B** (`csv-search.md`, 5 arquivos). Editor → **Dialeto A** (`csv-editor.md`, 1 CSV + BOM). Não assuma; gerar o dialeto errado quebra o import (Martins 2026-06-18).
1. **`champion-analysis.yml`** (darwin) — FONTE PRIMÁRIA: `clusters`, `ad_dna`, `negatives_shared`, `campaign_map`, `tCPA-hint`. **OU** o Plano de Mídia do Sobral, se não houver Análise de Campeões.
2. URL da landing page + budget diário por campanha (do Plano de Mídia / Sobral)
3. Tipo(s) de campanha: Search / PMax
4. Geo e idioma (padrão: Brasil / `pt`)

**Opcionais (fallback — NÃO travar por ausência):**
5. `icp_product_map` / Supabase (`project_id`, `version_id`, UUIDs) — SE existir; senão usar ref `MANUAL-PENDING` (caso comum em conta sem Supabase populado).

**Se não houver champion-analysis nem Sobral:** colete briefing express (objetivo, ICP, keywords-semente, budget) e documente que foi sem validação upstream.

Para buscar as combinações icp_product_map:
```bash
# Instrua o operador a executar no Supabase:
SELECT ipm.id, ipm.priority, ipm.status,
       i.icp_ref, i.name as icp_name, i.awareness_level,
       i.primary_pain, i.geo,
       p.product_ref, p.name as product_name, p.puv_statement
FROM icp_product_map ipm
JOIN icps i ON ipm.icp_id = i.id
JOIN products p ON ipm.product_id = p.id
WHERE ipm.project_id = '<project_id>'
  AND ipm.version_id = '<version_id>'
  AND ipm.status IN ('active', 'testing')
ORDER BY ipm.priority;
```

---

### Passo 2 — Plano de Estrutura (Intermediário)

Antes de gerar o CSV, crie o arquivo `plano-estrutura-goog.md` com:

```markdown
# Plano de Estrutura Google Ads — [Nome do Projeto]
**Data:** [data]  **version_id:** [uuid]

## Campanhas

| Nome da Campanha | Tipo | Objetivo | icp_product_maps cobertos | Budget Diário |
|-----------------|------|----------|--------------------------|---------------|
| TEST_GOOG_LEAD_ProdutoX_LandingPage | Search | LEAD | ICP-A/PROD-1, ICP-B/PROD-1 | R$50 |

## Grupos de Anúncios por Campanha

### [Nome da Campanha]
| Nome do Grupo | icp_product_map_id | Tipo de Intenção | Nº Keywords | Consciência |
|--------------|-------------------|-----------------|-------------|-------------|
| GRP-ICP-A-PROD-1_SOLUTION_001 | uuid | Solution-aware | 12 | SOL |

## Estratégia de Keywords por Grupo
[Para cada grupo: lista de keywords com match types + lista de negativas]

## Estratégia RSA por Grupo
[Para cada grupo: 8+ títulos com pilar (Marca/KW/Benefício/CTA) + 4 descrições com pilar (Autoridade/Benefício/Loss/Solução)]
```

**Apresente o plano ao operador para validação antes de gerar o CSV.**

> "Plano de estrutura gerado em `plano-estrutura-goog.md`. Confirma a estrutura antes de gerar o CSV? (sim/ajustar)"

---

### Passo 3 — Geração dos CSVs (dialeto = UI do Passo 1)

Após validação do plano, gere no dialeto da UI escolhida. **A estrutura (campanhas/grupos/keywords/negativas/RSAs) é a mesma; só o formato do CSV muda.**

#### Passo 3B — Google Ads Editor (Dialeto A) — `editor_import.csv`
Se a UI = Editor desktop: gere **1 CSV combinado** seguindo `references/csv-editor.md`. Resumo do que muda vs Web Bulk:
- 1 arquivo só; o Editor infere o tipo da linha pelas colunas (sem `Row Type`/`Action`/`Level`/`Ad type`).
- `Type` = `phrase`/`exact`/`broad` (**sem "match"**); `Campaign type=Search`; `Language=pt`.
- Negativas na coluna **`Keyword`** (`"x"`=phrase, `[x]`=exact) + `Type=Campaign negative` + `Ad group` vazio.
- **Encoding `utf-8-sig` (UTF-8 com BOM)** — senão mojibake + falso "char>30" no Editor.
- Gerador-base + header completo em `references/csv-editor.md`. Pular para o Passo 4.

#### Passo 3A — Web Bulk Upload (Dialeto B) — 5 CSVs
Se a UI = Web Bulk: gere **5 arquivos separados** usando as colunas exatas dos templates oficiais (`references/templates-oficiais/`). **NÃO use um único CSV flat** — o Web Bulk Upload exige 1 arquivo por tipo de entidade.

**Arquivos a gerar (na ordem de upload):**

| # | Arquivo | Row Type | Template oficial |
|---|---|---|---|
| 1 | `01_campaigns.csv` | `Campaign` | `templates-oficiais/campaign_template.csv` |
| 2 | `02_ad_groups.csv` | `Ad group` | `templates-oficiais/ad_group_template.csv` |
| 3 | `03_keywords.csv` | `Keyword` | `templates-oficiais/keyword_template.csv` |
| 4 | `04_negative_keywords.csv` | `Negative keyword` | `templates-oficiais/ad_group_negative_keyword_template.csv` |
| 5 | `05_ads.csv` | `Ad` | `templates-oficiais/responsive_search_ad_template.csv` |

**Regras de geração (detalhes em `references/csv-search.md` e `references/pitfalls.md`):**

1. **Use Python com `csv.DictWriter`** e `quoting=csv.QUOTE_MINIMAL` — contar vírgulas manualmente em headers de 30–57 colunas é receita pra erro.
2. **Encoding UTF-8** (acentos em Latin-1 corrompem).
3. **Toda linha começa com `Row Type` + `Action`** (`Add` para criação).
4. **Valores obrigatórios em case exato:**
   - `Campaign type`: `Search` (NÃO `Search Network`)
   - `Networks`: `Google search` (NÃO `Search`)
   - `Type` de keyword: `Phrase match` / `Exact match` / `Broad match` (com a palavra `match`)
   - `Language`: código ISO curto `pt` / `en`
   - `EU political ads`: `No` (obrigatório desde 2026-04-01, só na linha de campanha)
   - `Keyword status` nas negativas: **VAZIO** (Google rejeita `Enabled` apesar do template listar)
5. **Decimais com ponto** (`67`, `2.50`), nunca vírgula.
6. **Smart Bidding** (`Maximize clicks`, etc.) → `Default max. CPC` dos grupos deixar VAZIO. Cap de CPC vai como ajuste manual no Editor pós-upload.
7. **Validação programática de char limits** antes de escrever: Headlines ≤30, Descriptions ≤90, Paths ≤15.

**Template Python mínimo** (usar como base, adaptando aos dados do projeto):

```python
import csv
from pathlib import Path

CAMPAIGN_HEADERS = [...]  # copiar do template oficial
# idem AD_GROUP_HEADERS, KEYWORD_HEADERS, NEGATIVE_HEADERS, RSA_HEADERS

def write_csv(path, headers, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in headers})

# gera os 5 arquivos...
```

Salve cada um como `0N_<tipo>.csv` na pasta do projeto. Ver exemplo completo funcional no projeto Manchester (`03_Midia-Paga/midia-buyer-goog/_generate_csv.py`).

---

### Passo 4 — Documento Explicativo

Gere `estrutura-goog-[slug-projeto]-[data].md` com:

```markdown
# Estrutura de Campanhas Google Ads — [Nome do Projeto]
**Gerado em:** [data]  **Versão:** [version_id]

## Visão Geral
[Tabela resumo: campanha → tipo → grupos → keywords → ICPs cobertos]

## Lógica de Estrutura
[Por que essa divisão de campanhas foi escolhida]

## Detalhamento por Grupo de Anúncios

### [Nome do Grupo]
**icp_product_map:** [icp_ref] + [product_ref] (UUID: [uuid])
**Tipo de intenção:** [SOLUTION/PROBLEM/BRANDED/COMPETITOR/GENERIC]
**Nível de consciência do ICP:** [UNC/PRB/SOL/PRO]

**Keywords ([N] total):**
| Keyword | Match Type | Justificativa |
|---------|-----------|---------------|

**Negativas do grupo:**
[lista]

**RSA — Títulos ([N]):**
| Título | Pilar | Pin |
|--------|-------|-----|

**RSA — Descrições (4):**
| Descrição | Pilar Psicológico |
|-----------|------------------|

## Negativas de Campanha
[Lista de keywords negativas aplicadas no nível de campanha]

## Próximos Passos
- [ ] Importar CSV no Google Ads Editor
- [ ] Adicionar platform_id no Guardião do Log após subir as campanhas
- [ ] Conferir Índice de Qualidade nas primeiras 72h
```

---

### Passo 5 — Handoff ao Guardião do Log

Após gerar o CSV, produza o handoff estruturado para o Guardião do Log registrar cada entidade no Supabase.

**Formato do handoff:**

```
HANDOFF MEDIA BUYER GOOG → GUARDIÃO DO LOG
project_id: [uuid]
version_id: [uuid]
validator_url: [perguntar ao operador se não souber]

CAMPANHAS A REGISTRAR:
---
campanha_1:
  nome: TEST_GOOG_LEAD_ProdutoX_LandingPage
  canal: GOOG
  status: TEST
  objetivo: LEAD
  produto: ProdutoX
  destino: LandingPage
  icp_product_map_id: [uuid da combinação principal]
  platform_id: [preencher após subir]
  launched_at: [preencher após subir]
---
[repetir para cada campanha]

GRUPOS A REGISTRAR (após ter os campaign_ids):
[lista estruturada por campanha]

ANÚNCIOS A REGISTRAR (após ter os ad_set_ids):
[lista estruturada por grupo]
```

> "Handoff gerado. Ao subir as campanhas no Google Ads Editor, anote os IDs das campanhas/grupos/anúncios e acione o **Guardião do Log** para registrar no Supabase."

---

## Nomenclatura Dante Adaptada para Google Ads

### Campanhas
Convenção B (alinhada à taxonomia de entidade Meta): `{STATUS}_{CANAL}_{OBJ}_{PRODUTO}_{SEGMENTO}`

| Campo | Valores |
|-------|---------|
| STATUS | `HALL`, `TEST`, `EVER` |
| CANAL | `GOOG` (fixo) |
| OBJ | Estágio de conversão OTIMIZADO: `LEAD` (form da LP), `SALES`, `TRFC`, `AWAR` — nunca assumir default sem checar o evento real |
| PRODUTO | CamelCase sem espaços (ex: `CursoLongo`, `BootcampVendas`) |
| SEGMENTO | Rótulo de intenção/segmento no 5º campo (ex: `Branded`, `NucleoLocal`, `Confeitaria`). ⚠️ Busca **não tem temperatura de público** — `Frio/Morno/Quente` é campo do Meta; no Google (Search) o 5º campo é a **intenção**. |

Exemplo: `EVER_GOOG_LEAD_CursoLongo_Branded`

> **Migração A→B (2026-07-05).** Antes: "Mesma taxonomia Dante", 5º campo = DESTINO (`LandingPage`). B unifica OBJ como estágio de conversão; a diferença Meta(temperatura)×Google(intenção) no 5º campo é **intencional** (busca não tem temperatura de público).

### Grupos de Anúncios (Search / Display)
Formato: `GRP-[ICP_REF]-[PROD_REF]_[TIPO_INTENTO]_[N]`

| Campo | Definição | Exemplos |
|-------|-----------|---------|
| ICP_REF | icp_ref do banco, hífens mantidos | `ICP-A`, `ICP-B2` |
| PROD_REF | product_ref do banco, hífens mantidos | `PROD-1`, `PROD-3` |
| TIPO_INTENTO | Tipo de intenção de busca | `SOLUTION`, `PROBLEM`, `BRANDED`, `COMPETITOR`, `GENERIC`, `FEATURES`, `PRICE` |
| N | Sequencial 3 dígitos | `001`, `002` |

Exemplos:
- `GRP-ICP-A-PROD-1_SOLUTION_001` — ICP-A buscando solução para PROD-1
- `GRP-ICP-B-PROD-2_PROBLEM_001` — ICP-B com dor/problema, PROD-2
- `GRP-ICP-A-PROD-1_BRANDED_001` — buscas pela marca, PROD-1

### Asset Groups (PMax)
Formato: `AGP-[ICP_REF]-[PROD_REF]_[TEMA]_[N]`

### Anúncios RSA
Formato: `AD-[ID]_RSA_[CONSCIENCIA]_[GANCHO]_[VARIACAO]`

| Campo | Valores |
|-------|---------|
| ID | sequencial 3 dígitos |
| FORMATO | `RSA` (fixo para Search) |
| CONSCIENCIA | `UNC`, `PRB`, `SOL`, `PRO`, `MIX` |
| GANCHO | `Loss`, `Proof`, `Story`, `Error`, `Fact`, `Contr` |
| VARIACAO | CamelCase resumo do ângulo (ex: `EconomizeTempo`, `Prova3xROI`) |

Exemplos: `AD-001_RSA_SOL_Proof_ResultadosClientes`, `AD-002_RSA_PRB_Loss_CustoDoProblema`

---

## Regras de Keywords

**Distribuição de match types por grupo (mínimo 10 keywords):**
- 2–3 Exact match: termos de alta intenção, alta precisão
- 3–4 Phrase match: variações de intenção, cobertura moderada
- 3–4 Broad match: expansão semântica (apenas se conta tiver histórico de conversão)
- 1–2 Negative exact / Negative phrase: excluir intenções incompatíveis

**Negativas obrigatórias (sempre incluir):**
- Termos de emprego: "vaga", "emprego", "salário", "currículo"
- Termos gratuitos: "grátis", "de graça", "free", "pirata"
- Termos informativos puros (se objetivo for conversão): "o que é", "como funciona" (avaliar caso a caso)

**Regra de coerência:** Toda keyword de um grupo deve compartilhar a mesma intenção fundamental. Se uma keyword tem intenção diferente, crie um novo grupo para ela.

---

## Regras de RSA

**Títulos (8–15 por grupo):**
Use os 6 Pilares do Sobral (framework-sem.md):
- 2–3 Marca e Público
- 2–3 Termo-Chave e Variações
- 2–3 Benefícios e Diferenciais
- 1–2 CTA

**Descrições (4 por grupo):**
Use os 4 Pilares do Sobral:
1. Autoridade (prova social)
2. Benefício Direto (ganho tangível)
3. Aversão à Perda (risco de não agir)
4. Solução Descritiva (clareza para quem está avaliando)

**Pinagem:** Pin o título de marca na Posição 2 ou 3 apenas se necessário para consistência de marca. Evite pinagem excessiva — reduz combinações testáveis pelo algoritmo.

---

## Anti-patterns

- **Gerar o dialeto errado pro destino:** Web Bulk = 5 arquivos separados (`Row Type`/`Action`, `Phrase match`); Editor = 1 CSV combinado (`Type=phrase`, negativas na col `Keyword`, `utf-8-sig`). Trocar quebra o import. PERGUNTE a UI no Passo 1. Ver `csv-search.md` (B) vs `csv-editor.md` (A).
- **Valores legados genéricos:** `Search Network` e `Portuguese (Brazil)` quebram em AMBOS os dialetos — o correto é `Search` / `pt` nos dois. (NÃO são "valores do Editor" — esse engano quebrou a Martins.) Já `Phrase`/`Exact`/`Broad` sem "match" é o correto **no Editor** (Dialeto A), e errado no Web Bulk (que exige "match").
- **CSV sem BOM no Editor:** `utf-8` puro vira mojibake + falso "char>30" no Editor desktop. Usar `utf-8-sig`. (No Web Bulk, `utf-8` puro está correto.)
- **Faltar `EU political ads`:** Google rejeita desde 2026-04-01. Sempre preencher com `Yes` ou `No` na linha de campanha.
- **`Keyword status: Enabled` em negativas:** Rejeitado na prática mesmo sendo listado como válido no template. Deixar vazio.
- **Max CPC em grupo com Smart Bidding:** Deixar vazio. Cap vai como ajuste manual na campanha.
- **Contar vírgulas manualmente:** Sempre gerar CSV com `csv.DictWriter` em Python. Nunca montar linhas por concatenação de strings.
- **Headlines > 30 / Descriptions > 90 / Paths > 15:** Validar programaticamente antes de escrever.
- **Grupos sem icp_product_map:** Nunca criar grupo sem mapear ao UUID de uma combinação ativa — viola o contrato do Dante (exceção documentada: projetos sem Supabase populado podem usar ref manual `MANUAL-PENDING`, com obrigação de reconciliar depois).
- **Keywords genéricas em todos os grupos:** Sobreposição gera canibalização de leilão. Se houver sobreposição, usar negativas cruzadas entre grupos.
- **Broad match sem histórico:** Não incluir se conta for nova. Use Phrase + Exact até 50+ conversões.
- **RSA com menos de 8 títulos:** Mínimo do contrato Dante = 8 títulos, recomendado 12–15. Menos que isso limita testes do algoritmo.
- **Encoding errado:** Web Bulk = `utf-8`; **Editor = `utf-8-sig` (BOM)**. Latin-1 corrompe acentos em ambos.
- **Subir sem plano validado:** Sempre validar o plano de estrutura com o operador antes de gerar os CSVs.
- **Overpinning:** Máximo 2 headlines pinados por posição. Ao menos 3 totalmente sem pin. Caso contrário o Ad Strength cai.

---

## Avaliação

### Cenário 1 — Search com 2 combinações icp_product_map
**Input:** Sobral entregou estratégia Search; icp_product_map tem ICP-A/PROD-1 (priority 1) e ICP-B/PROD-1 (priority 2); objetivo LEAD; budget R$80/dia
**Comportamento esperado:**
- [ ] Cria plano com ao menos 2 campanhas OU 1 campanha com 2 grupos (um por combinação)
- [ ] Cada grupo tem icp_product_map_id mapeado explicitamente
- [ ] Cada grupo tem ≥10 keywords com mix Exact/Phrase/Broad
- [ ] Cada grupo tem 1 RSA com ≥8 títulos e 4 descrições
- [ ] CSV exportado com colunas exatas do csv-search.md
- [ ] Handoff gerado para Guardião do Log

### Cenário 2 — PMax
**Input:** Conta com 60+ conversões/mês; Sobral recomendou PMax; 1 produto, 2 ICPs
**Comportamento esperado:**
- [ ] Lê references/csv-pmax.md antes de gerar
- [ ] Cria Asset Groups distintos por combinação icp_product_map
- [ ] Inclui Search Themes (até 25 por asset group) baseados nas keywords do Sobral
- [ ] Não gera coluna "Keyword" (não aplicável em PMax)
- [ ] Adverte que PMax precisa de account-level negative keywords configuradas separadamente

### Cenário 3 — Recuperação de erro de coluna
**Input:** Operador diz "o import deu erro de coluna desconhecida / tipo de correspondência inválido"
**Comportamento esperado:**
- [ ] Confirma a UI (Web vs Editor) e lê o reference do dialeto certo (`csv-search.md` ou `csv-editor.md`)
- [ ] Identifica o campo com nome/valor incorreto (ex: `Phrase match` num CSV de Editor)
- [ ] Recria apenas as linhas/colunas afetadas (não o CSV inteiro)
- [ ] Não pede todos os dados novamente — usa o plano já gerado

### Cenário 4 — Destino é o Google Ads Editor (desktop)
**Input:** Operador diz "vou subir pelo Editor" (ou responde Editor no Passo 1)
**Comportamento esperado:**
- [ ] Gera **1 CSV combinado** (`editor_import.csv`), NÃO 5 arquivos
- [ ] `Type` = `phrase`/`exact` (sem "match"); `Campaign type=Search`; `Language=pt`
- [ ] Negativas na coluna `Keyword` (`"x"`=phrase) + `Type=Campaign negative` + `Ad group` vazio
- [ ] Encoding `utf-8-sig` (BOM) — confere que acentos não viram `Ã§`
- [ ] Char limits validados em Python antes de escrever; campanhas `Paused`
