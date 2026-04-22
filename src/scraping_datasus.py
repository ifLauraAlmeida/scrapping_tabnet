"""
Módulo para extração de dados de internações por AVC no Rio de Janeiro.

Este script realiza web scraping no sistema TABNET do DATASUS para coletar dados
de internações hospitalares relacionadas a acidentes vasculares cerebrais (AVC)
no estado do Rio de Janeiro, abrangendo o período de janeiro de 2008 a fevereiro de 2026.

Os dados são processados e salvos em um arquivo CSV para análise posterior.

Dependências:
- requests: Para fazer requisições HTTP
- pandas: Para manipulação de dados
- beautifulsoup4: Para parsing de HTML
- lxml: Parser XML/HTML para BeautifulSoup
- io: Para manipulação de streams (não usado diretamente aqui, mas importado)

Uso:
    Execute o script diretamente: python cu.py
    O resultado será salvo em 'internacoes_avc_rj.csv'
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import io
import os

# Importando o logger que criamos
from log import logger

# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))
# Gerar todos os arquivos de Jan/2008 até Fev/2026
# Os arquivos seguem o padrão nrrjYYMM.dbf, onde YY são os dois últimos dígitos do ano e MM o mês
arquivos = []
for ano in range(2008, 2027):
    for mes in range(1, 13):
        if ano == 2026 and mes > 2:
            break
        arquivos.append(f"nrrj{str(ano)[2:]}{mes:02d}.dbf")

# Headers para simular uma requisição de navegador e evitar bloqueios
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/nrrj.def",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Montar o corpo da requisição com parâmetros para filtrar dados de internações por AVC
# Inclui todos os arquivos gerados e códigos CID-10 relacionados a AVC (150, 178, 179, 180)
arquivos_str = "".join(f"&Arquivos={a}" for a in arquivos)
cids_str = "&SLista_Morb__CID-10=150&SLista_Morb__CID-10=178&SLista_Morb__CID-10=179&SLista_Morb__CID-10=180"

raw_body = (
    "Linha=Munic%EDpio&Coluna=Ano%2Fm%EAs_processamento&Incremento=Interna%E7%F5es"
    + arquivos_str
    + "&pesqmes1=Digite+o+texto+e+ache+f%E1cil&SMunic%EDpio=TODAS_AS_CATEGORIAS__"
    "&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o_de_Sa%FAde_%28CIR%29=TODAS_AS_CATEGORIAS__"
    "&SMacrorregi%E3o_de_Sa%FAde=TODAS_AS_CATEGORIAS__&SDivis%E3o_administ_estadual=TODAS_AS_CATEGORIAS__"
    "&pesqmes5=Digite+o+texto+e+ache+f%E1cil&SMicrorregi%E3o_IBGE=TODAS_AS_CATEGORIAS__"
    "&SRegi%E3o_Metropolitana_-_RIDE=TODAS_AS_CATEGORIAS__&pesqmes7=Digite+o+texto+e+ache+f%E1cil"
    "&SEstabelecimento=TODAS_AS_CATEGORIAS__&SCar%E1ter_atendimento=TODAS_AS_CATEGORIAS__"
    "&SRegime=TODAS_AS_CATEGORIAS__&pesqmes10=&pesqmes11="
    + cids_str
    + "&pesqmes12=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_1=TODAS_AS_CATEGORIAS__"
    "&pesqmes13=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_2=TODAS_AS_CATEGORIAS__"
    "&SSexo=TODAS_AS_CATEGORIAS__&SCor%2Fra%E7a=TODAS_AS_CATEGORIAS__&formato=table&mostre=Mostra"
)

logger.info(f"Iniciando requisição de {len(arquivos)} meses para o DATASUS...")

try:
    # Fazer requisição POST para obter os dados tabulares
    response = requests.post(
        "https://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/nrrj.def",
        data=raw_body,
        headers=headers,
        timeout=120,  # Aumentado para lidar com volume grande de dados
    )
    response.raise_for_status()  # Levantar erro se status não for 2xx
    response.encoding = "latin-1"  # Definir encoding para português
    logger.info(f"Resposta recebida com sucesso. Status: {response.status_code}")

    # Parsear tabela
    soup = BeautifulSoup(response.text, "lxml")
    tabela = soup.find("table")

    if not tabela:
        logger.error("A tabela não foi encontrada no HTML de resposta.")
    else:
        # Extrair dados da tabela HTML
        linhas = tabela.find_all("tr")
        dados = []
        for linha in linhas:
            celulas = linha.find_all(["td", "th"])
            dados.append([c.get_text(strip=True) for c in celulas])

        # Encontrar o índice do cabeçalho real (linha que começa com "Município")
        idx_header = next(
            i for i, l in enumerate(dados) if l and l[0].strip().lower() == "município"
        )

        colunas = dados[idx_header]
        df = pd.DataFrame(dados[idx_header + 1 :], columns=colunas)
        # Remover linhas vazias e resetar índice
        df = df[df.iloc[:, 0] != ""].reset_index(drop=True)
        df.rename(columns={df.columns[0]: "municipio"}, inplace=True)

        logger.info(f"Dados processados. Shape: {df.shape}")

        # Salvar dados em CSV
        output_file = os.path.join(
            project_root, "data", "raw", "internacoes_avc_rj.csv"
        )
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        logger.info(f"Arquivo salvo com sucesso: {output_file}")

except Exception as e:
    logger.exception(f"Ocorreu um erro crítico durante a execução: {str(e)}")
