import datetime
import os
import sqlite3
from tkinter import messagebox
from reportlab.pdfgen import canvas
import customtkinter as ctk
from PIL import Image, ImageTk

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BankDatabase:
    def __init__(self, db_name="bank_database.db"):
        try:
            # Establish a connection to the SQLite database
            self.conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
            self.conn.row_factory = sqlite3.Row  # Set row_factory for named columns
            self.cursor = self.conn.cursor()
            # Create necessary tables if they don't exist
            self.create_tables()
        except sqlite3.Error as e:
            print("Database connection error:", e)

    def create_tables(self):
        # Create necessary tables if they don't exist
        self.cursor.execute(
            """ CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                username TEXT,
                salt TEXT,
                hashed_password TEXT,
                balance REAL
            )"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS transactions
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, transaction_type TEXT, 
                              amount REAL, transaction_time DATETIME)"""
        )

        self.conn.commit()

    def user_deposit(self, user, amount):
        if amount >= 10 and amount % 10 == 0:
            try:
                # Calculate the new balance after deposit
                user_balance = user["balance"] + amount

                # Update user's balance in the database
                self.cursor.execute(
                    "UPDATE accounts SET balance=? WHERE account_number=?",
                    (user_balance, user["username"]),
                )

                # Get the current timestamp for the transaction
                transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert the deposit transaction into the transactions table
                self.cursor.execute(
                    "INSERT INTO transactions (account_number, transaction_type, amount, transaction_time) VALUES (?, ?, ?, ?)",
                    (user["username"], "Deposit", amount, transaction_time),
                )
                self.conn.commit()

                # Fetch the updated balance from the database
                self.cursor.execute(
                    "SELECT balance FROM accounts WHERE account_number=?",
                    (user["username"],),
                )
                updated_balance = self.cursor.fetchone()[0]

                return amount, updated_balance
            except sqlite3.Error as e:
                # Handle database error and return an error message
                print("Database error:", e)
                return "An error occurred while processing the deposit. Please try again later."
        else:
            # Return an error message for invalid deposit amount
            return "Invalid deposit amount. Please enter an amount above or equal to 10 and in multiples of 10."

    def user_withdraw(self, user, amount):
        if amount >= 60 and amount % 10 == 0:
            try:
                # Fetch the user's current balance from the database
                self.cursor.execute(
                    "SELECT balance FROM accounts WHERE account_number=?",
                    (user["username"],)
                )
                user_balance = self.cursor.fetchone()[0]

                # Check if the user has sufficient balance for the withdrawal
                if user_balance >= amount:
                    # Calculate the new balance after withdrawal
                    new_balance = user_balance - amount

                    # Update user's balance in the database
                    self.cursor.execute(
                        "UPDATE accounts SET balance=? WHERE account_number=?",
                        (new_balance, user["username"])
                    )

                    # Get the current timestamp for the transaction
                    transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Insert the withdrawal transaction into the transactions table
                    self.cursor.execute(
                        "INSERT INTO transactions (account_number, transaction_type, amount, transaction_time) VALUES (?, ?, ?, ?)",
                        (user["username"], "Withdrawal", amount, transaction_time)
                    )
                    self.conn.commit()

                    # Log the withdrawal transaction
                    self.log_transaction(
                        user["account_number"], "Withdrawal", amount, new_balance
                    )

                    # Fetch the updated balance from the database
                    self.cursor.execute(
                        "SELECT balance FROM accounts WHERE account_number=?",
                        (user["username"],)
                    )
                    updated_balance = self.cursor.fetchone()[0]

                    return amount, updated_balance
                else:
                    # Return an error message for insufficient balance
                    return "Insufficient balance for withdrawal."
            except sqlite3.Error as e:
                # Handle database error and return an error message
                print("Database error:", e)
                return "An error occurred while processing the withdrawal. Please try again later."
        else:
            # Return an error message for invalid withdrawal amount
            return "Invalid withdrawal amount. Please enter an amount above 50 and in multiples of 10."

    def log_transaction(self, username, transaction_type, amount, new_balance):
        # Placeholder for logging the transaction; replace with actual logic
        pass

    def close_connection(self):
        # Close the database connection
        self.conn.close()


