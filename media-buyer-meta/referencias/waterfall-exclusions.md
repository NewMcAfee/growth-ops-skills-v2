# Waterfall Exclusions — Lógica de Exclusão Hierárquica

## Princípio

O dígito de hierarquia do conjunto (`AUD-{N}-...`) determina automaticamente quais públicos devem ser **excluídos** daquele conjunto. A regra é: conjunto de dígito N exclui os públicos dos dígitos 0 até N-1.

Objetivo: eliminar sobreposição de leilão. Público mais quente não pode aparecer em campanha fria — pagaria duas vezes pelo mesmo usuário e contaminaria a métrica de cada temperatura.

---

## Tabela de Exclusões por Dígito

| Dígito | Nome do Conjunto | Exclui dígitos | Públicos a excluir (nomes descritivos) |
|--------|-----------------|----------------|---------------------------------------|
| **0** | Clientes Ativos | — | *(nenhum — público mais valioso)* |
| **1** | Clientes Inativos | 0 | `[EX] ClientesAtivos` |
| **2** | SQLs | 0–1 | `[EX] ClientesAtivos`, `[EX] ClientesInativos` |
| **3** | MQLs | 0–2 | `[EX] ClientesAtivos`, `[EX] ClientesInativos`, `[EX] SQLs` |
| **4** | Quente (Visitantes Site) | 0–3 | + `[EX] MQLs` |
| **5** | Morno (Video View) | 0–4 | + `[EX] VisitantesSite` |
| **6** | Morno (Engajamento) | 0–5 | + `[EX] VideoView30d` |
| **7** | Frio LAL | 0–6 | + `[EX] Engajamento30d` |
| **8** | Frio Interesses | 0–7 | + `[EX] LAL_Clientes` |
| **9** | Frio Broad | 0–8 | + `[EX] LAL_Clientes`, `[EX] Interesses` *(todos os acima)* |

---

## Nomes Padrão de Audiências Personalizadas

A skill lista estes nomes descritivos `[EX] ...` que o operador precisa ter criado no Business Manager. As exclusões entram no `targeting.excluded_custom_audiences` do `ads_create_ad_set` como array de `{id}` — o MCP **não cria** custom audience, só **referencia por ID existente**:

| Dígito | Nome da audiência no Meta (descritivo) |
|--------|----------------------------------------|
| 0 | `[EX] ClientesAtivos` |
| 1 | `[EX] ClientesInativos` |
| 2 | `[EX] SQLs` |
| 3 | `[EX] MQLs` |
| 4 | `[EX] VisitantesSite30d` |
| 5 | `[EX] VideoView50pct30d` |
| 6 | `[EX] Engajamento30d` |
| 7 | `[EX] LAL_Clientes` |
| 8 | `[EX] Interesses_{ICP}` |

**Nota:** No payload do `ads_create_ad_set`, as exclusões vão em `targeting.excluded_custom_audiences` como array de objetos `{id}`. Exemplo para dígito 9 (resolver cada nome `[EX]` pro ID da audiência correspondente no BM):
```
targeting.excluded_custom_audiences = [
  {id: <id_ClientesAtivos>}, {id: <id_ClientesInativos>}, {id: <id_SQLs>},
  {id: <id_MQLs>}, {id: <id_VisitantesSite30d>}, {id: <id_VideoView50pct30d>},
  {id: <id_Engajamento30d>}, {id: <id_LAL_Clientes>}, {id: <id_Interesses_{ICP}>}
]
```

---

## Função de Geração Automática

Para calcular as exclusões de um conjunto com dígito N, use esta lógica:

```
AUDIÊNCIAS_A_EXCLUIR(N) = [audiência(d) para d em range(0, N)]

Onde audiência(d):
  0 → [EX] ClientesAtivos
  1 → [EX] ClientesInativos
  2 → [EX] SQLs
  3 → [EX] MQLs
  4 → [EX] VisitantesSite30d
  5 → [EX] VideoView50pct30d
  6 → [EX] Engajamento30d
  7 → [EX] LAL_Clientes
  8 → [EX] Interesses_{ICP}
```

**Exemplo — dígito 7 (LAL):**
`range(0, 7)` → exclui dígitos 0,1,2,3,4,5,6 → 7 exclusões

**Exemplo — dígito 9 (Broad):**
`range(0, 9)` → exclui dígitos 0,1,2,3,4,5,6,7,8 → 9 exclusões

---

## Aviso ao Operador

> As exclusões são referenciadas pela skill por nomes descritivos com prefixo `[EX]`, mas o MCP só aceita IDs. Antes de a skill criar os conjuntos:
> 1. Crie cada audiência personalizada no Meta Business Manager
> 2. Tenha os IDs reais de cada audiência `[EX]` prontos pra referenciar no `targeting.excluded_custom_audiences`
> 3. O MCP não cria custom audience — só referencia por ID existente
