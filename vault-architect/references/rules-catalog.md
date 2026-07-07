# Catálogo de Regras de Auditoria

> Reference da skill `vault-architect`. Carregado no pré-vôo dos 3 modos. **16 prefixos** × N regras × severidade × auto-fixabilidade.
>
> **v2.1.0 (D-OPERADOR-1)** — adicionado prefixo `SI*` cobrindo Categoria 9ª `00-sistema/` (cópia da biblioteca shared do operador).
>
> **v2.2.0 (Doutrina Sináptica)** — adicionados prefixos `MP*` (mapa.md por pasta), `TC*` (TOC navegável), `RS*` (Resumo 60s). Escopo `--escopo=MP,TC,RS` ativa o sub-modo `audit-mapa` (atalhos: `audit-mapa` / `audit-mapa --fix`). Spec completo dos 3 prefixos novos em [`audit-mapa-mode.md`](audit-mapa-mode.md).

Severidades: `info` / `warning` / `error`. Auto-fixabilidade: `auto` (transformação sintática segura) / `manual` (decisão humana). Mexer em prosa é sempre `manual`.

---

## FM* — Frontmatter de outputs operacionais (Categoria 6)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| FM001 | error | Arquivo em `50-operacao/operacional/` sem frontmatter de lifecycle (`output_id`, `output_type`, `workflow`, `nature`, `status`, `created`, `updated_at`) | manual |
| FM002 | warning | Frontmatter sem `output_id` único (UUID ou kebab-case) | manual |
| FM003 | warning | `status` fora do enum (`draft`/`review`/`approved`/`active`/`paused`/`killed`/`archived`) | auto se inferível |
| FM004 | warning | `nature` fora do enum (`standard`/`evergreen`/`efemero`) | manual |
| FM005 | info | `updated_at` mais antigo que `created` (relógio do sistema?) | manual |

## MOC* — `index.md` raiz e dashboards Dataview

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| MOC001 | warning | Query Dataview com sintaxe inválida | manual |
| MOC002 | warning | Query Dataview que referencia campo inexistente nos arquivos da categoria | manual |
| MOC003 | info | `index.md` sem dashboard pra alguma categoria 10-99 | manual |

## NM* — Nomenclatura de arquivos

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| NM001 | warning | Arquivo com acento ou cedilha (quebra portabilidade cross-OS) | manual |
| NM002 | info | Arquivo em `30-decisoes/` sem prefixo de data (`YYYY-MM-DD-`) quando não é doc canônico (`gtm-plan.md`, `plano-midia.md`, `forecasting.md`) | manual |
| NM003 | info | Arquivo em `40-comunicacoes/` fora do padrão `YYYY-MM-DD-evento/` | manual |
| NM004 | warning | Espaço em nome de arquivo (use kebab-case ou snake_case) | manual |

## VR* — Versionamento (`80-versoes/`)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| VR001 | warning | Salto de versão sem `changelog.md` correspondente | manual |
| VR002 | error | `_atual.md` aponta pra versão inexistente | auto |
| VR003 | warning | Manifest sem `version`/`sprint`/`drop`/`created_at`/`created_by` no frontmatter | auto se inferível |
| VR004 | info | Versão `vX.Y` sem `diff-from-vX.Y-1.md` | manual |

## CL* — `claude.md`

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| CL001 | warning | Invariantes desatualizadas vs. template canônico (rodar `retrofit` recomendado) | auto via retrofit |
| CL002 | warning | Slot declarado em template sem delimitadores `<!-- vault-architect:slot:NOME -->` no arquivo | manual |
| CL003 | error | `claude.md` ausente ou sem header `# Vault Growth IA Ops` | manual |
| CL004 | warning | Mapa de Outputs em `claude.md` divergente do esperado pelo template | auto via retrofit |

## AG* — `agents.md`

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| AG001 | warning | Skill citada em `claude.md` Mapa de Inputs ausente em `agents.md` | auto |
| AG002 | warning | Skill em `agents.md` com `{{status}}` placeholder sem substituição | manual |
| AG003 | info | Skill em `agents.md` com status `not-configured` há mais de 90 dias (descontinuar?) | manual |

## IX* — `index.md`

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| IX001 | error | Query Dataview que referencia pasta-categoria inexistente | manual |
| IX002 | warning | Atalhos por intenção desatualizados vs. template | auto via retrofit |

