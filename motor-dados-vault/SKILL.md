---
name: motor-dados-vault
description: Instala, evolui e audita a camada de TRANSFORM da arquitetura dados-fonte 2.0 de um vault Growth IA Ops — dona do contrato de dados (contrato-dados-fonte.yml), do motor determinístico (_transform.py) e dos derivados (fato/dim-criativo/qa-report), com QA gates, âncora semântica provada por golden test, parser de taxonomia versionado e rateio de funil. Ative quando precisar criar a camada de dados num vault (bootstrap/replicação), adicionar derivado/coluna/gate por demanda de uma skill consumidora (feature request), ou auditar paridade/drift contrato↔realidade. NÃO ative para baixar dados/agendar cadeia (feed-planilha-vault), renderizar monitor (monitor-builder), crosswalk ad-hoc de exports avulsos fora de vault (kimball), nem analisar/interpretar dados (newton/darwin/falconi).
allowed-tools: Read,Write,Edit,Glob,Grep,Bash,PowerShell,AskUserQuestion
---

# motor-dados-vault — Engenheiro do Transform (dados-fonte 2.0)

## Contexto

Na arquitetura dados-fonte 2.0 (ELT), a planilha e os MCPs entregam só **bruto**; todo cruzamento, cálculo e enriquecimento acontece no vault, em código versionado. Esta skill é a dona do **estágio transform**: o `contrato-dados-fonte.yml` (manifesto que toda skill consumidora lê primeiro), o `_transform.py` (motor Python stdlib determinístico que lê `raw/` e materializa `derivado/`) e os derivados canônicos (`fato-ads-enriquecido.csv`, `dim-criativo.csv`, `qa-report.json`). Sem ela, cada skill refaz joins do zero — ou pior, improvisa; com ela, o cálculo acontece uma vez, certo, auditável, pra todos os consumidores.

Antes de agir, **leia [references/regras-aplicadas.md](references/regras-aplicadas.md)** (R1-R12 — as invariantes) e **[references/doutrina-transform.md](references/doutrina-transform.md)** (anatomia normativa do motor). O caso completo que forjou a skill: [references/exemplo-sigo.md](references/exemplo-sigo.md).

## Posição na cadeia (bounded context)

```
feed-planilha-vault          motor-dados-vault (ESTA)              monitor-builder + skills de análise
extract → raw/        ─────► contrato + transform → derivado/ ────► render / análise (consomem derivado/)
```

| Fronteira | De quem é |
|---|---|
| Baixar planilha/flow, orquestrar cadeia, agendar, notificar | `feed-planilha-vault` |
| **Contrato, joins, QA gates, derivados, âncoras, parser de taxonomia** | **esta skill** |
| Renderizar monitor/cockpit HTML | `monitor-builder` |
| Escrever/evoluir a convenção de nomenclatura (`taxonomia.yml`) | `media-buyer-*` (o motor só LÊ os patterns) |
| Crosswalk pontual de exports crus fora da cadeia do vault | `kimball` |
| Interpretar/analisar o dado | `newton`/`darwin`/`falconi` |

Se a demanda cruza a fronteira, pare e nomeie a skill dona.

## Modos

Detecte pela intenção; em dúvida, pergunte.

- **bootstrap** — montar a camada num vault que ainda não tem (replicação do padrão).
- **extensao** (default em vault já migrado) — novo derivado/coluna/gate por demanda de skill consumidora. **Todo pedido de dado que o derivado não cobre chega aqui como feature request** — nunca vira join improvisado na skill que pediu.
- **auditoria** — rodar QA, conferir drift contrato↔realidade, revalidar paridade/golden.

---

## Modo BOOTSTRAP — passos

### Passo 0 — Pré-requisitos + entrevista (não pule)
0. **Vault com monitor v1 vivo (gerador fazendo joins)?** É migração brownfield — siga **[references/migracao-v1-v2.md](references/migracao-v1-v2.md)** (levantamento + baseline congelado ANTES de qualquer skill; o v1 é a spec; golden test por estágio). Os passos abaixo valem, com as diferenças brownfield do playbook.
1. **Feed existente**: a camada transform pressupõe `raw/` alimentado. Sem feed → rode `feed-planilha-vault` primeiro.
2. **Inspecione as fontes reais** (headers, contagens, amostras de cada aba/extração) — grão e chave se descobrem olhando, não se assumem.
3. **Entreviste o operador** (AskUserQuestion) sobre o que só ele sabe: colunas de extensão por tabela (dono + semântica), semântica do funil do projeto (o que é MQL/SAL/demo aqui), linha-sentinela (valor + data), abas da família padrão ausentes (`presente: false`), quebras de série conhecidas.

