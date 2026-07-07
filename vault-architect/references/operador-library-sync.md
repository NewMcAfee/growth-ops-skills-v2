# Cópia + sync da biblioteca shared do operador → `<vault>/00-sistema/`

> Reference operacional da extensão **D-OPERADOR-1** (introduzida em vault-architect v2.1.0). Cobre 2 fluxos: (1) cópia inicial no `bootstrap` via input `--operador-library-path`; (2) sub-modo `re-sync-operador` em `retrofit` que reconcilia vault antigo com biblioteca shared atualizada.

---

## TOC

1. [Contexto + Princípio 11 (multi-tenant explícito)](#contexto)
2. [Path canônico 1:1](#path-canonico)
3. [Bootstrap — cópia inicial](#bootstrap)
4. [Retrofit — sub-modo `re-sync-operador`](#retrofit-re-sync)
5. [Marcador HTML — origem snapshot vs override local](#marcadores-html)
6. [Estados degradados (path inexistente / null / vazio)](#estados-degradados)
7. [Pseudocódigo Bash — cópia recursiva canônica](#pseudocodigo)
8. [Diff visual antes-depois](#diff-visual)
9. [Validações pós-cópia (regras SI*)](#validacoes)
10. [Edge cases](#edge-cases)

---

## Contexto

O sistema Growth IA Ops v2.0 tem **dois eixos multi-tenant disjuntos** (Princípio 11):

| Eixo | Identidade | Cadência | Onde mora |
|---|---|---|---|
| **Cliente final do projeto** | Brand Core + DS + Copy System produzidos pela Fundação per-projeto (`campbell` + `design-system-engineer` + `escriba`) | Once-per-project | `<vault>/10-fundacao/` (Categoria 1 Estado Evergreen) |
| **Operador / agência** | DS do operador + identidade + perfil + assinatura cerimonial + ferramental + integrations + snippets | Once-per-operator (cross-projeto) | Filesystem global: `~/.claude/growth-ia-ops/operador/` (biblioteca shared); espelhada em cada vault como cópia snapshot em `<vault>/00-sistema/` (Categoria 9ª) |

**Por que `00-sistema/` no vault e não só na biblioteca shared:**
- Preserva **Princípio 8 (Vault auto-contido)** — quem assume projeto ano 2 tem tudo dentro do vault sem hunt em `~/.claude/`.
- **Snapshot temporal:** DS muda em 2027; vault de 2025 mantém DS de 2025 — coerência histórica preservada.
- Skills cerimoniais (5 `*-deck-builder`) consomem `<vault>/00-sistema/design-system.css` localmente — sem dependência runtime de filesystem fora do vault.

---

## Path canônico

Mapping 1:1 nome-a-nome:

```
Biblioteca shared do operador             →  Cópia snapshot no vault
──────────────────────────────────────────   ──────────────────────────────────────
~/.claude/growth-ia-ops/operador/X.md     →  <vault>/00-sistema/X.md
~/.claude/growth-ia-ops/operador/Y/       →  <vault>/00-sistema/Y/
```

Estrutura completa esperada após cópia bootstrap (≈59 arquivos / 19 pastas baseado em V4 piloto):

```
<vault>/00-sistema/
├── _readme.md                       ← criado pela skill — documenta origem snapshot + procedure re-sync
├── identidade.md                    ← cópia da biblioteca shared
├── design-system.md                 ← cópia
├── design-system.css                ← cópia (consumido pelos *-deck-builder)
├── tese-growth-ia-ops-resumida.md   ← cópia
├── assinatura.html                  ← cópia
├── _status.md                       ← cópia
├── assets/                          ← cópia recursiva
│   ├── README.md
│   ├── logo.svg + logo-dark.svg + logo-horizontal*.svg + .png fallback
│   └── fontes/<famílias>/<pesos>.{woff2,ttf}
├── design-system-references/_catalogo.md
├── integrations/
│   ├── README.md
│   └── {calls,whatsapp,crm,tasks,health-score}-mcp.yml
├── n8n-snippets/README.md (+ JSONs quando materializados)
├── gtm-snippets/README.md (+ JSONs)
├── scripts-growthpack/README.md (+ .gs)
├── looker-templates/_pendente.md
├── lp-templates/_pendente.md
├── prompts/_pendente.md
├── few-shot/_pendente.md
├── eval-rubrics/_pendente.md
├── synthetic-clients/_pendente.md
├── decision-templates/_pendente.md
└── handoff-templates/_pendente.md
```

---

## Bootstrap

### Comportamento por estado de input

| `--operador-library-path` | Comportamento |
|---|---|
| Default `~/.claude/growth-ia-ops/operador/` (path existe + populado) | **Caminho feliz:** copia conteúdo recursivo + adiciona marcador origem snapshot + registra metadados em `.vault-architect.yml`. |
| Path explícito provido + path existe | Mesmo caminho feliz, mas com path custom (ex: outra V4 célula com biblioteca shared própria). |
| Path provido + path inexistente | Warning explícito + popula `<vault>/00-sistema/` com placeholders idênticos ao caso `null` + adiciona pendência em `.vault-architect.yml`. **Não bloqueia bootstrap.** |
| Path provido + path existe mas sem `identidade.md` (V1 da biblioteca shared falha) | Mesmo comportamento de path inexistente — biblioteca shared incompleta = degradado. |
| `null` explícito | Cria `<vault>/00-sistema/_readme.md` com placeholder explicativo. **Modo degradado intencional** — skills cerimoniais downstream omitem identidade do operador (asset placeholder). |

### Estrutura placeholder (modo degradado)

Quando `00-sistema/` não pode ser populada via cópia, skill cria stub minimal:

```
<vault>/00-sistema/
└── _readme.md
```

Conteúdo de `_readme.md` placeholder:

```markdown
---
versao_skill_origem: "vault-architect@2.1.0"
tipo_arquivo: placeholder-degraded
status: nao-populada
---

# 00-sistema/ — pasta placeholder (modo degradado)

Esta pasta deveria ter sido populada com cópia snapshot da biblioteca
shared do operador (`~/.claude/growth-ia-ops/operador/`) durante o
bootstrap, mas não foi (motivo abaixo).

## Motivo
{{`null` explícito | path inexistente: <path> | path sem identidade.md}}

## Como popular depois

1. Garanta que biblioteca shared do operador está populada:
   ```
   operador-onboarding inicial
   ```

2. Rode retrofit `re-sync-operador`:
   ```
   vault-architect retrofit \
     delta_tipo: re-sync-operador \
     operador_library_path: ~/.claude/growth-ia-ops/operador/ \
     escopo: completo
   ```

## Impacto sem popular

Skills cerimoniais downstream que consomem `00-sistema/` operam com
asset placeholder (omitem seções dependentes + nota explicativa):
- 5 `*-deck-builder` (gtm/qbr/sprint-review/growthstorming/drop-delivery)
- `account-curator` modo `kickoff` (cerimonial)
```

---

## Retrofit re-sync

### Quando rodar

- Operador rodou `operador-onboarding re-config-operador` (ex: rebrand, nova ferramenta, tese adapta) e quer propagar pros vaults ativos.
- Cliente assume projeto antigo + quer atualizar identidade do operador no vault pra versão atual.
- Auditoria detectou drift entre `<vault>/00-sistema/` e biblioteca shared atualizada.

### Inputs

| Campo | Tipo | Default | Função |
|---|---|---|---|
| `operador_library_path` | string (path absoluto) | `~/.claude/growth-ia-ops/operador/` | Path da biblioteca shared atualizada (source of truth) |
| `escopo` | enum | `completo` | `completo` reconcilia tudo; `apenas-snippets` reconcilia só `n8n-snippets/`, `gtm-snippets/`, `scripts-growthpack/` (cadência trimestral leve) |

### Workflow

1. **Pré-condições:**
   - Vault Growth IA Ops v2.0 detectado.
   - `git status` limpo (recusa se mudanças não-commitadas).
   - Biblioteca shared existe + tem `identidade.md` populado.

2. **Snapshot do estado pré-sync:** `git stash` opcional ou marca commit ID atual pra rollback.

3. **Computar diff cross-arquivo:**
   - Para cada arquivo em `<biblioteca-shared>/X.md`:
     - Se arquivo correspondente em `<vault>/00-sistema/X.md` tem `<!-- override-local: true -->` no primeiro byte → **PRESERVA** (não-toca; lista em report como "preservado por override").
     - Senão → marca pra atualizar.
   - Para cada arquivo em `<vault>/00-sistema/X.md` ausente em biblioteca shared → marca pra arquivar em `<vault>/99-arquivo/00-sistema-removidos-YYYY-MM-DD/X.md`.

4. **Apresentar plano visual** com símbolos `+ adicionar`, `~ atualizar`, `! preservar override`, `- arquivar`.

5. **Aguardar aprovação explícita** (`aprovar` / `aprovar exceto: <ids>` / `cancelar`).

6. **Aplicar** via Edit (não Write — preserva permissões + git history limpo).

7. **Atualizar metadados:**
   - `.vault-architect.yml`: `operador_library_snapshot.copied_at` ← agora; `historico_resync.<YYYY-MM-DD>` ← entrada nova com tipo + escopo + N arquivos tocados
   - `<vault>/00-sistema/_readme.md`: atualizar campo "última reconciliação"

8. **CHANGELOG.md** atualizado com entrada `retrofit(re-sync-operador): {{escopo}} — N arquivos atualizados, K preservados por override`.

9. **Stage Git** (apenas arquivos tocados — nunca `-A`). Mensagem proposta + aguardar comando explícito (`commit` / `editar mensagem` / `não commitar`).

10. **Audit pós-sync:** 0 errors novos (regras SI*).

### Recusas duras em re-sync-operador

- Biblioteca shared inexistente → "rode `operador-onboarding inicial` antes".
- Biblioteca shared com `identidade.md` ausente/vazio → "biblioteca shared incompleta — rode `operador-onboarding re-config-operador` antes".
- `git status` mostra mudanças não-commitadas → "commit ou stash antes".
- Operador não aprovou plano → não aplica nada.

---

## Marcadores HTML

Convenção pra distinguir arquivos copiados (atualizáveis) de overrides locais (preservados):

### Marcador 1 — Origem snapshot

```html
<!-- copied-from-operator-library: ~/.claude/growth-ia-ops/operador/ @ 2026-05-09 -->
```

- Inserido pela skill no **primeiro byte** de cada `.md` durante bootstrap + `re-sync-operador`.
- **Sobrescrevível em re-sync** — skill atualiza arquivo se diff existe vs biblioteca shared.

### Marcador 2 — Override local

```html
<!-- override-local: true -->
```

- Operador adiciona manualmente substituindo o marcador 1 quando customiza arquivo (ex: assinatura cerimonial adaptada à voz do cliente premium).
- **PRESERVADO em re-sync** — skill detecta + lista em report + não-toca.
- Operador pode remover o marcador depois (volta ao comportamento de cópia snapshot atualizável).

### Política

- Marcador 1 = "este é cópia snapshot — re-sync atualiza"
- Marcador 2 = "este foi customizado localmente — re-sync preserva"
- **Sem marcador** (caso edge): skill trata como suspeito — apresenta arquivo como "preservar?" ao operador antes de qualquer ação.

---

## Estados degradados

### Estado 1 — `null` explícito

Operador deliberadamente pula. Útil quando:
- Bootstrap em ambiente de teste (não precisa identidade real).
- Vault temporário pra avaliar estrutura sem pessoalidade.

### Estado 2 — Path inexistente

Path provido mas filesystem retorna ENOENT. Comportamento: warning + placeholders + pendência registrada. Nunca bloqueia bootstrap.

### Estado 3 — Path existe mas vazio / `identidade.md` ausente

Biblioteca shared incompleta (operador-onboarding não-rodado completo). Mesmo comportamento do Estado 2.

### Estado 4 — Path existe + populado mas operador rodou `null` por engano

Skill detecta + sugere: "biblioteca shared populada em `~/.claude/growth-ia-ops/operador/` — quer rodar com `--operador-library-path` apontando pra ela em vez de `null`?". Operador confirma.

---

## Pseudocódigo

```bash
# Bootstrap — cópia inicial via Bash
SRC="${OPERADOR_LIBRARY_PATH:-$HOME/.claude/growth-ia-ops/operador}"
DEST="$VAULT_PATH/00-sistema"

# 1) Estado degradado se path inexistente
if [ ! -s "$SRC/identidade.md" ]; then
  mkdir -p "$DEST"
  cat > "$DEST/_readme.md" <<EOF
[placeholder-degraded — ver operador-library-sync.md §estados-degradados]
EOF
  echo "warning: 00-sistema populada com placeholders — biblioteca shared ausente em $SRC"
  exit 0
fi

# 2) Cópia recursiva preservando estrutura
cp -r "$SRC/." "$DEST/"

# 3) Inserir marcador origem em cada .md (primeiro byte)
DATA_HOJE=$(date +%Y-%m-%d)
MARKER="<!-- copied-from-operator-library: $SRC @ $DATA_HOJE -->"

find "$DEST" -name "*.md" | while read f; do
  # Insere marker no início se não-presente (idempotente)
  if ! head -1 "$f" | grep -q "copied-from-operator-library\|override-local"; then
    sed -i "1i $MARKER" "$f"
  fi
done

# 4) Criar _readme.md específico da pasta no vault
cat > "$DEST/_readme.md" <<EOF
---
versao_skill_origem: "vault-architect@2.1.0"
tipo_arquivo: categoria-readme
categoria: 00-sistema
operador_library_origem: "$SRC"
copied_at: "$DATA_HOJE"
arquivos_count: $(find "$DEST" -type f | wc -l)
---

# 00-sistema/ — Identidade do operador (cópia snapshot)

Cópia snapshot de \`$SRC\` no momento do bootstrap. **Snapshot temporal:**
preserva versão da biblioteca shared mesmo se ela evoluir depois.

## Re-sincronizar com biblioteca shared atualizada

\`\`\`
vault-architect retrofit \\
  delta_tipo: re-sync-operador \\
  operador_library_path: $SRC \\
  escopo: completo
\`\`\`

## Customizar arquivo localmente (preservar em re-sync)

Substitua o marcador HTML \`<!-- copied-from-operator-library: ... -->\`
no primeiro byte do arquivo por \`<!-- override-local: true -->\`. Skill
PRESERVA esse arquivo em re-sync futuro.
EOF

# 5) Atualizar .vault-architect.yml
# (via yq ou append cuidadoso — pseudocódigo)
yq -i ".operador_library_snapshot.path = \"$SRC\"" "$VAULT_PATH/.vault-architect.yml"
yq -i ".operador_library_snapshot.copied_at = \"$DATA_HOJE\"" "$VAULT_PATH/.vault-architect.yml"
yq -i ".operador_library_snapshot.arquivos_count = $(find $DEST -type f | wc -l)" "$VAULT_PATH/.vault-architect.yml"

echo "✅ 00-sistema populada com $(find $DEST -type f | wc -l) arquivos copiados de $SRC"
```

---

## Diff visual

Em `re-sync-operador`, skill apresenta plano via símbolos canônicos:

```
[vault-architect re-sync-operador] Plano de reconciliação 00-sistema/

Path origem: ~/.claude/growth-ia-ops/operador/
Snapshot anterior: 2026-05-08 (via copied_at em .vault-architect.yml)
Estado atual biblioteca shared: 2026-05-09 (1 dia de diff)

  ~ identidade.md                                  (atualizar — 4 linhas adicionadas: §Equipe core)
  ~ integrations/crm-mcp.yml                       (atualizar — tipo: pendente → tipo: multi)
  ! assinatura.html                                (PRESERVAR — override-local: true detectado)
  + design-system-references/novos-12-ds.md        (adicionar — arquivo novo na biblioteca)
  - 99-arquivo/00-sistema-removidos-2026-05-09/old-stuff.md  (arquivar — não-existe mais na biblioteca)

Total: 2 atualizar, 1 preservar (override), 1 adicionar, 1 arquivar
Aprovar? (sim / aprovar exceto: <ids> / cancelar)
```

---

## Validações

Regras adicionadas a `references/rules-catalog.md` sob prefixo **SI*** (00-sistema/):

| ID | Regra | Severidade | Auto-fix |
|---|---|---|---|
| SI001 | `<vault>/00-sistema/` ausente quando `--operador-library-path` foi provido | error | manual (re-rodar bootstrap ou retrofit re-sync-operador) |
| SI002 | `<vault>/00-sistema/identidade.md` parse-quebrado (frontmatter inválido) | error | manual (operador investiga biblioteca shared origem) |
| SI003 | `<vault>/00-sistema/design-system.css` parse-quebrado (chaves desbalanceadas) | error | auto-fix se diff trivial vs biblioteca shared atual |
| SI004 | `.vault-architect.yml` sem campo `operador_library_snapshot` | warning | auto-fix (insere stub vazio) |
| SI005 | Arquivo em `00-sistema/` sem marcador origem nem override (ambíguo) | warning | manual (operador define qual marcador aplicar) |
| SI006 | Drift detectado entre `<vault>/00-sistema/X.md` e `~/.claude/growth-ia-ops/operador/X.md` (sem override-local) | info | auto-fix via re-sync-operador |
| SI007 | `<vault>/00-sistema/_readme.md` ausente | warning | auto-fix (re-cria via template) |

---

## Edge cases

| Cenário | Comportamento |
|---|---|
| Operador edita `00-sistema/identidade.md` direto no vault sem marcar override | re-sync detecta diff sem override-local → apresenta como ambíguo (regra SI005) → operador decide preservar ou descartar |
| Biblioteca shared atualiza arquivo X.md mas operador adiciona override-local em X.md no vault depois do bootstrap | re-sync preserva override-local; reporta no diff |
| Cliente é assumido por outro operador ano-2 com identidade visual diferente | Recomendação: novo operador roda `operador-onboarding inicial` (sua biblioteca shared própria) → roda `vault-architect retrofit re-sync-operador --operador-library-path=<sua-lib>` no vault. `00-sistema/` migra de uma identidade pra outra. Operação válida e documentada. |
| Operador renomeia arquivo na biblioteca shared (ex: `tese-growth-ia-ops-resumida.md` → `tese-resumida.md`) | re-sync detecta `tese-growth-ia-ops-resumida.md` ausente na biblioteca → marca pra arquivar; detecta `tese-resumida.md` novo → marca pra adicionar. Operador valida no diff. |
| Bootstrap em CI/CD sem stdin (operador humano ausente pra ratificar) | Skill aceita flag `--operador-library-path-ci=skip-prompt` que assume `null` automaticamente em ambiente CI. Documentado pra automação. |
| Re-sync com biblioteca shared corrompida (CSS inválido pós-edit do operador) | Skill recusa apply (regra SI003 blocker) + aponta arquivo problemático na biblioteca shared. Operador conserta lá antes de re-rodar. |
| Cópia tenta tocar arquivo write-protected no vault (ex: rede compartilhada) | Skill aborta + reporta path problemático + sugere `chmod`/permissão. Não-mascarado. |

---

## Métricas de saúde

| Métrica | Meta | Como medir |
|---|---|---|
| Cobertura `00-sistema/` em vaults novos | 100% (sempre populada com biblioteca shared real ou placeholder) | Audit cross-vault checa V19 (biblioteca shared populada) + SI001 |
| Drift cross-vault detectado e ressincronizado por trimestre | ≥80% dos vaults ativos rodam re-sync trimestralmente | `historico_resync` em cada `.vault-architect.yml` |
| Overrides locais preservados corretamente em re-sync | 100% (zero perda de customização operador) | Smoke test E2E pré-release |
| Tempo médio de re-sync (escopo `completo`) | <30s pra biblioteca de 60 arquivos | Logs internos |

---

## Referências

- [`SKILL.md` § Bootstrap → "Cópia da biblioteca shared do operador"](../SKILL.md)
- [`SKILL.md` § Retrofit → tipo `re-sync-operador`](../SKILL.md)
- [`rules-catalog.md` § SI*](rules-catalog.md)
- D-OPERADOR-1 (decisão âncora): `c:\...\Tese Growth IA Ops v2.0\arquitetura\decisoes-mcps-formatos.md`
- Setup Inicial do Operador (fase âncora): `c:\...\Tese Growth IA Ops v2.0\arquitetura\setup-inicial-operador.md`
- Skill produtora da biblioteca shared: `~/.claude/skills/_sistema/operador-onboarding/SKILL.md`
- Spec arquitetural completo §4.1 + §5.7: `c:\...\Tese Growth IA Ops v2.0\arquitetura\skills\setup\vault-architect.md`
