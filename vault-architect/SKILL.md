---
name: vault-architect
version: "2.2.0"
description: Faz bootstrap, retrofit e otimização contínua de vaults Growth IA Ops v2.0 (estrutura de 9 categorias por tipo de output incluindo `00-sistema/` da identidade do operador via D-OPERADOR-1 + meta-docs estruturais com slots customizáveis + manifesto versionado em 80-versoes/ + **doutrina sináptica v2.2.0** — `mapa.md` por pasta mesmo vazia + TOC navegável + Resumo 60s em MDs ≥100 linhas/Cat 1/2/3/4/8 + helper `atualiza-cascata` exportável pra outras skills + sub-modo `audit-mapa`). Padrão único — Dante v1 está deprecado. Ative quando o operador disser "cria estrutura do vault X", "inicializa vault", "bootstrap vault", "atualiza vault depois que [categoria/skill/schema] mudou", "audita o vault", "otimiza o vault", "valida o vault", "vault-architect", "checa health do vault", "re-sincroniza identidade do operador no vault", "re-sync 00-sistema", "atualiza mapa da pasta X", "regenera TOC do MD Y", "roda cascata sináptica", "audit-mapa". NÃO ative para criar conteúdo de marketing (use skills específicas como oraculo, michelangelo, cesar, escriba, sobral, etc.); mexer em manifesto vivo de 80-versoes/ pós-v0.0 (use system-manifest-builder); editar _atual.md em 60-loops/ (use skill de loop trimestral); processar transcrições em 70-memoria/ (use account-curator); materializar a biblioteca shared do operador (use operador-onboarding); vaults Dante v1 (suporte deprecado — recusar e apontar playbook de migração); vaults que não seguem o padrão Growth IA Ops v2.0 (recusar e apontar templates/vault-template/); escrever o conteúdo de um Resumo 60s real de um output (skill só insere stub — quem produziu o output escreve resumo via curadoria humana).
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite
---

# vault-architect — Camada de Estado (Growth IA Ops v2.0)

Skill **única autorizada a mutar estrutura canônica de vault** Growth IA Ops v2.0. Constrói/mantém a Camada de Estado (Princípio 8) de vaults de cliente. Padrão de Workflow Anthropic: **Routing** (state-based + intent-confirmation).

**Padrão único:** Growth IA Ops v2.0. Dante v1 está deprecado — skill recusa explicitamente vaults nesse formato (ver [`references/migration-from-dante-v1.md`](references/migration-from-dante-v1.md)).

**Posição arquitetural:** skills de domínio (`oraculo`, `michelangelo`, `cesar`, etc.) escrevem em paths canônicos do vault, mas **nunca** mexem nas pastas-categoria, nos meta-docs estruturais (`claude.md`/`agents.md`/`index.md`/`glossario.md`/`README.md`/`CHANGELOG.md`) nem no esquema `80-versoes/`. Tudo isso é escopo exclusivo desta skill.

---

## Modos de operação

Skill opera em **3 modos canônicos**. Cada modo tem pré-condição verificável distinta + side-effect declarado.

| Modo | Pré-condição (state-based) | Side-effect | Aprovação humana |
|---|---|---|---|
| `bootstrap` | Pasta-alvo inexistente OU vazia OU contém apenas `.git/`/`.obsidian/` (sem `.md` substantivo) | Cria estrutura completa de `templates/vault-template/` + meta-docs com Mustache substituído + manifesto v0.0 placeholder + **9ª categoria `00-sistema/` populada via cópia da biblioteca shared do operador (D-OPERADOR-1) quando `--operador-library-path` provido** + `git init` + commit inicial | Confirma inputs antes de criar |
| `retrofit` | Vault Growth IA Ops v2.0 detectado (tem `claude.md` mencionando "Growth IA Ops v2.0") + delta estrutural pendente declarado | Aplica delta nos meta-docs preservando slots customizáveis + atualiza `CHANGELOG.md` + `git add` (stage) + propõe mensagem de commit. **Sub-modo `re-sync-operador` reconcilia `00-sistema/` com biblioteca shared atualizada preservando overrides locais (D-OPERADOR-1).** | Aprovação explícita do diff antes de `git commit` |
| `otimização` | Vault Growth IA Ops v2.0 detectado, sem delta estrutural declarado | Audit read-only contra catálogo de regras (Fase 1). Sob aprovação, aplica correções auto-fixáveis individualmente (Fase 2) + stage + propõe commit | Aprovação por ID de achado (ou `aprovar all`) |

Detalhes operacionais por modo:
- Modo `bootstrap` — corpo abaixo + [`references/bootstrap-mustache-vars.md`](references/bootstrap-mustache-vars.md) + [`references/operador-library-sync.md`](references/operador-library-sync.md) (D-OPERADOR-1)
- Modo `retrofit` — corpo abaixo + [`references/slot-delimiters.md`](references/slot-delimiters.md) + [`references/operador-library-sync.md`](references/operador-library-sync.md) (sub-modo `re-sync-operador`)
- Modo `otimização` — corpo abaixo + [`references/rules-catalog.md`](references/rules-catalog.md) + [`references/audit-report-template.md`](references/audit-report-template.md) + sub-modo `audit-mapa` em [`references/audit-mapa-mode.md`](references/audit-mapa-mode.md) (v2.2.0)

