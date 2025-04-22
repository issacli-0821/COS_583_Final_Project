import llvmlite
from llvmlite import binding
import subprocess

from . import python_rep_to_pdp_assembly


# Compiles a C program located at file_path and create a PDP assembly file from it
def compile_to_pdp_assembly(c_file_path: str):
    llvm_path_name = c_to_llvm_ir(c_file_path)
    
    module = llvm_ir_to_python_rep(llvm_path_name)
    pdp_assembly = python_rep_to_pdp_assembly.python_rep_to_pdp_assembly(module)

    pdp_file_path = c_file_path.replace(".c", ".s")

    with open(pdp_file_path, "w") as pdp_file:
        for value in pdp_assembly:
            pdp_file.write(str(value) + "\n")
    
    return pdp_assembly


# Creates an LLVM IR file at the same location as c_file_path
def c_to_llvm_ir(c_file_path: str) -> str:
    llvm_path_name = c_file_path.replace(".c", ".ll")
    
    # Convert to LLVM IR using clang -S -emit-llvm -o <file_name>.ll <file_name>.c
    subprocess.run(["clang", "-S", "-emit-llvm", "-o", llvm_path_name, c_file_path])
    
    return llvm_path_name


# Convert LLVM IR into module in llvmlite
def llvm_ir_to_python_rep(llvm_path_name: str) -> llvmlite.binding.module.ModuleRef:
    with open(llvm_path_name, 'r') as file:
        llvm_ir_data = file.read()

    # Load IR from string
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    module = binding.parse_assembly(llvm_ir_data)
    module.verify()
    
    return module
