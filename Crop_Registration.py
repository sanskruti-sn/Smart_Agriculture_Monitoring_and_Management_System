from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
from PIL import Image, ImageTk
from datetime import datetime
import os
import pymysql

background = "#004225"
framefg = "white"

root = Tk()
root.title("Crop Registration System")
root.geometry("1250x700+210+10")
root.config(bg=background)

try:
    db = pymysql.connect(host='localhost', user='root', passwd='', db='test')
    cursor = db.cursor()

    # Create 'crop_data' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            crop_name VARCHAR(255),
            fertilizer_name VARCHAR(255),
            planting_date DATE,
            crop_health VARCHAR(50),
            pest_name VARCHAR(255),
            location TEXT,
            farmer_id INT
        )
    ''')

    # Check if 'farmer_id' column exists in the 'crop_data' table
    cursor.execute("SHOW COLUMNS FROM crop_data LIKE 'farmer_id'")
    result = cursor.fetchone()

    if not result:
        # Add 'farmer_id' column to 'crop_data' table
        cursor.execute('ALTER TABLE crop_data ADD COLUMN farmer_id INT')
        db.commit()

    cursor.close()

except pymysql.MySQLError as e:
    messagebox.showerror("Database Error", f"Error connecting to database: {e}")
    root.quit()

# Rest of your functions and GUI code remains unchanged...




def save_crop_data_to_database():
    crop_name = Name.get()
    fertilizer_name = Fertilizer_Name.get()
    planting_date_str = DOP.get()
    crop_health = "Diseased" if radio.get() == 1 else "Healthy" if radio.get() == 2 else "None"
    pest_name = Pest_Name.get()
    location = Location.get("1.0", "end-1c")

    try:
        # Convert the planting date string to a datetime object
        planting_date = datetime.strptime(planting_date_str, "%d/%m/%Y").date()
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please enter the date in the format DD/MM/YYYY.")
        return

    try:
        # Connect to MySQL database
        db = pymysql.connect(host='localhost', user='root', passwd='', db='test')
        cursor = db.cursor()

        cursor.execute('SELECT id FROM farmer ORDER BY id DESC LIMIT 1')
        farmer_id = cursor.fetchone()[0]

        # Save the image file with farmer_id in the file name
        img_filename = f'C:\\python312\\Scripts\\Images\\Crop_Img_{farmer_id}.png'
        img.save(img_filename)

        cursor.execute('''
            INSERT INTO crop_data (crop_name, fertilizer_name, planting_date, crop_health, pest_name, location, farmer_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (crop_name, fertilizer_name, planting_date, crop_health, pest_name, location, farmer_id))
        
        db.commit()
        messagebox.showinfo("Info", "Data entered successfully")
        clear_fields()

    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to database: {e}")

    finally:
        # Close the cursor and database connection
        cursor.close()
        db.close()




def clear_fields():
    Name.set('')
    Fertilizer_Name.set('')
    DOP.set('')
    radio.set(0)
    Pest_Name.set('')
    Location.delete("1.0", END)
    
    # Load and display the default image
    img1 = PhotoImage(file='C:\\python312\\Scripts\\Images\\Crop_Img.png')
    lbl.config(image=img1)
    lbl.image = img1
    
def Submit():
    root.destroy()
    import Crop_Dashboard
    Crop_Dashboard.root.mainloop()

def selection():
    global health
    value = radio.get()
    if value == 1:
        health = "Diseased"
    elif value == 2:
        health = "Healthy"
    else:
        health = "None"

def show_image():
    global filename
    global img
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select image file",filetype=(("JPG File", ".jpg"), ("PNG File", ".png"), ("All files", "*.txt")))
    img = Image.open(filename)
    resized_image = img.resize((199, 190))
    photo2 = ImageTk.PhotoImage(resized_image)
    lbl.config(image=photo2)
    lbl.image = photo2

obj = LabelFrame(root, text="Crop Details", font=20, bd=2, width=900, bg=background, fg=framefg, height=350, relief=GROOVE)
obj.place(x=30, y=100)

Label(obj, text="Crop Name:", font="arial 13", bg=background, fg=framefg).place(x=30, y=30)
Label(obj, text="Fertilizer:", font="arial 13", bg=background, fg=framefg).place(x=30, y=80)
Label(obj, text="Planting Date:", font="arial 13", bg=background, fg=framefg).place(x=30, y=130)
Label(obj, text="Crop Health:", font="arial 13", bg=background, fg=framefg).place(x=30, y=180)

Label(obj, text="Pest Name:", font="arial 13", bg=background, fg=framefg).place(x=480, y=30)
Label(obj, text="Location:", font="arial 13", bg=background, fg=framefg).place(x=480, y=80)

Name = StringVar()
name_entry = Entry(obj, textvariable=Name, width=40, font="arial 10")
name_entry.place(x=160, y=30)

Fertilizer_Name = StringVar()
fertilizer_entry = Entry(obj, textvariable=Fertilizer_Name, width=40, font="arial 10")
fertilizer_entry.place(x=160, y=80)

DOP = StringVar()
plant_date = Entry(obj, textvariable=DOP, width=40, font="arial 10")
plant_date.place(x=160, y=130)

radio = IntVar()
R1 = Radiobutton(obj, text='Diseased', variable=radio, value=1, bg=background, fg=framefg, command=selection)
R1.place(x=160, y=180)
R2 = Radiobutton(obj, text='Healthy', variable=radio, value=2, bg=background, fg=framefg, command=selection)
R2.place(x=240, y=180)
R3 = Radiobutton(obj, text='None', variable=radio, value=3, bg=background, fg=framefg, command=selection)
R3.place(x=320, y=180)

Pest_Name = StringVar()
pest_entry = Entry(obj, textvariable=Pest_Name, width=40, font="arial 10")
pest_entry.place(x=580, y=30)

Location = Text(obj, width=40, height=5, font="Arial 10")
Location.place(x=580, y=80)

f = Frame(root, bd=3, bg="black", width=200, height=200, relief=GROOVE)
f.place(x=1000, y=210)

try:
    original_image_crop = Image.open('C:\\python312\\Scripts\\Images\\Crop_Img.png')
    resized_image_crop = original_image_crop.resize((200, 200), Image.BICUBIC)
    img_crop = ImageTk.PhotoImage(resized_image_crop)
except Exception as e:
    print("Error loading crop image:", e)
    img_crop = None

if img_crop:
    lbl = Label(f, bg="black", image=img_crop)
    lbl.place(x=0, y=0)
else:
    print("Crop image not loaded.")

# Buttons
Button(root, text="Reset", width=19, height=2, font="aerial 12 bold", bg="lightpink", command=clear_fields).place(x=200, y=500)
Button(root, text="Upload", width=19, height=2, font="aerial 12 bold", bg="lightblue", command=show_image).place(x=1000, y=450)
saveButton = Button(root, text="Save", width=19, height=2, font="aerial 12 bold", bg="lightgreen", command=save_crop_data_to_database)
saveButton.place(x=425, y=500)
Button(root, text="Next Page", width=19, height=2, font="aerial 12 bold", bg="khaki", command=Submit).place(x=650, y=500)

root.mainloop()