---

## Doutrina Sináptica (v2.2.0)

Vault Growth IA Ops v2.0 funciona como **rede sináptica** — cada pasta é um nó com `mapa.md` que indexa conteúdo local, e cada arquivo MD substantivo tem TOC + Resumo 60s no topo. Princípio: agente paga 50-200 tokens de mapa em vez de 2k-10k de pasta inteira carregada às cegas; humano lê 60s e decide se precisa do full.

### 3 elementos sinápticos canônicos

1. **`mapa.md` por pasta** (obrigatório em TODAS, mesmo vazias) — frontmatter `tipo: mapa-pasta` + 7 seções (Resumo 60s da pasta · O que entra · O que NÃO entra · Subpastas · Arquivos · Pasta-pai · Última cascata). Spec completo em [`references/mapa-md-spec.md`](references/mapa-md-spec.md).

2. **TOC navegável + Resumo 60s em MDs elegíveis** — obrigatório em Cat 1 (Estado Evergreen) + Cat 2 (Snapshot) + Cat 3 (Decisão) + Cat 4 (Comunicação cerimonial) + Cat 8 (Manifest) **OU** qualquer MD com ≥100 linhas. Dispensado em meta-docs (`mapa.md`, `_readme.md`, `_index.md`), templates (`_templates/*.md`), placeholders (`_evento.md`, `_atual.md`), e configs YAML-only. Spec completo em [`references/toc-resumo-spec.md`](references/toc-resumo-spec.md).

3. **Helper `atualiza-cascata`** (exportável pra outras skills consumirem) — propaga mutação on-edit em 4 níveis: arquivo próprio (TOC + Resumo 60s) → `mapa.md` da pasta-pai (listagem) → walk-up até a raiz (se hierarquia mudou) → meta-docs raiz (`claude.md`/`agents.md`/`index.md` se output canônico ou skill citada). Interface pública completa em [`references/cascade-helper.md`](references/cascade-helper.md).

### Integração com modos canônicos

- **`bootstrap`**: cria `mapa.md` em TODAS as pastas que cria (incluindo subpastas do `templates/vault-template/`). TOC + Resumo 60s NÃO se aplicam no bootstrap (não há outputs ainda — só estrutura).
- **`retrofit`**: tipo novo de delta `doutrina-sinaptica-v2.2.0` aplica retrofit em vault v2.1.x (cria mapas faltantes + insere stubs de TOC/Resumo 60s em MDs elegíveis). Equivalente a rodar `audit-mapa --fix` na primeira passada.
- **`otimização`**: sub-modo `audit-mapa` (escopo restrito aos prefixos MP/TC/RS) detecta drift; spec completo em [`references/audit-mapa-mode.md`](references/audit-mapa-mode.md).

### Atalhos semânticos

```
vault-architect atualiza-cascata <path>     # helper de cascata (escopo limitado a 1 arquivo)
vault-architect audit-mapa                  # = otimização --escopo=MP,TC,RS (read-only)
vault-architect audit-mapa --fix            # = otimização --escopo=MP,TC,RS --aplicar_auto_fix=true
vault-architect regenera-toc <path>         # helper standalone — regenera TOC de 1 MD elegível
```

### Cadência recomendada

| Cenário | Comando |
|---|---|
| Skill downstream gravou output | `vault-architect atualiza-cascata <path>` (skill chama; ou operador no fim) |
| Início do Loop trimestral | `vault-architect audit-mapa --fix` (normaliza drift acumulado) |
| Pré-cerimônia (Apresentação/QBR/Sprint Review) | `vault-architect audit-mapa --fix` (material cliente-facing limpo) |
| Pós-batch grande de criação manual | `vault-architect audit-mapa --fix` |
| Primeira execução em vault pré-v2.2.0 | `vault-architect retrofit --delta=doutrina-sinaptica-v2.2.0` |

---

## Routing state-based — pré-vôo (sempre)

Antes de qualquer operação, executar nesta ordem:

1. **Pasta-alvo existe e tem `.md` substantivo?**
   - Não (inexistente, vazia, ou só `.git/`/`.obsidian/`) → único modo possível: `bootstrap`.
   - Sim → segue para 2.
2. **Pasta tem `claude.md` na raiz mencionando "Growth IA Ops v2.0"?**
   - Sim → vault Growth IA Ops v2.0 detectado. Segue para 3.
   - Não → checa Dante v1 (presença de `AGENTS.md` + 9 pastas `00_*..08_*`):
     - Sim Dante v1 → **recusar** com mensagem da [`references/migration-from-dante-v1.md`](references/migration-from-dante-v1.md), exceto se operador referenciou playbook de migração na invocação (fluxo de migração-guiada).
     - Não Dante v1 nem Growth IA Ops v2.0 → **recusar**: "vault não segue padrão Growth IA Ops v2.0 de 8 categorias; consulte `templates/vault-template/`".
3. **Operador declarou delta estrutural na invocação?**
   - Sim ("atualiza vault depois que adicionei X" / "aplica novo schema" / "adiciona Categoria Y") → `retrofit`.
   - Não ("audita o vault" / "otimiza" / "tem inconsistência?") → `otimização`.

