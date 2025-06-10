import json


def salvar_resultado_json(dados, path: str):
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(dados, str):
            json.dump({"resultado": dados}, f, ensure_ascii=False, indent=2)
        else:
            json.dump(dados, f, ensure_ascii=False, indent=2)
