import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from pathlib import Path
from refine import refine_gcode

# Define persistent storage path
storage_file_path = Path.home() / "refined_files.json"

# Load refined files from storage
def load_refined_files():
    if storage_file_path.exists():
        with open(storage_file_path, 'r') as f:
            return json.load(f)
    return []

# Save refined files to storage
def save_refined_files(refined_files):
    with open(storage_file_path, 'w') as f:
        json.dump(refined_files, f)

# Function to open the settings window
def open_settings_window(settings_label, settings_vars):
    settings_window = Toplevel()
    settings_window.title("Additional Settings")
    settings_window.geometry("300x200")

    # Create input fields for Laser Power, Scanning Speed, and Layers
    tk.Label(settings_window, text="Laser Power (0-1000):").grid(row=0, column=0, padx=5, pady=5)
    laser_entry = tk.Entry(settings_window)
    laser_entry.grid(row=0, column=1)
    laser_entry.insert(0, settings_vars["laser_power"])

    tk.Label(settings_window, text="Scanning Speed (0-1000):").grid(row=1, column=0, padx=5, pady=5)
    speed_entry = tk.Entry(settings_window)
    speed_entry.grid(row=1, column=1)
    speed_entry.insert(0, settings_vars["scanning_speed"])

    tk.Label(settings_window, text="Layers:").grid(row=2, column=0, padx=5, pady=5)
    layer_entry = tk.Entry(settings_window)
    layer_entry.grid(row=2, column=1)
    layer_entry.insert(0, settings_vars["layers"])

    # Function to save settings and update the label
    def save_settings():
        try:
            settings_vars["laser_power"] = int(laser_entry.get())
            settings_vars["scanning_speed"] = int(speed_entry.get())
            settings_vars["layers"] = int(layer_entry.get())

            if not (0 <= settings_vars["laser_power"] <= 1000 and 0 <= settings_vars["scanning_speed"] <= 1000 and settings_vars["layers"] > 0):
                raise ValueError

            # Update the settings label and make it visible after saving
            settings_label.config(
                text=f"LP: {settings_vars['laser_power']}    SS: {settings_vars['scanning_speed']}    Layers: {settings_vars['layers']}",
                fg="black",
            )
            settings_label.pack(pady=5)  # Show the label after saving
            settings_window.destroy()

        except ValueError:
            messagebox.showerror(
                "Input Error", "Invalid values entered. Please follow:\nLP (0-1000), SS (0-1000), Layers (>0)"
            )

    save_button = tk.Button(settings_window, text="Save", command=save_settings, bg="#4caf50", fg="white")
    save_button.grid(row=3, columnspan=2, pady=10)

# Upload G-code file (shows the settings panel)
def upload_file(refined_file_text, download_button, status_label, settings_frame):
    input_file = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
    if input_file:
        settings_frame.pack(pady=10)  # Show the settings panel after uploading a file
        status_label.config(text=f"File uploaded: {os.path.basename(input_file)}", fg="green")
        return input_file
    return None

# Apply the laser settings and refine the G-code file
def apply_settings(input_file, refined_file_text, download_button, status_label, settings_vars):
    if not input_file:
        messagebox.showerror("Error", "No file uploaded.")
        return None, None

    refined_content = refine_gcode(
        input_file, settings_vars["laser_power"], settings_vars["scanning_speed"], settings_vars["layers"]
    )

    if refined_content:
        refined_file_text.delete("1.0", tk.END)
        refined_file_text.insert(tk.END, refined_content)
        download_button.config(state="normal")
        status_label.config(text="Refinement applied successfully!", fg="blue")
        return refined_content, os.path.basename(input_file)

    return None, None

# Save the refined G-code file to the user's Downloads folder
def download_file(refined_content, file_name, refined_files, file_listbox, status_label):
    if not refined_content or not file_name:
        messagebox.showerror("Error", "No refined file to download.")
        return

    downloads_path = str(Path.home() / "Downloads")
    output_file_name = os.path.splitext(file_name)[0] + "_refined.gcode"
    output_file_path = os.path.join(downloads_path, output_file_name)

    with open(output_file_path, 'w') as file:
        file.write(refined_content)

    if output_file_path not in refined_files:
        refined_files.append(output_file_path)
        save_refined_files(refined_files)
        update_file_list(file_listbox, refined_files)

    messagebox.showinfo("Download Complete", f"Refined file saved to:\n{output_file_path}")
    status_label.config(text=f"File saved to Downloads: {output_file_name}", fg="blue")

# Update the file list in the listbox
def update_file_list(file_listbox, refined_files):
    file_listbox.delete(0, tk.END)
    for file in refined_files:
        file_listbox.insert(tk.END, os.path.basename(file))

# View the selected file's content in the text area
def view_file(file_listbox, refined_file_text, refined_files, status_label):
    selected_index = file_listbox.curselection()
    if not selected_index:
        return

    selected_file = refined_files[selected_index[0]]
    with open(selected_file, 'r') as file:
        content = file.read()

    refined_file_text.delete("1.0", tk.END)
    refined_file_text.insert(tk.END, content)
    status_label.config(text=f"Viewing: {os.path.basename(selected_file)}", fg="blue")

# Delete the selected file from the list and storage
def delete_file(file_listbox, refined_files, status_label):
    selected_index = file_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("No Selection", "Please select a file to delete.")
        return

    if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this file from the list?"):
        return

    refined_files.pop(selected_index[0])
    save_refined_files(refined_files)
    update_file_list(file_listbox, refined_files)
    status_label.config(text="File deleted from the list.", fg="red")
