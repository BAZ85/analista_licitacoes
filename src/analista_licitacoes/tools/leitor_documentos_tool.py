from crewai.tools import tool
import os
import tempfile
from docx import Document
from striprtf.striprtf import rtf_to_text
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTOS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "documentos")

@tool("Leitura bruta de documentos da licitação")
def carregar_arquivos(arquivos_upload: list = None) -> list:
    """
    Extrai o conteúdo textual de documentos.
    - Se 'arquivos_upload' for None, processa todos os arquivos em DOCUMENTOS_DIR (modo teste).
    - Se receber lista de caminhos (str), processa cada caminho diretamente.
    - Se receber lista de objetos de upload (dict com 'filename' e 'stream'), salva em arquivo temporário e processa.
    Retorna lista de dicts com 'nome_arquivo' e 'conteudo'.
    """
    print(">>> ENTRANDO EM carregar_arquivos()")

    print("DEBUG TOOL - VALOR RECEBIDO EM arquivos_upload:")
    print(arquivos_upload)
    print("TIPO DE arquivos_upload:", type(arquivos_upload))
    if arquivos_upload:
        print("TIPO DO PRIMEIRO ELEMENTO:", type(arquivos_upload[0]))


    documentos_extraidos = []
    itens = []

    if arquivos_upload:
        if isinstance(arquivos_upload[0], str):
            # Caso: lista de caminhos absolutos
            for caminho in arquivos_upload:
                filename = os.path.basename(caminho)
                itens.append((filename, caminho))
        else:
            # Caso: lista de objetos de upload com filename e stream
            for arquivo in arquivos_upload:
                filename = getattr(arquivo, 'filename', None) or arquivo.get('filename')
                stream = getattr(arquivo, 'stream', None) or arquivo.get('stream') or arquivo
                suffix = os.path.splitext(filename)[1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(stream.read())
                tmp.close()
                itens.append((filename, tmp.name))
    else:
        # Modo teste
        for nome_arquivo in os.listdir(DOCUMENTOS_DIR):
            caminho = os.path.join(DOCUMENTOS_DIR, nome_arquivo)
            if os.path.isfile(caminho):
                itens.append((nome_arquivo, caminho))

    for nome_arquivo, caminho in itens:
        nome_lower = nome_arquivo.lower()
        texto_extraido = ""

        try:
            if nome_lower.endswith(".pdf"):
                texto_extraido = extrair_texto_pdf(caminho)

            elif nome_lower.endswith(".docx"):
                doc = Document(caminho)
                texto_extraido = "\n".join(paragrafo.text for paragrafo in doc.paragraphs)

            elif nome_lower.endswith(".txt"):
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    texto_extraido = f.read()

            elif nome_lower.endswith(".rtf"):
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo_rtf = f.read()
                texto_extraido = rtf_to_text(conteudo_rtf)

            else:
                continue

        except Exception as e:
            print(f"Erro ao processar {nome_arquivo}: {e}")
            continue

        documentos_extraidos.append({
            "nome_arquivo": nome_arquivo,
            "conteudo": texto_extraido
        })

        # Remove apenas arquivos temporários (não os caminhos absolutos)
        if arquivos_upload and not isinstance(arquivos_upload[0], str):
            try:
                os.remove(caminho)
            except:
                pass

    return documentos_extraidos

def extrair_texto_pdf(caminho_pdf: str) -> str:
    """
    Tenta extrair texto diretamente; se vazio ou falhar, faz OCR.
    """
    try:
        reader = PdfReader(caminho_pdf)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""
        if texto.strip():
            return texto
    except:
        pass  # Se erro, tenta OCR

    imagens = convert_from_path(caminho_pdf)
    texto_ocr = ""
    for img in imagens:
        texto_ocr += pytesseract.image_to_string(img, lang="por")
    return texto_ocr
