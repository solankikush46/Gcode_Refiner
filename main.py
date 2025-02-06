import tkinter as tk
from functions import upload_file, download_file, view_file, delete_file, update_file_list, load_refined_files

# Initialize global variables
refined_files = load_refined_files()
current_refined_content = None
current_file_name = None

# Main application window
root = tk.Tk()
root.title("G-code Refiner")
root.geometry("800x500")
root.configure(bg="#f4f4f4")

# Title label
title_label = tk.Label(root, text="G-code Refiner", font=("Arial", 16, "bold"), bg="#f4f4f4", fg="#333")
title_label.pack(pady=20)

# File list frame
file_list_frame = tk.Frame(root, bg="#f4f4f4")
file_list_frame.pack(fill="y", side="left", padx=10, pady=10)

file_listbox = tk.Listbox(file_list_frame, height=20, width=30, font=("Courier", 10))
file_listbox.pack(fill="y", expand=True, padx=5, pady=5)

update_file_list(file_listbox, refined_files)

view_button = tk.Button(file_list_frame, text="View File", command=lambda: view_file(file_listbox, refined_file_text, refined_files, status_label),
                        font=("Arial", 12), bg="#2196f3", fg="white")
view_button.pack(pady=5)

delete_button = tk.Button(file_list_frame, text="Delete File", command=lambda: delete_file(file_listbox, refined_files, status_label),
                          font=("Arial", 12), bg="#f44336", fg="white")
delete_button.pack(pady=5)

# Text area for refined file
refined_file_text = tk.Text(root, wrap="none", font=("Courier", 10), height=20, width=60, bg="#ffffff", fg="#000000")
refined_file_text.pack(pady=10, padx=10)

# Status label
status_label = tk.Label(root, text="Upload a file to start refining.", font=("Arial", 12), bg="#f4f4f4", fg="black")
status_label.pack(pady=10)

# Buttons
upload_button = tk.Button(root, text="Upload G-code File", command=lambda: upload_file(refined_file_text, download_button, status_label),
                          font=("Arial", 14), bg="#4caf50", fg="white", padx=10, pady=5)
upload_button.pack(pady=10)

download_button = tk.Button(root, text="Download Refined File", command=lambda: download_file(current_refined_content, current_file_name, refined_files, file_listbox, status_label),
                            font=("Arial", 14), bg="#2196f3", fg="white", padx=10, pady=5, state="disabled")
download_button.pack(pady=10)

# Run application
root.mainloop()
