import llvmlite
from enum import Enum

branch_counter = 0
label_counter = 0

# PDP opcodes
class Opcode(Enum):
    MOV = "MOV"
    ADD = "ADD"
    HALT = "HALT"
    RET = "RET"
    RTS = "RTS"
    SUB = "SUB"
    JSR = "JSR"
    BR = "BR"
    BEQ = "BEQ"
    TST = "TST"
    CMP = "CMP"
    BLE = "BLE"
    BGT = "BGT"
    BGE = "BGE"
    BLT = "BLT"
    DIV = "DIV"
    MUL = "MUL"


# PDP registers
class Registers(Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    PC = "PC"
    SP = "SP"


# Useful labels for compilers
class Labels(Enum):
    ICMP_LABEL = "S"
    DONE_WITH_ICMP = "F"
    BRANCH_LABEL = "B"
    LABEL_LABEL = "L"
    MAIN = "main"


class ICMP_Type(Enum):
    SGE = "sge"
    SGT = "sgt"
    SLE = "sle"
    SLT = "slt"


# Useful constants
TOP_OF_STACK = "#40000"
ZERO = "#0"


# Dictionary from identifier to location on the stack
class Environment:
    def __init__(self):
        self.stack_env: dict[str, int] = {}
        self.labels_env: dict[str, str] = {}
        self.next_offset = 2

    def get(self, identifier: str) -> str:
        return oct(self.stack_env[identifier])[2:] + "(SP)"

    def add(self, identifier: str, size: int):
        self.stack_env[identifier] = self.next_offset
        self.next_offset += size

    def remove(self, identifier: str) -> int:
        return self.stack_env.pop(identifier)

    def add_label(self, identifier: str, label_name: str):
        self.labels_env[identifier] = label_name

    def get_label(self, identifier: str) -> str:
        return self.labels_env[identifier]
    
    def has_label(self, identifier: str) -> bool:
        return identifier in self.labels_env
            



# Base class for a single line of assembly code
class LineOfAssembly:
    # Should not be called
    def __init__():
        return


# Assembly labels
class Label(LineOfAssembly):
    def __init__(self, label_name):
        self.label_name = label_name

    def __str__(self):
        return f"{self.opcode.value}:"


# Assembly instructions
class Instruction(LineOfAssembly):
    def __init__(self, opcode: Opcode, operand1: str = None, operand2: str = None):
        self.opcode = opcode
        self.operand1 = operand1
        self.operand2 = operand2

    def __str__(self):
        if self.operand1 is not None and self.operand2 is not None:
            return f"\t{self.opcode.value} {self.operand1}, {self.operand2}"
        elif self.operand1 is not None:
            return f"\t{self.opcode.value} {self.operand1}"
        else:
            return f"\t{self.opcode.value}"


# -----------------------------------------------------------------------
# Functions for compiler
# -----------------------------------------------------------------------


def python_rep_to_pdp_assembly(
    module: llvmlite.binding.module.ModuleRef,
) -> list[LineOfAssembly]:
    # First instruction branches to the main method
    # all_instructions = [Instruction(Opcode.BR, Labels.MAIN.value)]
    all_instructions = []

    for function in module.functions:
        pdp_instructions = translate_function(function)

        # all_instructions.extend(pdp_instructions)

        _, function_name = extract_function_info(str(function))

        if function_name == Labels.MAIN.value:
            # print("pdp: ", pdp_instructions)
            # print("all: ", all_instructions)
            pdp_instructions.extend(all_instructions)
            all_instructions = pdp_instructions
            # print("this:", all_instructions)
        else:
            all_instructions.extend(pdp_instructions)
            # print("that: ", all_instructions)

    return all_instructions


def translate_function(
    function: llvmlite.binding.value.ValueRef,
) -> list[LineOfAssembly]:
    env = Environment()

    params, function_name = extract_function_info(str(function))
    for param in params:
        env.add(param, 2)

    all_instructions = [function_name + ":"]

    # TODO: Setup pc or use .global for main entry point

    # setup sp (choose a good start location)
    if function_name == Labels.MAIN.value:
        set_sp_instruction = Instruction(Opcode.MOV, TOP_OF_STACK, Registers.SP.value)
        all_instructions.append(set_sp_instruction)

    for block in function.blocks:
        pdp_instructions = translate_block(block, env)
        all_instructions.extend(pdp_instructions)

    # halt at the end
    if function_name == Labels.MAIN.value:
        # pop RTS PC instruction if main
        all_instructions.pop()

        halt_instruction = Instruction(Opcode.HALT)
        all_instructions.append(halt_instruction)

    return all_instructions


def translate_block(
    block: llvmlite.binding.value.ValueRef, env: Environment
) -> list[LineOfAssembly]:
    # Adding block label
    block_label = get_block_label(block)
    # print(block_label)
    if ":" in block_label:
        all_instructions = [env.get_label(block_label[:-1]) + ":"]
        block_label = block_label.replace(":", "")
    else:
        all_instructions = []
        block_label = 0

    for instr in block.instructions:
        pdp_instructions = translate_instruction(instr, env)
        all_instructions.extend(pdp_instructions)

    return all_instructions


def translate_instruction(
    instr: llvmlite.binding.value.ValueRef, env: Environment
) -> list[LineOfAssembly]:
    match instr.opcode:
        case "alloca":
            return translate_alloca(instr, env)

        case "add":
            return translate_add(instr, env)
        
        case "sub":
            raise NotImplementedError("Will implement sub")
        
        case "mul":
            return translate_mul(instr, env)
        
        case "sdiv":
            return translate_sdiv(instr, env)

        case "store":
            return translate_store(instr, env)

        case "load":
            return translate_load(instr, env)

        case "ret":
            return translate_ret(instr, env)

        case "call":
            return translate_call(instr, env)

        case "br":
            return translate_branch(instr, env)

        case "icmp":
            return translate_icmp(instr, env)

        case _:
            raise NotImplementedError(f"Instruction {instr.opcode} not supported yet.")


def translate_alloca(instr, env: Environment) -> list[LineOfAssembly]:
    env.add(get_identifier_from_instruction(instr), 2)
    return []


def translate_add(instr, env: Environment) -> list[LineOfAssembly]:
    instruction_identifier = get_identifier_from_instruction(instr)
    env.add(instruction_identifier, 2)

    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    operand_one_identifier = get_identifier_from_instruction(operand_one)
    if operand_one.is_constant:
        instruction_one = Instruction(
            Opcode.ADD, operand_one_identifier, env.get(instruction_identifier)
        )
    else:
        instruction_one = Instruction(
            Opcode.ADD, env.get(operand_one_identifier), env.get(instruction_identifier)
        )

    operand_two_identifier = get_identifier_from_instruction(operand_two)
    if operand_two.is_constant:
        instruction_two = Instruction(
            Opcode.ADD, operand_two_identifier, env.get(instruction_identifier)
        )
    else:
        instruction_two = Instruction(
            Opcode.ADD, env.get(operand_two_identifier), env.get(instruction_identifier)
        )

    clear_instruction = Instruction(Opcode.MOV, "#0", env.get(instruction_identifier))

    return [clear_instruction, instruction_one, instruction_two]


def translate_mul(instr, env: Environment) -> list[LineOfAssembly]:
    instruction_identifier = get_identifier_from_instruction(instr)
    env.add(instruction_identifier, 2)
    
    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    operand_one_identifier = get_identifier_from_instruction(operand_one)
    operand_two_identifier = get_identifier_from_instruction(operand_two)

    if operand_one.is_constant:
        move_multiplicand_instruction = Instruction(Opcode.MOV, operand_one_identifier, Registers.R0.value)
    else:
        move_multiplicand_instruction = Instruction(Opcode.MOV, env.get(operand_one_identifier), Registers.R0.value)
    
    if operand_two.is_constant:
        octal_value = oct(int(operand_two_identifier[1:]))[2:]
        move_constant_instruction = Instruction(Opcode.MOV, f"#{octal_value}", Registers.R1.value)
        multiply_instruction = Instruction(Opcode.MUL, Registers.R1.value, Registers.R0.value)
        move_result_instruction = Instruction(Opcode.MOV, Registers.R1.value, env.get(instruction_identifier))
        return [move_multiplicand_instruction, move_constant_instruction,
                multiply_instruction, move_result_instruction]
    else:
        operand_two_identifier = get_identifier_from_instruction(operand_two)
        multiply_instruction = Instruction(Opcode.MUL, env.get(operand_two_identifier), Registers.R0.value)
        move_result_instruction = Instruction(Opcode.MOV, Registers.R1.value, env.get(instruction_identifier))
        return [move_multiplicand_instruction, multiply_instruction, move_result_instruction]

    


def translate_sdiv(instr, env: Environment) -> list[LineOfAssembly]:

    instruction_identifier = get_identifier_from_instruction(instr)
    env.add(instruction_identifier, 2)

    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    operand_one_identifier = get_identifier_from_instruction(operand_one)
    operand_two_identifier = get_identifier_from_instruction(operand_two)

    move_zero_instruction = Instruction(Opcode.MOV, ZERO, Registers.R0.value)
    if operand_one.is_constant:
        move_dividend_instruction = Instruction(Opcode.MOV, operand_one_identifier, Registers.R1.value)
    else:
        move_dividend_instruction = Instruction(Opcode.MOV, env.get(operand_one_identifier), Registers.R1.value)
    
    if operand_two.is_constant:
        divide_instruction = Instruction(Opcode.DIV, operand_two_identifier, Registers.R0.value)
    else:
        divide_instruction = Instruction(Opcode.DIV, env.get(operand_two_identifier), Registers.R0.value)

    move_result_back_instruction = Instruction(Opcode.MOV, Registers.R0.value,
                                               env.get(instruction_identifier))

    return [move_zero_instruction, move_dividend_instruction,
            divide_instruction, move_result_back_instruction]


def translate_store(instr, env: Environment) -> list[LineOfAssembly]:
    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]

    operand_one_identifier = get_identifier_from_instruction(operand_one)

    operand_two_identifier = get_identifier_from_instruction(operand_two)

    if operand_one.is_constant:
        instruction = Instruction(
            Opcode.MOV, operand_one_identifier, env.get(operand_two_identifier)
        )
    else:
        instruction = Instruction(
            Opcode.MOV, env.get(operand_one_identifier), env.get(operand_two_identifier)
        )

    return [instruction]


