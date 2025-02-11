import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from pathlib import Path
from refine import refine_gcode

# Persistent storage path
storage_file_path = Path.home() / "refined_files.json"

def load_refined_files():
    if storage_file_path.exists():
        with open(storage_file_path, 'r') as f:
            return json.load(f)
    return []

def save_refined_files(refined_files):
    with open(storage_file_path, 'w') as f:
        json.dump(refined_files, f)

def open_settings_window(settings_label, settings_list):
    settings_window = Toplevel()
    settings_window.title("Additional Settings")
    settings_window.geometry("400x300")
    
    settings_frames = []
    
    def add_setting():
        frame = tk.Frame(settings_window)
        frame.pack(pady=5, fill='x')
        
        tk.Label(frame, text="Laser Power:").pack(side="left")
        laser_entry = tk.Entry(frame, width=5)
        laser_entry.pack(side="left", padx=5)
        
        tk.Label(frame, text="Scanning Speed:").pack(side="left")
        speed_entry = tk.Entry(frame, width=5)
        speed_entry.pack(side="left", padx=5)
        
        tk.Label(frame, text="Layers:").pack(side="left")
        layer_entry = tk.Entry(frame, width=5)
        layer_entry.pack(side="left", padx=5)
        
        settings_frames.append((laser_entry, speed_entry, layer_entry))
    
    add_button = tk.Button(settings_window, text="Add Setting", command=add_setting)
    add_button.pack(pady=5)

    def save_settings():
        try:
            settings_list.clear()
            for laser_entry, speed_entry, layer_entry in settings_frames:
                settings = {
                    "laser_power": int(laser_entry.get()),
                    "scanning_speed": int(speed_entry.get()),
                    "layers": int(layer_entry.get())
                }
                settings_list.append(settings)
            settings_label.config(text=f"Settings saved: {len(settings_list)} sets", fg="black")
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")
    
    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=5)
    
    add_setting()

def upload_file(refined_file_text, download_button, status_label, settings_frame):
    """Allows user to upload a G-code file and updates the UI accordingly."""
    
    input_file = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
    
    if input_file:
        settings_frame.pack(pady=10)  # Show the settings panel after uploading a file
        status_label.config(text=f"File uploaded: {os.path.basename(input_file)}", fg="green")
        return input_file

    return None  # Ensure function always returns something

def apply_settings(input_file, refined_file_text, download_button, status_label, settings_list):
    if not input_file:
        messagebox.showerror("Error", "No file uploaded.")
        return None, None
    
    refined_content = refine_gcode(input_file, settings_list)
    
    if refined_content:
        refined_file_text.delete("1.0", tk.END)
        refined_file_text.insert(tk.END, refined_content)
        download_button.config(state="normal")
        status_label.config(text="Refinement applied successfully!", fg="blue")
        return refined_content, os.path.basename(input_file)
    
    return None, None

def download_file(refined_content, file_name, refined_files, file_listbox, status_label):
    """Saves the refined G-code file to the user's Downloads folder."""
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

def update_file_list(file_listbox, refined_files):
    """Updates the file list in the Listbox."""
    file_listbox.delete(0, tk.END)
    for file in refined_files:
        file_listbox.insert(tk.END, os.path.basename(file))

def view_file(file_listbox, refined_file_text, refined_files, status_label):
    """Displays the selected refined file content in the text area."""
    selected_index = file_listbox.curselection()
    if not selected_index:
        return

    selected_file = refined_files[selected_index[0]]
    with open(selected_file, 'r') as file:
        content = file.read()

    refined_file_text.delete("1.0", tk.END)
    refined_file_text.insert(tk.END, content)
    status_label.config(text=f"Viewing: {os.path.basename(selected_file)}", fg="blue")

def delete_file(file_listbox, refined_files, status_label):
    """Deletes the selected file from the list and storage."""
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
