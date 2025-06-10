import os
from os import path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from encoder import encode_image
from decoder import decode_image
from encryption import encrypt_message, decrypt_message
from db import init_db, log_operation, get_history
from utils import validate_image
from PIL import Image, ImageTk
import threading

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography")
        self.root.geometry("700x800")
        self.root.config(bg="#f0f8ff")
        self.current_theme = "light"
        init_db()
        self.create_widgets()

    def build_color_scheme(self):
        self.colors = {
            'bg': '#f0f8ff' if self.current_theme == "light" else '#222',
            'fg': '#333' if self.current_theme == "light" else 'white',
            'btn_bg': '#32cd32',
            'btn_fg': '#fff',
            'accent': '#87cefa',
            'warning': '#ffcc00',
            'error': '#ff6347'
        }

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.create_widgets()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_widgets(self):
        self.clear_screen()
        self.build_color_scheme()
        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="Image Steganography", font=("Arial", 24, "bold"),
                 bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=20)

        tk.Button(frame, text="Encode", width=20, bg=self.colors['btn_bg'], fg=self.colors['btn_fg'],
                  font=("Arial", 12), command=self.encode_screen).pack(pady=10)

        tk.Button(frame, text="Decode", width=20, bg=self.colors['btn_bg'], fg=self.colors['btn_fg'],
                  font=("Arial", 12), command=self.decode_screen).pack(pady=10)

        tk.Button(frame, text="History Log", width=20, bg=self.colors['btn_bg'], fg=self.colors['btn_fg'],
                  font=("Arial", 12), command=self.show_history).pack(pady=10)

        tk.Button(frame, text="Toggle Theme", width=20, bg=self.colors['btn_bg'], fg=self.colors['btn_fg'],
                  font=("Arial", 12), command=self.toggle_theme).pack(pady=10)

    def encode_screen(self):
        self.clear_screen()
        self.build_color_scheme()
        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="Encode Message into Image", font=("Arial", 18, "bold"),
                 bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)

        tk.Label(frame, text="Confidential Message:", bg=self.colors['bg'], font=("Arial", 12),
                 fg=self.colors['fg']).pack(pady=5)
        self.message_entry = tk.Entry(frame, width=50, font=("Arial", 12))
        self.message_entry.pack(pady=5)

        tk.Label(frame, text="Password:", bg=self.colors['bg'], font=("Arial", 12),
                 fg=self.colors['fg']).pack(pady=5)
        self.password_entry = tk.Entry(frame, width=50, font=("Arial", 12), show='*')
        self.password_entry.pack(pady=5)

        self.file_path_label = tk.Label(frame, text="No file selected", bg=self.colors['bg'],
                                        fg="gray", font=("Arial", 10))
        self.file_path_label.pack(pady=5)

        tk.Button(frame, text="Browse", command=self.open_file_encode,
                  bg=self.colors['accent'], font=("Arial", 12)).pack(pady=5)

        self.preview_label = tk.Label(frame, bg=self.colors['bg'])
        self.preview_label.pack(pady=10)

        tk.Button(frame, text="Encode Message", width=15, bg=self.colors['btn_bg'],
                  fg=self.colors['btn_fg'], font=("Arial", 12),
                  command=lambda: threading.Thread(target=self.encode_image).start()).pack(pady=10)

        tk.Button(frame, text="Back", width=10, bg=self.colors['btn_bg'], fg=self.colors['btn_fg'],
                  font=("Arial", 12), command=self.create_widgets).pack(pady=10)

    def decode_screen(self):
        self.clear_screen()
        self.build_color_scheme()
        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="Decode Message from Image", font=("Arial", 18, "bold"),
                 bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)

        self.decode_file_path_label = tk.Label(frame, text="No file selected", bg=self.colors['bg'],
                                               fg="gray", font=("Arial", 10))
        self.decode_file_path_label.pack(pady=5)

        tk.Button(frame, text="Browse", command=self.open_file_decode,
                  bg=self.colors['accent'], font=("Arial", 12)).pack(pady=5)

        tk.Button(frame, text="Decode Message", width=15, bg=self.colors['btn_bg'],
                  fg=self.colors['btn_fg'], font=("Arial", 12),
                  command=self.ask_password_and_decode).pack(pady=10)

        self.decoded_message_label = tk.Label(frame, text="", bg=self.colors['bg'],
                                              font=("Arial", 12), fg=self.colors['fg'])
        self.decoded_message_label.pack(pady=5)

        self.decoded_message_text = tk.Text(frame, height=6, width=60, font=("Arial", 12),
                                            bg=self.colors['accent'], wrap='word')
        self.decoded_message_text.pack(pady=10)

        tk.Button(frame, text="Back", width=10, bg=self.colors['btn_bg'],
                  fg=self.colors['btn_fg'], font=("Arial", 12), command=self.create_widgets).pack(pady=10)

    def ask_password_and_decode(self):
        # Ask password on main thread
        password = simpledialog.askstring("Password", "Enter password:", show='*')
        if password is None:  # User cancelled
            return
        # Start decode thread with password
        threading.Thread(target=self.decode_image, args=(password,), daemon=True).start()

    def decode_image(self, password):
        # This runs in a separate thread
        path = self.decode_file_path_label.cget("text")
        if not path or path == "No file selected":
            self.root.after(0, lambda: messagebox.showwarning("Missing File", "Please select an image."))
            return

        success, encoded_msg = decode_image(path)
        if not success:
            self.root.after(0, lambda: messagebox.showerror("Error", encoded_msg))
            return

        decrypted = decrypt_message(encoded_msg, password)
        if decrypted:
            self.root.after(0, lambda: self.show_decoded_message(decrypted))
            log_operation("decode", path)
        else:
            self.root.after(0, lambda: messagebox.showerror("Decryption Failed", "Wrong password or corrupted data."))

    def show_decoded_message(self, decrypted):
        self.decoded_message_label.config(text="Decoded Message:")
        self.decoded_message_text.delete(1.0, tk.END)
        self.decoded_message_text.insert(tk.END, decrypted)

    def show_history(self):
        df = get_history()
        history_window = tk.Toplevel(self.root)
        history_window.title("History Log")
        text = tk.Text(history_window, wrap="word", width=80, height=20, font=("Arial", 10))
        text.pack(padx=10, pady=10)
        text.insert(tk.END, df.to_string(index=False))

    def open_file_encode(self):
        path_ = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path_ and validate_image(path_):
            self.file_path_label.config(text=path_)
            img = Image.open(path_)
            img = img.resize((200, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.preview_label.config(image=img_tk)
            self.preview_label.image = img_tk

    def open_file_decode(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not file_path:
            return  # no file selected

        if file_path.lower().endswith((".jpg", ".jpeg")):
            messagebox.showinfo("JPG Notice", "JPG is a lossy format. The encoded image will be saved as PNG to avoid corruption.")

        self.decode_file_path_label.config(text=file_path)

    def encode_image(self):
        message = self.message_entry.get()
        password = self.password_entry.get()
        image_path = self.file_path_label.cget("text")

        if not all([message, password, image_path]) or image_path == "No file selected":
            messagebox.showwarning("Missing Data", "Please complete all fields.")
            return
        if len(message) > 500:
            messagebox.showwarning("Too Long", "Message should be under 500 characters.")
            return

        encrypted = encrypt_message(message, password)
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if not save_path:
            return

        success, result = encode_image(image_path, encrypted, save_path)
        if success:
            log_operation("encode", save_path)
            messagebox.showinfo("Success", result)
            self.create_widgets()
        else:
            messagebox.showerror("Failed", result)


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
