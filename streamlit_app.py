import os
import streamlit as st
import requests
from io import BytesIO

# 🔗 Endereço do backend API
API_URL = os.getenv("API_URL", "http://localhost:8000")  # Na máquina local, seria http://localhost:8000

st.set_page_config(page_title="Análise de Licitações", page_icon="📄")

st.title("📄 Análise de Licitações com IA")

st.markdown("""
Faça o upload dos documentos da licitação (PDF, DOCX, TXT ou RTF) e clique em **Executar Análise**.

O sistema irá processar os documentos, realizar as análises jurídicas e gerar um relatório em JSON e Excel.
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
            files = [('documentos', (file.name, file.read())) for file in uploaded_files]
            try:
                response = requests.post(f"{API_URL}/analisar", files=files, timeout=300)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Análise concluída com sucesso!")

                    # Botões de download
                    st.download_button(
                        label="📥 Baixar JSON",
                        data=requests.get(data['download_json']).content,
                        file_name="resultado_analise.json",
                        mime="application/json"
                    )
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=requests.get(data['download_xlsx']).content,
                        file_name="resultado_analise.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                else:
                    st.error(f"Erro na análise: {response.json().get('mensagem', 'Erro desconhecido')}")

            except Exception as e:
                st.error(f"Erro na conexão com a API: {e}")

st.markdown("---")
st.caption("Este é um projeto em fase de testes. Qualquer erro, entre em contato com o autor.")
st.caption("Autor do projeto: Bruno Alberto Zys (Auditor Público Externo no TCE/MT.")
