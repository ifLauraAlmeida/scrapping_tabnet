"""
Módulo de configuração de logging para o projeto de scraping do DATASUS.

Este módulo fornece uma configuração padronizada de logging para registrar eventos,
erros e informações durante a execução dos scripts de extração de dados de internações
por AVC no Rio de Janeiro.

Funcionalidades:
- Logging simultâneo em arquivo e console
- Formatação consistente com timestamp
- Níveis de log configuráveis (DEBUG por padrão)
- Evita duplicação de handlers

Dependências:
- logging: Módulo padrão do Python para logging
- sys: Para acesso ao stdout

Uso:
    from log import logger
    logger.info("Mensagem de informação")
    logger.error("Mensagem de erro")
"""

import logging
import sys
import os


def setup_logger(name="datasus_scraper"):
    """
    Configura e retorna um logger personalizado para o projeto.

    Cria um logger com handlers para arquivo e console, formatando mensagens
    com timestamp, nível de log e mensagem. Evita adicionar handlers duplicados
    se o logger já foi configurado.

    Args:
        name (str): Nome do logger. Padrão: "datasus_scraper".

    Returns:
        logging.Logger: Instância configurada do logger.

    Notas:
        - Arquivo de log: "execucao.log" (UTF-8)
        - Nível: DEBUG (registra todos os níveis)
        - Formato: "YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE"
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Formato da mensagem: Data/Hora - Nível - Mensagem
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Caminho absoluto para a raiz do projeto
    project_root = os.path.dirname(os.path.dirname(__file__))
    log_file_path = os.path.join(project_root, "logs", "execucao.log")

    # Handler para salvar em arquivo
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Handler para exibir no console (terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Instância padrão para importação direta
logger = setup_logger()
