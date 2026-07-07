# Convenção de Slots Customizáveis

> Reference da skill `vault-architect`. Carregado em modo `retrofit` quando precisa preservar customização do operador.

Convenção HTML pra delimitar **invariantes** (skill substitui em retrofit) vs. **slots customizáveis** (skill preserva integralmente em retrofit).

---

## Sintaxe

```markdown
<!-- vault-architect:slot:NOME -->
[conteúdo customizável aqui — preservado em retrofit]
<!-- /vault-architect:slot:NOME -->
```

`NOME` é identificador do slot (kebab-case). Skill localiza par open/close por nome literal.

---

## Comportamento em `retrofit`

1. Lê o conteúdo entre `<!-- vault-architect:slot:NOME -->` e `<!-- /vault-architect:slot:NOME -->`.
2. Reconstrói o arquivo a partir do template canônico (versão nova).
3. **Reinjeta** o conteúdo do slot na posição equivalente do novo arquivo.
4. Se o template canônico **removeu** um slot que tinha conteúdo:
   - Skill alerta o operador.
   - Move conteúdo pra `99-arquivo/slots-removidos-{{data}}.md`.
   - Pede aprovação (`sim` / `cancelar`).

**Bootstrap inicial** já cria os arquivos com delimitadores prontos (ver §[Slots por meta-doc](#slots-por-meta-doc) abaixo). Operador edita o conteúdo dentro deles em runtime.

---

## Slots por meta-doc (mapa canônico)

### `claude.md` (root)

| Seção | Tipo | Slot ID |
|---|---|---|
| Título `# Vault Growth IA Ops — {{cliente_nome}}` | invariante | — |
| `## Contexto do projeto` | slot | `contexto-projeto` |
| `## Saúde dos pilares (Pillars-Health vigente)` | slot dinâmico (atualizado por outras skills) | `pillars-health` |
| `## Estrutura do vault (categorias de output)` | invariante | — |
| `## Mapa de Outputs (path canônico × output)` | invariante | — |
| `## Mapa de Inputs por Skill` | invariante por skill, slot por status | — (status interno fica preservado) |
| `## Convenção de tags canônica` | invariante | — |
| `## Princípios fundamentais (resumo)` | invariante | — |
| `## O que NÃO fazer aqui` | invariante | — |
| `## Como peço ajuda do Claude` | slot | `como-peco-ajuda` |

### `agents.md`

| Seção | Tipo | Slot ID |
|---|---|---|
| Título + bloco introdutório | invariante | — |
| `## Skills da Fase 0 — Setup` | invariante por skill, slot por status | (slots por skill diferidos pra B7) |
| `## Skills da Fase 1 — Fundação` | idem | idem |
| `## Skills das Camadas de Suporte (Fase 2)` | idem | idem |
| `## Skills dos Workflows Operacionais (Fase 2)` | idem | idem |
| `## Convenção de status no projeto` | invariante | — |

### `index.md`

| Seção | Tipo | Slot ID |
|---|---|---|
| Título + `## Versão atual do sistema` | invariante | — |
| `## Outputs por categoria` (queries Dataview) | invariante | — |
| `## Visões transversais (por tag)` | invariante | — |
| `## Sprint e Drop atuais` | slot dinâmico | `sprint-drop-atuais` |
| `## Saúde dos pilares (Pillars-Health)` | slot dinâmico | `pillars-health` |
| `## Atalhos por intenção` | invariante (default), pode virar slot se operador customizar | — |

### `glossario.md`

| Seção | Tipo | Slot ID |
|---|---|---|
| `## Termos técnicos do sistema (compartilhados com a tese)` | invariante | — |
| `## Termos específicos do projeto {{cliente_nome}}` | slot | `termos-projeto` |

### `README.md` e `CHANGELOG.md`

Inteiramente invariantes. Se operador precisar customizar, marca seção com `<!-- custom -->...<!-- /custom -->` (sintaxe genérica). Skill respeita esses blocos sem nome canônico.

---

## Política de preservação

A skill **NUNCA**:

- Sobrescreve conteúdo dentro de slots em retrofit.
- Renomeia slot existente sem alertar.
- Cria slot novo sem incluir nas docs canônicas (template + esta reference).
- Remove slot do template sem migrar conteúdo pra `99-arquivo/slots-removidos-{{data}}.md`.

A skill **PODE**:

- Adicionar invariante novo entre slots existentes.
- Atualizar conteúdo invariante (fora dos slots).
- Mover ordem das seções desde que slots permaneçam intactos.
- Criar slot novo no template (próxima major version) — operador faz retrofit pra adquirir.

---

## Status atual (2026-05-08)

Slots ativos no `templates/vault-template/`:

- ✅ `claude.md`: `contexto-projeto`, `pillars-health`, `como-peco-ajuda`
- ✅ `index.md`: `sprint-drop-atuais`, `pillars-health`
- ✅ `glossario.md`: `termos-projeto`

Slots **diferidos pra B7** (modo bootstrap não depende; modo retrofit pode operar com fallback):

- `agents.md`: slots por skill (1 por skill listada — preserva `Status no projeto: {{status}}` durante retrofit). Aprox. 20+ slots a adicionar quando catálogo canônico de skills for fechado em B7.
- `CHANGELOG.md`: sem slots planejados (invariante completo + linhas adicionadas pelo operador são preservadas implicitamente).
- `README.md`: sem slots planejados (invariante completo).
