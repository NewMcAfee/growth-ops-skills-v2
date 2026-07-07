# Spec — Helper `atualiza-cascata` (Doutrina Sináptica v2.2.0)

> Reference da skill `vault-architect`. Define a interface pública do helper de cascata que outras skills (oraculo, michelangelo, cesar, escriba, etc.) chamam ao gravar output no vault.

---

## Princípio

Cada mutação em arquivo do vault (Edit/Write/mv/rm) propaga em cascata através de até 4 níveis: arquivo → pasta-pai → ancestrais → meta-docs raiz. Sem helper canônico, cada skill teria que reimplementar essa lógica e o drift seria garantido.

O helper `atualiza-cascata` centraliza a propagação. É **componente de skill** (`vault-architect`) exposto como interface pública pra consumo por outras skills.

---

## Interface pública

### Invocação

```
vault-architect atualiza-cascata <path-absoluto-do-arquivo-mutado>
```

Argumentos:
- **path** (obrigatório): path absoluto do arquivo que sofreu Edit/Write/mv/rm.
- **--motivo** (opcional): string descrevendo a mutação ("ratificacao-apresentacao", "drop-mensal-M2", "patch-mid-drop"). Vai pro `historico_cascata` em `.vault-architect.yml`.
- **--dry-run** (opcional, default `false`): se `true`, computa e mostra diff sem aplicar — útil pra debug.

Side-effects:
- Edita `mapa.md` da pasta-pai (sempre).
- Edita `mapa.md` de ancestrais até a raiz (se hierarquia mudou).
- Edita meta-docs raiz (`claude.md` / `agents.md` / `index.md`) condicionalmente.
- Edita `80-versoes/_atual.md` + `CHANGELOG.md` raiz (se Manifest bumpou).
- Atualiza `.vault-architect.yml` (`historico_cascata` append).
- Stage Git (`git add` dos arquivos tocados).
- **NÃO commita** — operador commita explicitamente.

### Output

Retorna estrutura:

```yaml
cascata_aplicada:
  path_origem: /path/absoluto/do/arquivo/mutado.md
  motivo: ratificacao-apresentacao
  timestamp: 2026-05-24T15:30:00-03:00
  arquivos_tocados:
    - <vault>/30-decisoes/mapa.md
    - <vault>/mapa.md
    - <vault>/claude.md
  niveis_propagados:
    - nivel_1_arquivo_proprio: true
    - nivel_2_pasta_pai_mapa: true
    - nivel_3_walk_up: false  # hierarquia não mudou
    - nivel_4_meta_docs_raiz: true  # output canônico Cat 3
  manifest_bumpou: false
  warnings: []
```

---

## 4 níveis de propagação

### Nível 1 — Arquivo próprio

Quando: SEMPRE que arquivo é Edit/Write.

Ação:
- Detecta se arquivo é elegível pra TOC + Resumo 60s (ver `references/toc-resumo-spec.md`).
- Se elegível e headings H2/H3 mudaram → regenera TOC.
- Se elegível e conteúdo material mudou (heurística: ≥10 linhas alteradas fora de TOC/frontmatter) → insere anotação `<!-- resumo-pendente-revisao: <motivo> -->` no Resumo 60s. NÃO reescreve resumo automaticamente (resumo precisa de curadoria humana).
- Se arquivo é `mapa.md` → valida frontmatter + estrutura conforme `mapa-md-spec.md`.

### Nível 2 — `mapa.md` da pasta-pai

Quando: arquivo foi criado, deletado, renomeado, OU teve `description` do frontmatter alterado.

Ação:
- Lê pasta-pai com `ls` real.
- Atualiza seção "Arquivos" do `mapa.md` da pasta-pai com entry novo/removido/atualizado.
- Atualiza `updated_at` no frontmatter do `mapa.md`.
- Atualiza linha "_Última cascata: ..._" no rodapé.

### Nível 3 — Walk-up até a raiz

Quando: pasta foi criada OU deletada (não só arquivo dentro de pasta existente).

Ação:
- Pra cada pasta ancestral até a raiz do vault:
  - Atualiza seção "Subpastas" do `mapa.md` da ancestral (adiciona/remove entry da subpasta filha).
  - Atualiza `updated_at`.
  - Atualiza "_Última cascata_".

### Nível 4 — Meta-docs raiz (`claude.md`, `agents.md`, `index.md`)

Quando (qualquer um dos gatilhos):
- Pasta de Categoria top-level (00-99) foi criada/deletada.
- Output canônico de Cat 1, Cat 3 Decisão, Cat 4 Comunicação, ou Cat 8 Manifest foi criado/deletado.
- Skill foi citada/removida em output (detectado por mudança em frontmatter `created_by` ou seção de handoff).

