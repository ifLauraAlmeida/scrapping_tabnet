import imageio.v3 as iio
import numpy as np
import os
from log import logger


# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))


def criar_gif_acumulado(
    pasta_origem=os.path.join(project_root, "data", "mapas_acumulados_totais"),
    nome_saida=os.path.join(
        project_root, "data", "visualizations", "evolucao_avc_rj_HISTORICO.gif"
    ),
    fps=12,
):
    """
    Cria um GIF animado a partir de imagens PNG de mapas acumulados, mostrando a evolução histórica
    de internações por AVC no Rio de Janeiro ao longo do tempo.

    Esta função lê todas as imagens PNG da pasta especificada, ordena-as cronologicamente (baseado
    no nome dos arquivos), garante que todas tenham o mesmo tamanho para evitar erros na animação,
    e salva um GIF animado com loop infinito.

    Parâmetros:
    - pasta_origem (str): Caminho da pasta contendo as imagens PNG dos mapas acumulados.
      Padrão: 'mapas_acumulados_totais'.
    - nome_saida (str): Nome do arquivo GIF de saída. Padrão: 'evolucao_avc_rj_HISTORICO.gif'.
    - fps (int): Quadros por segundo da animação. Padrão: 12 (adequado para ~18 segundos de vídeo
      com dados de 18 anos).

    Retorno:
    - None: A função não retorna valor, mas salva o GIF no diretório atual e registra logs.

    Exceções:
    - Pode lançar exceções se não houver arquivos na pasta ou se houver problemas de leitura/escrita.

    Exemplo de uso:
    >>> criar_gif_acumulado(fps=15)  # Cria GIF mais rápido
    """
    try:
        logger.info("--- INICIANDO CRIAÇÃO DO GIF HISTÓRICO ---")

        # 1. Listar e ordenar os arquivos (o nome heatmap_2008_01_Jan garante a ordem)
        arquivos = sorted([f for f in os.listdir(pasta_origem) if f.endswith(".png")])

        if not arquivos:
            logger.error(
                f"Nenhum arquivo encontrado na pasta {pasta_origem}. Gere as imagens primeiro!"
            )
            return

        logger.info(f"Lendo {len(arquivos)} quadros para o GIF...")

        # 2. Carregar as imagens garantindo que todas tenham o mesmo 'shape' (tamanho)
        imagens = []
        shapes = []

        for nome_arquivo in arquivos:
            caminho_completo = os.path.join(pasta_origem, nome_arquivo)
            img = iio.imread(caminho_completo)
            imagens.append((nome_arquivo, img))
            shapes.append(img.shape)

        target_shape = tuple(np.min(shapes, axis=0))
        if any(shape != target_shape for shape in shapes):
            logger.warning(f"Normalizando frames para o shape comum {target_shape}.")

        imagens_normalizadas = []
        for nome_arquivo, img in imagens:
            original_shape = img.shape
            if original_shape != target_shape:
                img = img[: target_shape[0], : target_shape[1], ...]
                logger.warning(
                    f"Cortando {nome_arquivo} de {original_shape} para {target_shape}."
                )
            imagens_normalizadas.append(img)

        if not imagens_normalizadas:
            logger.error(
                "Nenhuma imagem compatível foi carregada. Verifique os arquivos PNG e os tamanhos dos frames."
            )
            return

        # 3. Salvar o GIF
        # fps=12 é uma boa velocidade para 18 anos de dados (cerca de 18 segundos de vídeo)
        iio.imwrite(nome_saida, imagens_normalizadas, fps=fps, loop=0)

        logger.info(f"--- SUCESSO! GIF salvo como: {nome_saida} ---")

    except Exception as e:
        logger.error(f"Erro ao gerar o GIF: {e}")


if __name__ == "__main__":
    # Ajuste o FPS se quiser que o GIF passe mais rápido ou mais devagar
    criar_gif_acumulado(fps=15)
