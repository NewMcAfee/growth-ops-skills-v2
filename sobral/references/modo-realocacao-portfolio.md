# Modo `realocacao` — Gestão de Portfólio de Mídia Orientada a Indicador

> Detalhe operacional do modo `realocacao` do `sobral`. **Doutrina canônica completa** (com a derivação, as 5 leis, referências de mercado e o roadmap de versões) vive na tese cross-projeto:
> `C:\Users\mcafe\OneDrive\Documentos\Claude\Projects\04_estudos\Gestão de Portfólio de Mídia\tese-portfolio-midia-v0.1.md`
> **Motor de cálculo** (helper determinístico, reutilizável): `…\04_estudos\Gestão de Portfólio de Mídia\motor-portfolio-v0.3.ps1`

## O que é (vs modo `padrao`)

| | `padrao` | `realocacao` |
|---|---|---|
| Quando | 1×, greenfield, Subfase 1.4.2 da Fundação | Recorrente (mensal + semanal) |
| Inputs formais | GTM Plan + Cenário Baseline + Taxonomia… | **Orçamento + indicador-alvo + período** (3 params do operador) + feed real |
| Fonte de dado | benchmark / premissas | **feed de performance real** (CSV granular dia×anúncio) |
| Lógica | alocação tática por canal/ICP/etapa | **alocação por retorno marginal** (portfólio) |
| Output | `plano-midia.md` + `forecasting.md` (trimestral) | `30-decisoes/YYYY-MM-DD-realocacao-*.md` (decisão datada mensal) |

Não substitui o `padrao` nem os planos trimestrais — é a realocação data-driven do ciclo.

## Mandato (M0)

- **Indicador-alvo único e puro, definido por projeto** = o que o cliente acompanha como sucesso.
- Lista canônica: `lead · mql · sal · sql · demo_agendada · demo_realizada · novos_clientes · roas · faturamento`.
- Sem ponderação de qualidade na v0.1 (decisão consciente). **Gatilho de troca:** se o pool entrega o alvo mas o resultado de negócio não vem (ex.: muitas demos, poucas vendas), o objetivo avança no funil (demo → venda/ROAS) e re-otimiza.

## Inputs

| # | Input | Severidade |
|---|---|---|
| 1 | Orçamento do ciclo (R$) | blocker |
| 2 | Indicador-alvo (da lista) | blocker |
| 3 | Período (mês) | blocker |
| 4 | Feed de performance real — CSV granular dia×anúncio (`90-referencias/dados-fonte/` ou equivalente do projeto) com Canal/Campanha/Conjunto/Anúncio/Investimento + colunas de funil até o indicador | blocker |
| 5 | (cond.) CRM para lag de maturação | alto |

## Workflow (8 passos — executados pelo motor + julgamento)

0. **Normalizar** — dedup de linhas-resumo que duplicam investimento; limpar moeda/%/corrupção; tratar outliers; classificar cada linha em canal/temperatura/pool.
1. **Sinal por pool** — CP-{alvo} por janela (ano·tri·mês·30d), ponderado por recência; tendência; volatilidade.
1.5. **Maturação de safra** — descontar/excluir coortes mais novas que a janela de maturação (lag lead→evento); a projeção sem isso é piso.
2. **Marginal & saturação** — `cp_marginal = cp_base × (1+over)^β`, **β=1**, `over` mordendo **só acima do gasto mensal já provado (Ref)**. `cp_base` = CP-{alvo} do **cenário típico maduro** (exclui mês outlier e safra imatura).
3. **Camada estratégica (M4)** — **piso por temperatura** (ex.: Frio 85 / Morno 10 / Quente 5); piso é alvo **limitado pela capacidade** da audiência (forçar acima satura).
4. **Camada tática (M4)** — dentro de cada temperatura, **water-filling equimarginal** entre os pools, respeitando saturação.
5. **100% alocado** — sem reserva estática; exploração/ajuste via rebalanceamento semanal.
6. **Pisos de aprendizado** — mínimo por pool p/ algoritmos de plataforma (PMax/Advantage+) saírem do learning.
7. **Forecast** — projeção do indicador em 3 cenários; **cenário (sazonal/leilão) = swing exógeno → FAIXA**, não meta. Decompor mês outlier em estrutura vs cenário (shift-share).

## Calibração obrigatória (back-test)

A projeção da estrutura **não pode ser menor que o realizado recente** (piso). Se ficar abaixo, a curva de saturação está mal calibrada — revisar β/Ref. Validar antes de publicar.

## Cadência (D4)

- **Mensal — entre canais:** decidido na janela **dia 25 → dia 1**.
- **Semanal — dentro do canal:** redistribui entre campanhas da mesma temperatura (faz o papel de exploração).

## Output

Decisão datada `30-decisoes/YYYY-MM-DD-realocacao-<periodo>.md` (Decision Doc Template: DECISÃO + WHY + CONSEQUÊNCIA + VALIDADE + DONO + EXCEÇÕES + AÇÕES ESTRUTURAIS + CONFIG TÉCNICA + FORECAST + CASCATA). **Não revoga** o Plano de Mídia/Forecasting trimestral. Exemplo materializado: `01_assessoria/Sigo ERP/30-decisoes/2026-06-26-realocacao-portfolio-midia-julho.md`.

## Roadmap (v0.1 → v0.2+, NÃO implementar agora)

- Ponderação de qualidade no mandato (indicador ajustado pela conversão downstream) + guardrails por estágio.
- Curva de maturação de safra calibrada com dado de lag limpo.
- Refino dos % de temperatura pela capacidade real de cada audiência.
- Regra de graduação de teste (quando um conjunto novo vira validado).
- Evolução para MMM bayesiano / testes de incrementalidade quando o volume permitir.
