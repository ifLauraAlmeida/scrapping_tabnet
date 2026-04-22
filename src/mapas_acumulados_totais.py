"""
Módulo para geração de mapas de acumulação histórica total de internações por AVC no Rio de Janeiro.

Este script processa dados de internações hospitalares por acidente vascular cerebral (AVC)
e gera uma série de mapas de calor (heatmaps) que mostram a acumulação histórica crescente
ao longo do tempo, com escala de cores baseada no valor máximo final para manter consistência.

Diferenças do módulo evolucao.py:
- Acumulação nunca é resetada (cresce continuamente)
- Escala baseada no máximo histórico total
- Foco em visualização da tendência acumulada completa

Funcionalidades:
- Carrega dados de CSV processado
- Obtém dados populacionais do IBGE (Censo 2022)
- Baixa malha geográfica do estado do Rio de Janeiro
- Gera mapas mensais com acumulação histórica crescente
- Salva imagens PNG em pasta 'mapas_acumulados_totais'

Dependências:
- pandas: Manipulação de dados
- geopandas: Manipulação de dados geoespaciais
- requests: Requisições HTTP para APIs
- matplotlib: Geração de gráficos
- io: Manipulação de streams binários
- os: Operações do sistema de arquivos
- log: Logger customizado

Uso:
    from plotting import gerar_serie_acumulada_historica
    gerar_serie_acumulada_historica('dados.csv')
"""

import pandas as pd
import geopandas as gpd
import requests
import matplotlib.pyplot as plt
import io
import os
from log import logger


# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))


def gerar_serie_acumulada_historica(csv_path):
    """
    Gera uma série de mapas de calor mostrando a acumulação histórica total de internações por AVC.

    Esta função processa dados de internações hospitalares por município no Rio de Janeiro,
    calcula taxas acumuladas por 100.000 habitantes de forma crescente (sem reset) e gera
    mapas mensais com escala de cores baseada no máximo histórico total.

    Args:
        csv_path (str): Caminho para o arquivo CSV contendo os dados de internações.
                        O CSV deve ter uma coluna 'municipio_id' e colunas de datas no formato 'YYYY/MMM'.

    Returns:
        None: Salva os mapas como arquivos PNG na pasta 'mapas_acumulados_totais'.

    Raises:
        Exception: Em caso de erro na leitura de dados, requisições HTTP ou geração de mapas.

    Notas:
        - Utiliza dados populacionais do Censo 2022 do IBGE
        - Baixa malha geográfica do IBGE para o estado do RJ
        - Escala de cores baseada no máximo total histórico (não muda ao longo da série)
        - Acumulação cresce continuamente sem resetar
        - Ideal para visualizar tendência histórica acumulada
    """
    try:
        # 1. Pasta de Saída
        PASTA = os.path.join(project_root, "data", "mapas_acumulados_totais")
        if not os.path.exists(PASTA):
            os.makedirs(PASTA)

        df_silver = pd.read_csv(csv_path, dtype={"municipio_id": str})

        # 2. Base populacional (Censo 2022)
        logger.info("Buscando base populacional fixa...")
        url_pop = "https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93?localidades=N6[N3[33]]"
        res_pop = requests.get(url_pop).json()
        pop_dict = {
            item["localidade"]["id"][:6]: int(item["serie"]["2022"])
            for item in res_pop[0]["resultados"][0]["series"]
        }

        MESES_MAP = {
            "Jan": "01",
            "Fev": "02",
            "Mar": "03",
            "Abr": "04",
            "Mai": "05",
            "Jun": "06",
            "Jul": "07",
            "Ago": "08",
            "Set": "09",
            "Out": "10",
            "Nov": "11",
            "Dez": "12",
        }

        colunas = [c for c in df_silver.columns if "/" in c]
        colunas.sort(
            key=lambda x: (int(x.split("/")[0]), MESES_MAP.get(x.split("/")[1]))
        )

        # --- O SEGREDO: VMAX FIXO NO VALOR FINAL DE 2026 ---
        logger.info("Calculando o teto máximo de 2026 para travar a escala...")
        # Calcula a soma total de todos os meses para determinar o máximo histórico
        soma_total_final = df_silver[colunas].sum(axis=1)
        VMAX_FINAL = (
            soma_total_final / df_silver["municipio_id"].map(pop_dict) * 100000
        ).max()
        logger.info(f"Escala travada no máximo histórico: {VMAX_FINAL:.2f}")

        # 3. Download da Malha (uma vez)
        logger.info("Baixando malha do Rio de Janeiro...")
        rj_map = gpd.read_file(
            io.BytesIO(
                requests.get(
                    "https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio"
                ).content
            )
        )
        rj_map["municipio_id_6"] = rj_map["codarea"].str[:6]

        # 4. Loop de Plotagem (Sem Reset)
        # O balde começa vazio e só enche até o fim do loop
        soma_acumulada = pd.Series(0.0, index=df_silver.index)

        logger.info(f"Iniciando geração de {len(colunas)} imagens...")
        for i, data_ref in enumerate(colunas):
            ano, mes_nome = data_ref.split("/")
            mes_num = MESES_MAP.get(mes_nome)

            # Acumulando sem nunca zerar
            soma_acumulada += df_silver[data_ref].astype(float)
            df_silver["taxa_acumulada"] = (
                soma_acumulada / df_silver["municipio_id"].map(pop_dict)
            ) * 100000

            merged = rj_map.merge(
                df_silver[["municipio_id", "taxa_acumulada"]],
                left_on="municipio_id_6",
                right_on="municipio_id",
            )

            fig, ax = plt.subplots(1, 1, figsize=(15, 10), dpi=100)

            # VMAX_FINAL garante que o mapa nunca "esvazie"
            merged.plot(
                column="taxa_acumulada",
                ax=ax,
                cmap="YlOrRd",
                vmin=0,
                vmax=VMAX_FINAL,
                legend=True,
                edgecolor="black",
                linewidth=0.2,
                legend_kwds={
                    "label": "Taxa Acumulada Total (desde 2008)",
                    "orientation": "horizontal",
                    "pad": 0.02,
                },
            )

            plt.title(
                f"Acúmulo Histórico de AVC no RJ: {data_ref}",
                fontsize=20,
                fontweight="bold",
            )
            ax.set_axis_off()

            nome_arq = f"{PASTA}/heatmap_{ano}_{mes_num}_{mes_nome}.png"
            plt.tight_layout()
            plt.savefig(nome_arq, dpi=100, facecolor="white")
            plt.close(fig)

            if (i + 1) % 24 == 0:
                logger.info(f"Processado até {data_ref}...")

        logger.info("Processo concluído com sucesso!")

    except Exception as e:
        logger.error(f"Erro: {e}")


if __name__ == "__main__":
    csv_path = os.path.join(
        project_root, "data", "processed", "internacoes_avc_rj_silver.csv"
    )
    gerar_serie_acumulada_historica(csv_path)
