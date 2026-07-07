# Armadilhas do CSV Google Ads — Descobertas em Produção

> Lista viva de erros reais que o import do Google Ads Web Bulk Upload rejeita, mesmo quando os templates oficiais parecem dizer que tudo está certo. **Sempre ler isso antes de gerar CSV.**

## Formato: DOIS dialetos válidos, NÃO intercambiáveis

O Google Ads tem dois formatos de CSV — ambos atuais, **dialetos diferentes** (não "antigo vs novo"). O **destino** decide qual usar:

1. **Google Ads Editor (app desktop)** — `Account > Import > From file`. **1 CSV combinado** (Editor infere o tipo da linha pelas colunas). Dialeto completo em `csv-editor.md` (**Dialeto A**).
2. **Web Bulk Upload (web)** — `Tools > Bulk Actions > Uploads`. **5 CSVs separados** com `Row Type`/`Action`. Detalhe em `csv-search.md` (**Dialeto B**) — ancorado nos templates oficiais.

**Pergunte qual UI ANTES de gerar (Passo 1).** Gerar o dialeto errado pro destino quebra o import — foi o que aconteceu na Martins (2026-06-18): negativas Dialeto B no Editor davam *"Tipo de linha ambíguo"* e `Phrase match` dava *"tipo de correspondência inválido"*. As diferenças de valor estão nos itens 2–4 abaixo; o Editor **não** é incompleto, é outro dialeto.

## Armadilhas de valor (templates oficiais são ambíguos ou incompletos)

### 1. `Networks` não aceita `Search`

- **Template diz:** valores suportados incluem `Google search`, `Search partners`, etc.
- **Erro real:** `"O valor 'Search' na coluna 'Networks' é inválido"` — `Search` é aceito em `Campaign type` mas NÃO em `Networks`.
- **Correto:** `Google search` (duas palavras, não confundir com `Campaign type: Search`).

### 2. `Campaign type` = `Search` em AMBOS os dialetos

- **Erro real (Web Bulk):** `"O valor 'Search Network' na coluna 'Campaign type' é inválido"`.
- **Correto:** `Search` (sem `Network`) — vale para Web Bulk **e** Editor. `Search Network` é legado genérico, NÃO "o valor do Editor" (esse engano vazou e quebrou a Martins).

### 3. `Type` de keyword — a palavra `match` DEPENDE do dialeto

- **Web Bulk (Dialeto B):** `Phrase match` / `Exact match` / `Broad match` — **com** "match".
- **Editor (Dialeto A):** `phrase` / `exact` / `broad` — **sem** "match" (o Editor rejeita `Phrase match`: *"tipo de correspondência inválido"*). Ver `csv-editor.md`.

### 4. `Language` = `pt` em AMBOS os dialetos

- **Correto:** `pt` (ISO 639-1) — Web Bulk **e** Editor. `Portuguese (Brazil)` é legado, NÃO "o valor do Editor" (mesma inversão do item 2).

### 5. `EU political ads` é obrigatório e só vai na campanha

- **Contexto:** Google tornou obrigatório declarar em 2026-04-01 (enforcement desde então).
- **Onde aparece:** apenas na coluna `EU political ads` da linha de **Campaign**, não nos outros 4 arquivos.
- **Valores:** `Yes` ou `No`. Para projetos não-políticos no BR, sempre `No`.

### 6. `Keyword status` NÃO aceita `Enabled` em negativas

- **Template diz:** `Optional. Supported values: Enabled; Removed; Paused` (listado no `ad_group_negative_keyword_template.csv`).
- **Erro real:** `"O valor 'Enabled' na coluna 'Keyword status' é inválido"` — o Google rejeita `Enabled` pra Negative keyword apesar de listar como válido no template.
- **Correto:** **DEIXAR VAZIO**. O campo é Optional.

### 7. `Default max. CPC` com decimal em Smart Bidding

- **Erro real:** `"Na coluna 'Max CPC', não foi possível analisar o valor '2.50'"` quando Editor está em locale PT-BR.
- **Contexto:** quando `Bid strategy type` da campanha é `Maximize clicks` / `Target CPA` / `Maximize Conversions` / etc. (qualquer Smart Bidding), os lances são governados pela campanha — não precisa definir nos grupos.
- **Correto:** deixar `Default max. CPC` VAZIO nos grupos. Se precisar cap de CPC, usar `Max CPC Bid Limit for Target IS` no nível de campanha ou ajuste manual pós-upload em Settings > Bidding.

## Armadilhas estruturais

### 8. Order of upload

Cada arquivo depende do anterior. Subir fora de ordem causa "Nenhuma entidade corresponde à Campanha/Grupo". Ordem: 1 Campaigns → 2 Ad groups → 3 Keywords → 4 Negative keywords → 5 Ads.

### 9. Unificar os 5 em 1 CSV não é suportado no Web Bulk Upload

O Editor Desktop aceita CSV flat misturando row types. O **Web Bulk Upload requer 5 uploads separados** (mesmo que cada arquivo tenha uma única linha).

### 10. `Row Type` + `Action` em TODA linha

Mesmo linhas de "keyword filha" e "ad filho" precisam de `Row Type` e `Action` preenchidos. Herança de linha pai não funciona no Web Bulk Upload.

### 11. Negative keyword exige `Level`

Coluna `Level` é obrigatória em `04_negative_keywords.csv`: `Campaign` (nível campanha) ou `Ad group` (nível grupo). Se `Level = Campaign`, deixar `Ad group` vazio.

### 12. Overpinning em RSA

Google penaliza Ad Strength quando há mais de 2 headlines pinados na mesma posição. Regra prática: pinar no máximo 3 headlines (um em cada posição 1/2/3) e manter ao menos 3 totalmente sem pin pra o algoritmo testar.

## Armadilhas de geração (Python)

### 13. Manipular vírgulas manualmente é propenso a erro

Cada arquivo tem 18–57 colunas. Contar vírgulas na mão é inviável. **Sempre usar `csv.DictWriter` com `quoting=csv.QUOTE_MINIMAL`** — garante escape correto de campos com vírgula/aspas internas e preserva a estrutura do header.

### 14. Encoding depende do dialeto — Editor exige BOM

- **Web Bulk (Dialeto B):** `encoding="utf-8"` (sem BOM). Latin-1 corrompe acentos.
- **Editor (Dialeto A):** `encoding="utf-8-sig"` (**UTF-8 COM BOM**) — OBRIGATÓRIO. O Editor no Windows pt-BR lê CSV sem BOM como cp1252 → mojibake (`ç`→`Ã§`) + cada acento vira 2 chars → **falso "título > 30"** (o validador Python conta certo; o Editor conta o lixo). Dois sintomas, uma causa. Fallback à prova de erro: UTF-16 LE + BOM, TAB-delimited, .txt. Detalhe em `csv-editor.md`.

### 15. Validar char counts antes de escrever

Headlines > 30, Descriptions > 90 ou Paths > 15 causam erro de validação no upload — melhor capturar antes. Inserir função `validate_lengths()` no script.

---

## Como atualizar este arquivo

Quando um novo erro aparecer em import real, adicionar aqui com:
- **Mensagem exata do erro** (em PT-BR, que é o que o operador vê)
- **Contexto:** qual coluna, qual tipo de entidade
- **Causa raíz:** por que o template oficial não cobria
- **Correção:** valor/ajuste correto

Ver também: `csv-search.md` (referência geral) e `templates-oficiais/` (os 6 templates baixados do Google).
