import base64
import json
import csv
from collections import Counter
import re
import os
import glob
import pandas as pd

# Percorso del file CSV da cui leggere

output_file_path = "./output/username_counts.csv"
input_folder = "./input_folder"
input_file_path = "./input/csv_unito.csv"

def decode_base64_url(encoded_str):
    """Converte base64url in base64 standard e decodifica"""
    # Aggiungi padding se necessario
    padding = len(encoded_str) % 4
    if padding == 2:
        encoded_str += '=='
    elif padding == 3:
        encoded_str += '='
    
    # Sostituisci i caratteri speciali di base64url con quelli di base64 standard
    encoded_str = encoded_str.replace('-', '+').replace('_', '/')
    
    try:
        # Decodifica la stringa
        return base64.b64decode(encoded_str)
    except Exception as e:
        print(f"Errore nella decodifica: {e}")
        return None

def decode_jwt(token, part=2, field=None):
    """
    Decodifica un JWT e restituisce la parte specificata (header=1, payload=2)
    Se specificato un campo, restituisce il valore di quel campo
    """
    try:
        parts = token.strip().split('.')
        if len(parts) < 3:
            return None
        
        decoded = decode_base64_url(parts[part-1])
        if not decoded:
            return None
            
        json_data = json.loads(decoded)
        
        if field:
            return json_data.get(field)
        return json_data
    except Exception as e:
        print(f"Errore nel parsing del JWT: {e}")
        return None

def main():
    
    # Unisci tutti i file CSV in un unico file di output

    # Trova tutti i file CSV nella cartella
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

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
        combined_df.to_csv(input_file_path, index=False)
        print(f"File unificato salvato in: {input_file_path}")
    else:
        print("Nessun file CSV trovato o leggibile.")
        exit

    # Regex per trovare i token JWT (3 segmenti separati da punti)
    token_pattern = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")

    # Set per evitare duplicati
    found_tokens = set()

    # Legge e cerca i token riga per riga
    with open(input_file_path, "r", encoding="utf-8") as f:
        for line in f:
            matches = token_pattern.findall(line)
            found_tokens.update(matches)

    username_counts = Counter()
    client_counts = Counter()
    line_number = 0
    
    try:
        # Elaborazione del file di input
        for token in found_tokens:
                line_number += 1
                line = token.strip()
                
                # Salta le righe vuote
                if not line:
                    continue
                
                # Stampa messaggi di debug ogni 100 righe
                if line_number % 100 == 0:
                    print(f"Processing line number: {line_number}")
                
                # Estrai il nome utente dal payload del JWT
                username = decode_jwt(line, part=2, field="user_name")
                client_id = decode_jwt(line, part=2, field="client_id")
                
                # check = str(username)
                # if check.find("barberis") != -1:
                #     print(f"Found username with 'barberis': {check} in token: {line}")
                #     breakpoint()
                    
                # Conta solo i nomi utente non vuoti
                if username and username != "null":
                    username_counts[username] += 1
                    
                if client_id and client_id != "null":
                    client_counts[client_id] += 1
        
        print(f"Finished processing {line_number} lines")
        
        # Calcola il conteggio totale
        # total_count = sum(username_counts.values())
        # clients_count = sum(client_counts.values())
        
        # Genera il file CSV
        with open(output_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Intestazione
            csv_writer.writerow(['External_ID', 'Farmacia', 'Conteggio'])
            
            # Dati ordinati per conteggio decrescente
            for username, count in username_counts.most_common():
                if "." in username:
                    parti = username.split(".", 1)
                    codice = parti[0]
                    
                    if re.fullmatch(r"F\d+", codice):
                        descrizione = parti[1].replace(".", " ").upper()
                    else:
                        codice = None
                        # Se il codice non è un codice F, usa l'intero username come descrizione
                        descrizione = username.replace(".", " ").upper()
                else:
                    codice = None
                    descrizione = username.upper()
                    
                if descrizione != "DONANT" and descrizione != "DAVIDE GIUDICI":
                    csv_writer.writerow([codice, descrizione, count])
        
        print(f"Results have been saved to {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()