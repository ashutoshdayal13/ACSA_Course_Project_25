# memory.py
class Memory:
    def __init__(self, size=1024):
        self.mem = [0] * size

    def load(self, addr: int):
        return self.mem[addr]

    def store(self, addr: int, value: int):
        self.mem[addr] = value

    def __repr__(self):
        # show first few
        return "Memory[" + ", ".join(str(x) for x in self.mem[:16]) + " ...]"
