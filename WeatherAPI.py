import requests
import csv
from datetime import datetime, timedelta
import os
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import sys
import threading
from queue import Queue
from tkcalendar import DateEntry
import pickle

def translate_weather_condition(condition):
    weather_translations = {
        "Sunny": "Nắng",
        "Clear": "Quang đãng",
        "Partly cloudy": "Mây rải rác",
        "Cloudy": "Nhiều mây",
        "Overcast": "U ám",
        "Mist": "Sương mù nhẹ",
        "Patchy rain possible": "Có thể mưa rải rác",
        "Patchy snow possible": "Có thể tuyết rải rác",
        "Patchy sleet possible": "Có thể mưa tuyết rải rác",
        "Patchy freezing drizzle possible": "Có thể mưa phùn đóng băng",
        "Thundery outbreaks possible": "Có thể có dông",
        "Blowing snow": "Tuyết thổi",
        "Blizzard": "Bão tuyết",
        "Fog": "Sương mù",
        "Freezing fog": "Sương mù đóng băng",
        "Patchy light drizzle": "Mưa phùn nhẹ rải rác",
        "Light drizzle": "Mưa phùn nhẹ",
        "Freezing drizzle": "Mưa phùn đóng băng",
        "Heavy freezing drizzle": "Mưa phùn đóng băng nặng",
        "Patchy light rain": "Mưa nhẹ rải rác",
        "Light rain": "Mưa nhẹ",
        "Moderate rain at times": "Mưa vừa lúc",
        "Moderate rain": "Mưa vừa",
        "Heavy rain at times": "Mưa to lúc",
        "Heavy rain": "Mưa to",
        "Light freezing rain": "Mưa đóng băng nhẹ",
        "Moderate or heavy freezing rain": "Mưa đóng băng vừa đến nặng",
        "Light sleet": "Mưa tuyết nhẹ",
        "Moderate or heavy sleet": "Mưa tuyết vừa đến nặng",
        "Patchy light snow": "Tuyết nhẹ rải rác",
        "Light snow": "Tuyết nhẹ",
        "Patchy moderate snow": "Tuyết vừa rải rác",
        "Moderate snow": "Tuyết vừa",
        "Patchy heavy snow": "Tuyết rơi dày rải rác",
        "Heavy snow": "Tuyết rơi dày",
        "Ice pellets": "Mưa đá",
        "Light rain shower": "Mưa rào nhẹ",
        "Moderate or heavy rain shower": "Mưa rào vừa đến nặng",
        "Torrential rain shower": "Mưa rào lớn",
        "Light sleet showers": "Mưa tuyết rào nhẹ",
        "Moderate or heavy sleet showers": "Mưa tuyết rào vừa đến nặng",
        "Light snow showers": "Tuyết rơi nhẹ",
        "Moderate or heavy snow showers": "Tuyết rơi vừa đến nặng",
        "Light showers of ice pellets": "Mưa đá nhẹ",
        "Moderate or heavy showers of ice pellets": "Mưa đá vừa đến nặng",
        "Patchy light rain with thunder": "Mưa nhẹ có sấm rải rác",
        "Moderate or heavy rain with thunder": "Mưa vừa đến to có sấm",
        "Patchy light snow with thunder": "Tuyết nhẹ có sấm rải rác",
        "Moderate or heavy snow with thunder": "Tuyết vừa đến dày có sấm"
    }
    return weather_translations.get(condition, condition)

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Thời tiết")
        self.root.geometry("1200x600+100+100")
        self.root.wm_iconbitmap("")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_container = ttk.Frame(root, padding="10")
        main_container.grid(sticky="nsew")
        main_container.grid_columnconfigure(1, weight=3) 
        main_container.grid_rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        
        path_frame = ttk.LabelFrame(left_frame, text="Đường dẫn file", padding="5")
        path_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(path_frame, text="File cấu hình:").pack(anchor="w")
        config_frame = ttk.Frame(path_frame)
        config_frame.pack(fill="x", pady=(0, 5))
        self.config_path = ttk.Entry(config_frame)
        self.config_path.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(config_frame, text="...", width=3,
                  command=lambda: self.browse_file(self.config_path, "config_weather.txt")).pack(side="right")

        ttk.Label(path_frame, text="File CSV đầu ra:").pack(anchor="w")
        csv_frame = ttk.Frame(path_frame)
        csv_frame.pack(fill="x", pady=(0, 5))
        self.csv_path = ttk.Entry(csv_frame)
        self.csv_path.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(csv_frame, text="...", width=3,
                  command=lambda: self.browse_file(self.csv_path, "weather_all.csv", save=True)).pack(side="right")

        date_frame = ttk.LabelFrame(left_frame, text="Khoảng thời gian", padding="5")
        date_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(date_frame, text="Từ ngày:").pack(anchor="w")
        self.start_date = DateEntry(date_frame, width=20, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='yyyy-mm-dd',
                                  mindate=datetime(2010, 1, 1),
                                  maxdate=datetime.now())
        self.start_date.pack(fill="x", pady=(0, 5))

        ttk.Label(date_frame, text="Đến ngày:").pack(anchor="w")
        self.end_date = DateEntry(date_frame, width=20, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd',
                                mindate=datetime(2010, 1, 1),
                                maxdate=datetime.now())
        self.end_date.pack(fill="x")

        control_frame = ttk.LabelFrame(left_frame, text="Điều khiển", padding="5")
        control_frame.pack(fill="x", pady=(0, 10))

        resume_frame = ttk.Frame(control_frame)
        resume_frame.pack(fill="x", pady=(0, 5))
        
        self.resume_var = tk.BooleanVar(value=True)
        self.resume_check = ttk.Checkbutton(
            resume_frame, 
            text="Tiếp tục phiên trước", 
            variable=self.resume_var,
            command=self.toggle_resume
        )
        self.resume_check.pack(side="left")
        
        ttk.Button(resume_frame, text="Xóa phiên", 
                  command=self.clear_session,
                  style='Action.TButton').pack(side="right")

        style = ttk.Style()
        style.configure('Action.TButton', padding=5)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x", pady=(0, 5))

        self.load_id_btn = ttk.Button(button_frame, text="Tải danh sách ID", 
                                     command=self.load_id_list, style='Action.TButton')
        self.load_id_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.pause_btn = ttk.Button(button_frame, text="Tạm dừng", 
                                   command=self.toggle_pause, state='disabled', style='Action.TButton')
        self.pause_btn.pack(side="right", fill="x", expand=True, padx=(2, 0))

        self.get_data_btn = ttk.Button(control_frame, text="Lấy dữ liệu thời tiết", 
                                      command=self.get_weather_data, style='Action.TButton')
        self.get_data_btn.pack(fill="x")

        config_info_frame = ttk.LabelFrame(left_frame, text="Hướng dẫn sử dụng", padding="5")
        config_info_frame.pack(fill="both", expand=True)
        
        self.config_info = scrolledtext.ScrolledText(
            config_info_frame,
            wrap=tk.WORD,
            width=50,
            height=8
        )
        self.config_info.pack(fill="both", expand=True)
        
        instructions = """HƯỚNG DẪN SỬ DỤNG:

1. Cấu hình file:
   • Chọn đường dẫn file cấu hình chứa API key
   • Chọn đường dẫn file CSV để lưu dữ liệu

2. Chọn khoảng thời gian:
   • Chọn ngày bắt đầu
   • Chọn ngày kết thúc

3. Điều khiển:
   • Tải danh sách ID: Tải danh sách thành phố
   • Tạm dừng/Tiếp tục: Điều khiển quá trình lấy dữ liệu
   • Lấy dữ liệu thời tiết: Bắt đầu quá trình

Lưu ý: Có thể tiếp tục phiên trước đó bằng cách chọn "Tiếp tục phiên trước"."""

        self.config_info.insert(tk.END, instructions)
        self.config_info.configure(state='disabled') 

        console_frame = ttk.LabelFrame(main_container, text="Console Log", padding="5")
        console_frame.grid(row=0, column=1, sticky="nsew")
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(0, weight=1)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            font=('Consolas', 10),
            wrap=tk.WORD,
            bg='#1E1E1E',  
            fg='#FFFFFF',
            state='disabled',
            insertbackground='white'
        )
        self.console.grid(row=0, column=0, sticky="nsew")

        self.init_default_values()

        sys.stdout = StdoutRedirector(self.console)
        self.log_queue = Queue()
        self.root.after(100, self.process_log_queue)

        self.current_api_index = 0
        self.api_keys = []
        self.failed_apis = set() 

        self.session_file = 'config.bin'
        self.current_session = {
            'current_date': None,
            'end_date': None,
            'current_city_index': 0,
            'cities': [],
            'api_state': {
                'current_index': 0,
                'failed_apis': set()
            }
        }
        
        self.load_session()

        self.paused = False
        self.pause_event = threading.Event()
        self.pause_event.set() 

    def init_default_values(self):
        default_paths = {
            self.config_path: "config_weather.txt",
            self.csv_path: "weather_all.csv"
        }
        for entry, default_file in default_paths.items():
            entry.insert(0, os.path.abspath(default_file))

    def browse_file(self, entry_widget, default_name, save=False):
        initial_dir = os.path.dirname(entry_widget.get()) if entry_widget.get() else os.getcwd()
        if save:
            filename = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                initialfile=default_name,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        else:
            filename = filedialog.askopenfilename(
                initialdir=initial_dir,
                initialfile=default_name,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def load_id_list(self):
        _, cities = self.load_config()
        if cities:
            self.thread_safe_print("✅ Đã tải danh sách thành phố:")
            for city in cities:
                self.thread_safe_print(f"  📍 {city}")

    def process_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.console.configure(state='normal') 
            self.console.insert(tk.END, message)
            if "❌" in message:
                self.console.tag_add("error", "end-{}c".format(len(message)), "end-1c")
            elif "✅" in message:
                self.console.tag_add("success", "end-{}c".format(len(message)), "end-1c")
            elif "📅" in message or "🔍" in message:
                self.console.tag_add("info", "end-{}c".format(len(message)), "end-1c")
            self.console.see(tk.END)
            self.console.configure(state='disabled')
        
        self.root.after(100, self.process_log_queue)

    def thread_safe_print(self, message):
        self.log_queue.put(message + "\n")

    def load_config(self):
        try:
            api_keys = []
            cities = []
            current_section = None
            
            with open(self.config_path.get(), 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line: 
                        continue
                        
                    if line == '[API_KEYS]':
                        current_section = 'api'
                        continue
                    elif line == '[CITIES]':
                        current_section = 'cities'
                        continue
                    
                    if current_section == 'api':
                        api_keys.append(line)
                    elif current_section == 'cities':
                        cities.append(line)
            
            if not api_keys:
                self.thread_safe_print("❌ Không tìm thấy API keys trong file cấu hình")
            if not cities:
                self.thread_safe_print("❌ Không tìm thấy danh sách thành phố trong file cấu hình")
            
            return api_keys, cities
        except FileNotFoundError:
            self.thread_safe_print("❌ Không tìm thấy file cấu hình")
            return [], []
        except Exception as e:
            self.thread_safe_print(f"❌ Lỗi khi đọc file cấu hình: {str(e)}")
            return [], []

    def get_next_valid_api(self):
        if not self.api_keys:
            api_keys, _ = self.load_config()
            self.api_keys = api_keys
            if not self.api_keys:
                return None

        if len(self.failed_apis) == len(self.api_keys):
            self.thread_safe_print("❌ Tất cả API key đều đã bị lỗi")
            return None

        while self.current_api_index < len(self.api_keys):
            current_api = self.api_keys[self.current_api_index]
            if current_api not in self.failed_apis:
                return current_api
            self.current_api_index += 1

        self.current_api_index = 0
        while self.current_api_index < len(self.api_keys):
            current_api = self.api_keys[self.current_api_index]
            if current_api not in self.failed_apis:
                return current_api
            self.current_api_index += 1

        return None

    def get_weather_data(self):
        self.console.delete(1.0, tk.END)
        self.get_data_btn.configure(state='disabled')
        self.pause_btn.configure(state='normal') 
        self.paused = False
        self.pause_event.set()
        
        api_keys, cities = self.load_config()
        if not api_keys or not cities:
            self.get_data_btn.configure(state='normal')
            return

        if not self.validate_dates():
            self.get_data_btn.configure(state='normal')
            return

        self.api_keys = api_keys

        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()

        weather_thread = threading.Thread(
            target=self.weather_worker,
            args=(cities, start_date, end_date),
            daemon=True
        )
        weather_thread.start()

    def validate_dates(self):
        start = self.start_date.get()
        end = self.end_date.get()
        
        if not validate_date(start) or not validate_date(end):
            return False
            
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        
        if end_date < start_date:
            print("❌ Ngày kết thúc phải sau ngày bắt đầu")
            return False
            
        return True

    def save_session(self):
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.current_session, f)
            self.thread_safe_print("✅ Đã lưu trạng thái phiên làm việc")
        except Exception as e:
            self.thread_safe_print(f"❌ Lỗi khi lưu phiên: {str(e)}")

    def load_session(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    self.current_session = pickle.load(f)
                if self.current_session['current_date']:
                    self.thread_safe_print("ℹ️ Tìm thấy phiên làm việc trước:")
                    self.thread_safe_print(f"📅 Ngày hiện tại: {self.current_session['current_date']}")
                    self.thread_safe_print(f"📅 Ngày kết thúc: {self.current_session['end_date']}")
                    self.thread_safe_print(f"📍 Số thành phố còn lại: {len(self.current_session['cities']) - self.current_session['current_city_index']}")
        except Exception as e:
            self.thread_safe_print(f"❌ Lỗi khi đọc phiên: {str(e)}")
            self.current_session = {
                'current_date': None,
                'end_date': None,
                'current_city_index': 0,
                'cities': [],
                'api_state': {
                    'current_index': 0,
                    'failed_apis': set()
                }
            }

    def clear_session(self):
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            self.current_session = {
                'current_date': None,
                'end_date': None,
                'current_city_index': 0,
                'cities': [],
                'api_state': {
                    'current_index': 0,
                    'failed_apis': set()
                }
            }
            self.thread_safe_print("✅ Đã xóa phiên làm việc")
        except Exception as e:
            self.thread_safe_print(f"❌ Lỗi khi xóa phiên: {str(e)}")

    def toggle_resume(self):
        if not self.resume_var.get():
            self.clear_session()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_event.clear() 
            self.pause_btn.configure(text="Tiếp tục")
            self.thread_safe_print("\n⏸️ Đã tạm dừng")
        else:
            self.pause_event.set()   
            self.pause_btn.configure(text="Tạm dừng")
            self.thread_safe_print("\n▶️ Đã tiếp tục")

    def weather_worker(self, cities, start_date, end_date):
        try:
            if self.resume_var.get() and self.current_session['current_date']:
                current_date = datetime.strptime(self.current_session['current_date'], '%Y-%m-%d')
                end_date = datetime.strptime(self.current_session['end_date'], '%Y-%m-%d')
                current_city_index = self.current_session['current_city_index']
                cities = self.current_session['cities']
                
                self.current_api_index = self.current_session['api_state']['current_index']
                self.failed_apis = self.current_session['api_state']['failed_apis']
            else:
                current_date = start_date
                current_date = start_date
                current_city_index = 0
                self.current_session['cities'] = cities
                api_keys, _ = self.load_config()
                self.api_keys = api_keys

            while current_date <= end_date:
                self.pause_event.wait()
                
                date_str = current_date.strftime('%Y-%m-%d')
                self.thread_safe_print(f"\n📅 Ngày: {date_str}")
                
                self.current_session.update({
                    'current_date': date_str,
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'current_city_index': current_city_index,
                    'api_state': {
                        'current_index': self.current_api_index,
                        'failed_apis': self.failed_apis
                    }
                })
                self.save_session()
                
                for city in cities[current_city_index:]:
                    self.thread_safe_print(f"\n🌍 Đang tìm thông tin cho {city}...")
                    if self.get_weather(city, date_str):
                        current_city_index += 1
                    else:
                        break
                
                current_city_index = 0
                if current_date < end_date:
                    self.thread_safe_print("\n⏳ Đợi 3 giây...\n")
                    time.sleep(3)
                
                current_date += timedelta(days=1)
            
            self.clear_session()
            self.thread_safe_print("\n✅ Hoàn thành!\n")
        except Exception as e:
            self.thread_safe_print(f"\n❌ Lỗi: {str(e)}\n")
            self.save_session()
        finally:
            self.root.after(0, lambda: self.get_data_btn.configure(state='normal'))
            self.root.after(0, lambda: self.pause_btn.configure(state='disabled'))
            self.pause_event.set()

    def get_weather(self, city, date):
        if not self.api_keys:
            api_keys, _ = self.load_config()
            self.api_keys = api_keys
            if not self.api_keys:
                self.thread_safe_print("❌ Không có API key khả dụng")
                return False

        BASE_URL = "http://api.weatherapi.com/v1/history.json"
        
        while True:
            api_key = self.get_next_valid_api()
            if not api_key:
                self.thread_safe_print("❌ Không còn API key khả dụng")
                return False

            params = {
                "key": api_key,
                "q": city,
                "dt": date
            }

            try:
                response = requests.get(BASE_URL, params=params)
                data = response.json()

                if "error" in data:
                    self.thread_safe_print(f"❌ API {api_key[:5]}... không hợp lệ\n")
                    self.failed_apis.add(api_key)
                    self.current_api_index += 1
                    continue

                location = data["location"]["name"]
                forecast_day = data["forecast"]["forecastday"][0]["day"]
                
                temp_c = forecast_day.get("avgtemp_c", 0)
                maxtemp_c = forecast_day.get("maxtemp_c", 0)
                mintemp_c = forecast_day.get("mintemp_c", 0)
                condition = translate_weather_condition(forecast_day.get("condition", {}).get("text", "Không có thông tin"))
                
                precip_mm = forecast_day.get("totalprecip_mm", 0)
                rain_chance = forecast_day.get("daily_chance_of_rain", 0)
                
                humidity = forecast_day.get("avghumidity", 0)
                wind_kph = forecast_day.get("maxwind_kph", 0)
                
                uv = forecast_day.get("uv", 0)
                vis_km = forecast_day.get("avgvis_km", 0)

                weather_data = {
                    'Ngày': date,
                    'Thành phố': location,
                    'Nhiệt độ TB (°C)': temp_c,
                    'Nhiệt độ cao nhất (°C)': maxtemp_c,
                    'Nhiệt độ thấp nhất (°C)': mintemp_c,
                    'Thời tiết': condition,
                    'Lượng mưa (mm)': precip_mm,
                    'Xác suất mưa (%)': rain_chance,
                    'Độ ẩm TB (%)': humidity,
                    'Gió mạnh nhất (km/h)': wind_kph,
                    'Chỉ số UV': uv,
                    'Tầm nhìn TB (km)': vis_km
                }

                self.save_to_csv(weather_data)

                self.thread_safe_print(
                    f"✅ Kết quả:\n"
                    f"- {location}\n"
                    f"- Nhiệt độ: {temp_c}°C (Cao: {maxtemp_c}°C, Thấp: {mintemp_c}°C)\n"
                    f"- Thời tiết: {condition}\n"
                    f"- Lượng mưa: {precip_mm}mm\n"
                    f"- Xác suất mưa: {rain_chance}%\n"
                    f"- Độ ẩm: {humidity}%\n"
                    f"- Gió: {wind_kph}km/h\n"
                    f"- UV: {uv}\n"
                    f"- Tầm nhìn: {vis_km}km\n"
                )
                return True

            except Exception as e:
                self.thread_safe_print(f"❌ Lỗi API {api_key[:5]}...\n")
                self.failed_apis.add(api_key)
                self.current_api_index += 1
                continue

    def save_to_csv(self, weather_data):
        filename = self.csv_path.get()
        file_exists = os.path.isfile(filename)
        
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=weather_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(weather_data)
        except Exception as e:
            self.thread_safe_print(f"❌ Lỗi lưu CSV: {str(e)}")

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.tag_configure("error", foreground="#ff6b6b")      
        self.text_widget.tag_configure("success", foreground="#69db7c")    
        self.text_widget.tag_configure("info", foreground="#4dabf7")      
        self.text_widget.tag_configure("warning", foreground="#ffd43b")   
        self._buffer = []

    def write(self, text):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, text)
        if "❌" in text:
            self.text_widget.tag_add("error", "end-{}c".format(len(text)), "end-1c")
        elif "✅" in text:
            self.text_widget.tag_add("success", "end-{}c".format(len(text)), "end-1c")
        elif "📅" in text or "🔍" in text:
            self.text_widget.tag_add("info", "end-{}c".format(len(text)), "end-1c")
        elif "⚠️" in text:
            self.text_widget.tag_add("warning", "end-{}c".format(len(text)), "end-1c")
        self.text_widget.configure(state='disabled')
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        print("❌ Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD")
        return False

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()