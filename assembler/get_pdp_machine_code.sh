# Run with assembly file as an argument. The assembly file can be a path.

# Get the input file from the first argument
PDP_ASSEMBLY_FILE="$1"

# Create output directory if it doesn't exist
mkdir -p output

# Extract the base filename without directory and extension
BASE_NAME="$(basename "$PDP_ASSEMBLY_FILE" .asm)"

# Set output file paths
OBJECT_FILE="output/${BASE_NAME}.obj"
BINARY_FILE="output/${BASE_NAME}.bin"

# Assemble the source file into an object file
./bin/macro11 "$PDP_ASSEMBLY_FILE" -o "$OBJECT_FILE"

# Convert the object file to a binary
./bin/obj2bin.pl --binary --rt11 --outfile="$BINARY_FILE" "$OBJECT_FILE"

echo "Assembled successfully!"