# Blueprint — Recorrência / SaaS (assinatura, mensalidade contratual)

> **Exemplo: `../exemplos/sigo/` (Sigo ERP).** Retrofit 2026-07-02: o exemplo está no
> UX estado-da-arte do catálogo (metas client-side por vigência + pro-rata + pacing +
> chart-lg + reconciliação CRM×campanhas) — serve tanto pro **cruzamento backend do
> modelo** quanto de referência visual, junto do Martins.
> Modelo: receita = mensalidade recorrente + implementação one-shot. Funil longo com
> etapas de qualificação humana (SDR/demo). A pergunta do gestor: "quantas demos
> realizadas e quanto MRR novo, e quando o CAC se paga?".
>
> **Variante HÍBRIDA por BU (validada no Colina, 2026-07-02):** cliente com BUs
> recorrentes E BUs one-time no mesmo cockpit → NÃO escolher um blueprint só; compor
> via `receita.por_bu` no contrato (`{modelo: recorrente, mensalidade, ltv_meses}` vs
> `{modelo: tcv, valor}`). MRR Novo/Receita Contratada/LTV:CAC/payback derivam por BU.
> Sem dado de receita no CRM → **receita PREMISSA** (valores da fundação, selo visível,
> rota de troca no contrato). Ver `../exemplos/colina/README.md`.

## Sinais de que é este blueprint

Contrato com mensalidade; funil com demo/reunião como métrica-estrela; `total_value`
decomposto em `value_mensalidade` + `value_implementação`; churn relevante.

## Cruzamento backend

- **Funil mapeado etapa a etapa no contrato** (bloco `funil:` — cada projeto nomeia
  flags/datas diferente; ex. Sigo: coluna "MQL" das campanhas JÁ é o SAL). Métrica-estrela
  declarada (ex.: demo realizada = `show_meeting`).
- Lead ↔ anúncio via `ad_id` (campanhas = a verdade do CRM fatiada por anúncio).
- **Safra de mensalidade**: mês do `win` abre a safra; MRR da safra persiste nos meses
  seguintes (menos churn quando houver flag) → base do DRE de payback.
- Close-rate = clientes ÷ demos realizadas.

## Telas (v5 do exemplo Sigo — IA decision-first, cada tela com sua pergunta)

| Tela | Pergunta | Conteúdo | Origem dos componentes |
|---|---|---|---|
| Visão Geral | estou no ritmo da meta? | placar OKR (★ demos) c/ sparkline+pacing · trio Volume·Ritmo·Forecast · custos c/ alvo · sales velocity | okr-card 3 camadas + trio Colina + velocity (catálogo §UX) |
| Atenção | o que precisa de ação? | pontos cegos de dado + reconciliação campanhas×CRM + veredito Cortar/Escalar | kb cards + recon + veredito 3 col |
| Funil & Pipeline | onde o funil trava? | funil período + pipeline por stage REAL + velocidade 180d + perdas (lost_at) | funil vertical + ritmo |
| Qualificadores | quem converte melhor? | funil por resposta do form (heatmap) + evolução + funil por SDR | tela Qualificadores (catálogo §UX) |
| Safra / MRR | as coortes maturam? | triângulo M0–Mn + mensalidade por safra | heatmap cohort |
| Mídia | onde o dinheiro trabalha? | canal + drill full-funnel (CPL/freq) + termos c/ impression share | dim-table + drill + expWrap |
| Mensal / DRE | o projeto se paga? | DRE competência + payback + meta mensal na vigência | DRE transposta |

## Contrato — blocos-chave

`funil{etapa: {flag, date}}` (o coração) · `campos_valor{mensalidade, implementacao}` ·
métrica-estrela + meta mensal · `config-financeiro.csv` (custos p/ DRE de payback).

## KPIs que NÃO fazem sentido aqui

Taxa de recompra por lead (recompra = renovação contratual, não novo deal), frente de
negócio por keyword de campanha (produto único), CAC blended sem separar implementação.
