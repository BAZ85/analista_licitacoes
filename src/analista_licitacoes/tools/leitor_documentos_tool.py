from crewai.tools import tool
import os
from docx import Document
from striprtf.striprtf import rtf_to_text
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader


@tool("Leitura bruta de documentos da licitação")
def carregar_arquivos(pasta: str) -> list:
    """
    Extrai o conteúdo textual de todos os documentos na pasta informada.
    Aplica OCR em PDFs se necessário.
    Retorna uma lista de dicionários com 'nome_arquivo' e 'conteudo'.

    Parâmetros:
    - pasta: Caminho para a pasta onde estão os arquivos a serem analisados.
    """
    print(f"[DEBUG] Pasta recebida na tool: {pasta}")
    documentos_extraidos = []

    pasta_absoluta = os.path.abspath(pasta)

    if not os.path.exists(pasta_absoluta):
        raise FileNotFoundError(f"A pasta '{pasta_absoluta}' não foi encontrada.")

    for nome_arquivo in os.listdir(pasta_absoluta):
        caminho = os.path.join(pasta_absoluta, nome_arquivo)

        if not os.path.isfile(caminho):
            continue

        nome_lower = nome_arquivo.lower()
        texto_extraido = ""

        try:
            if nome_lower.endswith(".pdf"):
                texto_extraido = extrair_texto_pdf(caminho)

            elif nome_lower.endswith(".docx"):
                doc = Document(caminho)
                texto_extraido = "\n".join(p.text for p in doc.paragraphs)

            elif nome_lower.endswith(".txt"):
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    texto_extraido = f.read()

            elif nome_lower.endswith(".rtf"):
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo_rtf = f.read()
                texto_extraido = rtf_to_text(conteudo_rtf)

            else:
                continue  # Ignora formatos não suportados

        except Exception as e:
            print(f"[Erro] Falha ao processar '{nome_arquivo}': {e}")
            continue

        documentos_extraidos.append({
            "nome_arquivo": nome_arquivo,
            "conteudo": texto_extraido
        })

    return documentos_extraidos


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """
    Tenta extrair texto de PDF. Se falhar, aplica OCR página a página.
    """
    try:
        reader = PdfReader(caminho_pdf)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""
        if texto.strip():
            return texto
    except Exception as e:
        print(f"[Aviso] Falha na extração direta do PDF: {e}")

    try:
        imagens = convert_from_path(caminho_pdf)
        texto_ocr = ""
        for img in imagens:
            texto_ocr += pytesseract.image_to_string(img, lang="por")
        return texto_ocr
    except Exception as e:
        print(f"[Erro] Falha na extração via OCR: {e}")
        return ""
