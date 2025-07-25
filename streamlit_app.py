import streamlit as st
import os
import shutil
import tempfile
import json
import pandas as pd
from src.analista_licitacoes.main import run  # função run agora recebe o caminho como argumento

st.set_page_config(page_title="Análise de Licitações", page_icon="📄", layout="centered")
st.title("📄 Análise de Licitações com IA")

st.markdown("""
Faça o upload dos documentos da licitação **(Edital, Termo de Referência e Estudo Técnico Preliminar)** nos formatos PDF, DOCX, TXT ou RTF e clique em **Executar Análise**.

O sistema irá processar os documentos, realizar as análises e gerar um relatório em JSON e Excel.
""")

# Etapa 1: Upload dos arquivos
uploaded_files = st.file_uploader(
    "📤 Carregue os documentos da licitação (.pdf, .docx, .txt, .rtf)",
    type=["pdf", "docx", "txt", "rtf"],
    accept_multiple_files=True
)

# Etapa 2: Botão para executar a análise
if uploaded_files and st.button("▶️ Executar Análise"):
    with st.spinner("🔍 Analisando documentos... Isso pode levar alguns minutos..."):

        # Cria pasta temporária e salva os arquivos
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in uploaded_files:
                file_path = os.path.join(tmpdir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())

            # Executa a Crew com o caminho temporário como argumento
            try:
                run(caminho_temporario=tmpdir)
            except Exception as e:
                st.error(f"Erro ao executar a análise: {e}")
                st.stop()

            # Exibe resultados
            resultado_path = os.path.join("src", "analista_licitacoes", "output", "resultado_analise.json")
            if os.path.exists(resultado_path):
                with open(resultado_path, "r", encoding="utf-8") as f:
                    resultado = json.load(f)

                try:
                    inner = json.loads(resultado["resultado"])
                    st.subheader(":bookmark_tabs: Metadados Extraídos")
                    st.markdown(f"**Ente Licitante:** {inner['edital'].get('ente_licitante', '-')}")
                    st.markdown(f"**Número/Ano:** {inner['edital'].get('numero_ano_licitacao', '-')}")
                    st.markdown(f"**Modalidade:** {inner['edital'].get('modalidade_licitacao', '-')}")
                    st.markdown(f"**Objeto:** {inner['edital'].get('objeto_licitacao', '-')}")

                    st.subheader(":mag: Tabela de Análise")
                    df = pd.DataFrame(inner["analises"])
                    st.dataframe(df, use_container_width=True)

                    # Download do Excel
                    excel_path = os.path.join("src", "analista_licitacoes", "output", "resultado_analise.xlsx")
                    if os.path.exists(excel_path):
                        with open(excel_path, "rb") as f:
                            st.download_button(
                                label="🗃️ Baixar Resultado em Excel",
                                data=f,
                                file_name="resultado_analise.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                except Exception as e:
                    st.error(f"Erro ao carregar resultado JSON: {e}")
            else:
                st.error("Arquivo de resultado não encontrado.")

st.markdown("---")
st.caption("Autor do projeto: Bruno Alberto Zys, Auditor Público Externo do TCE/MT.")
st.caption("Este é um projeto em fase de testes. Qualquer erro, entre em contato com o autor.")