### Passo 1 — Contrato + config financeiro
Gere `<vault>/90-referencias/dados-fonte/contrato-dados-fonte.yml` a partir de [references/contrato-template.yml](references/contrato-template.yml). Grão em 1 frase por tabela (R9); PII marcada (determina o que é commitável); gates de QA por chave declarada (R3-R4).

Crie também o **`config-financeiro.yml` por entrevista** (doutrina §8: vigências append-only · declarado = fee/margem/tcv/impostos/budget de mídia por canal/contas pré×pós-pago/thresholds de alerta · derivável do dado → NÃO declarar · intermediário → `premissa:`). Consumidores: DRE do monitor + notify do feed. Nada inferido em silêncio — o que só o operador/cliente sabe, pergunte.

### Passo 2 — Motor
Escreva `_transform.py` clonando os padrões do exemplo Sigo, parametrizado pelo contrato deste vault:
- Helpers de parsing como biblioteca importável (o render importa daqui — 1 fonte de verdade).
- Cargas com gates NA CARGA (unicidade da dimensão antes do join — R4).
- `derive_funil` com a **âncora declarada no contrato** (ver Passo 3).
- Parser de taxonomia lendo `10-fundacao/taxonomia.yml` (se existe; ausente = parse desligado com WARN).
- Materialização padrão (TODA rodada, todo vault): **fato + dim-criativo + qa-report + baseline-metricas** (doutrina §7.5 — o baseline lê `contrato_inicio`/fee/tech/tcv do config-financeiro e a semântica do bloco `receita:` do contrato; métricas sem input ficam AUSENTES declaradas). WARNs em stdout, nunca stderr.

### Passo 3 — Âncora semântica + golden test (gate de qualidade CRÍTICO)
Se o motor substitui cálculo preexistente (fórmula, relatório legado): **execute o procedimento de golden test** da doutrina §4 — congele baseline, teste variantes de âncora, aceite só diff ZERO nas métricas-âncora, registre a âncora vencedora no contrato com a prova. Se não há baseline (vault novo sem cálculo prévio): declare a âncora por decisão explícita do operador (safra × calendário por métrica) e registre no contrato.

### Passo 4 — Plugar na cadeia + 1ª rodada
Adicione o estágio transform no orquestrador do feed (`_atualizar-dados.ps1`, entre feed e render — via `cmd /c "python _transform.py 2>&1"`, decisão por exit code; falha degrada com WARN). ⚠️ **O `.ps1` é UTF-8 com BOM** (R4 do feed — PS 5.1 lê sem BOM como ANSI e quebra em acento): após editar, re-assegure o BOM (`[IO.File]::WriteAllText($p,(Get-Content $p -Raw -Encoding UTF8),(New-Object Text.UTF8Encoding($true)))`). Rode a cadeia completa 1× e leia o `qa-report.json`: os achados da 1ª rodada são o teste de aceitação (gates sempre pegam algo real).

### Passo 5 — Cascata + handoff
Atualize `mapa.md` da pasta, seção de dados do `claude.md` do vault (caminho canônico: contrato → derivado → raw como exceção) e reporte: derivados materializados, achados de QA (com o que corrigir na origem), âncoras registradas.

---

## Modo EXTENSAO — passos

1. **Leia o contrato** e o pedido da skill consumidora: o dado já existe em algum derivado? (Frequentemente sim — aponte e encerre.)
2. **Additive-only** (R2): coluna/derivado novo OK; remover/renomear/re-tipar coluna consumida = bump de versão do contrato + aviso aos `consumidores:` declarados.
3. Implemente no `_transform.py` + declare no contrato (`derivados:` com grão/PII/consumidores) **no mesmo turno**.
4. Rode o transform, confira o qa-report, valide 2-3 valores da saída contra o raw na mão (spot check).

## Modo AUDITORIA — passos

1. Rode o transform e leia `qa-report.json` — WARNs abertos são fila de correção (na ORIGEM, nunca no CSV).
2. **Drift contrato↔realidade**: headers reais das fontes vs `colunas_core` declaradas; derivados listados vs arquivos em `derivado/`; consumidores declarados vs skills que realmente leem.
3. **Frescor** (R12): timestamp do qa-report vs cadência declarada da cadeia.
4. **Paridade** (se houve mudança de lógica desde o último golden): re-rode o diff contra o baseline congelado.
5. Reporte tabela: gate · achado · ação · dono (origem/media-buyer/motor).

---

## Padrão de output (relatório de bootstrap)

