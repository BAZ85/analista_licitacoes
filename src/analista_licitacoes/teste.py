from crewai.crews.crew_output import CrewOutput
from src.analista_licitacoes.utils.output_writer import salvar_resultado_json

# Exemplo fictício de output
fake_output = CrewOutput(
    json_dict={"edital": {"ente_licitante": "Teste"}, "analises": []},
    raw="raw text",
    tasks_output=[],
)

salvar_resultado_json(fake_output, "teste_saida.json")
