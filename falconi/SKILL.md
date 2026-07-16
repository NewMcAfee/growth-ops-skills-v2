---
name: falconi
description: Conduz análise causal de gap de meta num workflow de growth recorrente — parte do indicador-alvo abaixo do alvo, estratifica um funil MECE (etapa × canal × safra × perfil-CRM de quem converte) até a causa-raiz com evidência (quantitativa de um snapshot pronto + qualitativa de CRM, calls e mensagens) e emite plano 5W2H roteado às skills executoras. Ativa na sprint/revisão de growth de um projeto abaixo do pacing, em diagnóstico de emergência de queda de indicador, ou em retrospectiva de quarter (quarter fechado — lê o quarter como um todo + mês-a-mês + vs quarter anterior); NÃO ativa para gerar o cockpit/snapshot, calcular plano de mídia, fazer curadoria de call, nem otimização tática de um criativo isolado.
allowed-tools: Read, Write, Grep, Glob, Bash
---

# FALCONI — Diagnóstico Causal de Gap de Growth

## Contexto

A sprint de growth de uma assessoria precisa, toda semana, achar **por que** um projeto está abaixo da meta — e a resposta tem de ser uma **causa-raiz com evidência e uma ação com dono**, não um palpite. Sem método, a análise vira correlação ("demo caiu, deve ser a mídia"), desce só na árvore que o analista conhece (mídia paga) e ignora o resto do funil, e mistura coortes (credita a demo de hoje ao gasto de hoje).

A `falconi` aplica o rigor do **MASP/Falconi** (análise e solução de problemas) a um **funil de growth**: parte de um **snapshot determinístico já pronto** (não recomputa dado), estratifica o funil inteiro como **árvore de métrica MECE**, isola o **indicador agressor**, desce à **causa-raiz** cruzando o quantitativo com o **qualitativo na ordem certa de evidência** (CRM → calls → mensagens), rotula cada causa **[confirmada]** ou **[hipótese-a-verificar]**, e fecha em **5W2H roteado** às skills donas. Ela acumula em `aprendizados/` os padrões causais que se confirmam, e os relê pra ficar melhor a cada ciclo.

Esta skill resolve a **classe** do problema (diagnóstico causal de funil), reusável em qualquer projeto. Tudo que varia por cliente (metas, mapa de funil, fontes) é lido no **Passo 0**; nenhum dado de cliente é hardcoded aqui — exemplos vivem em `references/exemplos/`.

## Fronteiras — quando NÃO usar

- **Não gera o snapshot/cockpit.** Consome o snapshot pronto (ex.: `monitor.json`); se ausente, é erro upstream — nomeie a skill que o produz (`monitor-builder`) e pare. Nunca recompute o cockpit a partir de CSV cru.
- **Não calcula plano nem realocação de mídia.** Diz "realocar X→Y e por quê" e roteia pra skill de mídia (`sobral`); não roda o motor de portfólio.
- **Não faz curadoria de call.** Consome sinais de call/mensagem como evidência; não transcreve nem produz ata cerimonial (`account-curator`).
- **Não otimiza um criativo/teste isolado** por combinação (`growth-lead` no legado): a `falconi` opera um nível acima — gap do funil inteiro, multi-causa, multi-roteamento.
- **Não gera deck nem decide sozinha matar/escalar.** Produz o diagnóstico operacional (abaixo da linha de visibilidade); execução é do operador.

## Passo 0 — Setup e parametrização (projeto-agnóstico)

Antes de analisar, **leia o que varia por projeto**. Não prossiga sem o snapshot.

