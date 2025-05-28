import os
from dotenv import dotenv_values

env = os.environ.get("ENV", "dev")
config = dotenv_values(f"./conf/{env}.env")

if not config:
    raise RuntimeError(f"Could not load config for env: {env}")
