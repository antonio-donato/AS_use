import re
import os
import glob

# Percorso del file CSV da cui leggere
# input_file = "kibana_2025_05_22.csv"
    
# Cerca un file .csv nella cartella ./input
input_folder = "./input"
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

if not csv_files:
    print(f"Nessun file CSV trovato nella cartella {input_folder}")
    exit()

# Usa il primo file trovato
input_file = csv_files[0]
print(f"File selezionato: {input_file}")

# Percorso del file di output dove salvare i token
output_file = "./output/extracted_tokens.txt"

# Regex per trovare i token JWT (3 segmenti separati da punti)
token_pattern = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")

# Set per evitare duplicati
found_tokens = set()

# Legge e cerca i token riga per riga
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        matches = token_pattern.findall(line)
        found_tokens.update(matches)

# Scrive i token trovati in un file di output
with open(output_file, "w", encoding="utf-8") as f:
    for token in found_tokens:
        f.write(token + "\n")

print(f"{len(found_tokens)} token trovati e salvati in '{output_file}'.")
