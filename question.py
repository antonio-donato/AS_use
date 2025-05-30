import csv
import re

# File di input e output
input_file = './input/z_lista_domande.csv'
output_file = './output/domande_estratte.csv'

# Stringhe chiave
keywords = ["User Message: ", "Return value, user message plus compressed query: "]

# Funzione per pulire il testo: rimuove codici ANSI e decodifica caratteri Unicode
def clean_text(text):
    if not text:
        return text
    # Rimuove codici ANSI (es. \x1b[0m)
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    # Decodifica sequenze unicode escape
    try:
        text = text.encode('utf-8').decode('unicode_escape')
    except UnicodeDecodeError:
        pass  # in caso di errore, lascia il testo com'è
    return text

# Lista per salvare le domande estratte
domande_estratte = []

# Leggi il file CSV e cerca le domande dopo le stringhe chiave
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        for i, cell in enumerate(row):
            for keyword in keywords:
                if keyword in cell:
                    # Estrai la parte dopo la stringa chiave, se esiste
                    split_text = cell.split(keyword)
                    if len(split_text) > 1:
                        domanda = split_text[1].strip()
                        if domanda:
                            domanda_pulita = clean_text(domanda)
                            domande_estratte.append([domanda_pulita])

# Scrivi le domande estratte in un nuovo file CSV
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Domanda'])  # intestazione
    writer.writerows(domande_estratte)

print(f"Estratte {len(domande_estratte)} domande in '{output_file}'")

