import os
import sys
import shutil
import warnings
import json
import pandas as pd
from crewai import CrewOutput
from datetime import datetime
from src.analista_licitacoes.crew import AnalistaLicitacoes
from src.analista_licitacoes.utils.output_writer import salvar_resultado_json, carregar_resultado_json

from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

OUTPUTDIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUTDIR, exist_ok=True)


def run(caminho_temporario: str):
    """
    Executa a crew com os documentos localizados em caminho_temporario.
    """
    print(f"[DEBUG] Caminho temporário recebido: {caminho_temporario}")
    try:
        resultado = AnalistaLicitacoes().crew().kickoff(inputs={"pasta": caminho_temporario})

        print("========================")
        print(f"O tipo de 'resultado' é: {type(resultado)}")
        print(f"[DEBUG] RESULTADO DA ANÁLISE: {resultado}")
        print("========================")

###        if isinstance(resultado, CrewOutput):
###            if resultado.json_dict:
###                output = resultado.json_dict
###            else:
###                output = resultado.raw
###        else:
###            output = resultado

##        output = getattr(resultado, "final_output", None) or resultado

#        try:
#            output = resultado.final_output
#        except AttributeError:
#            output = str(resultado)

        salvar_resultado_json(resultado, os.path.join(OUTPUTDIR, "resultado_analise.json"))

###        json_path = os.path.join(OUTPUTDIR, "resultado_analise.json")
        resultado_dict = carregar_resultado_json(os.path.join(OUTPUTDIR, "resultado_analise.json"))
        
###        with open(json_path, 'r', encoding='utf-8') as f:
###            outer = json.load(f)
        
###        resultado_raw = outer.get("resultado")
###        print("[DEBUG] Resultado bruto:", resultado_raw)

###        if isinstance(resultado_raw, str):
###            try:
###                inner = json.loads(resultado_raw)
###            except json.JSONDecodeError as e:
###                raise ValueError(f"Erro ao decodificar o campo 'resultado'. Conteúdo bruto:\n{resultado_raw}") from e
###        elif isinstance(resultado_raw, dict):
###            inner = resultado_raw
###        else:
###            raise ValueError(f"O formato inesperado do campo 'resultado': {type(resultado_raw)}")
        
#        inner = json.loads(outer['resultado'])
        
        md = resultado_dict['edital']
        df = pd.DataFrame(resultado_dict['analises'])
        df = df.rename(columns={
            'numero_prompt': 'Número do prompt',
            'pergunta': 'Texto da pergunta',
            'saida': 'Resposta',
            'justificativa': 'Justificativa',
            'codigo_irregularidade': 'Código da irregularidade',
            'fundamento_legal': 'Fundamentação legal'
        })

        excel_path = os.path.join(OUTPUTDIR, "resultado_analise.xlsx")
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            ws = workbook.add_worksheet('Análise')
            writer.sheets['Análise'] = ws

            wrap_fmt = workbook.add_format({'text_wrap': True})
            header_fmt = workbook.add_format({'bold': True, 'text_wrap': True})

            ws.write('A1', 'Ente licitante', header_fmt)
            ws.write('B1', md.get('ente_licitante', '-'))
            ws.write('A2', 'Número/Ano da licitação', header_fmt)
            ws.write('B2', md.get('numero_ano_licitacao', '-'))
            ws.write('A3', 'Modalidade da licitação', header_fmt)
            ws.write('B3', md.get('modalidade_licitacao', '-'))
            ws.write('A4', 'Objeto da licitação', header_fmt)
            ws.write('B4', md.get('objeto_licitacao', '-'))

            for col_num, title in enumerate(df.columns):
                ws.write(6, col_num, title, header_fmt)

            for row_idx, row in enumerate(df.values, start=7):
                for col_idx, cell in enumerate(row):
                    ws.write(row_idx, col_idx, cell, wrap_fmt)

            ws.set_column('A:A', 23, wrap_fmt)
            ws.set_column('B:B', 28, wrap_fmt)
            ws.set_column('C:C', 14, wrap_fmt)
            ws.set_column('D:D', 51, wrap_fmt)
            ws.set_column('E:E', 34, wrap_fmt)
            ws.set_column('F:F', 34, wrap_fmt)

    except Exception as e:
        raise Exception(f"Erro ao executar a análise com a crew: {str(e)}")


def train():
    """
    Treina a crew para um número de iterações.
    """
    try:
        AnalistaLicitacoes().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs={}
        )
    except Exception as e:
        raise Exception(f"Erro durante o treinamento: {str(e)}")


def replay():
    """
    Reexecuta a crew a partir de uma task específica.
    """
    try:
        AnalistaLicitacoes().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Erro ao reexecutar a partir da task: {str(e)}")


def test():
    """
    Testa a execução da crew.
    """
    try:
        AnalistaLicitacoes().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs={}
        )
    except Exception as e:
        raise Exception(f"Erro ao testar a execução da crew: {str(e)}")


if __name__ == "__main__":
    print("Este script requer um caminho temporário como argumento.")
    print("Use-o apenas como módulo (ex: chamado via Streamlit).")
