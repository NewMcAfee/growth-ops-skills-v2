# Exemplo canônico — Sigo ERP (2026-06-26)

Caso real que validou a skill. Use como referência de "como fica um setup completo". **Não copie os IDs/paths** — são deste projeto; cada feed novo passa pelo Passo 0.

## Parâmetros

| Campo | Valor |
|---|---|
| Planilha | `1zSuWNzxkB6panHHEdZmHMFg9Asm43NVjK-dj4nQ-DNs` (pública "qualquer um com o link") |
| Abas | `ads_ano_atual` (campanhas) · `crm_ano_atual` (CRM) |
| Pasta-destino | `90-referencias/dados-fonte/` |
| Arquivos | `campanhas-ano-corrente.csv` (agregado, commitável) · `crm-ano-corrente.csv` (PII, git-ignored) |
| Tarefa | `Sigo ERP - Dados Fonte` · diária 09:00 |

## feed-config.json resultante

```json
{
  "sheetId": "1zSuWNzxkB6panHHEdZmHMFg9Asm43NVjK-dj4nQ-DNs",
  "minBytes": 500,
  "minLineRatio": 0.5,
  "targets": [
    { "sheet": "ads_ano_atual", "out": "campanhas-ano-corrente.csv", "mustContain": "Canal", "pii": false },
    { "sheet": "crm_ano_atual", "out": "crm-ano-corrente.csv", "mustContain": "deal_growthpack_id", "pii": true }
  ]
}
```

## Linhas adicionadas ao .gitignore

```
90-referencias/dados-fonte/crm-ano-corrente.csv
90-referencias/dados-fonte/_download.log
```

## Achados de QA que viraram regra R7

A planilha tinha 13 colunas no CRM formatadas como **Porcentagem**, corrompendo o dado no export:
- `phone` → `551790000000000,00%` (devia ser `5517900000000` — nº mascarado aqui) → corrigir p/ **Texto simples**
- 11 timestamps (`mql_at`, `lost_at`, …) → `4618384,72%` → corrigir p/ **Data e hora**
- `ga4_client_id` → ao virar Número, caiu em notação científica `9,37284E+18` → corrigir p/ **Texto simples**

Lição: a correção é **na planilha-fonte** (formato da célula), não no CSV — qualquer fix no CSV é sobrescrito no próximo run. A skill reporta e o operador corrige a origem.

## Resultado

Carga inicial + teste real da tarefa (disparada pelo agendador) com `LastTaskResult: 0`. Campanhas 4.323 linhas (granularidade dia×anúncio) · CRM 35.407 linhas. PII confirmada fora do Git via `git check-ignore`.
