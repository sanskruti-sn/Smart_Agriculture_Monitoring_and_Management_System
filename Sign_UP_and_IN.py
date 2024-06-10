from tkinter import *
from tkinter import messagebox
import pymysql

background = "#06283D"
framebg = "#EDEDED"
framefg = "#06283D"

global trial_no
trial_no = 0

def trial():
    global trial_no
    trial_no += 1
    print("Trial no is ", trial_no)
    if trial_no == 3:
        messagebox.showwarning("Warning", "You have tried more than the limit!!")
        root.destroy()  # Program close

def loginuser():
    username = user.get()
    password = code.get()

    if (username == "" or username == "UserID") or (password == "" or password == "Password"):
        messagebox.showerror("Entry error", "Type username or password!!")
    else:
        try:
            db = pymysql.connect(host='localhost', passwd='', user='root', db='test')
            cursor = db.cursor()
            print("Connected to Database!!")
        except:
            messagebox.showerror("Connection", "Database connection not established!!")
            return

        command = "SELECT * FROM farmer_signUp WHERE Username=%s AND Password=%s"
        cursor.execute(command, (username, password))
        result = cursor.fetchone()

        if result == None:
            messagebox.showinfo("Invalid", "Invalid userid and password")
            # Password cannot be incorrect more than 3 times
            trial()
        else:
            messagebox.showinfo("Login", "Successfully login")

def register_user():
    username = user.get()
    password = code.get()

    if username == "UserID" or password == "Password":
        messagebox.showerror("Entry error!", "Type username or password !!!")
    else:
        try:
            # Connect to MySQL
            db_connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="test",
                port=3306
            )
            cursor = db_connection.cursor()

            # Create table if not exists
            cursor.execute("CREATE TABLE IF NOT EXISTS farmer_signUp (id INT AUTO_INCREMENT PRIMARY KEY, Username VARCHAR(50), Password VARCHAR(100))")

            # Insert new user
            insert_query = "INSERT INTO farmer_signUp (Username, Password) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, password))
            db_connection.commit()

            db_connection.close()

            messagebox.showinfo("Register", "New User added successfully!!")
            root.destroy()  # Close the registration window after successful registration
            import Farmer_Login  # Import and open the login window
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = Tk()
root.title("Login System")
root.geometry("890x500+210+10")
root.config(bg=background)
root.resizable(False, False)

# icon image
image_icon = PhotoImage(file="C:\\python312\\Scripts\\Images\\user_key.png")
root.iconphoto(False, image_icon)

# background image
frame = Frame(root, bg="red")
frame.pack(fill=Y)

backgroundimage = PhotoImage(file="C:\\python312\\Scripts\\Images\\Sign_IN_UI.png")
Label(frame, image=backgroundimage).pack()

def user_enter(e):
    user.delete(0, 'end')

def user_leave(e):
    name = user.get()
    if name == '':
        user.insert(0, 'UserID')

user = Entry(frame, width=10, fg="#fff", border=0, bg="#375174", font=('Arial Bold', 24))
user.insert(0, 'UserID')
user.bind("<FocusIn>", user_enter)
user.bind("<FocusOut>", user_leave)
user.place(x=370, y=215)

def password_enter(e):
    code.delete(0, 'end')

def password_leave(e):
    if code.get() == '':
        code.insert(0, 'Password')

code = Entry(frame, width=10, fg="#fff", border=0, bg="#375174", font=('Arial Bold', 24))
code.insert(0, 'Password')
code.bind("<FocusIn>", password_enter)
code.bind("<FocusOut>", password_leave)
code.place(x=370, y=285)

openeye = PhotoImage(file="C:\\python312\\Scripts\\Images\\open_eye.png").subsample(15, 15)
closeeye = PhotoImage(file="C:\\python312\\Scripts\\Images\\eye.png").subsample(15, 15)
eyeButton = Button(frame, image=openeye, bg="#375174", bd=0, command=hide)
eyeButton.place(x=540, y=285)

loginButton = Button(root, text="LOGIN", bg="#1f5675", fg="white", width=10, height=1, font=("arial", 16, 'bold'), bd=0, command=loginuser)
loginButton.place(x=370, y=420)

Label(root, text="Don't have an account?", fg="#fff", bg="#00264d", font=('Microsoft YaHei UI Light', 9)).place(x=300, y=473)

registerButton = Button(root, width=10, text="add new user", border=0, bg="#00264d", cursor='hand2', fg="#57a1f8", command=register_user)
registerButton.place(x=450, y=473)

root.mainloop()