def translate_load(instr, env: Environment) -> list[LineOfAssembly]:
    identifier = get_identifier_from_instruction(instr)
    env.add(identifier, 2)

    operands = list(instr.operands)
    operand = operands[0]

    operand_identifier = get_identifier_from_instruction(operand)

    instruction = Instruction(
        Opcode.MOV, env.get(operand_identifier), env.get(identifier)
    )

    return [instruction]


def translate_ret(instr, env: Environment) -> list[LineOfAssembly]:
    operands = list(instr.operands)
    operand = operands[0]

    operand_identifier = get_identifier_from_instruction(operand)

    if operand.is_constant:
        mov_instruction = Instruction(Opcode.MOV, operand_identifier, Registers.R0.value)
    else:
        mov_instruction = Instruction(
            Opcode.MOV, env.get(operand_identifier), Registers.R0.value
        )

    return_instruction = Instruction(Opcode.RTS, Registers.PC.value)

    return [mov_instruction, return_instruction]


def translate_call(instr, env: Environment) -> list[LineOfAssembly]:
    instructions = []

    operands = list(instr.operands)
    # index of next parameter being pushed onto stack
    next_index = env.next_offset + 2

    for i, op in enumerate(operands):
        if i == len(operands) - 1:
            break

        operand_identifier = get_identifier_from_instruction(op)

        store_param_onto_stack = Instruction(
            Opcode.MOV, env.get(operand_identifier), f"{oct(next_index)[2:]}(SP)"
        )
        instructions.append(store_param_onto_stack)
        next_index += 2

    add_SP_instruction = Instruction(
        Opcode.ADD, f"#{oct(env.next_offset + 2)[2:]}", Registers.SP.value
    )
    instructions.append(add_SP_instruction)

    # jump to the function
    function_name = get_function_name_from_instruction(instr)
    JSR_instruction = Instruction(Opcode.JSR, Registers.PC.value, function_name)
    instructions.append(JSR_instruction)

    # return SP to original position so offsets of new environment are accurate
    return_SP_instruction = Instruction(
        Opcode.SUB, f"#{oct(env.next_offset + 2)[2:]}", Registers.SP.value
    )
    instructions.append(return_SP_instruction)

    return_identifier = get_identifier_from_instruction(instr)
    env.add(return_identifier, 2)
    put_return_onto_stack = Instruction(
        Opcode.MOV, Registers.R0.value, env.get(return_identifier)
    )
    instructions.append(put_return_onto_stack)

    return instructions


