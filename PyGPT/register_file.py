# register_file.py
from typing import Dict, Optional

class RegisterFile:
    def __init__(self, num_regs=32):
        self.num_regs = num_regs
        self.regs: Dict[str, int] = {f"R{i}": 0 for i in range(num_regs)}
        # reg_status maps reg -> ROB tag (or None if value is ready)
        self.reg_status: Dict[str, Optional[int]] = {f"R{i}": None for i in range(num_regs)}

    def read(self, reg: str):
        return self.regs[reg]

    def write(self, reg: str, value: int):
        self.regs[reg] = value

    def set_status(self, reg: str, rob_tag: Optional[int]):
        self.reg_status[reg] = rob_tag

    def get_status(self, reg: str) -> Optional[int]:
        return self.reg_status[reg]

    def __repr__(self):
        reg_vals = ", ".join(f"{r}:{v}" for r,v in list(self.regs.items())[:8]) + " ..."
        return f"<RegisterFile {reg_vals}>"
