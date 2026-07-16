---
name: feed-planilha-vault
description: Monta e opera a camada de EXTRAÇÃO + ORQUESTRAÇÃO (dados-fonte 2.0) de um vault Growth IA Ops (Windows, zero-Claude) — feed de planilha Google pública → raw/, extração de warehouse flow via MCP JSON-RPC stdlib, cadeia agendada extract→transform→render→publish→notify, e report diário WhatsApp via Evolution API; com PII→gitignore, travas de sobrescrita atômica, QA da origem e tarefas agendadas robustas. Ative para bootstrap de feed novo, extensão de feed existente (aba/extração/estágio/report novo), ou auditoria de feeds (modo status). NÃO ative para criar contrato/transform/derivados (motor-dados-vault), renderizar monitor (monitor-builder), planilhas privadas com OAuth, fontes não-Google-Sheets sem MCP, análise de dados (newton/darwin/falconi), ou agendamento em cloud.
allowed-tools: Read,Write,Edit,Bash,PowerShell,AskUserQuestion
---

# feed-planilha-vault — Engenheiro da Camada de Extração (dados-fonte 2.0)

## Contexto

Na arquitetura **dados-fonte 2.0** (ELT), o vault é a camada de dados do projeto: fontes entregam **bruto**, um motor determinístico deriva, o monitor renderiza e o operador recebe report — tudo **zero-Claude** (scripts puros agendados; nenhuma sessão de LLM na cadeia). Esta skill é a dona das pontas: **extração** (planilha Google 2×/dia + warehouse flow às segundas → `raw/`) e **orquestração** (a cadeia `extract → transform → render → publish → notify`, com cada estágio degradando com WARN sem derrubar o que está de pé). O que erra num feed não é o download (trivial) — é a governança: PII vazando pro Git, dado corrompido passando batido, cadeia parada em silêncio, tarefa que não roda no laptop. A skill faz o feed **nascer auditável, seguro e encadeado**.

Antes de agir, **leia [references/regras-aplicadas.md](references/regras-aplicadas.md)** (R1-R16 — as invariantes). Caso vivo completo: [references/exemplo-sigo-erp.md](references/exemplo-sigo-erp.md).

## Posição na cadeia (bounded context)

```
feed-planilha-vault (ESTA)        motor-dados-vault            monitor-builder
extract → raw/  +  orquestra ───► contrato + transform ───►    render (monitor.*)
a cadeia inteira e o notify         → derivado/                 └► publish + notify (estágios DESTA)
```

| Fronteira | De quem é |
|---|---|
| **Baixar fontes, escrever `raw/`, orquestrar/agendar a cadeia, notify** | **esta skill** |
| Contrato de dados, `_transform.py`, `derivado/`, QA gates de join | `motor-dados-vault` |
| Gerador/renderer do monitor (`_gerar-monitor.py`/`_render_monitor.py`) | `monitor-builder` |
| Interpretar o dado | `newton`/`darwin`/`falconi` |

> **Exceção declarada de posse do orquestrador:** `motor-dados-vault` e `monitor-builder` **instalam o próprio estágio** (transform/render) no `_atualizar-dados.ps1` existente quando são executadas depois do feed — cada skill pluga o estágio que é dela, no padrão try/catch degradante + R12. Quem edita o `.ps1` **obedece R4** (UTF-8 com BOM): após qualquer edição, re-assegure o BOM (`[IO.File]::WriteAllText($p,(Get-Content $p -Raw -Encoding UTF8),(New-Object Text.UTF8Encoding($true)))`) e rode a cadeia 1× pra validar.

A cadeia é **incremental**: um vault pode ter só o feed (estágio 1) e ganhar transform/render/notify depois — o orquestrador pula estágio ausente com WARN.

> **Vault v1 sendo MIGRADO pro 2.0** (já tem feed antigo + monitor vivo com gerador fazendo joins)? Antes de mexer, siga o playbook canônico **`motor-dados-vault/references/migracao-v1-v2.md`** — ele define a ordem (baseline congelado → raw/ → contrato/motor → render), o handoff entre as 3 skills e os golden tests que protegem a lógica específica do projeto. Esta skill executa o Passo 1 de lá.

## Modos

- **setup** (default) — bootstrap do feed num projeto (planilha; + flow e notify se o projeto tem).
- **extensao** — aba nova, extração flow nova, estágio novo na cadeia, ou configurar o notify num feed existente.
- **status** — listar/auditar feeds (logs, tarefas, frescor, re-QA).

