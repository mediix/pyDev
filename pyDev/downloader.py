import tempfile
import MySQLdb
from requests import Session, get
from bs4 import BeautifulSoup
# from PyPDF2 import PdfFileReader, PdfFileWriter

base_url = 'https://www.rbkc.gov.uk'
files_storage = '/Users/medinazari/Desktop/'

with Session() as s:
  r = s.get('https://www.rbkc.gov.uk/planning/searches/details.aspx?batch=20&id=PP/14/03477&type=&tab=#tabs-planning-6')
  c = s.cookies.get_dict()
r.encoding = 'utf-8'
soup = BeautifulSoup(r.content, 'lxml')

## Table tags for depending on boroughs Documents tab
table = soup.find('table', {'id': 'casefiledocs'})  # kensigton
# table = soup.find('table', {'id': 'Documents'})   # City of Westminster/Hammersmith

#
vals = []
rows = table.findAll('tr')
for tr in rows:
  cols = tr.findAll('td')
  for td in cols:
    if td.get_text().strip() == 'Application Form':
      vals.append(base_url+tr.find('a').get('href'))

print vals

fk = lambda x: x.replace('/', '_')
if len(vals) > 1:
  print 'Length > 1'
  for idx, url in enumerate(vals):
    try:
      response = get(url, cookies=c)
      # doc = PdfFileReader(open(files_storage + 'kensigton' + '_application_form' + '_' + str(idx+1) + '.pdf', 'rb'))
      # print pdf.documentInfo
      # f = open(files_storage + 'kensigton' + '_application_form' + '_' + str(idx+1) + '.pdf', 'wb')
      # f.write(response.content)
      # doc = PdfFileReader(open(response.content))
      import pdb; pdb.set_trace()
    except Exception as err:
      raise IOError('Error Writing into File', err)
    else:
      print "%s Download Completed. :)" % ('kensigton'+'_application_form'+'_'+str(idx+1)+'.pdf')
elif len(vals) == 1:
  print 'Length == 1'
  try:
    response = get(vals[0], cookies=c)
    with tempfile.NamedTemporaryFile() as temp:
      temp.write(response.content)
    doc = PdfFileReader(open(temp, 'rb'))
    # f = open(files_storage + 'kensigton' + '_application_form' + '.pdf', 'wb')
    # f.write(response.content)
    # doc = PdfFileReader(open(f, 'rb'))
    # print pdf.documentInfo
    # doc = PdfFileReader(open(f))
    import pdb; pdb.set_trace()
  except Exception as err:
    raise IOError('Error Writing to File', err)
  else:
    print "%s Download Completed. :)" % ('kensigton'+'_application_form'+'.pdf')
else:
  print 'Length == 0'
  raise ValueError('No Document Link to Download!')
