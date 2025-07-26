import streamlit as st
import os
import tempfile
import json
import pandas as pd
from src.analista_licitacoes.main import run  # função run agora recebe o caminho como argumento
from src.analista_licitacoes.utils.output_writer import carregar_resultado_json


st.set_page_config(page_title="Análise de Licitações", page_icon="📄", layout="wide")
st.title("📄 Análise de Licitações com IA")

for key in ["analise_executada", "caminho_temp", "exibir_resultado", "excel_bytes"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "excel_bytes" else None
# Inicializa o estado da sessão
#if "analise_executada" not in st.session_state:
#    st.session_state.analise_executada = False

#if "caminho_temp" not in st.session_state:
#    st.session_state.caminho_temp = None

#if "exibir_resultado" not in st.session_state:
#    st.session_state.exibir_resultado = False

#if "excel_bytes" not in st.session_state:
#    st.session_state.excel_bytes = None

# Etapa 1: Upload dos arquivos
if not st.session_state.exibir_resultado:
    st.markdown("""
    Faça o upload dos documentos da licitação **(Edital, Termo de Referência e Estudo Técnico Preliminar)** nos formatos PDF, DOCX, TXT ou RTF e clique em **Executar Análise**.
    """)

    uploaded_files = st.file_uploader(
        "📤 Carregue os documentos da licitação (.pdf, .docx, .txt, .rtf)",
        type=["pdf", "docx", "txt", "rtf"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("▶️ Executar Análise"):
        with st.spinner("🔍 Analisando documentos... Isso pode levar alguns minutos..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                for file in uploaded_files:
                    file_path = os.path.join(tmpdir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())

                try:
                    run(caminho_temporario=tmpdir)
                except Exception as e:
                    st.error(f"Erro ao executar a análise: {e}")
                    st.stop()

                # Lê os resultados após execução
                resultado_path = os.path.join("src", "analista_licitacoes", "output", "resultado_analise.json")
                excel_path = os.path.join("src", "analista_licitacoes", "output", "resultado_analise.xlsx")

                if os.path.exists(resultado_path) and os.path.exists(excel_path):
                    st.session_state.exibir_resultado = True    
#                    with open(resultado_path, "r", encoding="utf-8") as f:
#                        resultado = json.load(f)
                    with open(excel_path, "rb") as ef:
                        st.session_state.excel_bytes = ef.read()                  
                else:
                    st.error("Resultado não encontrado. Verifique se a análise foi concluída.")
                    st.stop()

# Etapa 2: Exibir resultados
if st.session_state.exibir_resultado:
    resultado_path = os.path.join("src", "analista_licitacoes", "output", "resultado_analise.json")
    try:
#        with open(resultado_path, "r", encoding="utf-8") as f:
#            resultado = json.load(f)
#        inner = json.loads(resultado["resultado"])
        resultado = carregar_resultado_json(resultado_path
                                            )
        st.subheader(":bookmark_tabs: Metadados Extraídos")
        st.markdown(f"**Ente Licitante:** {resultado['edital'].get('ente_licitante', '-')}")
        st.markdown(f"**Número/Ano:** {resultado['edital'].get('numero_ano_licitacao', '-')}")
        st.markdown(f"**Modalidade:** {resultado['edital'].get('modalidade_licitacao', '-')}")
        st.markdown(f"**Objeto:** {resultado['edital'].get('objeto_licitacao', '-')}")

        st.subheader(":mag: Resultado da Análise")
        df = pd.DataFrame(resultado["analises"])
        st.dataframe(df, use_container_width=True)

        if st.session_state.excel_bytes:
            st.download_button(
                label="🗃️ Baixar Resultado em Excel",
                data=st.session_state.excel_bytes,
                file_name="resultado_analise.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Botão para reiniciar a análise
        if st.button("🔄 Nova Análise"):
            for key in ["analise_executada", "exibir_resultado", "excel_bytes"]:
                st.session_state[key] = False if key != "excel_bytes" else None
#            st.session_state.exibir_resultado = False
#            st.session_state.excel_bytes = None
            st.rerun()

    except Exception as e:
        st.error(f"Erro ao carregar resultado JSON: {e}")

st.markdown("---")
st.caption("Autor do projeto: Bruno Alberto Zys, Auditor Público Externo do TCE/MT.")
st.caption("Este é um projeto em fase de testes. Qualquer erro, entre em contato com o autor.")
