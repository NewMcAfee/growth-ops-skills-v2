# Variáveis Mustache do Bootstrap

> Reference da skill `vault-architect`. Carregado no Passo de substituição do modo `bootstrap`.

A skill clona `templates/vault-template/` arquivo a arquivo via `Bash` (`cp -r`). Em cada `.md` substitui ocorrências de `{{var}}` pelos valores derivados dos 7 inputs obrigatórios + opcionais. **Substituição manual literal** — não depende do plugin Templater do Obsidian estar carregado.

---

## Tabela canônica de placeholders

| Placeholder | Origem | Exemplo |
|---|---|---|
| `{{cliente_nome}}` | input `cliente_nome` (slug kebab-case) | `belo-restaurante` |
| `{{ticker}}` | input `ticker` (id externo Flow MCP, `[A-Z]{4}`) | `BELO` |
| `{{setor}}` | input `setor` | `food service — alta gastronomia` |
| `{{modelo_negocio}}` | input `modelo_negocio` | `B2C — restaurante de ticket alto, serviço presencial + reservas digitais` |
| `{{ponto_focal}}` | input `ponto_focal` | `Ricardo Martins — sócio fundador` |
| `{{data_inicio}}` | input `data_inicio` (ISO date) | `2026-05-08` |
| `{{sprint_atual}}` | input opcional, default inferido de `data_inicio` | `2026-Q2` |
| `{{drop_atual}}` | input opcional, default inferido de `data_inicio` | `2026-05` |
| `{{nivel_oferta}}` | input opcional `nivel_inicial_pilares.oferta`, default `desconhecido` | `desconhecido` |
| `{{nivel_marketing}}` | idem `.marketing` | `desconhecido` |
| `{{nivel_vendas}}` | idem `.vendas` | `desconhecido` |
| `{{nivel_retencao}}` | idem `.retencao` | `desconhecido` |
| `{{ultima_revisao_diagnostico}}` | placeholder default | `pendente — primeiro Diagnóstico ainda não rodou` |
| `{{ultimo_diagnostico}}` | placeholder default | `pendente` |
| `{{gargalo_oferta}}` | placeholder default | `pendente` |
| `{{gargalo_marketing}}` | placeholder default | `pendente` |
| `{{gargalo_vendas}}` | placeholder default | `pendente` |
| `{{gargalo_retencao}}` | placeholder default | `pendente` |
| `{{status}}` (em `agents.md`) | default `not-configured` | `not-configured` |
| `{{termo_1}}` / `{{termo_2}}` (em `glossario.md`) | placeholder default | `<!-- adicione termo específico do projeto -->` |
| `{{definicao_1}}` / `{{definicao_2}}` (em `glossario.md`) | placeholder default | `<!-- adicione definição -->` |

---

## Defaults inferidos

### `sprint_atual` — derivado de `data_inicio`

Mapeamento ISO date → `YYYY-Q[1-4]`:
- Mês 01-03 → Q1
- Mês 04-06 → Q2
- Mês 07-09 → Q3
- Mês 10-12 → Q4

Exemplo: `data_inicio: 2026-05-08` → `sprint_atual: 2026-Q2`.

### `drop_atual` — derivado de `data_inicio`

Mapeamento ISO date → `YYYY-MM`:

Exemplo: `data_inicio: 2026-05-08` → `drop_atual: 2026-05`.

### `nivel_inicial_pilares` — default `desconhecido`

Cada um dos 4 pilares (oferta/marketing/vendas/retencao) começa como `desconhecido` no bootstrap. O primeiro Diagnóstico de Maturidade (Subfase 1.1.5, skill `maturity-diagnoser`) estabelece baseline.

---

## Placeholders ausentes (input não fornecido)

Quando input opcional não foi fornecido pelo operador, skill substitui por placeholder de pendência:

```markdown
<!-- pendente: descreva aqui {{nome_do_campo}} -->
```

E registra em `pendencias_iniciais` no `.vault-architect.yml`:

```yaml
pendencias_iniciais:
  - resumo_handoff_comercial: ausente — substituir placeholder em claude.md e CHANGELOG.md
  - nivel_inicial_pilares: desconhecido — primeiro Diagnóstico de Maturidade vai populá-los
```

---

## `.vault-architect.yml` (root do vault)

Schema canônico produzido no bootstrap:

```yaml
template_version: 2.0.0
sistema: growth-ia-ops-v2.0
cliente_nome: belo-restaurante              # id interno do vault (slug kebab-case = nome da pasta)
ticker: BELO                                # id EXTERNO do projeto no Flow MCP — não gerado aqui
setor: food service — alta gastronomia
modelo_negocio: B2C — restaurante de ticket alto, serviço presencial + reservas digitais
ponto_focal: Ricardo Martins — sócio fundador
data_inicio: 2026-05-08
sprint_atual: 2026-Q2
drop_atual: 2026-05
mode_origin: bootstrap
created_at: 2026-05-08T18:32:00Z
created_by: vault-architect@2.0.0
rule_overrides: {}                          # operador customiza severidades aqui
disabled_rules: []                          # regras desativadas globalmente nesse vault
pendencias_iniciais: []                     # populado se inputs opcionais ausentes
historico_retrofit: []                      # populado por modo retrofit
```

---

## Validação de substituição

Após clonar e substituir, skill roda audit interno com flag `bootstrap_just_ran: true`:

1. Validar que todos placeholders Mustache foram substituídos. Achados restantes `\{\{[a-z_]+\}\}` viram **warning** (pode haver placeholder Templater legítimo em `_templates/`).
2. Validar que `.vault-architect.yml` parseia YAML válido + tem todos campos obrigatórios — em especial **`ticker` presente e não-vazio** (regra TK001 — error). Se ticker fora da convenção `[A-Z]{4}`, registra warning (TK002).
3. Validar que cada categoria 10-99 tem `_readme.md`.
4. Validar que `80-versoes/v0.0/manifest.md` parseia frontmatter.
5. Validar que `git status` mostra árvore limpa após primeiro commit.

**Resultado esperado:** 0 errors, 0 warnings (exceto pendências declaradas e placeholders Templater em `_templates/`).
