import argparse

from compiler.compile_to_pdp import compile_to_pdp_assembly, llvm_ir_to_python_rep
from compiler.python_rep_to_pdp_assembly import python_rep_to_pdp_assembly

def main():

    llvm_path_name = "example_c_and_ll_files/simple.ll"

    module = llvm_ir_to_python_rep(llvm_path_name)
    # print(module)
    pdp_assembly = python_rep_to_pdp_assembly(module)
    print(pdp_assembly)
    return




    parser = argparse.ArgumentParser(
        description = "Compile C program into PDP program")
    parser.add_argument("file_path",
                        help="Name of the C file")
    args = parser.parse_args()
    file_path = args.file_path

    compile_to_pdp_assembly(file_path)
    return

"""
python3 compiler.py example_c_and_ll_files/addFive.c
"""
if __name__ == "__main__":
    main()