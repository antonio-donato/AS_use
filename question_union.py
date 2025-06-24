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
input_file = "./input/lista_domande_unito.csv"
output_file = './output/domande_estratte.csv'

# Unisci tutti i file CSV in un unico file di output

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

# Unisce tutti i DataFrame e rimuove i duplicati
if all_dfs:
    combined_df = pd.concat(all_dfs).drop_duplicates()
    combined_df.to_csv(input_file, index=False)
    print(f"File unificato salvato in: {input_file}")
else:
    print("Nessun file CSV trovato o leggibile.")
    exit

# Stringhe chiave
keywords = ["User Message: ", "Return value, user message plus compressed query: "]

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

