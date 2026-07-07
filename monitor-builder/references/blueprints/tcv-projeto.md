# Blueprint — TCV / Projeto (one-shot de ticket alto, ciclo longo)

> **PARCIALMENTE VALIDADO (Colina 2026-07-02, BUs Jazigo/Serviços em cockpit híbrido):**
> confirmados — **TCV = valor cheio do contrato mesmo parcelado** · **n pequeno exige
> janela longa** (preset default maior; veredito por canal/campanha só com volume
> mínimo antes de sentenciar) · TCV entra inteiro no M0 do payback da safra.
> Ainda por exercitar em cliente TCV-puro: pipeline aberto ponderado por probabilidade,
> aging por etapa, tabela nominal de deals grandes. Modelo: poucos deals, ticket alto
> (obra, projeto, contrato único), ciclo de semanas/meses. A pergunta do gestor:
> "quanto TCV entrou, quanto está em jogo no pipeline e onde ele envelhece?".

## Sinais de que é este blueprint

Dezenas (não milhares) de deals/quarter; `total_value` = valor total do contrato (TCV);
ciclo mediano > 2 semanas; won/lost demora a bater com o mês da criação.

## Cruzamento backend

- **TCV no grão de deal**; nada de MRR nem recompra por lead (expansão de cliente
  existente pode existir — trate como dimensão `novo × expansão`, não cohort).
- **Duas datas, duas leituras**: criação (geração de pipeline) vs fechamento (receita).
  Séries mensais devem existir NAS DUAS bases — o gestor pergunta as duas coisas.
- **Pipeline aberto ponderado**: valor em aberto × probabilidade por etapa (do contrato);
  com poucos deals, mediana/percentil > média (1 outlier distorce tudo).
- **Aging**: dias na etapa atual; balde >P75 = alerta.

## Telas típicas

| Tela | Conteúdo | Origem dos componentes |
|---|---|---|
| Visão Geral | TCV ganho, nº contratos, ticket médio, invest, CAC, ROAS, pipeline aberto (bruto e ponderado) | card OKR + pro-rata + pacing |
| Pipeline | funil de valor por etapa + aging por etapa + deals paradas (lista nominal — são poucas) | funil vertical + dim-table + tabela nominal |
| Atenção | veredito por canal + pontos cegos + deals grandes envelhecendo | veredito 3 col + pontos cegos |
| Mídia | invest × TCV por canal/campanha (cautela: n pequeno → janela longa default) | dim-table + drill |
| Mensal | TCV fechado por mês (toggle Volume↔Receita) + DRE | DRE transposta + toggle |

## Contrato — blocos-chave

`metas{tcv, contratos, ticket_medio, investimento, roas_min, cac_max}` ·
`probabilidade_por_etapa{}` (pro pipeline ponderado) · `janela_default: quarter`
(períodos curtos são ruído neste modelo — o preset default deve ser maior).

## Cautelas específicas

1. Meta pro-rata em janela diária/semanal é quase sempre ruído aqui — manter o
   princípio, mas o blueprint recomenda presets mínimos de mês.
2. Veredito Cortar/Escalar precisa de n mínimo (ex.: ≥5 deals) antes de sentenciar canal.
3. Deal única gigante = anotar nominalmente no monitor (não deixar o agregado esconder).
