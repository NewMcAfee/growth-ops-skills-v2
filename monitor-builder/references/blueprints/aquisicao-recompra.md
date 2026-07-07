# Blueprint — Aquisição × Recompra (B2C/B2B transacional de alta frequência)

> **Exemplo canônico: `../exemplos/martins/` (locação de equipamentos).**
> Modelo: cliente compra, e o valor do negócio está em ele VOLTAR. Receita = 1ª compra
> (aquisição, movida por mídia) + recompras (retenção). Ticket baixo/médio, ciclo curto,
> alto volume de deals.

## Sinais de que é este blueprint

Growthpack/CRM com muitos deals pequenos por cliente; mesmo lead ganha mais de uma vez;
pergunta central do gestor: "quanto custa um cliente NOVO e quanto ele devolve depois?".

## Variante — B2B consultivo + one-shot (ex: Aquatro Suprimentos, jul/2026)

Nem toda aquisição-recompra é transacional de alta frequência como Martins. A **Aquatro**
(distribuição B2B de suprimentos) é aquisição-recompra, mas na fase inicial tem **funil
consultivo com qualificação** (SDR/CRM) e **venda one-shot** (`total_value`, sem mensalidade):
- **Funil simples do cliente**: `Lead → MQL → SQL → Ganho/Perdido` — confirmar com o operador
  quais flags (na Aquatro: MQL = flag `mql`, não `sal`; sem etapas de demo). Não force o funil
  demo/SDR do Sigo; colapse as etapas que o cliente não usa (nos cards OKR, funVolCard,
  funilRange, velocidade e séries).
- **Receita one-shot**: `fatOf()` = `total_value`; `mensOf()` = 0; **desligar a aba Mensal/DRE**
  (sem FEE/recorrência) — remover do nav + section + chamada no `renderAll()`.
- **Recompra "acende depois"**: a dimensão de recompra do blueprint (cohort por 1ª compra) fica
  quase vazia até haver volume — mantê-la mas não fazer dela a tela principal na fase de teste.
- **KRs** costumam ser Investimento + MQL + SQL (não demos/clientes) — remapear os slots do placar
  (`demos_real` → MQL/estrela; `demos_agend` → SQL) e deixar clientes/valor sem meta (`0` → card
  mostra realizado; guardar divisões por zero em `TGT_CAC`/`TGT_CUSTO_DEMO`).

## Cruzamento backend (o coração do `_gerar-monitor.py`)

- **Classificação por `lead_id`**: 1º ganho lifetime (menor `crosed_at`) = **aquisição**;
  demais ganhos do mesmo lead = **recompra**. Lifetime classifica; o período recorta.
- Canal do ganho via join `deal_id` → pipeline (bd_buy não carrega canal).
- KRs do OKR contam **só `canais_meta`** (a "máquina de aquisição" é mídia paga).
- Frente/linha de negócio: campanha→frente por keyword; deal→frente por funil/produto.

## Telas (SCR)

| Tela | Conteúdo | Componentes do catálogo |
|---|---|---|
| Visão Geral | 12 cards: fat/ticket de 1ª compra, fat/ticket de recompra, invest, novos clientes, CAC, recompras, fat total, ROAS, hit-rate, taxa de recompra + 2 charts mensais | card OKR + pro-rata + pacing; combo invest×fat×ROAS; volume aq×rc |
| Atenção | pontos cegos de dado + veredito por canal + veredito por frente | pontos cegos; veredito 3 col ×2; detector clickid |
| Funil & Perdas | funil volume/valor, motivos de perda, velocidade, por origem/canal, qualificadores temporais | funil vertical; dim-table; velocidade |
| Recompra | cohort por safra de 1ª compra (taxa/valor), filtrável por frente | heatmap cohort + subtabs |
| Mídia | invest por canal + invest×retorno por frente + drill campanha/conjunto/anúncio | dim-tables; porFrenteRows |
| Produtos | win rate/ciclo/share por produto + distribuição de ticket | dim-table; barras de faixa |
| Mensal | fechados mês/ano (toggle Volume↔Receita) + DRE com metas pro-rata | DRE transposta; toggle |

## Contrato (`contrato-cockpit.yml`) — blocos-chave

`eixos{chave_cliente: lead_id, data_ganho: crosed_at}` · `canais_meta` ·
`periodo{quarter, inicio, fim}` · `metas.aquisicao{faturamento, clientes, ticket_medio,
investimento, roas_min, cac_max}` (recompra pode ser `null` — monitora só realizado) ·
`fee{default, por_mes}` pro DRE.

## KPIs que NÃO fazem sentido aqui

MRR/churn/expansão (não é recorrência contratual), pipeline ponderado (ciclo é curto
demais), payback multi-mês de mensalidade.