A diferenciação `retrofit` × `otimização` é **operador-declarada**, não state-based. O estado isolado não distingue "delta esperado" de "divergência indesejada".

### Pré-vôo comum aos 3 modos

1. Verificar versão do template canônico em `templates/vault-template/.template-version`.
2. Carregar catálogo de regras de [`references/rules-catalog.md`](references/rules-catalog.md).
3. Carregar overrides do `.vault-architect.yml` no root do vault (em `retrofit` e `otimização`).
4. Validar permissões de escrita na pasta-alvo (em `bootstrap` e `retrofit`).
5. Iniciar `TodoWrite` com plano de operação visível ao operador.

---

## Modo `bootstrap` — síntese

### Inputs obrigatórios (skill recusa sem)

| Campo | Tipo | Origem | Exemplo |
|---|---|---|---|
| `path_destino` | string (path absoluto) | operador | `c:\Users\mcafe\OneDrive\Documentos\Claude\Projects\01_assessoria\Belô` |
| `cliente_nome` | string (slug kebab-case) | handoff comercial / operador | `belo-restaurante` |
| `ticker` | string `[A-Z]{4}` (id externo do Flow MCP) | operador no prompt | `BELO` |
| `setor` | string | handoff comercial | `food service — alta gastronomia` |
| `modelo_negocio` | string | handoff comercial | `B2C — restaurante de ticket alto` |
| `ponto_focal` | string | handoff comercial | `Ricardo Martins — sócio fundador` |
| `data_inicio` | ISO date `YYYY-MM-DD` | hoje | `2026-05-08` |

**Sem `ticker`, integrações com Flow MCP quebram.** Por isso é input obrigatório — não gerável pela skill (id externo do projeto no Flow, criado antes do bootstrap).

Inputs opcionais (skill prossegue, registra como pendência): `resumo_handoff_comercial`, `nivel_inicial_pilares`, `sprint_atual`, `drop_atual`. Defaults em [`references/bootstrap-mustache-vars.md`](references/bootstrap-mustache-vars.md).

### Input D-OPERADOR-1 — `--operador-library-path`

| Campo | Tipo | Default | Comportamento |
|---|---|---|---|
| `--operador-library-path` | string (path absoluto) ou `null` | `~/.claude/growth-ia-ops/operador/` | Skill copia conteúdo desse path pra `<vault>/00-sistema/` (Categoria 9ª — identidade do operador). Detalhe completo em [`references/operador-library-sync.md`](references/operador-library-sync.md). |

**Comportamento por estado:**
- **Path provido + existe + populado** (default): copia conteúdo da biblioteca shared → `<vault>/00-sistema/` como **snapshot temporal** (preserva versão da biblioteca shared no momento do bootstrap mesmo se ela evoluir depois).
- **Path provido + path inexistente**: emite warning + popula `<vault>/00-sistema/` com placeholders + lista lacuna em `pendencias_iniciais` do `.vault-architect.yml` (não bloqueia bootstrap; modo degradado documentado).
- **`null` explícito**: pula `00-sistema/` (modo degradado intencional). Skills cerimoniais downstream (`*-deck-builder`) operam sem identidade do operador (asset placeholder); `deck-renderer` usa identidade Colli&Co própria, independente do `00-sistema/`.

**Princípio 11 (Multi-tenant explícito):** identidade do **operador** (cross-projeto) ≠ identidade do **cliente final** (per-projeto via `10-fundacao/`). `00-sistema/` ≠ `10-fundacao/` por design.

### Outputs (35+ arquivos + cópia da biblioteca shared do operador)

Estrutura completa em `[path_destino]/[cliente_nome]/` clonada de `templates/vault-template/` com substituição Mustache. Lista canônica:

- `.gitignore`, `.gitattributes`, `.obsidian/` (placeholder vazio), `.vault-architect.yml`, `.template-version`
- 6 meta-docs raiz: `README.md`, `claude.md`, `agents.md`, `index.md`, `glossario.md`, `CHANGELOG.md`
- **9 categorias top-level** cada uma com `_readme.md`:
  - `00-sistema/` — **NOVA D-OPERADOR-1** — Identidade do **operador** (cross-projeto). Cópia snapshot da biblioteca shared `~/.claude/growth-ia-ops/operador/` provida via `--operador-library-path`. Consome 5 arquivos canônicos no raiz (`identidade.md` + `design-system.{md,css}` + `tese-growth-ia-ops-resumida.md` + `assinatura.html`) + `assets/` + `integrations/` + `design-system-references/` + snippets canônicos. Distinto de `10-fundacao/` (identidade do CLIENTE FINAL — Princípio 11)
  - `10-fundacao/` (semeado com `contexto.md` stub — **doc de estado vivo**, 10 seções fixas do `socrates/references/contexto-template.md`; substitui o antigo `briefing-inicial.md`, mantido como fallback legado), `20-snapshots/`, `30-decisoes/`, `40-comunicacoes/`, `50-operacao/operacional/_index.md`, `60-loops/_atual.md`, `70-memoria/`, `80-versoes/_atual.md` + `80-versoes/v0.0/manifest.md`, `90-referencias/`, `99-arquivo/`
- 7 templates em `_templates/`: decision-doc-template, drop-template, evento-memoria-template, loop-template, manifest-template, output-operacional-template, sprint-template
- Repo Git inicializado: `git init` + commit `bootstrap: vault inicializado`

