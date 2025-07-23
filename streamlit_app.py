import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
from src.analista_licitacoes.crew import AnalistaLicitacoes
from src.analista_licitacoes.utils.output_writer import salvar_resultado_json

st.set_page_config(page_title="Análise de Licitações", page_icon="📄")
st.title("📄 Análise de Licitações com IA")

st.markdown("""
Faça o upload dos documentos da licitação (PDF, DOCX, TXT ou RTF) e clique em **Executar Análise**.

O sistema irá processar os documentos, realizar as análises e gerar um relatório em JSON e Excel.
""")

uploaded_files = st.file_uploader(
    "📤 Envie seus documentos",
    type=["pdf", "docx", "txt", "rtf"],
    accept_multiple_files=True
)

if st.button("🚀 Executar Análise"):
    if not uploaded_files:
        st.warning("Por favor, envie pelo menos um documento.")
    else:
        with st.spinner('🔍 Analisando... Isso pode levar alguns minutos...'):

            # Cria uma pasta temporária para salvar os arquivos
            session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            session_dir = os.path.join("output", session_id)
            os.makedirs(session_dir, exist_ok=True)

            file_paths = []
            arquivos_upload = []

            for file in uploaded_files:
                path = os.path.join(session_dir, file.name)
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                file_paths.append(path)

                # Corrigido: prepara dicionário com filename e stream (BytesIO)
                arquivos_upload.append({
                    "filename": file.name,
                    "stream": BytesIO(file.getvalue())
                })

            try:
                resultado = AnalistaLicitacoes().crew().kickoff(inputs={"arquivos_upload": arquivos_upload})
                output = getattr(resultado, 'final_output', str(resultado))

                json_path = os.path.join(session_dir, "resultado_analise.json")
                salvar_resultado_json(output, json_path)

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

                # Cria planilha Excel em memória
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
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

                st.success("✅ Análise concluída com sucesso!")

                # Botões de download
                st.download_button(
                    label="📥 Baixar JSON",
                    data=json.dumps(outer, indent=2),
                    file_name="resultado_analise.json",
                    mime="application/json"
                )
                st.download_button(
                    label="📥 Baixar Excel",
                    data=excel_buffer.getvalue(),
                    file_name="resultado_analise.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Ocorreu um erro durante a análise: {e}")

st.markdown("---")
st.caption("Autor do projeto: Bruno Alberto Zys, Auditor Público Externo do TCE/MT.")
st.caption("Este é um projeto em fase de testes. Qualquer erro, entre em contato com o autor.")
