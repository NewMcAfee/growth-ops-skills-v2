
# monitor-builder · Modo Monitor — Forjador de cockpit vivo (ex-cockpit-builder)

## Contexto

Existe um padrão validado (Sigo ERP, jun/2026) de **cockpit operacional vivo**: um `monitor.html` auto-contido que o gestor abre pra entender *como está, o que priorizar, o que cortar/escalar*, e que **regenera sozinho** toda vez que o feed diário sobrescreve os CSVs. Esta skill **replica esse padrão pra qualquer projeto**, parametrizando o que muda por cliente (definições de funil, metas, fórmula de receita, canais) num **contrato** — sem reescrever a engenharia do zero.

A skill NÃO inventa dado nem analisa: ela **constrói a ferramenta** (gerador `_gerar-monitor.py` + renderer `_render_monitor.py`) e a pluga no feed. O CRM é a verdade (lead→venda); campanhas é a mesma verdade fatiada por anúncio (join `ad_id`).

**Arquitetura inegociável** (detalhe em `references/monitor-arquitetura.md`):
- Gerador Python emite **dados granulares interned** (campanha diária + leads **só com campos analíticos**) e **agregação roda em JS** → filtros recalculam ao vivo, load instantâneo (sem servidor).
- **Single-file**: zero build, Chart.js via CDN, identidade lida do `00-sistema/design-system.css`.
- **PII nunca no HTML**: nada de nome/email/telefone/CNPJ embutido. `monitor.html` git-ignored; os `.py` commitáveis.

## Workflow (7 passos)

### Passo 0 — Blueprint + contrato do projeto (parametrização) — BLOQUEANTE
**Primeiro, escolha o blueprint pelo modelo de negócio do cliente** (`references/blueprints/`): `aquisicao-recompra` (transacional de alta frequência — ex. Martins) · `recorrencia` (assinatura/mensalidade — ex. Sigo) · `tcv-projeto` (one-shot ticket alto, ciclo longo — draft). O blueprint dita telas, KPIs, o cruzamento do gerador e os blocos do contrato. Em dúvida entre dois, pergunte ao operador qual pergunta o gestor faz ("cliente novo volta?" vs "quanto MRR?" vs "quanto TCV em jogo?").

Depois, **leia `references/monitor-contrato-projeto.md`** e produza/preencha um `contrato-cockpit.yml` na `dados-fonte/` do projeto-alvo. Pra isso:
1. `Read` os headers dos CSVs do feed do alvo (`campanhas-*.csv`, `crm-*.csv`, `termos-*.csv` se houver).
2. Com o operador, trave o **mapeamento campo-CRM→etapa-de-funil** e o **evento de conversão** — é o ponto que mais varia. Ex Sigo: "MQL operacional = SAL = flag `sal`"; a coluna "MQL" do campanhas JÁ é o SAL.
3. Trave **estrela + metas OKR** (métrica-estrela mensal, metas por quarter, taxas-alvo, **`quarter_vigencia`**), **fórmula de TCV** (recorrente: N×mensalidade+impl; one-shot: total_value), **lista de canais** e **MIN_ANO** (corte de outliers). O bloco `metas` é **lido em runtime** — avise o operador que trocar de quarter = editar só esse bloco do `.yml`, sem tocar no código.
4. Se algo essencial não está claro, **pergunte** — não assuma. Contrato errado quebra todo o downstream.

### Passo 1 — Forjar gerador + renderer
**Ponto de partida: `references/exemplos/martins/`** (estado-da-arte de visual/UX/filtros/metas) compondo com o **catálogo de componentes** (`references/monitor-biblioteca.md`) — cada componente lá tem identificadores estáveis e contrato de dados. O **cruzamento backend** vem do blueprint escolhido (pra `recorrencia`, o `exemplos/sigo/` é a referência do backend; o visual continua vindo do Martins/catálogo). Copie os 2 `.py` pra `dados-fonte/` do alvo e **adapte conforme o contrato**:
- Reescreva o bloco de constantes/`MIN_ANO`/paths. As **metas NÃO são hardcoded**: `load_meta()` lê o bloco `metas` do `contrato-cockpit.yml` em runtime (`pyyaml` + fallback pro `META_DEFAULT`) — materialize o `contrato-cockpit.yml` no projeto-alvo (Passo 0).
- Reescreva os **nomes de campo** (parsing de campanhas e CRM) conforme o `funil:` do contrato — `references/monitor-data-realities.md` lista exatamente quais trechos mapeiam quais chaves.
- Ajuste a fórmula de `tcvOf` à fórmula do contrato.
- Mantenha intacta a engenharia (interned payload, **emissão do `monitor.json`** no `main()`, agregação JS, telas, filtros) — só os parâmetros mudam.

