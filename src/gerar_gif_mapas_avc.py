import imageio.v3 as iio
import os
from log import logger


# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))


def criar_gif_da_serie(
    pasta_origem=os.path.join(project_root, "data", "mapas_acumulados_totais"),
    nome_saida=os.path.join(
        project_root, "data", "visualizations", "evolucao_avc_rj.gif"
    ),
    fps=5,
):
    """
    Cria um GIF animado a partir de uma série de imagens PNG, mostrando a evolução temporal
    de mapas de internações por AVC no Rio de Janeiro.

    Esta função lê todas as imagens PNG da pasta especificada, ordena-as cronologicamente
    (baseado no nome dos arquivos, que seguem o padrão ano_mês), e combina em um GIF animado
    com loop infinito.

    Parâmetros:
    - pasta_origem (str): Caminho da pasta contendo as imagens PNG dos mapas.
      Padrão: 'mapas_avc'.
    - nome_saida (str): Nome do arquivo GIF de saída. Padrão: 'evolucao_avc_rj.gif'.
    - fps (int): Quadros por segundo da animação. Padrão: 5 (mais lento para visualização).
      Aumente para acelerar (ex.: 8-12 fps).

    Retorno:
    - None: A função não retorna valor, mas salva o GIF no diretório atual e registra logs.

    Exceções:
    - Pode lançar exceções se não houver arquivos na pasta ou se houver problemas de leitura/escrita.

    Exemplo de uso:
    >>> criar_gif_da_serie(fps=8)  # Cria GIF mais rápido
    """
    try:
        logger.info("Iniciando a criação do GIF...")

        # 1. Lista todos os arquivos da pasta e ordena (a ordem 2008_01, 2008_02 garante a cronologia)
        arquivos = sorted([f for f in os.listdir(pasta_origem) if f.endswith(".png")])

        if not arquivos:
            logger.error("Nenhum arquivo PNG encontrado na pasta.")
            return

        logger.info(f"Processando {len(arquivos)} quadros...")

        # 2. Lê as imagens e armazena em uma lista
        imagens = []
        for nome_arquivo in arquivos:
            caminho_completo = os.path.join(pasta_origem, nome_arquivo)
            imagens.append(iio.imread(caminho_completo))

        # 3. Salva como GIF
        # fps: quadros por segundo. Aumente para ficar mais rápido.
        # loop=0: o GIF vai ficar repetindo infinitamente.
        iio.imwrite(nome_saida, imagens, fps=fps, loop=0)

        logger.info(f"Sucesso! GIF salvo como: {nome_saida}")

    except Exception as e:
        logger.error(f"Erro ao gerar GIF: {e}")


if __name__ == "__main__":
    # Certifique-se de que a pasta 'mapas_avc' existe e tem as fotos
    criar_gif_da_serie(fps=8)  # 8 fotos por segundo para um vídeo fluido
