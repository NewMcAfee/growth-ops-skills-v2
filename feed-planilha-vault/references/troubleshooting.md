# Troubleshooting — feed-planilha-vault

## Acesso à planilha

| Sintoma | Causa | Ação |
|---|---|---|
| Download volta HTML / `<!DOCTYPE` / poucos bytes | Planilha **não é pública** | Pedir ao operador: Compartilhar → "Qualquer pessoa com o link" (Leitor). gviz NÃO autentica. Se tiver de ser privada, escopo (B) com OAuth — fora desta skill. |
| `/export?gid` dá **HTTP 401/403** mas a planilha É pública (gviz e htmlview dão 200) | Org Google Workspace bloqueia o endpoint `/export` anônimo (visto em growthpacks V4) — R11 | **Automático**: o motor cai pra `gviz?gid` sozinho e loga `fallback automático` no `_download.log`. NÃO remover o gid do config. Só é planilha-privada-de-fato se **todos** os endpoints (gviz incluso) derem 401. |
| HTTP 200 mas conteúdo errado/vazio | Nome da aba diferente do informado | Conferir nome exato da aba (case-sensitive, com acento). A skill usa `[uri]::EscapeDataString`. |
| Aba existe mas vem outra | gviz às vezes resolve por gid | Usar o gid explícito: trocar `&sheet=Nome` por `&gid=123456` no endpoint. |

## Qualidade do dado (gviz distorce)

gviz passa pela Visualization API e pode reinterpretar tipos por locale (datas, decimais). Se o QA (`scan-fonte.py`) acusar distorção **que não existe na planilha**:

- **Fallback p/ endpoint de export cru** (R2): `https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid={GID}`. Esse devolve o CSV mais fiel ao display, mas exige `gid` (não aceita nome de aba). Pegar o gid abrindo a aba no navegador (`...#gid=NUMERO`).
- Editar `feed-download.ps1`? **Não.** Se precisar do endpoint export, isso é uma variação estrutural — documentar e ajustar o motor na skill, não no vault.

## PowerShell

| Sintoma | Causa | Ação |
|---|---|---|
| `Token 'xxx' inesperado` / parse error em acento | `.ps1` salvo sem BOM, PS 5.1 leu como ANSI (R4) | Reconverter: `$c=Get-Content p -Raw -Encoding UTF8; [IO.File]::WriteAllText(p,$c,(New-Object Text.UTF8Encoding($true)))`. Nunca editar o script com ferramenta que remova BOM. |
| Acento sai como `Ã§` no CSV | download decodificando errado | `feed-download.ps1` usa `curl.exe` (R9), que grava os bytes UTF-8 crus do gviz sem reinterpretar. |
| Aba grande dá `O tempo limite da operação foi atingido` / timeout ~100s | Era `System.Net.WebClient.DownloadFile` (timeout oculto de 100s) | Resolvido na R9: motor usa `curl.exe -sL --fail --max-time 600`. Se ainda estourar (aba gigante + rede lenta), suba o `--max-time`. A trava de segurança mantém o dado bom anterior e loga WARN — não há perda. |

## Tarefa agendada

| Sintoma | Causa | Ação |
|---|---|---|
| Não roda no laptop na bateria | Falta `-AllowStartIfOnBatteries` (R3) | `register-task.ps1` já inclui. Recriar a tarefa por ele. |
| Perdeu o horário (PC desligado) e não rodou | Falta `-StartWhenAvailable` | idem — recriar pelo helper. |
| `LastTaskResult` ≠ 0 | Erro no script | Ler `_download.log` na pasta do feed; `Get-ScheduledTaskInfo -TaskName ...`. |
| Quero ver/disparar/remover | — | `schtasks /Query /TN "<nome>" /V /FO LIST` · `Start-ScheduledTask -TaskName "<nome>"` · `Unregister-ScheduledTask -TaskName "<nome>" -Confirm:$false` |

## Sobrescrita não aconteceu (log diz WARN, abortado)

A trava de segurança (R5) recusou sobrescrever. Motivos possíveis no log:
- `muito pequeno` → fonte devolveu erro/login.
- `header sem âncora` → aba mudou de estrutura OU caiu página de erro.
- `truncamento suspeito` → novo arquivo < 50% das linhas do atual. Se a redução for **legítima** (ex: reset de ano), baixar manualmente uma vez ou ajustar `minLineRatio` no config.
