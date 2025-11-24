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
unique_user_ids = set()

# Legge tutti i file CSV e li aggiunge alla lista

import re
user_id_pattern = re.compile(r"user_id='([^']+)'")
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
                    else:
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
                # Estrai user_id dalla seconda colonna
                if len(row) > 1:
                    match = user_id_pattern.search(row[1])
                    if match:
                        user_id = match.group(1).strip()
                        if user_id:
                            unique_user_ids.add(user_id)
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

# Stampa il numero di user_id unici trovati

# Salva la lista degli user_id unici in un file CSV
user_id_output_file = './output/user_id_unici.csv'
with open(user_id_output_file, 'w', newline='', encoding='utf-8') as outfh:
    writer = csv.writer(outfh)
    writer.writerow(['user_id'])
    for uid in sorted(unique_user_ids):
        writer.writerow([uid])

print(f"User_id unici trovati nei file CSV: {len(unique_user_ids)}")
print(f"Lista degli user_id unici salvata in: {user_id_output_file}")

