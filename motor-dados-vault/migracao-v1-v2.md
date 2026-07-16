# Playbook — Migração de vault v1 → dados-fonte 2.0 (brownfield)

> Roteiro canônico pra migrar um vault que JÁ TEM feed v1 (CSVs soltos na pasta) e
> monitor v1 vivo (gerador fazendo joins) pro padrão dados-fonte 2.0 — **sem quebrar a
> lógica específica do projeto e sem parar o monitor**. Referenciado pelas 3 skills da
> cadeia; qualquer uma que for chamada primeiro numa migração roteia pra cá.
> Greenfield (vault sem camada de dados) NÃO usa este playbook — usa os bootstraps normais.

## Princípios (invioláveis)

1. **A cadeia velha fica viva até a paridade ser provada.** Nenhum estágio v1 é desligado antes do substituto reproduzir os números dele. O gestor não pode abrir um monitor quebrado durante a migração.
2. **O v1 é a spec, não o inimigo.** A lógica específica do projeto (mês fiscal, BUs, `canais_meta`, fórmula de TCV, reconciliações, exceções) JÁ está codificada no gerador v1 + `contrato-cockpit.yml`. Migrar = **ler e extrair** essa semântica, nunca reescrever de cabeça — improvisar produz versão pior do que já existe escrito (mesma lição da âncora safra do Sigo).
3. **Golden test por estágio.** Cada passo fecha com diff contra baseline congelado: **zero ou explicado linha a linha, senão não avança**.
4. **Migração preserva; melhoria vem depois.** Mudança consciente de semântica durante a migração é proibida — ela contaminaria o golden test. Melhorias entram DEPOIS da paridade, como extensão normal, com `quebras_de_serie` declarada se mudar definição.
5. **Entrevista só pro que o v1 não codifica** (extensões de CRM, sentinela nova, budget por canal, pré/pós-pago). O que dá pra ler do código, lê do código e **confirma** com o operador.

## Sequência (1 sessão por vault; handoff entre as 3 skills)

| Passo | Skill executora | Entrega | Gate de saída (bloqueante) |
|---|---|---|---|
| 0. Levantamento + baseline | (sessão — antes de qualquer skill) | inventário + baseline congelado | números-âncora anotados |
| 1. Estrutura raw/ | `feed-planilha-vault` modo extensao | `raw/` + targets re-apontados | cadeia v1 regenera **idêntica** |
| 2. Contrato + motor | `motor-dados-vault` modo bootstrap (brownfield) | contrato (c/ bloco `receita:`) + `_transform.py` + derivados (fato · dim-criativo · qa-report · **baseline-metricas**) + config-financeiro (c/ `contrato_inicio`) | **golden test: derivado reproduz o monitor v1** |
| 3. Render v3 | `monitor-builder` modo monitor | gerador v1 → render-prep sobre `derivado/` | monitor novo = monitor v1 nos números |
| 4. Decomissão + cascata | (sessão) | joins mortos removidos, docs/memória atualizados | cadeia 2.0 roda ponta-a-ponta 1× |

### Passo 0 — Levantamento + baseline congelado (NÃO PULE)

1. **Inventário do vault**: quais CSVs o feed baixa (targets/tarefa agendada), qual gerador roda, `contrato-cockpit.yml`, `config-financeiro.csv` (v1), o que está no `.gitignore`.
2. **Mapa da semântica específica**: leia o gerador v1 inteiro e liste TODO join/derivação/exceção que ele faz (ex. Martins: aquisição×recompra, `DEALS` filtrável; Colina: mês fiscal 16→15, BUs híbridas, rateio de canal indireto, atribuição ao mês do lead; Sigo pré-2.0: reconciliação de resíduo). **Essa lista é a spec do Passo 2.**
3. **Congele o baseline**: `monitor.json` v1 no estado atual (copie pro scratchpad + anote o commit) e extraia os **números-âncora**: OKR da vigência, clientes/faturamento totais e por canal×mês, totais das telas core. É contra ISSO que os golden tests rodam.

