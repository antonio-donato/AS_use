import base64
import json
import csv
from collections import Counter
import re
import os
import glob

# Percorso del file CSV da cui leggere
output_file_path = "./output/username_counts_new.csv"
output_jwt_folder = "./output_jwt"

# Crea la cartella output_jwt se non esiste
os.makedirs(output_jwt_folder, exist_ok=True)

def decode_base64_url(encoded_str):
    """Converte base64url in base64 standard e decodifica"""
    padding = len(encoded_str) % 4
    if padding == 2:
        encoded_str += '=='
    elif padding == 3:
        encoded_str += '='

    encoded_str = encoded_str.replace('-', '+').replace('_', '/')

    try:
        return base64.b64decode(encoded_str)
    except Exception as e:
        print(f"Errore nella decodifica: {e}")
        return None

def decode_jwt(token, part=2):
    """
    Decodifica un JWT e restituisce la parte specificata (header=1, payload=2, signature=3)
    """
    try:
        parts = token.strip().split('.')
        if len(parts) < 3:
            return None

        decoded = decode_base64_url(parts[part - 1])
        if not decoded:
            return None

        json_data = json.loads(decoded)
        return json_data
    except Exception as e:
        print(f"Errore nel parsing del JWT: {e}")
        return None

def main():
    input_folder = "./input"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    if not csv_files:
        print(f"Nessun file CSV trovato nella cartella {input_folder}")
        return

    input_file = csv_files[0]
    print(f"File selezionato: {input_file}")

    token_pattern = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")
    found_tokens = set()

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            matches = token_pattern.findall(line)
            found_tokens.update(matches)

    username_counts = Counter()
    client_counts = Counter()
    line_number = 0

    try:
        for token in found_tokens:
            line_number += 1
            line = token.strip()

            if not line:
                continue

            if line_number % 100 == 0:
                print(f"Processing token number: {line_number}")

            payload = decode_jwt(line, part=2)
            username = payload.get("user_name") if payload else None
            client_id = payload.get("client_id") if payload else None

            if username and username != "null":
                username_counts[username] += 1

            if client_id and client_id != "null":
                client_counts[client_id] += 1

            # Salva il payload in un file JSON
            if payload:
                output_file = os.path.join(output_jwt_folder, f"jwt_{line_number}.json")
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(payload, json_file, indent=4, ensure_ascii=False)

        print(f"Finished processing {line_number} tokens")

        total_count = sum(username_counts.values())

        with open(output_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Username', 'Count'])

            for username, count in username_counts.most_common():
                csv_writer.writerow([username, count])

            csv_writer.writerow(['TOTAL', total_count])

        print(f"Results have been saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
