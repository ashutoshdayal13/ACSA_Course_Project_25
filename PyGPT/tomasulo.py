# tomasulo.py
from instruction import Instruction
from register_file import RegisterFile
from reservation_station import ReservationStation, RSEntry
from reorder_buffer import ReorderBuffer
from functional_unit import FunctionalUnit
from memory import Memory

# Fix imports (we used module filenames)
# If you put files together in same package directory, use relative import style or run from that folder.

# For simplicity in this single-file example, I'll re-import classes directly:
from reservation_station import ReservationStation, RSEntry
from reorder_buffer import ReorderBuffer
from functional_unit import FunctionalUnit
from register_file import RegisterFile
from memory import Memory

class Tomasulo:
    def __init__(self, program, reg_count=32, rob_size=16):
        self.program = program[:]  # list of Instruction
        self.pc = 0
        self.cycle = 0
        self.rf = RegisterFile(reg_count)
        self.rob = ReorderBuffer(rob_size)
        # reservation stations for ALU (add), MUL, LOAD/STORE
        self.rs_add = ReservationStation("A", 4)
        self.rs_mul = ReservationStation("M", 2)
        self.rs_ldst = ReservationStation("L", 4)
        # functional units
        self.fu_add = FunctionalUnit("ALU", latency=1, count=2)
        self.fu_mul = FunctionalUnit("MUL", latency=3, count=1)
        self.fu_ld = FunctionalUnit("LD", latency=2, count=1)  # load/store address computation and mem access combined
        self.memory = Memory(256)
        self.completed_instructions = 0

    def issue(self):
        if self.pc >= len(self.program):
            return
        instr = self.program[self.pc]
        if self.rob.is_full():
            return  # stall: no ROB space
        # choose RS and type
        if instr.opcode in ("ADD", "SUB"):
            rs = self.rs_add.find_free()
            typ = "ALU"
            fu = self.fu_add
        elif instr.opcode in ("MUL", "DIV"):
            rs = self.rs_mul.find_free()
            typ = "MUL"
            fu = self.fu_mul
        elif instr.opcode in ("LD", "ST"):
            rs = self.rs_ldst.find_free()
            typ = "LOAD" if instr.opcode == "LD" else "STORE"
            fu = self.fu_ld
        else:
            # unknown op - treat as NOP and advance pc
            self.pc += 1
            return

        if rs is None:
            return  # no RS free -> stall

        # allocate ROB entry
        dest = instr.dest if instr.opcode != "ST" else None
        rob_tag = self.rob.allocate(instr, dest, typ)
        # fill RS entry
        rs.busy = True
        rs.op = instr.opcode
        rs.dest = rob_tag
        rs.instr = instr

        # sources: set V or Q depending on register status (rob mapping)
        def prepare_src(rs_entry, src_reg, field):
            if src_reg is None:
                setattr(rs_entry, field, None)
                return
            tag = self.rf.get_status(src_reg)
            if tag is None:
                # value ready
                setattr(rs_entry, "V" + field[-1], self.rf.read(src_reg))
                setattr(rs_entry, "Q" + field[-1], None)
            else:
                setattr(rs_entry, "Q" + field[-1], tag)
                setattr(rs_entry, "V" + field[-1], None)

        # For LD: imm is address; for ST: src1 may be address base, src2 may be value
        if instr.opcode == "LD":
            # we will compute address in execute; treat src1 as base reg optionally
            if instr.src1:
                prepare_src(rs, instr.src1, "Vj")
            else:
                rs.Vj = instr.imm
                rs.Qj = None
            rs.Qk = None
            rs.Vk = None
        elif instr.opcode == "ST":
            # store: src1 = base (address), src2 = value register
            if instr.src1:
                prepare_src(rs, instr.src1, "Vj")
            else:
                rs.Vj = instr.imm
                rs.Qj = None
            if instr.src2:
                prepare_src(rs, instr.src2, "Vk")
            else:
                rs.Vk = instr.imm
                rs.Qk = None
        else:
            # ALU ops: src1, src2 are registers (or imm)
            prepare_src(rs, instr.src1, "Vj")
            prepare_src(rs, instr.src2, "Vk")

        # update register status for destination (register will be written at commit from ROB)
        if instr.dest:
            self.rf.set_status(instr.dest, rob_tag)

        self.pc += 1

    def start_execution(self):
        # scan RS entries and dispatch to FUs if ready and FU available
        for rs in self.rs_add:
            if rs.busy and rs.is_ready() and self.fu_add.can_accept():
                rs.exec_cycles_left = self.fu_add.latency
                self.fu_add.assign(rs, self.fu_add.latency)
        for rs in self.rs_mul:
            if rs.busy and rs.is_ready() and self.fu_mul.can_accept():
                rs.exec_cycles_left = self.fu_mul.latency
                self.fu_mul.assign(rs, self.fu_mul.latency)
        for rs in self.rs_ldst:
            # loads/stores: need address ready (Vj or Qj resolved)
            # treat as ready if Qj and (for store) Qk resolved too
            for rs_e in self.rs_ldst.entries:
                if rs_e.busy and rs_e.is_ready() and self.fu_ld.can_accept():
                    # for loads/stores we expect address in Vj (or immediate)
                    rs_e.exec_cycles_left = self.fu_ld.latency
                    self.fu_ld.assign(rs_e, self.fu_ld.latency)

    def step_functional_units(self):
        # advance FUs; collect finished RS entries
        finished = []
        finished += self.fu_add.step()
        finished += self.fu_mul.step()
        finished += self.fu_ld.step()
        return finished

    def produce_result(self, rs_entry):
        instr = rs_entry.instr
        # compute result depending on opcode
        def val(v):
            return v
        result = None
        addr = None
        if instr.opcode == "ADD":
            result = rs_entry.Vj + rs_entry.Vk
        elif instr.opcode == "SUB":
            result = rs_entry.Vj - rs_entry.Vk
        elif instr.opcode == "MUL":
            result = rs_entry.Vj * rs_entry.Vk
        elif instr.opcode == "DIV":
            result = rs_entry.Vj // rs_entry.Vk if rs_entry.Vk != 0 else 0
        elif instr.opcode == "LD":
            # address = base + imm (if imm present)
            base = rs_entry.Vj if rs_entry.Vj is not None else 0
            addr = base + (instr.imm or 0)
            # perform actual memory read now and put into ROB as value
            result = self.memory.load(addr)
        elif instr.opcode == "ST":
            # compute address and store value at commit. or compute now and put in ROB.
            base = rs_entry.Vj if rs_entry.Vj is not None else 0
            addr = base + (instr.imm or 0)
            result = rs_entry.Vk  # value to be stored
        # write to ROB and broadcast
        self.rob.mark_ready(rs_entry.dest, value=result, addr=addr)
        # broadcast to RS: update any Qj/Qk waiting for this ROB tag
        for rscol in (self.rs_add, self.rs_mul, self.rs_ldst):
            for e in rscol:
                if e.busy:
                    if e.Qj == rs_entry.dest:
                        e.Vj = result
                        e.Qj = None
                    if e.Qk == rs_entry.dest:
                        e.Vk = result
                        e.Qk = None
        # free this RS entry
        rs_entry.clear()

    def commit(self):
        head = self.rob.peek_head()
        if head and head.ready:
            committed = self.rob.commit_head()
            if committed.typ == "ALU" or committed.typ == "LOAD":
                # write to register file
                if committed.dest:
                    # only commit if the register still maps to this ROB tag
                    if self.rf.get_status(committed.dest) == committed.tag:
                        self.rf.write(committed.dest, committed.value)
                        self.rf.set_status(committed.dest, None)
            elif committed.typ == "STORE":
                # actually write to memory
                self.memory.store(committed.addr, committed.value)
            self.completed_instructions += 1

    def run_cycle(self, verbose=False):
        self.cycle += 1
        if verbose:
            print(f"\n=== Cycle {self.cycle} ===")
        # Commit first? Classical Tomasulo does commit at end of cycle; we'll struct: issue -> exec -> writeback -> commit
        self.issue()
        # start execution (dispatch ready RS to FU)
        self.start_execution()
        # advance FUs
        finished = self.step_functional_units()
        # writeback: finished produce results and broadcast
        for rs_entry in finished:
            self.produce_result(rs_entry)
        # commit stage: commit at most one per cycle (common Tomasulo variant)
        self.commit()
        if verbose:
            print("ROB:", self.rob)
            print("RF status:", self.rf.reg_status)
            print("Registers (R0..R7):", {f"R{i}": self.rf.read(f"R{i}") for i in range(8)})
            print("RS ADD:", self.rs_add)
            print("RS MUL:", self.rs_mul)
            print("RS LDST:", self.rs_ldst)
            print("Mem(0..8):", self.memory.mem[:9])

    def run(self, max_cycles=200, verbose=False):
        while (self.completed_instructions < len(self.program)) and self.cycle < max_cycles:
            self.run_cycle(verbose=verbose)
        if verbose:
            print(f"\nFinished after {self.cycle} cycles, completed {self.completed_instructions} instructions.")
