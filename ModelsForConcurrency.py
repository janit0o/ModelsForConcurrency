import os
import subprocess

class Place:
    def __init__(self, name, tokens=0):
        self.name = name
        self.tokens = tokens

    def __repr__(self):
        return f"{self.name}: {self.tokens}"


class Transition:
    def __init__(self, name, label=None):
        self.name = name
        self.label = label if label else name
        self.inputs = []     # List of (Place, count)
        self.outputs = []    # List of (Place, count)
        self.inhibitors = [] # List of Places

    def add_input(self, place, count=1):
        self.inputs.append((place, count))

    def add_output(self, place, count=1):
        self.outputs.append((place, count))

    def add_inhibitor(self, place):
        self.inhibitors.append(place)

    def is_enabled(self):
        return all(p.tokens >= c for p, c in self.inputs) and \
               all(p.tokens == 0 for p in self.inhibitors)

    def fire(self):
        if not self.is_enabled():
            return False
        for p, c in self.inputs:
            p.tokens -= c
        for p, c in self.outputs:
            p.tokens += c
        print(f"Fired: {self.name}")
        return True


class MinskyMachinePetriNet:
    def __init__(self, program, initial_tokens=None):
        self.program = program
        self.places = {}      # name -> Place
        self.transitions = []
        self.initial_tokens = initial_tokens if initial_tokens else {}
        self._build()

    def _get_place(self, name, default_tokens=0):
        if name not in self.places:
            tokens = self.initial_tokens.get(name, default_tokens)
            self.places[name] = Place(name, tokens)
        return self.places[name]

    def _build(self):
        # Add registers
        self._get_place("R1")
        self._get_place("R2")
        # Initial control place
        self._get_place("P0", default_tokens=1)

        for i, instr in enumerate(self.program):
            pi = self._get_place(f"P{i}")

            if instr[0] == "INC":
                r = self._get_place(f"R{instr[1]}")
                pi_next = self._get_place(f"P{i+1}")
                t = Transition(f"T_INC_{i}", label=f"INC R{instr[1]}")
                t.add_input(pi)
                t.add_output(pi_next)
                t.add_output(r)
                self.transitions.append(t)

            elif instr[0] == "DEC":
                r = self._get_place(f"R{instr[1]}")
                target = self._get_place(f"P{instr[2]}")
                pi_next = self._get_place(f"P{i+1}")

                # Case R > 0
                t_pos = Transition(f"T_DEC_{i}_POS", label=f"DEC R{instr[1]} > 0")
                t_pos.add_input(pi)
                t_pos.add_input(r)
                t_pos.add_output(pi_next)
                self.transitions.append(t_pos)

                # Case R == 0
                t_zero = Transition(f"T_DEC_{i}_ZERO", label=f"DEC R{instr[1]} == 0")
                t_zero.add_input(pi)
                t_zero.add_output(target)
                t_zero.add_inhibitor(r)
                self.transitions.append(t_zero)

            elif instr[0] == "HALT":
                t = Transition(f"T_HALT_{i}", label="HALT")
                t.add_input(pi)
                self.transitions.append(t)


    def simulate(self, max_steps=100, export_frames=True, out_dir="frames", render_pdf=True):
        os.makedirs(out_dir, exist_ok=True)

        for step in range(max_steps):
            print(f"\n--- Step {step} ---")
            for p in self.places.values():
                print(p)

            if export_frames:
                dot_path = os.path.join(out_dir, f"frame_{step:03d}.dot")
                self._export_dot_frame(dot_path)
                if render_pdf:
                    pdf_path = dot_path.replace(".dot", ".pdf")
                    subprocess.run(["dot", "-Tpdf", dot_path, "-o", pdf_path])

            fired = False
            for t in self.transitions:
                if t.fire():
                    fired = True
                    break

            if not fired:
                print("Keine Transition feuert. Ende.")
                break

    def _export_dot_frame(self, filepath):
        lines = ["digraph PetriNetStep {", "  rankdir=LR;"]
        for place in self.places.values():
            shape = "circle" if place.name.startswith("R") else "ellipse"
            color = "lightblue" if place.tokens > 0 else "white"
            label = f"{place.name}\\n({place.tokens})"
            lines.append(f'  {place.name} [shape={shape}, label="{label}", style=filled, fillcolor={color}];')

        for t in self.transitions:
            lines.append(f'  {t.name} [shape=box, label="{t.label}", style=filled, fillcolor=lightgrey];')
            for p, _ in t.inputs:
                lines.append(f'  {p.name} -> {t.name};')
            for p, _ in t.outputs:
                lines.append(f'  {t.name} -> {p.name};')
            for p in t.inhibitors:
                lines.append(f'  {p.name} -> {t.name} [style=dashed, label="inhibitor"];')

        lines.append("}")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        print(f"Frame exportiert: {filepath}")

if __name__ == "__main__":
    program = [
        ("INC", 1),
        ("DEC", 1, 0),
        ("HALT",)
    ]

    #R1 = R1 + R2
    program2 = [
        ("DEC", 2, 3),    # P0: if R2 == 0 → P3, else R2-- → P1
        ("INC", 1),       # P1: R1++
        ("DEC", 0, 0),    # P2: Dummy-DEC mit R0 = 0 → zurück zu P0
        ("HALT",)
    ]


    initial_tokens = {
        "R1": 5,
        "R2": 6,
    }

    initial_tokens2 = {
        "R1": 5,
        "R2": 6,
        "R0": 0  # dummy register
    }

    net = MinskyMachinePetriNet(program2, initial_tokens=initial_tokens2)
    net.simulate()

