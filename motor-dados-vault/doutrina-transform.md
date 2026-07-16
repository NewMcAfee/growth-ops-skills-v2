# Doutrina do transform — anatomia do motor

> Referência normativa do `_transform.py` que a skill instala/evolui num vault.
> O exemplo vivo completo está em `90-referencias/dados-fonte/_transform.py` do
> vault Sigo ERP (piloto, 2026-07-09) — clone os padrões de lá, parametrize pelo contrato.

## 1. Posição na cadeia

```
feed (.ps1, agendado)          _transform.py (ESTA doutrina)      render/skills
  escreve raw/          ─────►   lê raw/ + contrato + taxonomia  ─────►  consomem derivado/
  (espelho fiel das fontes)      materializa derivado/                   (nunca refazem join)
```

- `raw/` — **só o feed escreve**. Espelho fiel; nenhuma correção manual (seria sobrescrita no próximo run).
- `derivado/` — **só o transform escreve**. Humano nunca edita. Todo derivado é reproduzível do raw.
- Falha do transform **não derruba a cadeia**: o render usa o último derivado bom e loga WARN.
- WARNs vão pra **STDOUT** (stderr mata a cadeia no PS 5.1 — o orquestrador roda `cmd /c "python ... 2>&1"` e decide pelo exit code).

## 2. O transform é também a biblioteca de parsing (1 fonte de verdade)

Helpers canônicos (`br_num`, `br_int`, `pdate`, `iso`, `istrue`, `canal_norm`) vivem **no `_transform.py`** e são **importados** pelo gerador do monitor e por qualquer script da cadeia. Nunca duplique um parser em outro script — drift de parsing entre transform e render produz números divergentes silenciosos.

Parsers defensivos obrigatórios (falhas reais do piloto):
- **Números BR** (planilha): `1.234,56` — remover `.` de milhar, `,`→`.`. **MAS CSVs do flow/API usam ponto decimal** — neles use `float()` puro; `br_num` trataria `2.0` como `20`.
- **Datas**: aceitar `dd/mm/yyyy` **e** serial do Sheets (`46186` = epoch 1899-12-30 + n dias; janela plausível 30000–80000). Retornar `None` no lixo, nunca levantar.
- **`MIN_ANO`**: bases completas carregam outliers de data (1999/2023 de teste) — filtrar por ano mínimo declarado, com exceção da linha-sentinela.
- **Booleans de planilha**: comparar `str(x).strip().upper() == "TRUE"` (vem como texto).
- **Células corrompidas por formato** (`%` na célula, notação científica de ID): tratar no parse, reportar no QA pra correção na origem.

## 3. QA gates — "nunca trava, nunca esconde"

O motor **nunca trava o cockpit por dado sujo** (dedup determinístico e segue) e **nunca esconde** (todo achado vai pro `qa-report.json` + stdout; o notify e a tela Atenção do monitor consomem de lá).

| Gate | Política | Racional |
|---|---|---|
| Chave duplicada em **dimensão** (`ad_id` no index) | keep-first. Dup **IDÊNTICO** = INFO benigno (contar); dup **CONFLITANTE** = WARN alto com amostra de ids | join com dim duplicada **explode** o fato. Distinguir idêntico×conflitante evita alarme falso (caso real: 972 dups idênticos benignos — linha por keyword em legado Google) |
| Chave duplicada em **fato** (`data+ad_id`; `deal_id`; `lead_id`) | keep-first + WARN com lista amostrada (≤20 ids) | soma 2× métricas / infla funil. Lista amostrada permite correção na origem |
| **Órfão de join** (ad_id do fato sem match na dim) | contar + fallback declarado (ex.: valores legados do próprio CSV) + INFO | órfão silencioso vira "campanha —" no monitor sem ninguém saber por quê |
| **Linha-sentinela** (canário) | excluir do cálculo; **WARN alto se SUMIR** | linha sintética fixa na origem detecta quebra silenciosa do export (aba renomeada, range truncado, permissão) — a ausência do canário é o alarme |
| **Nomes fora do vocabulário** da taxonomia | WARN com amostra → fila de correção do media-buyer | naming é contrato; o gate pega drift de convenção de fábrica (caso real: 5 campanhas com tema no lugar de temperatura, detectadas na 1ª rodada) |

