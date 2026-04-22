# Scrapping TABNET - Análise de Internações por AVC no Rio de Janeiro

### O GIF animado mostrando a evolução histórica das internações por AVC no Rio de Janeiro: 
![Texto Alternativo](data/visualizations/evolucao_avc_rj_HISTORICO.gif)

## Visão Geral do Projeto
Este projeto realiza web scraping no sistema TABNET do DATASUS (Sistema Único de Saúde do Brasil) para coletar dados de internações hospitalares relacionadas a acidentes vasculares cerebrais (AVC) no estado do Rio de Janeiro. Os dados são processados, limpos e utilizados para gerar mapas de calor acumulados ao longo do tempo, culminando na criação de um GIF animado que ilustra a evolução histórica da doença.

## Objetivo de Estudo
O estudo visa analisar a distribuição geográfica e temporal das internações por AVC no Rio de Janeiro, identificando padrões de incidência por município e tendências ao longo dos anos (de 2008 a 2026). O objetivo é fornecer insights sobre a saúde pública, auxiliando na alocação de recursos e políticas de prevenção. O estudo foi concluído com sucesso, gerando visualizações que mostram o acúmulo progressivo de casos, com escala de cores fixa para comparação justa entre períodos.

## Estrutura do Repositório
```
scrapping_tabnet/
├── README.md                 # Documentação principal do projeto
├── requirements.txt          # Dependências Python (a serem criadas)
├── .gitignore               # Arquivos ignorados pelo Git
├── .venv/                   # Ambiente virtual Python
├── data/                    # Pasta para todos os dados e outputs
│   ├── raw/                 # Dados brutos extraídos (CSV não processado)
│   ├── processed/           # Dados processados e limpos (CSV silver)
│   └── visualizations/      # Outputs visuais (GIFs)
│       └── mapas_acumulados_totais/  # Mapas PNG gerados
│       └── mapas_avc/                # Cópia dos mapas para GIF alternativo
├── src/                     # Código fonte (scripts Python)
│   ├── scraping_datasus.py          # Extração de dados brutos
│   ├── limpeza_dados.py             # Limpeza e processamento
│   ├── mapas_acumulados_totais.py   # Geração de mapas acumulados
│   ├── gerar_mapas_acumulados.py    # Geração alternativa de mapas
│   ├── gerar_gif_mapas_acumuladostotais_avc_rj.py  # Criação do GIF histórico
│   ├── gerar_gif_mapas_avc.py       # Criação do GIF alternativo
│   ├── explorando.py                # Script exploratório
│   └── log.py                       # Configuração de logging
├── notebooks/               # Notebooks Jupyter para exploração
│   └── explorando.ipynb     # Notebook interativo para scraping
└── logs/                    # Arquivos de log
    └── execucao.log         # Log de execuções
```

## Escolhas de Extração e Possíveis Dificuldades
### Escolhas Técnicas
- **Fonte de Dados**: TABNET foi escolhido por ser a plataforma oficial do DATASUS para dados de saúde pública, garantindo confiabilidade e abrangência.
- **Período**: De janeiro de 2008 a fevereiro de 2026, cobrindo uma série histórica extensa para análise temporal.
- **Códigos CID-10**: Utilizados códigos I60-I69 (doenças cerebrovasculares) para capturar todas as subcategorias de AVC.
- **Granularidade**: Dados agregados por município e mês, permitindo análise geográfica detalhada.
- **Processamento**: Dados brutos salvos em `data/raw/`, processados em `data/processed/` com limpeza de colunas e extração de códigos IBGE.
- **Visualização**: Mapas de calor com GeoPandas e Matplotlib, escala fixa baseada no máximo histórico para evitar distorções visuais.
- **GIF**: Criado com ImageIO para animação fluida, loop infinito para visualização contínua.

### Possíveis Dificuldades
- **Bloqueios de IP**: O TABNET pode bloquear requisições excessivas; foi implementado um timeout de 120 segundos e headers simulando navegador.
- **Estrutura HTML**: A tabela pode variar; o código usa BeautifulSoup para parsing robusto e identifica o cabeçalho dinamicamente.
- **Dados Faltantes**: Alguns municípios podem ter dados ausentes; o processamento filtra linhas vazias.
- **Performance**: Processamento de 218 meses gera muitos arquivos; otimizado com logging e verificações de progresso.
- **Dependências**: Requer bibliotecas como GeoPandas (que depende de GDAL); instalado em ambiente virtual.
- **Caminhos de Arquivos**: Inicialmente relativos, ajustados para absolutos para execução independente do diretório.

## Passo a Passo para Executar o Projeto até o GIF
1. **Configurar Ambiente**:
   - Instalar Python 3.8+.
   - Criar ambiente virtual (opcional, mas recomendado para isolar dependências): `python -m venv .venv`
   - Ativar o ambiente virtual: `source .venv/bin/activate` (Linux/Mac) ou `.venv\Scripts\activate` (Windows)
   - Instalar dependências: `pip install -r requirements.txt`

2. **Executar Scraping de Dados Brutos**:
   - Rodar: `python src/scraping_datasus.py`
   - Resultado: CSV bruto salvo em `data/raw/internacoes_avc_rj.csv`

3. **Processar e Limpar Dados**:
   - Rodar: `python src/limpeza_dados.py`
   - Resultado: CSV processado salvo em `data/processed/internacoes_avc_rj_silver.csv`

4. **Gerar Mapas de Calor**:
   - Rodar: `python src/mapas_acumulados_totais.py`
   - Resultado: 218 imagens PNG em `data/mapas_acumulados_totais/`

5. **Criar GIF Animado**:
   - Rodar: `python src/gerar_gif_mapas_acumuladostotais_avc_rj.py`
   - Resultado: GIF histórico em `data/visualizations/evolucao_avc_rj_HISTORICO.gif`

6. **Verificar Logs**:
   - Logs em `logs/execucao.log` para acompanhar progresso e erros.

Para exploração interativa, abra `notebooks/explorando.ipynb` no Jupyter.

## Notas Finais
Este projeto demonstra uma pipeline completa de coleta, processamento e visualização de dados de saúde pública. As visualizações geradas podem ser usadas para relatórios ou apresentações sobre saúde no Rio de Janeiro. Para expansões, considere adicionar mais estados ou doenças.