## GL* — `glossario.md`

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| GL001 | info | Termo do vocabulário canônico usado em outputs sem entrada no glossário | manual |
| GL002 | info | Entrada do glossário sem ocorrências em nenhum output (orfão) | manual |

## DUP* — Duplicação

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| DUP001 | warning | Bloco >50% duplicado entre 2 meta-docs estruturais | manual |
| DUP002 | info | Output operacional com texto >70% duplicado de outro output operacional | manual |

## LK* — Wikilinks

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| LK001 | warning | Wikilink `[[X]]` aponta pra arquivo inexistente | manual (pode ser TODO intencional) |
| LK002 | info | Wikilink com fragmento (`[[X#header]]`) onde header não existe | manual |
| LK003 | warning | Output em `10-fundacao/` sem nenhum wikilink de saída (output órfão de referências?) | manual |

## TG* — Tags

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| TG001 | warning | Tag fora da convenção canônica (`#pilar/`, `#suporte/`, `#fase/`, `#categoria/`, `#workflow/`, `#status/`, `#nature/`, `#sprint/`, `#drop/`) | manual |
| TG002 | error | Tag canônica com valor não-permitido (ex: `#pilar/operacao` em vez de `#pilar/oferta`) | manual |
| TG003 | info | Output em `50-operacao/` sem tag `#sprint/...` ou `#drop/...` | manual |

## SC* — Schema de output canônico

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| SC001 | error | Manifest v1.X sem `version`, `sprint` ou `drop` no frontmatter | auto se inferível do path |
| SC002 | warning | Decision Doc sem campos canônicos (`validade`, `dono`, `status`) | manual |
| SC003 | warning | Output operacional com path canônico mas tipo declarado diverge | manual |

## TK* — Ticker (id externo Flow MCP)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| TK001 | error | `.vault-architect.yml` sem `ticker:` ou ticker vazio | manual (bloqueia integrações Flow) |
| TK002 | warning | Ticker fora da convenção `[A-Z]{4}` (ex: 3 letras, com números, lowercase) | manual (operador confirma intenção) |
| TK003 | info | Ticker presente mas não citado em meta-docs (claude.md/agents.md) | auto via retrofit |

## SI* — `00-sistema/` (Categoria 9ª — Identidade do operador, D-OPERADOR-1)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| SI001 | error | `<vault>/00-sistema/` ausente quando `--operador-library-path` foi provido (não-`null`) no bootstrap | manual (re-rodar bootstrap ou retrofit re-sync-operador) |
| SI002 | error | `<vault>/00-sistema/identidade.md` ausente, vazio, ou frontmatter parse-quebrado (deveria espelhar biblioteca shared) | manual (operador investiga biblioteca shared origem) |
| SI003 | error | `<vault>/00-sistema/design-system.css` parse-quebrado (chaves desbalanceadas; deveria ser parse-able pelos `*-deck-builder`) | auto se diff trivial vs biblioteca shared atual |
| SI004 | warning | `.vault-architect.yml` sem campo `operador_library_snapshot` (path + copied_at + arquivos_count) | auto (insere stub vazio) |
| SI005 | warning | Arquivo `.md` em `<vault>/00-sistema/` sem marcador `<!-- copied-from-operator-library: ... -->` nem `<!-- override-local: true -->` no primeiro byte (origem ambígua — re-sync não-determinístico) | manual (operador define qual marcador aplicar) |
| SI006 | info | Drift detectado: `<vault>/00-sistema/X.md` ≠ `~/.claude/growth-ia-ops/operador/X.md` em arquivo SEM `override-local: true` (cópia desatualizada) | auto via retrofit re-sync-operador |
| SI007 | warning | `<vault>/00-sistema/_readme.md` ausente (deveria documentar origem snapshot + procedure re-sync) | auto (re-cria via template) |
| SI008 | warning | `<vault>/00-sistema/integrations/*.yml` com `tipo` fora dos enums permitidos D-MCP-16 (calls/whatsapp/crm/tasks/health-score) | manual |

