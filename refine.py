import re
from tkinter import messagebox

def refine_gcode(input_file, settings_list):
    """
    Reads a G-code file, removes E values, and applies user-defined laser power (S###) and scanning speed (F###)
    to the first G1 move after a G0 move, applying settings layer by layer.
    Additionally, removes layer 0 and all its contents.
    """
    try:
        refined_lines = []
        current_setting_index = 0
        layer_count = 0
        previous_g_command = None
        inside_layer_0 = False  # Track whether we're inside layer 0

        with open(input_file, 'r') as file:
            for line in file:
                # Detect and remove layer 0 and its contents
                if ";layer:0" in line.lower():
                    inside_layer_0 = True
                    continue  # Skip this line and enter layer 0 removal mode
                
                if inside_layer_0:
                    if ";layer:" in line.lower() and "0" not in line:
                        inside_layer_0 = False  # Exit layer 0 removal mode
                    else:
                        continue  # Continue skipping lines inside layer 0
                
                # Remove all the E values
                if line.startswith("G"):
                    line = re.sub(r'E.*', '', line)

                # Track layers
                if ";layer:" in line.lower():
                    layer_number = int(re.search(r'\d+', line).group())

                    # Check if the current layer count matches the setting's layer count
                    if layer_count >= settings_list[current_setting_index]["layers"]:
                        current_setting_index = min(current_setting_index + 1, len(settings_list) - 1)
                        layer_count = 0  # Reset layer count for the new setting
                    
                    layer_count += 1  # Increment the layer counter

                # Apply F### and S### only to the first G1 move after G0 within the current layer settings
                if previous_g_command == "G0" and line.startswith("G1"):
                    setting = settings_list[current_setting_index]
                    line = line.strip() + f" F{setting['scanning_speed']} S{setting['laser_power']}\n"

                previous_g_command = line[:2] if line.startswith("G") else previous_g_command
                refined_lines.append(line.strip())

        return "\n".join(refined_lines)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None
