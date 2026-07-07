# Template — Audit Report (modo `otimização`)

> Reference da skill `vault-architect`. Formato canônico do output da Fase 1 do modo `otimização` (read-only).

---

```markdown
# Audit Report — {{cliente_nome}}

> Rodado em {{timestamp}} por `vault-architect@2.0.0`
> Escopo: {{categorias}} (ex: FM, MOC, NM, …)
> Severidade mínima: {{severidade}}
> Path do vault: {{path_vault}}

---

## Sumário

| Métrica | Valor |
|---|---|
| Errors | {{N}} |
| Warnings | {{N}} |
| Info | {{N}} |
| Auto-fixáveis | {{N}} |
| Decisão humana | {{N}} |

> **Status global:** {{status}} (`saudavel` se 0 errors; `atencao` se errors ≤ 5; `critico` se errors > 5)

---

## Decisões humanas necessárias

> Achados que **NÃO** são auto-fixáveis. Operador precisa avaliar caso a caso.

### {{categoria_da_regra}} — {{regra_id}} ({{severidade}})

- **ID do achado:** `{{regra_id}}-{{N}}`
- **Path:** `{{path_relativo}}` (linha {{linha}} se aplicável)
- **Mensagem:** {{mensagem_humana}}
- **Ação sugerida:** {{texto_livre_acionavel}}

[repete pra cada achado de decisão humana, agrupado por categoria]

---

## Auto-fixáveis

> Achados que PODEM ser auto-aplicados se operador comandar `aprovar [ids]` ou `aprovar all`.

### {{categoria_da_regra}} — {{regra_id}} ({{severidade}})

- **ID do achado:** `{{regra_id}}-{{N}}`
- **Path:** `{{path_relativo}}` (linha {{linha}})
- **Mensagem:** {{mensagem_humana}}
- **Diff proposto:**
  ```diff
  - {{conteudo_atual}}
  + {{conteudo_proposto}}
  ```
- **Justificativa:** {{regra} {{detalhe_canonico}}.

[repete pra cada achado auto-fixável, agrupado por categoria]

---

## Loop de feedback (se > 10 achados)

> Skill detectou {{N}} achados — risco de alert fatigue.
>
> Algum desses é falso positivo legítimo no contexto deste projeto? Posso adicionar `disabled-rules` no frontmatter dos arquivos afetados ou `rule_overrides` no `.vault-architect.yml` global.
>
> Sugestões a considerar (regras com mais ocorrências, candidatas a ajuste):
> - {{regra_X}}: {{N}} ocorrências.
> - {{regra_Y}}: {{N}} ocorrências.

---

## Próximo passo recomendado

[Texto livre baseado em quê foi encontrado. Exemplos:]

- Operador comanda `aprovar all` para aplicar os {{N}} auto-fixáveis.
- Operador escolhe IDs específicos: `aprovar FM003-01 FM003-02 AG001-04`.
- Operador desativa regras false-positive: `desativar regra GL001 em escopo: pasta 10-fundacao/`.
- Operador resolve manualmente os {{N}} achados de decisão humana.
- Re-rodar `otimização` com escopo reduzido (`escopo: [FM, AG]`) se quer focar.

---

## Histórico de auditorias

> Últimas 5 auditorias deste vault (extraído de `.vault-architect.yml`):

| Data | Errors | Warnings | Auto-fix aplicados | Operador |
|---|---|---|---|---|
| {{data}} | ... | ... | ... | ... |
```

---

## Schema de cada achado individual

Estrutura interna (não exposta diretamente no report — usada pra computar o output):

```yaml
id: FM003-01           # {regra}-{contador}
regra: FM003
categoria: FM           # primeiras letras
severidade: warning     # info | warning | error
path: 50-operacao/operacional/aquisicao/paga/sprint-2026-Q2/drop-2026-05/lp-belo.md
linha: 7                # opcional, quando aplicável
mensagem: "status 'rodando' fora do enum canônico"
auto_fixavel: true
acao_sugerida: "alterar pra 'active'"
diff_proposto:
  before: "status: rodando"
  after: "status: active"
justificativa: "FM003: status fora do enum (draft/review/approved/active/paused/killed/archived)"
```

---

## Apply (Fase 2) — comportamento

Quando operador comanda `aprovar [ids]` ou `aprovar all`:

1. Para cada ID aprovado:
   - Re-mostra diff.
   - Aplica via `Edit` (preferir Edit sobre Write).
   - Atualiza `updated_at` no frontmatter do arquivo tocado (se aplicável).
2. Re-roda audit interno.
3. Se introduziu nova divergência: **reverte o último apply automaticamente** + mensagem de erro.
4. Se OK:
   - Atualiza `CHANGELOG.md` com entrada estruturada.
   - `git add` dos arquivos tocados (nunca `-A`).
   - Propõe mensagem `chore(otimizacao): aplica {{N}} correções auto-fixáveis`.
   - Aguarda comando explícito do operador (`commit` / `editar mensagem` / `não commitar`).

---

## Achados pra excluir do report

Achados com severidade `< severidade_minima` (default: `warning`) ficam fora do report — só aparecem se operador roda com `severidade_minima: info`. Achados em arquivos com `disabled-rules: [...]` no frontmatter, ou regras com `rule_overrides.{regra}.severity: ignored` no `.vault-architect.yml`, são suprimidos silenciosamente (mas registrados em log de debug se operador pedir `--verbose`).
