"""
GUI front-end for the Tomasulo simulator.

Place this file in the same folder as your other modules:
- instruction.py
- register_file.py
- reservation_station.py
- reorder_buffer.py
- functional_unit.py
- memory.py
- tomasulo.py

Run with:
    python gui_tomasulo.py

This GUI uses tkinter and provides controls to Step / Run / Pause / Reset the simulator,
and shows live tables for: Program (instruction fetch), ROB, Reservation Stations, Registers, and Memory.

It calls the Tomasulo.run_cycle() method to advance the simulator by one cycle.
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Import your simulator
try:
    from tomasulo import Tomasulo
    from instruction import Instruction
except Exception as e:
    # Provide a helpful message if imports fail
    raise ImportError("Couldn't import simulator modules. Make sure this file sits in the project folder and the other .py files are present. Original error: %s" % e)


class TomasuloGUI:
    def __init__(self, master):
        self.master = master
        master.title("Tomasulo Simulator — GUI")

        # make root resize nicely
        master.rowconfigure(2, weight=1)
        master.columnconfigure(0, weight=1)

        # simulation instance (created on reset/load)
        self.sim = None
        self.running = False
        self.run_delay_ms = 500  # default delay between cycles when running

        # top: controls
        ctrl_frame = ttk.Frame(master, padding=(6,6))
        ctrl_frame.grid(row=0, column=0, sticky="ew")
        ctrl_frame.columnconfigure(6, weight=1)

        ttk.Button(ctrl_frame, text="Load Sample Program", command=self.load_sample).grid(row=0, column=0, padx=4)
        self.step_btn = ttk.Button(ctrl_frame, text="Step", command=self.step)
        self.step_btn.grid(row=0, column=1, padx=4)
        self.run_btn = ttk.Button(ctrl_frame, text="Run", command=self.toggle_run)
        self.run_btn.grid(row=0, column=2, padx=4)
        ttk.Button(ctrl_frame, text="Reset", command=self.reset_sim).grid(row=0, column=3, padx=4)

        ttk.Label(ctrl_frame, text="Speed (ms):").grid(row=0, column=4, padx=(12,4))
        self.speed_var = tk.IntVar(value=self.run_delay_ms)
        speed_spin = ttk.Spinbox(ctrl_frame, from_=50, to=2000, increment=50, textvariable=self.speed_var, width=6, command=self.update_speed)
        speed_spin.grid(row=0, column=5, padx=4)

        # Status / stats
        status_frame = ttk.Frame(master, padding=(6,0))
        status_frame.grid(row=1, column=0, sticky="ew")
        self.cycle_var = tk.StringVar(value="Cycle: 0")
        ttk.Label(status_frame, textvariable=self.cycle_var).grid(row=0, column=0, sticky="w")
        self.completed_var = tk.StringVar(value="Completed: 0")
        ttk.Label(status_frame, textvariable=self.completed_var).grid(row=0, column=1, sticky="w", padx=(12,0))

        # main panes: left column (Program + ROB) | middle (RS) | right (Registers & Memory)
        panes = ttk.Frame(master, padding=(6,6))
        panes.grid(row=2, column=0, sticky="nsew")
        panes.rowconfigure(0, weight=1)
        panes.columnconfigure(0, weight=1)
        panes.columnconfigure(1, weight=2)
        panes.columnconfigure(2, weight=1)

        # Left: Program (instruction fetch view) and ROB
        left_frame = ttk.Frame(panes)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        prog_frame = ttk.LabelFrame(left_frame, text="Program (Instruction Memory)", padding=(6,6))
        prog_frame.grid(row=0, column=0, sticky="nsew", pady=(0,6))
        prog_frame.rowconfigure(0, weight=1)
        prog_frame.columnconfigure(0, weight=1)

        # program listbox with scrollbar
        self.prog_listbox = tk.Listbox(prog_frame, exportselection=False)
        prog_scroll = ttk.Scrollbar(prog_frame, orient="vertical", command=self.prog_listbox.yview)
        self.prog_listbox.config(yscrollcommand=prog_scroll.set)
        self.prog_listbox.grid(row=0, column=0, sticky="nsew")
        prog_scroll.grid(row=0, column=1, sticky="ns")

        # ROB
        rob_frame = ttk.LabelFrame(left_frame, text="Reorder Buffer (ROB)", padding=(6,6))
        rob_frame.grid(row=1, column=0, sticky="nsew")
        rob_frame.rowconfigure(0, weight=1)
        rob_frame.columnconfigure(0, weight=1)

        self.rob_tree = ttk.Treeview(rob_frame, columns=("tag","instr","dest","type","ready","value","addr"), show="headings", height=8)
        for col in ("tag","instr","dest","type","ready","value","addr"):
            self.rob_tree.heading(col, text=col)
            self.rob_tree.column(col, width=80, anchor="center")
        self.rob_tree.grid(row=0, column=0, sticky="nsew")
        rob_scroll = ttk.Scrollbar(rob_frame, orient="vertical", command=self.rob_tree.yview)
        self.rob_tree.config(yscrollcommand=rob_scroll.set)
        rob_scroll.grid(row=0, column=1, sticky="ns")

        # Middle: Reservation Stations
        rs_frame = ttk.LabelFrame(panes, text="Reservation Stations", padding=(6,6))
        rs_frame.grid(row=0, column=1, sticky="nsew")
        rs_frame.rowconfigure(0, weight=1)
        rs_frame.columnconfigure(0, weight=1)

        # three RS tables: ADD, MUL, LDST
        self.rs_tabs = ttk.Notebook(rs_frame)
        self.rs_tabs.grid(row=0, column=0, sticky="nsew")

        self.rs_add_tree = self._make_rs_tree(self.rs_tabs, "ADD RS")
        self.rs_mul_tree = self._make_rs_tree(self.rs_tabs, "MUL RS")
        self.rs_ld_tree = self._make_rs_tree(self.rs_tabs, "LD/ST RS")

        # Right: Registers & Memory
        rm_frame = ttk.Frame(panes)
        rm_frame.grid(row=0, column=2, sticky="nsew", padx=(6,0))
        rm_frame.rowconfigure(0, weight=1)
        rm_frame.rowconfigure(1, weight=1)
        rm_frame.columnconfigure(0, weight=1)

        reg_frame = ttk.LabelFrame(rm_frame, text="Registers", padding=(6,6))
        reg_frame.grid(row=0, column=0, sticky="nsew")
        reg_frame.rowconfigure(0, weight=1)
        reg_frame.columnconfigure(0, weight=1)

        self.reg_tree = ttk.Treeview(reg_frame, columns=("reg","val","status"), show="headings", height=12)
        for col, w in (("reg",60),("val",80),("status",120)):
            self.reg_tree.heading(col, text=col)
            self.reg_tree.column(col, width=w, anchor="center")
        self.reg_tree.grid(row=0, column=0, sticky="nsew")
        reg_scroll = ttk.Scrollbar(reg_frame, orient="vertical", command=self.reg_tree.yview)
        self.reg_tree.config(yscrollcommand=reg_scroll.set)
        reg_scroll.grid(row=0, column=1, sticky="ns")

        mem_frame = ttk.LabelFrame(rm_frame, text="Memory (partial view)", padding=(6,6))
        mem_frame.grid(row=1, column=0, sticky="nsew", pady=(8,0))
        mem_frame.rowconfigure(0, weight=1)
        mem_frame.columnconfigure(0, weight=1)

        self.mem_tree = ttk.Treeview(mem_frame, columns=("addr","val"), show="headings", height=12)
        self.mem_tree.heading("addr", text="addr")
        self.mem_tree.heading("val", text="value")
        self.mem_tree.column("addr", width=80, anchor="center")
        self.mem_tree.column("val", width=120, anchor="center")
        self.mem_tree.grid(row=0, column=0, sticky="nsew")
        mem_scroll = ttk.Scrollbar(mem_frame, orient="vertical", command=self.mem_tree.yview)
        self.mem_tree.config(yscrollcommand=mem_scroll.set)
        mem_scroll.grid(row=0, column=1, sticky="ns")

        # footer: tips
        tip = ttk.Label(master, text="Tip: load the sample program and press Run. Step executes one cycle." )
        tip.grid(row=3, column=0, sticky="w", padx=8, pady=(4,8))

        self.reset_sim()

    def _make_rs_tree(self, parent, title):
        frame = ttk.Frame(parent)
        parent.add(frame, text=title)
        cols = ("name","op","busy","Vj","Vk","Qj","Qk","dest","exec_left")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=80, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        # add vertical scrollbar
        scr = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.config(yscrollcommand=scr.set)
        scr.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def reset_sim(self):
        # create a fresh simulator with sample program
        self.load_sample()
        self.running = False
        self.run_btn.config(text="Run")

    def load_sample(self):
        # build a sample program (same as earlier example) and show in listbox
        prog = [
            Instruction("LD", dest="R1", src1=None, imm=10),
            Instruction("LD", dest="R2", src1=None, imm=11),
            Instruction("ADD", dest="R3", src1="R1", src2="R2"),
            Instruction("MUL", dest="R4", src1="R3", src2="R1"),
            Instruction("SUB", dest="R5", src1="R4", src2="R2"),
            Instruction("ST", dest=None, src1=None, src2="R5", imm=12),
        ]
        self.sim = Tomasulo(prog, reg_count=16, rob_size=8)
        # init memory
        self.sim.memory.store(10, 5)
        self.sim.memory.store(11, 7)

        # populate program listbox
        self.prog_listbox.delete(0, tk.END)
        for i, instr in enumerate(prog):
            self.prog_listbox.insert(tk.END, f"{i}: {repr(instr)}")
        # highlight PC (0)
        if self.prog_listbox.size() > 0:
            self.prog_listbox.selection_clear(0, tk.END)
            self.prog_listbox.selection_set(0)
            self.prog_listbox.see(0)

        self.update_all_views()

    def update_speed(self):
        try:
            self.run_delay_ms = int(self.speed_var.get())
        except Exception:
            pass

    def step(self):
        if not self.sim:
            messagebox.showwarning("No simulator","Load a program first")
            return
        # run a single cycle
        self.sim.run_cycle(verbose=False)
        self.update_all_views()

    def toggle_run(self):
        if not self.sim:
            messagebox.showwarning("No simulator","Load a program first")
            return
        self.running = not self.running
        self.run_btn.config(text="Pause" if self.running else "Run")
        if self.running:
            self._run_loop()

    def _run_loop(self):
        if not self.running:
            return
        # step one cycle
        if self.sim.completed_instructions < len(self.sim.program):
            self.sim.run_cycle(verbose=False)
            self.update_all_views()
            # schedule next
            self.master.after(self.run_delay_ms, self._run_loop)
        else:
            self.running = False
            self.run_btn.config(text="Run")
            messagebox.showinfo("Finished","Simulation finished all instructions")

    def update_all_views(self):
        if not self.sim:
            return
        # update status
        self.cycle_var.set(f"Cycle: {self.sim.cycle}")
        self.completed_var.set(f"Completed: {self.sim.completed_instructions}")

        # highlight PC in program listbox
        if self.prog_listbox.size() > 0:
            pc = min(self.sim.pc, self.prog_listbox.size()-1)
            self.prog_listbox.selection_clear(0, tk.END)
            if pc >= 0:
                self.prog_listbox.selection_set(pc)
                self.prog_listbox.see(pc)

        # ROB
        for i in self.rob_tree.get_children():
            self.rob_tree.delete(i)
        try:
            entries = list(self.sim.rob.entries)
        except Exception:
            entries = []
        for e in entries:
            self.rob_tree.insert("", "end", values=(e.tag, repr(e.instr), e.dest, e.typ, str(e.ready), str(e.value), str(e.addr)))

        # RS tables
        self._update_rs_tree(self.rs_add_tree, self.sim.rs_add)
        self._update_rs_tree(self.rs_mul_tree, self.sim.rs_mul)
        self._update_rs_tree(self.rs_ld_tree, self.sim.rs_ldst)

        # Registers
        for i in self.reg_tree.get_children():
            self.reg_tree.delete(i)
        for r in sorted(self.sim.rf.regs.keys(), key=lambda x: int(x[1:])):
            val = self.sim.rf.read(r)
            status = self.sim.rf.get_status(r)
            self.reg_tree.insert("", "end", values=(r, val, str(status)))

        # Memory (show first 64 locations by default)
        for i in self.mem_tree.get_children():
            self.mem_tree.delete(i)
        memview = list(enumerate(self.sim.memory.mem[:64]))
        for addr, val in memview:
            self.mem_tree.insert("", "end", values=(addr, val))

        # visually emphasize ROB ready entries and busy RS rows using tags
        for iid in self.rob_tree.get_children():
            vals = self.rob_tree.item(iid, 'values')
            if vals and vals[4] == 'True':
                self.rob_tree.item(iid, tags=('ready',))
            else:
                self.rob_tree.item(iid, tags=())
        self.rob_tree.tag_configure('ready', background='#dff0d8')

    def _update_rs_tree(self, tree, rs_obj):
        for i in tree.get_children():
            tree.delete(i)
        for e in rs_obj.entries:
            exec_left = getattr(e, 'exec_cycles_left', None)
            tree.insert("", "end", values=(e.name, str(e.op), str(e.busy), str(e.Vj), str(e.Vk), str(e.Qj), str(e.Qk), str(e.dest), str(exec_left)))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    app = TomasuloGUI(root)
    root.mainloop()
