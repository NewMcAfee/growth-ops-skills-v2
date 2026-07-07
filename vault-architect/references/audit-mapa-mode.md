# Spec — Modo `audit-mapa` / sub-modo de Otimização (v2.2.0)

> Reference da skill `vault-architect`. Detalha o modo de auditoria sináptica que detecta drift entre `mapa.md` / TOC / Resumo 60s e o estado real do vault.

---

## Posicionamento

`audit-mapa` é **sub-modo do modo `otimização`** (Fase 1 audit + Fase 2 apply). NÃO é modo novo standalone — herda toda a infra de severidade/auto-fix/loop-de-feedback do modo otimização. Apenas restringe escopo aos prefixos sinápticos: **MP** (Mapa per-folder), **TC** (TOC navegável), **RS** (Resumo 60s).

Invocação canônica:

```
vault-architect otimização --escopo=MP,TC,RS
vault-architect otimização --escopo=MP,TC,RS --aplicar_auto_fix=true
```

Atalho semântico equivalente:

```
vault-architect audit-mapa
vault-architect audit-mapa --fix
```

Atalho expande pra forma canônica internamente.

---

## O que o sub-modo varre

### MP — Mapa per-folder (4 regras canônicas)

| ID | Detecta | Severidade | Auto-fix |
|---|---|---|---|
| **MP001** | Pasta sem `mapa.md` | error | auto (cria stub conforme `references/mapa-md-spec.md`) |
| **MP002** | `mapa.md` com listagem de "Arquivos" divergente do `ls` real (faltando/sobrando entry) | warning | auto (regenera seção "Arquivos" + "Subpastas") |
| **MP003** | `mapa.md` órfão (existe em pasta que não existe mais — ex: pasta renomeada manualmente) | warning | manual (operador decide: deletar mapa órfão ou recriar pasta) |
| **MP004** | `mapa.md` sem frontmatter obrigatório (`name`, `description`, `categoria_pai`, `tipo: mapa-pasta`, `updated_at`) | warning | auto (insere stub de frontmatter com inferências sensatas; `description` fica como placeholder pra revisão humana) |
| **MP005** | `mapa.md` sem seção "Pasta-pai" (breadcrumb) OU com link `../mapa.md` quebrado | warning | auto (insere/corrige breadcrumb) |
| **MP006** | `mapa.md` sem seção "O que entra" / "O que NÃO entra" (contrato de pasta ausente) | info | manual (operador escreve critério; herda do meta-doc da categoria-pai se aplicável) |

### TC — TOC navegável (3 regras canônicas)

| ID | Detecta | Severidade | Auto-fix |
|---|---|---|---|
| **TC001** | MD elegível (Cat 1/2/3/4/8 OU ≥100 linhas) sem seção `## TOC` no topo | error | auto (gera TOC parseando headings H2/H3) |
| **TC002** | MD com `## TOC` presente mas links âncora vazios/malformados | warning | auto (regenera) |
| **TC003** | TOC presente mas drift vs. headings reais (heading foi renomeado/adicionado/removido sem regenerar TOC) | warning | auto (regenera) |
| **TC004** | TOC com entries H4+ inflacionado (>3 níveis) | info | auto (poda pra H2/H3) |

### RS — Resumo 60s (3 regras canônicas)

| ID | Detecta | Severidade | Auto-fix |
|---|---|---|---|
| **RS001** | MD elegível (Cat 1/2/3/4/8 OU ≥100 linhas) sem seção `## Resumo 60s` | error | auto (insere stub `<!-- vault-architect:resumo-60s-stub -->` aguardando humano) |
| **RS002** | Resumo 60s presente mas em formato fora do canônico (sem H2 `Resumo 60s`, ou tamanho fora de 1-3 parágrafos) | warning | manual (operador re-escreve seguindo spec) |
| **RS003** | Stub `<!-- vault-architect:resumo-60s-stub -->` não-substituído há ≥30 dias | warning | manual (alerta humano que stub precisa virar resumo real) |
| **RS004** | Resumo 60s contém anotação `<!-- resumo-pendente-revisao: ... -->` (cascata sinalizou que conteúdo mudou e resumo pode estar stale) | warning | manual (revisão humana — anotação foi inserida pela cascata on-edit) |

---

## Fluxo do sub-modo

Idêntico ao modo `otimização` canônico, com escopo restrito:

### Fase 1 — Audit Report (sempre)

