import base64
import json
import csv
from collections import Counter

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
    input_file_path = "./extracted_tokens.txt"
    output_file_path = "./username_counts.csv"
    username_counts = Counter()
    line_number = 0
    
    try:
        # Elaborazione del file di input
        with open(input_file_path, 'r') as file:
            for line in file:
                line_number += 1
                line = line.strip()
                
                # Salta le righe vuote
                if not line:
                    continue
                
                # Stampa messaggi di debug ogni 100 righe
                if line_number % 100 == 0:
                    print(f"Processing line number: {line_number}")
                
                # Estrai il nome utente dal payload del JWT
                username = decode_jwt(line, part=2, field="user_name")
                
                # Conta solo i nomi utente non vuoti
                if username and username != "null":
                    username_counts[username] += 1
        
        print(f"Finished processing {line_number} lines")
        
        # Calcola il conteggio totale
        total_count = sum(username_counts.values())
        
        # Genera il file CSV
        with open(output_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Intestazione
            csv_writer.writerow(['Username', 'Count'])
            
            # Dati ordinati per conteggio decrescente
            for username, count in username_counts.most_common():
                csv_writer.writerow([username, count])
            
            # Aggiungi il totale come ultima riga
            csv_writer.writerow(['TOTAL', total_count])
        
        print(f"Results have been saved to {output_file_path}")
    
    except FileNotFoundError:
        print(f"File not found: {input_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()