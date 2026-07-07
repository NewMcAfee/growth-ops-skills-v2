# Spec — TOC navegável + Resumo 60s em MDs (Doutrina Sináptica v2.2.0)

> Reference da skill `vault-architect`. Define quando TOC + Resumo 60s são obrigatórios em arquivos MD do vault e qual o formato canônico de cada um.

---

## Princípio

Arquivos longos ou estruturais do vault têm 2 elementos sinápticos no topo:

1. **TOC navegável** — bullet list com links âncora pras seções H2/H3 (não H4+ pra evitar ruído). Permite agente saltar pra seção específica sem ler do começo.
2. **Resumo 60s** — bloco "## Resumo 60s" com 1-3 parágrafos curtos cobrindo tese central + outputs + quando ler full vs. quando ler só o resumo.

Custo: ~50-150 tokens de overhead. Ganho: agente e humano decidem em <60s se precisam do conteúdo completo.

---

## Threshold canônico (quando é obrigatório)

| Critério | Obrigatoriedade |
|---|---|
| Arquivo de **Categoria 1 (Estado Evergreen)** — `10-fundacao/*.md` | **SEMPRE** obrigatório |
| Arquivo de **Categoria 2 (Snapshot)** — `20-snapshots/YYYY-MM/*.md` | **SEMPRE** obrigatório |
| Arquivo de **Categoria 3 (Decisão)** — `30-decisoes/*.md` | **SEMPRE** obrigatório |
| Arquivo de **Categoria 4 (Comunicação cerimonial)** — `40-comunicacoes/YYYY-MM-DD-evento/*.md` | **SEMPRE** obrigatório (cliente-facing — TOC ajuda navegação na apresentação) |
| Arquivo de **Categoria 8 (Manifest)** — `80-versoes/vX.Y/{manifest,changelog,diff-*}.md` | **SEMPRE** obrigatório |
| Qualquer outro MD com **≥100 linhas** | **OBRIGATÓRIO** |
| MD com <100 linhas que não seja Cat 1/2/3/4/8 | Opcional |
| Meta-docs estruturais curtos (`mapa.md`, `_readme.md`, `_index.md`) | **DISPENSADO** (são índices por natureza) |
| Templates em `_templates/` | **DISPENSADO** (são esqueletos) |
| Placeholders (`_evento.md`, `_atual.md` em `60-loops/`) | **DISPENSADO** |
| Configs YAML-only (`taxonomia.yml`, `measurement-plan.yml`, `contrato-de-dados.yml`) | **N/A** (não é MD) |

Limite de 100 linhas é heurística — arquivo de 95 linhas que claramente tem 5+ seções H2 também ganha TOC; usar bom-senso.

---

## Estrutura canônica no topo do MD

Logo após o frontmatter YAML, antes da primeira seção H2 substantiva:

```markdown
---
<frontmatter YAML>
---

# <Título H1 do documento>

## TOC

- [Resumo 60s](#resumo-60s)
- [Seção A](#seção-a)
  - [Sub A.1](#sub-a1)
  - [Sub A.2](#sub-a2)
- [Seção B](#seção-b)
  - [Sub B.1](#sub-b1)
- [Seção C](#seção-c)
- [Referências](#referências)

## Resumo 60s

<1-3 parágrafos curtos — tese central, outputs, quando ler full vs. só resumo>

## <Primeira seção substantiva>

...
```

---

## TOC — regras

- **Bullet list aninhada** refletindo hierarquia H2 → H3 do documento. Não incluir H4+ (vira ruído).
- **Links âncora** seguindo convenção GitHub-flavored markdown: lowercase, espaços viram `-`, acentos preservados, pontuação removida. Ex: `## Análise de Dados Históricos` → `[Análise de Dados Históricos](#análise-de-dados-históricos)`.
- **Não incluir o próprio TOC** no TOC (não aponta pra si).
- **Sempre incluir Resumo 60s** como primeiro item do TOC (após Resumo é que vem o conteúdo).
- **Ordem**: idêntica à ordem das seções no documento.

