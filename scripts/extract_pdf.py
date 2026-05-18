import pdfplumber, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with pdfplumber.open('alevizaki_ref.pdf') as pdf:
    text = ''
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            text += t + '\n'

# Print later portion — where numerical parameters are typically listed
print(text[8000:18000])