### Passo 1 — `feed-planilha-vault` (extensao): estrutura raw/

- Crie `raw/`, mova os destinos dos targets pra `raw\<arquivo>.csv` no orquestrador do vault e **re-aponte os paths de leitura do gerador v1** pra `raw/` (mudança mecânica de path, zero lógica). Mantenha nomes de tarefa agendada (mover o `.ps1` re-apontaria a tarefa — não mova).
- ⚠️ `.ps1` é UTF-8 com BOM (R4) — re-assegure após editar.
- **Gate:** rode a cadeia 1×: `_download.log` com OK por aba e o **monitor v1 regenera idêntico** (mesmos números-âncora). Nada mudou pro gestor.

### Passo 2 — `motor-dados-vault` (bootstrap brownfield): contrato + transform

Igual ao bootstrap normal (Passos 0-5 do SKILL.md), com três diferenças brownfield:
- **A entrevista começa pela spec do Passo 0.2**: cada join/exceção do gerador v1 vira item do contrato (`joins_reconstruidos_no_motor`, âncoras, extensões) — confirme com o operador só o ambíguo.
- **`config-financeiro.yml`**: migre o `config-financeiro.csv` v1 pra blocos de vigência (o histórico mensal do CSV vira vigências; valores novos por entrevista). O loader do gerador mantém fallback CSV, então isso pode ser o último sub-passo.
- **Golden test contra o baseline do Passo 0.3** (não contra planilha): o `derivado/fato-*.csv` agregado tem que reproduzir os números-âncora do monitor v1 congelado. Diff zero ou explicado linha a linha (ex.: dedup do QA gate corrigindo dup que o v1 somava 2× é divergência EXPLICADA e desejável — documente no contrato/achados_qa).
- Plugue o estágio transform no orquestrador (R4/R12) — o gerador v1 continua rodando dos CSVs por enquanto; os dois convivem neste passo.

### Passo 3 — `monitor-builder` (modo monitor v3): gerador vira render-prep

- Refatore o gerador v1: joins/parsing saem (o que sobrou de semântica de RENDER fica — metas client-side, payload, telas), entra `load_fato()` sobre `derivado/` + import dos helpers do `_transform.py`.
- Blocos novos (`P.dim`/`P.brk`/`P.lib` e telas Criativos/Debriefing/Dimensões) **só se** o vault tiver extração flow — senão degradam vazios; a extração flow é extensão OPCIONAL pós-migração (`feed-planilha-vault`), não pré-requisito.
- **Gate:** monitor novo = monitor v1 nos números-âncora + validação browser (console limpo, filtros recalculam) + publicação OK.

### Passo 4 — Decomissão + cascata (sessão)

- Remova do gerador o código morto (joins v1), arquive CSVs soltos v1 que viraram `raw/` (git guarda; sem cópia datada).
- Cascata: `mapa.md` da dados-fonte + seção "Caminho canônico de DADOS" no `claude.md` do vault (copie o padrão do Sigo) + memória project-specific com as definições travadas.
- Se alguma divergência explicada do golden test muda leitura longitudinal → registre em `quebras_de_serie`.
- **Gate final:** cadeia 2.0 ponta-a-ponta 1× (feed→transform→render→publish) com OK por estágio no log.

## Anti-patterns da migração

- ❌ **Big-bang** (tudo num passo, cadeia velha desligada antes do diff zero) → gestor abre monitor quebrado; sem baseline não há prova de paridade.
- ❌ **"Aproveitar pra melhorar"** a semântica no meio da migração → contamina o golden test; melhoria é DEPOIS, com quebra de série declarada.
- ❌ **Reescrever de cabeça o que o gerador v1 já codifica** → a versão improvisada perde as exceções do projeto (mês fiscal, rateios). O v1 é a spec.
- ❌ **Pular o Passo 0** e "descobrir" a semântica durante o Passo 2 → entrevista vira adivinhação e o contrato nasce furado.
- ❌ **Exigir extração flow como pré-requisito** → é extensão opcional; a migração fecha sem ela (telas condicionais desligam sozinhas).
