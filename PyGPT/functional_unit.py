# functional_unit.py
from typing import Dict, List

class FunctionalUnit:
    def __init__(self, name: str, latency: int, count: int = 1):
        self.name = name
        self.latency = latency
        # simple pool: each slot can run one RS entry
        self.slots = [None] * count  # each slot stores (rs_entry)

    def can_accept(self):
        return any(slot is None for slot in self.slots)

    def assign(self, rs_entry, cycles):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = (rs_entry, cycles)
                return True
        return False

    def step(self):
        """Advance one cycle. Return list of finished RS entries."""
        finished = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                rs_entry, cycles_left = slot
                cycles_left -= 1
                if cycles_left <= 0:
                    finished.append(rs_entry)
                    self.slots[i] = None
                else:
                    self.slots[i] = (rs_entry, cycles_left)
        return finished

    def __repr__(self):
        return f"<FU {self.name} latency={self.latency} slots={self.slots}>"
