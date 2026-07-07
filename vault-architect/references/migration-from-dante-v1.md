# Política de Migração — Dante v1 → Growth IA Ops v2.0

> Reference da skill `vault-architect`. Carregado quando routing detecta vault Dante v1 OU operador invoca migração explicitamente.

**Decisão arquitetural fechada (B1.3):** **NÃO** existe 4º modo nominal `migrate-from-dante-v1`. Migração é operação **one-off por projeto legado**, conduzida pelo operador, com a skill atuando como **executora competente guiada por playbook explícito em contexto**.

---

## Por que não é modo nominal

- Dante v1 é deprecado integralmente. Não há "compatibilidade dupla" como recurso permanente.
- Migração é tarefa pontual: cada projeto legado migra **uma única vez**. Volume esperado: ≤5 projetos.
- Mapear `00_Governanca` → `40-comunicacoes/` ou `30-decisoes/` ou `70-memoria/` exige **juízo humano** (depende do conteúdo de cada arquivo). Skill genérica nunca fará bem.
- Mas a skill tem **ferramental certo** (Read/Edit/Write/Glob/Grep/Bash) e domínio do destino (sabe Growth IA Ops v2.0 de cor). Recusar a operar é desperdício.

**Equilíbrio:** playbook é o contrato (descreve mapeamento canônico + decisões arquiteturais); skill é a executora (aplica passo a passo com aprovação humana).

---

## Detecção de Dante v1

Skill detecta no pré-vôo do routing state-based (`vault-architect SKILL.md` § Routing):

**Heurística canônica:**
- Pasta-alvo tem `AGENTS.md` (maiúsculo) na raiz.
- 9 pastas numeradas no padrão `00_Governanca`, `01_Estrategia`, `02_Marca-e-Design`, `03_Midia-Paga`, `04_Criativos-e-Producao`, `05_Produto-e-Prototipacao`, `06_Funil-e-Comercial`, `07_Performance-e-Relatorios`, `08_Memoria-e-Aprendizados`.
- Ausência de `claude.md` (minúsculo) com referência a "Growth IA Ops v2.0".

Combinação dos 3 critérios → Dante v1 confirmado.

---

## Comportamento da skill ao detectar Dante v1 SEM playbook em contexto

**Recusa explícita:**

```
[vault-architect] Recusa: vault Dante v1 detectado em {{path}}.

Dante v1 está deprecado a partir do Growth IA Ops v2.0. A operação canônica
(bootstrap/retrofit/otimização) não suporta esse padrão.

Para migrar:
  → produza ou localize `arquitetura/playbook-migracao-dante-v1.md`.
  → invoque novamente a skill referenciando o playbook explicitamente:
    "vault-architect, lê o playbook em <path> e migra esse Dante v1 pra v2."

Para descartar e começar do zero:
  → mova {{path}} pra {{path}}-dante-v1-arquivado.
  → rode `vault-architect bootstrap path: {{path}} ...` em pasta limpa.
```

Skill **não** prossegue mesmo se operador insistir — exige referência explícita ao playbook.

---

## Comportamento da skill ao detectar Dante v1 COM playbook em contexto

Skill **não recusa**. Sequência:

1. **Lê o playbook integralmente** (`arquitetura/playbook-migracao-dante-v1.md` ou path declarado pelo operador).
2. **Adota o playbook como contrato operacional** dessa execução. O playbook É a fonte canônica do mapeamento; o doc desta skill descreve operação canônica, não migração.
3. **Confirma intenção com o operador** antes de começar:
   ```
   [vault-architect] Detectei Dante v1 em {{path}} + playbook em {{playbook_path}}.
   
   Vou conduzir migração guiada conforme o playbook:
   - Inventário do vault Dante v1 (~{{N}} arquivos substantivos detectados)
   - Bootstrap pasta paralela em {{path}}-v2/ (Growth IA Ops v2.0)
   - Migração arquivo a arquivo com aprovação humana (lote por categoria autorizado se você OK)
   - Preservação do original em 99-arquivo/dante-v1-original/ no vault novo
   
   Estimativa: 2-4 horas de operação assistida. Confirma proceder? (sim/não/ajustes)
   ```
4. **Executa o playbook passo a passo:**
   - Inventaria o vault Dante v1.
   - Para cada arquivo, propõe destino canônico Growth IA Ops v2.0 conforme regras do playbook.
   - **Aprovação humana arquivo a arquivo** (ou em lote por categoria, se operador autorizar).
   - Aplica `bootstrap` em pasta paralela (`{{path}}-v2/`) na primeira fase.
   - Migra cada arquivo aprovado pra path canônico no vault novo.
   - Preserva original em `99-arquivo/dante-v1-original/` no vault novo.
5. **Ao final:** vault novo está em estado Growth IA Ops v2.0; daí em diante segue os 3 modos canônicos (bootstrap não roda mais nesse projeto; retrofit/otimização sim).

---

## Tabela de mapeamento canônico (referência)

Detalhamento completo no playbook. Resumo:

