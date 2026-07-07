# Operação do PMax — o que dá e o que NÃO dá pra controlar (campo)

> Gotchas operacionais de Performance Max, validados em produção (Sigo ERP, construção civil B2B, jun/2026). Diferente de `pitfalls.md` (erros de CSV/import), aqui é sobre **otimizar um PMax já no ar**.

## Asset group ≠ ad set da Meta — não separa por formato

- Cada asset group **combina imagens + vídeos + textos juntos**. O algoritmo monta os anúncios e serve cada formato na superfície certa: **vídeo no YouTube/Shorts, imagem no Display/Gmail/Discover, texto no Search**.
- Como rodam em superfícies diferentes, **vídeo e imagem NÃO competem entre si** — o medo de "estático sufoca vídeo" (real na Meta/CBO) **não se aplica ao PMax**. Não crie asset group só-vídeo vs só-imagem.
- Para "reforçar vídeo": adicione mais vídeos bons no asset group. Recomendado **1 asset group concentrado** (não fragmentar o sinal).

## Criativo com 0 conversão é NORMAL — não cortar por isso

- Imagens e vídeos quase sempre aparecem com **0 conversão**: o crédito last-click vai pro texto/Search. **Não dá pra usar conversão pra podar criativo.**
- Use a coluna **"Classificação de desempenho"** (Baixo / Bom / Melhor). Corte só os **"Baixo"** com **≥3–4 semanas** de casa, e **substitua** (não só remova). Asset recém-adicionado com baixa impressão geralmente é falta de tempo, não baixa qualidade.
- O PMax gosta de **volume de assets** (10–20 imagens) — cortar demais reduz as combinações do algoritmo.

## Segmentação: o controle é mínimo (e onde ele está)

- **Demografia (idade/sexo):** só **leitura** — NÃO dá pra excluir no PMax (diferente do Search). A tabela serve só pra validar o público.
- **Geo (locais):** **ÚNICO controle real** — dá pra **excluir** estados/regiões. É onde mora a otimização de segmentação do PMax. Critério: cortar local com gasto relevante e 0 conv num período significativo (1 conv em pouco volume é ruído).
- **Audience signals:** são **sugestões, não filtros** (incluindo o signal baseado em conversão, ex. "Submit lead form").

## Brand Exclusion (sempre, no PMax de aquisição)

Ligue **Brand Exclusion** — senão o PMax canibaliza tráfego de marca e **infla volume falso** (o CP-conv parece melhor do que é). Confirme também qual ação de conversão está marcada como **principal**: é ela que o algoritmo persegue.
