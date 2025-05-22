# Minsky Machine as Petri Net

This project implements a simulation of a [Minsky Machine](https://en.wikipedia.org/wiki/Minsky_machine) using an object-oriented Petri net model in Python. It provides a visualization of the execution steps as `.dot` files and optionally as `.pdf` files using Graphviz.

## Features

- Models Minsky machine instructions (`INC`, `DEC`, `HALT`) as Petri net transitions
- Visualizes the state of the net at each step
- Supports inhibitor arcs for zero-checks
- Generates `.dot` and `.pdf` frames for each simulation step (Snoopy and Similar did not work on my computer)

## Installation

### Prerequisites

Make sure you have Python 3 installed.

You also need [Graphviz](https://graphviz.org/) for PDF rendering:

**Ubuntu/Debian:**
```bash
sudo apt install graphviz
```

**macOS (Homebrew):**
```bash
brew install graphviz
```

**Windows:**

Download and install Graphviz from: https://graphviz.org/download/

Ensure that the `dot` executable is available in your system `PATH`.

```

No additional Python packages are required.

## Usage

To run the simulation, execute:

```bash
python3 ModelsForConcurrency.py
```

This will:

- Simulate the defined Minsky program 
- Create a `frames/` directory with `.dot` and `.pdf` visualizations of each step
- Print each step to the terminal, including which transition fired

## Project Notes

- The machine state is encoded via places: `R1`, `R2`, and control flow places `P0`, `P1`, ...
- Transitions encode instructions:
  - `INC Rn`: consumes control token, adds one token to register `Rn`
  - `DEC Rn target`: branches based on whether `Rn` has tokens
- Inhibitor arcs are used to model zero-checks in `DEC` instructions
- The `simulate()` function stops when no transition is enabled or when `max_steps` is reached

## Example

The included program (`program2`) performs the addition `R1 = R1 + R2` by transferring tokens from `R2` to `R1` until `R2` is empty.

Initial state:
```
R1 = 5
R2 = 6
```

After execution:
```
R1 = 11
R2 = 0
```