### Auto-geração

Helper canônico `vault-architect regenera-toc <path>` faz parse das seções H2/H3 e regenera. Re-executar após qualquer Edit que altere headings.

Drift comum: edição renomeia ou adiciona/remove H2 sem regenerar TOC. Audit pega via regra `TC003` (TOC drift vs. headings reais).

---

## Resumo 60s — regras

- **Tamanho**: 1-3 parágrafos curtos (~80-200 palavras total). Leitura em <60s por humano.
- **Conteúdo obrigatório**:
  1. **Tese central** do documento — qual é a afirmação/decisão/observação principal.
  2. **Outputs** — quais artefatos concretos o documento entrega ou consolida.
  3. **Quando ler full vs. resumo** — critério prático ("ler full se vai produzir handoff cross-fase X" / "resumo basta se está só navegando contexto").
- **Conteúdo proibido**:
  - Repetir literalmente seções do documento (resumo ≠ executive summary detalhado).
  - Citar números, métricas ou claims específicos (esses vivem no corpo — resumo é orientador).
  - Listar TOC em prosa (TOC já é seção própria acima).
- **Tom**: declarativo, presente. Não usar futuro ("este documento vai mostrar...") — usar presente ("este documento sustenta...").

### Exemplo canônico (Brand Core)

```markdown
## Resumo 60s

Brand Core do cliente X — documento perene de identidade estratégica em 5 pilares (Propósito,
Princípios, Arquétipo, Tom de Voz, Posicionamento). Produzido pela skill `campbell` na Subfase
1.2.3 da Fundação. Consumido por todas as skills downstream da Fase 2+ (família copy-*,
ad-design-*, post-design-*, lp-*, email-*) + skills cerimoniais (gtm-deck-builder + 4 outros
*-deck-builder) + auditorias trimestrais (account-curator modo apresentacao + qbr).

Ler full quando: (a) produzindo qualquer asset cliente-facing que precise carregar tom de voz e
posicionamento literais; (b) auditando consistência de brand cross-asset; (c) propondo
re-posicionamento ou pivot de arquétipo (Loop trimestral). Resumo basta quando: navegando
contexto, identificando upstream de outro output, ou confirmando que Brand Core está ratificado
no Manifest vigente.
```

### Stub quando ausente

Se um MD ≥100 linhas / Cat 1/2/3/4/8 NÃO tem Resumo 60s, o helper insere stub:

```markdown
## Resumo 60s

<!-- vault-architect:resumo-60s-stub -->
**Resumo pendente.** Este documento foi auto-detectado como elegível pra Resumo 60s mas ainda
não tem síntese escrita. Skill responsável pela produção (ver frontmatter `created_by`) deve
escrever resumo cobrindo: tese central, outputs, quando ler full vs. só resumo.
<!-- /vault-architect:resumo-60s-stub -->
```

Stub permanece até alguém (humano ou skill) substituir. Audit detecta via regra `RS003` (stub não-substituído ≥30 dias = warning).

---

## Anti-patterns

- ❌ TOC com H4+ inflacionado — vira ruído, prefira manter H2/H3 apenas.
- ❌ Resumo 60s que é cópia da intro do documento — resumo é orientador, intro é narrativa.
- ❌ Resumo 60s ≥5 parágrafos — vira executive summary, perde a função sináptica.
- ❌ Resumo 60s com números/claims específicos — esses pertencem ao corpo (resumo não é fonte de verdade).
- ❌ TOC manualmente curado e desatualizado — sempre regenerar via helper.
- ❌ Aplicar TOC/Resumo em `mapa.md`/`_readme.md` — esses são índices por natureza.
- ❌ Aplicar TOC/Resumo em template `_templates/*.md` — esses são esqueletos, não outputs.
- ❌ Aplicar TOC/Resumo em arquivo <100 linhas que não seja Cat 1/2/3/4/8 — overhead supera ganho.
