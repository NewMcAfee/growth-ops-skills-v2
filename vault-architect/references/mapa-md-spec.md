# Spec — `mapa.md` por pasta (Doutrina Sináptica v2.2.0)

> Reference da skill `vault-architect`. Define a estrutura canônica do `mapa.md` que toda pasta do vault Growth IA Ops v2.0 deve ter, mesmo se vazia.

---

## Princípio

Cada pasta do vault é um **nó sináptico**. O `mapa.md` é o índice local que permite ao agente navegar a pasta sem carregar conteúdo full dos arquivos dentro. Custo: ~50-200 tokens por `mapa.md` × N pastas vs. 2k-10k tokens de pasta inteira carregada.

Inspiração: Claude Code cascading CLAUDE.md, Backstage `catalog-info.yaml`, Diátaxis landing pages, monorepos com README per dir.

---

## Frontmatter obrigatório

```yaml
---
name: mapa-<slug-da-pasta>           # mapa-fundacao, mapa-snapshots, mapa-versoes-v1-0, etc.
description: Mapa local da pasta <path-relativo>. <Função sintetizada em 1 linha.>
categoria_pai: <id-categoria>        # 1, 2, 3, 4, 6, 7, 8, 9 (categorias canônicas) OR "sistema" pra raiz
tipo: mapa-pasta                     # invariante — marca que é mapa, não output
updated_at: <YYYY-MM-DD>             # data da última cascata
---
```

`name` segue convenção kebab-case com prefixo `mapa-`. `categoria_pai` herda da pasta-pai imediata (mapa de subpasta dentro de `30-decisoes/` tem `categoria_pai: 3`).

---

## 7 seções obrigatórias (na ordem)

### 1. Resumo 60s da pasta

1 parágrafo curto (3-6 linhas) cobrindo:
- O que a pasta contém em essência.
- A quem serve (qual fase / cadência / cerimônia).
- Quando o agente deve abrir essa pasta vs. quando deve ler só este `mapa.md`.

Exemplo:

> Pasta da Categoria 1 (Estado Evergreen). Contém os outputs perenes da Fundação que descrevem identidade do cliente — Brand Core, ICM, Product Position, Copy System, Design System, BPMN Bowtie, Sistema de Qualificação, Measurement Plan e Contrato de Dados. Consumida por TODAS as skills downstream da Fase 2+ e por toda cerimônia trimestral do Loop. Abre só se a tarefa pede leitura literal de um desses outputs; pra navegar a estrutura, basta este mapa.

### 2. O que entra

Critério positivo de inclusão. Lista bullet curta (3-7 itens), cada item nomeando tipo de output OU padrão de naming OU regra estrutural.

Exemplo:

```markdown
## O que entra

- Outputs canônicos de Fundação com `nature: evergreen` (versionados via Git, vivem aqui pra sempre).
- Arquivos com path canônico declarado no `claude.md` Mapa de Outputs (ex: `icm.md`, `brand-core.md`, `taxonomia.{md,yml}`).
- Pacotes dual-format MD+YAML quando o output exige consumo humano + máquina (taxonomia, measurement-plan, contrato-de-dados).
```

### 3. O que NÃO entra

Critério negativo — delimita escopo e previne drift de categoria. Lista bullet com redirect explícito quando aplicável.

Exemplo:

```markdown
## O que NÃO entra

- Snapshots periódicos (Diagnóstico de Maturidade, Cenário Baseline, Relatório de Mercado) → vão em `20-snapshots/YYYY-MM/`.
- Decisões com validade temporal (GTM Plan, Plano de Mídia, Forecasting) → vão em `30-decisoes/`.
- Material cliente-facing cerimonial → vão em `40-comunicacoes/YYYY-MM-DD-evento/`.
- Identidade do operador (DS, assinatura, tese) → vai em `00-sistema/` (Princípio 11 multi-tenant — operador ≠ cliente).
```

### 4. Subpastas

Tabela markdown lista cada subpasta direta com link relativo + 1 linha de hook (extraído do `description` do `mapa.md` da subpasta).

Exemplo:

```markdown
## Subpastas

| Subpasta | Hook |
|---|---|
| [`v0.0/`](v0.0/mapa.md) | Manifest placeholder pré-baseline (vault-architect bootstrap) |
| [`v1.0/`](v1.0/mapa.md) | Manifest baseline ratificado pós-Apresentação cerimonial |
| [`v2.0/`](v2.0/mapa.md) | Manifest sprint Q1 pós-primeiro Loop trimestral |
```

