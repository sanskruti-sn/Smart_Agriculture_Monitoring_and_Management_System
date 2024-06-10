from tkinter import *
from tkinter import messagebox
import pymysql

def register():
    username = user.get()
    password = code.get()
    admincode = adminaccess.get()

    if admincode == "8605":
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

                # Create database and table if not exists
                cursor.execute("CREATE DATABASE IF NOT EXISTS FarmerRegistration")
                cursor.execute("USE FarmerRegistration")
                cursor.execute("CREATE TABLE IF NOT EXISTS signup (user INT AUTO_INCREMENT PRIMARY KEY, Username VARCHAR(50), Password VARCHAR(100))")

                # Insert new user
                insert_query = "INSERT INTO signup (Username, Password) VALUES (%s, %s)"
                cursor.execute(insert_query, (username, password))
                db_connection.commit()
                db_connection.close()

                messagebox.showinfo("Register", "New User added successfully!!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Admin code!", "Input Correct Admin code to add new user!!")


def login():
    root.destroy()
    import login


background = "#06283D"
framebg = "#EDEDED"
framefg = "#06283D"

root = Tk()
root.title("New User Registration")
root.geometry("1250x700+210+100")
root.config(bg=background)
root.resizable(False, False)

image_icon = PhotoImage(file="C:\\python312\\Scripts\\Images\\user_key.png")
root.iconphoto(False, image_icon)

frame = Frame(root, bg="red")
frame.pack(fill=Y)

backgroundimage = PhotoImage(file="C:\\python312\\Scripts\\Images\\Sign_in_UI.jpg")
Label(frame, image=backgroundimage).pack()

adminaccess = Entry(frame, width=15, fg="#000", border=0, bg="#e8ecf7", font=("Arial Bold", 20), show="*")
adminaccess.focus()
adminaccess.place(x=550, y=280)

user = Entry(frame, width=18, fg="#fff", bg="#375174", border=0, font=("Arial Bold", 20))
user.insert(0, "UserID")
user.place(x=500, y=380)

code = Entry(frame, width=18, fg="#fff", bg="#375174", border=0, font=("Arial Bold", 20))
code.insert(0, "Password")
code.place(x=500, y=470)

button_mode = True

def hide():
    global button_mode

    if button_mode:
        eyeButton.config(image=closeeye, activebackground="white")
        code.config(show="*")
        button_mode = False
    else:
        eyeButton.config(image=openeye, activebackground="white")
        code.config(show="")
        button_mode = True

openeye = PhotoImage(file="C:\\python312\\Scripts\\Images\\open_eye.jpg")
closeeye = PhotoImage(file="C:\\python312\\Scripts\\Images\\eye.jpg")

eyeButton = Button(root, image=openeye, bg="#375174", bd=0, command=hide)
eyeButton.place(x=780, y=470)

regis_button = Button(root, text="ADD NEW USER", bg="#455c88", fg="white", width=13, height=1,
                      font=("Arial", 16, "bold"), bd=0, command=register)
regis_button.place(x=530, y=600)

backbuttonimage = PhotoImage(file="C:\\python312\\Scripts\\Images\\back.jpg")
Backbutton = Button(root, image=backbuttonimage, fg="#deeefb", command=login)
Backbutton.place(x=20, y=15)

root.mainloop()
