# Run with assembly file as an argument

# Get the absolute path of the assembly file from the first argument
PDP_ASSEMBLY_FILE="$(realpath $1)"

PARENT_PATH=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$PARENT_PATH"

# Make macro11
cd macro11/
make -s
cd ..

# Create output directory if it doesn't exist
mkdir -p output

# Extract the base filename without directory and extension
BASE_NAME="$(basename "$PDP_ASSEMBLY_FILE" .s)"

# Set output file paths
OBJECT_FILE="output/${BASE_NAME}.obj"
BINARY_FILE="output/${BASE_NAME}.bin"

# Assemble the source file into an object file
./macro11/macro11 "$PDP_ASSEMBLY_FILE" -o "$OBJECT_FILE"

# Convert the object file to a binary
./obj2bin/obj2bin.pl --binary --rt11 --outfile="$BINARY_FILE" "$OBJECT_FILE"