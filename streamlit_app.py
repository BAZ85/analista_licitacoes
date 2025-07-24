import os
import sys
import json
import pandas as pd
from datetime import datetime
from io import BytesIO
import streamlit as st

# Ajuste de caminho para importar módulos dentro de src/
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analista_licitacoes.crew import AnalistaLicitacoes
from analista_licitacoes.utils.output_writer import salvar_resultado_json


# 🔧 Diretórios
BASE_TMP_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(BASE_TMP_DIR, exist_ok=True)

# 🚀 Função principal para executar a análise
def executar_analise(uploaded_files):
    session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
    tmp_dir = os.path.join(BASE_TMP_DIR, session_id)
    os.makedirs(tmp_dir, exist_ok=True)

    file_paths = []
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        out_path = os.path.join(tmp_dir, filename)
        with open(out_path, 'wb') as f:
            f.write(uploaded_file.read())
        file_paths.append(out_path)

    inputs = {'arquivos_upload': file_paths} if file_paths else {'arquivos_upload': []}

    st.info('Executando a análise... Isso pode levar alguns minutos.')

    try:
        resultado = AnalistaLicitacoes().crew().kickoff(inputs=inputs)
        output = getattr(resultado, 'final_output', str(resultado))

        # Salva JSON
        json_path = os.path.join(tmp_dir, "resultado_analise.json")
        salvar_resultado_json(output, json_path)

        # Processa para Excel
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

            ws.write('A1', 'Ente licitante', header_fmt); ws.write('B1', md.get('ente_licitante', ''))
            ws.write('A2', 'Número/Ano da licitação', header_fmt); ws.write('B2', md.get('numero_ano_licitacao', ''))
            ws.write('A3', 'Modalidade da licitação', header_fmt); ws.write('B3', md.get('modalidade_licitacao', ''))
            ws.write('A4', 'Objeto da licitação', header_fmt); ws.write('B4', md.get('objeto_licitacao', ''))

            for col_num, title in enumerate(df.columns):
                ws.write(6, col_num, title, header_fmt)

            for row_idx, row in enumerate(df.values, start=7):
                for col_idx, cell in enumerate(row):
                    ws.write(row_idx, col_idx, str(cell), wrap_fmt)

            ws.set_column('A:A', 23, wrap_fmt)
            ws.set_column('B:B', 28, wrap_fmt)
            ws.set_column('C:C', 14, wrap_fmt)
            ws.set_column('D:D', 51, wrap_fmt)
            ws.set_column('E:E', 34, wrap_fmt)
            ws.set_column('F:F', 34, wrap_fmt)

        return json_path, excel_path, session_id

    except Exception as e:
        st.error(f'Erro na execução: {e}')
        return None, None, None


# 🎨 Interface Streamlit
st.set_page_config(page_title="Análise de Licitações", page_icon="📄", layout="centered")

st.title("📄 Análise de Licitações com IA")
st.markdown("""
Faça o upload dos documentos da licitação (PDF, DOCX, TXT ou RTF) e clique em **Executar Análise**.

O sistema irá processar os documentos, realizar as análises jurídicas e gerar um relatório em JSON e Excel.
""")

uploaded_files = st.file_uploader("📤 Envie seus documentos", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'rtf'])

if st.button("🚀 Executar Análise"):
    if not uploaded_files:
        st.warning("Por favor, envie ao menos um documento para análise.")
    else:
        with st.spinner('Analisando...'):
            json_path, excel_path, session_id = executar_analise(uploaded_files)

        if json_path and excel_path:
            st.success("✅ Análise concluída com sucesso!")

            # Download JSON
            with open(json_path, 'rb') as f:
                st.download_button(
                    label="📥 Baixar JSON",
                    data=f,
                    file_name=f"resultado_analise_{session_id}.json",
                    mime="application/json"
                )

            # Download Excel
            with open(excel_path, 'rb') as f:
                st.download_button(
                    label="📥 Baixar Excel",
                    data=f,
                    file_name=f"resultado_analise_{session_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

st.markdown("---")
st.caption("Este é um projeto em fase de testes. Sugestões, reclamações e melhorias, guarde pra você!!")