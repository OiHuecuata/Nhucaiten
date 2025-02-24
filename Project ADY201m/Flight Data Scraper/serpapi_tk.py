import requests
import json
import csv
from datetime import datetime, timedelta
import time
import os
import pickle
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import sys
import logging
import threading
from queue import Queue

def load_config_file(config_path):
    api_keys = []
    routes = []
    
    try:
        with open(config_path, "r") as file:
            section = None
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                    
                if line == "[API_KEYS]":
                    section = "api_keys"
                elif line == "[ROUTES]":
                    section = "routes"
                else:
                    if section == "api_keys":
                        api_keys.append(line)
                    elif section == "routes":
                        origin, destination = line.split('-')
                        routes.append((origin.strip(), destination.strip()))
                        
        return api_keys, routes
    except FileNotFoundError:
        print("Error: config_flights.txt file not found")
        return [], []
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return [], []

def is_valid_response(response):
    try:
        data = response.json()
        if "error" in data or "search_metadata" not in data:
            return False
        return True
    except json.JSONDecodeError:
        return False

def get_flight_data(api_key, outbound_date, return_date, departure_id, arrival_id):
    print("\n" + "="*50)
    print("NEW FLIGHT QUERY")
    print("="*50)
    print(f"Route: {departure_id} ➜ {arrival_id}")
    print(f"Date Range: {outbound_date} to {return_date}")
    print(f"API Key: {api_key[:8]}...")
    print("-"*50)

    params = {
        "engine": "google_flights",      
        "departure_id": departure_id,    
        "arrival_id": arrival_id,        
        "outbound_date": outbound_date,  
        "return_date": return_date,      
        "currency": "VND",               
        "hl": "vi",                      
        "api_key": api_key               
    }

    try:
        print("\nSending API request...")
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200 and is_valid_response(response):
            print("Successfully received flight data!")
            return response.json()
        else:
            error_message = f"Error: API Status code {response.status_code}"
            if response.status_code == 200:
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message = f"Error: {error_data['error']}"
                        if "Google Flights hasn't returned any results for this query." in error_message:
                            print("Warning: No flights found for this route and date")
                            return "NO_FLIGHTS"
                except json.JSONDecodeError:
                    error_message = "Error: Invalid JSON response"
            print(error_message)
            return None
    except requests.RequestException as e:
        print(f"Error: Request failed - {str(e)}")
        return None

def extract_flight_info(data):
    flights = []
    
    all_flights = data.get("best_flights", []) + data.get("other_flights", [])
    print("\n" + "-"*50)
    print(f"Found {len(all_flights)} flights!")
    print("-"*50)
    
    for flight in all_flights:
        for flight_segment in flight.get("flights", []):
            flight_info = {
                "Flight Date": flight_segment["departure_airport"]["time"].split()[0],
                "Return Date": flight_segment["departure_airport"]["time"].split()[0],
                "Airline": flight_segment.get("airline", ""),
                "Origin": flight_segment["departure_airport"]["id"],
                "Destination": flight_segment["arrival_airport"]["id"],
                "Departure Time": flight_segment["departure_airport"]["time"].split()[1],
                "Arrival Time": flight_segment["arrival_airport"]["time"].split()[1],
                "Duration (minutes)": flight_segment.get("duration", ""),
                "Price (VND)": flight.get("price", "")
            }
            flights.append(flight_info)
            print(f"➜ {flight_info['Airline']} | {flight_info['Origin']} ➜ {flight_info['Destination']} | {flight_info['Price (VND)']} VND")
    
    return flights

def save_to_csv(flights, filename="flight_data.csv", mode='a'):
    if not flights:
        print("Warning: No flights to save")
        return False
        
    fieldnames = ["Flight Date", "Return Date", "Airline", "Origin", "Destination", 
                  "Departure Time", "Arrival Time", "Duration (minutes)", "Price (VND)"]
    
    try:
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists or mode == 'w':
                writer.writeheader()
                print(f"\nCreated new CSV file: {filename}")
            writer.writerows(flights)
            print(f"Successfully saved {len(flights)} flights!")
        return True
    except Exception as e:
        print(f"Error: Failed to save to CSV - {e}")
        return False