### Cópia da biblioteca shared do operador → `00-sistema/` (D-OPERADOR-1)

Após criar estrutura base do vault, antes da Validação:

1. Verificar `--operador-library-path`:
   - Se `null` explícito: pula este bloco. Cria `00-sistema/_readme.md` com placeholder explicando como popular depois (`operador-onboarding inicial` + `vault-architect retrofit re-sync-operador`).
   - Se path provido: continua.
2. Verificar path existe + tem `identidade.md` populado (V1 da biblioteca shared):
   - Se não: emite warning + popula `00-sistema/` com placeholders idênticos ao `null` + adiciona pendência `00-sistema/ não-populada — identidade do operador ausente em <path>`. Não bloqueia bootstrap.
   - Se sim: continua.
3. Copiar conteúdo recursivo de `<operador-library-path>/*` → `<vault>/00-sistema/` (path canônico 1:1):
   - 5 arquivos raiz: `identidade.md`, `design-system.md`, `design-system.css`, `tese-growth-ia-ops-resumida.md`, `assinatura.html`
   - `assets/` (logos + fontes + ícones brand)
   - `integrations/` (5 yml + README)
   - `design-system-references/_catalogo.md`
   - `n8n-snippets/`, `gtm-snippets/`, `scripts-growthpack/` (snippets transversais cross-projeto)
   - 8 placeholders `_pendente.md` (Etapa 3 manual offline)
4. Adicionar marcador `<!-- copied-from-operator-library: <path> @ YYYY-MM-DD -->` no primeiro byte de cada `.md` copiado pra rastrear origem snapshot. Operador customiza arquivo trocando esse marcador por `<!-- override-local: true -->` (preserva customização em `re-sync-operador` futuro).
5. Criar `<vault>/00-sistema/_readme.md` documentando a cópia + data + path origem + procedure pra `re-sync-operador`.
6. Registrar em `.vault-architect.yml`: `operador_library_snapshot.path`, `operador_library_snapshot.copied_at`, `operador_library_snapshot.arquivos_count`.

Detalhe operacional completo em [`references/operador-library-sync.md`](references/operador-library-sync.md).

### Validação pós-bootstrap

Checklist obrigatório (zero erros pra declarar conclusão):
- [ ] 35+ arquivos clonados, permissões corretas
- [ ] Placeholders Mustache substituídos: 0 residuais (exceto em `_templates/`)
- [ ] `.vault-architect.yml` parseia YAML válido + tem todos campos obrigatórios + **`ticker` presente** (regra TK001 — error)
- [ ] **Cada categoria 00-99 tem `_readme.md`** (9 categorias com `00-sistema/` D-OPERADOR-1)
- [ ] `80-versoes/v0.0/manifest.md` parseia frontmatter
- [ ] `git status` retorna "nothing to commit, working tree clean"
- [ ] Audit interno pós-bootstrap: 0 errors (warnings só em pendências documentadas)

**Validação D-OPERADOR-1 (regra SI001 — quando `--operador-library-path` não-null):**
- [ ] `<vault>/00-sistema/identidade.md` existe e parseia frontmatter (espelha biblioteca shared)
- [ ] `<vault>/00-sistema/design-system.css` parse válido (não-quebra `*-deck-builder` downstream)
- [ ] `.vault-architect.yml` tem campo `operador_library_snapshot` populado (path + copied_at + arquivos_count)
- [ ] Cada `.md` copiado tem marcador `<!-- copied-from-operator-library: ... -->` no primeiro byte (rastreabilidade origem snapshot)

Se algum item falhar, modo não está concluído — retorna erro nomeando o item.

### Handoff (final do bootstrap)

```
[vault-architect] Bootstrap concluído para "{{cliente_nome}}" (ticker: {{ticker}}).
  Path: {{path_destino}}/{{cliente_nome}}/
  Versão do template clonado: 2.0.0
  Versão inicial do manifesto: v0.0
  Arquivos criados: 35
  Validação pós-bootstrap: 0 errors, 0 warnings.
  Pendências registradas no .vault-architect.yml: {{N}}.
  Git: repo inicializado, commit "bootstrap: vault inicializado" criado.

Próximo passo recomendado:
  → invocar `socrates` (modo `roteiro-kickoff`) para etapa 0.3 da Fase 0.
  → ou, se já há briefing v1 e operador pulou pra Subfase 1.2, invocar `oraculo`.

Pendências para você:
  - Substituir placeholder de resumo_handoff_comercial em claude.md (linha NN).
  - Configurar plugins Obsidian em .obsidian/ (Obsidian Git, Templater, Dataview, QuickAdd).
  - Conectar repo a remote (GitHub/GitLab/Gitea) se for trabalhar em time.
```

---

## Modo `retrofit` — síntese

Aplica quando template canônico evoluiu, schema mudou, skill foi adicionada/renomeada, ou nova categoria foi adicionada à tese. **Nunca** sobrescreve outputs produzidos por outras skills (Categoria 1-7, 9, 99) — só meta-docs estruturais e `_readme.md`.

### Tipos de delta suportados

