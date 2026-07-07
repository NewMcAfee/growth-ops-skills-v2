---
name: feed-planilha-vault
description: Configura um feed diário que baixa abas de uma planilha Google Sheets pública como CSV e sobrescreve arquivos de nome fixo num vault local (Windows), com detecção de PII→gitignore, QA de qualidade da origem, tarefa agendada robusta e cascata sináptica. Ative quando o operador quiser automatizar a entrada de dados de uma planilha no vault de um projeto, ou auditar/replicar um feed existente. NÃO ative para planilhas privadas que exigem OAuth, fontes que não sejam Google Sheets (Excel/OneDrive/API), análise dos dados (use newton/darwin), ou agendamento em cloud.
allowed-tools: Read,Write,Edit,Bash,PowerShell,AskUserQuestion
---

# feed-planilha-vault

## Contexto

Operadores Growth IA Ops alimentam vaults locais com dados vivos de planilhas (campanhas, CRM, financeiro). O download em si é trivial; o que erra é a **governança**: PII de cliente vazando pro Git, dado corrompido na origem passando despercebido, cópias acumuladas do mesmo year-to-date, e tarefa agendada que não roda no laptop. Esta skill faz o feed **nascer auditável e seguro**: um arquivo de nome fixo por aba, sobrescrito diariamente, com PII protegida, qualidade verificada e docs do vault em cascata. Mecanismo é **sempre local** (PowerShell + Agendador do Windows) — cloud não enxerga o filesystem do vault.

Antes de agir, **leia [references/regras-aplicadas.md](references/regras-aplicadas.md)** (R1–R8 — as invariantes). O caso completo de referência está em [references/exemplo-sigo-erp.md](references/exemplo-sigo-erp.md).

## Modos

- **setup** (default) — bootstrap de um feed novo num projeto.
- **status** — listar/auditar feeds já configurados (lê `_download.log`, checa a tarefa, re-roda QA).

Detecte o modo pela intenção. Em dúvida, pergunte.

---

## Modo SETUP — passos

### Passo 0 — Coletar parâmetros (não pule)
Levante, perguntando o que faltar (use AskUserQuestion para escolhas):
1. **Link da planilha** → extraia o ID (`/spreadsheets/d/{ID}/`).
2. **Abas** a puxar (nomes exatos, case-sensitive).
3. **Projeto/vault** alvo e **pasta-destino** — default `90-referencias/dados-fonte/` (R6: é input externo bruto, não output canônico). Confirme o root do vault.
4. **Nomes de arquivo** de saída — fixos, sem data (porque sobrescreve). Sugira a partir do conteúdo (ex: `campanhas-ano-corrente.csv`).
5. **Horário** do download diário.

### Passo 1 — Descobrir gids, testar acesso e baixar amostra
Pegue os **gids** de todas as abas de uma vez (R10 — `/export?gid=` materializa fórmulas que o gviz trunca):
```bash
ID="<id>"
curl -sL "https://docs.google.com/spreadsheets/d/$ID/htmlview" \
  | grep -oE '"[^"]+", pageUrl:[^}]*gid: "[0-9]+"' | grep -oE '(name: )?"[^"]+"|gid: "[0-9]+"'
# (mais simples: abra a aba no navegador e leia o #gid= na URL)
```
Baixe cada aba via `/export?gid=` pro scratchpad e inspecione:
```bash
GID="<gid>"
curl -sL "https://docs.google.com/spreadsheets/d/$ID/export?format=csv&gid=$GID" \
  -o "/tmp/amostra.csv" -w "HTTP %{http_code} | %{size_download}b | %{content_type}\n"
```
- `content_type: text/csv` + 200 → **pública, ok**.
- HTML / `<!DOCTYPE` / poucos bytes → **privada** → ver [troubleshooting.md](references/troubleshooting.md); pare e peça compartilhamento público.
- Anote, de cada aba, **1ª coluna do header** → âncora `mustContain` (R5), e a **contagem de registros esperada** → o truncamento por fórmula é silencioso (R10), valide o nº de linhas.

### Passo 2 — PII + QA de qualidade (decisão de segurança)
Rode o scanner em cada amostra:
```bash
python "<skill>/scripts/scan-fonte.py" /tmp/amostra.csv
```
- **PII detectada** → esse CSV vai pro `.gitignore` (R6). Sem PII → commitável.
- **Colunas contaminadas** (R7: porcentagem-corrompida, notação-científica, célula-erro) → **reporte ao operador por nome de cabeçalho + formato-alvo** pra ele corrigir **na planilha** (não no CSV). Não bloqueie o setup por isso — registre como pendência.

### Passo 3 — Montar a pasta e a config
1. Crie a pasta-destino no vault.
2. **Copie** (byte-a-byte, preserva BOM — R4) `scripts/feed-download.ps1` → `<destino>/_feed-download.ps1`. Use `Copy-Item`, **nunca** Write/Edit (removeria o BOM).
3. Gere `<destino>/feed-config.json` a partir de `scripts/feed-config.exemplo.json`, preenchendo `sheetId` e um `targets[]` por aba (`sheet`, `gid`, `out`, `mustContain`, `pii`). Preferir `gid` (R10); sem ele, o motor cai no fallback gviz por nome. JSON pode ser UTF-8 sem BOM.

