import os
import sys
import warnings
import json
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from src.analista_licitacoes.crew import AnalistaLicitacoes
from src.analista_licitacoes.utils.output_writer import salvar_resultado_json
    
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

#OUTPUTDIR = os.path.join(os.path.dirname(__file__), "output")
tmp_dir = os.path.join(os.path.dirname(__file__), 'output')
#os.makedirs(OUTPUTDIR, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

app = Flask(__name__)

def send_and_delete(path: str, download_name: str):
    """
    Envia o arquivo via HTTP e deleta após a resposta ser enviada.
    """
    if not os.path.isfile(path):
        abort(404)
    response = send_file(
        path,
        as_attachment = True,
        download_name=download_name
    )

    @response.call_on_close
    def _cleanup():
        try:
            os.remove(path)
        except OSError:
            pass
        return response
    
@app.route('/analisar', methods=['POST'])
def analisar():
    """
    Recebe uploads de documentos, executa análise via CrewAI, gera JSON e Excel em OUTPUTDIR,
    e retorna links de download.
    """
    # Recebe arquivos do usuário (pode ser lista vazia)
    uploads = request.files.getlist('documentos')
    file_paths = []
    for f in uploads:
        filename = secure_filename(f.filename)
        out_path = os.path.join(tmp_dir, filename)
        f.save(out_path)
        file_paths.append(out_path)

    # Prepara inputs para o CrewAI
    inputs = {'arquivos_upload': file_paths} if file_paths else {}
 
    # Executa a crew
    resultado = AnalistaLicitacoes().crew().kickoff(inputs=inputs)

    try:
        output = resultado.final_output
    except AttributeError:
        output = str(resultado)

    # Salva JSON no servidor
    json_path = os.path.join(tmp_dir, "resultado_analise.json")
    salvar_resultado_json(output, json_path)

    # Gera planilha Excel com base no JSON
    excel_path = os.path.join(tmp_dir, "resultado_analise.xlsx")
    with open(json_path, 'r', encoding='utf-8') as f:
        outer = json.load(f)        
    inner = json.loads(outer['resultado'])
    md = inner['edital']
    df = pd.DataFrame(inner['analises'])
    df = df.rename(columns={
        'numero_prompt': 'Número do prompt',
        'pergunta': 'Texto da pergunta',
        'saida': 'Resposta',
        'justificativa': 'Justificativa',
        'codigo_irregularidade': 'Código da irregularidade',
        'fundamento_legal': 'Fundamentação legal'
    })

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        ws = workbook.add_worksheet('Análise')
        writer.sheets['Análise'] = ws

        wrap_fmt = workbook.add_format({'text_wrap': True})
        header_fmt = workbook.add_format({'bold': True, 'text_wrap': True})

        ws.write('A1', 'Ente licitante', header_fmt); ws.write('B1', md.get('ente_licitante', wrap_fmt))
        ws.write('A2', 'Número/Ano da licitação', header_fmt); ws.write('B2', md.get('numero_ano_licitacao', wrap_fmt))
        ws.write('A3', 'Modalidade da licitação', header_fmt); ws.write('B3', md.get('modalidade_licitacao', wrap_fmt))
        ws.write('A4', 'Objeto da licitação', header_fmt); ws.write('B4', md.get('objeto_licitacao', wrap_fmt))

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
  
    # Retorna links de download
    base = request.url_root.rstrip('/')
    return jsonify({
        'status': 'sucesso',
        'download_json': f'{base}/download/json',
        'download_xlsx': f'{base}/download/xlsx'
    })

@app.route('/download/json', methods=['GET'])
def download_json():
    path = os.path.join(tmp_dir, 'resultado_analise.json')
    return send_and_delete(path, 'resultado_analise.json')

@app.route('/download/xlsx', methods=['GET'])
def download_xlsx():
    path = os.path.join(tmp_dir, 'resultado_analise.xlsx')
    return send_and_delete(path, 'resultado_analise.xlsx')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)