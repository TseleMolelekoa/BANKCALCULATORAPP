# Import necessary libraries and modules
import subprocess
from customtkinter import CTkButton, CTkLabel, CTkEntry, CTk
from tkinter import messagebox
import sqlite3
import bcrypt
import random
import string
from PIL import Image, ImageTk
from passlib.hash import bcrypt

# Class for managing the bank database
class BankDatabase:
    def __init__(self, db_file="bank_database.db"):
        # Connect to the SQLite database
        self.conn = sqlite3.connect(db_file)
        # Create necessary tables in the database
        self.create_tables()

    def create_tables(self):
        # Create a cursor for executing SQL queries
        cursor = self.conn.cursor()

        # Create the accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                username TEXT,
                password TEXT, 
                balance REAL
            )
        ''')

        # Create the transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT,
                amount REAL,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES accounts(account_number)
            )
        ''')

        # Commit changes to the database
        self.conn.commit()

# Function to open the UserLogin page
def UserLogin():
    try:
        # Use subprocess to run UserLogin.py
        subprocess.run(["python", "UserLogin.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open User Home Page: {e}")

# Class for creating a new bank account
class CreateAccountPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Create Account")
        # Initialize the BankDatabase object
        self.bank_db = BankDatabase()

        # Load and display an image
        try:
            image = Image.open(r"C:\Users\molel\PycharmProjects\BANK & CALCULATOR APP\home.png")
            image = image.resize((150, 150))  # Adjust the size as needed
            photo = ImageTk.PhotoImage(image)
            image_label = CTkLabel(master=self.master, image=photo)
            image_label.image = photo  # To prevent image from being garbage collected
            image_label.pack(pady=12, padx=10)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image 'home.png' not found. Please provide the correct path.")

        # Create form elements
        label = CTkLabel(master=self.master, text='CREATE A BANK ACCOUNT')
        label.pack(pady=12, padx=10)

        self.user_entry = CTkEntry(master=self.master, placeholder_text="Username")
        self.user_entry.pack(pady=12, padx=10)

        # Entry for the password
        self.user_pass = CTkEntry(master=self.master, placeholder_text="Password", show="*")
        self.user_pass.pack(pady=12, padx=10)

        # Entry for confirming the password
        self.confirm_pass = CTkEntry(master=self.master, placeholder_text="Confirm Password", show="*")
        self.confirm_pass.pack(pady=12, padx=10)

        # Entry for the initial deposit
        self.initial_deposit_entry = CTkEntry(master=self.master, placeholder_text="Initial Deposit")
        self.initial_deposit_entry.pack(pady=12, padx=10)

        # Button to suggest and fill in a random password
        suggest_password_button = CTkButton(master=self.master, text='Suggest Password', command=self.suggest_random_password)
        suggest_password_button.pack(pady=12, padx=10)

        # Button to create the account
        create_account_button = CTkButton(master=self.master, text='Create Account', command=self.create_account)
        create_account_button.pack(pady=12, padx=10)

    def suggest_random_password(self):
        # Generate a random password
        random_password = self.generate_random_password()

        # Display the password in a message box and ask the user if they want to use it
        response = messagebox.askyesno("Generated Password",
                                       f"Your auto-generated password is:\n\n{random_password}\n\nDo you want to use this password?")

        if response:
            # Clear the current text in both password entries and set the new password
            self.user_pass.delete(0, "end")
            self.confirm_pass.delete(0, "end")
            self.user_pass.insert(0, random_password)
            self.confirm_pass.insert(0, random_password)

    def generate_random_password(self, length=12):
        """
        Generates a random password with the specified length.
        You can customize this method according to your password requirements.
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def create_account(self):
        # Get user input
        username = self.user_entry.get()
        password = self.user_pass.get()
        confirm_password = self.confirm_pass.get()
        initial_deposit = self.initial_deposit_entry.get()

        # Check if the username already exists
        if self.is_username_exists(username):
            # Suggest a new username
            suggested_username = self.suggest_new_username(username)
            response = messagebox.askyesno("Username Exists",
                                           f"The username '{username}' already exists. Would you like to use the suggested username '{suggested_username}'?")
            if response:
                # Set the suggested username
                self.user_entry.delete(0, "end")
                self.user_entry.insert(0, suggested_username)
            else:
                return  # Stop account creation if the user does not want to use the suggested username

        # Check if the passwords match
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Check if the password matches another user's password
        if self.is_password_used(password):
            # Suggest a new password
            suggested_password = self.generate_random_password()
            response = messagebox.askyesno("Password Used",
                                           f"The password you entered has been used by another user. Would you like to use the suggested password?")
            if response:
                # Set the suggested password
                self.user_pass.delete(0, "end")
                self.confirm_pass.delete(0, "end")
                self.user_pass.insert(0, suggested_password)
                self.confirm_pass.insert(0, suggested_password)
            else:
                return  # Stop account creation if the user does not want to use the suggested password

        try:
            # Hash the password before storing it in the database
            hashed_password = self.hash_password(password)

            # Generate a random account number
            account_number = self.generate_account_number()

            # Validate that initial_deposit is not an empty string before converting to float
            if initial_deposit == '':
                messagebox.showerror("Error", "Please enter an initial deposit amount.")
                return

            # Insert account into the database
            cursor = self.bank_db.conn.cursor()
            # Store the salt and hashed password securely in the database
            cursor.execute(
                "INSERT INTO accounts (account_number, username, password, balance) VALUES (?, ?, ?, ?)",
                (account_number, username, hashed_password, float(initial_deposit))
            )

            # Insert the initial deposit as a transaction
            cursor.execute(
                "INSERT INTO transactions (account_number, amount, description) VALUES (?, ?, ?)",
                (account_number, float(initial_deposit), 'Initial Deposit')
            )

            # Commit changes to the database
            self.bank_db.conn.commit()

            messagebox.showinfo("Account Created", "Account has been successfully created!")

            # Call the login page after creating the account
            self.master.destroy()  # Close the create account page
            login_page = UserLogin()  # Replace 'LoginPage' with the actual name of your login page class
            login_page.master.mainloop()
        except Exception as e:
            print("Database Insert Error:", e)
            messagebox.showerror("Error", "An error occurred during account creation.")

    def is_username_exists(self, username):
        """
        Checks if the given username already exists in the database.
        """
        cursor = self.bank_db.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username=?", (username,))
        return cursor.fetchone() is not None

    def is_password_used(self, password):
        """
        Checks if the given password has been used by another user.
        """
        cursor = self.bank_db.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE password=?", (self.hash_password(password),))
        return cursor.fetchone() is not None

    def suggest_new_username(self, username):
        """
        Suggests a new username by appending a random string to the original username.
        """
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        return f"{username}_{random_suffix}"

    def hash_password(self, password):
        """
        Hashes the password using passlib's bcrypt and returns the hashed password.
        """
        return bcrypt.hash(password)

    def generate_account_number(self):
        """
        Generates a random account number.
        """
        return ''.join(random.choices(string.digits, k=10))

if __name__ == "__main__":
    # Create the main application window
    app = CTk()
    # Create an instance of the CreateAccountPage class, passing the app as the master
    CreateAccountPage(app)
    # Start the Tkinter event loop
    app.mainloop()