Detecte o modo pela intenção. Em dúvida, pergunte.

---

## Modo SETUP — passos

### Passo 0 — Coletar parâmetros (não pule)
Levante, perguntando o que faltar (AskUserQuestion para escolhas):
1. **Planilha**: link → ID (`/spreadsheets/d/{ID}/`); **abas** exatas (case-sensitive); horários (default 2×/dia 07:30+17:30).
2. **Vault/pasta-destino** — default `90-referencias/dados-fonte/` com **subpasta `raw/`** (R6: bruto é input externo; raw/ separa o que o feed escreve do que o motor deriva).
3. **Nomes de arquivo** fixos, sem data (sobrescreve — padrão base-completa).
4. **Flow/warehouse?** Se o projeto tem MCP de warehouse (flow/Nekt): quais extrações (criativos/geo/demo/device/hora/keywords/saldo) — ver [references/extracao-flow-mcp.md](references/extracao-flow-mcp.md).
5. **Notify?** Se o operador quer report WhatsApp: destino (grupo/número), horário (default 08:00) — pressupõe `config-financeiro.yml` (budget/alertas; se ausente, o `motor-dados-vault` cria por entrevista).

### Passo 1 — Descobrir gids, testar acesso e baixar amostra
Pegue os **gids** de todas as abas (R10 — `/export?gid=` materializa fórmulas que o gviz trunca):
```bash
ID="<id>"
curl -sL "https://docs.google.com/spreadsheets/d/$ID/htmlview" \
  | grep -oE '"[^"]+", pageUrl:[^}]*gid: "[0-9]+"' | grep -oE '(name: )?"[^"]+"|gid: "[0-9]+"'
# (mais simples: abra a aba no navegador e leia o #gid= na URL)
```
Baixe cada aba via `/export?gid=` pro scratchpad e inspecione:
- `content_type: text/csv` + 200 → pública, ok. HTML/`<!DOCTYPE`/poucos bytes → privada → [troubleshooting.md](references/troubleshooting.md); pare e peça compartilhamento.
- Anote por aba: **1ª coluna do header** → âncora `mustContain` (R5) e **contagem esperada** de linhas (truncamento é silencioso — R10).

### Passo 2 — PII + QA de qualidade (decisão de segurança)
Rode `python "<skill>/scripts/scan-fonte.py" <amostra>` em cada aba:
- **PII detectada** → CSV vai pro `.gitignore` (R6). Sem PII → commitável.
- **Colunas contaminadas** (R7: %-corrompida, notação científica, célula-erro) → reporte por nome de cabeçalho + formato-alvo pra correção **na planilha**. Pendência, não bloqueio.

### Passo 3 — Montar estrutura + motor de download
1. Crie `<destino>/raw/` (e adicione `derivado/` ao plano se o vault vai ganhar o motor).
2. **Copie** (byte-a-byte, preserva BOM — R4) `scripts/feed-download.ps1` → `<destino>/_feed-download.ps1`. `Copy-Item`, **nunca** Write/Edit.
3. Gere `<destino>/feed-config.json` do exemplo, com `out` apontando pra `raw\<arquivo>.csv`, um target por aba (`sheet`, `gid`, `out`, `mustContain`, `pii`; `minBytes` menor pra aba padrão ainda vazia).

### Passo 4 — Estágios da cadeia (orquestração)
O motor de download é o estágio 1. Encadeie os demais **que existirem** no vault, cada um em `try/catch` que degrada com WARN (o modelo completo é o `_atualizar-dados.ps1` do exemplo Sigo — ver [references/cadeia-e-notify.md](references/cadeia-e-notify.md)):
- **transform** (`_transform.py`, se o `motor-dados-vault` já instalou) — R12: rodar via `cmd /c "python ... 2>&1"` e decidir pelo **exit code** (stderr mata a cadeia no PS 5.1).
- **render** (`_gerar-monitor.py`, se o `monitor-builder` já construiu) — mesmo padrão R12.
- **publish** (Cloudflare Pages via wrangler) — R13: `Push-Location` na pasta do feed antes (tarefa agendada roda com cwd=System32 e o wrangler morre com EPERM).
- **extração flow** é script/tarefa **separada** (`_extrair-flow.py`, segundas 07:00 antes do feed diário) — ver [references/extracao-flow-mcp.md](references/extracao-flow-mcp.md).
- **notify** é script/tarefa separada (`_notify.py`, diário 08:00) — ver [references/cadeia-e-notify.md](references/cadeia-e-notify.md).

