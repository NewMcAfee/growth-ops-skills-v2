# Método — diagnóstico causal de funil

Detalha o "como" das fases do `SKILL.md`. Leia quando precisar aprofundar uma fase.

## Árvore de métrica do funil (MECE)

O indicador-alvo no topo decompõe em **volume × taxa de passagem** por etapa: `Nₑ = Nₑ₋₁ × taxaₑ`. Quebre cada etapa por **canal × segmento × safra**. A árvore é **MECE** — cobre o funil inteiro (topo: lead/MQL; meio: agendamento/comparecimento; fundo: proposta/negociação/ganho), ramos mutuamente exclusivos. É a versão visual dos 5 porquês: construída uma vez, você **recursa** do topo até o driver.

## Contribution analysis (achar o agressor)

Não escolha o agressor por "maior queda relativa" — escolha por **maior contribuição absoluta ao gap**. Uma queda grande num ramo de baixo volume contribui pouco.

Método: compare o resultado real com o **contrafactual** em que **só aquela etapa** estivesse na meta (as demais no realizado). A diferença é a contribuição daquela etapa pro gap. Ordene as etapas por contribuição; o topo da lista é o agressor.

## As 4 fontes de variância (checar antes de concluir que um ramo é o agressor)

1. **Drift de componente** — a sub-métrica de fato caiu (vs baseline, não vs zero)?
2. **Mudança de mix/dimensão** — um segmento/canal mudou de peso e arrastou a média (paradoxo de Simpson)?
3. **Variância temporal/sazonal** — é sinal ou ruído? Compare com o mesmo período anterior.
4. **Evento externo** — campanha, mudança de preço, concorrente, mercado.

## Coorte × calendário (não misturar)

- **Meta = calendário:** conta eventos cujo `_at` cai no período. É o que o cliente cobra; já vem pré-computado no `okr` do snapshot.
- **Causa/atribuição = safra (coorte):** agrupe leads por entrada (`create_at`) e siga a coorte pelas etapas (o "caminho do lead"). Liga o investimento ao resultado que ele gerou.
- **Regra de derivação:** **volume via flag, timing via `_at`**. Conte a etapa pelo flag completo (`sal`, `show_meeting`…); use as datas só para janela/ciclo, e **exiba o `n`** (os `_at` são esparsos).
- **Respeite o lag:** se o ciclo pós-demo leva ~N dias, **não** cobre uma safra incipiente pelo resultado final — ela ainda não maturou. Misturar coortes ou ignorar lag é o erro de atribuição mais comum.

## Hierarquia de fontes de evidência (o "porquê")

O porquê de uma conversão mora primeiro no **registro do deal** (CRM), mas a **voz** (calls + grupo do cliente) é dimensão própria — consulte-a **no ciclo**, não só como verificação futura:

1. **CRM** (estruturado) — motivo de perda (frequentemente **tagueado por etapa**), qualificadores (BANT), temperatura/score. Fonte #1 do "porquê". Parte já vem no snapshot (`reason`/`lost`/datas); aprofunde no CRM completo para texto/anotação.
2. **Calls de venda** (voz do **lead**) — objeção, dor, o que faltou na demo, por que não fechou. Captura o que o motivo de perda estruturado não diz. Via MCP de calls.
3. **Grupo de mensagens com o cliente** (voz do **cliente da assessoria** + **contexto recente**) — o feedback dele sobre a operação, o que foi conversado/prometido, e mudanças recentes que expliquem o gap. Via MCP de mensagens.
4. **Notebook de contexto** (NotebookLM) — ancora a interpretação.

Regras: **consulte a voz no ciclo** se o MCP existe (evidência [confirmada]); só relegue ao Loop a fonte **indisponível**. **Campo vazio não é evidência** (é não-instrumentado); **texto livre** (relatório BANT em "dor") é leitura **caso-a-caso**, não agregação; toda evidência citada nominalmente.

## 5 porquês ancorados

Cada "porquê" aponta um **dado**, não uma opinião. Pare quando chegar a uma causa **acionável** (vira 5W2H) e **confirmável** (tem evidência ou vira hipótese declarada). Não desça além do que o dado sustenta.

## Rotulagem

- **[confirmada]** — métrica do snapshot **+** registro qualitativo, ambos citados.
- **[hipótese-a-verificar]** — plausível, sem evidência suficiente; declare **qual dado/fonte** a confirmaria no próximo ciclo.

## 5W2H + priorização ICE

Cada causa confirmada → ação **5W2H** (o quê · por quê · quem · quando · onde · como · quanto). Priorize por **ICE** (impacto × confiança × esforço) — gap grande com causa cara/incerta **não** é prioridade automática. Dono = skill/área executora; handoff = 1 parágrafo, sem gerar o artefato dela.

## Normalização (sempre, antes de agregar)

Capitalização/sinônimos; remoção de registros de teste; isolamento de outliers de data; tratamento de campos não-instrumentados como lacuna (não como sinal).
