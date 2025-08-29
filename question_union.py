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

    # Correzioni per caratteri mal decodificati (spesso dovuti a encoding mismatches)
    # Ordine importante: sostituisci prima le sequenze più lunghe
    replacements = {
        'Ã¨': 'è',
        'Ã²': 'ò',
        'Ã¹': 'ù',
        'Ã': 'à',
        'Ã¬': 'ì',
        'é': 'è',
        'à©': 'è',
    }
    for k, v in replacements.items():
        if k in text:
            text = text.replace(k, v)

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
seen_rows = set()
combined_rows = []
header_row = None
total_rows_read = 0

# Legge tutti i file CSV e li aggiunge alla lista
for file in csv_files:
    try:
        with open(file, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            first_row_in_file = True
            for row in reader:
                # conta righe (esclude header dalla conta dei record letti)
                if first_row_in_file:
                    # registra l'header dal primo file
                    if header_row is None:
                        header_row = tuple(row)
                        # non contiamo l'header come record dati
                    else:
                        # se la prima riga del file corrente è identica all'header registrato,
                        # la saltiamo come header; altrimenti la trattiamo come record dati
                        if tuple(row) == header_row:
                            first_row_in_file = False
                            continue
                    first_row_in_file = False
                    continue

                total_rows_read += 1
                key = tuple(row)
                if key not in seen_rows:
                    seen_rows.add(key)
                    combined_rows.append(row)
    except Exception as e:
        print(f"Errore durante la lettura di {file}: {e}")

# Scrivi il file unificato rispettando l'header originale (se presente)
with open(input_file, 'w', newline='', encoding='utf-8') as outfh:
    writer = csv.writer(outfh)
    if header_row is not None:
        writer.writerow(list(header_row))
    writer.writerows(combined_rows)

duplicates = total_rows_read - len(combined_rows)
print(f"Record totali letti (esclusi header): {total_rows_read}")
print(f"Duplicati trovati e scartati: {duplicates}")
print(f"File unificato salvato in: {input_file}")

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
        # restituisci la data nello stesso formato del file di input: 'Aug 29, 2025'
        date = f"{month} {day}, {year}"
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

def extract_user_prompt_from_text(text):
    """Estrae il valore associato a user_prompt in modo robusto anche con virgolette raddoppiate."""
    if not text:
        return None
    s = text.replace('""', '"').replace("''", "'")
    # cerca la parola user_prompt (case-insensitive)
    idx = s.lower().find('user_prompt')
    if idx == -1:
        return None
    # cerca il carattere ':' dopo user_prompt
    colon = s.find(':', idx)
    if colon == -1:
        return None
    # cerca la prima virgoletta dopo i due punti
    # preferisci doppia virgoletta, poi singola
    dq = s.find('"', colon)
    sq = s.find("'", colon)
    if dq == -1 and sq == -1:
        # fallback usando regex per prendere fino a virgola o parentesi
        m = _re.search(r'user_prompt\s*[:=]\s*([^,\)\}\n]+)', s, flags=_re.IGNORECASE)
        if m:
            return clean_text(m.group(1).strip().strip('"\''))
        return None
    # scegli il tipo di virgoletta più vicina
    if dq == -1 or (sq != -1 and sq < dq):
        start = sq + 1
        quote_char = "'"
    else:
        start = dq + 1
        quote_char = '"'
    end = s.find(quote_char, start)
    if end == -1:
        # se non trovi la chiusura, prendi fino a parenth o fine stringa
        end = len(s)
    prompt = s[start:end].strip()
    return clean_text(prompt)

# Lista per salvare le domande estratte (now with date and time)
domande_estratte = []

# Leggi il file CSV combinato e cerca le domande dopo le stringhe chiave
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # unisci la riga in una stringa per facilitare la ricerca di data/ora
        row_text = ' '.join(cell for cell in row if cell)

        # Primo tentativo: estrai Data/Ora dalla prima colonna se presente
        data = None
        ora = None
        if len(row) > 0 and row[0]:
            d0, t0 = extract_date_time_from_text(row[0])
            if d0:
                data = d0
            if t0:
                ora = t0

        # Prova a estrarre la domanda dal campo user_prompt nella riga
        domanda_pulita = None
        # cerco prima nella riga completa
        domanda_pulita = extract_user_prompt_from_text(row_text)
        # se non trovata, cerca in ciascuna cella
        if not domanda_pulita:
            for cell in row:
                domanda_pulita = extract_user_prompt_from_text(cell)
                if domanda_pulita:
                    break

        # Se ancora non trovata, usa i keywords esistenti (fallback)
        if not domanda_pulita:
            for i, cell in enumerate(row):
                for keyword in keywords:
                    if keyword in cell:
                        split_text = cell.split(keyword)
                        if len(split_text) > 1:
                            domanda = split_text[1].strip()
                            if domanda:
                                domanda_pulita = clean_text(domanda)
                                # se Data/Ora non ancora trovati, prova a cercarli nella riga
                                if not data or not ora:
                                    d, t = extract_date_time_from_text(row_text)
                                    if d and not data:
                                        data = d
                                    if t and not ora:
                                        ora = t
                                break
                if domanda_pulita:
                    break

        # Se abbiamo una domanda valida, assicurati di avere Data/Ora provando diverse fonti
        if domanda_pulita:
            # se mancano dati, cerca in celle diverse dalla prima
            if not data or not ora:
                # priorità: cella con keyword (se identificata), poi riga completa, poi altre celle
                d, t = extract_date_time_from_text(row_text)
                if d and not data:
                    data = d
                if t and not ora:
                    ora = t
                # cerca nelle singole celle
                for c in row:
                    if (not data) or (not ora):
                        d, t = extract_date_time_from_text(c)
                        if d and not data:
                            data = d
                        if t and not ora:
                            ora = t
                    else:
                        break
            domande_estratte.append([data or '', ora or '', domanda_pulita])

# Scrivi le domande estratte in un nuovo file CSV con intestazioni Data, Ora, Domanda
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Data', 'Ora', 'Domanda'])  # intestazione nell'ordine richiesto
    writer.writerows(domande_estratte)

print(f"Estratte {len(domande_estratte)} domande in '{output_file}'")