def translate_branch(instr, env: Environment) -> list[LineOfAssembly]:
    global label_counter
    instr_split = str(instr).split(",")
    # Unconditional branch
    if len(instr_split) < 3:
        (label, ) = get_fields_for_unconditional_branch(instr_split)
        if not env.has_label(label):
            branch_label = get_new_label()
        else:
            branch_label = env.get_label(label)
        branch_instruction = Instruction(Opcode.BR, branch_label)
        env.add_label(label, branch_label)

        return [branch_instruction]
    # Conditional branch
    else:
        argument, if_true_label, if_false_label = get_fields_for_conditional_branch(
            instr_split
        )

        test_instruction = Instruction(Opcode.TST, env.get(argument))
        false_label = get_new_label()
        true_label = get_new_label()
        env.add_label(if_false_label, false_label)
        env.add_label(if_true_label, true_label)
        beq_instruction = Instruction(Opcode.BEQ, false_label)
        br_instruction = Instruction(Opcode.BR, true_label)

        return [test_instruction, beq_instruction, br_instruction]


def translate_icmp(instr, env: Environment) -> list[LineOfAssembly]:
    global branch_counter
    # TODO: add support for multiple icmp, need unique labels?
    instructions = []
    instr_identifier = get_identifier_from_instruction(instr)

    operands = list(instr.operands)
    operand_one = operands[0]
    operand_two = operands[1]
    if len(operands) < 2:
        raise ValueError("Not comparing two operands")
    operand1_identifier = get_identifier_from_instruction(operands[0])
    operand2_identifier = get_identifier_from_instruction(operands[1])

    if not operand_one.is_constant:
        operand1_identifier = env.get(operand1_identifier)

    if not operand_two.is_constant:
        operand2_identifier = env.get(operand2_identifier)

    icmp_type = get_icmp_type_from_instruction(instr)
    match icmp_type:
        case ICMP_Type.SGE.value:
            env.add(instr_identifier, 2)
            compare_instruction = Instruction(
                Opcode.CMP, operand1_identifier, operand2_identifier
            )
            bge_instruction = Instruction(
                Opcode.BGE, get_ICMP_label()
            )
            if_no_branch_set_to_zero = Instruction(
                Opcode.MOV, "#0", env.get(instr_identifier)
            )
            go_to_done_with_branch = Instruction(
                Opcode.BR, get_DONE_WITH_ICMP_label()
            )
            instructions = [
                compare_instruction,
                bge_instruction,
                if_no_branch_set_to_zero,
                go_to_done_with_branch,
            ]

            # if BGE is true
            instructions.append(f"{get_ICMP_label()}:")
            if_branch_set_to_one = Instruction(
                Opcode.MOV, "#1", env.get(instr_identifier)
            )
            instructions.append(if_branch_set_to_one)

            # done with BGE compare
            instructions.append(f"{get_DONE_WITH_ICMP_label()}:")

        case ICMP_Type.SGT.value:
            env.add(instr_identifier, 2)
            compare_instruction = Instruction(
                Opcode.CMP, operand1_identifier, operand2_identifier
            )
            bgt_instruction = Instruction(
                Opcode.BGT, get_ICMP_label()
            )
            if_no_branch_set_to_zero = Instruction(
                Opcode.MOV, "#0", env.get(instr_identifier)
            )
            go_to_done_with_branch = Instruction(
                Opcode.BR, get_DONE_WITH_ICMP_label()
            )
            instructions = [
                compare_instruction,
                bgt_instruction,
                if_no_branch_set_to_zero,
                go_to_done_with_branch,
            ]

            # if BGT is true
            instructions.append(f"{get_ICMP_label()}:")
            if_branch_set_to_one = Instruction(
                Opcode.MOV, "#1", env.get(instr_identifier)
            )
            instructions.append(if_branch_set_to_one)

            # done with BGT compare
            instructions.append(f"{get_DONE_WITH_ICMP_label()}:")

        case ICMP_Type.SLE.value:
            env.add(instr_identifier, 2)
            compare_instruction = Instruction(
                Opcode.CMP, operand1_identifier, operand2_identifier
            )
            ble_instruction = Instruction(
                Opcode.BLE, get_ICMP_label()
            )
            if_no_branch_set_to_zero = Instruction(
                Opcode.MOV, "#0", env.get(instr_identifier)
            )
            go_to_done_with_branch = Instruction(
                Opcode.BR, get_DONE_WITH_ICMP_label()
            )
            instructions = [
                compare_instruction,
                ble_instruction,
                if_no_branch_set_to_zero,
                go_to_done_with_branch,
            ]

            # if BLE is true
            instructions.append(f"{get_ICMP_label()}:")
            if_branch_set_to_one = Instruction(
                Opcode.MOV, "#1", env.get(instr_identifier)
            )
            instructions.append(if_branch_set_to_one)

            # done with BLE compare
            instructions.append(f"{get_DONE_WITH_ICMP_label()}:")

        

        case ICMP_Type.SLT.value:
            env.add(instr_identifier, 2)
            compare_instruction = Instruction(
                Opcode.CMP, operand1_identifier, operand2_identifier
            )
            blt_instruction = Instruction(
                Opcode.BLT, get_ICMP_label()
            )
            if_no_branch_set_to_zero = Instruction(
                Opcode.MOV, "#0", env.get(instr_identifier)
            )
            go_to_done_with_branch = Instruction(
                Opcode.BR, get_DONE_WITH_ICMP_label()
            )
            instructions = [
                compare_instruction,
                blt_instruction,
                if_no_branch_set_to_zero,
                go_to_done_with_branch,
            ]

            # if BLT is true
            instructions.append(f"{get_ICMP_label()}:")
            if_branch_set_to_one = Instruction(
                Opcode.MOV, "#1", env.get(instr_identifier)
            )
            instructions.append(if_branch_set_to_one)

            # done with BLT compare
            instructions.append(f"{get_DONE_WITH_ICMP_label()}:")

        case _:
            raise NotImplementedError(f"Icmp type {icmp_type} not supported yet.")

    branch_counter += 1

    return instructions


