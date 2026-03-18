import tkinter as tk

class Wire:
    def __init__(self, canvas, start_gate, start_pos, end_gate, end_pos):
        self.canvas = canvas
        self.start_gate = start_gate
        self.start_pos = start_pos
        self.end_gate = end_gate
        self.end_pos = end_pos
        self.line = canvas.create_line(*self.get_coords(), width=2)
        self.update_color()
        canvas.tag_bind(self.line, "<Button-3>", self.delete)

    def get_coords(self):
        x1 = self.start_gate.x + self.start_pos[0]
        y1 = self.start_gate.y + self.start_pos[1]
        x2 = self.end_gate.x + self.end_pos[0]
        y2 = self.end_gate.y + self.end_pos[1]
        return (x1, y1, x2, y2)

    def update_color(self):
        value = getattr(self.start_gate, "output", 0)
        color = "yellow" if value else "black"
        self.canvas.itemconfig(self.line, fill=color)

    def redraw(self):
        self.canvas.coords(self.line, *self.get_coords())
        self.update_color()

    def delete(self, event=None):
        if hasattr(self.start_gate, "wires_out") and self in self.start_gate.wires_out:
            self.start_gate.wires_out.remove(self)
        if self.end_gate.inputs.count(self.start_gate):
            idx = self.end_gate.inputs.index(self.start_gate)
            self.end_gate.inputs[idx] = None
        self.canvas.delete(self.line)
        if self in wires:
            wires.remove(self)
        update_all_outputs()


class Gate:
    def __init__(self, canvas, x, y, gate_type, num_inputs=2):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.type = gate_type
        self.num_inputs = num_inputs
        self.inputs = [None]*num_inputs
        self.input_positions = [(0, 10 + i*15) for i in range(num_inputs)]
        self.output = 0
        self.output_pos = (60, 20)
        self.wires_out = []

        # Draw rectangle
        self.id = canvas.create_rectangle(x, y, x+60, y+40, fill="lightblue")
        self.text_id = canvas.create_text(x+30, y+20, text=gate_type)

        # Input circles
        self.input_circles = []
        for pos in self.input_positions:
            circle = canvas.create_oval(x+pos[0]-5, y+pos[1]-5, x+pos[0]+5, y+pos[1]+5, fill="white")
            self.input_circles.append(circle)

        # Output circle
        self.output_circle = canvas.create_oval(x+self.output_pos[0]-5, y+self.output_pos[1]-5,
                                                x+self.output_pos[0]+5, y+self.output_pos[1]+5, fill="white")

        canvas.tag_bind(self.id, "<B1-Motion>", self.drag)
        canvas.tag_bind(self.text_id, "<B1-Motion>", self.drag)
        canvas.tag_bind(self.id, "<Button-3>", self.delete)
        canvas.tag_bind(self.text_id, "<Button-3>", self.delete)

    def drag(self, event):
        dx = event.x - self.x - 30
        dy = event.y - self.y - 20
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        for circle in self.input_circles:
            self.canvas.move(circle, dx, dy)
        self.canvas.move(self.output_circle, dx, dy)
        for wire in self.wires_out:
            wire.redraw()
        for g in gates:
            for wire in getattr(g, 'wires_out', []):
                wire.redraw()
        update_all_outputs()

    def compute(self):
        input_vals = [inp.output if isinstance(inp, Gate) else inp for inp in self.inputs]
        if self.type == "AND":
            self.output = int(all(input_vals))
        elif self.type == "OR":
            self.output = int(any(input_vals))
        elif self.type == "NOT":
            self.output = int(not input_vals[0])
        elif self.type == "XOR":
            self.output = int(input_vals[0] != input_vals[1])
        # Update colors
        color = "yellow" if self.output else "lightblue"
        self.canvas.itemconfig(self.id, fill=color)
        self.canvas.itemconfig(self.output_circle, fill="yellow" if self.output else "black")
        for wire in self.wires_out:
            wire.update_color()

    def delete(self, event=None):
        for wire in self.wires_out[:]:
            wire.delete()
        for gate in gates:
            for i, inp in enumerate(gate.inputs):
                if inp == self:
                    for wire in wires:
                        if wire.start_gate == self and wire.end_gate == gate:
                            wire.delete()
        canvas.delete(self.id)
        canvas.delete(self.text_id)
        canvas.delete(self.output_circle)
        for circle in self.input_circles:
            canvas.delete(circle)
        gates.remove(self)
        update_all_outputs()