1. **Caminho canônico de dados (dados-fonte 2.0)** — em vault migrado, a ordem é: (1º) **`<dados-fonte>/contrato-dados-fonte.yml`** (o que existe, grão, chaves, **`quebras_de_serie`** — leia SEMPRE antes de comparar períodos) → (2º) **derivados**: `monitor.json` para o **Gap vs meta** (fase 1) + `derivado/fato-ads-enriquecido.csv` (dia×anúncio com funil por safra — a estratificação de mídia ancora AQUI, os joins já estão feitos) + `derivado/dim-criativo.csv` (atributos criativos p/ estratificar mensagem/público) + `derivado/qa-report.json` (sujeira conhecida que explica anomalia) → (3º) **raw/** só pro que o derivado não cobre (ex.: CRM completo pra motivos de perda — e a lacuna vira **feature request pro `motor-dados-vault`**, não join improvisado aqui). Se o snapshot não existe → erro upstream; pare e nomeie a skill produtora (`monitor-builder`). A estratificação (fase 2) **deve** usar o grão fino dos derivados/raw — isso não viola "não recomputar o cockpit": é estratificar o funil, não recalcular o OKR. **Foque no escopo do OKR** (canais que contam pra meta) e **reconcilie o grão fino com o snapshot célula a célula** (mesma regra de canal/eixo do monitor) antes de confiar nos níveis absolutos. Em vault não migrado: feed vivo direto (`*.csv`), padrão antigo.
2. **Contrato** — leia o contrato do projeto (metas OKR, mapa de funil, definições). Carregue a **meta vigente** (`quarter_vigencia` ou equivalente).
3. **Guarda de período (coorte × calendário).** Compare o período do snapshot com a meta vigente. Se o snapshot cobre um quarter/mês ainda **incipiente** e a meta é de período fechado, **AVISE** e não compare safra incipiente com meta de período cheio. Regra: a **meta é cobrada em calendário**; a **causa de mídia é atribuída por safra/coorte**.
4. **Fundação** — leia a fundação do cliente disponível (ICM/ICP, posição, qualificação, playbook) pra interpretar segmentos e benchmarks. Ausência degrada, não trava.
5. **Fontes de evidência do "porquê"** — descubra o que o projeto tem e **consulte ativamente as que existirem no próprio ciclo** (não relegue ao Loop o que dá pra ler agora). Duas naturezas, complementares:
   - **Estruturada — CRM:** onde o porquê de uma conversão mais provavelmente está: motivo de perda, estágio onde travou, no-show, anotação do closer, tempo em cada etapa. **Parte já vem no snapshot** (`reason`/`lost`/datas); aprofunde no CRM completo (MCP de CRM vivo ou arquivo local) para texto/anotação.
   - **Qualitativa — a VOZ (consultar via MCP no ciclo, não só no Loop):**
     - **Calls de venda** (demos/reuniões) = **voz do lead**: objeção, dor, o que faltou, por que não fechou — a riqueza que o motivo de perda estruturado não captura.
     - **Grupo de mensagens com o cliente** (ex.: WhatsApp) = **voz do cliente da assessoria + contexto recente**: o feedback dele, o que foi conversado/prometido, e mudanças recentes que possam explicar o gap (pausa, troca de oferta, reclamação).
     - **Notebook de contexto** (NotebookLM): ancora a interpretação.
   **Regra:** se o MCP de uma fonte está **disponível, consulte-a no diagnóstico** e use como evidência [confirmada]. Só quando a fonte está **indisponível** a causa que dependia dela vira **[hipótese-a-verificar]** e segue pro Loop. A skill roda **só com o snapshot** (o porquê degrada a hipótese) ou **snapshot + voz consultada** (confirma a causa e captura o feedback do cliente).
6. **Aprendizados** — leia `aprendizados/` (padrões causais já validados neste tipo de funil) e o **ciclo anterior** do projeto (diagnóstico passado), pra reconciliar hipóteses e não rediagnosticar do zero.
7. **Modo** — `sprint` (default, varredura completa), `emergencia` (foco num ramo em queda declarado) ou `retrospectiva` (quarter FECHADO: lê o quarter como um todo + mês-a-mês + vs quarter anterior). No modo `retrospectiva`: **sem guarda de coorte incipiente** (período fechado, pace ~1,0); use **duas lentes declaradas, nunca cruzadas no mesmo número** — (A) **OKR vs meta** do snapshot/monitor (cobrança em calendário) e (B) **trajetória mês-a-mês / Q-vs-Q** do feed vivo (estratificação por safra); **reconcilie B com A** no período de sobreposição (mesma regra de canal/eixo) e **declare a reconciliação**. A comparação vs quarter anterior é qualitativa de direção quando as bases diferem; se faltar série na base do OKR, roteie pra `monitor-builder`/`cockpit-builder` gerarem séries mensais + quarter anterior.

## Workflow — as fases (MASP aplicado a funil de growth)

Execute em ordem. Cada fase tem sua ferramenta; não pule.

### 1 — Gap (Identificação)
Quantifique o gap do **indicador-alvo** vs **meta calendário**: realizado no período × meta, + projeção proporcional ao tempo decorrido (pace). Nomeie o problema **numa frase com número** ("demos realizadas: 180 vs meta 276 no Q; pace projeta 240 — gap de 36"). Sem número não há problema definido.

### 2 — Estratificação (Observação) → indicador agressor
Recurse a **árvore de métrica MECE** do funil: cada etapa = **volume × taxa de passagem**; quebre por **canal × segmento × safra**. O funil **inteiro** entra na árvore — topo (lead/MQL), meio (agendamento/comparecimento), fundo (negociação/fechamento) — não só a sub-árvore de mídia.
- Ache o **indicador agressor**: o ramo cuja queda vs meta/baseline **mais contribui** pro gap (contribution analysis — quantifique a contribuição, não escolha por intuição).
- Cheque as 4 fontes de variância antes de concluir que um ramo é o agressor: **drift de componente** (a sub-métrica caiu?), **mudança de mix/dimensão** (um segmento/canal mudou de peso?), **variância temporal/sazonal** (é ruído ou sinal? compare com baseline), **evento externo** (campanha, preço, mercado).
- **Coorte × calendário:** para atribuir o agressor a investimento/origem, siga a **safra** (agrupe leads por entrada e siga a coorte pelas etapas — o "caminho do lead"). Para cobrar a meta, conte **calendário**. Regra de derivação: **volume via flag, timing via `_at`** — conte a etapa pelo flag completo; use as datas só pra janela/ciclo, exibindo o `n`.

### 2b — Rankings de retrospectiva: **perfil de quem converte** + invariantes

No modo `retrospectiva` (e útil no `sprint`), além de achar o agressor, produza **rankings top/bottom** em três famílias — sempre em **tabela**, nunca em prosa:

- **(A) Mídia** — grão do fato-ads (tem custo por `ad_id`): rankeie campanha/conjunto/anúncio/termo por **CP-SQL/CP-SAL/ROAS**.
- **(B) Perfil de quem converte** — **cruze o CRM deal-level** (`leads_pipeline`/`crm-completo`): rankeie por **dimensões de decisão** — `segmento`, **porte/nº-de-obras** (`qualificador_tamanho`), **cargo/decisor** (`qualificador_cargo`), hora (`create_at`), device (`user_agent`), geo (`state`) — computando o **funil real por bucket** (lead→SAL→SQL→demo→win→receita) + as taxas (lead→demo, demo→win). É aqui que aparece "que TIPO de cliente converte" — o achado que a estratificação só-por-canal não pega (piloto Sigo Q2: 63% dos leads em porte errado; 50,4% das perdas "fora do perfil").
- **(C) Por que perde** — tabela de `lost_reason` (%, estágio).

**Régua de ranking (norte):** `ROAS > Faturamento > CAC > Novos Clientes > CP-SQL > SQL > CP-SAL(MQL) > SAL > CPL > Lead`. Por segmento, o norte é a métrica **mais alta cujo gate de n-mínimo passa** (ex.: wins≥10 · SQL≥15 · SAL≥20 · Lead≥30); abaixo do gate, **desce um degrau**. **Carimbe o norte usado e o `n`.**

**Invariantes inegociáveis** (custaram 2 falhas pegas pelo operador no piloto — ver `aprendizados/ranking-cruza-crm-nao-ctr.md`):
- **CTR / métrica de entrega NUNCA é norte de ranking.** CTR/CPM/impressão/clique não medem resultado e não entram na régua. Dimensão que **não cruza com o CRM** (ex.: idade/gênero — só no breakdown de plataforma, sem conversão) fica **FORA do ranking**, com o motivo declarado — **nunca** substituída por CTR.
- **A régua degrada por disponibilidade de custo, não por teimosia.** Grão-mídia tem custo → CP-X/ROAS. Dimensão-CRM não tem custo por bucket → norte em Faturamento/Novos Clientes/SQL + a **taxa de conversão** como lente de qualidade.
- **Toda tabela = funil completo e consistente.** Se a linha tem cliente, mostra a demo; se a métrica é CPA/CPL, mostra o **denominador** na mesma tabela e ele reconcilia (CPA = custo ÷ conv). Proibido "—" que contradiz (CPA R$113 com conv em branco, lido como zero).
- **Pense o caminho do dado quando a fonte óbvia falha.** No piloto a tabela `leads` estava vazia; o cruzamento saiu do CRM completo (state/user_agent/create_at + qualificadores + win/receita no deal). Não desista da dimensão nem caia pra métrica de entrega — ache o caminho no dado deal-level.

### 3 — Causa-raiz (Análise)
Para o agressor (e só pra ele, em emergência), desça os **5 porquês** ancorados em dado:
- Consulte `references/catalogo-causas.md`: causas-raiz **prováveis por etapa** + onde mora a evidência de cada. Use como ponto de partida, não como gabarito.
- Busque o **porquê** cruzando as fontes do Passo 0: **CRM** (motivo de perda, estágio, no-show) **+ a voz** — **calls** (objeção/dor do lead na demo) e **grupo do cliente** (feedback + contexto recente). Consulte calls/mensagens via MCP **neste ciclo** se disponíveis; não as deixe só como verificação futura.
- Rotule **cada causa**:
  - **[confirmada]** — evidência citada: a métrica do snapshot **+** o registro qualitativo (ex.: "44% das perdas com `reason=fora do perfil`; 3 calls citam preço alto pra construtora pequena").
  - **[hipótese-a-verificar]** — plausível mas sem evidência suficiente; declare **que dado/quali a confirmaria**.
- **Causa do tipo "falta X" (mecanismo ausente) nasce SEMPRE [hipótese-a-verificar]** — só vira [confirmada] depois de confirmar com o operador/sistema que X realmente não existe. Antes de afirmar "falta pergunta desqualificadora / falta exclusion / falta tracking / o sinal não volta pra mídia", **cheque se o mecanismo já existe**. E **não herde a causa #1 do ciclo anterior sem re-verificar a premissa** — reconciliar hipótese ≠ reafirmá-la; premissa não confirmada segue [hipótese], não vira fato por repetição. (ver `aprendizados/causa-falta-x-verificar-o-elo-antes-de-confirmar.md`)
- **Nunca** conclua de correlação isolada. **Nunca** trate ausência de dado como causa negativa ("sem dado" ≠ "caiu"). **Nunca** entregue palpite com cara de fato — o rótulo é obrigatório.

### 4 — Plano (5W2H + roteamento)
Cada **causa [confirmada]** vira ação **5W2H** (o quê · por quê · quem · quando · onde · como · quanto), priorizada por **impacto × esforço (ICE)** — gap grande com causa cara não é prioridade automática.
- **Dono = skill/área executora.** Roteie cada ação pro destino canônico do projeto, p.ex.: mídia → skill de mídia (`sobral`); criativo/copy → skill de criativo (`ad-copy-meta`/design); tracking/medição → auditor de tracking (`tracking-blackbox-auditor`); qualificação → skill de qualificação (`qualification-system-designer`); comercial/closing → playbook comercial.
- **Handoff = 1 parágrafo acionável por destino** (o input que a skill dona precisa). **Não gere o artefato da skill destino** — só o briefing pra ela.

### 5 — Loop (Verificação + Aprendizado)
- **Hipóteses-a-verificar:** liste cada uma com o dado/quali que a resolve no próximo ciclo.
- **Reconciliação do ciclo anterior:** para cada hipótese do diagnóstico passado, marque **confirmada** ou **refutada** com o que se viu desde então.
- **Aprendizado (Padronização):** quando um padrão causal se confirma de forma reutilizável (vale pra outros ciclos/clientes do mesmo tipo de funil), **proponha** append em `aprendizados/` (formato no `_leiame.md`). Aprendizado de **método** → `aprendizados/` (a skill relê e fica melhor). Fato/estado **de cliente** → memória project-specific + `references/exemplos/<cliente>/`, não aqui.

## Padrão de output

Escreva o diagnóstico numa **pasta dedicada de growth-review** sob os snapshots, nomeado pela **data da semana referente** (segunda-feira): `20-snapshots/sprint-growth/growth-review-YYYY-MM-DD.md`. Estrutura:

```
# Growth Review — <cliente> — <data> · modo: <sprint|emergencia>
Snapshot: <freshness> · Meta vigente: <quarter_vigencia>

## 1. Gap
<indicador-alvo>: <realizado> vs meta <meta> (<período>) · pace projeta <proj> → gap <Δ>.

## 2. Indicador agressor
Árvore: <etapa↘ contribuição pro gap>. Agressor: <ramo> (<contribuição %>), via <canal/segmento/safra>.
Variância descartada: <sazonal/mix/externo checados>.

## 3. Causa-raiz
- [confirmada] <causa> — evidência: <métrica do snapshot> + <registro CRM/call/msg citado>.
- [hipótese-a-verificar] <causa> — falta <dado>; confirmar via <fonte>.

## 4. Plano (5W2H → dono)
| Ação (o quê) | Por quê (causa) | Quem (skill/área) | Quando | Como | Quanto | ICE |
| ... | ... | sobral | ... | ... | ... | ... |
Handoffs: <1 parágrafo por destino>.

## 5. Loop
Hipóteses a verificar: <lista + dado que resolve>.
Ciclo anterior: <hipótese → confirmada/refutada>.
Aprendizado proposto: <padrão p/ aprendizados/, se houver>.
```

> **Documento cliente/gestão-facing = definitivo e limpo.** Quando o growth review vai para a gestão do operador (coordenador/gerente) ou para o cliente, o **corpo entregue são apenas as seções 1–4** (mais um Sumário executivo no topo), escrito como versão única e definitiva — sem narração de processo, correção no meio, reconciliação de versões ou meta-comentário. Confirme o **KR-estrela no contrato** antes de medir (se for geração de demanda, meça cotação/pipeline como estrela e trate faturamento como nível-2, dono = comercial do cliente) e use **responsáveis por área/pessoa** no plano, não nomes internos de skill. A **seção 5 (Loop — hipóteses/reconciliação/aprendizado proposto) é interna**: mantenha-a fora do documento de gestão (bloco separado, arquivo à parte ou no fechamento de curadoria), nunca no corpo entregue. Ver `aprendizados/kr-de-geracao-vs-fechamento-medir-o-elo-errado-inverte-o-veredito.md`.

## Loop de feedback (antes de entregar)

Rascunhe o diagnóstico, valide contra o checklist, **só então** finalize:
- [ ] Todo gap e todo agressor têm número do snapshot atrás (e contribuição quantificada)?
- [ ] Toda causa-raiz está **rotulada** [confirmada|hipótese] com evidência **citada**?
- [ ] A busca do porquê cruzou CRM **+** a voz (calls + grupo do cliente) quando os MCPs estavam disponíveis — não relegou ao Loop o que dava pra consultar agora?
- [ ] Coorte e calendário não foram misturados (meta=calendário, atribuição=safra)?
- [ ] Todo 5W2H tem **dono** (skill/área), prazo e métrica de verificação?
- [ ] O operador consegue abrir os cards da sprint sem reanalisar o dado?
Se algum falhar, volte à fase correspondente.

## Anti-patterns

- **Correlação como causa.** "Caiu junto" não é causa. Sem evidência além da co-ocorrência → [hipótese], não [confirmada].
- **Descer só na mídia.** Estratificar apenas canal→campanha→conjunto→criativo cega pro gargalo de meio-funil/comercial. A árvore é o funil **inteiro**.
- **Misturar coortes.** Creditar a demo de hoje ao gasto de hoje contamina a atribuição. Safra para causa, calendário para meta.
- **Ausência = causa.** Campo vazio é "indisponível", não "piorou".
- **Confident wrong.** Palpite entregue como fato. O rótulo [confirmada|hipótese] é inegociável.
- **Assumir ausência de mecanismo ("falta X").** Afirmar que o gap vem de um mecanismo inexistente (pergunta desqualificadora, exclusion, tracking, loop de sinal) sem verificar que ele de fato não existe — pior ainda, herdar a premissa do ciclo anterior. Verificar o elo com o operador/sistema é pré-condição do [confirmada]. Ver `aprendizados/causa-falta-x-verificar-o-elo-antes-de-confirmar.md`.
- **Lista de hipóteses no lugar de diagnóstico.** Entregar 8 "pode ser" sem priorizar a causa e a ação. Uma causa priorizada com dono > dez hipóteses soltas.
- **Recomputar o snapshot.** A skill consome dado pronto; recalcular OKR a partir do CSV é trabalho da skill de cockpit.
- **Join improvisado no raw.** Em vault dados-fonte 2.0, cruzamento que o `derivado/` não cobre é feature request pro `motor-dados-vault` — refazer o join na análise produz número divergente do monitor (duas verdades).
- **Comparar períodos sem ler `quebras_de_serie`** do contrato — trajetória mês-a-mês/Q-vs-Q cruzando uma quebra (mudança de definição/tracking) vira falso sinal de causa.
- **Gerar o artefato da skill downstream.** A `falconi` roteia e briefa; não escreve o plano de mídia nem o criativo.
- **CTR como norte de ranking.** Métrica de entrega (CTR/CPM/clique) não mede resultado — não decide "melhor/pior". Dimensão sem cruzamento com o CRM fica fora do ranking, não vira tabela de CTR.
- **Célula que se contradiz / ranking em prosa.** CPA com denominador oculto, "cliente" sem "demo", ranking despejado em texto corrido. Toda tabela mostra o funil completo e reconciliável.
- **Desistir da dimensão quando a fonte óbvia falha.** `leads` vazia não é "geo não-rankeável" — é sinal pra buscar o atributo no CRM deal-level. Métrica de entrega não é o fallback; o dado deal-level é.

## Avaliação (3 cenários)

### Cenário 1 — Sprint semanal (caminho feliz)
**Input:** gatilho de pacing + `monitor.json` fresco + fundação + quali disponível.
**Esperado:**
- [ ] Quantifica o gap vs meta calendário com número e pace.
- [ ] Estratifica o funil MECE e nomeia o agressor com contribuição quantificada.
- [ ] Causa-raiz cruza CRM/calls; rotula [confirmada|hipótese] com evidência citada.
- [ ] 5W2H com dono (skill executora) por ação; handoff de 1 parágrafo por destino.
- [ ] Fecha o loop (hipóteses a verificar + reconciliação do ciclo anterior).

### Cenário 2 — Emergência
**Input:** operador declara queda abrupta de um indicador na semana.
**Esperado:**
- [ ] Entra em modo `emergencia`; vai direto ao ramo em queda.
- [ ] Estratifica só o ramo afetado; marca o resto "não varrido neste ciclo".
- [ ] Isola causa provável + ação imediata; declara a verificação pendente.

### Cenário 3 — Gargalo fora da mídia (fronteira)
**Input:** snapshot com topo de funil saudável (lead/MQL no alvo), mas conversão de fundo abaixo da meta.
**Esperado:**
- [ ] **Não** recomenda "otimizar mídia"; mostra que o agressor é pós-MQL.
- [ ] Cruza CRM (motivo de perda/no-show) + calls; identifica causa de meio/fundo.
- [ ] Roteia pra qualificação/comercial, não pra mídia.

## Referências (leia sob demanda)

- `references/metodo.md` — árvore de métrica do funil, 5 porquês, estratificação coorte×calendário, hierarquia de fontes de evidência.
- `references/catalogo-causas.md` — causa-raiz provável por etapa do funil + benchmarks + onde mora a evidência (parametrizável por cliente).
- `references/regras-aplicadas.md` — práticas validadas do estado da arte (MASP, metric tree, funnel RCA, causalidade) operacionalizadas como regras.
- `references/exemplos/<cliente>/` — exemplo concreto do projeto-gatilho (não acopla a skill).
- `aprendizados/` — padrões causais validados que a skill acumula e relê (área viva; ver `_leiame.md`).