| Tipo | Payload | Side-effect |
|---|---|---|
| `atualizacao_template` | `from_version`, `to_version` | Reaplica diff do template entre versões nos meta-docs (preservando slots) |
| `nova_categoria` | `id`, `nome`, `descricao`, `_readme.md content` | Cria pasta + atualiza `claude.md`/`index.md`/`glossario.md` |
| `renomear_skill` | `nome_antigo`, `nome_novo` | Atualiza `agents.md` + `claude.md`. Não toca outputs já produzidos. |
| `adicionar_skill` | `nome`, `inputs`, `outputs`, `categoria_principal` | Adiciona entrada em `agents.md` + `claude.md` |
| `remover_skill` | `nome`, `motivo` | Marca como `archived` em `agents.md`. Não remove outputs já produzidos. |
| `schema_atualizado` | `arquivo_alvo`, `schema_antigo`, `schema_novo` | Aplica migração; valida conformidade; diff por arquivo |
| `convencao_tags_atualizada` | `tags_adicionadas/renomeadas/removidas` | Atualiza `glossario.md` + `index.md` (queries Dataview) |
| **`re-sync-operador`** (NOVO D-OPERADOR-1) | `operador_library_path` (default `~/.claude/growth-ia-ops/operador/`), `escopo` (`completo` / `apenas-snippets`) | Reconcilia `00-sistema/` do vault com biblioteca shared atualizada. **Preserva overrides locais** (arquivos com `<!-- override-local: true -->` no primeiro byte). Diff visual antes/depois apresentado pra ratificação. Atualiza `.vault-architect.yml` com novo `operador_library_snapshot.copied_at`. Detalhe operacional em [`references/operador-library-sync.md`](references/operador-library-sync.md) §re-sync-operador. |

### Workflow

1. Validar pré-condições: vault Growth IA Ops v2.0; `path_vault` existe; `.vault-architect.yml` parseia; delta válido.
2. Snapshot do estado pré-retrofit: `git status` deve estar limpo (recusa se mudanças não-commitadas).
3. Computar plano: `{arquivo, ação: editar/criar/adicionar-seção, diff_resumo}`.
4. Mostrar plano com símbolos `+` criar / `~` modificar / `!` decisão humana / `-` remover.
5. Aguardar aprovação (`aprovar` / `aprovar exceto: <ids>` / `cancelar`).
6. Aplicar via `Edit` (preferir Edit sobre Write em arquivos com slots customizáveis — ver [`references/slot-delimiters.md`](references/slot-delimiters.md)).
7. Atualizar `CHANGELOG.md` + `.template-version` + `.vault-architect.yml` (`historico_retrofit`).
8. Validar pós-retrofit: 0 errors novos.
9. `git add` (apenas arquivos tocados — nunca `-A`).
10. Propor mensagem padrão `retrofit({{tipo_delta}}): {{resumo}}` + aguardar comando explícito (`commit` / `editar mensagem` / `não commitar`).

### Recusas duras em retrofit

- `git status` mostra mudanças não-commitadas → "commit ou stash antes".
- Conflito de merge ativo → "resolva o conflito antes".
- Detached HEAD → "posicione-se em branch antes".
- Operador não aprovou plano → não aplica nada.

---

## Modo `otimização` — síntese

Audit read-only contra catálogo de regras (Fase 1) + apply opcional sob aprovação (Fase 2). Triggers verbais: "audita o vault", "otimiza", "tem problema?", "checa health".

### Inputs

| Campo | Tipo | Default |
|---|---|---|
| `path_vault` | string | obrigatório |
| `escopo` | array de prefixos | todas: `[FM, MOC, NM, VR, CL, AG, IX, GL, DUP, LK, TG, SC, TK]` |
| `severidade_minima` | enum (`info`/`warning`/`error`) | `warning` |
| `aplicar_auto_fix` | bool | `false` (read-only por default) |

### Fase 1 — Audit Report (sempre)

Estrutura padronizada em [`references/audit-report-template.md`](references/audit-report-template.md). Achados estruturados com `id`, `regra`, `severidade`, `path`, `linha`, `mensagem`, `auto_fixavel`, `acao_sugerida`, `diff_proposto`.

### Fase 2 — Apply (opcional)

Se `aplicar_auto_fix: true` ou operador comanda `aprovar [ids]`:
1. Para cada achado aprovado: gera diff, mostra ao operador, aplica via `Edit`.
2. Não toca achados não-aprovados.
3. Atualiza `updated_at` no frontmatter dos arquivos tocados.
4. Re-roda audit interno. Se introduziu nova divergência, **reverte o último apply** automaticamente.
5. Atualiza `CHANGELOG.md` + stage + propõe `chore(otimizacao): aplica {{N}} correções auto-fixáveis` + aguarda aprovação.

### Loop de feedback (anti alert fatigue)

Após audit com **> 10 achados**, skill **obrigatoriamente** pergunta: *"Algum desses é falso positivo legítimo? Posso adicionar `disabled-rules` no frontmatter dos arquivos afetados ou `rule_overrides` no `.vault-architect.yml`."* Operador responde com lista; skill aplica + re-roda audit + mostra report enxuto. Combate o anti-pattern de "200 achados sem priorização" identificado em estado da arte (Praetorian).

---

## Política de Git