## MP* — Mapa por pasta (Doutrina Sináptica v2.2.0)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| MP001 | error | Pasta sem `mapa.md` (todas as pastas do vault precisam de mapa, mesmo vazias) | auto (cria stub conforme [`mapa-md-spec.md`](mapa-md-spec.md)) |
| MP002 | warning | `mapa.md` com seções "Arquivos" ou "Subpastas" divergentes do `ls` real (faltando/sobrando entry) | auto (regenera as 2 seções; preserva seções humano-curadas) |
| MP003 | warning | `mapa.md` órfão (existe em pasta que não existe mais — pasta renomeada/movida manualmente) | manual (operador decide: deletar mapa órfão ou recriar pasta) |
| MP004 | warning | `mapa.md` sem frontmatter obrigatório (`name`, `description`, `categoria_pai`, `tipo: mapa-pasta`, `updated_at`) | auto (insere stub de frontmatter; `description` fica placeholder pra revisão) |
| MP005 | warning | `mapa.md` sem seção "Pasta-pai" (breadcrumb) OU com link `../mapa.md` quebrado | auto (insere/corrige breadcrumb) |
| MP006 | info | `mapa.md` sem seção "O que entra" / "O que NÃO entra" (contrato de pasta ausente) | manual (operador escreve critério; herda do meta-doc da categoria-pai quando aplicável) |

## TC* — TOC navegável (Doutrina Sináptica v2.2.0)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| TC001 | error | MD elegível (Cat 1/2/3/4/8 OU ≥100 linhas) sem seção `## TOC` no topo | auto (gera TOC parseando H2/H3) |
| TC002 | warning | `## TOC` presente mas links âncora vazios/malformados | auto (regenera) |
| TC003 | warning | TOC drift vs. headings reais (heading renomeado/adicionado/removido sem regenerar TOC) | auto (regenera) |
| TC004 | info | TOC com entries H4+ inflacionado (>3 níveis — vira ruído) | auto (poda pra H2/H3) |

## RS* — Resumo 60s (Doutrina Sináptica v2.2.0)

| ID | Severidade | Descrição | Auto-fix |
|---|---|---|---|
| RS001 | error | MD elegível (Cat 1/2/3/4/8 OU ≥100 linhas) sem seção `## Resumo 60s` | auto (insere stub `<!-- vault-architect:resumo-60s-stub -->` aguardando humano) |
| RS002 | warning | Resumo 60s presente mas fora do canônico (sem H2 `Resumo 60s`, ou tamanho fora de 1-3 parágrafos curtos) | manual (operador re-escreve seguindo [`toc-resumo-spec.md`](toc-resumo-spec.md)) |
| RS003 | warning | Stub `<!-- vault-architect:resumo-60s-stub -->` não-substituído há ≥30 dias | manual (alerta humano que stub precisa virar resumo real) |
| RS004 | warning | Resumo 60s contém anotação `<!-- resumo-pendente-revisao: ... -->` (cascata sinalizou que conteúdo mudou e resumo pode estar stale) | manual (revisão humana — anotação foi inserida pelo helper de cascata on-edit) |

---

## Política de auto-fix

Auto-fix limitado a transformações **sintáticas seguras**:

✅ Permitido:
- Adicionar campo de frontmatter ausente com valor default declarado.
- Atualizar `_atual.md` pra apontar pra versão correta.
- Adicionar entrada faltante em `agents.md` quando skill foi citada em `claude.md`.
- Reformatar tabela markdown com colunas desalinhadas.
- Padronizar quebras de linha / encoding.
- Substituir `claude.md` invariantes por nova versão do template (em `retrofit`).

❌ Proibido:
- Mexer em prosa de outputs operacionais ou evergreen (briefings, ICMs, planos).
- Renomear arquivo silenciosamente.
- Mudar wikilinks sem aprovação.
- Mexer em conteúdo de slots customizáveis (preserva sempre).

## Loop de feedback (quando > 10 achados)

Skill **obrigatoriamente** pergunta ao operador:
> "Algum desses achados é falso positivo legítimo no contexto deste projeto? Posso adicionar `disabled-rules` no frontmatter dos arquivos afetados ou `rule_overrides` no `.vault-architect.yml` global."

Operador responde:
- Lista de regras a desativar (ex: `disabled-rules: [GL001, NM002]`).
- Escopo (arquivo / pasta / global).

Skill aplica overrides → re-roda audit → mostra report enxuto.

## Estrutura de override no `.vault-architect.yml`

```yaml
rule_overrides:
  GL001:
    severity: info  # downgrade de warning pra info
  NM002:
    severity: ignored  # desabilita inteiro
disabled_rules:
  - DUP002  # globalmente desabilitada
```

Frontmatter de arquivo individual:

```yaml
disabled-rules: [GL001, LK001]  # apenas neste arquivo
```