| Camada Dante v1 | Categoria Growth IA Ops v2.0 | Critério |
|---|---|---|
| `00_Governanca/briefings/*` | `10-fundacao/briefing-inicial.md` (curado) | Estado evergreen |
| `00_Governanca/atas/*` | `70-memoria/YYYY-MM-DD-evento/curadoria.md` | Memória de interação |
| `00_Governanca/manual-estrategico/*` | `30-decisoes/gtm-plan.md` + `30-decisoes/plano-midia.md` + `20-snapshots/YYYY-MM/cenario-baseline.md` | Decompor por tipo |
| `01_Estrategia/icp-e-posicionamento/*` | `10-fundacao/icm.md` + `10-fundacao/product-position.md` + `10-fundacao/icp-product-map.md` | Estado evergreen |
| `01_Estrategia/inteligencia-mercado/*` | `20-snapshots/YYYY-MM/relatorio-mercado.md` | Snapshot |
| `01_Estrategia/puv-e-ofertas/*` | `10-fundacao/product-position.md` | Estado evergreen |
| `02_Marca-e-Design/brand-core/*` | `10-fundacao/brand-core.md` + `10-fundacao/copy-system.md` + `10-fundacao/direcao-arte.md` | Estado evergreen (decompor) |
| `03_Midia-Paga/planos/*` | `30-decisoes/plano-midia.md` + `30-decisoes/forecasting.md` | Decisão em vigor |
| `03_Midia-Paga/campanhas/*` | `50-operacao/operacional/aquisicao/paga/sprint-XXX/drop-YYY/` | Output operacional |
| `04_Criativos-e-Producao/*` | `50-operacao/operacional/aquisicao/paga/sprint-XXX/drop-YYY/{lp,ad,email}-*` | Output operacional |
| `05_Produto-e-Prototipacao/*` | `90-referencias/` (referência externa curada) ou `99-arquivo/` | Curadoria |
| `06_Funil-e-Comercial/*` | `10-fundacao/bpmn-bowtie.md` + `10-fundacao/sistema-qualificacao.md` + `10-fundacao/playbook-comercial.md` + `10-fundacao/sla.md` | Estado evergreen (decompor) |
| `07_Performance-e-Relatorios/*` | `20-snapshots/YYYY-MM/performance-{sprint,drop}.md` | Snapshot |
| `08_Memoria-e-Aprendizados/Truths-and-Traps.md` | Múltiplos `30-decisoes/YYYY-MM-DD-titulo.md` | **Desestruturar em Decision Docs individuais** |

---

## Princípios da migração (do playbook)

1. **Preservação do original.** Dante v1 inteiro fica em `99-arquivo/dante-v1-original/` no vault novo. Nada apagado.
2. **Curadoria, não conversão automática.** Skill não migra cega — propõe destino, operador aprova.
3. **Vocabulário canônico.** Todo conteúdo migrado é reformatado pra vocabulário Growth IA Ops v2.0 quando aplicável.
4. **Estado vivo vs. snapshot histórico.** Conteúdo Dante v1 muitas vezes mistura — operador decide caso a caso.
5. **Wikilinks são frágeis.** Skill lista links afetados antes de cada mudança. Nunca renomeia silenciosamente.
6. **Pillars-Health não existia.** Vault novo começa com 4 pilares `desconhecido`. Primeiro Diagnóstico de Maturidade pós-migração estabelece baseline.
7. **Cliente multi-BU (B3b) → 1 vault consolidado, fundação híbrida.** Vault Dante B3b (holding + N sub-vaults BU aninhados) NÃO vira N vaults nem holding aninhado: consolida em **1 vault v2.0** com fundação híbrida — `brand-core`+`copy-system` **unified** (1 por marca-mãe, princípio `campbell`); `icm`/`product-position`/`design-system` **per-BU** com sufixo `-<bu>` (princípio `michelangelo`/`da-vinci`); `contexto.md` guarda-chuva apontando pros per-BU. BU via tag `bu/*` + sufixo, não por pasta. Cada nó Dante preservado em `99-arquivo/dante-v1-original/<no>/`. Detalhe operacional no playbook **§9.9**. Validado no Grupo SA 2026-06-29 (3 BUs).

---

## Pré-requisitos pra migração

1. **Ticker do projeto no Flow** disponível.
2. **Cliente_nome canônico** decidido (slug kebab-case).
3. **Path do vault Dante v1** atual.
4. **Path destino do vault v2** decidido (recomenda mesmo path, com Dante v1 movido pra `_dante-v1-original/` no final).
5. **`git status` do vault Dante v1 limpo** (sem mudanças não-commitadas).
6. **Backup** (tag Git `pre-migracao-{{data}}`).
7. **Operador disponível** pra revisar arquivo a arquivo (ou autorizar lote).

---

## Quando NÃO usar o fluxo de migração

- Vault legado não é Dante v1 (estrutura ad-hoc, pasta plana, outro framework). Caso típico: cliente em pasta plana com docs soltos. Não tem o que migrar; é **bootstrap puro** com extração curada do conteúdo plano pra `10-fundacao/briefing-inicial.md`.
- Projeto está encerrado/arquivado — sem ROI em migrar.
- Operador quer descartar trabalho prévio e recomeçar do zero — usa `bootstrap` em pasta limpa direto.
- Volume é trivial (<10 arquivos substantivos) — copia manualmente.

---

## Iteração futura

Playbook v1.0.0 é fechado mas a primeira migração real (provavelmente Manchester ou Grupo Colina) deve gerar aprendizados. Operador agendará retrospectiva pós-primeira-migração que pode gerar playbook v1.1.0.

Localização canônica do playbook: `c:\Users\mcafe\OneDrive\Documentos\Claude\Projects\06_teses\Tese Growth IA Ops v2.0\arquitetura\playbook-migracao-dante-v1.md`.
