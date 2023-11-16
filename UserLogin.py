import hashlib
import sqlite3
import subprocess
import random
from tkinter import messagebox

from PIL import Image, ImageTk
import customtkinter as ctk
from passlib.handlers import bcrypt

# Set custom appearance mode and color theme for customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BankDatabase:
    def __init__(self, db_name="bank_database.db"):
        try:
            # Establish a connection to the SQLite database
            self.conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            # Create necessary tables and ensure the existence of the admin user
            self.create_tables()
            self.create_admin()
        except sqlite3.Error as e:
            print("Database connection error:", e)

    def create_tables(self):
        # Create the 'accounts' table with required columns
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                username TEXT,
                password TEXT,
                balance REAL,
                validation_code TEXT
            )"""
        )
        self.conn.commit()

    def validate_username(self, username):
        # Check if the given username exists in the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username=?", (username,))
        user_data = cursor.fetchone()
        return user_data

    def create_admin(self):
        # Create a default admin user if it doesn't exist
        cursor = self.conn.cursor()
        # Hash the password using hashlib (replace 'sha256' with the desired hashing algorithm)
        hashed_password = hashlib.sha256("password".encode("utf-8")).hexdigest()
        cursor.execute(
            "INSERT OR IGNORE INTO accounts (username, password, balance, validation_code) VALUES (?, ?, ?, ?)",
            (
                "user",
                hashed_password,
                0.0,
                None,
            ),
        )
        self.conn.commit()

    def generate_validation_code(self):
        # Generate a random 6-digit validation code
        return str(random.randint(100000, 999999))

    def set_validation_code(self, username, validation_code):
        # Set the validation code for the user in the database
        self.cursor.execute("UPDATE accounts SET validation_code=? WHERE username=?", (validation_code, username))
        self.conn.commit()

    def update_password(self, username, new_password):
        # Update the password for the given username in the 'accounts' table
        hashed_password = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
        self.cursor.execute("UPDATE accounts SET password=? WHERE username=?", (hashed_password, username))
        self.conn.commit()

def open_user_home():
    # Open the User Home page using subprocess
    try:
        subprocess.run(["python", "UserHome.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open User Home page: {e}")

def login(username_entry, password_entry):
    # Handle user login
    entered_username = username_entry.get().strip()
    entered_password = password_entry.get().strip()

    # Check if the entered username exists in the database
    cursor = bank_database.cursor.execute("SELECT * FROM accounts WHERE username=?", (entered_username,))
    user_data = cursor.fetchone()

    if user_data and bcrypt.verify(entered_password, user_data["password"]):
        # If username and password are correct, show a welcome message and open the user home page
        messagebox.showinfo("Login Successful", f"Welcome, {entered_username}!")
        open_user_home()
    else:
        # If login fails, show an error message
        messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

def forgot_password():
    # Display custom username entry dialog with 'app' as the parent
    username_dialog = open_password_reset_window(app)
    app.wait_window(username_dialog)

    username = username_dialog.result
    if username:
        # Validate the username against the database
        user_data = bank_database.validate_username(username)
        if user_data:
            # Generate and set a validation code for the user
            validation_code = bank_database.generate_validation_code()
            bank_database.set_validation_code(username, validation_code)

            # Open the password reset window
            open_password_reset_window(app, username, bank_database)
        else:
            messagebox.showerror("User Not Found", "Username not found. Please enter a valid username.")

def open_password_reset_window(parent, username, bank_database):
    win = ctk.CTk(parent)
    win.geometry("350x350")
    win.title("Forgot Password")
    win.configure(background='#888000')
    win.resizable(False, False)

    # Declare new_password_entry as a global variable


    def update_password():
        # Declare new_password_entry as a global variable
        global new_password_entry

        # Retrieve the entered new password
        new_password = new_password_entry.get().strip()

        # Update the password in the database
        bank_database.update_password(username, new_password)

        # Display a success message
        messagebox.showinfo("Password Updated", "Your password has been successfully updated.")

        # Close the password reset window
        win.destroy()

        # Username entry

        username_entry = ctk.CTkEntry(win, placeholder_text="Username", font=("yu gothic ui semibold", 12))
        username_entry.place(x=40, y=80, width=256, height=50)
        username_entry.insert(0, username)  # Display the provided username in the entry
        username_entry.config(state='disabled')  # Disable editing

        username_label = ctk.CTkLabel(win, text='• Username', fg="#FFFFFF", bg='#272A37', font=("yu gothic ui", 11, 'bold'))
        username_label.place(x=40, y=50)

        # New Password entry
        new_password_entry = ctk.CTkEntry(win, placeholder_text="New Password", show='•', font=("yu gothic ui semibold", 12))
        new_password_entry.place(x=40, y=180, width=256, height=50)
        new_password_label = ctk.CTkLabel(win, text='• New Password', fg="#FFFFFF", bg='#272A37', font=("yu gothic ui", 11, 'bold'))
        new_password_label.place(x=40, y=150)

        # Update password button
        update_pass = ctk.CTkButton(win, fg='#f8f8f8', text='Update Password', bg='#1D90F5', font=("yu gothic ui", 12, "bold"),
                                    cursor='hand2', relief="flat", bd=0, activebackground="#1D90F5",
                                    command=update_password)
        update_pass.place(x=40, y=260, width=256, height=45)

    win.mainloop()

app = ctk.CTk()
app.geometry("600x600")
app.title("USER LOGIN")

# Initialize the bank database
bank_database = BankDatabase()

frame = ctk.CTkFrame(master=app)
frame.pack(pady=20, padx=40, fill='both', expand=True)

# Load and display an image
try:
    image = Image.open("home.png")  # Replace with your image path
    image = image.resize((150, 150))  # Adjust the size as needed
    photo = ImageTk.PhotoImage(image)
    image_label = ctk.CTkLabel(master=frame, image=photo)
    image_label.image = photo  # Keep a reference to the image
    image_label.pack(pady=12, padx=10)
except FileNotFoundError:
    messagebox.showerror("Error", "Image 'home.png' not found. Please provide the correct path.")

label = ctk.CTkLabel(master=frame, text='ENTER USER DETAILS')
label.pack(pady=12, padx=10)

user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
user_entry.pack(pady=12, padx=10)

user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
user_pass.pack(pady=12, padx=10)

# Create the login button
button = ctk.CTkButton(master=frame, text='Login', command=lambda: login(user_entry, user_pass))
button.pack(pady=12, padx=10)

# Create the "Forgot Password" button
forgot_password_button = ctk.CTkButton(master=frame, text='Forgot Password', command=forgot_password)
forgot_password_button.pack(pady=12, padx=10)

def on_closing():
    # Close the database connection when the app is closed
    bank_database.conn.close()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
