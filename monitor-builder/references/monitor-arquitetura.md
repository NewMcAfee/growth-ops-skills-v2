# Arquitetura — engenharia inegociável

A engenharia é estável entre projetos; só os parâmetros (contrato) mudam. Preserve estes invariantes ao adaptar.

## 1. Dois arquivos, uma responsabilidade cada
- **`_gerar-monitor.py`** — lê os CSVs, faz parsing/limpeza, **emite um payload granular** + computa o OKR fixo do quarter. Não renderiza. Escreve **dois artefatos do mesmo payload `P`**: `monitor.html` (via `render`) e **`monitor.json`** (snapshot estruturado p/ skills de análise — ver `contrato-snapshot.md`). Lê as **metas do `contrato-cockpit.yml` em runtime** (`load_meta()`, `pyyaml` + fallback gracioso pro `META_DEFAULT`) — troca de quarter sem tocar código.
- **`_render_monitor.py`** — recebe o payload (`P`) e devolve o HTML completo (CSS inline + Chart.js + **toda a agregação em JS**). Não lê CSV.

`_gerar` importa `render` de `_render`. O feed roda só `_gerar` (que escreve HTML + JSON).

## 2. Payload granular interned (leve + sem PII)
- Emite **linhas granulares** (campanha diária; leads 1-por-linha), NÃO pré-agregados — pra os filtros recalcularem no browser.
- **Interning**: strings repetidas (campanha/conjunto/anúncio, segmento, motivo de perda) viram índice + tabela de lookup → payload 3-5× menor. Datas como ISO `YYYY-MM-DD`, booleanos 0/1.
- **Leads só com campos analíticos**: canal, segmento, datas das etapas, flags, valores. **NUNCA** nome/email/telefone/CNPJ. (Por isso o HTML pode embutir o CRM sem vazar PII — mas mesmo assim fica git-ignored.)
- Formato por tabela: `{cols:[...], rows:[[...]], <interned-lists>}`. O JS reconstrói objetos no boot.
- **Mesmo payload, dois consumidores:** `P` vira `monitor.html` (humano, agregação JS) **e** `monitor.json` (máquina, skills de análise — `json.dumps(P)` cru, schema em `contrato-snapshot.md`). Quem consome o JSON deriva safra/recortes do granular; não recomputa o cockpit.

## 3. Agregação em JS (filtros vivos)
- O JS decodifica o payload, mantém `FILT={period,canal,cmp}` e tem funções puras de agregação (`kpis`, `funil`, `cohort`, `drill`, `canais`, `velocidade`, `dreData`, `kpiSet`…) que filtram as linhas e recomputam.
- `renderAll()` re-renderiza todas as telas (innerHTML) + redesenha charts (destrói e recria instâncias Chart.js). Trocar filtro/aba chama `renderAll`/toggle.
- **OKR do quarter é fixo** (meta é trimestral, todos os canais) → pré-computado no Python, não reage a filtros. Sinalize isso na UI.
- **Séries temporais** (volume/eficiência/cohort/fechados) respeitam **Canal** mas não **Período** (são a visão temporal). KPIs/tabelas/funil respeitam ambos.

## 4. Single-file, zero build
- Um `.html` que abre direto no browser. CSS inline (tokens copiados do `00-sistema/design-system.css`). Chart.js + chartjs-plugin-datalabels via **CDN** (precisam de internet; tabelas/KPIs funcionam offline).
- Fontes/logo do operador via **path relativo** (`../../00-sistema/assets/...`) + fallback. Título via Google Fonts (Archivo) se a fonte do DS não couber.
- Charts: re-criados a cada `renderAll` (destrua os antigos pra não vazar instâncias).

## 5. Telas (componível pelo contrato)
8 telas no exemplo. Cada uma é uma `função rXxx()` que retorna HTML + uma `<section class="screen">`. Nav vertical à esquerda. Subtabs (drill/cohort/termos) com wiring próprio. Desligue uma tela se o projeto não tem o dado (ex: sem FEE → sem Mensal/DRE; sem termos → seção some sozinha).

## 6. Loop de validação (Playwright)
`file://` é bloqueado no Playwright MCP → suba `python -m http.server <porta>` **na raiz do vault** (pra preservar os paths relativos das fontes) e navegue em `http://localhost:<porta>/.../monitor.html`. Gate: console sem erro (favicon 404 OK), telas renderizam, números batem com sanity-check dos CSVs, troca de filtro/aba recalcula. Screenshot 2-3 telas.

## 7. Plug no feed
`_atualizar-dados.ps1`, depois de sobrescrever os CSVs, chama `python _gerar-monitor.py` num `try/catch` que loga WARN mas **não derruba o feed** (os CSVs já foram salvos). Assim o monitor regenera a cada execução do feed, sem tarefa separada.
