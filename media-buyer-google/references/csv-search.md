# CSV Google Ads — Web Bulk Upload (Dialeto B)

> **IMPORTANTE:** O Google Ads tem **2 dialetos de CSV, ambos válidos** — escolha pelo destino:
> - **Web Bulk Upload** (web, *Tools > Bulk Actions > Uploads*) → **este arquivo (Dialeto B)** → **5 CSVs separados**, ancorados nos templates oficiais.
> - **Editor Desktop** (app, *Account > Import > From file*) → `csv-editor.md` (**Dialeto A**) → **1 CSV combinado**.
>
> Não são intercambiáveis (match type, negativas, encoding mudam). **Pergunte qual UI ANTES de gerar** (Passo 1 do SKILL.md). Este doc cobre o **Dialeto B**.

## Estrutura: 5 arquivos separados, não um CSV flat

Cada tipo de entidade tem seu próprio arquivo com headers próprios. Upload na ordem:

| Ordem | Arquivo | Row Type | Template oficial |
|---|---|---|---|
| 1 | `01_campaigns.csv` | `Campaign` | `templates-oficiais/campaign_template.csv` |
| 2 | `02_ad_groups.csv` | `Ad group` | `templates-oficiais/ad_group_template.csv` |
| 3 | `03_keywords.csv` | `Keyword` | `templates-oficiais/keyword_template.csv` |
| 4 | `04_negative_keywords.csv` | `Negative keyword` | `templates-oficiais/ad_group_negative_keyword_template.csv` |
| 5 | `05_ads.csv` | `Ad` | `templates-oficiais/responsive_search_ad_template.csv` |

> Dependências: upload 2 depende de 1 (campanha tem que existir), upload 3–5 dependem de 2 (grupos têm que existir). Por isso a ordem importa.

## Colunas obrigatórias em toda linha

Toda linha dos 5 arquivos começa com estas 2 colunas:

| Coluna | Valores possíveis |
|---|---|
| `Row Type` | `Campaign` / `Ad group` / `Keyword` / `Negative keyword` / `Ad` |
| `Action` | `Add` / `Edit` / `Remove` |

---

## 01 — Campaigns (`01_campaigns.csv`)

**Header exato:**
```
Row Type,Action,Campaign status,Campaign ID,Campaign,Campaign type,Networks,Budget,Delivery method,Budget type,Bid strategy type,Bid strategy,Campaign start date,Campaign end date,Language,Location,Exclusion,Devices,Label,Target CPA,Target ROAS,Display URL option,Website description,Target Impression Share,Max CPC Bid Limit for Target IS,Location Goal for Target IS,Tracking template,Final URL suffix,Custom parameter,Inventory type,Campaign subtype,Video ad formats,EU political ads
```

**Valores críticos (case exato):**

| Coluna | Valores válidos (Add) | Armadilha comum |
|---|---|---|
| `Campaign status` | `Enabled` / `Paused` / `Removed` | — |
| `Campaign type` | `Search` / `Display` / `Video` | ❌ **não** `Search Network` |
| `Networks` | `Google search` / `Search partners` / `Display Network` / `Google TV` / `YouTube videos` | ❌ **não** `Search`, **não** `Search Network` |
| `Budget` | Número puro com ponto decimal (`67`, `10.00`) | ❌ não usar R$ nem vírgula decimal |
| `Budget type` | `Daily` / `Campaign Total` / `Monthly` | — |
| `Delivery method` | `Standard` | — |
| `Bid strategy type` | `Maximize clicks` / `Manual CPC` / `CPC (enhanced)` / `Target CPA` / `Maximize Conversions` / `Target ROAS` / etc. | Use `Maximize clicks` para conta nova sem conversões |
| `Language` | Código ISO curto: `pt`, `en`, `es` | ❌ **não** `Portuguese (Brazil)` |
| `Location` | `Brazil` (nome em inglês, nível país) OU cidade por extenso `Rio de Janeiro, Rio de Janeiro, Brazil` | Múltiplas cidades: separar por `;` |
| `EU political ads` | `Yes` / `No` | **OBRIGATÓRIO desde 2026-04-01.** Só vai na linha de campanha |

---

## 02 — Ad Groups (`02_ad_groups.csv`)

**Header exato:**
```
Row Type,Action,Ad group status,Campaign ID,Campaign,Ad group ID,Ad group,Ad group type,Ad rotation,Default max. CPC,CPC%,Max. CPM,Max. CPV,Target CPA,Target CPM,TrueView target CPV,Label,Tracking template,Final URL suffix,Custom parameter,Target ROAS
```

**Valores críticos:**

| Coluna | Valores válidos | Armadilha |
|---|---|---|
| `Ad group status` | `Enabled` / `Paused` / `Removed` | — |
| `Ad group type` | `Standard` (Search) / `Display` / `Shopping - Product` / `In-stream` / etc. | — |
| `Default max. CPC` | **DEIXAR VAZIO** quando a campanha usa Smart Bidding (Maximize clicks, Target CPA, etc.) | Forçar valor causa erro de parser em locale PT-BR |
| `Ad rotation` | `Optimize` / `Do not optimize` | — |

---

## 03 — Keywords (`03_keywords.csv`)

