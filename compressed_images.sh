#!/bin/bash

cd data/processed/dataset/images/test || exit 1
shopt -s nullglob

OUTPUT_DIR="compressed_images"

mkdir -p "$OUTPUT_DIR"

files=( *.jpg *.png )
total=${#files[@]}

i=1
for f in "${files[@]}"; do
    echo "$i/$total - $f"
    convert "$f" -quality 80 "$OUTPUT_DIR/${f%.*}.webp"
    ((i++))
done