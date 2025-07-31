import base64
import json
import csv
from collections import Counter
import re
import os
import glob
import pandas as pd
from collections import defaultdict
import datetime  # aggiunto per la gestione della data

# Percorso del file CSV da cui leggere

output_file_path = "./output/count_daily.csv"
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

    # Mappa per conteggiare (tenant_id, descrizione, data)
    counts = Counter()
    # Mappa username -> tenant_id
    username_to_tenant = dict()
    # Mappa username -> descrizione
    username_to_descrizione = dict()

    # Legge tutti i file CSV e processa riga per riga
    for file in csv_files:
        try:
            with open(file, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    data_str = row[0]
                    # Normalizza la data in formato GG/MM/AAAA
                    try:
                        # Rimuovi eventuale parte oraria e normalizza
                        # Gestione formato tipo 'Jun 5, 2025 @ 15:35:40.948'
                        match = re.search(r'(\w{3,}) (\d{1,2}), (\d{4})', data_str)
                        if match:
                            mese, giorno, anno = match.groups()
                            mese_num = pd.to_datetime(mese, format='%b').month
                            data_str = f"{int(giorno):02d}/{int(mese_num):02d}/{anno}"
                        else:
                            dt = pd.to_datetime(data_str, errors='coerce', dayfirst=False)
                            if pd.notnull(dt):
                                data_str = dt.strftime('%d/%m/%Y')
                            else:
                                # Prova a estrarre solo la parte di data se il parsing fallisce
                                match = re.search(r'(\d{1,2})[\s/-](\w+)[\s/-](\d{4})', data_str)
                                if match:
                                    giorno, mese, anno = match.groups()
                                    # Gestione mese in lettere
                                    try:
                                        mese_num = pd.to_datetime(mese, format='%b').month
                                    except:
                                        try:
                                            mese_num = pd.to_datetime(mese, format='%B').month
                                        except:
                                            mese_num = 1
                                    data_str = f"{int(giorno):02d}/{int(mese_num):02d}/{anno}"
                    except Exception:
                        pass
                    for cell in row[1:]:
                        # Cerca token JWT
                        matches = token_pattern.findall(cell)
                        for token in matches:
                            username = decode_jwt(token, part=2, field="user_name")
                            client_id = decode_jwt(token, part=2, field="client_id")
                            # Sostituzione client_id
                            if client_id == "askStellaStandalone":
                                client_id_label = "Wingesfar"
                            elif client_id == "g3pAngularClient":
                                client_id_label = "Stella"
                            else:
                                client_id_label = client_id
                            custom_info = decode_jwt(token, part=2, field="CustomInfo")
                            tenant_id = custom_info.get("tenantId") if custom_info else None
                            if username and username != "null" and tenant_id and tenant_id != "null":
                                # Calcola descrizione
                                if "." in username:
                                    parti = username.split(".", 1)
                                    codice = parti[0]
                                    if re.fullmatch(r"F\d+", codice):
                                        descrizione = parti[1].replace(".", " ").upper()
                                    else:
                                        descrizione = username.replace(".", " ").upper()
                                else:
                                    descrizione = username.upper()
                                # Salva mapping
                                username_to_tenant[username] = tenant_id
                                username_to_descrizione[username] = descrizione
                                
                                # Conta per chiave (tenant_id, descrizione, data)
                                if descrizione != "DONANT" and descrizione != "DAVIDE GIUDICI":
                                    counts[(tenant_id, descrizione, data_str, client_id_label)] += 1
        except Exception as e:
            print(f"Errore durante la lettura di {file}: {e}")

    # Scrivi il file CSV di output ordinato per Farmacia e Data
    rows = [ (tenant_id, descrizione, data_str, client_id, count) for (tenant_id, descrizione, data_str, client_id), count in counts.items() ]
    # Ordina per Farmacia (descrizione) e Data (convertita in datetime per ordinamento corretto)
    rows.sort(key=lambda x: (x[1], pd.to_datetime(x[2], format='%d/%m/%Y', errors='coerce')))
    with open(output_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Tenant_ID', 'Farmacia', 'Data', 'Client', 'Conteggio'])
        for row in rows:
            csv_writer.writerow(row)
    print(f"Results have been saved to {output_file_path}")
    
if __name__ == "__main__":
    main()