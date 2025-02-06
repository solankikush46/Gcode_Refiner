import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
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

# Upload and refine G-code file
def upload_file(refined_file_text, download_button, status_label):
    input_file = filedialog.askopenfilename(filetypes=[("G-code Files", "*.gcode")])
    if input_file:
        refined_content = refine_gcode(input_file)
        if refined_content:
            refined_file_text.delete("1.0", tk.END)
            refined_file_text.insert(tk.END, refined_content)
            download_button.config(state="normal")
            status_label.config(text=f"File refined: {os.path.basename(input_file)}", fg="green")
            return refined_content, os.path.basename(input_file)
    return None, None

# Save refined G-code file
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

# Update file list UI
def update_file_list(file_listbox, refined_files):
    file_listbox.delete(0, tk.END)
    for file in refined_files:
        file_listbox.insert(tk.END, os.path.basename(file))

# View a file's content
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

# Delete a file from the list
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
