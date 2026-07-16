# Referência — Monitor Sigo ERP (padrão VIGENTE: dados-fonte 2.0, v6.4)

Exemplo canônico do **modo monitor v3** (só render sobre a camada derivada) e do blueprint
**`recorrencia`** (SaaS B2B: funil demo/SDR, safra de mensalidade, DRE de payback).
1º monitor do padrão (jun/2026) · retrofit UX 2026-07-02 (v5) · **upgrade dados-fonte 2.0
+ F5.1/F5.2 em 2026-07-09 (v6.4, este re-sync)**.

## Arquivos (código real, pronto pra clonar)

| Arquivo | O que é |
|---|---|
| `_gerar-monitor.py` | **Render-prep** (v6.x): `load_fato()` lê `derivado/`, importa helpers do `_transform.py`, monta payload interned + `P.dim`/`P.brk`/`P.lib` + OKR da vigência + reconciliação CRM×campanhas + `monitor.json`. **Zero join próprio.** |
| `_render_monitor.py` | Cockpit 10 telas decision-first + filtros Google-Ads-style + sort clicável + selects cascata + popup de criativo + rateio `*`. |
| `_transform.py` | **Dependência de leitura** (domínio do `motor-dados-vault`): o gerador importa `br_num/pdate/iso/istrue/canal_norm` daqui. Incluído pra entender a interface; ao replicar, o transform nasce pelo `motor-dados-vault`. |
| `contrato-cockpit.yml` | Funil (MQL=SAL), metas OKR c/ `quarter_vigencia`, `canais_meta`, TCV recorrente (6×mens+impl). |
| `config-financeiro.yml` | **Vigências append-only** (fee/margem/tcv_meses/custo_tech + budget de mídia por canal + contas pré/pós-pago + alertas) — loader expande pra mensal; substituiu o CSV legado. |
| `contrato-dados-fonte.yml` | Manifesto da camada de dados (domínio do `motor-dados-vault`) — incluído pra ver o que o gerador pode assumir do `derivado/`. |

## As 10 telas (v6.4)

Visão Geral (OKR vigência + pace/**forecast adaptativo `natEnd()`** — projeta até o fim natural da janela do preset, rótulo com data-fim) · Atenção (pontos cegos + reconciliação + QA do transform + veredito) · Funil & Pipeline · Qualificadores (form heatmap + funil por SDR) · Safra (triângulo M0–Mn) · Mídia (drill com **selects cascata Campanha→Conjunto** + **filtro de texto** que carrega a campanha-mãe no filho + **clique no anúncio abre popup do criativo** via ANIDX) · **Criativos** (biblioteca: cards com preview `image_hash→adimages.url` fallback thumbnail, agrupado por nome, ordenável por SAL/invest/CP-SAL/demos/cli, popup imagem+headline+CTA+copy+métricas; URLs CDN renovam na extração das segundas) · **Debriefing** (2 tabelas full-width com subtabs Mensagem: consciência/gancho/avatar/formato/tema · Público: público/tipo/funil/temp/OBJ + **1 cruzamento único** com 3 selects atributo × público/entrega × métrica; colunas de entrega = funil **estimado por rateio** com `*`) · **Dimensões** (seletor único geo-meta/geo-google/cidades/idade/gênero/device/hora; Leads*/SAL*/CP-SAL* estimados) · Mensal/DRE (+CPL/CP-SAL/custo-demo ag/re; aviso: **âncora = MÊS DO EVENTO (calendário), não safra**).

## O que este exemplo demonstra (e os outros não)

1. **Separação transform×render** — o gerador não parseia nem cruza; consome fato/dim prontos. Números do monitor = números do derivado = números que as skills de análise leem (1 cálculo, N consumidores).
2. **Metas client-side com vigência** (`metaPeriodo()`/`periodMeta()`/`pacing()`) — pro-rata por dias, taxas não escalam, fora da vigência a meta some; `canais_meta: null` = meta da operação toda. Virada de quarter não trava a cadeia.
3. **Reconciliação CRM×campanhas no grão dia×anúncio** — resíduo distribuído fracionado, merge no `CAMP`; conservação no stdout; veredito arredonda; só volume (valor não se reconcilia).
4. **Rateio de funil por dimensão de entrega** — `P.brk.funil` (evento ad×mês) × share de spend; células `*`; real vs estimado sinalizado (a API Meta não dá conversão por breakdown).
5. **Biblioteca de criativos + debriefing por atributo** — `P.dim` (parse da taxonomia, gerações versionadas) + `P.lib` (copy/imagem do flow) cruzando mensagem×público×resultado.
6. **Qualificadores/SDR, KPI-card 3 camadas, sales velocity, top-N expansível, `lastDL`, `.qask`** — herdados do v5 (2026-07-02).

## Gotchas (não repetir)

- **PS 5.1 + stderr do python**: `& $py $gen 2>&1` com `ErrorActionPreference=Stop` converte QUALQUER linha de stderr em exceção — WARN benigno derrubou o render por 2 dias. Rodar via `cmd /c "python ... 2>&1"`, decidir pelo exit code; WARNs em STDOUT.
- **Console do feed é cp1252**: não printar `→`/emoji; usar ASCII/`·`.
- **Meta NUNCA no gerador** — quarter-fixo no Python foi a causa-raiz do travamento; meta vive no contrato, placar recalcula no cliente.
- **Origem pode SUPERCONTAR** (linha por placement): reconciliação só completa faltantes, nunca desconta; nota da UI diz "se aproximam do CRM".
- **NÃO estilizar `<canvas>` via CSS** — sizing pelo container (`.chwrap{position:relative;height:...}` + `maintainAspectRatio:false`).
- **Chart criado em aba `display:none`** fica no fallback → no handler das tabs, `requestAnimationFrame(()=>Object.values(CH).forEach(c=>c.resize()))`.
- **Subtabs com a mesma classe**: bind genérico sobrescreve onclick inline do 2º grupo → bind só em `.stbtn[data-st]`.
- **Grid+Chart.js** exige `.grid>*{min-width:0}`; **popup fecha no re-render** → `event.stopPropagation()`.
- **CSVs do flow usam ponto decimal** — `float()` puro, não `br_num` (que leria `2.0` como `20`).