### Passo 4 — Carga inicial + validação
Rode o motor uma vez e confira o log:
```powershell
& "<destino>\_feed-download.ps1"
```
Espere `[OK]` por aba em `_download.log`. Se `[WARN]`, diagnostique antes de seguir (troubleshooting.md). Confirme que os CSV existem com tamanho plausível.

### Passo 5 — Proteger PII no Git (antes de qualquer commit)
Para cada CSV marcado `pii: true`, adicione ao `.gitignore` do vault (junto com `_download.log`):
```
<pasta-destino>/<arquivo-crm>.csv
<pasta-destino>/_download.log
```
**Verifique de fato:** `git check-ignore -v <caminho-do-csv-pii>` tem que retornar match. PII fora do Git é requisito, não nice-to-have.

### Passo 6 — Registrar a tarefa agendada
Use o helper (R3 — já inclui StartWhenAvailable + bateria + retry):
```powershell
& "<skill>\scripts\register-task.ps1" -TaskName "<Projeto> - Dados Fonte" `
    -ScriptPath "<destino>\_feed-download.ps1" -Time "<HH:mm>"
```
Depois **dispare um teste real** e cheque `LastTaskResult` = 0:
```powershell
Start-ScheduledTask -TaskName "<Projeto> - Dados Fonte"; Start-Sleep 8
(Get-ScheduledTaskInfo -TaskName "<Projeto> - Dados Fonte").LastTaskResult
```

### Passo 7 — Cascata sináptica (R7 do vault / doutrina Growth IA Ops)
- Crie `<destino>/mapa.md` — TOC + Resumo 60s + comandos de operação da tarefa + nota de PII. Modele pelo do exemplo Sigo ERP.
- Atualize o `mapa.md`/`_readme.md` da pasta-pai registrando a nova subpasta.
- Se a skill `vault-architect` estiver disponível: `vault-architect atualiza-cascata <destino>/mapa.md`.

### Passo 8 — Reportar
Resuma: pasta, arquivos (quais commitáveis × git-ignored), próxima execução da tarefa, e a **lista de colunas pra corrigir na origem** (Passo 2), se houver.

---

## Modo STATUS — passos

1. **Localize feeds** no vault: procure `feed-config.json` / `_feed-download.ps1` (`Glob **/feed-config.json`).
2. Para cada um: leia `feed-config.json` + as últimas linhas de `_download.log` (último OK/WARN por aba).
3. **Tarefa:** `Get-ScheduledTaskInfo -TaskName "<nome>"` → última execução, `LastTaskResult`, próxima.
4. **Frescor:** `LastWriteTime` dos CSV — bate com a periodicidade?
5. **Re-QA opcional:** rode `scan-fonte.py` nos CSV atuais pra flagrar PII nova (coluna adicionada) ou contaminação reintroduzida.
6. Reporte uma tabela: feed · última atualização · status · pendências.

---

## Padrão de output (exemplo de relatório de setup)

```
Feed configurado: <Projeto>
  Pasta:    90-referencias/dados-fonte/
  Arquivos: campanhas-ano-corrente.csv (commitável) · crm-ano-corrente.csv (git-ignored, PII)
  Tarefa:   "<Projeto> - Dados Fonte" · diária 09:00 · próx: amanhã 09:00 · teste LastResult=0
  Pendência na origem: phone, mql_at, +11 colunas formatadas como Porcentagem → Texto/Data
```

## Loop de feedback (obrigatório)
Não declare "pronto" sem: (a) `[OK]` no `_download.log` da carga inicial; (b) `git check-ignore` confirmando cada CSV de PII fora do Git; (c) `LastTaskResult = 0` no teste real da tarefa. Os três são verificações observáveis, não suposições.

## Anti-patterns
- ❌ **Escrever/editar o `.ps1` na pasta-destino com Write/Edit** → remove o BOM, PS 5.1 quebra (R4). Copie o motor; parametrize só o JSON.
- ❌ **Acumular CSV com data no nome** (`dados-2026-06-26.csv`) → o feed é year-to-date cumulativo; nome fixo + sobrescrita (R5). Cópias datadas só repetem dado.
- ❌ **Propor `/schedule` cloud ou loop do Claude** pro download → cloud não vê o vault local; MCP Drive some headless (R8). Sempre Agendador local.
- ❌ **Commitar antes de verificar `git check-ignore`** → PII de cliente vaza pro histórico (irreversível). Passo 5 é gate.
- ❌ **Corrigir dado contaminado no CSV** → é sobrescrito no próximo run. A correção é na planilha-fonte (R7); a skill só reporta.
- ❌ **Pular o Passo 0** e assumir paths/abas → cada projeto tem vault e abas próprios; a skill é genérica, o exemplo Sigo ERP é só referência.