1. Pré-vôo: validar vault Growth IA Ops v2.0 (`claude.md` raiz menciona "Growth IA Ops v2.0").
2. Walk recursivo da árvore do vault (excluindo `.git/`, `.obsidian/`, `node_modules/`).
3. Pra cada pasta encontrada: aplicar regras MP001-MP006.
4. Pra cada arquivo `.md` encontrado: classificar elegibilidade (Cat 1/2/3/4/8 OU ≥100 linhas?) → se elegível, aplicar TC001-TC004 + RS001-RS004.
5. Renderizar Audit Report no formato canônico de `audit-report-template.md`, agrupado por severidade + auto-fixabilidade + path.

### Fase 2 — Apply (opcional, com `--aplicar_auto_fix=true` ou `aprovar [ids]`)

1. Pra cada achado **auto-fixável** aprovado:
   - Gera diff, mostra ao operador, aplica via `Edit` ou `Write`.
   - MP001 (criar mapa.md ausente) usa template canônico de `references/mapa-md-spec.md`.
   - MP002 (regenerar listagem) preserva texto livre nas seções "Resumo 60s da pasta" / "O que entra" / "O que NÃO entra" (essas são humano-curadas; só atualiza "Subpastas" e "Arquivos").
   - TC001/TC002/TC003 (regenerar TOC) preserva conteúdo do Resumo 60s (não toca seção `## Resumo 60s`).
   - RS001 (inserir stub) NÃO substitui resumo já escrito — só insere se ausente.
2. Pra cada achado **manual**: lista no relatório com sugestão de ação, mas não aplica.
3. Re-roda audit pós-apply. Se introduziu nova divergência (raro mas possível com regeneração de TOC em MD malformado), **reverte automaticamente** o último apply.
4. Atualiza `CHANGELOG.md` raiz + `.vault-architect.yml` (`historico_otimizacao`).
5. Stage Git (`git add` dos arquivos tocados) + propõe mensagem `chore(audit-mapa): aplica {{N}} correções sinápticas`.

---

## Loop de feedback (anti alert fatigue)

Modo otimização canônico já tem loop quando >10 achados. Pra audit-mapa especificamente, é comum o **primeiro** audit retornar 50-200 achados (vault pré-v2.2.0 não tem mapas/TOCs). Comportamento esperado nessa primeira passada:

1. Skill reporta total + agrupa por tipo (X MP001 + Y TC001 + Z RS001) + pergunta:
   > "Primeira execução de audit-mapa neste vault. Esperado encontrar muitos achados de inicialização. Quer aplicar **todos** os MP001+TC001+RS001 em batch? Esses são criação/inserção de stubs sem perda de conteúdo. RS001 deixa resumos como stub pra humano preencher depois."

2. Operador responde `aprovar all-init` → skill cria mapas em todas pastas + insere TOCs + insere stubs de Resumo 60s + commita como `chore(audit-mapa): inicialização sináptica v2.2.0`.

3. Audits seguintes (cadência trimestral recomendada) retornam só drift incremental — handling normal.

---

## Cadência recomendada

- **On-edit (sempre)**: cascata automática via helper `atualiza-cascata` chamado pela skill que escreveu o output. NÃO é audit-mapa — é prevenção. Audit-mapa é o catch-all pra drift que escapou.
- **Trimestral**: `vault-architect otimização --escopo=MP,TC,RS --aplicar_auto_fix=true` no início do Loop trimestral (cadência canônica Fase 3). Pega drift acumulado.
- **Pré-cerimônia**: rodar antes de Apresentação (Subfase 1.5.3), QBR (F3), Sprint Review (F3) — garante que material cliente-facing tem navegação limpa.
- **Pós-batch grande**: depois de ondas grandes de criação manual (ex: bootstrap + Onda 1 Fundação rodada em batch), rodar pra normalizar.

---

## Anti-patterns

- ❌ Rodar `audit-mapa --fix` sem ter rodado audit read-only antes (sempre Fase 1 → revisar → Fase 2).
- ❌ Aceitar RS001 batch sem nunca voltar pra preencher os stubs (RS003 detecta isso ≥30 dias, mas vale curadoria proativa).
- ❌ Misturar regras MP/TC/RS com regras core (FM/CL/AG/etc.) no mesmo audit grande — separar escopo facilita revisão.
- ❌ Auto-fixar MP003 (mapa órfão) — sempre manual, porque pode indicar pasta movida vs. pasta deletada e a ação correta difere.
