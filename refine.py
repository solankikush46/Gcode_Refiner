import re
from tkinter import messagebox

def refine_gcode(input_file, laser_power, scanning_speed, layers):
    """
    Reads a G-code file, removes E values, and applies user-defined laser power (S###) and scanning speed (F###)
    to the first G1 move after a G0 move, for the specified number of layers.
    """
    try:
        in_layer_0_section = False
        layer_count = 0
        previous_g_command = None
        refined_lines = []

        with open(input_file, 'r') as file:
            for line in file:
                # Remove all the E values
                if line.startswith("G"):
                    line = re.sub(r'E.*', '', line)

                # Track layers
                if ";layer:" in line.lower():
                    layer_number = int(re.search(r'\d+', line).group())
                    if layer_number >= layers:
                        layer_count += 1

                # Apply F### and S### only to the first G1 move after G0, within the specified layers
                if previous_g_command == "G0" and line.startswith("G1") and layer_count < layers:
                    line = line.strip() + f" F{scanning_speed} S{laser_power}\n"
                    layer_count += 1  # Increase applied layer count

                previous_g_command = line[:2] if line.startswith("G") else previous_g_command

                refined_lines.append(line.strip())

        return "\n".join(refined_lines)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None
