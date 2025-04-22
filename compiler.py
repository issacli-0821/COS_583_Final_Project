import argparse

from compiler.compile_to_pdp import compile_to_pdp_assembly

# Usage: python3 compiler.py example_c_files/fib.c
def main():

    parser = argparse.ArgumentParser(
        description = "Compile C program into PDP program")
    parser.add_argument("file_path",
                        help="Name of the C file")
    args = parser.parse_args()
    file_path = args.file_path

    compile_to_pdp_assembly(file_path)
    return

if __name__ == "__main__":
    main()