| Modo | Comportamento | Mensagem-padrão |
|---|---|---|
| `bootstrap` | **Auto-commit autorizado** (vault novo, zero risco) | `bootstrap: vault inicializado para {{cliente_nome}}` + bloco descritivo |
| `retrofit` | Stage automático (`git add` arquivos tocados); commit **manual** após aprovação humana | `retrofit({{tipo_delta}}): {{resumo curto}}` |
| `otimização` Fase 2 | Stage automático; commit manual após aprovação | `chore(otimizacao): aplica {{N}} correções auto-fixáveis` |

Skill **não** configura remote, não faz push, não conecta a GitHub. Operador faz isso depois manualmente. Skill **não** configura hooks de pré-commit (Husky/etc.) — deixa pra operador.

---

## Catálogo de regras (resumo)

12 prefixos canônicos. Detalhe completo em [`references/rules-catalog.md`](references/rules-catalog.md).

| Prefixo | Domínio | Exemplo |
|---|---|---|
| **FM*** | Frontmatter de outputs operacionais | FM001: arquivo em `50-operacao/operacional/` sem frontmatter de lifecycle (error, manual) |
| **MOC*** | `index.md` raiz / Dataview | MOC001: query Dataview com sintaxe inválida (warning, manual) |
| **NM*** | Nomenclatura de arquivos | NM001: arquivo com acento ou cedilha (warning, manual) |
| **VR*** | Versionamento (`80-versoes/`) | VR001: salto de versão sem changelog (warning); VR002: `_atual.md` aponta pra versão inexistente (error, auto-fix) |
| **CL*** | `claude.md` | CL001: invariantes desatualizadas vs. template (warning, auto-fix via retrofit); CL002: slot sem delimitadores (warning, manual) |
| **AG*** | `agents.md` | AG001: skill no Mapa de Inputs ausente em `agents.md` (warning, auto-fix); AG002: `{{status}}` sem substituição (warning, manual) |
| **IX*** | `index.md` | IX001: query Dataview que referencia categoria inexistente (error, manual) |
| **GL*** | `glossario.md` | GL001: termo usado sem entrada no glossário (info, manual) |
| **DUP*** | Duplicação | DUP001: bloco >50% duplicado entre 2 meta-docs (warning, manual) |
| **LK*** | Wikilinks | LK001: wikilink quebrado (warning, manual — pode ser TODO intencional) |
| **TG*** | Tags | TG001: tag fora da convenção (warning, manual); TG002: tag canônica com valor não-permitido (error, manual) |
| **SC*** | Schema de output canônico | SC001: manifesto sem `version`/`sprint`/`drop` no frontmatter (error, auto-fix se inferível) |
| **TK*** | Ticker (id externo Flow MCP) | TK001: `.vault-architect.yml` sem `ticker` (error, manual — bloqueia integrações Flow); TK002: ticker fora de `[A-Z]{4}` (warning) |

**Auto-fix limitado a transformações sintáticas seguras:** adicionar campo de frontmatter ausente; atualizar `_atual.md`; adicionar entrada faltante em `agents.md`; reformatar tabela markdown desalinhada; padronizar quebras de linha. **Mexer em prosa: NUNCA.**

---

## Invariantes vs. slots customizáveis

Convenção pra `retrofit` preservar customização do operador. Delimitadores HTML em meta-docs:

```markdown
## Saúde dos pilares (Pillars-Health vigente)

<!-- vault-architect:slot:pillars-health -->
- **Oferta:** N2 (gargalo: posicionamento)
- **Marketing:** N1
- **Vendas:** N1
- **Retenção:** N1
<!-- /vault-architect:slot:pillars-health -->
```

Em retrofit, skill: lê conteúdo entre delimitadores → reconstrói arquivo do template canônico → reinjeta conteúdo do slot na posição equivalente. Mapa completo dos slots por meta-doc em [`references/slot-delimiters.md`](references/slot-delimiters.md).

Se template canônico **removeu** um slot que tinha conteúdo: skill alerta e move conteúdo pra `99-arquivo/slots-removidos-{{data}}.md` sob aprovação.

---

## Migração de Dante v1 — política

Skill **recusa** vaults Dante v1 em fluxo canônico. Mas aceita **execução guiada por playbook explícito em contexto** quando operador invoca migração referenciando o playbook canônico (`arquitetura/playbook-migracao-dante-v1.md`). Detalhe completo em [`references/migration-from-dante-v1.md`](references/migration-from-dante-v1.md).

Mensagem de recusa quando Dante v1 detectado SEM playbook:

```
[vault-architect] Recusa: vault Dante v1 detectado em {{path}}.

Dante v1 está deprecado a partir do Growth IA Ops v2.0. A operação
canônica (bootstrap/retrofit/otimização) não suporta esse padrão.

Para migrar:
  → produza ou localize `arquitetura/playbook-migracao-dante-v1.md`.
  → invoque novamente referenciando o playbook explicitamente:
    "vault-architect, lê o playbook em <path> e migra esse Dante v1 pra v2."

Para descartar e começar do zero:
  → mova {{path}} pra {{path}}-dante-v1-arquivado.
  → rode `vault-architect bootstrap path: {{path}} ...` em pasta limpa.
```

---

## Handoff com outras skills

### Após `bootstrap`

