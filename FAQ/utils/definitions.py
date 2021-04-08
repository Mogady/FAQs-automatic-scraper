import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configs')
TOKENS_PATH = os.path.join(ROOT_DIR, 'tokens')
SPIDER_SETTINGS = os.path.join(ROOT_DIR, CONFIG_PATH, 'spider_settings.yaml')
