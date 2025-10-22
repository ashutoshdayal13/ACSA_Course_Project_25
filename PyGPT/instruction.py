# instruction.py
from typing import Optional

class Instruction:
    """
    Simple instruction representation.
    opcode: string like "ADD", "SUB", "MUL", "DIV", "LD", "ST"
    dest: destination register (for LD/ALU), or None for stores (stores use src2 as value)
    src1, src2: source registers or immediate (for LD store address we use immediate)
    imm: immediate for load/store addresses
    """
    def __init__(self, opcode: str, dest: Optional[str]=None,
                 src1: Optional[str]=None, src2: Optional[str]=None, imm: Optional[int]=None):
        self.opcode = opcode.upper()
        self.dest = dest
        self.src1 = src1
        self.src2 = src2
        self.imm = imm

    def __repr__(self):
        parts = [self.opcode]
        if self.dest: parts.append(self.dest)
        if self.src1: parts.append(self.src1)
        if self.src2: parts.append(self.src2)
        if self.imm is not None: parts.append(f"#{self.imm}")
        return "<" + " ".join(parts) + ">"
