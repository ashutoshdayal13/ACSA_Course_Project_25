# main.py
from instruction import Instruction
from tomasulo import Tomasulo

def sample_program():
    # memory initial values
    # LD R1, #10  ; R1 = mem[10]
    # LD R2, #11  ; R2 = mem[11]
    # ADD R3, R1, R2
    # MUL R4, R3, R1
    # SUB R5, R4, R2
    # ST R5, #12  ; mem[12] = R5
    prog = [
        Instruction("LD", dest="R1", src1=None, imm=10),
        Instruction("LD", dest="R2", src1=None, imm=11),
        Instruction("ADD", dest="R3", src1="R1", src2="R2"),
        Instruction("MUL", dest="R4", src1="R3", src2="R1"),
        Instruction("SUB", dest="R5", src1="R4", src2="R2"),
        Instruction("ST", dest=None, src1=None, src2="R5", imm=12),
    ]
    return prog

def main():
    prog = sample_program()
    sim = Tomasulo(prog, reg_count=16, rob_size=8)
    # initialize memory values
    sim.memory.store(10, 5)
    sim.memory.store(11, 7)
    print("Starting simulation...")
    sim.run(max_cycles=100, verbose=True)
    print("Final registers (R0..R7):")
    for i in range(8):
        print(f"R{i} = {sim.rf.read(f'R{i}')}")
    print("Memory[12] =", sim.memory.load(12))

if __name__ == "__main__":
    main()