# -----------------------------------------------------------------------
# Helper functions for parsing
# -----------------------------------------------------------------------


# Takes in function_string and extracts info associated with it
def extract_function_info(function_string):
    params = []

    lines = function_string.split("\n")

    for line in lines:
        if line.strip().startswith("define"):
            start_parenthesis_index = line.find("(")
            end_parenthesis_index = line.find(")")

            arg_str = line[start_parenthesis_index + 1 : end_parenthesis_index].strip()

            args = arg_str.split(",")
            for arg in args:
                parts = arg.split()
                if len(parts) >= 2 and parts[2].startswith("%"):
                    params.append(parts[2])

            at_index = line.find("@")
            function_name = line[at_index + 1 : start_parenthesis_index]

    return params, function_name


# Prints string representation of module
def print_module(module: llvmlite.binding.module.ModuleRef):
    for func in module.functions:
        print("Function:", func.value)
        for block in func.blocks:
            print(" Block:", block.value)
            for instr in block.instructions:
                print("  Instr:", instr.opcode)
                for op in instr.operands:
                    print("    Operand:", op)


def get_identifier_from_instruction(instr) -> str:
    str_instr = str(instr).lstrip()

    if instr.is_constant:
        identifier = str_instr[str_instr.index(" ") :].lstrip()

        return f"#{identifier}"
    else:
        if "=" in str_instr:
            identifier = str_instr[: str_instr.index(" ")]
        else:
            identifier = str_instr[str_instr.index(" ") :].lstrip()

        return identifier