```
Camada transform instalada: <Projeto>
  Contrato:  contrato-dados-fonte.yml (6 tabelas, 2 com extensões declaradas)
  Motor:     _transform.py plugado na cadeia (estágio 2, degrada com WARN)
  Derivados: fato-ads-enriquecido.csv (12.480 linhas) · dim-criativo.csv (572 ads) · qa-report.json
             · baseline-metricas.json (13 métricas × 4 janelas; ausentes: recompra/ARPU)
  Âncora:    funil = SAFRA (golden test vs baseline @ <hash>: cli/fat diff 0)
  QA 1ª rodada: 21 deals dup no CRM (corrigir na origem) · sentinela OK
```

## Loop de feedback (obrigatório)

Não declare "pronto" sem: (a) transform rodado com exit 0 e derivados materializados; (b) `qa-report.json` lido e achados triados (benigno × corrigir-na-origem); (c) golden test com diff ZERO quando substituiu cálculo preexistente — ou âncora declarada pelo operador registrada no contrato; (d) spot check de 2-3 valores do derivado contra o raw.

## Anti-patterns

- ❌ **Join improvisado numa skill consumidora** porque "o derivado não tinha" → é feature request pro modo `extensao`; o cálculo mora no motor, uma vez, pra todos.
- ❌ **Assumir a âncora temporal** de um cálculo substituído → engenharia reversa + golden test (a âncora "óbvia" divergiu 10× no piloto).
- ❌ **Corrigir dado sujo no CSV** (raw ou derivado) → raw é sobrescrito pelo feed; derivado, pelo motor. Correção é na origem; o gate reporta.
- ❌ **Abortar a cadeia por dup/órfão pontual** → dedup keep-first + WARN. Abortar só em corrupção estrutural (R6) — consumidor prefere dado de ontem a dado quebrado.
- ❌ **Hardcodar regex de nomenclatura no motor** → patterns vivem em `10-fundacao/taxonomia.yml` (donos: media-buyer-*); o motor lê e versiona por geração.
- ❌ **Duplicar helper de parsing em outro script** da cadeia → importar do `_transform.py` (drift de parser = números divergentes silenciosos).
- ❌ **Apresentar rateio como observado** → célula estimada sempre sinalizada (`*`).
- ❌ **Derivado com PII commitado** → PII no raw exige derivar agregando (grão anúncio/dia) ou gitignore no derivado.
- ❌ **Copiar extensões do Sigo como padrão** → `temperatura`/`score`/MQL=SAL são do projeto-gatilho; cada vault declara as suas na entrevista.

## Avaliação (3 cenários)

### Cenário 1 — Bootstrap em vault novo (replicação F8)
**Input:** "Monta a camada de dados do vault <X> no padrão dados-fonte 2.0; o feed já roda."
**Esperado:**
- [ ] Inspeciona fontes reais + entrevista extensões/sentinela/semântica de funil (não assume)
- [ ] Contrato gerado do template com grão/chave/PII/gates por tabela
- [ ] `_transform.py` parametrizado pelo contrato; helpers importáveis; WARNs em stdout
- [ ] Âncora declarada (golden test se há cálculo prévio; decisão do operador se não)
- [ ] 1ª rodada executada + qa-report triado + cascata no vault

### Cenário 2 — Feature request de skill consumidora (modo extensao)
**Input:** "A falconi precisa de conversão por qualificador de form que o fato não tem."
**Esperado:**
- [ ] Checa se algum derivado já cobre antes de implementar
- [ ] Novo derivado additive-only, declarado no contrato (grão/PII/consumidores) no mesmo turno
- [ ] NÃO edita a falconi pra ler raw — o join nasce no motor
- [ ] Transform rodado + spot check

### Cenário 3 — Fronteira (não é o motor)
**Input:** "Baixa a aba nova da planilha e agenda pra rodar de manhã."
**Esperado:**
- [ ] Reconhece extração/agendamento como `feed-planilha-vault` e redireciona
- [ ] Se a aba nova precisar entrar no contrato/derivados, executa SÓ essa parte (modo extensao)

---

> **v1.0.0 (2026-07-09)** — forjada via `god` na F7 do dados-fonte 2.0 (decisão
> `30-decisoes/2026-07-09-dados-fonte-v2.md` do vault Sigo ERP, piloto). Critério de
> quebra: vocabulário próprio (grão/fato/dim/contrato/quebras-de-série/âncora),
> recorrente cross-vault (F8 = replicação). Bounded context extraído do
> `feed-planilha-vault` (extração) e do `monitor-builder` (render).
