#!/bin/bash
decode_base64_url() {
  local len=$((${#1} % 4))
  local result="$1"
  if [ $len -eq 2 ]; then result="$1"'=='
  elif [ $len -eq 3 ]; then result="$1"'='
  fi
  echo "$result" | tr '_-' '/+' | base64 -d
}

decode_jwt(){
   decode_base64_url $(echo -n $2 | cut -d "." -f $1) | jq -r .$3
}

# Decode JWT header
alias jwth="decode_jwt 1"

# Decode JWT Payload
alias jwtp="decode_jwt 2"

alias docker-bash='db'
alias docker-logs='dl'
alias j='jwtp'

# File path
file_path=".\extracted_tokens.txt"

# Loop through each line of the file and decode the base64 content
declare -A username_counts
line_number=0
while IFS= read -r line; do
    ((line_number++))
    # Skip empty lines
    if [[ -z "$line" ]]; then
        continue
    fi

    # For debugging
    if ((line_number % 100 == 0)); then
        echo "Processing line number: $line_number"
    fi

    # Decode the line using base64 and get username
    username=$(decode_jwt 2 "$line" user_name)

    # Only count non-empty usernames
    if [[ -n "$username" && "$username" != "null" ]]; then
        username_counts["$username"]=$((username_counts["$username"] + 1))
    fi
done < "$file_path"

echo "Finished processing $line_number lines"

# Calculate total count separately
total_count=0
for count in "${username_counts[@]}"; do
    total_count=$((total_count + count))
done

# Print counts of unique usernames sorted by their count
echo "Username counts:"
for user in "${!username_counts[@]}"; do
    echo "$user: ${username_counts[$user]}"
done | sort -k2 -rn

# Print the sum of username_counts values
echo "Total username count: $total_count"
