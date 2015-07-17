import scraps

# Step 1: without apply

class CetipScrap(scraps.Scrap):
    data = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDateDI"]')
    taxa = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDI"]')

scrap = CetipScrap()
scrap.fetch('http://www.cetip.com.br')

print(scrap.data)
print(scrap.taxa)

# Step 2: with apply

from datetime import datetime

def strptime(format='%Y-%m-%d'):
    return lambda text: datetime.strptime(text, format)

def replace(_from, _to):
    def _replace(text):
        for f, t in zip(_from, _to):
            text = text.replace(f, t)
        return text
    return _replace

divide_by = lambda x: lambda y: y/x

class CetipScrap(scraps.Scrap):
    data = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDateDI"]', apply=[
        strptime('(%d/%m/%Y)')
    ])
    taxa = scraps.Attribute(xpath='//*[@id="ctl00_Banner_lblTaxDI"]', apply=[
        replace([',', '%'], ['.', '']), float, divide_by(100)
    ])

scrap = CetipScrap()
scrap.fetch('http://www.cetip.com.br')

print(scrap.data)
print(scrap.taxa)