class CounterDisplay(Gate):
    """1 input, no output, shows numeric value"""
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "COUNTER", num_inputs=1)
        canvas.delete(self.output_circle)
        self.output_circle = None
        self.canvas.itemconfig(self.text_id, text="0")

    def compute(self):
        input_val = self.inputs[0].output if self.inputs[0] else 0
        self.output = int(input_val)
        self.canvas.itemconfig(self.text_id, text=str(self.output))


class InputSwitch(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "SWITCH", num_inputs=0)
        self.output = 0
        self.canvas.itemconfig(self.id, fill="lightgreen")
        canvas.tag_bind(self.id, "<Button-1>", self.toggle)
        canvas.tag_bind(self.text_id, "<Button-1>", self.toggle)
        canvas.itemconfig(self.text_id, text="SWITCH")

    def toggle(self, event):
        self.output = 0 if self.output else 1
        self.canvas.itemconfig(self.output_circle, fill="yellow" if self.output else "black")
        self.canvas.itemconfig(self.id, fill="yellow" if self.output else "lightgreen")
        for wire in self.wires_out:
            wire.update_color()
        update_all_outputs()


# Global lists
gates = []
wires = []
drawing_wire = {"start_gate": None, "start_pos": None, "line": None}


def add_gate(gate_type):
    if gate_type == "NOT":
        gate = Gate(canvas, 50, 50, gate_type, num_inputs=1)
    elif gate_type == "COUNTER":
        gate = CounterDisplay(canvas, 50, 50)
    else:
        gate = Gate(canvas, 50, 50, gate_type, num_inputs=2)
    gates.append(gate)


def add_switch():
    sw = InputSwitch(canvas, 50, 50)
    gates.append(sw)


def start_wire(event):
    global drawing_wire
    for gate in gates:
        if hasattr(gate, "output_pos") and gate.output_pos:
            x, y = gate.x + gate.output_pos[0], gate.y + gate.output_pos[1]
            if abs(event.x - x) < 10 and abs(event.y - y) < 10:
                drawing_wire["start_gate"] = gate
                drawing_wire["start_pos"] = gate.output_pos
                drawing_wire["line"] = canvas.create_line(x, y, event.x, event.y, fill="black", width=2)
                break


def move_wire(event):
    global drawing_wire
    if drawing_wire["line"]:
        canvas.coords(drawing_wire["line"],
                      drawing_wire["start_gate"].x + drawing_wire["start_pos"][0],
                      drawing_wire["start_gate"].y + drawing_wire["start_pos"][1],
                      event.x, event.y)


def end_wire(event):
    global drawing_wire
    if not drawing_wire["start_gate"]:
        return
    for gate in gates:
        for idx, pos in enumerate(getattr(gate, "input_positions", [])):
            x, y = gate.x + pos[0], gate.y + pos[1]
            if abs(event.x - x) < 10 and abs(event.y - y) < 10:
                gate.inputs[idx] = drawing_wire["start_gate"]
                if hasattr(gate, "wires_out"):
                    wire = Wire(canvas, drawing_wire["start_gate"], drawing_wire["start_pos"], gate, pos)
                    drawing_wire["start_gate"].wires_out.append(wire)
                    wires.append(wire)
                canvas.delete(drawing_wire["line"])
                drawing_wire = {"start_gate": None, "start_pos": None, "line": None}
                update_all_outputs()
                return
    canvas.delete(drawing_wire["line"])
    drawing_wire = {"start_gate": None, "start_pos": None, "line": None}


def update_all_outputs():
    for gate in gates:
        gate.compute()


# GUI
root = tk.Tk()
root.title("Logic Simulator with All Gates + Counter Display")

canvas = tk.Canvas(root, width=1000, height=600, bg="white")
canvas.pack()

frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="Add SWITCH", command=add_switch).pack(side=tk.LEFT)
tk.Button(frame, text="Add AND", command=lambda: add_gate("AND")).pack(side=tk.LEFT)
tk.Button(frame, text="Add OR", command=lambda: add_gate("OR")).pack(side=tk.LEFT)
tk.Button(frame, text="Add NOT", command=lambda: add_gate("NOT")).pack(side=tk.LEFT)
tk.Button(frame, text="Add XOR", command=lambda: add_gate("XOR")).pack(side=tk.LEFT)
tk.Button(frame, text="Add COUNTER", command=lambda: add_gate("COUNTER")).pack(side=tk.LEFT)

canvas.bind("<Button-1>", start_wire)
canvas.bind("<B1-Motion>", move_wire)
canvas.bind("<ButtonRelease-1>", end_wire)

tk.Label(frame, text="Click-drag output to input to connect wires. Right-click to delete.").pack(side=tk.LEFT)

root.mainloop()