import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import requests
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
import operator


class SmartAgriDashboard:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Smart Agriculture Dashboard")
        self.root.geometry("1300x800+200+10")
        self.username = username
        self.db = pymysql.connect(host='localhost', user='root', passwd='', db='test')
        self.cursor = self.db.cursor()
        

        # Create a frame for the navbar
        self.navbar_frame = tk.Frame(root, width=200, bg='lightgray')
        self.navbar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Initialize ttk.Notebook widget
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Call methods to create tabs
        
        self.create_pests_tab()
        self.create_fertilizer_tab()        
        self.create_market_tab()
        self.create_irrigation_tab()
        self.create_harvest_tab()
        self.create_crop_health_tab()
        self.create_weather_tab()
        self.create_sensors_tab()
        self.create_profile_tab()
        
        

        # Add image section
        self.canvas = tk.Canvas(self.navbar_frame, width=200, height=200, bg='lightgray', highlightthickness=0)
        self.canvas.pack()

        # Load and resize image using PIL
        image_path = f"C:\\python312\\Scripts\\Images\\Profile_Img_{self.get_id()}.png"
        original_image = Image.open(image_path)
        
        # Calculate aspect ratio
        aspect_ratio = original_image.width / original_image.height
        
        # Calculate new dimensions
        if aspect_ratio > 1:
            new_width = 200
            new_height = int(200 / aspect_ratio)
        else:
            new_height = 200
            new_width = int(200 * aspect_ratio)
        
        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert PIL Image to Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(100, 110, image=self.image)

        # Create a label for farmer's name
        self.farmer_name_label = tk.Label(self.navbar_frame, text=self.get_farmer_name(), font=("Arial", 16))
        self.farmer_name_label.pack(pady=10)
        

    def get_id(self):
        try:
            self.cursor.execute("SELECT id FROM farmer_signUp WHERE Username=%s", (self.username,))
            user_id = self.cursor.fetchone()[0]
            return user_id
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching ID from database: {e}")

    def get_farmer_name(self):
        try:
            farmer_id = self.get_id()
            self.cursor.execute("SELECT name FROM farmer WHERE id=%s", (farmer_id,))
            full_name = self.cursor.fetchone()[0]
            return full_name
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching name from database: {e}")
            
    def create_pests_tab(self):
        pests_tab = ttk.Frame(self.notebook)
        self.notebook.add(pests_tab, text="Pests")

        # Create labels and entry fields for pest attributes
        fields = ["Pest Name", "Description", "Control Methods"]
        self.pests_entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(pests_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            if field == "Pest Name":
                # Fetch pest names based on farmer ID from crop_data table
                try:
                    farmer_id = self.get_id()  # Replace 1 with the actual farmer ID
                    self.cursor.execute("SELECT DISTINCT pest_name FROM crop_data WHERE farmer_id = %s", (farmer_id,))
                    pest_names = [row[0] for row in self.cursor.fetchall()]
                except pymysql.Error as e:
                    messagebox.showerror("Error", f"Error fetching pest names: {e}")
                    pest_names = []

                # Populate dropdown with pest names if available
                if pest_names:
                    self.pests_entries[field] = tk.StringVar()
                    dropdown = ttk.Combobox(pests_tab, textvariable=self.pests_entries[field], values=pest_names)
                    dropdown.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
                    dropdown.current(0)  # Set default selection
                else:
                    tk.Label(pests_tab, text="No pest names available").grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)

            else:
                entry = tk.Entry(pests_tab)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
                self.pests_entries[field] = entry

        # Button to save pest data
        save_button = tk.Button(pests_tab, text="Save Pest Data", command=self.save_pest_data)
        save_button.grid(row=len(fields), columnspan=2, padx=10, pady=10)


    def save_pest_data(self):
        try:
            # Retrieve and validate data from entry widgets
            pest_name = self.pests_entries["Pest Name"].get().strip()
            description = self.pests_entries["Description"].get().strip()
            control_methods = self.pests_entries["Control Methods"].get().strip()

            # Insert into the pests table
            farmer_id = 1  # Replace 1 with the actual farmer ID
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    farmer_id INT,
                    pest_name VARCHAR(255),
                    description TEXT,
                    control_methods TEXT
                )
            """)
            self.cursor.execute("""
                INSERT INTO pests (farmer_id, pest_name, description, control_methods)
                VALUES (%s, %s, %s, %s)
            """, (farmer_id, pest_name, description, control_methods))

            self.db.commit()

            messagebox.showinfo("Success", "Pest data saved successfully")

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error saving pest data: {e}")

        
    def create_fertilizer_tab(self):
        fertilizer_tab = ttk.Frame(self.notebook)
        self.notebook.add(fertilizer_tab, text="Fertilizer")

        # Create the fertilizer table if it doesn't exist
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS fertilizer (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fertilizer_name VARCHAR(255),
                    description TEXT,
                    application_rate FLOAT,
                    application_schedule VARCHAR(255)
                )
            """)
            self.db.commit()
        except pymysql.Error as e:
            messagebox.showerror("Error", f"Error creating fertilizer table: {e}")
            self.db.rollback()

        fields = ["Fertilizer Name", "Description", "Application Rate", "Application Schedule"]

        self.fertilizer_entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(fertilizer_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            if field == "Fertilizer Name":
                # Fetch fertilizer names based on farmer ID from crop_data table
                try:
                    farmer_id = self.get_id()
                    self.cursor.execute("SELECT DISTINCT fertilizer_name FROM crop_data WHERE farmer_id = %s", (farmer_id,))
                    fertilizer_names = [row[0] for row in self.cursor.fetchall()]
                except pymysql.Error as e:
                    messagebox.showerror("Error", f"Error fetching fertilizer names: {e}")
                    fertilizer_names = []

                # Populate dropdown with fertilizer names if available
                if fertilizer_names:
                    self.fertilizer_entries[field] = tk.StringVar()
                    dropdown = ttk.Combobox(fertilizer_tab, textvariable=self.fertilizer_entries[field], values=fertilizer_names)
                    dropdown.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
                    dropdown.current(0)  # Set default selection
                else:
                    tk.Label(fertilizer_tab, text="No fertilizer names available").grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)

            else:
                entry = tk.Entry(fertilizer_tab)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
                self.fertilizer_entries[field] = entry

        # Button to save fertilizer data
        save_button = tk.Button(fertilizer_tab, text="Save Fertilizer Data", command=self.save_fertilizer_data)
        save_button.grid(row=len(fields), columnspan=2, padx=10, pady=10)


    def save_fertilizer_data(self):
        try:
            # Retrieve and validate data from entry widgets
            fertilizer_name = self.fertilizer_entries["Fertilizer Name"].get().strip()
            description = self.fertilizer_entries["Description"].get().strip()
            application_rate = float(self.fertilizer_entries["Application Rate"].get().strip())
            application_schedule = self.fertilizer_entries["Application Schedule"].get().strip()

            # Insert into the fertilizer table
            self.cursor.execute("""
                INSERT INTO fertilizer (fertilizer_name, description, application_rate, application_schedule)
                VALUES (%s, %s, %s, %s)
            """, (fertilizer_name, description, application_rate, application_schedule))

            self.db.commit()

            messagebox.showinfo("Success", "Fertilizer data saved successfully")

        except ValueError:
            messagebox.showerror("Error", "Invalid input for application rate. Please enter a valid number.")

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error saving fertilizer data: {e}")

            
    def get_crop_name(self, farmer_id):
        try:
            self.cursor.execute("SELECT crop_name FROM crop_data WHERE farmer_id=%s", (farmer_id,))
            crop_name = self.cursor.fetchone()[0]
            return crop_name
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching crop name from database: {e}")



    def create_weather_tab(self):
        weather_tab = ttk.Frame(self.notebook)
        self.notebook.add(weather_tab, text="Weather Data")

        fields = ["Weather ID", "Location", "Date", "Temperature", "Humidity", "Precipitation"]

        for i, field in enumerate(fields):
            label = tk.Label(weather_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            if field == "Weather ID":
                # Assign weather ID equal to farmer ID
                weather_id = self.get_id()
                entry = tk.Entry(weather_tab)
                entry.insert(tk.END, weather_id)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            elif field == "Location":
                # Fetch location based on the last 2 words of the farm location
                location = self.get_location()  # Implement this method
                entry = tk.Entry(weather_tab)
                entry.insert(tk.END, location)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            elif field == "Date":
                # Fetch current date
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                entry = tk.Entry(weather_tab)
                entry.insert(tk.END, date)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            else:
                # Fetch live weather data
                weather_data = self.fetch_weather_data()  # Implement this method
                if weather_data:
                    if field == "Temperature":
                        entry = tk.Entry(weather_tab)
                        entry.insert(tk.END, weather_data["temp"])
                        entry.config(state='readonly')
                        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
                    elif field == "Humidity":
                        entry = tk.Entry(weather_tab)
                        entry.insert(tk.END, weather_data["humidity"])
                        entry.config(state='readonly')
                        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
                    elif field == "Precipitation":
                        entry = tk.Entry(weather_tab)
                        entry.insert(tk.END, weather_data["precipitation"])
                        entry.config(state='readonly')
                        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)


    def get_location(self):
        try:
            # Retrieve location from the database based on farmer_id
            self.cursor.execute("SELECT location FROM crop_data WHERE farmer_id=%s", (self.get_id(),))
            farm_location = self.cursor.fetchone()[0]
            
            # Extract last 2 words from the location
            last_two_words = ' '.join(farm_location.split()[-2:])
            
            return last_two_words
            
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching location from database: {e}")


    def fetch_weather_data(self):
        # Fetch live weather data from OpenWeatherMap API
        api_key = "62b934dca93073f94706fd1b7e9a4106"  # Your API key
        location = self.get_location()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "precipitation": data["weather"][0]["description"]
            }
            return weather_data
        else:
            messagebox.showerror("Error", "Failed to fetch weather data")
            return None



    def create_market_tab(self):
        market_tab = ttk.Frame(self.notebook)
        self.notebook.add(market_tab, text="Market Prices")

        # Check if the market table exists, if not, create it
        try:
            self.cursor.execute("SELECT 1 FROM market LIMIT 1")
        except pymysql.Error:
            # Create the market table if it doesn't exist
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS market (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        crop_name VARCHAR(255),
                        market_price FLOAT,
                        date DATE
                    )
                """)
                self.db.commit()
            except pymysql.Error as e:
                messagebox.showerror("Error", f"Error creating market table: {e}")
                self.db.rollback()

        fields = ["Crop Name", "Market Price", "Date"]

        self.market_entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(market_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            entry = tk.Entry(market_tab)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
            self.market_entries[field] = entry

        # Button to save market data
        save_button = tk.Button(market_tab, text="Save Market Data", command=self.save_market_price)
        save_button.grid(row=len(fields), columnspan=2, padx=10, pady=10)


    def save_market_price(self):
        try:
            # Retrieve and validate data from entry widgets
            crop_name = self.market_entries["Crop Name"].get().strip()
            market_price_str = self.market_entries["Market Price"].get().strip()
            date_str = self.market_entries["Date"].get().strip()

            if not crop_name or not market_price_str or not date_str:
                raise ValueError("All fields are required")

            market_price = float(market_price_str)  # Convert to float
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert to date

            # Insert into the market table
            self.cursor.execute("""
                INSERT INTO market (crop_name, market_price, date)
                VALUES (%s, %s, %s)
            """, (crop_name, market_price, date))

            self.db.commit()

            messagebox.showinfo("Success", "Market price data stored successfully")

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))  # Handle invalid input data
            self.db.rollback()  # Rollback if there's an error

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error storing market price data: {e}")

    def create_irrigation_tab(self):
        irrigation_tab = ttk.Frame(self.notebook)
        self.notebook.add(irrigation_tab, text="Irrigation")

        # Fields for the tab
        fields = ["Irrigation ID", "Location", "Type", "Status"]
        self.irrigation_entries = {}

        # Create entry fields for Irrigation ID and Location
        for i, field in enumerate(fields[:2]):
            label = tk.Label(irrigation_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            entry = tk.Entry(irrigation_tab)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
            self.irrigation_entries[field] = entry

        # Create drop-down for Type with sample values
        label = tk.Label(irrigation_tab, text="Type")
        label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        type_options = ["Drip", "Sprinkler", "Surface"]
        type_combobox = ttk.Combobox(irrigation_tab, values=type_options, state="readonly")
        type_combobox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
        self.irrigation_entries["Type"] = type_combobox

        # Create drop-down for Status with predefined values
        label = tk.Label(irrigation_tab, text="Status")
        label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)

        status_options = ["In Use", "Planted", "Idle"]
        status_combobox = ttk.Combobox(irrigation_tab, values=status_options, state="readonly")
        status_combobox.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W + tk.E)
        self.irrigation_entries["Status"] = status_combobox

        # Button to save the irrigation record
        save_button = tk.Button(irrigation_tab, text="Save Irrigation", command=self.save_irrigation_record)
        save_button.grid(row=4, columnspan=2, padx=10, pady=10)

        # Check if the irrigation table exists, if not, create it
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS irrigation (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    irrigation_id VARCHAR(255) UNIQUE,
                    location VARCHAR(255),
                    type VARCHAR(50),
                    status VARCHAR(50)
                )
            """)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error creating irrigation table: {e}")


    def save_irrigation_record(self):
        try:
            # Retrieve data from entry widgets
            irrigation_id = self.irrigation_entries["Irrigation ID"].get().strip()
            location = self.irrigation_entries["Location"].get().strip()
            irrigation_type = self.irrigation_entries["Type"].get()
            status = self.irrigation_entries["Status"].get()

            # Ensure all fields are provided
            if not irrigation_id or not location or not irrigation_type or not status:
                raise ValueError("All fields are required")

            # Insert into the irrigation table
            self.cursor.execute("""
                INSERT INTO irrigation (irrigation_id, location, type, status)
                VALUES (%s, %s, %s, %s)
            """, (irrigation_id, location, irrigation_type, status))

            self.db.commit()
            messagebox.showinfo("Success", "Irrigation record stored successfully")

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))  # Handle invalid input
            self.db.rollback()  # Rollback if there's an error

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error storing irrigation record: {e}")



    
    def create_harvest_tab(self):
        # Create the tab
        harvest_tab = ttk.Frame(self.notebook)
        self.notebook.add(harvest_tab, text="Harvest Records")

        # Create table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS harvest (
                id INT AUTO_INCREMENT PRIMARY KEY,
                harvest_id VARCHAR(255),
                crop_id INT,
                farmer_id INT,
                quantity_harvested FLOAT,
                date DATE,
                time TIME
            )
        """)
        self.db.commit()

        # Add entry fields to the tab
        fields = ["Quantity Harvested", "Date", "Time"]
        self.entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(harvest_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            entry = tk.Entry(harvest_tab)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
            self.entries[field] = entry

        # Add a button to save the harvest record
        save_button = tk.Button(harvest_tab, text="Save Harvest", command=self.save_harvest_record)
        save_button.grid(row=len(fields), columnspan=2, padx=10, pady=10)

    def save_harvest_record(self):
        try:
            # Retrieve and validate data from entry widgets
            date_str = self.entries["Date"].get().strip()
            time_str = self.entries["Time"].get().strip()
            quantity_str = self.entries["Quantity Harvested"].get().strip()

            if not date_str or not time_str or not quantity_str:
                raise ValueError("All fields are required")

            # Convert to correct formats
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.datetime.strptime(time_str, "%H:%M").time()
            quantity_harvested = float(quantity_str)

            # Get Farmer ID
            self.cursor.execute("SELECT id FROM farmer_signUp WHERE Username=%s", (self.username,))
            farmer_id = self.cursor.fetchone()

            if farmer_id is None:
                raise ValueError("Farmer ID not found")

            farmer_id = farmer_id[0]

            # Get Crop ID
            self.cursor.execute("SELECT id FROM crop_data WHERE farmer_id=%s", (farmer_id,))
            crop_id = self.cursor.fetchone()

            if crop_id is None:
                raise ValueError("Crop ID not found")

            crop_id = crop_id[0]

            # Generate Harvest ID
            harvest_id = f"{farmer_id}_{crop_id}"

            # Insert into the harvest table
            self.cursor.execute("""
                INSERT INTO harvest (harvest_id, crop_id, farmer_id, quantity_harvested, date, time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (harvest_id, crop_id, farmer_id, quantity_harvested, date, time))

            # Commit the transaction
            self.db.commit()

            messagebox.showinfo("Success", "Harvest record stored successfully")

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))  # Handle invalid input data
            self.db.rollback()  # Rollback if there's an error

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error storing harvest record: {e}")

    def create_sensors_tab(self):
        sensors_tab = ttk.Frame(self.notebook)
        self.notebook.add(sensors_tab, text="Sensors")

        load_data_btn = tk.Button(sensors_tab, text="Load Data", command=self.load_sensor_data)
        load_data_btn.grid(row=0, column=0, padx=10, pady=5)

        display_graph_btn = tk.Button(sensors_tab, text="Display Graph", command=self.display_sensor_graph)
        display_graph_btn.grid(row=0, column=1, padx=10, pady=5)

        self.graph_frame = tk.Frame(sensors_tab)
        self.graph_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.sensor_data_label = tk.Label(sensors_tab, text="Sensor Data")
        self.sensor_data_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        self.sensor_graph_label = tk.Label(sensors_tab, text="Sensor Graph")
        self.sensor_graph_label.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    def load_sensor_data(self):
        try:
            file_path = "C:\\python312\\Sensors Table.xlsx"
            df = pd.read_excel(file_path)

            # Strip trailing spaces from column names
            df.columns = df.columns.str.strip()

            self.sensor_data_df = df
            self.sensor_data_label.config(text=f"Loaded Data:\n{df.to_string()}")
            print("Columns in the data frame:", df.columns)  # Print the columns

        except Exception as e:
            messagebox.showerror("Error", f"Error loading data from Excel file: {e}")



    def display_sensor_graph(self):
        try:
            file_path = "C:\\python312\\Sensors Table.xlsx"
            df = pd.read_excel(file_path)

            # Strip trailing spaces from column names
            df.columns = df.columns.str.strip()

            sensor_id = 1
            sensor_data = df[df["Sensor ID"] == sensor_id]

            print("Sensor data columns:", sensor_data.columns)  # Print the columns to verify

            time_values = sensor_data["Time"]
            soil_moisture = sensor_data["Soil Moisture (%)"]
            ph_of_water = sensor_data["PH of Water"]
            co2 = sensor_data["CO2 (ppm)"]
            temperature = sensor_data["Temperature (K)"]
            humidity = sensor_data["Humidity (%)"]
            tds = sensor_data["TDS (ppm)"]

            plt.figure(figsize=(10, 7))

            parameters = ["Soil Moisture", "PH of Water", "CO2", "Temperature", "Humidity", "TDS"]
            data = [soil_moisture, ph_of_water, co2, temperature, humidity, tds]

            for i, param in enumerate(parameters, start=1):
                plt.subplot(3, 2, i)
                plt.plot(time_values, data[i-1], marker='o')
                plt.xlabel('Time')
                plt.ylabel(param)
                plt.title(param)
                plt.grid(True)

            plt.tight_layout()

            self.graph = FigureCanvasTkAgg(plt.gcf(), master=self.graph_frame)
            self.graph_widget = self.graph.get_tk_widget()
            self.graph_widget.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying graph: {e}")
   


    def get_crop_id(self):
        try:
            # Get the farmer_id based on the username
            self.cursor.execute("SELECT id FROM farmer WHERE name=%s", (self.username,))
            farmer_id = self.cursor.fetchone()[0]

            # Get the crop_id based on the farmer_id
            self.cursor.execute("SELECT crop_id FROM crop_data WHERE farmer_id=%s", (farmer_id,))
            crop_id = self.cursor.fetchone()[0]
            
            return crop_id
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching crop ID from database: {e}")
            return None  # Return None if an error occurs

    def get_crop_name(self):
        try:
            self.cursor.execute("SELECT crop_name FROM crop_data WHERE farmer_id=%s", (self.get_id(),))
            crop_name = self.cursor.fetchone()[0]
            return crop_name
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching crop name from database: {e}")    

    def create_crop_health_tab(self):
        crop_health_tab = ttk.Frame(self.notebook)
        self.notebook.add(crop_health_tab, text="Crop Health Monitoring")

        fields = ["Health ID", "Date", "Predicted Health Status"]

        for i, field in enumerate(fields):
            label = tk.Label(crop_health_tab, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

            if field == "Health ID":
                health_id = self.get_id()
                entry = tk.Entry(crop_health_tab, width=50)
                entry.insert(tk.END, health_id)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            elif field == "Date":
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                entry = tk.Entry(crop_health_tab, width=50)
                entry.insert(tk.END, date)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            elif field == "Predicted Health Status":
                health_status, out_of_range_values, live_values = self.predict_health_status()
                print("Predicted Health Status:", health_status)
                print("Out of Range Values:", out_of_range_values)
                print("Live Values:", live_values)
                entry = tk.Entry(crop_health_tab, width=50)
                entry.insert(tk.END, health_status)
                entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)  

                if out_of_range_values:
                    out_of_range_label = tk.Label(crop_health_tab, text="Out of Range:")
                    out_of_range_label.grid(row=i+1, column=0, padx=10, pady=5, sticky=tk.W)

                    out_of_range_text = "\n".join([f"{key}: {value}" for key, value in out_of_range_values.items()])
                    out_of_range_entry = tk.Text(crop_health_tab, height=4, width=30)
                    out_of_range_entry.insert(tk.END, out_of_range_text)
                    out_of_range_entry.config(state='disabled')
                    out_of_range_entry.grid(row=i+1, column=1, padx=10, pady=5, sticky=tk.W)

    def predict_health_status(self):
        try:
            # Load historical sensor data
            file_path = "C:\\python312\\Sensors Table.xlsx"
            df = pd.read_excel(file_path)

            # Strip trailing spaces from column names
            df.columns = df.columns.str.strip()

            # Feature extraction for training
            X_train = df[["Soil Moisture (%)", "PH of Water", "CO2 (ppm)", "Temperature (K)", "Humidity (%)", "TDS (ppm)"]]
            y_train = df["Health Status"]  # Assuming there's a column named "Health Status" in historical data

            # Train Naive Bayes model
            model = GaussianNB()
            model.fit(X_train, y_train)

            # Verify model training
            print("Model trained with X_train shape:", X_train.shape, "and y_train shape:", y_train.shape)

            # Fetch live weather data
            weather_data = self.fetch_weather_data()

            # Prepare input features for prediction
            live_temperature = weather_data["temp"]
            live_humidity = weather_data["humidity"]

            # Numerical ranges for each determinant
            soil_moisture_range = (23, 45)
            ph_of_water_range = (6.5, 6.9)
            co2_range = (398, 410)
            temperature_range = (297.75, 298.35)
            humidity_range = (58, 61)
            tds_range = (300, 312)

            # Use historical average values for other features or fetch them dynamically
            soil_moisture = df["Soil Moisture (%)"].mean()
            ph_of_water = df["PH of Water"].mean()
            co2 = df["CO2 (ppm)"].mean()
            tds = df["TDS (ppm)"].mean()

            # Create a DataFrame for live data prediction
            live_data_df = pd.DataFrame([{
                "Soil Moisture (%)": soil_moisture,
                "PH of Water": ph_of_water,
                "CO2 (ppm)": co2,
                "Temperature (K)": live_temperature,
                "Humidity (%)": live_humidity,
                "TDS (ppm)": tds
            }])

            # Verify live data used for prediction
            print("Live DataFrame for prediction:", live_data_df)

            # Predict health status
            health_status = model.predict(live_data_df)[0]
            print("Predicted Health Status:", health_status)

            # Check if live data is within acceptable ranges
            ranges = {
                "Temperature (K)": temperature_range,
                "Humidity (%)": humidity_range,
            }
            
            live_values = {
                "Temperature (K)": live_temperature,
                "Humidity (%)": live_humidity,
            }

            within_ranges = True
            out_of_range_values = {}
            for key, (low, high) in ranges.items():
                value = live_values[key]
                if not (low <= value <= high):
                    out_of_range_values[key] = value
                    within_ranges = False

            print("Within Ranges:", within_ranges)
            print("Out of Range Values:", out_of_range_values)

            if within_ranges:
                return "Healthy" if health_status == 1 else "Diseased", None, None
            else:
                return "Make arrangements to change out of range values", out_of_range_values, live_values

        except Exception as e:
            messagebox.showerror("Error", f"Error health status: {e}")
            return "Make arrangements to change out of range values", None, None

            
    def create_profile_tab(self):
        profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(profile_tab, text="Profile")

        try:
            self.cursor.execute("SELECT name FROM farmer WHERE id=%s", (self.get_id(),))
            full_name = self.cursor.fetchone()[0]
        except Exception as e:
            full_name = "Error retrieving name"

        try:
            self.cursor.execute("SELECT location FROM crop_data WHERE farmer_id=%s", (self.get_id(),))
            farm_location = self.cursor.fetchone()[0]
        except Exception as e:
            farm_location = "Error retrieving location"

        try:
            self.cursor.execute("SELECT crop_name FROM crop_data WHERE farmer_id=%s", (self.get_id(),))
            crop_name = self.cursor.fetchone()[0]
        except Exception as e:
            crop_name = "Error retrieving crop name"

        tk.Label(profile_tab, text="Name:", font="arial 13").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Label(profile_tab, text=full_name, font="arial 13").grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(profile_tab, text="Farm Location:", font="arial 13").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Label(profile_tab, text=farm_location, font="arial 13").grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(profile_tab, text="Crop Name:", font="arial 13").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Label(profile_tab, text=crop_name, font="arial 13").grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(profile_tab, text="Crop Photo:", font="arial 13").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)

        try:
            image_path = f"C:\\python312\\Scripts\\Images\\Crop_Img_{self.get_id()}.png"
            original_image = Image.open(image_path)

            aspect_ratio = original_image.width / original_image.height

            if aspect_ratio > 1:
                new_width = 100
                new_height = int(100 / aspect_ratio)
            else:
                new_height = 100
                new_width = int(100 * aspect_ratio)

            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

            self.crop_image = ImageTk.PhotoImage(resized_image)
            tk.Label(profile_tab, image=self.crop_image).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        except Exception as e:
            tk.Label(profile_tab, text="Error loading image", font="arial 13").grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # Replace "Change Login Details" button with "Logout" button
        tk.Button(profile_tab, text="Logout", command=self.logout).grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def logout(self):
        # Perform logout actions here
        self.root.destroy()
        # Add any additional actions like clearing session data, etc.

    def __del__(self):
        if hasattr(self, 'cursor') and hasattr(self, 'db'):
            self.cursor.close()
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    #username = "Sanskruti"
    app = SmartAgriDashboard(root, username)
    root.mainloop()