| Próximo passo | Skill recomendada | Pré-condição atendida |
|---|---|---|
| Conduzir kickoff (etapa 0.3 Fase 0) | `socrates` modo `roteiro-kickoff` | Vault inicializado, `claude.md` apontando paths canônicos |
| Pesquisa de mercado (Subfase 1.2.1) | `oraculo` | `10-fundacao/contexto.md` (seção Negócio & Mercado) semeado — fallback legado: `briefing-inicial.md` |
| ICM (Subfase 1.2.2) | `michelangelo` | Briefing v1 + Relatório de Mercado disponíveis |
| GTM Plan (Subfase 1.4.1) | `cesar` | Toda Fundação populada |

### Skill **nunca** chama outra skill diretamente

Operador é o orchestrator (Princípio 7). Quando outra skill detecta necessidade de retrofit:

```
[skill-X] Vault precisa de retrofit. Rode `/vault-architect retrofit
path: {{path}} delta: {{tipo}}` antes de continuar.
```

### Anti-corruption layer

Skills da Operação (ex: `media-buyer-meta`) escrevem em `50-operacao/operacional/aquisicao/paga/sprint-XXX/drop-YYY/` esperando que essa estrutura exista. Bootstrap cria apenas `50-operacao/operacional/_index.md` — pastas por workflow são criadas **on-demand** pelas skills operacionais. Critério: vault-architect constrói "carcaças vazias" das categorias top-level; skills operacionais criam subpastas conforme produzem outputs.

---

## Anti-patterns

Evite:
- ❌ **Mexer em prosa de outputs.** Frontmatter sim; conteúdo curado pelo operador (briefings, ICMs, planos), jamais.
- ❌ **Renomear arquivo silenciosamente.** Quebra wikilinks. Sempre listar links afetados antes.
- ❌ **`git add -A` ou `git add .`** em retrofit/otimização. Use sempre stage explícito dos arquivos tocados.
- ❌ **`git commit` sem aprovação humana** em retrofit/otimização. Bootstrap auto-commita; outros modos não.
- ❌ **Aplicar correções da Fase 2 (otimização) sem ID aprovado.** Read-only por default.
- ❌ **Aceitar Dante v1 sem playbook explícito.** Recusa direta + apontar playbook.
- ❌ **Substituir Mustache via plugin Templater.** Substituição é manual no bootstrap (não dependemos do plugin estar carregado).
- ❌ **Inflar severidade.** 3 níveis (info/warning/error) — não criar 7 níveis.
- ❌ **Pular loop de feedback** com >10 achados em otimização. Alert fatigue arruína a skill.

---

## Critérios de qualidade (gates por modo)

### Bootstrap
- [ ] 35+ arquivos clonados com permissões corretas.
- [ ] 0 placeholders Mustache residuais (exceto em `_templates/`).
- [ ] `.vault-architect.yml` parseia + todos campos obrigatórios + **ticker presente**.
- [ ] `git init` + primeiro commit + working tree limpa.
- [ ] Audit interno pós-bootstrap: 0 errors.
- [ ] Manifesto v0.0 criado e referenciado por `_atual.md`.
- [ ] Handoff explícito apontando próxima skill recomendada.

### Retrofit
- [ ] Pré-condição validada (Growth IA Ops v2.0 + `git status` limpo).
- [ ] Plano apresentado com diff por arquivo.
- [ ] Aprovação explícita recebida.
- [ ] Slots customizáveis preservados (verificável por diff antes/depois).
- [ ] `CHANGELOG.md` + `.vault-architect.yml` atualizados (`historico_retrofit`).
- [ ] Audit pós-retrofit: 0 errors novos.
- [ ] Stage Git pronto, mensagem proposta. **Skill não fez `git commit`.**

### Otimização
- [ ] Audit report renderizado conforme estrutura canônica.
- [ ] Achados agrupados por categoria/severidade/auto-fixabilidade.
- [ ] Loop de feedback ativado se >10 achados.
- [ ] Apply (se houver) por ID aprovado, com diff visualizável.
- [ ] Re-audit após apply: nenhuma divergência nova introduzida (caso contrário, reverte).
- [ ] `CHANGELOG.md` atualizado se houve apply.

### Comuns aos 3 modos
- [ ] `TodoWrite` usado para visibilidade do progresso.
- [ ] Linguagem em pt-BR.
- [ ] Vocabulário canônico (Output, Workflow, Bounded Context, Vault, Manifest, Sprint, Drop).
- [ ] Nenhuma operação destrutiva sem aprovação humana.

---

## Referências

