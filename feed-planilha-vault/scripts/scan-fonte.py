#!/usr/bin/env python3
"""
scan-fonte.py — Detecção de PII + QA de qualidade de um CSV de feed.

Usado pela skill feed-planilha-vault em dois momentos:
  1. SETUP: decidir se um CSV vai pro .gitignore (PII) e reportar colunas
     com problema de formatação na ORIGEM antes de confiar no feed.
  2. STATUS: re-auditar um feed já configurado.

Uso:
    python scan-fonte.py <arquivo.csv> [--json]

Saída (texto por default; --json pra consumo programático):
  - pii: colunas com dado pessoal -> recomendação .gitignore
  - qualidade: colunas contaminadas (porcentagem corrompida, notação
    científica, etc) -> reportar pro operador corrigir na planilha-fonte.

Heurística PII: nome do cabeçalho OU conteúdo (regex email/cpf/cnpj/phone).
Não faz rede. Não modifica nada. Lê só amostra pra ser rápido em CSV grande.
"""
import csv, sys, re, json, io

SAMPLE = 2000  # linhas amostradas pra classificar (suficiente e rápido)

# Cabeçalhos que denunciam PII (substring, case-insensitive)
PII_HEADERS = [
    'email', 'e-mail', 'mail', 'phone', 'telefone', 'celular', 'whatsapp',
    'cpf', 'cnpj', 'rg', 'nome', 'name', 'full_name', 'first_name', 'last_name',
    'endereco', 'address', 'street', 'cep', 'owner_name', 'owner_phone',
    'company_phone', 'person', 'contato', 'document', 'passport',
]
# Conteúdo que denuncia PII mesmo se o cabeçalho for genérico
RE_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
RE_CPF   = re.compile(r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$')
RE_CNPJ  = re.compile(r'^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$')

# Contaminação de formatação na origem (planilha)
RE_PCT_CORRUPT = re.compile(r'\d,\d+%$')        # ex: 551...700,00%  (célula como Porcentagem)
RE_SCI         = re.compile(r'^\d[.,]\d+E[+-]?\d+$', re.I)  # ex: 9,37284E+18 (ID longo como Número)
RE_ERROR_CELL  = re.compile(r'#(ERROR|REF|N/A|VALUE|DIV/0|NAME)!', re.I)


def load(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    return rows[0], rows[1:1+SAMPLE]


def col_values(data, i):
    return [r[i] for r in data if i < len(r) and r[i].strip()]


def scan(path):
    header, data = load(path)
    pii, quality = [], []
    for i, col in enumerate(header):
        col = col.strip()
        if not col:
            continue
        vals = col_values(data, i)
        if not vals:
            continue

        # PII por cabeçalho ou conteúdo
        is_pii = any(h in col.lower() for h in PII_HEADERS)
        if not is_pii:
            hits = sum(1 for v in vals[:200]
                       if RE_EMAIL.match(v) or RE_CPF.match(v) or RE_CNPJ.match(v))
            if hits >= max(3, len(vals[:200]) * 0.3):
                is_pii = True
        if is_pii:
            pii.append({'col': col, 'idx': i, 'exemplo': vals[0][:40]})

        # Qualidade: contaminação de formatação
        bad_pct = [v for v in vals if RE_PCT_CORRUPT.search(v)]
        bad_sci = [v for v in vals if RE_SCI.match(v)]
        bad_err = [v for v in vals if RE_ERROR_CELL.search(v)]
        if bad_pct:
            quality.append({'col': col, 'idx': i, 'tipo': 'porcentagem-corrompida',
                            'afetados': len(bad_pct), 'total': len(vals),
                            'exemplo': bad_pct[0][:40], 'corrigir_para': 'Texto simples ou Data'})
        if bad_sci:
            quality.append({'col': col, 'idx': i, 'tipo': 'notacao-cientifica',
                            'afetados': len(bad_sci), 'total': len(vals),
                            'exemplo': bad_sci[0][:40], 'corrigir_para': 'Texto simples'})
        if bad_err:
            quality.append({'col': col, 'idx': i, 'tipo': 'celula-erro',
                            'afetados': len(bad_err), 'total': len(vals),
                            'exemplo': bad_err[0][:40], 'corrigir_para': 'verificar formula na origem'})
    return pii, quality


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    as_json = '--json' in sys.argv
    if not args:
        print('uso: python scan-fonte.py <arquivo.csv> [--json]'); sys.exit(2)
    path = args[0]
    pii, quality = scan(path)

    if as_json:
        sys.stdout.reconfigure(encoding='utf-8')
        print(json.dumps({'pii': pii, 'quality': quality}, ensure_ascii=False, indent=2))
        return

    out = io.StringIO()
    out.write(f"\n=== PII detectada ({len(pii)} colunas) → se houver, CSV vai pro .gitignore ===\n")
    if pii:
        for p in pii:
            out.write(f"  • {p['col']:<24} ex: {p['exemplo']}\n")
    else:
        out.write("  (nenhuma — CSV provavelmente commitável)\n")

    out.write(f"\n=== Qualidade: colunas contaminadas na ORIGEM ({len(quality)}) → corrigir na planilha ===\n")
    if quality:
        for q in quality:
            out.write(f"  ❌ {q['col']:<24} [{q['tipo']}] {q['afetados']}/{q['total']} "
                      f"→ formatar como {q['corrigir_para']}  (ex: {q['exemplo']})\n")
    else:
        out.write("  ✅ nenhuma contaminação detectada\n")
    sys.stdout.reconfigure(encoding='utf-8')
    print(out.getvalue())


if __name__ == '__main__':
    main()
