import json
from crewai import CrewOutput


#def salvar_resultado_json(dados, path: str):
#    if isinstance (dados, CrewOutput):
#        dados = dados.final_output
#
#    with open(path, "w", encoding="utf-8") as f:
#        if isinstance(dados, str):
#            dados = dados.strip().strip("`").replace("```json", "").replace("```", "")
#            json.dump({"resultado": dados}, f, ensure_ascii=False, indent=2)
#        elif isinstance(dados, dict):
#            json.dump({"resultado": dados}, f, ensure_ascii=False, indent=2)
#        else:
#            try: 
#                json_str = json.dumps(dados, ensure_ascii=False, indent=2)
#                json.dump({"resultado": json.loads(json_str)}, f, ensure_ascii=False, indent=2)
#            except TypeError as e:
#                raise ValueError(f"Erro ao serializar objeto para JSON:{e}")

def salvar_resultado_json(dados, path: str):
    if isinstance(dados, CrewOutput):
        if dados.json_dict:
            dados = dados.json_dict
        elif dados.pydantic:
            dados = dados.pydantic.model_dump()
        else:
            dados = dados.raw

    with open(path, "w", encoding="utf-8") as f:
        if isinstance(dados, str):
            # Remove formatação Markdown
            dados_limpo = dados.strip().replace("```json", "").replace("```", "").strip("`").strip()
            try:
                # Tenta interpretar a string como JSON
                dados_json = json.loads(dados_limpo)
                json.dump({"resultado": dados_json}, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # Se não for JSON válido, salva como string mesmo
                json.dump({"resultado": dados_limpo}, f, ensure_ascii=False, indent=2)

        elif isinstance(dados, dict):
            json.dump({"resultado": dados}, f, ensure_ascii=False, indent=2)

        else:
            try:
                json_str = json.dumps(dados, ensure_ascii=False, indent=2)
                json.dump({"resultado": json.loads(json_str)}, f, ensure_ascii=False, indent=2)
            except TypeError as e:
                raise ValueError(f"Erro ao serializar objeto para JSON: {e}")


def carregar_resultado_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        outer = json.load(f)
    
    resultado_raw = outer.get("resultado")

    if isinstance(resultado_raw, str):
        try:
            return json.loads(resultado_raw)
        except json.JSONDecodeError as e: 
            raise (f"Erro ao interpretar o JSON salvo. Conteúdo bruto:\n{resultado_raw}") from e
    elif isinstance(resultado_raw, dict):
        return resultado_raw
    else:
        raise ValueError(f"O formato inesperado do campo 'resultado': {type(resultado_raw)}")
