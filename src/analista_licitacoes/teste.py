from crewai.tools import tool
import os
from docx import Document
from striprtf.striprtf import rtf_to_text
# import textract
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTOS_DIR = os.path.join(BASE_DIR, "..", "..", "..", "documentos")


documentos_extraidos = []

for nome_arquivo in os.listdir(DOCUMENTOS_DIR):
   caminho = os.path.join(DOCUMENTOS_DIR, nome_arquivo)

   # Verifica se é um arquivo regular (evita pastas e lixos)
   if not os.path.isfile(caminho):
      continue

   nome_lower = nome_arquivo.lower()

   texto_extraido = ""

   try:
            
      if nome_lower.endswith(".docx"):
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