Formato do achado: `{nivel: warn|info, check: <slug>, msg: <humano>, <extra>: [amostra]}`, acumulado e gravado em `derivado/qa-report.json` com timestamp + contagem de linhas.

## 4. Âncora semântica + golden test (o coração da paridade)

Toda métrica derivada tem uma **âncora temporal** que precisa ser declarada no contrato:
- **Safra**: o evento conta no período de **criação do lead** (o "caminho do lead" — atribuição a mídia/coorte).
- **Calendário**: o evento conta no período em que **aconteceu** (cobrança de meta, DRE).

**Nunca assuma a âncora — descubra e prove.** Quando o motor substitui um cálculo preexistente (fórmula de planilha, relatório legado), a âncora usada pela origem é frequentemente contra-intuitiva. Procedimento validado no piloto (engenharia reversa da fórmula do growthpack):

1. **Congele um baseline**: o output antigo num estado conhecido (`git show <HEAD>:<arquivo>` do CSV pré-corte, ou export congelado).
2. **Implemente as variantes candidatas** de âncora (ex.: A = data do evento com fallback create; B = create/safra; C = só data do evento).
3. **Rode o diff** de cada variante contra o baseline nas métricas-âncora (as mais a jusante: clientes, faturamento).
4. **Aceite só diff ZERO** (ou explique cada divergência linha a linha). No piloto: variante safra deu cli e fat diff 0; a "óbvia" (data do evento) divergia 10×.
5. **Registre a âncora vencedora no contrato** (`joins_reconstruidos_no_motor.funil`) com a prova.

Sem golden test, "paridade" é opinião. Com ele, é matemática.

## 5. Parser de taxonomia — versionado por geração

Nomenclatura de entidade (campanha/conjunto/anúncio) evolui no tempo; nomes antigos não podem quebrar o parse.

- Patterns vivem em **`10-fundacao/taxonomia.yml`** do vault (donos: `media-buyer-*`) — o motor **lê de lá**, nunca hardcoda regex.
- Estrutura: `nomenclatura_entidades.<entidade>.geracoes[]` com `{id, pattern}` (regex com named groups), **em ordem — primeira que casa vence**.
- Sem match = `geracao: "legado"`, campos vazios — **nunca quebra**, e a cobertura por geração vai pro QA (INFO).
- Campo com vocabulário fechado (ex.: temperatura ∈ Frio/Morno/Quente): valor fora do vocab **não entra no campo** — vira `variante` + flag fora-de-vocab no QA (fila de correção do media-buyer).
- `taxonomia.yml` ausente/quebrado → parse desliga com WARN, o resto do transform segue.

Saída: `derivado/dim-criativo.csv` — 1 linha por ad_id da dim, atributos parseados + enriquecimento de copy/CTA/imagem do flow (dedup do criativo keep-LAST — a fonte guarda versões, a última é a vigente).

## 6. Rateio de funil por dimensão de entrega (funil estimado)

APIs de plataforma dão breakdowns (geo/demo/device/hora) só de **custo/volume** — não de conversão. Para cruzar funil × dimensão de entrega:

```
evento_estimado(dimensão, mês) = Σ_ads [ evento(ad, mês) × share_spend(ad, dimensão, mês) ]
```

- O rateio distribui o funil REAL do anúncio proporcionalmente ao investimento dele em cada valor da dimensão.
- **Toda célula estimada é sinalizada** (`*` na UI, coluna `_estimado` no dado) — nunca apresentar rateio como observado.
- Funil por **atributo do anúncio/público** (a dimensão é o próprio ad) é REAL — não precisa de rateio.

## 7. Reconciliação de totais (fato × CRM analítico)

Quando o fato (grão dia×anúncio) não captura todo o CRM (leads sem ad_id, canais não rastreados), o resíduo é **distribuído fracionado** no grão, proporcional ao investimento — nunca descartado nem duplicado.

