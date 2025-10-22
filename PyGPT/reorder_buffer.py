# reorder_buffer.py
from typing import Optional, List, Dict

class ROBEntry:
    def __init__(self, tag: int, instr, dest: Optional[str], typ: str):
        self.tag = tag            # unique ROB id
        self.instr = instr        # original instruction
        self.dest = dest          # destination register (None for stores only if store has no reg dest)
        self.typ = typ            # "ALU", "LOAD", "STORE"
        self.ready = False        # true when result is available
        self.value = None         # produced value (for stores this may be the store value; address may be stored separately)
        self.addr = None          # for store / load address computed during execute
        self.committed = False

    def __repr__(self):
        return f"<ROB#{self.tag} {self.instr} dest={self.dest} ready={self.ready} val={self.value}>"

class ReorderBuffer:
    def __init__(self, size: int):
        self.size = size
        self.entries: List[ROBEntry] = []
        self.next_tag = 1

    def is_full(self):
        return len(self.entries) >= self.size

    def allocate(self, instr, dest: Optional[str], typ: str) -> int:
        tag = self.next_tag
        self.next_tag += 1
        entry = ROBEntry(tag, instr, dest, typ)
        self.entries.append(entry)
        return tag

    def get_entry(self, tag: int) -> Optional[ROBEntry]:
        for e in self.entries:
            if e.tag == tag:
                return e
        return None

    def mark_ready(self, tag: int, value=None, addr=None):
        e = self.get_entry(tag)
        if e:
            e.ready = True
            e.value = value
            if addr is not None:
                e.addr = addr

    def peek_head(self) -> Optional[ROBEntry]:
        return self.entries[0] if self.entries else None

    def commit_head(self):
        if not self.entries:
            return None
        head = self.entries[0]
        if head.ready:
            self.entries.pop(0)
            head.committed = True
            return head
        return None

    def __repr__(self):
        return "ROB[" + ", ".join(repr(e) for e in self.entries) + "]"