def get_identifier_from_operand_with_type(operand) -> str:
    str_instr = str(operand).lstrip()
    identifier = str_instr[str_instr.index(" ") :]

    return identifier.lstrip()


def get_function_name_from_instruction(instr) -> str:
    str_instr = str(instr)

    at_index = str_instr.find("@")
    start_parenthesis_index = str_instr.find("(")

    return str_instr[at_index + 1 : start_parenthesis_index]


def get_icmp_type_from_instruction(instr) -> str:
    str_instr = str(instr).split(" ")

    icmp_index = str_instr.index("icmp")

    return str_instr[icmp_index + 1]


def get_block_label(block) -> str:
    label = str(block).lstrip().split("\n")[0]
    colon_index = label.find(":")
    return label[: colon_index + 1]


def get_fields_for_conditional_branch(instr_split: list[str]):
    argument = instr_split[0].lstrip().split(" ")[2]
    if_true_label = instr_split[1].lstrip().split(" ")[1].replace("%", "")
    if_false_label = instr_split[2].lstrip().split(" ")[1].replace("%", "")

    return (argument, if_true_label, if_false_label)


def get_fields_for_unconditional_branch(instr_split: list[str]):
    return (instr_split[0].lstrip().split(" ")[2].replace("%", ""),)


def add_label_suffix(label):
    return f"{Labels.BRANCH_LABEL.value}{label}"


def get_ICMP_label():
    return f"{Labels.ICMP_LABEL.value}{branch_counter}"


def get_DONE_WITH_ICMP_label():
    return f"{Labels.DONE_WITH_ICMP.value}{branch_counter}"


def get_new_label():
    global label_counter 
    result = f"{Labels.LABEL_LABEL.value}{label_counter}"
    label_counter += 1
    return result