> **Estado atual (exceção declarada, 2026-07-09):** no piloto Sigo essa reconciliação
> (`compute_resid()`) vive no **render-prep** (`_gerar-monitor.py`) por precedência histórica —
> ela nasceu antes do motor existir. É a única derivação fora do transform, tolerada porque o
> bloco `resid` é ADITIVO (as linhas cruas do fato não mudam). **Migração pro motor (derivado
> próprio) é backlog do modo `extensao`** — ao mexer nela, mover pra cá, não estender lá.
- Reconciliação só **completa faltantes, nunca desconta** (a origem pode supercontar por placement).
- Imprimir a **conservação** no stdout (total fato + resíduo = total CRM) — é o teste de que nada sumiu.
- Vereditos/decisões **arredondam** eventos fracionários (senão nada cruza thresholds).

## 7.5 Derivado `baseline-metricas` (fato de baselines do projeto)

Cubo **métrica × janela × estatística** materializado a cada rodada (`derivado/baseline-metricas.json`) — alimenta breakeven, forecast e análise (arquimedes/sobral/breakeven-builder/falconi) sem cada skill re-derivar baseline. Regras canônicas (decisão do operador, 2026-07-09 — não recalibrar por projeto sem decisão explícita):

- **Janelas**: todo período · 12m · 6m · 3m. **Estatísticas**: n_meses · **mediana (= o baseline)** · média · melhor · pior.
- **Mês corrente (parcial) sempre excluído**; melhor/pior só com **n ≥ 3 meses**; mês só entra na série da métrica com **denominador ≥ n_min** declarado (ex.: leads≥10 p/ CPL, cli≥1 p/ ticket).
- **Métricas de safra maturam**: roas/ticket/fundo de funil excluem os `maturidade_min_meses` (premissa: 2) últimos meses fechados — safra imatura mente.
- **Início de série = 1º mês com valor > 0**: zero ANTES do tracking existir é artefato de implantação (registrar a data em `quebras_de_serie`); zero DEPOIS é mês ruim real e conta. Caso vivo Sigo: win desde 2025-01, receita limpa desde 2025-09 — sem essa regra o ROAS "todo período" dava mediana 0.
- **Receita declarada por métrica** (bloco `receita:` do contrato): recorrente (`value_mensalidade`) · pontual (`value_implementação`) · composta (TCV = `tcv_meses`×mens+impl, do config). Projeto declara o que EXISTE; ROAS/ticket citam qual fórmula usam.
- **Métrica sem input existe como AUSENTE declarada** (`metricas_ausentes` com o motivo), nunca inventada — ex. Sigo: recompra/ARPU/ticket-cotações.
- **Recompra/retenção (projetos que têm)**: nunca 1 número de "taxa em 12m" sobre coorte fechada (pouco n) — derive a **curva de recompra por idade da coorte** (T3/T6/T12 acumulados, cada ponto usando só coortes que viveram até aquela idade, com `n` declarado). T3 é leading indicator do T12; T12 honesto vem só de coorte fechada. Share recompra e recorrências/ano seguem a mesma âncora de safra.
- Declarado que entra no config pra isso: `contrato_inicio` (LT do projeto DERIVA dele) — nada de digitar ROAS/ticket/taxa no config (segunda verdade que envelhece).

## 8. Config financeiro (declarado × derivado × premissa)

`config-financeiro.yml` com **blocos de vigência** (`de:` + valores; append-only — nunca editar vigência passada, sempre abrir bloco novo). Regra de ouro: **se dá pra calcular do dado → derivado** (ticket, ciclo); **se só o operador/cliente sabe → declarado** (fee, margem, budget, pré/pós-pago); **intermediário → `premissa:`** (motor prefere dado real quando passar a existir). O loader expande vigências pra série mensal em runtime; valores nunca são copiados pra dentro de script.

## 9. Checklist de saída do transform (toda rodada)

- [ ] `derivado/fato-*.csv` materializado com datas ISO + números com ponto (formato máquina, não BR).
- [ ] `derivado/qa-report.json` gravado com timestamp + linhas + achados.
- [ ] Sentinela verificada (presente = excluída; ausente = WARN alto).
- [ ] Stdout com resumo de 1 linha (linhas fato · ads na dim · achados QA) — sem emoji (console cp1252).
- [ ] Nenhum derivado com PII quando o raw de origem tem PII: derivar **agregando** (grão anúncio/dia) torna commitável; se o derivado precisar de linha-lead, é PII → gitignore.