### Passo 5 — Carga inicial + validação
Rode a cadeia 1× e confira `_download.log`: `[OK]` por aba + por estágio. `[WARN]` → diagnostique antes de seguir. Confirme CSVs em `raw/` com contagens plausíveis vs Passo 1.

### Passo 6 — Proteger PII no Git (gate antes de qualquer commit)
Para cada CSV `pii: true` + logs + artefatos com PII:
```
<destino>/raw/<arquivo-pii>.csv
<destino>/_download.log
<destino>/monitor.html      # se a cadeia renderiza (payload carrega CRM)
<destino>/monitor.json
```
**Verifique de fato**: `git check-ignore -v <path>` tem que dar match em cada um.

### Passo 7 — Registrar a família de tarefas
Use o helper (R3 — StartWhenAvailable + bateria + retry) pra **cada** tarefa: feed diário (2 gatilhos ou 2 tarefas), flow semanal (segundas, ANTES do feed do dia), notify diário:
```powershell
& "<skill>\scripts\register-task.ps1" -TaskName "<Projeto> - Dados Fonte" -ScriptPath "<destino>\_feed-download.ps1" -Time "07:30"
```
Depois **dispare um teste real** de cada e cheque `LastTaskResult = 0`.

### Passo 8 — Cascata sináptica + handoff
- `<destino>/mapa.md` (TOC + Resumo 60s + comandos de operação + nota de PII) e `mapa.md` da pasta-pai.
- Se o vault ainda não tem contrato/transform: **nomeie o próximo passo** — "rodar `motor-dados-vault` modo bootstrap" (a skill não cria contrato).
- Reporte: pasta, arquivos (commitável × git-ignored), estágios ativos da cadeia, tarefas + próxima execução, pendências de origem.

---

## Modo EXTENSAO — passos

1. **Aba nova**: Passos 1-2 só pra ela → novo target no `feed-config.json` (ou `$Targets` do orquestrador do vault) → rodar 1× → gitignore se PII → avisar `motor-dados-vault` se ela deve entrar no contrato.
2. **Extração flow nova**: adicionar ao `_extrair-flow.py` seguindo [references/extracao-flow-mcp.md](references/extracao-flow-mcp.md) (trava de sobrescrita; APPEND p/ fontes-snapshot — R14).
3. **Estágio novo na cadeia**: try/catch degradante + R12/R13; nunca reordenar estágios existentes sem reler o log de uma rodada.
4. **Notify novo/ajuste**: formato bloco-compacto multi-projeto (R16) — nunca reinventar o layout por projeto.

## Modo STATUS — passos

1. **Localize feeds**: `Glob **/feed-config.json` + `**/_atualizar-dados.ps1`.
2. Por feed: config + últimas linhas de `_download.log` e `_flow.log` (último OK/WARN por aba/estágio/extração).
3. **Tarefas**: `Get-ScheduledTaskInfo` de cada (feed/flow/notify) → última execução, `LastTaskResult`, próxima.
4. **Frescor**: `LastWriteTime` dos CSVs de `raw/` vs cadência declarada.
5. **Re-QA opcional**: `scan-fonte.py` nos CSVs pra PII nova ou contaminação reintroduzida.
6. Reporte tabela: feed · estágios ativos · última atualização · status · pendências.

---

## Padrão de output (relatório de setup)

```
Feed configurado: <Projeto> (dados-fonte 2.0)
  Pasta:    90-referencias/dados-fonte/ (raw/ = só o feed escreve)
  Fontes:   planilha 5 abas 2×/dia · flow 10 extrações às segundas
  Cadeia:   extract → transform → render → publish → notify (todos ativos)
  Arquivos: raw/campanhas-completo.csv (commitável) · raw/crm-completo.csv (git-ignored, PII)
  Tarefas:  "- Dados Fonte" 07:30+17:30 · "- Flow Semanal" seg 07:00 · "- Report WhatsApp" 08:00 (LastResult=0 nas 3)
  Próximo:  rodar motor-dados-vault (bootstrap do contrato/transform)
  Pendência na origem: phone, mql_at +11 colunas como Porcentagem → Texto/Data
```

