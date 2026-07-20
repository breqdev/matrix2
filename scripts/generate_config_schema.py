from json import dump

from matrix.utils.config import Config

with open("matrix_schema.json", "w") as f:
    dump(Config.model_json_schema(), f, indent=2)
