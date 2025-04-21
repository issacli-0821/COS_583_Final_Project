import llvmlite
import re



# Dictionary from identifier to location on the stack
class Environment:
    def __init__(self):
        self.env : dict[str, int] = {}
        self.nextOffset = 0
    
    def get(self, identifier: str) -> int:
        return self.env[identifier]
    
    def add(self, identifier: str, size: int):
        self.env[identifier] = self.nextOffset
        self.nextOffset += size
    
    def remove(self, identifier: str) -> int:
        return self.env.pop(identifier)


"""
define dso_local i32 @add(i32 noundef %0, i32 noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %0, i32* %3, align 4
  store i32 %1, i32* %4, align 4
  %5 = load i32, i32* %3, align 4
  %6 = load i32, i32* %4, align 4
  %7 = add nsw i32 %5, %6
  ret i32 %7
}
"""

def print_module(module: llvmlite.binding.module.ModuleRef):
    for func in module.functions:
        print("Function:", func.name)
        for block in func.blocks:
            print(" Block:", block.name)
            for instr in block.instructions:
                print("  Instr:", instr.opcode)
                for op in instr.operands:
                    print("    Operand:", op)
    return


def python_rep_to_pdp_assembly(module: llvmlite.binding.module.ModuleRef) -> list[str]:
    all_instructions = []
    # print_module(module)
    for function in module.functions:
        pdp_instructions = translate_function(function)
        all_instructions.extend(pdp_instructions)
    
    return all_instructions
    

def translate_function(function: llvmlite.binding.value.ValueRef) -> list[str]:
    env = Environment()
    # Populate env with function inputs?

    all_instructions = []
    for block in function.blocks:
        pdp_instructions = translate_block(block, env)
        all_instructions.extend(pdp_instructions)
    
    return all_instructions


def translate_block(block: llvmlite.binding.value.ValueRef, env: Environment) -> list[str]:
    all_instructions = []

    for instr in block.instructions:
        pdp_instructions = translate_instruction(instr, env)
        all_instructions.extend(pdp_instructions)

    return all_instructions

def translate_instruction(instr: llvmlite.binding.value.ValueRef, env: Environment) -> list[str]:

    print(instr)
    print("type: ", instr.type)
    print("opcode: ", instr.opcode)
    for op in instr.operands:
        print("Operand: ", op)
    print()

    match instr.opcode:
        case "alloca":
            return translate_alloca(instr, env)

        case "add":
            return translate_add(instr, env)
        
        case "store":
            return translate_store(instr, env)
            
        case "load":
            return translate_load(instr, env)
        
        case "ret":
            return translate_ret(instr, env)
        
        case _:
            raise NotImplementedError(f"Instruction {instr.opcode} not supported yet.")
  

def translate_alloca(instr, env: Environment) -> list[str]:

    # from pprint import pprint
    # print(dir(instr))
    print("Name here---%s---" % (instr.name))
    # env.add()

    # print(instr.name)

    return []  


"""
instr format: add [flags] <type> <op1>, <op2>
"""
def translate_add(instr, env: Environment) -> list[str]:
    for op in instr.operands:
       add_op = str(op.name)
       

    
    
    

    

    
    return []


def translate_store(instr, env: Environment) -> list[str]:
    return []



"""
  %5 = load i32, i32* %3, align 4
type:  i32
opcode:  load
Operand:    %3 = alloca i32, align 4
"""
def translate_load(instr, env: Environment) -> list[str]:
    operands = instr.operands
    for op in operands:
        print("Operand in load: ", op.name)
        print(type(op.name))
    
        
    return []


def translate_ret(instr, env: Environment) -> list[str]:
    return []