## Loop de feedback (obrigatório)

Não declare "pronto" sem: (a) `[OK]` no log da carga inicial de **cada estágio ativo**; (b) `git check-ignore` confirmando cada artefato de PII fora do Git; (c) `LastTaskResult = 0` no teste real de **cada tarefa** registrada; (d) contagem de linhas de cada aba vs esperado do Passo 1.

## Anti-patterns

- ❌ **Escrever/editar `.ps1` na pasta-destino com Write/Edit** → remove o BOM, PS 5.1 quebra (R4). Copie o motor; parametrize pelo JSON. (Exceção: orquestrador já-existente do vault editado com ferramenta que preserve BOM + teste imediato.)
- ❌ **CSV com data no nome** (`dados-2026-06-26.csv`) → base-completa: nome fixo + sobrescrita (R5). Exceção única: fontes-snapshot em **APPEND** (R14 — ex. saldo de conta).
- ❌ **Redirecionar stderr de python dentro do PowerShell** (`& $py ... 2>&1` com EAP=Stop) → WARN benigno vira exceção e mata a cadeia (R12; monitor ficou 2 dias parado). `cmd /c` + exit code.
- ❌ **Propor `/schedule` cloud ou loop do Claude** → cloud não vê o vault; MCP some headless (R8). Agendador local, zero-Claude.
- ❌ **Commitar antes do `git check-ignore`** → PII no histórico é irreversível. Passo 6 é gate.
- ❌ **Corrigir dado contaminado no CSV** → sobrescrito no próximo run. Correção na planilha-fonte (R7).
- ❌ **Criar contrato/transform/derivado "de carona"** → é `motor-dados-vault`; esta skill entrega raw/ + cadeia e nomeia o próximo passo.
- ❌ **Report WhatsApp verboso por projeto** → formato é bloco compacto multi-projeto (R16); detalhe mora no monitor, não na mensagem.
- ❌ **Pular o Passo 0** e assumir paths/abas → cada projeto tem vault e fontes próprios; o exemplo Sigo é referência, não default.

## Avaliação (3 cenários)

### Cenário 1 — Bootstrap completo (setup, projeto com flow e notify)
**Input:** "Configura o feed do vault <X>: planilha <link>, tem warehouse flow, quero report de manhã."
**Esperado:**
- [ ] Passo 0 completo (abas, gids, extrações flow, destino do report) — nada assumido
- [ ] `raw/` criado; PII → gitignore verificado com `git check-ignore`
- [ ] Cadeia com estágios existentes (R12/R13 aplicados); flow e notify como tarefas separadas
- [ ] 3 tarefas registradas + teste real `LastTaskResult=0`
- [ ] Handoff nomeia `motor-dados-vault` pro contrato/transform

### Cenário 2 — Extensão (aba nova num feed vivo)
**Input:** "Adiciona a aba `bd_buy` no feed do Sigo."
**Esperado:**
- [ ] Descobre gid + âncora + PII só da aba nova; novo target no orquestrador do vault
- [ ] Roda 1× e valida contagem; NÃO mexe nos targets existentes
- [ ] Avisa que a tabela deve ser declarada no contrato (`motor-dados-vault` modo extensao)

### Cenário 3 — Fronteira (pedido de transform)
**Input:** "O feed tá rodando; agora cruza o CRM com as campanhas por ad_id."
**Esperado:**
- [ ] Reconhece join/derivado como `motor-dados-vault` e redireciona
- [ ] Não escreve `_transform.py` nem contrato

---

> **v2.0.0 (2026-07-09)** — UPGRADE GERAL (F7 dados-fonte 2.0, decisão
> `30-decisoes/2026-07-09-dados-fonte-v2.md` do Sigo): de "planilha→CSV" pra
> **engenheiro da camada de extração+orquestração** — `raw/`, cadeia
> extract→transform→render→publish→notify, extração flow via MCP JSON-RPC stdlib,
> família de tarefas (diária+semanal+notify), report WhatsApp bloco-compacto.
> R12-R16 novas. Padrão v1 (arquivo solto na pasta, sem cadeia): ainda funciona
> em vaults não migrados, mas todo setup novo nasce no 2.0 — histórico no git da skill.
> **v1.x (2026-06-26)** — feed diário planilha→CSV com PII/QA/tarefa (caso Sigo original).
