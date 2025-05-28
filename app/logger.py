import logging
from colorlog import ColoredFormatter
import sys
from app.config import env

# Crée un logger
logger = logging.getLogger("kavale_api")

# Choix du niveau selon l'env
logger.setLevel(logging.DEBUG if env == "dev" else logging.INFO)

# Handler console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# ANSI pour gras et italique
BOLD = '\033[1m'
ITALIC = '\033[3m'
RESET = '\033[0m'

# format coloré pour le terminal
formatter = ColoredFormatter(
    f"%(log_color)s{BOLD}[%(asctime)s]%(reset)s %(log_color)s%(levelname)s in %(name)s: {ITALIC}%(message)s{RESET}",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    },
    reset=True
)

console_handler.setFormatter(formatter)

# Ajoute le handler au logger
logger.addHandler(console_handler)