- Doc canônico de arquitetura: `c:\Users\mcafe\OneDrive\Documentos\Claude\Projects\06_teses\Tese Growth IA Ops v2.0\arquitetura\skills\setup\vault-architect.md` (§4.1 input + §5.7 sub-modo D-OPERADOR-1)
- **D-OPERADOR-1 (decisão âncora):** `c:\...\Tese Growth IA Ops v2.0\arquitetura\decisoes-mcps-formatos.md`
- **Setup Inicial do Operador (fase âncora):** `c:\...\Tese Growth IA Ops v2.0\arquitetura\setup-inicial-operador.md`
- **Skill produtora da biblioteca shared:** `~/.claude/skills/_sistema/operador-onboarding/SKILL.md` (D-OPERADOR-1 — produz o conteúdo que esta skill consome via `--operador-library-path`)
- Tese Growth IA Ops v2.0 (Princípios 1, 3, 4, 7, 8, **11 — Multi-tenant explícito**)
- Esqueleto template: `c:\...\Tese Growth IA Ops v2.0\templates\vault-template\` (clonado em bootstrap)
- Fase 0 detalhada (etapa 0.2 invoca esta skill)
- Anthropic — Building Effective Agents (padrão Routing)
- Eric Evans — Domain-Driven Design (Bounded Context)
- Terraform `plan` × `apply` (inspiração dry-run default)
- ESLint `--fix-dry-run` (inspiração severidade 3-níveis)
- Praetorian — Alert Fatigue (loop de feedback)
- Copier / Cruft (inspiração `bootstrap` + `retrofit` com `.template-version`)

## References internas (carregadas sob demanda)

- [`references/rules-catalog.md`](references/rules-catalog.md) — **16 prefixos** × N regras × severidade × auto-fixabilidade (inclui SI* — `00-sistema/` D-OPERADOR-1 + **MP\*/TC\*/RS\* — doutrina sináptica v2.2.0**)
- [`references/audit-report-template.md`](references/audit-report-template.md) — formato canônico do output de modo `otimização`
- [`references/bootstrap-mustache-vars.md`](references/bootstrap-mustache-vars.md) — tabela de placeholders Mustache substituídos no bootstrap
- [`references/slot-delimiters.md`](references/slot-delimiters.md) — convenção dos slots HTML em meta-docs
- [`references/migration-from-dante-v1.md`](references/migration-from-dante-v1.md) — política de recusa + fluxo de migração-guiada por playbook
- [`references/operador-library-sync.md`](references/operador-library-sync.md) — **v2.1.0 D-OPERADOR-1** — cópia bootstrap + sub-modo `re-sync-operador` retrofit + política de overrides locais via marcador HTML
- [`references/mapa-md-spec.md`](references/mapa-md-spec.md) — **NOVO v2.2.0** — spec canônico do `mapa.md` por pasta (frontmatter + 7 seções obrigatórias + protocolo pasta vazia + anti-patterns)
- [`references/toc-resumo-spec.md`](references/toc-resumo-spec.md) — **NOVO v2.2.0** — spec do TOC navegável + Resumo 60s com threshold canônico (Cat 1/2/3/4/8 OU ≥100 linhas) + stub procedure
- [`references/audit-mapa-mode.md`](references/audit-mapa-mode.md) — **NOVO v2.2.0** — sub-modo `audit-mapa` (escopo MP+TC+RS) + atalhos semânticos + cadência recomendada
- [`references/cascade-helper.md`](references/cascade-helper.md) — **NOVO v2.2.0** — interface pública do helper `atualiza-cascata` exportável pra outras skills + 4 níveis de propagação + telemetria

---

## Changelog v2.1.0 → v2.2.0 (Doutrina Sináptica)

**Capacidades novas:**
- `mapa.md` obrigatório por pasta (mesmo vazia) — funciona como índice sináptico local; 7 seções canônicas incluindo "O que entra"/"O que NÃO entra" como contrato de pasta.
- TOC navegável + Resumo 60s obrigatórios em MDs de Categoria 1/2/3/4/8 e em qualquer MD ≥100 linhas.
- Helper `atualiza-cascata` exportável — outras skills (oraculo, michelangelo, cesar, escriba, etc.) chamam ao gravar output pra propagar mutação em até 4 níveis (arquivo → pasta-pai → ancestrais → meta-docs raiz).
- Sub-modo `audit-mapa` (escopo restrito MP/TC/RS) com atalhos semânticos `audit-mapa` e `audit-mapa --fix`.
- 3 prefixos novos no rules-catalog: **MP\*** (mapa per-folder) + **TC\*** (TOC) + **RS\*** (Resumo 60s).
- Tipo novo de delta de retrofit: `doutrina-sinaptica-v2.2.0` (aplica retrofit em vault v2.1.x criando mapas faltantes + inserindo stubs).
- 4 references novas: `mapa-md-spec.md`, `toc-resumo-spec.md`, `audit-mapa-mode.md`, `cascade-helper.md`.

**Compatibilidade:**
- Vaults v2.0.x e v2.1.x continuam funcionando — retrofit via `--delta=doutrina-sinaptica-v2.2.0` traz pra v2.2.0 sem perda de conteúdo (só insere mapas + stubs).
- Skills downstream que não chamam o helper continuam funcionando — cascata vira best-effort (operador roda `audit-mapa --fix` periodicamente pra normalizar).

**Não muda:**
- 9 categorias canônicas da estrutura (00-sistema/ + 10-fundacao/ + 20-snapshots/ + 30-decisoes/ + 40-comunicacoes/ + 50-operacao/ + 60-loops/ + 70-memoria/ + 80-versoes/ + 90-referencias/ + 99-arquivo/).
- Manifesto versionado em 80-versoes/ permanece com `system-manifest-builder` (skill não invade).
- Princípio "Dante v1 deprecado, só Growth IA Ops v2.0" permanece.
- 13 prefixos de regras anteriores (FM/MOC/NM/VR/CL/AG/IX/GL/DUP/LK/TG/SC/TK/SI) permanecem inalterados.
