import tkinter as tk
from tkinter import filedialog

def select_image_from_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )

    return file_path
