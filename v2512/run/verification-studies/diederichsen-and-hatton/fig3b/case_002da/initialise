#!/bin/bash

# Takes the inputfile "overview" and generates the complete case based on a template case

set -e  # Exit on error

template="../../template"
overview="overview"
case_dir="."

# Check if overview file exists
if [ ! -f "$overview" ]; then
    echo "Error: Overview file '$overview' not found!"
    exit 1
fi

# Check if template directory exists
if [ ! -d "$template" ]; then
    echo "Error: Template directory '$template' not found!"
    exit 1
fi

# Create an associative array to store parameters
declare -A params

# Read the overview file and populate the associative array
while IFS=' ' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    params["$key"]="$value"
    echo "Read parameter: $key = $value"
done < "$overview"

# Copy template contents to current directory
echo "Copying template files to current directory..."
cp -r "$template"/* .

# Function to replace placeholders in a file
replace_placeholders() {
    local file="$1"
    local temp_file="${file}.tmp"
    
    cp "$file" "$temp_file"
    
    # Replace each parameter placeholder
    for key in "${!params[@]}"; do
        sed -i "s/{${key}}/${params[$key]}/g" "$temp_file"
    done
    
    mv "$temp_file" "$file"
}

# Find all files in the current directory and replace placeholders
echo "Replacing placeholders in template files..."
while IFS= read -r -d '' file; do
    # Skip initialise.sh and overview files
    basename_file=$(basename "$file")
    if [[ "$basename_file" == "initialise.sh" || "$basename_file" == "overview" ]]; then
        continue
    fi
    
    # Skip binary files
    if [ -f "$file" ] && file "$file" | grep -q text; then
        echo "Processing: $file"
        replace_placeholders "$file"
    fi
done < <(find . -type f -print0)

echo ""
echo "Case generation complete!"
echo "Parameters used:"
for key in "${!params[@]}"; do
    echo "  $key = ${params[$key]}"
done