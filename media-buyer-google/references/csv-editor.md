# CSV Google Ads — Editor Desktop (Dialeto A)

> **DOIS dialetos de CSV, NÃO intercambiáveis.** O destino da importação define o formato:
> - **Editor Desktop** (app, *Account > Import > From file*) → **este arquivo (Dialeto A)** → **1 CSV combinado**.
> - **Web Bulk Upload** (web, *Tools > Bulk Actions > Uploads*) → `csv-search.md` (Dialeto B) → **5 CSVs separados**.
>
> Gerar Dialeto B com destino Editor (ou vice-versa) **quebra o import** — foi o que aconteceu na Martins (2026-06-18): negativas davam *"Tipo de linha ambíguo"* e `Phrase match` dava *"tipo de correspondência inválido"*. **Pergunte qual UI ANTES de gerar** (Passo 1 do SKILL.md).

## Estrutura: 1 CSV combinado, tipo inferido pelas colunas

O Editor **não** usa `Row Type` / `Action` / `Level`. Ele infere o tipo de cada linha pelas **colunas preenchidas**:
- linha com `Keyword` + `Type` em (`phrase`/`exact`/`broad`) → **keyword positiva**;
- linha com `Keyword` + `Type=Campaign negative` + `Ad group` vazio → **negativa de campanha**;
- linha com `Headline 1..n` preenchidos → **RSA** (sem coluna `Ad type` — é inferido);
- config de campanha (type/budget/networks/language/bid/status) repetida nas linhas daquela campanha — o Editor consolida.

Header em inglês; capitalização/espaços do header não importam (o Editor faz column-mapping no import e mostra preview).

## Valores críticos (Dialeto A — case e grafia)

| Campo | Valor Editor | ❌ NÃO usar (isso é Web Bulk) |
|---|---|---|
| Match type (col `Type`) | `phrase` / `exact` / `broad` — **sem "match"** | ❌ `Phrase match` (Editor rejeita) |
| Negativa | col **`Keyword`** com símbolo no texto + `Type=Campaign negative` + `Ad group` vazio | ❌ col `Negative keyword` + `Level` (dá "linha ambígua") |
| `Campaign type` | `Search` | ❌ `Search Network` |
| `Language` | `pt` | ❌ `Portuguese (Brazil)` |
| `Networks` | `Google Search;Search Partners` (`;` separa) | — |
| Budget | `Campaign daily budget` (nº) — **não existe `Budget type`** | — |
| Bid strategy | sentence case: `Maximize clicks` / `Maximize conversions` / `Target CPA` / `Target ROAS` / `Manual CPC` | — |
| Status | `Campaign status` / `Ad group status` / `Status` (ad) = `Enabled`/`Paused` | — |
| `Ad rotation` | `Optimize` (opcional) | — |

**Negativas — símbolo de match vai no TEXTO** (porque `Campaign negative` não carrega match type):
`"split"` = phrase · `[split]` = exact · `split` = broad.

**Não existem no Dialeto A:** `Row Type`, `Action`, `Level`, `Negative keyword`, `Ad type`, `Budget type`, `EU political ads` (este último é só Web Bulk).

## ⚠️ Encoding — UTF-8 SEM BOM quebra acento no Editor (Martins 2026-06-18)

O Editor no Windows pt-BR, ao ler CSV **sem BOM**, assume a code page do sistema (**cp1252**) e lê os bytes UTF-8 como cp1252 → **mojibake** (`ç`→`Ã§`, `ã`→`Ã£`). Pior: cada acento vira 2 chars → **infla o char count** → dispara **falso "título > 30 caracteres"** (o validador Python conta certo ≤30; o Editor conta o lixo). Dois sintomas, uma causa.

- **Fix obrigatório:** salvar em **UTF-8 COM BOM** → Python `encoding="utf-8-sig"`. Mantém vírgula/.csv.
- **Risco residual:** BOM colado no 1º header (`﻿Campaign`) em versões antigas → conferir no Preview se "Campaign" casou.
- **Fallback à prova de erro** (Google doc answer/56368): **UTF-16 LE com BOM, TAB-delimited, .txt** ("Unicode Text" do Excel) — sem risco de header.
- **NUNCA** UTF-8 sem BOM; evitar cp1252 (frágil em emoji/aspas curvas).

## Header de referência (1 CSV combinado)

```
Campaign,Campaign type,Campaign daily budget,Networks,Language,Locations,Bid strategy,Campaign status,Ad group,Ad group status,Keyword,Type,Headline 1..Headline 15,Description 1..Description 4,Path 1,Path 2,Final URL,Final URL suffix,Status
```

## Gerador Python (base — adaptar aos dados do projeto)

```python
import csv
from pathlib import Path

def ed_match(t):  # Web Bulk -> Editor
    return {"Phrase match":"phrase","Exact match":"exact","Broad match":"broad"}.get(t,"broad")
def ed_neg_text(kw,t):  # negativa: símbolo de match no texto
    return f'"{kw}"' if t=="Phrase match" else (f"[{kw}]" if t=="Exact match" else kw)

ED_H = (["Campaign","Campaign type","Campaign daily budget","Networks","Language","Locations",
         "Bid strategy","Campaign status","Ad group","Ad group status","Keyword","Type"]
        + [f"Headline {i}" for i in range(1,16)] + [f"Description {i}" for i in range(1,5)]
        + ["Path 1","Path 2","Final URL","Final URL suffix","Status"])

# validar char limits ANTES (≤30/≤90/≤15) — é o que mais quebra
def chk(text, limit, ctx, errs):
    if len(text) > limit: errs.append(f"[{len(text)}>{limit}] {ctx}: {text}")
    return text

# ... montar rows (campcfg em cada linha; keyword positiva: Type=phrase/exact;
#     negativa: Ad group vazio + Keyword=ed_neg_text + Type='Campaign negative';
#     RSA: Headlines/Descriptions) ...

# UTF-8 COM BOM:
with Path("editor_import.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=ED_H, quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in ED_H})
```

## Como subir (Editor Desktop)

**Editor** → conta → **Account > Import > From file...** → selecionar o CSV → column-mapping (conferir) → **preview com erros destacados** → corrigir o que apontar → **Keep / Post**. O preview é mais perdoador que o Web Bulk (que rejeita o arquivo inteiro). Campanhas sobem `Paused`.

## Fontes oficiais (Editor)
support.google.com/google-ads/editor/answer/57747 (colunas) · answer/47635 (match types) · answer/94241 (bid strategy) · answer/56368 (preparar CSV / encoding). Em ambos os dialetos: decimal com ponto; char limits ≤30/≤90/≤15 validados em Python antes de escrever.
