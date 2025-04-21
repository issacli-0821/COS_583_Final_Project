import llvmlite
from enum import Enum

# Dictionary from identifier to location on the stack
class Environment:
    def __init__(self):
        self.env : dict[str, int] = {"%0": 0, "%1": 2}
        self.next_offset = 4
    
    def get(self, identifier: str) -> str:
        return str(self.env[identifier]) + "(SP)"
    
    def add(self, identifier: str, size: int):
        print(f"Added {identifier} to {self.next_offset}")
        self.env[identifier] = self.next_offset
        self.next_offset += size

    # TODO?
    def update(self, identifier: str):
        return
    
    def remove(self, identifier: str) -> int:
        return self.env.pop(identifier)


# Enum to represent PDP opcodes
class Opcode(Enum):
    MOV = "MOV"
    ADD = "ADD"
    RET = "RET"
    RTS = "RTS"

class Registers(Enum):
    R0 = "R0"
    PC = "PC"
    SP = "SP"

class Instruction:
    def __init__(self, opcode: Opcode, operand1: str, operand2: str = None):
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2
    
    def __str__(self):
        if self.operand2 is not None:
            return f"{self.opcode.name} {self.operand1}, {self.operand2}"
        else:
            return f"{self.opcode.name} {self.operand1}"
    


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


def python_rep_to_pdp_assembly(module: llvmlite.binding.module.ModuleRef) -> list[Instruction]:
    all_instructions = []
    # print_module(module)
    for function in module.functions:
        pdp_instructions = translate_function(function)
        all_instructions.extend(pdp_instructions)
    
    return all_instructions
    

def translate_function(function: llvmlite.binding.value.ValueRef) -> list[Instruction]:
    env = Environment()
    # Populate env with function inputs?

    all_instructions = []
    for block in function.blocks:
        pdp_instructions = translate_block(block, env)
        all_instructions.extend(pdp_instructions)
    
    return all_instructions


def translate_block(block: llvmlite.binding.value.ValueRef, env: Environment) -> list[Instruction]:
    all_instructions = []

    for instr in block.instructions:
        pdp_instructions = translate_instruction(instr, env)
        all_instructions.extend(pdp_instructions)

    return all_instructions


def translate_instruction(instr: llvmlite.binding.value.ValueRef, env: Environment) -> list[Instruction]:

    # print(instr)
    # print("type: ", instr.type)
    # print("opcode: ", instr.opcode)
    # for op in instr.operands:
    #     print("Operand: ", op)
    # print()

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


def get_identifier_from_instruction(instr) -> str:

    str_instr = str(instr).lstrip()
    identifier = str_instr[:str_instr.index(" ")]

    return identifier

def get_identifier_from_operand_with_type(operand) -> str:
    str_instr = str(operand).lstrip()
    identifier = str_instr[str_instr.index(" "):]

    return identifier.lstrip()


def translate_alloca(instr, env: Environment) -> list[Instruction]:

    env.add(get_identifier_from_instruction(instr), 2)
    return []


"""
instr format: add [flags] <type> <op1>, <op2>
"""
def translate_add(instr, env: Environment) -> list[Instruction]:
    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    instruction_identifier = get_identifier_from_instruction(instr)
    env.add(instruction_identifier, 2)

    operand_one_identifier = get_identifier_from_instruction(operand_one)
    instruction_one = Instruction(Opcode.ADD,
                                  env.get(operand_one_identifier), env.get(instruction_identifier))

    operand_two_identifier = get_identifier_from_instruction(operand_two)
    instruction_two = Instruction(Opcode.ADD,
                                  env.get(operand_two_identifier), env.get(instruction_identifier))

    
    return [instruction_one, instruction_two]


def translate_store(instr, env: Environment) -> list[Instruction]:
    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    operand_one_identifier = get_identifier_from_operand_with_type(operand_one)

    operand_two_identifier = get_identifier_from_instruction(operand_two)
    
    instruction = Instruction(Opcode.MOV, env.get(operand_one_identifier), env.get(operand_two_identifier))
    return [instruction]



"""
%5 = load i32, i32* %3, align 4
type:  i32
opcode:  load
Operand:    %3 = alloca i32, align 4
"""
def translate_load(instr, env: Environment) -> list[Instruction]:
    operands = list(instr.operands)
    operand = operands[0]

    identifier = get_identifier_from_instruction(instr)

    operand_identifier = get_identifier_from_instruction(operand)
    
    env.add(identifier, 2)
    instruction = Instruction(Opcode.MOV, env.get(operand_identifier), env.get(identifier))

    return [instruction]


def translate_ret(instr, env: Environment) -> list[Instruction]:
    operands = list(instr.operands)
    operand = operands[0]

    operand_identifier = get_identifier_from_instruction(operand)
    mov_instruction = Instruction(Opcode.MOV, env.get(operand_identifier), Registers.R0.name)
    return_instruction = Instruction(Opcode.RTS, Registers.PC.name)
    
    return [mov_instruction, return_instruction]