import os
import pandas as pd
import json


OUTPUTDIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUTDIR, exist_ok=True)

json_path = os.path.join(OUTPUTDIR, "resultado_analise.json")
excel_path = os.path.join(OUTPUTDIR, "resultado_analise.xlsx")

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
         ws.write(5, col_num, title, header_fmt)

      for row_idx, row in enumerate(df.values, start=7):
         for col_idx, cell in enumerate(row):
            ws.write(row_idx, col_idx, cell, wrap_fmt)
      
      ws.set_column('A:A', 23, wrap_fmt)
      ws.set_column('B:B', 28, wrap_fmt)
      ws.set_column('C:C', 14, wrap_fmt)
      ws.set_column('D:D', 51, wrap_fmt)
      ws.set_column('E:E', 34, wrap_fmt)
      ws.set_column('F:F', 34, wrap_fmt)
