#!/usr/bin/env zsh

set -e

# ---- Get directory ----
DIR="${1:-}"

if [[ -z "$DIR" ]]; then
    read "DIR?Enter directory containing HEIC files: "
fi

DIR="${~DIR}"

if [[ ! -d "$DIR" ]]; then
    echo "Directory not found: $DIR"
    exit 1
fi

# ---- Find files ----
files=("$DIR"/*.HEIC(N) "$DIR"/*.heic(N))

if (( ${#files} == 0 )); then
    echo "No HEIC files found."
    exit 0
fi

# ---- Convert ----
for file in "${files[@]}"; do
    output="${file:r}.jpg"

    echo "Converting: $(basename "$file")"
    sips -s format jpeg "$file" --out "$output" >/dev/null
done

echo
echo "Conversion complete"
