import tkinter as tk

# ------------------------------
# Logic Gate Base Class
# ------------------------------
class LogicGate:
    def __init__(self, canvas, x, y, gate_type):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.gate_type = gate_type
        self.width = 80
        self.height = 50
        self.inputs = [0, 0] if gate_type != "NOT" else [0]
        self.output = 0
        self.drag_data = {"x": 0, "y": 0}

        # Draw gate rectangle
        self.rect = self.canvas.create_rectangle(
            x, y, x + self.width, y + self.height, fill="lightblue"
        )
        self.text = self.canvas.create_text(
            x + self.width / 2, y + self.height / 2, text=gate_type, font=("Arial", 12, "bold")
        )

        # Bind mouse events for dragging
        for item in (self.rect, self.text):
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_start)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)

    def on_start(self, event):
        """Start dragging"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        """While dragging"""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drop(self, event):
        """Drop gate"""
        coords = self.canvas.coords(self.rect)
        self.x, self.y = coords[0], coords[1]

    def evaluate(self):
        """Evaluate gate output based on inputs"""
        if self.gate_type == "AND":
            self.output = int(all(self.inputs))
        elif self.gate_type == "OR":
            self.output = int(any(self.inputs))
        elif self.gate_type == "NOT":
            self.output = int(not self.inputs[0])
        return self.output

# ------------------------------
# Main Application
# ------------------------------
class LogicGateGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Logic Gate Game - Tkinter")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Create gates
        self.gates = [
            LogicGate(self.canvas, 50, 50, "AND"),
            LogicGate(self.canvas, 200, 50, "OR"),
            LogicGate(self.canvas, 350, 50, "NOT")
        ]

        # Input toggle buttons
        self.input_vars = [tk.IntVar(value=0), tk.IntVar(value=0)]
        tk.Checkbutton(root, text="Input A", variable=self.input_vars[0], command=self.update_outputs).pack(side="left")
        tk.Checkbutton(root, text="Input B", variable=self.input_vars[1], command=self.update_outputs).pack(side="left")

        # Output label
        self.output_label = tk.Label(root, text="Outputs: ", font=("Arial", 12))
        self.output_label.pack(side="left", padx=20)

        self.update_outputs()

    def update_outputs(self):
        """Update gate outputs based on inputs"""
        a = self.input_vars[0].get()
        b = self.input_vars[1].get()

        for gate in self.gates:
            if gate.gate_type == "NOT":
                gate.inputs = [a]
            else:
                gate.inputs = [a, b]
            gate.evaluate()

        outputs = ", ".join([f"{g.gate_type}: {g.output}" for g in self.gates])
        self.output_label.config(text=f"Outputs: {outputs}")

# ------------------------------
# Run the Game
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LogicGateGame(root)
    root.mainloop()