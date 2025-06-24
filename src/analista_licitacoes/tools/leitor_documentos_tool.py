from crewai.tools import tool
import os
import tempfile
from docx import Document
from striprtf.striprtf import rtf_to_text
# import textract
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTOS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "documentos")

@tool("Leitura bruta de documentos da licitação")
def carregar_documentos(arquivos_upload: list = None) -> list:
    """
    Extrai o conteúdo textual de documentos.
    - Se 'arquivos_upload' for None, processa todos os arquivos em DOCUMENTOS_DIR (modo teste).
    - Se receber lista de objetos de upload (FileStorage ou dict com 'filename' e 'stream'), processa cada um.
    Retorna lista de dicts com 'nome_arquivo' e 'conteudo'.
    """

    documentos_extraidos = []

    # Define fonte de arquivos: uploads ou diretório local
    itens = []
    if arquivos_upload:
        # Processa arquivos enviados pelo usuário
        for arquivo in arquivos_upload:
            filename = getattr(arquivo, 'filename', None) or arquivo.get('filename')
            stream = getattr(arquivo, 'stream', None) or arquivo.get('stream') or arquivo
            suffix = os.path.splitext(filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(stream.read())
            tmp.close()
            itens.append((filename, tmp.name))
    else:
        # Modo teste: lê do diretório DOCUMENTS_DIR
        for nome_arquivo in os.listdir(DOCUMENTOS_DIR):
            caminho = os.path.join(DOCUMENTOS_DIR, nome_arquivo)
            # Verifica se é um arquivo regular (evita pastas e lixos)
            if os.path.isfile(caminho):
                itens.append((nome_arquivo, caminho))
        
        # Extrai texto de cada arquivo
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

        # Remove temporário de upload
        if arquivos_upload:
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