Ação:
- `claude.md` — atualiza Mapa de Outputs (path canônico × output) se output novo/removido.
- `agents.md` — atualiza catálogo de skills com novo `created_by` se skill nova citada.
- `index.md` — atualiza queries Dataview se categoria nova/removida.
- Se Manifest bumpou versão → atualiza `80-versoes/_atual.md` (ponteiro) + `CHANGELOG.md` raiz (entry novo).

---

## Heurísticas de detecção

### Mutação material vs. cosmética

Heurística: comparar arquivo pré-mutação (via `git diff HEAD <path>`) com pós:
- Mudança ≥10 linhas fora de frontmatter/TOC = **material** → triggers nível 1 anotação `<!-- resumo-pendente-revisao -->`.
- Mudança <10 linhas OU só em frontmatter/TOC = **cosmética** → não trigger anotação.

### Output canônico vs. arquivo arbitrário

Heurística: arquivo é output canônico se path bate com Mapa de Outputs declarado em `claude.md` raiz. Skill consulta `claude.md` na primeira invocação por sessão e cacheia.

### Skill citada

Heurística: detecta via frontmatter (`created_by: <skill>`) ou via seções padronizadas ("Inputs", "Outputs", "Handoff"). Se skill nova aparece, atualiza `agents.md`.

---

## Quando NÃO cascatear

- Arquivo em `.git/`, `.obsidian/`, `node_modules/`, ou qualquer pasta opaca.
- Arquivo fora do vault Growth IA Ops v2.0 (sem `claude.md` raiz mencionando "Growth IA Ops v2.0" subindo na árvore).
- Mutação puramente de whitespace/lint (helper detecta via `git diff --shortstat` retornando 0 linhas materiais).
- Arquivo de skill (`~/.claude/skills/`) — skills não são vault.

---

## Política de erro

Helper é **best-effort não-bloqueante**:
- Se cascata falha (ex: `mapa.md` da pasta-pai está com YAML inválido), helper:
  - Loga warning.
  - Adiciona achado em `.vault-architect.yml` (`cascata_falhas_pendentes`).
  - Retorna sucesso da operação principal (Edit/Write não é revertido).
  - Recomenda rodar `audit-mapa --fix` pra normalizar.

Filosofia: cascata é otimização — sua falha NÃO deve bloquear o trabalho substantivo do operador. Audit-mapa periódico (trimestral) captura backlog.

---

## Consumo por outras skills

### Pattern canônico (recomendado)

Skill downstream (ex: `cesar` ao gravar `gtm-plan.md`):

1. Gera output e escreve via `Write` em path canônico.
2. Imediatamente após o `Write`, chama:
   ```
   vault-architect atualiza-cascata /path/absoluto/30-decisoes/gtm-plan.md --motivo=fundacao-1.4.1
   ```
3. Recebe estrutura de retorno; se houver warnings, propaga ao operador.

### Pattern manual (fallback)

Se helper indisponível (skill rodando em sandbox sem vault-architect carregado):
1. Skill escreve output.
2. Skill emite mensagem ao operador:
   > "[skill-X] Output gravado em <path>. Rodar `vault-architect atualiza-cascata <path>` ao fim da sessão pra propagar."
3. Operador roda manualmente ou agenda no fim da sessão.

### Anti-patterns

- ❌ Skill downstream regenerar `mapa.md` da pasta-pai por conta própria (não passa pelo helper, drift de implementação).
- ❌ Skill downstream editar `claude.md` / `agents.md` / `index.md` raiz (escopo exclusivo do `vault-architect`).
- ❌ Skill downstream commitar Git (helper só faz stage; commit é operador).
- ❌ Pular cascata "porque é só uma pequena edição" — drift acumula.

---

## Telemetria e audit

`.vault-architect.yml` ganha campo:

```yaml
historico_cascata:
  - timestamp: 2026-05-24T15:30:00-03:00
    path_origem: 30-decisoes/gtm-plan.md
    motivo: fundacao-1.4.1
    skill_origem: cesar
    arquivos_tocados: 3
    niveis: [1, 2, 4]
  - timestamp: 2026-05-24T16:45:00-03:00
    path_origem: 20-snapshots/2026-05/cenario-baseline.md
    motivo: fundacao-1.3.4
    skill_origem: arquimedes
    arquivos_tocados: 2
    niveis: [1, 2]
```

Auditável retroativamente: `vault-architect otimização --escopo=cascata` reporta cobertura (% de Edit/Write que tiveram cascata correspondente).
