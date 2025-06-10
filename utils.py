from PIL import Image
from tkinter import messagebox

def validate_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except Exception as e:
        messagebox.showerror("Invalid File", f"Could not open image:\n{str(e)}")
        return False
