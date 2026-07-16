# Exemplo vivo — Sigo ERP (piloto dados-fonte 2.0, 2026-07-09)

> O caso que forjou a skill. Serve de referência de implementação — **nada daqui é
> lógica da skill**; cada vault tem contrato, âncoras e extensões próprios.

**Vault:** `...\01_assessoria\Sigo ERP\90-referencias\dados-fonte\`
**Decisão-mãe:** `30-decisoes/2026-07-09-dados-fonte-v2.md` (arquitetura ELT completa, fases F0-F8)

## Artefatos (clonar padrões daqui)

| Artefato | O que exemplifica |
|---|---|
| `contrato-dados-fonte.yml` | contrato completo: 6 tabelas, core×extensão, quebras de série, sentinela, extrações flow, achados_qa |
| `_transform.py` (~330 lin, stdlib pura) | motor completo: helpers de parsing como biblioteca importável, QA gates, âncora safra, parser taxonomia por geração, dim-criativo com copy do flow |
| `derivado/fato-ads-enriquecido.csv` + `dim-criativo.csv` + `qa-report.json` | os 3 derivados canônicos |
| `config-financeiro.yml` | vigências append-only, declarado×premissa, budget por canal, pré/pós-pago |
| `_atualizar-dados.ps1` | orquestrador da cadeia (estágio transform entre feed e render) |

## História do caso (o que provou a doutrina)

- **Corte de fórmulas materializou mid-execução** (~11h de 09/07): o export veio com todas as colunas cruzadas vazias e o monitor publicado zerou. O motor reconstruiu os joins do bruto no mesmo dia — a arquitetura ELT foi validada sob fogo.
- **Âncora safra por engenharia reversa:** a fórmula do growthpack contava eventos de funil no **dia de criação do lead** (flag TRUE + create_at), não na data do evento. Descoberta por golden test com 3 variantes contra o CSV congelado @ git HEAD: variante safra deu **cli e fat diff ZERO**; a variante "óbvia" (data do evento) divergia 10× (sql 1652 vs 177).
- **Gates pegaram sujeira real na 1ª rodada:** 21 deals com `deal_growthpack_id` duplicado no CRM (pendência na origem, avisada 2×) + 972 dups **idênticos benignos** no index (linha por keyword em legado Google) — o refinamento idêntico×conflitante nasceu desse alarme falso.
- **QA fora-de-vocab funcionou de fábrica:** 5 campanhas `TEST_GOOG_*` com TEMA no 5º campo onde a spec pede TEMPERATURA → fila de correção pro media-buyer.
- **Sentinela:** linha `{ad_id: manual, data: 08/12/1999}` (easter egg do operador — aniversário dele) na 1ª linha do bd_ads; excluída do cálculo, WARN alto se sumir.
- **Rateio de funil por share de spend** nasceu da lacuna da API Meta (sem conversão por breakdown; `actions` é ARRAY e o gateway bloqueia UNNEST) — células estimadas com `*`.

## Extensões específicas do Sigo (NÃO copiar como padrão)

- `temperatura` (dono: closer — projeção de SE/QUANDO fecha) e `score` (dono: SDR) no CRM.
- MQL=SAL na semântica do funil; demo = `show_meeting`; TCV = 6×mensalidade (só no DRE).
- `bd_buy` não existe (`presente: false`).
