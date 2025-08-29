import csv
import re
import glob
import os
import pandas as pd

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

# File di input e output
input_folder = "./input_folder_question"
input_file = './output/_combined_input.csv'
output_file = './output/domande_estratte.csv'

# Trova tutti i file CSV nella cartella
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
if not csv_files:
    print("Nessun file CSV trovato nella cartella specificata.")
    exit()
    
# Stampa i file trovati
print(f"Lista dei file trovati nella cartella '{input_folder}':")
for f in csv_files:
    print(f" - {f}")
print(f"Trovati {len(csv_files)} file CSV nella cartella '{input_folder}'.")
print("Unendo i file...")

# Lista per contenere tutti i DataFrame
all_dfs = []

# Legge tutti i file CSV e li aggiunge alla lista
for file in csv_files:
    try:
        df = pd.read_csv(file)
        all_dfs.append(df)
    except Exception as e:
        print(f"Errore durante la lettura di {file}: {e}")

# Conteggia i record totali prima della rimozione dei duplicati
if all_dfs:
    total_records = sum(len(df) for df in all_dfs)
    print(f"Record totali prima della rimozione dei duplicati: {total_records}")
    combined_df = pd.concat(all_dfs)
    unique_records = len(combined_df.drop_duplicates())
    duplicates = len(combined_df) - unique_records
    print(f"Duplicati trovati e scartati: {duplicates}")
    combined_df = combined_df.drop_duplicates()
    combined_df.to_csv(input_file, index=False)
    print(f"File unificato salvato in: {input_file}")
else:
    print("Nessun file CSV trovato o leggibile.")
    exit

# Stringhe chiave
keywords = ["User Message: ", "Return value, user message plus compressed query: "]

# funzione per estrarre data e ora da un testo
import re as _re

def extract_date_time_from_text(text):
    if not text:
        return (None, None)
    # cerca pattern datetime ISO e altri formati comuni
    patterns = [
        r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)",
        r"(\d{2}/\d{2}/\d{4})[ T](\d{2}:\d{2}(?::\d{2})?)",
        r"(\d{2}-\d{2}-\d{4})[ T](\d{2}:\d{2}(?::\d{2})?)",
        r"(\d{4}/\d{2}/\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)",
    ]
    for p in patterns:
        m = _re.search(p, text)
        if m:
            return (m.group(1), m.group(2))

    # pattern con mese prima del giorno (es. Aug 29, 2025 @ 10:50:13.049)
    month_first = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2}),\s*(\d{4})(?:[ \t@T]+(\d{2}:\d{2}:\d{2}(?:\.\d+)?))?"
    m = _re.search(month_first, text, flags=_re.IGNORECASE)
    if m:
        month = m.group(1)
        day = m.group(2)
        year = m.group(3)
        time = m.group(4)
        date = f"{day} {month} {year}"
        return (date, time)

    # pattern con nomi dei mesi (es. 29 Aug 2025 o August 29, 2025)
    month_pattern = r"(\d{1,2})[ ]*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ ,]+(\d{4})(?:[ T]+(\d{2}:\d{2}(?::\d{2})?))?"
    m = _re.search(month_pattern, text, flags=_re.IGNORECASE)
    if m:
        day = m.group(1)
        month = m.group(2)
        year = m.group(3)
        time = m.group(4)
        date = f"{day} {month} {year}"
        return (date, time)

    # se non trovato, prova a cercare separatamente date e orari
    date = None
    time = None
    date_patterns = [r"(\d{4}-\d{2}-\d{2})", r"(\d{2}/\d{2}/\d{4})", r"(\d{2}-\d{2}-\d{4})", r"(\d{4}/\d{2}/\d{2})"]
    # supporta anche secondi frazionari
    time_patterns = [r"(\d{2}:\d{2}:\d{2}(?:\.\d+)?)", r"(\d{2}:\d{2})"]
    for dp in date_patterns:
        m = _re.search(dp, text)
        if m:
            date = m.group(1)
            break
    for tp in time_patterns:
        m = _re.search(tp, text)
        if m:
            time = m.group(1)
            break
    return (date, time)

# Lista per salvare le domande estratte (now with date and time)
domande_estratte = []

# Leggi il file CSV combinato e cerca le domande dopo le stringhe chiave
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # unisci la riga in una stringa per facilitare la ricerca di data/ora
        row_text = ' '.join(cell for cell in row if cell)
        for i, cell in enumerate(row):
            for keyword in keywords:
                if keyword in cell:
                    split_text = cell.split(keyword)
                    if len(split_text) > 1:
                        domanda = split_text[1].strip()
                        if domanda:
                            domanda_pulita = clean_text(domanda)
                            # prova ad estrarre data/ora dalla cella, poi dall'intera riga e infine dalle altre celle
                            data = None
                            ora = None
                            search_texts = [cell, ' '.join(row), ' '.join(c for idx, c in enumerate(row) if idx != i)]
                            for txt in search_texts:
                                d, t = extract_date_time_from_text(txt)
                                if d and not data:
                                    data = d
                                if t and not ora:
                                    ora = t
                                if data and ora:
                                    break
                            # se non trovata, lascia stringhe vuote
                            domande_estratte.append([domanda_pulita, data or '', ora or ''])

# Scrivi le domande estratte in un nuovo file CSV con intestazioni Data e Ora
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Domanda', 'Data', 'Ora'])  # intestazione
    writer.writerows(domande_estratte)

print(f"Estratte {len(domande_estratte)} domande in '{output_file}'")

