import re
from tkinter import messagebox

def refine_gcode(input_file):
    """
    Reads a G-code file, removes E values, and adds 'S0.25' only when switching from G0 to G1.
    """
    try:
        in_layer_0_section = False
        previous_g_command = None
        refined_lines = []

        with open(input_file, 'r') as file:
            for line in file:
                # Remove all the E values
                if line.startswith("G"):
                    line = re.sub(r'E.*', '', line)

                # Add 'S0.25' only when transitioning from G0 to G1
                if previous_g_command == "G0" and line.startswith("G1"):
                    line = line.strip() + " S0.25\n"

                previous_g_command = line[:2] if line.startswith("G") else previous_g_command

                if ";layer:0" in line.lower():
                    in_layer_0_section = True
                    continue

                elif ";MESH" in line and in_layer_0_section:
                    in_layer_0_section = False
                    refined_lines.append(line)

                elif not in_layer_0_section:
                    refined_lines.append(line)

        return "\n".join(refined_lines)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None
