# Cadeia orquestrada + notify WhatsApp

> Doutrina do orquestrador (`_atualizar-dados.ps1`) e do estágio notify
> (`_notify.py`). Modelo vivo: vault Sigo ERP, `90-referencias/dados-fonte/`.

## A cadeia (extract → transform → render → publish → notify)

Um único `.ps1` agendado orquestra os estágios diários, em ordem, cada um num `try/catch` que **degrada com WARN** — falha num estágio nunca derruba o que está de pé (transform quebrado → render usa o último derivado bom; render quebrado → CSVs já atualizados; publish sem rede → monitor local segue).

```
[1 extract]  targets planilha -> raw\  (trava: .tmp -> valida tamanho/header/linhas -> Move-Item)
[2 transform] cmd /c "python _transform.py 2>&1"   -> derivado\    (dono: motor-dados-vault)
[3 render]    cmd /c "python _gerar-monitor.py 2>&1" -> monitor.*  (dono: monitor-builder)
[4 publish]   wrangler pages deploy (Push-Location na pasta antes)
[5 notify]    tarefa separada 08:00 (dado fresco do feed 07:30)
```

Regras do orquestrador (todas de incidente real):
- **R12 — stderr mata a cadeia no PS 5.1**: `& $py script 2>&1` com `ErrorActionPreference=Stop` converte QUALQUER linha de stderr em exceção — um WARN benigno parou o monitor por 2 dias. Rodar python via `cmd /c "python ... 2>&1"` e decidir **só pelo exit code**; scripts python imprimem WARN em **stdout**.
- **R13 — cwd da tarefa agendada é System32**: wrangler cria `.wrangler\tmp` no cwd → EPERM. `Push-Location <pasta-do-feed>` antes do deploy, `Pop-Location` depois.
- Estágio ausente (script não existe no vault) → WARN e segue — a cadeia é incremental.
- Credenciais (Cloudflare, Evolution) lidas do `settings.json` global em runtime — nunca coladas no script.
- Scripts `_*` ficam na **raiz** da pasta dados-fonte (mover o `.ps1` re-apontaria a tarefa agendada — risco sem ganho).
- Log único `_download.log` (git-ignored) com `[OK]`/`[WARN]` por estágio.

## Notify — report diário WhatsApp (formato bloco-compacto multi-projeto, R16)

Script python stdlib (`_notify.py`), tarefa própria (~08:00, após o feed da manhã). Envia via **Evolution API** (`POST /message/sendText/<instancia>`, payload v2 `{number, text}`, fallback v1 `{number, textMessage:{text}}`); URL/key do `settings.json` global (**ler com `utf-8-sig`** — Set-Content UTF8 do PS grava BOM).

**Formato aprovado pelo operador** (v2, 2026-07-09 — o v1 verboso foi rejeitado: "mal formatado e confuso, inviável pra multi-projeto"). Bloco compacto por projeto, desenhado pra EMPILHAR num futuro report cross-projeto:

```
📊 Report diário · qua 09/07          ← cabeçalho 1× (dia/mês pt-BR HARDCODED — %B sai em inglês)

*SIGO ERP* 🔴                          ← projeto + PIOR semáforo do bloco
Invest jul: R$ 4,1k/25k · no ritmo (−5%)
  Meta R$ 2,9k/16k 🟢 · Google R$ 1,2k/9k 🔴 (25% abaixo)
Demos: 14 MTD · ritmo 48/54 🟡
Saldo: Google R$ 8,9k (~30d) · Meta pós R$ 1,9k
QA: 2 avisos (detalhe no monitor)
```

Regras do formato:
- 4-6 linhas por projeto; valores `R$ 4,1k`; status **verbal** ("no ritmo (−5%)", "25% abaixo") — não tabela de números.
- Detalhe mora no **monitor** (link/QA só contagem); a mensagem é semáforo, não relatório.
- Conteúdo: pacing de invest por canal vs budget do `config-financeiro.yml` (até ontem) · total vs budget do mês · indicador-alvo MTD + ritmo vs meta · saldo/runway (pré-paga alerta <7d; pós-paga informativo) · contagem de achados QA.
- Thresholds (±% pacing, runway mínimo) vêm do `config-financeiro.yml → alertas`, nunca hardcode.
- **Dedup 1 envio/dia** via state file git-ignored (`_notify-state.json`); `--force` reenvia.
- Fontes do payload: `derivado/fato-*.csv` + `monitor.json` + `config-financeiro.yml` + `raw/flow-saldo-contas.csv` + `derivado/qa-report.json` — o notify **não recalcula** nada que a cadeia já derivou.

## Família de tarefas agendadas (padrão de nomes)

| Tarefa | Cadência | Script |
|---|---|---|
| `<Projeto> - Dados Fonte` | diária 07:30 + 17:30 | `_atualizar-dados.ps1` (cadeia 1-4) |
| `<Projeto> - Flow Semanal` | segundas 07:00 | `_extrair-flow.py` (antes do feed do dia) |
| `<Projeto> - Report WhatsApp` | diária 08:00 | `_notify.py` |

Todas via `register-task.ps1` (R3: StartWhenAvailable + bateria + retry). `schtasks` com espaços no nome quebra o quoting — usar sempre `Register-ScheduledTask` (o helper já usa).
