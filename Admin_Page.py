# Import necessary modules
import sqlite3
from tkinter import messagebox
import bcrypt
import customtkinter as ctk
import tkinter as tk

# Sets the appearance of the window
ctk.set_appearance_mode("System")

# Sets the color of the widgets in the window
ctk.set_default_color_theme("green")

# Dimensions of the window
appWidth, appHeight = 600, 300

# AdminPage class for handling admin actions
class AdminPage:
    def __init__(self, db_file="bank_database.db"):
        # Initialize your database connection here
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # Create necessary tables if they don't exist
        self.create_tables()

    def create_tables(self):
        # Create the 'users' table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                username TEXT,
                salt TEXT,
                hashed_password TEXT,
                balance REAL
            )
        ''')

        # Create the 'transactions' table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Commit the changes to the database
        self.conn.commit()

    # Function to remove user

# App class for the main application window
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ADMIN HOMEPAGE")
        self.geometry(f"{appWidth}x{appHeight}")

        # Entry widget for user input
        self.accountNumberEntry = ctk.CTkEntry(self)
        self.accountNumberEntry.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # Button for removing user
        self.removeUserButton = ctk.CTkButton(self, text="Remove User", command=self.remove_user_button_click)
        self.removeUserButton.grid(row=4, column=1, padx=20, pady=20, sticky="ew")



        # View All Users Button
        self.viewAllUsersButton = ctk.CTkButton(self, text="View All Users", command=self.view_all_users_button_click)
        self.viewAllUsersButton.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.logoutButton = ctk.CTkButton(self, text="Logout", command=self.logout_button_click)
        self.logoutButton.grid(row=6, column=2, padx=20, pady=20, sticky="ew")

        # Text Box
        self.displayBox = ctk.CTkTextbox(self, width=200, height=100)
        self.displayBox.grid(row=7, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")

    def remove_user(self, account_number):
        # Implement database removal logic here
        messagebox.showinfo("User Removed", f"User with account number {account_number} has been removed successfully.")

        # Function to view all users

    def view_all_users_button_click(self):
        # Connect to the database and fetch all users
        users = admin_page.get_all_users()

        # Display the fetched users in the textbox
        self.displayBox.delete("1.0", "end")  # clear existing text
        for user in users:
            user_info = f"Username: {user[1]}, Account Number: {user[4]}, Balance: R{user[3]}\n"
            self.displayBox.insert("end", user_info)

        # Optionally, show a message box if there are no users
        if not users:
            messagebox.showinfo("No Users", "There are no users in the database.")
            quit()


    def remove_user_button_click(self):
        # Get the account number from the entry widget
        account_number = self.accountNumberEntry.get()

        # Check if the user entered a valid account number
        if account_number.strip() != "":
            admin_page.remove_user(account_number)
        else:
            # Show an error message in a message box
            messagebox.showerror("Error", "Invalid account number. Please try again.")


    def logout_button_click(self):
        # Display a confirmation message box
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            # Implement the link to the homepage here (for example, show a message)
            messagebox.showinfo("Logged Out", "You have been logged out. Redirecting to the homepage...")
            open.admin_page()
    def mainloop(self):
        super().mainloop()

# Main entry point
if __name__ == "__main__":
    app = App()
    admin_page = AdminPage()
    app.mainloop()
