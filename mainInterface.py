
from tkinter import messagebox
import subprocess
from PIL import Image, ImageTk
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainInterface:
    def __init__(self, master):
        self.master = master
        master.geometry("660x400")
        master.title("ADMIN")

        frame = ctk.CTkFrame(master=master)
        frame.pack(pady=20, padx=40, fill='both', expand=True)

        # Load and display an image
        try:
            image = Image.open("home.png")
            image = image.resize((150, 150))  # Adjust the size as needed
            photo = ImageTk.PhotoImage(image)
            image_label = ctk.CTkLabel(master=frame, image=photo)
            image_label.image = photo  # Keep a reference to the image
            image_label.pack(pady=12, padx=10)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image 'home.png' not found. Please provide the correct path.")

        # Create the login button
        button_login = ctk.CTkButton(master=frame, text='Login', command=self.login)
        button_login.pack(pady=12, padx=10)

        # Create the create account button
        create_account_button = ctk.CTkButton(master=frame, text='Create Account', command=self.open_create_account_page)
        create_account_button.pack(pady=12, padx=10)

        # Create the admin button
        button_admin = ctk.CTkButton(master=frame, text='Admin', command=self.admin)
        button_admin.pack(pady=12, padx=10)

    def login(self):
        try:
            # Use subprocess to run UserLogin.py
            subprocess.run(["python", "UserLogin.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open User Login: {e}")

    def open_create_account_page(self):
        try:
            # Use subprocess to run create_account.py
            subprocess.run(["python", "create_account.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open create account page: {e}")

    def admin(self):
        try:
            # Use subprocess to run Admin_Login.py
            subprocess.run(["python", "Admin_Login.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Admin Login: {e}")


if __name__ == "__main__":
    root = ctk.CTk()
    main_interface = MainInterface(root)
    root.mainloop()