**Header exato:**
```
Row Type,Action,Keyword status,Campaign ID,Campaign,Ad group ID,Ad group,Keyword ID,Keyword,Type,Label,Default max. CPC,Max. CPV,Final URL,Mobile final URL,Final URL suffix,Tracking template,Custom parameter
```

**Valores críticos:**

| Coluna | Valores válidos | Armadilha |
|---|---|---|
| `Keyword status` | `Enabled` / `Removed` / `Paused` | — |
| `Type` | **`Phrase match`** / **`Exact match`** / **`Broad match`** | ❌ **não** `Phrase` / `Exact` / `Broad` (faltam `match`) |
| `Keyword` | Texto puro, sem colchetes (para exact) nem aspas (para phrase) — o match type vai em `Type` | Não colocar `[kw]` nem `"kw"` no texto |

---

## 04 — Negative Keywords (`04_negative_keywords.csv`)

**Header exato:**
```
Row Type,Action,Keyword status,Level,Campaign ID,Campaign,Ad group ID,Ad group,Keyword ID,Negative keyword,Type
```

**Valores críticos:**

| Coluna | Valores válidos | Armadilha |
|---|---|---|
| `Row Type` | `Negative keyword` | — |
| `Keyword status` | **DEIXAR VAZIO** | ⚠️ Apesar do template listar `Enabled; Removed; Paused`, o Google REJEITA `Enabled` pra negativas na prática. Campo é Optional — omitir. |
| `Level` | **`Campaign`** (nível campanha) ou `Ad group` (nível grupo) | Obrigatório — define se a negativa aplica à campanha inteira ou só a um grupo |
| `Type` | `Phrase match` / `Exact match` / `Broad match` | Igual keywords positivas |
| `Negative keyword` | Texto puro | — |

> Quando `Level = Campaign`, deixar `Ad group` vazio. Quando `Level = Ad group`, preencher `Ad group`.

---

## 05 — Ads — Responsive Search Ads (`05_ads.csv`)

**Header exato:**
```
Row Type,Action,Ad status,Campaign ID,Campaign,Ad group ID,Ad group,Ad ID,Ad type,Label,Headline 1,...,Headline 15,Description 1,Description 2,Description 3,Description 4,Headline 1 position,...,Headline 15 position,Description 1 position,...,Description 4 position,Path 1,Path 2,Final URL,Mobile final URL,Tracking template,Final URL suffix,Custom parameter
```

**Valores críticos:**

| Coluna | Valores válidos | Armadilha |
|---|---|---|
| `Row Type` | `Ad` | — |
| `Ad status` | `Enabled` / `Paused` / `Removed` | — |
| `Ad type` | `Responsive search ad` | Case exato — apenas R maiúsculo |
| `Headline 1..15` | ≤ **30 caracteres** cada, mínimo 3, recomendado 12–15, **ao menos 5 distintos** (sem repetir frases) | Google só mostra aviso de redundância — valida no upload |
| `Description 1..4` | ≤ **90 caracteres** cada, mínimo 2, recomendado 4 | — |
| `Headline N position` | `1` / `2` / `3` ou vazio | Cada headline tem sua própria coluna de posição — evite overpinning |
| `Description N position` | `1` / `2` ou vazio | — |
| `Path 1` / `Path 2` | ≤ **15 caracteres** cada | Opcional mas recomendado |
| `Final URL` | URL completa com `https://` | — |

**Regras de pinning (Google Ads algorithm):**
- Máximo 2 headlines pinados por posição (1, 2 ou 3)
- Ao menos 3 headlines totalmente sem pin — dá combinações pro algoritmo testar
- Overpinning (pinar demais) reduz Ad Strength e limita testes

---

## Checklist pré-upload

- [ ] 5 arquivos separados, cada um seguindo o template oficial de `references/templates-oficiais/`
- [ ] Encoding: **UTF-8** (acentos em Latin-1 corrompem)
- [ ] Separador: vírgula — campos com vírgula interna devem estar entre aspas duplas
- [ ] Decimal com **ponto** (`67`, `2.50`), nunca vírgula
- [ ] Headlines ≤ 30 chars · Descriptions ≤ 90 chars · Path ≤ 15 chars
- [ ] `EU political ads` preenchido com `Yes` ou `No` — apenas na linha de campanha
- [ ] `Keyword status` vazio nas negativas
- [ ] Upload em ordem: 01 → 02 → 03 → 04 → 05 (nunca simultâneo)

## Como subir

`Google Ads web` (https://ads.google.com) → login na conta → **Tools & Settings (🔧) > Bulk Actions > Uploads** → **+ New Upload** → selecionar arquivo → "Preview" → conferir contagem de alterações (sem erros) → **Apply**.

Repetir para os 5 arquivos.

## Quando gerar via script

Use Python com `csv.DictWriter` e `quoting=csv.QUOTE_MINIMAL` — evita erros de contagem de vírgulas e garante escape de campos com vírgula/aspas internas. Template mínimo:

```python
import csv
from pathlib import Path

HEADERS = [...]  # header exato do template oficial
rows = [...]     # lista de dicts

with Path("01_campaigns.csv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADERS, quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in HEADERS})
```

Ver `references/pitfalls.md` para armadilhas descobertas em produção.