def save_config(config, config_file):
    try:
        with open(config_file, 'wb') as f:
            pickle.dump(config, f)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def load_config(config_file):
    try:
        with open(config_file, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No existing configuration found. Starting fresh.")
        return None
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

class TelegramReporter:
    def __init__(self):
        self.bot_token = "API_TOKEN"
        self.chat_id = "ID" 
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session_stats = {
            'flights_collected': 0,
            'api_errors': {},
            'routes_processed': set(),
            'start_time': None
        }

    def send_message(self, message):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
            if not response.ok:
                print(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"Error sending Telegram message: {str(e)}")

    def start_session(self):
        self.session_stats['start_time'] = datetime.now()
        message = (
            "🚀 <b>Flight Scraper Session Started</b>\n"
            f"Start Time: {self.session_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            "Status: Initializing..."
        )
        self.send_message(message)

    def report_api_error(self, api_key, error_message):
        if api_key not in self.session_stats['api_errors']:
            self.session_stats['api_errors'][api_key] = []
        self.session_stats['api_errors'][api_key].append(error_message)

        message = (
            "⚠️ <b>API Key Error Detected</b>\n"
            f"API Key: {api_key[:8]}...\n"
            f"Error: {error_message}\n"
            "\n<b>Troubleshooting Steps:</b>\n"
        )

        if "quota" in error_message.lower():
            message += "1. Check API key quota limits\n2. Consider upgrading plan or waiting for quota reset"
        elif "invalid" in error_message.lower():
            message += "1. Verify API key is correct\n2. Check if API key is still active"
        else:
            message += "1. Check API documentation for error details\n2. Contact support if issue persists"

        self.send_message(message)

    def update_stats(self, flights_count=0, route=None):
        self.session_stats['flights_collected'] += flights_count
        if route:
            self.session_stats['routes_processed'].add(route)

    def send_progress_report(self):
        duration = datetime.now() - self.session_stats['start_time']
        hours = duration.total_seconds() / 3600

        message = (
            "📊 <b>Scraping Progress Report</b>\n"
            f"Session Duration: {duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m\n"
            f"Flights Collected: {self.session_stats['flights_collected']}\n"
            f"Routes Processed: {len(self.session_stats['routes_processed'])}\n"
            f"Collection Rate: {self.session_stats['flights_collected'] / hours:.1f} flights/hour\n"
            f"Failed API Keys: {len(self.session_stats['api_errors'])}\n"
        )
        self.send_message(message)

    def send_final_report(self):
        duration = datetime.now() - self.session_stats['start_time']
        
        message = (
            "🏁 <b>Flight Scraping Session Completed</b>\n"
            f"Total Duration: {duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m\n"
            f"Total Flights Collected: {self.session_stats['flights_collected']}\n"
            f"Total Routes Processed: {len(self.session_stats['routes_processed'])}\n"
            "\n<b>API Key Status Summary:</b>\n"
        )

        for api_key, errors in self.session_stats['api_errors'].items():
            message += f"\nAPI Key {api_key[:8]}...:\n"
            message += f"- Total Errors: {len(errors)}\n"
            message += f"- Last Error: {errors[-1]}\n"

        self.send_message(message)

def main(path_config_file, output_csv, config_file,
         days_to_collect=30, days_increment=3, days_between_flights=3, stop_event=None):
    telegram = TelegramReporter()
    telegram.start_session()

    print("\n=== Starting Flight Data Collection ===")
    print(f"Configuration:")
    print(f"- Days to collect: {days_to_collect}")
    print(f"- Days increment: {days_increment}")
    print(f"- Days between flights: {days_between_flights}")

    config = load_config(config_file)
    
    if config:
        print("\nResuming from saved configuration...")
        current_date = config['current_date']
        current_api_index = config['current_api_index']
        print(f"- Current date: {current_date}")
        print(f"- Current API index: {current_api_index}")
    else:
        print("\nStarting new data collection...")
        current_date = datetime.now()
        current_api_index = 0
    
    api_keys, routes = load_config_file(path_config_file)
    
    print(f"\nLoaded configuration:")
    print(f"- Number of API keys: {len(api_keys)}")
    print(f"- Number of routes: {len(routes)}")
    
    if not api_keys:
        print("Error: No API keys available")
        telegram.send_message("❌ Error: No API keys available")
        return
    
    if not routes:
        print("Error: No routes available")
        telegram.send_message("❌ Error: No routes available")
        return

    end_date = current_date + timedelta(days=days_to_collect)
    failed_api_keys = set()
    
    try:
        while current_date < end_date:
            if stop_event and stop_event.is_set():
                telegram.send_message("⚠️ Scraping process stopped by user")
                break

            failed_api_keys.clear()
            
            outbound_date = current_date.strftime("%Y-%m-%d")
            return_date = (current_date + timedelta(days=days_between_flights)).strftime("%Y-%m-%d")
            
            for departure_id, arrival_id in routes:
                route = f"{departure_id}-{arrival_id}"
                
                if stop_event and stop_event.is_set():
                    break
                    
                if len(failed_api_keys) == len(api_keys):
                    telegram.send_message("🛑 All API keys have failed. Stopping scraping process.")
                    telegram.send_final_report()
                    return

                success = False
                original_index = current_api_index
                
                while not success:
                    api_key = api_keys[current_api_index]
                    
                    if api_key in failed_api_keys:
                        current_api_index = (current_api_index + 1) % len(api_keys)
                        if current_api_index == original_index:
                            break
                        continue
                    
                    flight_data = get_flight_data(api_key, outbound_date, return_date, departure_id, arrival_id)
                    
                    if flight_data == "NO_FLIGHTS":
                        break
                    elif flight_data:
                        flights = extract_flight_info(flight_data)
                        if save_to_csv(flights, output_csv, mode='a'):
                            telegram.update_stats(len(flights), route)
                            success = True
                            break
                    else:
                        error_msg = f"Failed to retrieve data for route {route}"
                        telegram.report_api_error(api_key, error_msg)
                        failed_api_keys.add(api_key)
                        current_api_index = (current_api_index + 1) % len(api_keys)
                        time.sleep(1)
                        
                        if current_api_index == original_index:
                            break
                
                time.sleep(3)
                
                if len(telegram.session_stats['routes_processed']) % 5 == 0:
                    telegram.send_progress_report()
                
                current_config = {
                    'current_date': current_date,
                    'current_api_index': current_api_index,
                    'days_to_collect': days_to_collect,
                    'days_increment': days_increment,
                    'days_between_flights': days_between_flights
                }
                save_config(current_config, config_file)
            
            current_date += timedelta(days=days_increment)

        telegram.send_final_report()

    except Exception as e:
        error_msg = f"Critical error in scraping process: {str(e)}"
        telegram.send_message(f"❌ {error_msg}")
        raise e

    finally:
        telegram.send_final_report()

class RedirectText:
    def __init__(self, text_widget, log_file):
        self.text_widget = text_widget
        self.log_file = log_file
        self.queue = Queue()
        
        self.text_widget.tag_config('success', foreground='#4EC9B0')  
        self.text_widget.tag_config('error', foreground='#F44747')   
        self.text_widget.tag_config('warning', foreground='#FFA500')  
        self.text_widget.tag_config('info', foreground='#569CD6')    
        self.text_widget.tag_config('highlight', foreground='#C586C0') 
        self.text_widget.tag_config('timestamp', foreground='#6A9955')
        
        self.update_thread = threading.Thread(target=self.update_widget, daemon=True)
        self.update_thread.start()

    def write(self, string):
        if string.strip() and not string.isspace():
            timestamp = datetime.now().strftime('%H:%M:%S')
            string_with_timestamp = f"[{timestamp}] {string}"
        else:
            string_with_timestamp = string

        if "Error" in string or "Failed" in string:
            self.queue.put((string_with_timestamp, ['timestamp', 'error']))
        elif "Success" in string or "Successfully" in string:
            self.queue.put((string_with_timestamp, ['timestamp', 'success']))
        elif "Warning" in string or "No flights found" in string:
            self.queue.put((string_with_timestamp, ['timestamp', 'warning']))
        elif string.startswith(("Query", "Found", "Added", "Sending")):
            self.queue.put((string_with_timestamp, ['timestamp', 'info']))
        elif "===" in string or "Configuration" in string:
            self.queue.put((string_with_timestamp, ['timestamp', 'highlight']))
        else:
            self.queue.put((string_with_timestamp, ['timestamp']))

    def flush(self):
        pass

    def update_widget(self):
        while True:
            try:
                string, tags = self.queue.get()
                self.text_widget.after(0, self.update_text, string, tags)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(string)
                self.queue.task_done()
            except Exception as e:
                print(f"Error updating widget: {e}")
            time.sleep(0.01)

    def update_text(self, string, tags):
        self.text_widget.configure(state='normal')
        
        self.text_widget.insert(tk.END, string, tags)
        
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
        self.text_widget.update()

class FlightScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Data Scraper")
        self.root.geometry("1200x600+100+100")

        self.default_paths = {
            'config_file': os.path.join(os.getcwd(), "config_flights.txt"),
            'output_csv': os.path.join(os.getcwd(), "flight_data_all.csv"),
            'scraper_config': os.path.join(os.getcwd(), "scraper_config.bin")
        }
        
        self.path_entries = {}
        self.param_entries = {}

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_logging()

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.config_frame = ttk.LabelFrame(self.left_frame, text="Configuration", padding="5")
        self.config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.param_frame = ttk.LabelFrame(self.left_frame, text="Parameters", padding="5")
        self.param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.config_info_frame = ttk.LabelFrame(self.left_frame, text="Current Configuration Status", padding="5")
        self.config_info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.config_info_frame.grid_rowconfigure(0, weight=1)
        self.config_info_frame.grid_columnconfigure(0, weight=1)
        
        self.config_info = scrolledtext.ScrolledText(self.config_info_frame, wrap=tk.WORD, width=50, height=8)
        self.config_info.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.console_frame = ttk.LabelFrame(self.right_frame, text="Console Output", padding="5")
        self.console_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.console = scrolledtext.ScrolledText(
            self.console_frame,
            wrap=tk.WORD,
            state='disabled',
            font=('Consolas', 10),
            bg='#1E1E1E',
            fg='#FFFFFF',
            insertbackground='white'
        )
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))

        self.start_button = ttk.Button(self.button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_scraping, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.refresh_button = ttk.Button(self.button_frame, text="Refresh Config", command=self.update_config_info)
        self.refresh_button.grid(row=0, column=2, padx=5)

        sys.stdout = RedirectText(self.console, self.log_file)

        self.scraping_thread = None
        self.stop_event = threading.Event()

        self.create_path_entries()
        self.create_parameter_entries()

        self.update_config_info()

        self.root.resizable(True, True)

        self.root.minsize(800, 600)

    def setup_logging(self):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = os.path.join(log_dir, f"flight_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def create_path_entries(self):
        path_labels = {
            'config_file': 'Config File:',
            'output_csv': 'Output CSV:',
            'scraper_config': 'Scraper Config:'
        }
        
        for key, label in path_labels.items():
            row = len(self.path_entries)
            ttk.Label(self.config_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            var = tk.StringVar(value=self.default_paths[key])
            entry = ttk.Entry(self.config_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.path_entries[key] = var
            browse_btn = ttk.Button(
                self.config_frame,
                text="Browse",
                command=lambda e=var, k=key: self.browse_path(e, k)
            )
            browse_btn.grid(row=row, column=2, padx=5, pady=5)

    def browse_path(self, entry_var, path_type):
        current_path = entry_var.get()
        initial_dir = os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
        
        if path_type == 'output_csv':
            file_path = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                title="Select Output CSV Location",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                defaultextension=".csv"
            )
        else:
            file_types = {
                'config_file': [("Text files", "*.txt"), ("All files", "*.*")],
                'scraper_config': [("Binary files", "*.bin"), ("All files", "*.*")]
            }
            
            file_path = filedialog.askopenfilename(
                initialdir=initial_dir,
                title=f"Select {path_type.replace('_', ' ').title()}",
                filetypes=file_types.get(path_type, [("All files", "*.*")])
            )
        
        if file_path:
            entry_var.set(file_path)

    def create_parameter_entries(self):
        default_frame = ttk.LabelFrame(self.param_frame, text="Default Parameters", padding="5")
        default_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        params = {
            'days_to_collect': ('Days to Collect:', 30, (1, 365)),
            'days_increment': ('Days Increment:', 3, (1, 30)),
            'days_between_flights': ('Days Between Flights:', 3, (1, 30))
        }

        self.param_entries = {}
        for i, (key, (label, default, limits)) in enumerate(params.items()):
            ttk.Label(default_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            
            var = tk.IntVar(value=default)
            spinbox = ttk.Spinbox(
                default_frame,
                from_=limits[0],
                to=limits[1],
                textvariable=var,
                width=10,
                wrap=True
            )
            spinbox.grid(row=i, column=1, sticky=tk.W, padx=5)
            
            ToolTip(spinbox, f"Range: {limits[0]}-{limits[1]}")
            
            self.param_entries[key] = var

            reset_btn = ttk.Button(
                default_frame,
                text="Reset",
                command=lambda v=var, d=default: v.set(d)
            )
            reset_btn.grid(row=i, column=2, padx=5)

    def stop_scraping(self):
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_event.set()
            self.stop_button.configure(state='disabled')
            print("\nStopping scraping process... Please wait...")

    def run_scraping(self):
        try:
            logging.info("Starting scraping with configuration:")
            for key, entry in self.path_entries.items():
                logging.info(f"{key}: {entry.get()}")
            for key, entry in self.param_entries.items():
                logging.info(f"{key}: {entry.get()}")

            main(
                path_config_file=self.path_entries['config_file'].get(),
                output_csv=self.path_entries['output_csv'].get(),
                config_file=self.path_entries['scraper_config'].get(),
                days_to_collect=self.param_entries['days_to_collect'].get(),
                days_increment=self.param_entries['days_increment'].get(),
                days_between_flights=self.param_entries['days_between_flights'].get(),
                stop_event=self.stop_event
            )

        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}", exc_info=True)
            self.console.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        self.refresh_button.configure(state='normal')
        self.stop_event.clear()
        self.update_config_info()

    def start_scraping(self):
        try:
            self.start_button.configure(state='disabled')
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            self.refresh_button.configure(state='disabled')
            self.stop_event.clear()
            
            logging.info("Starting scraping with configuration:")
            for key, entry in self.path_entries.items():
                logging.info(f"{key}: {entry.get()}")
            for key, entry in self.param_entries.items():
                logging.info(f"{key}: {entry.get()}")

            self.scraping_thread = threading.Thread(target=self.run_scraping)
            self.scraping_thread.daemon = True
            self.scraping_thread.start()

        except Exception as e:
            logging.error(f"Error starting scraping: {str(e)}", exc_info=True)
            self.console.insert(tk.END, f"\nError: {str(e)}\n")
            self.reset_ui_state()

    def update_config_info(self):
        self.config_info.configure(state='normal') 
        self.config_info.delete(1.0, tk.END)
        config_file = self.path_entries['scraper_config'].get()
        
        try:
            config = load_config(config_file)
            if config:
                current_date = config.get('current_date', 'Not set')
                if isinstance(current_date, datetime):
                    current_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
                
                info_text = f"""Configuration Status:
• Current Date: {current_date}
• Current API Index: {config.get('current_api_index', 'Not set')}
• Days to Collect: {config.get('days_to_collect', 'Not set')}
• Days Increment: {config.get('days_increment', 'Not set')}
• Days Between Flights: {config.get('days_between_flights', 'Not set')}

Status: Ready to resume from saved configuration"""
            else:
                info_text = """No existing configuration found.
                
Status: Will start new data collection"""
        except Exception as e:
            info_text = f"""Error reading configuration:
{str(e)}

Status: Will start new data collection"""

        self.config_info.insert(tk.END, info_text)
        self.config_info.configure(state='disabled')

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def run_gui():
    root = tk.Tk()
    app = FlightScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

# kết quả cần đạt:
# - tên các hãng bay
# - giá vé
# - thời gian bay
# - thời gian đi và về
# - thời gian chuyến bay

# kết quả cần đạt của api thời tiết:
# - thời gian
# - ngày trong năm
# - ngày, tháng mưa
# - ngày, tháng nắng
# - ngày, tháng lạnh
# - ngày, tháng nóng

# - ngày, tháng mùa lễ hội, sự kiện

# => dự đoán giá vé theo thời gian
# => dự đoán khoảng thời gian đặt vé trước mấy ngày để có giá vé rẻ nhất