Se a pasta não tem subpastas, mantém a seção mas escreve:

```markdown
## Subpastas

_Sem subpastas._
```

### 5. Arquivos

Tabela markdown lista cada arquivo direto (não-recursivo) com link relativo + 1 linha de hook (extraído do `description` do frontmatter quando existe; default genérico se ausente).

Exemplo:

```markdown
## Arquivos

| Arquivo | Hook |
|---|---|
| [`brand-core.md`](brand-core.md) | Brand Core ratificado — propósito, princípios, arquétipo, tom de voz, posicionamento |
| [`icm.md`](icm.md) | Ideal Customer Map — comitê de decisão Forrester + Anti-ICP + Champion identification |
| [`product-position.md`](product-position.md) | Proposta Única de Valor + Oferta de Ativação (PUV+OA) |
| [`measurement-plan.md`](measurement-plan.md) | Plano de mensuração — eventos × destinos × EMQ alvo |
| [`measurement-plan.yml`](measurement-plan.yml) | YAML máquina pareado com measurement-plan.md (consumo família tracking-* + IE v2) |
```

Se a pasta está vazia (só tem `mapa.md`):

```markdown
## Arquivos

_Pasta vazia — contrato em aberto. Aguardando primeiro output conforme "O que entra"._
```

### 6. Pasta-pai (breadcrumb)

Link reverso pro `mapa.md` ancestral. Sempre presente — exceto na raiz do vault (que aponta pra `claude.md` em vez de `mapa.md`).

Exemplo:

```markdown
## Pasta-pai

↑ [`../mapa.md`](../mapa.md) — Vault raiz
```

Pra raiz do vault:

```markdown
## Pasta-pai

↑ [`claude.md`](claude.md) — Reference doc do vault
```

### 7. Última cascata

Linha curta no rodapé documentando data + skill/agente que rodou a cascata. Permite audit de drift.

Exemplo:

```markdown
---

_Última cascata: 2026-05-24 por `vault-architect atualiza-cascata`._
```

---

## Mapa em pasta vazia — protocolo

Pasta criada mas ainda sem outputs (ex: `20-snapshots/` recém-bootstrapped, ou `60-loops/storms/2026-W21/` criada antecipando growthstorming). Mapa **ainda é obrigatório** — funciona como **contrato de o que entra**, sinaliza ao agente que a pasta é parte oficial do vault, e previne que skills downstream criem arquivos no path errado por "não saber".

Pasta vazia herda "O que entra" e "O que NÃO entra" do meta-doc da categoria-pai. Seções "Subpastas" e "Arquivos" ficam com placeholder `_Sem ... — contrato em aberto._`.

---

## Mapa em pasta dinâmica (`20-snapshots/YYYY-MM/`, `40-comunicacoes/YYYY-MM-DD-evento/`)

Pastas com naming dinâmico (date-stamped, event-stamped) recebem `mapa.md` na criação da pasta específica. A pasta-pai (ex: `20-snapshots/`) lista as subpastas datadas via seção "Subpastas" atualizada por cascata sempre que nova subpasta nasce.

Exemplo de `20-snapshots/2026-05/mapa.md`:

```yaml
---
name: mapa-snapshots-2026-05
description: Snapshots periódicos produzidos em maio de 2026 (Fundação inicial + recalibragens cond.).
categoria_pai: 2
tipo: mapa-pasta
updated_at: 2026-05-24
---
```

---

## Anti-patterns

- ❌ Mapa.md sem frontmatter — quebra parser de `mapa-md-spec`.
- ❌ Lista de arquivos manualmente curada e desatualizada — sempre derivar do `ls` real via cascata.
- ❌ Hook genérico copy-paste em todos arquivos ("Output canônico") — extrair do `description` do frontmatter do arquivo destino.
- ❌ Resumo 60s da pasta replicando conteúdo de arquivos individuais — resumo é da PASTA, não dos arquivos.
- ❌ Misturar critério "O que entra" / "O que NÃO entra" na mesma lista — separar em 2 seções pra clareza.
- ❌ Pular criação de mapa em pasta vazia — anula o contrato e quebra walk-up de cascata.
- ❌ Mapa.md com TOC ou Resumo 60s no estilo de output (esses pertencem a arquivos MD substantivos, não a mapas — mapa já é índice por natureza).