### Passo 2 — Config financeiro (se DRE)
Crie `config-financeiro.csv` (`mes,fee,margem,tcv_meses,outras_receitas,outros_custos`), 1 linha/mês desde o início do projeto. Sem FEE/DRE no escopo? Pule e desligue a aba Mensal.

### Passo 3 — Plugar no feed + governança
- Edite (ou crie) `_atualizar-dados.ps1` pra chamar `python _gerar-monitor.py` **no fim** (após sobrescrever CSVs), em `try/catch` que não derruba o feed.
- `.gitignore`: adicione `monitor.html` **e `monitor.json`** (ambos embutem comportamento do CRM) + o CSV de CRM + `__pycache__/`. Os `.py`, o `contrato-cockpit.yml` e o config são commitáveis.

### Passo 4 — Gerar + validar (loop de feedback obrigatório)
1. `python _gerar-monitor.py` → confere stdout (sem traceback; sem WARN de `pyyaml`/contrato ausente) e que **`monitor.json` foi escrito e é JSON válido** (`python -c "import json;json.load(open('monitor.json',encoding='utf-8'))"`).
2. Suba `python -m http.server` na raiz do vault e abra `monitor.html` via Playwright MCP (file:// é bloqueado).
3. **Gate**: console **sem erros** (favicon 404 OK); cada tela renderiza; números batem com sanity-check dos CSVs (rode um `python -c` cruzando totais). Screenshot de 2-3 telas (Visão Geral, a aba mais complexa, uma com filtro aplicado) e confira visualmente.
4. Teste 1 troca de filtro (canal/período) e 1 troca de aba — devem recalcular sem erro.

### Passo 5 — Cascata sináptica
Atualize `mapa.md` da pasta (novos arquivos), o ponteiro no `claude.md` raiz (Mapa de Outputs), e grave/atualize a memória project-specific com as definições canônicas travadas no Passo 0.

### Passo 6 — Colheita pra biblioteca (obrigatório em construção E atualização)
A biblioteca só se mantém viva se todo monitor devolver o que aprendeu. Antes de encerrar, faça o diff **do que você construiu vs o que a biblioteca já tem** e proponha ao operador (não materialize sozinho):

1. **Componente/lógica novo** que não existe no catálogo → propor entrada em `monitor-biblioteca.md` (com identificadores estáveis + contrato de dados + gotchas).
2. **Variação por modelo de negócio** descoberta → propor no blueprint correspondente (e se o blueprint era draft — ex. `tcv-projeto` — corrigi-lo contra a realidade e remover a marca de draft no que se confirmou).
3. **Melhoria num componente existente** (bug, UX, edge case) → propor atualização da entrada no catálogo E listar os monitores existentes que a carregam desatualizada (candidatos a retrofit).
4. **Gotcha novo** → seção de gotchas do exemplo/SKILL.md.
5. Se o monitor construído **supera o exemplo canônico** em algum aspecto validado pelo operador → propor re-sync ou troca do exemplo.

Formato: lista curta "item → destino proposto" no fechamento da sessão (mesmo espírito da síntese de curadoria do CLAUDE.md global). **Quando existir o kit físico (`assets/monitor-kit/`, Fase 2): componente usado por 2+ monitores é candidato a extração pro kit** — anotar o segundo uso é exatamente o gatilho.

## Padrão de output

Arquivos entregues em `<vault>/90-referencias/dados-fonte/` (ou onde mora o feed):
- `_gerar-monitor.py` + `_render_monitor.py` (commitáveis) · `config-financeiro.csv` (commitável) · `contrato-cockpit.yml` (commitável; bloco `metas` lido em runtime) · `monitor.html` **+ `monitor.json`** (git-ignored, regeneram no feed — o `.json` é o snapshot p/ skills de análise; schema em `references/monitor-contrato-snapshot.md`).

Telas do monitor (todas no exemplo): **Visão Geral** (OKR quarter fixo + pace/projeção + pipeline em aberto por etapa + KPIs + qualidade) · **KPIs** (grid com Δ%) · **Decisão** (Cortar/Escalar/Investigar) · **Funil & Qualidade** (funil + velocidade entre-etapas + leads/semana por status + perdas) · **Safra** (triângulo de maturação M0–Mn, métrica trocável) · **Mídia** (canal + charts + drill campanha→conjunto→anúncio + termos) · **Mensal/DRE** (competência + breakeven + payback) · **Segmentos**. Filtros: Período · Canal (multi) · Comparar (Δ%).

## Regras Aplicadas (estado da arte incorporado)

Leia `references/monitor-data-realities.md` pro detalhe operacional. Síntese das regras que NÃO podem faltar:

| Regra | Origem | Como aplica |
|---|---|---|
| **Volume via flags, timing via `_at`** | dado real: datas de meio-de-funil vêm esparsas | Contagem de etapa usa o flag; tempo-de-ciclo usa `_at` e exibe `n` (amostra). Nunca dependa de `_at` pra volume. |
| **Cohort-payback é ferramenta financeira** | SaaS cohort best-practice 2025 ([fiscallion](https://www.fiscallion.io/blog/saas-cohort-analysis-how-to-turn-retention-data-into-decisions)) | Triângulo de maturação M0–Mn com CAC/receita/conversão por maturidade; payback = resultado acumulado ≥ 0. |
| **M0–M2 <75% → consertar funil antes de escalar CAC** | cohort best-practice 2025 | A camada Decisão prioriza gargalo de conversão sobre volume; pace vs meta deixa o gargalo explícito. |
| **CAC payback benchmark ~16m (mediana SaaS 2025)** | [getaleph](https://www.getaleph.com/answers/cac-payback-period-saas-2026) | DRE de payback contextualiza; não trate vermelho como falha sem checar a janela. |
| **Load <3s, pré-agregação** | dashboard best-practice ([aceinfoway](https://www.aceinfoway.com/blog/big-data-dashboard-design-practices)) | Dado embutido + agregação client-side = instantâneo; interning pra payload leve. |
| **~10 KPIs core, não tudo** | SaaS KPI framework 2025 | KPIs agrupados (Resultado/Volume/Taxas/Custos); evite poluição. |
| **Receita faltante ≠ prejuízo** | dado real Sigo | Sem o campo de receita → "s/ receita" mudo, não "Faltou". Flag o backfill. |
| **Outliers de data** | dado real (linhas de 1999) | `MIN_ANO` descarta lixo pré-início. |
| **Colunas opcionais tolerantes** | dado real (impressões/termos chegam depois) | Leia com fallback 0/None; a feature "acende" quando a fonte preenche; some se ausente. |
| **PII nunca no HTML** | princípio Avo / LGPD | Payload de leads só com campos analíticos; HTML git-ignored. |

## Anti-patterns (não faça)

- ❌ **Hardcodar o cliente-gatilho.** Tudo que varia por projeto vive no contrato (Passo 0). Sigo é exemplo em `references/`, não default.
- ❌ **Servidor / build / framework.** Single-file estático, vanilla JS + Chart.js CDN. Zero React/webpack/Node.
- ❌ **PII embutida** (nome/email/telefone/CNPJ) no payload ou HTML. Só campos analíticos.
- ❌ **Confundir flag e `_at`** pra contagem de volume (subconta etapa).
- ❌ **Ler "MQL" sem confirmar a definição.** O evento de conversão é project-specific (Sigo: MQL=SAL). Confirmar no Passo 0.
- ❌ **Entregar sem validar no browser.** O gate Playwright (console limpo + números batendo) é obrigatório.
- ❌ **Duplicar `darwin`/`newton`.** A seção de termos/análise no monitor é leve/operacional; análise profunda fica nas skills donas.
- ❌ **Esquecer a cascata** (mapa.md/claude.md/memória) — drift degrada o vault.

## Avaliação

### Cenário 1 — Replicar num projeto novo (recorrente)
**Input:** operador aponta `dados-fonte/` de um cliente SaaS com `campanhas-*.csv` + `crm-*.csv`, conversão = "lead qualificado" (campo `qualified`), TCV = 12×mensalidade.
**Esperado:**
- [ ] Passo 0 produz `contrato-cockpit.yml` com o mapeamento de funil e TCV 12×.
- [ ] Gera `_gerar-monitor.py`+`_render_monitor.py` adaptados (sem field-name do Sigo).
- [ ] `monitor.html` renderiza, console limpo, números batem.
- [ ] Plugado no feed + git-ignore + cascata.

### Cenário 2 — Projeto one-shot (sem recorrência)
**Input:** cliente de ticket único (sem mensalidade); sem FEE de assessoria informado.
**Esperado:**
- [ ] TCV = total_value (não N×mensalidade); aba Mensal/DRE desligada ou só com mídia.
- [ ] Não inventa receita recorrente; flag claro do escopo.

### Cenário 3 — Recusa correta
**Input:** "renderiza o dashboard do snapshot `dados-brutos-google-60d.md`".
**Esperado:**
- [ ] Recusa e redireciona pra `monitor-builder` (snapshot curado ≠ monitor vivo de feed).

> Detalhes: `references/monitor-contrato-projeto.md` (schema do contrato + exemplo Sigo) · `references/monitor-contrato-snapshot.md` (schema do `monitor.json` p/ skills consumidoras) · `references/monitor-arquitetura.md` (engenharia) · `references/monitor-data-realities.md` (regras de dado) · `references/exemplos/sigo/` (implementação de referência completa).
