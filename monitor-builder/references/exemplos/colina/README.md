# Referência — Monitor Grupo Colina (cockpit híbrido recorrência + TCV)

2º monitor construído com o catálogo (2026-07-02, pós-Martins) — **exemplo canônico do
modelo HÍBRIDO por BU** (BUs recorrentes + BUs one-time/TCV no mesmo cockpit) e das
capacidades novas: **mês fiscal customizado**, **receita premissa**, **atribuição de
funil ao drill** e **snapshot analítico anexado pelo renderer**. Visual/UX/filtros
herdam o padrão Martins. Publicado em https://colina-monitor.pages.dev (deploy no
wrapper do feed, padrão da memória global `publicar-monitor-cloudflare-pages`).

## Arquivos (código real, pronto pra clonar)

| Arquivo | O que é |
|---|---|
| `_render_monitor.py` | Cockpit 7 telas (Visão Geral c/ receita premissa + trio volume·ritmo·forecast · Por BU c/ 6 mini-charts · Atenção · Funil & Perdas · Safra & Payback 3 visões · Mídia c/ drill atribuído · Mensal). No fim, **anexa `funil_atribuido_campanha_mes` ao monitor.json**. |
| `_gerar-monitor.py` | Snapshot determinístico (OKR por BU restrito a `canais_meta` + receita premissa). Roda antes do render. |
| `contrato-cockpit.yml` | Parametrização: BU (origem+fallback), `mes_fiscal`, metas mensais por BU, `receita.por_bu` híbrida (rec/tcv), rateio implícito, payback, vigência fiscal. |

## O que este exemplo demonstra (e o Martins não)

1. **Híbrido rec+TCV por BU** — `receita.por_bu`: `{modelo: recorrente, mensalidade, ltv_meses}` pros planos; `{modelo: tcv, valor}` pro one-time (contrato cheio mesmo parcelado). MRR Novo, Receita Contratada e LTV:CAC derivam disso.
2. **Receita PREMISSA** — `total_value` vazio no CRM → valores da fundação com selo `PREMISSA` visível; trocar `receita.fonte` quando o dado real chegar (sem tocar código).
3. **Mês fiscal 16→15 nomeado pelo fim** — helpers `fm_key()` (Python) e `fmKey/fmStart/fmEnd/fmAdd` (JS) substituem o mês civil em metas, presets ("Este mês" = fiscal vigente), série mensal, safras e payback. Vigência do quarter também fiscal.
4. **Rateio de canal indireto** — `manual_zendesk` não é canal: dividido entre `paid_meta`/`paid_google` pela taxa observada de `manual_*` com canal pago, POR BU (`rateia_mz()` determinístico no grão deal; fracionário nos agregados/bd_ads). **Silencioso na UI.**
5. **Atribuição de funil ao drill** (`_atribui()`) — MQL/SQL/Ganho do CRM, motor único, ancorados no **mês fiscal do LEAD** (não do win — evita "campanha sem invest com ganho" por lag) + trava: evento só assenta em criativo-mês **com investimento**. ad_id rastreável direto; resto proporcional aos rastreáveis do mês×BU×canal; fallback share de invest; sem base → sem atribuição. Conservação impressa no stdout.
6. **Snapshot analítico sem duplicação** — o renderer (que já computa a atribuição) anexa o bloco ao `monitor.json` após gerar o HTML (wrapper roda gerar→render, então o bloco sobrevive a toda rodada).
7. **Semáforo parametrizado** — `pctMeta/stPct`: ≥70% verde · 60–70% amarelo · <60% vermelho; métrica de CUSTO (CPMQL/CAC) usa conta **inversa** `meta/realizado`.
8. **Telas de referência ignoram o filtro de período** — Safra & Payback (3 visões: taxa conv · clientes acumulados · CAC da safra caindo com a maturação) e Mensal mostram sempre tudo; BU/canal aplicam. Medianas de tempo entre etapas em **janela fixa 180d vs 180d anteriores** (tiragem de período curto engana).

## Gotchas (não repetir)

- **Cozinha não vai pro cliente**: metodologia (atribuição, rateio, premissa) vive em comentário Python — nunca em nota no HTML **nem em comentário JS do template** (viaja no view-source).
- **CTR impossível** (cliques > impressões — 9 anúncios no bd_ads do Colina): exibir "—", não o número; reportar à origem. Guard: `v.impr && v.clk<=v.impr`.
- **Grid + Chart.js estoura horizontal** sem `.grid>*{min-width:0}` + `canvas{max-width:100%}`.
- **Preset "Este mês" termina em HOJE** → forecast deve projetar até o **fim do mês fiscal vigente** (senão nunca dispara).
- **BU multi-campo no CRM**: `origem` primário, `funnel` fallback (7,8% divergiam) — normalização única `bu_crm()` usada por TODOS os consumidores (funil, rateio, atribuição).
- Charts multi-métrica por BU são ilegíveis com escalas díspares → **6 mini-charts horizontais, 1 métrica/escala cada**.
