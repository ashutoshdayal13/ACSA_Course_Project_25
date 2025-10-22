# reservation_station.py
from typing import Optional, List, Dict

class RSEntry:
    def __init__(self, name: str):
        self.name = name
        self.busy = False
        self.op = None           # opcode
        self.Vj = None
        self.Vk = None
        self.Qj = None          # ROB tag producing Vj (or None)
        self.Qk = None          # ROB tag producing Vk (or None)
        self.dest = None        # ROB tag where result should go
        self.instr = None
        self.exec_cycles_left = None

    def is_ready(self):
        return (self.busy and self.Qj is None and self.Qk is None and self.exec_cycles_left is None)

    def clear(self):
        self.__init__(self.name)

    def __repr__(self):
        return f"<RS {self.name} op={self.op} busy={self.busy} Vj={self.Vj} Vk={self.Vk} Qj={self.Qj} Qk={self.Qk} dest=ROB{self.dest} exec_left={self.exec_cycles_left}>"

class ReservationStation:
    def __init__(self, name_prefix: str, n: int):
        self.entries: List[RSEntry] = [RSEntry(f"{name_prefix}{i}") for i in range(n)]

    def find_free(self) -> Optional[RSEntry]:
        for e in self.entries:
            if not e.busy:
                return e
        return None

    def busy_count(self):
        return sum(1 for e in self.entries if e.busy)

    def __iter__(self):
        return iter(self.entries)

    def __repr__(self):
        return "RS[" + ", ".join(repr(e) for e in self.entries) + "]"