class MainInterface:
    def __init__(self, master):
        self.master = master
        self.bank_db = BankDatabase()  # Initialize BankDatabase
        self.user = None  # Placeholder for storing user details after login
        master.geometry("500x700")
        master.title("MAIN PAGE")

        frame = ctk.CTkFrame(master=master)
        frame.pack(pady=20, padx=40, fill='both', expand=True)

        # Load and display an image
        try:
            image = Image.open(r"C:\Users\molel\PycharmProjects\BANK & CALCULATOR APP\home.png")
            image = image.resize((150, 150))  # Adjust the size as needed
            photo = ImageTk.PhotoImage(image)
            image_label = ctk.CTkLabel(master=frame, image=photo)
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.pack(pady=12, padx=10)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image 'home.png' not found. Please provide the correct path.")

        label = ctk.CTkLabel(master=frame, text='Welcome to 5 Stars LocalBank')
        label.pack(pady=12, padx=10)

        # Entry widget for deposit amount
        deposit_amount_label = ctk.CTkLabel(master=frame, text='Enter Deposit Amount:')
        deposit_amount_label.pack(pady=5, padx=10)
        self.deposit_amount_entry = ctk.CTkEntry(master=frame)
        self.deposit_amount_entry.pack(pady=5, padx=10)

        # Create the deposit button
        button_deposit = ctk.CTkButton(master=frame, text='Deposit', command=self.make_deposit)
        button_deposit.pack(pady=12, padx=10)

        # Entry widget for withdrawal amount
        withdraw_amount_label = ctk.CTkLabel(master=frame, text='Enter Withdrawal Amount:')
        withdraw_amount_label.pack(pady=5, padx=10)
        self.withdraw_amount_entry = ctk.CTkEntry(master=frame)
        self.withdraw_amount_entry.pack(pady=5, padx=10)

        # Create the withdrawal button
        button_withdrawal = ctk.CTkButton(master=frame, text='Withdrawal', command=self.make_withdrawal)
        button_withdrawal.pack(pady=12, padx=10)

        # Create the check balance button
        button_check_balance = ctk.CTkButton(master=frame, text='Check Balance', command=self.view_balance)
        button_check_balance.pack(pady=12, padx=10)

        # Create the print statement button
        button_print_statement = ctk.CTkButton(master=frame, text='Print Statement', command=self.print_statement)
        button_print_statement.pack(pady=12, padx=10)

    def login(self, username, password):
        # Placeholder for login logic; replace with actual logic
        pass

    def make_deposit(self):
        if self.user:
            # Get the deposit amount from the entry widget
            deposit_amount_str = self.deposit_amount_entry.get()

            # Validate and convert the deposit amount to float
            try:
                deposit_amount = float(deposit_amount_str)
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid numeric amount.")
                return

            # Perform deposit
            deposit_result = self.bank_db.user_deposit(self.user, deposit_amount)

            # Handle the deposit result
            if isinstance(deposit_result, tuple):
                # Deposit successful
                deposited_amount, updated_balance = deposit_result
                message = f"Deposited: R{deposited_amount}\nCurrent Balance: R{updated_balance}"
                messagebox.showinfo("Deposit Successful", message)
            elif isinstance(deposit_result, str):
                # Display error message for invalid deposit amount
                messagebox.showerror("Invalid Deposit", deposit_result)
        else:
            messagebox.showerror("Login Required", "Please log in before making a transaction.")

    def make_withdrawal(self):
        if self.user:
            # Get the withdrawal amount from the entry widget
            withdraw_amount_str = self.withdraw_amount_entry.get()

            # Validate and convert the withdrawal amount to float
            try:
                withdraw_amount = float(withdraw_amount_str)
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid numeric amount.")
                return

            # Perform withdrawal
            withdrawal_result = self.bank_db.user_withdraw(self.user, withdraw_amount)

            # Handle the withdrawal result
            if isinstance(withdrawal_result, tuple):
                # Withdrawal successful
                withdrawn_amount, updated_balance = withdrawal_result
                message = f"Withdrawn: R{withdrawn_amount}\nCurrent Balance: R{updated_balance}"
                messagebox.showinfo("Withdrawal Successful", message)
            elif isinstance(withdrawal_result, str):
                # Display error message for insufficient balance
                messagebox.showerror("Insufficient Balance", withdrawal_result)
        else:
            messagebox.showerror("Login Required", "Please log in before making a transaction.")

    def view_balance(self):
        if self.user:
            try:
                # Fetch the user's current balance from the database
                self.bank_db.cursor.execute(
                    "SELECT balance FROM accounts WHERE account_number=?",
                    (self.user["username"],)
                )
                user_balance = self.bank_db.cursor.fetchone()[0]

                # Display the user's current balance
                message = f"Current Balance: R{user_balance}"
                messagebox.showinfo("Balance Inquiry", message)
            except sqlite3.Error as e:
                # Handle database error and display an error message

                messagebox.showerror("Error", "An error occurred while fetching the balance. Please try again later.")
        else:
            messagebox.showerror("Login Required", "Please log in to check your balance.")

    def print_statement(self):
        if self.user:
            try:
                # Fetch the user's transaction history from the database
                self.bank_db.cursor.execute(
                    "SELECT * FROM transactions WHERE account_number=?",
                    (self.user["username"],)
                )
                transactions = self.bank_db.cursor.fetchall()

                if transactions:
                    # Create a PDF file with the user's transaction history
                    pdf_filename = f"{self.user['account_number']}_transaction_statement.pdf"
                    with canvas.Canvas(pdf_filename) as pdf:
                        pdf.setFont("Helvetica", 12)
                        pdf.drawString(30, 800, "Transaction Statement:")
                        y_position = 780
                        for transaction in transactions:
                            y_position -= 20
                            pdf.drawString(30, y_position, f"Transaction ID: {transaction['id']}")
                            pdf.drawString(30, y_position - 15, f"Transaction Type: {transaction['transaction_type']}")
                            pdf.drawString(30, y_position - 30, f"Amount: R{transaction['amount']}")
                            pdf.drawString(30, y_position - 45, f"Transaction Time: {transaction['transaction_time']}")
                            pdf.drawString(30, y_position - 60, "-" * 60)  # Separator line

                    # Display a message box with options for the user
                    result = messagebox.askquestion(
                        "Transaction Statement",
                        "Transaction statement generated successfully!\nDo you want to:\n1. View on screen\n2. Download PDF"
                    )

                    if result == 'yes':
                        # Option 1: View on screen
                        messagebox.showinfo("Transaction Statement", "Opening PDF on screen.")
                        os.startfile(pdf_filename, "open")
                    else:
                        # Option 2: Download PDF
                        messagebox.showinfo("Transaction Statement", f"PDF saved as {pdf_filename}.")
                else:
                    # Print message for no transactions
                    messagebox.showinfo("Transaction Statement", "No transactions available.")

            except sqlite3.Error as e:
                # Handle database error and print error message
                print("Database error:", e)
                messagebox.showerror("Error", "An error occurred while fetching the transaction statement. Please try again later.")
        else:
            messagebox.showerror("Login Required", "Please log in to view your transaction statement.")


if __name__ == "__main__":
    root = ctk.CTk()
    main_interface = MainInterface(root)
    root.mainloop()
