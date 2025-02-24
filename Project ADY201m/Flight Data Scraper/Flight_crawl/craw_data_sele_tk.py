from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import threading
import queue
import tkinter.filedialog as filedialog
import zipfile
import os
import base64

def load_existing_data():
    try:
        with open("flights.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(flights_data):
    with open("flights.json", "w", encoding="utf-8") as f:
        json.dump(flights_data, f, ensure_ascii=False, indent=4)

def search_flights(start_date, num_days):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        all_flights = load_existing_data()
        
        driver.get("https://sanvemaybay.vn/")
        time.sleep(3)

        one_way = driver.find_element(By.ID, "one-way")
        one_way.click()
        time.sleep(1)

        departure_input = driver.find_element(By.ID, "depinput")
        departure_input.click()
        time.sleep(1)

        choice_departure = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='listDep']//a[@data-city='HAN']"))
        )
        choice_departure.click()

        destination_input = driver.find_element(By.ID, "desinput")
        destination_input.click()
        time.sleep(1)

        choice_destination = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='listDes']//a[@data-city='SGN']"))
        )
        choice_destination.click()
        
        for day in range(num_days):
            try:
                departure_date_input = driver.find_element(By.ID, "depdate")
                departure_date_input.click()
                time.sleep(1)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ui-datepicker-div"))
                )

                current_date = start_date + timedelta(days=day)
                date_to_select = str(current_date.day)
                
                if day == 0:
                    today = datetime.now()
                    
                    months_diff = (start_date.year - today.year) * 12 + (start_date.month - today.month)
                    
                    print(f"Cần chuyển {months_diff} tháng") 

                    if months_diff > 0:
                        for _ in range(months_diff):
                            next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                            next_button.click()
                            time.sleep(1)

                elif date_to_select == "1":
                    next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                    next_button.click()
                    time.sleep(1)

                date_element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[text()='{date_to_select}']"))
                )
                date_element.click()
                time.sleep(1)

                search_button = driver.find_element(By.ID, "btn-tim-ve")
                search_button.click()

                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "OutBound")))
                time.sleep(10)

                flight_rows = driver.find_elements(By.CLASS_NAME, "lineresult-main")

                flight_date = current_date.strftime("%Y-%m-%d")
                
                current_day_flights = []

                for row in flight_rows:
                    try:
                        flight_code = row.find_element(By.CLASS_NAME, "f_code").text.strip()
                        flight_time = row.find_element(By.CLASS_NAME, "f_time").text.strip()
                        flight_price = row.find_element(By.CLASS_NAME, "f_price").text.strip()

                        flight_info = {
                            "Ngày bay": flight_date,
                            "Mã chuyến bay": flight_code,
                            "Thời gian bay": flight_time,
                            "Giá vé": flight_price
                        }
                        current_day_flights.append(flight_info)
                    except Exception as e:
                        print(f"Lỗi khi xử lý chuyến bay: {str(e)}")
                        continue

                all_flights.extend(current_day_flights)
                
                save_to_json(all_flights)
                
                print(f"Đã lưu dữ liệu cho ngày {flight_date}")

            except Exception as e:
                print(f"Lỗi khi xử lý ngày {current_date.strftime('%Y-%m-%d')}: {str(e)}")
                save_to_json(all_flights)
                continue

        print("Đã hoàn thành việc thu thập dữ liệu")

    finally:
        driver.quit()

class FlightScraperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Scraper")
        self.root.geometry("1200x600+100+100")
        
        self.root.grid_columnconfigure(0, weight=1)  
        self.root.grid_columnconfigure(1, weight=3) 
        self.root.grid_rowconfigure(0, weight=1)
        
        self.log_queue = queue.Queue()
        
        self.paused = False
        self.running = False
        
        self.airport_codes = {
            "Hà Nội": "HAN",
            "Hồ Chí Minh": "SGN",
            "Đà Nẵng": "DAD",
            "Phú Quốc": "PQC",
            "Huế": "HUI",
            "Đà Lạt": "DLI",
        }
        
        self.create_styles()
        
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text="Thủ công")
        
        self.auto_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.auto_tab, text="Tự động")
        
        self.proxy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_tab, text="Proxy")
        
        console_frame = ttk.LabelFrame(right_frame, text="Console", padding="5")
        console_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        self.console = tk.Text(console_frame, wrap=tk.WORD, width=50, height=30)
        console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=console_scrollbar.set)
        
        self.console.grid(row=0, column=0, sticky="nsew")
        console_scrollbar.grid(row=0, column=1, sticky="ns")
        
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)
        
        self.update_options()
        
        self.create_manual_tab()
        self.create_auto_tab()
        self.create_proxy_tab()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.process_logs()

    def create_styles(self):
        style = ttk.Style()
        style.configure('TLabelframe', padding=10)
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=3)
        style.configure('Custom.TButton', padding=10, font=('Helvetica', 10))

    def create_manual_tab(self):
        options_frame = ttk.Frame(self.manual_tab)
        options_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        ttk.Label(options_frame, text="Điểm đi:").grid(row=0, column=0, pady=8, sticky="w")
        self.departure = ttk.Combobox(options_frame, 
                                    values=sorted(list(self.airport_codes.keys())), 
                                    state="readonly", 
                                    width=25)
        self.departure.set("Hà Nội")
        self.departure.grid(row=0, column=1, pady=8, padx=5, sticky="ew")
        
        ttk.Label(options_frame, text="Điểm đến:").grid(row=1, column=0, pady=8, sticky="w")
        self.destination = ttk.Combobox(options_frame, 
                                      values=sorted(list(self.airport_codes.keys())), 
                                      state="readonly", 
                                      width=25)
        self.destination.set("Hồ Chí Minh")
        self.destination.grid(row=1, column=1, pady=8, padx=5, sticky="ew")
        
        self.departure.bind('<<ComboboxSelected>>', self.update_destination_options)
        self.destination.bind('<<ComboboxSelected>>', self.update_departure_options)
        
        ttk.Label(options_frame, text="Ngày bắt đầu:").grid(row=2, column=0, pady=8, sticky="w")
        self.start_date = DateEntry(options_frame, 
                                   width=23,
                                   background='darkblue',
                                   foreground='white',
                                   borderwidth=2,
                                   date_pattern='dd/mm/yyyy',
                                   locale='vi_VN')
        self.start_date.grid(row=2, column=1, pady=8, padx=5, sticky="ew")
        
        ttk.Label(options_frame, text="Số ngày thu thập:").grid(row=3, column=0, pady=8, sticky="w")
        self.num_days = ttk.Spinbox(options_frame, from_=1, to=30, width=23)
        self.num_days.set("7")
        self.num_days.grid(row=3, column=1, pady=8, padx=5, sticky="ew")
        
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(row=4, column=0, columnspan=2, pady=8, sticky="ew")
        
        self.headless = tk.BooleanVar(value=False)
        ttk.Checkbutton(checkbox_frame, text="Chạy ẩn trình duyệt", 
                        variable=self.headless,
                        command=self.toggle_headless).grid(row=0, column=0, sticky="w")
        
        self.close_after = tk.BooleanVar(value=True)
        self.close_browser_checkbox = ttk.Checkbutton(checkbox_frame, 
                                                    text="Đóng trình duyệt sau khi chạy",
                                                    variable=self.close_after)
        self.close_browser_checkbox.grid(row=1, column=0, pady=(5,0), sticky="w")
        
        if self.headless.get():
            self.close_browser_checkbox.configure(state="disabled")
            self.close_after.set(True)
        
        button_frame = ttk.Frame(self.manual_tab) 
        button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.start_button = ttk.Button(button_frame, text="Bắt đầu", 
                                     command=self.start_scraping, style='Custom.TButton')
        self.start_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.pause_button = ttk.Button(button_frame, text="Tạm dừng", 
                                     command=self.toggle_pause, state="disabled",
                                     style='Custom.TButton')
        self.pause_button.grid(row=0, column=1, padx=5, sticky="ew")

    def create_auto_tab(self):
        auto_frame = ttk.Frame(self.auto_tab)
        auto_frame.grid(row=0, column=0, sticky="nsew")
        auto_frame.grid_columnconfigure(0, weight=1)
        
        guide_text = ("Format: ORIGIN-DEST DATE DAYS\n"
                     "Example: HAN-SGN 25/02/2025 7")
        
        guide_label = ttk.Label(auto_frame, text=guide_text, wraplength=300)
        guide_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        file_frame = ttk.Frame(auto_frame)
        file_frame.grid(row=1, column=0, pady=10, sticky="ew")
        
        self.config_path = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.config_path, width=30)
        path_entry.grid(row=0, column=0, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Chọn file", command=self.browse_config)
        browse_btn.grid(row=0, column=1, padx=5)

        task_frame = ttk.LabelFrame(auto_frame, text="Danh sách các task", padding="10")
        task_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        
        self.task_text = tk.Text(task_frame, height=10, width=40)
        scrollbar = ttk.Scrollbar(task_frame, orient="vertical", command=self.task_text.yview)
        self.task_text.configure(yscrollcommand=scrollbar.set)
        
        self.task_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_text.configure(state="disabled")
        
        checkbox_frame = ttk.Frame(auto_frame)
        checkbox_frame.grid(row=3, column=0, pady=10, sticky="w", padx=10)
        
        self.auto_headless = tk.BooleanVar(value=True)
        ttk.Checkbutton(checkbox_frame, text="Chạy ẩn trình duyệt", 
                       variable=self.auto_headless).grid(row=0, column=0, sticky="w")
        
        self.start_auto_btn = ttk.Button(auto_frame, text="Bắt đầu tự động", 
                                       command=self.start_auto_scraping,
                                       style='Custom.TButton')
        self.start_auto_btn.grid(row=4, column=0, pady=20)

    def create_proxy_tab(self):
        proxy_frame = ttk.Frame(self.proxy_tab)
        proxy_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.proxy_type = tk.StringVar(value="off")
        
        ttk.Label(proxy_frame, text="Chọn loại proxy:", 
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, pady=10, sticky="w")
        
        radio_frame = ttk.Frame(proxy_frame)
        radio_frame.grid(row=1, column=0, sticky="w")
        
        ttk.Radiobutton(radio_frame, text="Tắt", 
                       variable=self.proxy_type, 
                       value="off",
                       command=self.update_proxy_options).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ttk.Radiobutton(radio_frame, text="Proxy xoay", 
                       variable=self.proxy_type, 
                       value="rotating",
                       command=self.update_proxy_options).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        ttk.Radiobutton(radio_frame, text="Proxy tĩnh", 
                       variable=self.proxy_type, 
                       value="static",
                       command=self.update_proxy_options).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.rotating_frame = ttk.LabelFrame(proxy_frame, text="Cấu hình proxy xoay", padding=10)
        self.rotating_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        ttk.Label(self.rotating_frame, text="API Key:").grid(row=0, column=0, pady=5, sticky="w")
        self.rotating_api_key = ttk.Entry(self.rotating_frame, width=40)
        self.rotating_api_key.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.rotating_frame, text="Endpoint:").grid(row=1, column=0, pady=5, sticky="w")
        self.rotating_endpoint = ttk.Entry(self.rotating_frame, width=40)
        self.rotating_endpoint.grid(row=1, column=1, pady=5, padx=5)
        
        self.static_frame = ttk.LabelFrame(proxy_frame, text="Cấu hình proxy tĩnh", padding=10)
        self.static_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        ttk.Label(self.static_frame, text="IP:").grid(row=0, column=0, pady=5, sticky="w")
        self.static_ip = ttk.Entry(self.static_frame, width=40)
        self.static_ip.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Port:").grid(row=1, column=0, pady=5, sticky="w")
        self.static_port = ttk.Entry(self.static_frame, width=40)
        self.static_port.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Username:").grid(row=2, column=0, pady=5, sticky="w")
        self.static_username = ttk.Entry(self.static_frame, width=40)
        self.static_username.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Password:").grid(row=3, column=0, pady=5, sticky="w")
        self.static_password = ttk.Entry(self.static_frame, width=40, show="*")
        self.static_password.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Button(proxy_frame, text="Lưu cấu hình", 
                  command=self.save_proxy_config,
                  style='Custom.TButton').grid(row=4, column=0, pady=20)
        
        self.load_saved_proxy_config()
        
        self.update_proxy_options()

    def load_saved_proxy_config(self):
        config = self.get_proxy_config()
        self.proxy_type.set(config.get("type", "off"))
        
        if config["type"] == "rotating":
            self.rotating_api_key.insert(0, config.get("api_key", ""))
            self.rotating_endpoint.insert(0, config.get("endpoint", ""))
        elif config["type"] == "static":
            self.static_ip.insert(0, config.get("ip", ""))
            self.static_port.insert(0, config.get("port", ""))
            self.static_username.insert(0, config.get("username", ""))
            self.static_password.insert(0, config.get("password", ""))

    def update_proxy_options(self):
        proxy_type = self.proxy_type.get()
        
        if proxy_type == "rotating":
            self.rotating_frame.grid()
            self.static_frame.grid_remove()
        elif proxy_type == "static":
            self.rotating_frame.grid_remove()
            self.static_frame.grid()
        else: 
            self.rotating_frame.grid_remove()
            self.static_frame.grid_remove()

    def save_proxy_config(self):
        proxy_type = self.proxy_type.get()
        config = {"type": proxy_type}
        
        if proxy_type == "rotating":
            config.update({
                "api_key": self.rotating_api_key.get(),
                "endpoint": self.rotating_endpoint.get()
            })
        elif proxy_type == "static":
            config.update({
                "ip": self.static_ip.get(),
                "port": self.static_port.get(),
                "username": self.static_username.get(),
                "password": self.static_password.get()
            })
            
        try:
            with open("proxy_config.json", "w") as f:
                json.dump(config, f, indent=4)
            self.log("Đã lưu cấu hình proxy thành công")
        except Exception as e:
            self.log(f"Lỗi khi lưu cấu hình proxy: {str(e)}")

    def get_proxy_config(self):
        try:
            with open("proxy_config.json", "r") as f:
                config = json.load(f)
            return config
        except:
            return {"type": "off"}

    def browse_config(self):
        filename = filedialog.askopenfilename(
            title="Chọn file cấu hình",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.config_path.set(filename)
            self.load_and_display_tasks()

    def load_and_display_tasks(self):
        try:
            with open(self.config_path.get(), 'r', encoding='utf-8') as f:
                tasks = f.readlines()
            
            valid_tasks = []
            invalid_tasks = []
            
            for i, task in enumerate(tasks, 1):
                task = task.strip()
                if not task:
                    continue
                    
                try:
                    route, date, days = task.split()
                    dep, arr = route.split('-')
                    
                    if dep not in self.airport_codes.values() or arr not in self.airport_codes.values():
                        raise ValueError(f"Mã sân bay không hợp lệ: {dep} hoặc {arr}")
                    
                    date_obj = datetime.strptime(date, "%d/%m/%Y")
                    
                    days = int(days)
                    if days <= 0:
                        raise ValueError("Số ngày phải lớn hơn 0")
                    
                    dep_city = next(city for city, code in self.airport_codes.items() if code == dep)
                    arr_city = next(city for city, code in self.airport_codes.items() if code == arr)
                    
                    task_info = {
                        'index': i,
                        'dep': dep,
                        'arr': arr,
                        'dep_city': dep_city,
                        'arr_city': arr_city,
                        'date': date,
                        'days': days
                    }
                    valid_tasks.append(task_info)
                    
                except Exception as e:
                    invalid_tasks.append((i, task, str(e)))
            
            self.task_text.configure(state="normal")
            self.task_text.delete(1.0, tk.END)
            
            self.task_text.insert(tk.END, f"Tổng số task: {len(valid_tasks)}\n")
            self.task_text.insert(tk.END, "=" * 40 + "\n\n")
            
            for task in valid_tasks:
                self.task_text.insert(tk.END, f"Task {task['index']}:\n")
                self.task_text.insert(tk.END, f"- Từ: {task['dep_city']} ({task['dep']})\n")
                self.task_text.insert(tk.END, f"- Đến: {task['arr_city']} ({task['arr']})\n")
                self.task_text.insert(tk.END, f"- Ngày bắt đầu: {task['date']}\n")
                self.task_text.insert(tk.END, f"- Số ngày: {task['days']}\n")
                self.task_text.insert(tk.END, "-" * 30 + "\n")
            
            if invalid_tasks:
                self.task_text.insert(tk.END, "\nCác task không hợp lệ:\n")
                for idx, task, error in invalid_tasks:
                    self.task_text.insert(tk.END, f"Dòng {idx}: {task}\n")
                    self.task_text.insert(tk.END, f"Lỗi: {error}\n")
            
            self.task_text.configure(state="disabled")
            
            self.valid_tasks = valid_tasks
            
            if valid_tasks:
                self.start_auto_btn.configure(state="normal")
            else:
                self.start_auto_btn.configure(state="disabled")
            
        except Exception as e:
            self.log(f"Lỗi khi đọc file cấu hình: {str(e)}")
            self.task_text.configure(state="normal")
            self.task_text.delete(1.0, tk.END)
            self.task_text.insert(tk.END, f"Lỗi khi đọc file: {str(e)}")
            self.task_text.configure(state="disabled")
            self.start_auto_btn.configure(state="disabled")

    def start_auto_scraping(self):
        if not hasattr(self, 'valid_tasks') or not self.valid_tasks:
            self.log("Không có task hợp lệ để thực hiện")
            return
            
        self.start_auto_btn.configure(state="disabled")
        self.notebook.tab(0, state="disabled") 
        self.notebook.tab(2, state="disabled") 
        
        self.running = True
        thread = threading.Thread(target=self.run_auto_tasks, args=(self.valid_tasks,))
        thread.daemon = True
        thread.start()

    def run_auto_tasks(self, tasks):
        try:
            total_tasks = len(tasks)
            for i, task in enumerate(tasks, 1):
                if not self.running:
                    break
                
                self.log("\n" + "="*40)
                self.log(f"Bắt đầu task {i}/{total_tasks}:")
                self.log(f"Từ {task['dep_city']} đến {task['arr_city']}")
                self.log(f"Ngày bắt đầu: {task['date']}, Số ngày: {task['days']}")
                self.log("="*40 + "\n")
                
                update_done = threading.Event()
                
                def update_ui():
                    self.departure.set(task['dep_city'])
                    self.destination.set(task['arr_city'])
                    self.start_date.set_date(datetime.strptime(task['date'], "%d/%m/%Y"))
                    self.num_days.set(str(task['days']))
                    update_done.set()
                
                self.root.after(0, update_ui)
                update_done.wait()
                
                self.current_task_running = True
                
                self.run_scraper_for_task()
                
                while self.current_task_running:
                    time.sleep(1)
                    if not self.running:
                        break
                
                remaining_tasks = total_tasks - i
                self.log(f"\nHoàn thành task {i}/{total_tasks}")
                if remaining_tasks > 0:
                    self.log(f"Còn lại {remaining_tasks} task")
                self.log("="*40)
                
            self.log("\nĐã hoàn thành tất cả các task")
            
        finally:
            self.running = False
            self.paused = False
            
            def enable_buttons():
                self.start_auto_btn.configure(state="normal")
                self.notebook.tab(0, state="normal")
                self.notebook.tab(2, state="normal")
                self.pause_button.configure(state="disabled")
            
            self.root.after(0, enable_buttons)

    def run_scraper_for_task(self):
        try:
            chrome_options = Options()
            if self.auto_headless.get():
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            
            self.setup_proxy_options(chrome_options)

            driver = webdriver.Chrome(options=chrome_options)

            try:
                all_flights = load_existing_data()
                
                driver.get("https://sanvemaybay.vn/")
                time.sleep(3)

                one_way = driver.find_element(By.ID, "one-way")
                one_way.click()
                time.sleep(1)

                departure_input = driver.find_element(By.ID, "depinput")
                departure_input.click()
                time.sleep(1)

                dep_city = self.airport_codes[self.departure.get()]
                choice_departure = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDep']//a[@data-city='{dep_city}']"))
                )
                choice_departure.click()
                self.log(f"Đã chọn điểm đi: {self.departure.get()}")

                destination_input = driver.find_element(By.ID, "desinput")
                destination_input.click()
                time.sleep(1)

                des_city = self.airport_codes[self.destination.get()]
                choice_destination = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDes']//a[@data-city='{des_city}']"))
                )
                
                choice_destination.click()
                self.log(f"Đã chọn điểm đến: {self.destination.get()}")
                
                total_days = int(self.num_days.get())
                for day in range(total_days):
                    remaining_days = total_days - day - 1
                    try:
                        departure_date_input = driver.find_element(By.ID, "depdate")
                        departure_date_input.click()
                        time.sleep(1)

                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ui-datepicker-div"))
                        )

                        current_date = datetime.strptime(self.start_date.get(), "%d/%m/%Y") + timedelta(days=day)
                        date_to_select = str(current_date.day)
                        
                        if day == 0:
                            today = datetime.now()
                            
                            months_diff = (current_date.year - today.year) * 12 + (current_date.month - today.month)
                            
                            self.log(f"Cần chuyển {months_diff} tháng")
                            
                            if months_diff > 0:
                                for _ in range(months_diff):
                                    next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                                    next_button.click()
                                    time.sleep(1)

                        elif date_to_select == "1":
                            next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                            next_button.click()
                            time.sleep(1)

                        date_element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[text()='{date_to_select}']"))
                        )
                        
                        date_element.click()
                        time.sleep(1)
                        self.log(f"Đã chọn ngày: {current_date.strftime('%d/%m/%Y')}")

                        while self.paused:
                            time.sleep(1)
                            continue

                        search_button = driver.find_element(By.ID, "btn-tim-ve")
                        search_button.click()
                        self.log("Đang tìm kiếm chuyến bay...")

                        while self.paused:
                            time.sleep(1)
                            continue

                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "OutBound")))
                        time.sleep(10)

                        flight_rows = driver.find_elements(By.CLASS_NAME, "lineresult-main")

                        flight_date = current_date.strftime("%Y-%m-%d")
                        
                        current_day_flights = []

                        for row in flight_rows:
                            try:
                                flight_code = row.find_element(By.CLASS_NAME, "f_code").text.strip()
                                flight_time = row.find_element(By.CLASS_NAME, "f_time").text.strip()
                                flight_price = row.find_element(By.CLASS_NAME, "f_price").text.strip()

                                flight_info = {
                                    "Ngày bay": flight_date,
                                    "Mã chuyến bay": flight_code,
                                    "Thời gian bay": flight_time,
                                    "Giá vé": flight_price
                                }
                                current_day_flights.append(flight_info)
                                self.log(f"Tìm thấy chuyến bay: {flight_code} - {flight_time} - {flight_price}")
                            except Exception as e:
                                self.log(f"Lỗi khi xử lý chuyến bay: {str(e)}")
                                continue

                        all_flights.extend(current_day_flights)
                        
                        save_to_json(all_flights)
                        
                        self.log(f"Đã lưu dữ liệu cho ngày {flight_date}")
                        self.log(f"Tìm thấy {len(current_day_flights)} chuyến bay")
                        self.log(f"Còn lại {remaining_days} ngày trong task hiện tại")
                        self.log("------------------------")

                    except Exception as e:
                        self.log(f"Lỗi khi xử lý ngày {current_date.strftime('%Y-%m-%d')}: {str(e)}")
                        continue

            finally:
                if self.auto_headless.get():
                    driver.quit()
                    self.log("Đã đóng trình duyệt (chế độ chạy ẩn)")
                else:
                    driver.quit()
                    self.log("Đã đóng trình duyệt sau khi hoàn thành task")

        finally:
            self.current_task_running = False

    def setup_proxy_options(self, chrome_options):
        proxy_config = self.get_proxy_config()
        
        if proxy_config["type"] == "rotating":
            if not proxy_config.get("api_key") or not proxy_config.get("endpoint"):
                self.log("Thiếu thông tin cấu hình proxy xoay")
                return
            
            proxy = f"{proxy_config['endpoint']}?api_key={proxy_config['api_key']}"
            chrome_options.add_argument(f'--proxy-server={proxy}')
            self.log("Đã cấu hình proxy xoay")
            
        elif proxy_config["type"] == "static":
            if not proxy_config.get("ip") or not proxy_config.get("port"):
                self.log("Thiếu thông tin cấu hình proxy tĩnh")
                return
                
            proxy = f"{proxy_config['ip']}:{proxy_config['port']}"
            chrome_options.add_argument(f'--proxy-server={proxy}')
            self.log("Đã cấu hình proxy tĩnh")
            
            if proxy_config.get("username") and proxy_config.get("password"):
                self.log("Đang cấu hình xác thực proxy...")
                manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    }
                }
                """

                background_js = """
                var config = {
                    mode: "fixed_servers",
                    rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: %s
                        }
                    }
                };

                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }

                chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
                );
                """ % (proxy_config['ip'], proxy_config['port'], 
                       proxy_config['username'], proxy_config['password'])

                plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proxy_auth_plugin.zip')
                with zipfile.ZipFile(plugin_path, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                chrome_options.add_extension(plugin_path)
                self.log("Đã cấu hình xác thực proxy")

    def log(self, message):
        self.log_queue.put(message)

    def process_logs(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.console.configure(state="normal")
                self.console.insert(tk.END, message + "\n")
                self.console.see(tk.END)
                self.console.configure(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_logs)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.configure(text="Tiếp tục")
            self.log("Đã tạm dừng quá trình thu thập dữ liệu")
        else:
            self.pause_button.configure(text="Tạm dừng")
            self.log("Đang tiếp tục thu thập dữ liệu")

    def start_scraping(self):
        if not self.running:
            self.running = True
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            self.notebook.tab(1, state="disabled") 
            self.notebook.tab(2, state="disabled")
            
            thread = threading.Thread(target=self.run_scraper)
            thread.daemon = True
            thread.start()

    def update_options(self):
        try:
            encoded_message = "4pWU4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWXCuKVkSAgICAgIFdFTENPTUUgVE8gRkxJR0hUIFNDUkFQRVIgVE9PTCAgICAgIOKVkQrilaDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilaMK4pWRICAgICBHcm91cCAgOiBOaHVjYWl0ZW4gKEdyb3VwIDUpICAgICAgICAg4pWRCuKVkSAgICAgTWVtYmVyczogICAgICAgICAgICAgICAgICAgICAgICAgICAgIOKVkQrilZEgICAgICAg4oCiIE5ndXnhu4VuIMSQ4bupYyBIb8OgbiAgICAgICAgICAgICAgICAgIOKVkQrilZEgICAgICAg4oCiIEhvw6BuZyBOZ+G7jWMgTMawdSDEkOG7qWMgICAgICAgICAgICAgICDilZEK4pWRICAgICAgIOKAoiBOZ3V54buFbiBUaGFuaCBUcsaw4budbmcgVHXhuqVuICAgICAgICAg4pWRCuKVkSAgICAgICDigKIgSHXhu7NuaCDEkOG7qWMgQW5oICAgICAgICAgICAgICAgICAgICDilZEK4pWRICAgICBEZXYgICAgOiBOZ3V54buFbiDEkOG7qWMgSG/DoG4gICAgICAgICAgICAg4pWRCuKVkSAgICAgR2l0aHViIDogaHR0cHM6Ly9zaG9ydC5jb20udm4vbDVlNCAgIOKVkQrilZrilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZ0="
            
            self.console.configure(state="normal")
            decoded_msg = base64.b64decode(encoded_message).decode('utf-8')
            self.console.insert(tk.END, decoded_msg + "\n\n")
            self.console.configure(state="disabled")
            self.console.see(tk.END)
            
        except Exception as e:
            print(f"Lỗi hiển thị thông tin: {str(e)}")

    def run_scraper(self):
        try:
            chrome_options = Options()
            if self.headless.get():
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            
            self.setup_proxy_options(chrome_options)

            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                date_str = self.start_date.get()
                start_date = datetime.strptime(date_str, "%d/%m/%Y")
                self.log(f"Ngày bắt đầu: {start_date.strftime('%d/%m/%Y')}")
            except ValueError as e:
                self.log("Lỗi: Định dạng ngày không hợp lệ")
                return
            
            num_days = int(self.num_days.get())
            
            try:
                all_flights = load_existing_data()
                self.log("Đã tải dữ liệu hiện có")
                
                driver.get("https://sanvemaybay.vn/")
                time.sleep(3)
                self.log("Đã mở trang web thành công")

                while self.paused: 
                    time.sleep(1)
                    continue
                
                one_way = driver.find_element(By.ID, "one-way")
                one_way.click()
                time.sleep(1)
                self.log("Đã chọn vé một chiều")

                while self.paused: 
                    time.sleep(1)
                    continue
                
                departure_input = driver.find_element(By.ID, "depinput")
                departure_input.click()
                time.sleep(1)

                dep_city = self.airport_codes[self.departure.get()]
                choice_departure = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDep']//a[@data-city='{dep_city}']"))
                )
                choice_departure.click()
                self.log(f"Đã chọn điểm đi: {self.departure.get()}")

                destination_input = driver.find_element(By.ID, "desinput")
                destination_input.click()
                time.sleep(1)

                des_city = self.airport_codes[self.destination.get()]
                choice_destination = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDes']//a[@data-city='{des_city}']"))
                )
                
                choice_destination.click()
                self.log(f"Đã chọn điểm đến: {self.destination.get()}")
                
                for day in range(num_days):
                    while self.paused:
                        self.log("Đã tạm dừng. Nhấn 'Tiếp tục' để tiếp tục.")
                        time.sleep(1)
                        continue

                    try:
                        departure_date_input = driver.find_element(By.ID, "depdate")
                        departure_date_input.click()
                        time.sleep(1)

                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ui-datepicker-div"))
                        )
                        current_date = start_date + timedelta(days=day)
                        date_to_select = str(current_date.day)
                        
                        if day == 0:
                            today = datetime.now()
                            
                            months_diff = (start_date.year - today.year) * 12 + (start_date.month - today.month)
                            
                            self.log(f"Cần chuyển {months_diff} tháng")
                            
                            if months_diff > 0:
                                for _ in range(months_diff):
                                    next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                                    next_button.click()
                                    time.sleep(1)

                        elif date_to_select == "1":
                            next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
                            next_button.click()
                            time.sleep(1)

                        date_element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[text()='{date_to_select}']"))
                        )
                        
                        date_element.click()
                        time.sleep(1)
                        self.log(f"Đã chọn ngày: {current_date.strftime('%d/%m/%Y')}")

                        while self.paused:
                            time.sleep(1)
                            continue

                        search_button = driver.find_element(By.ID, "btn-tim-ve")
                        search_button.click()
                        self.log("Đang tìm kiếm chuyến bay...")

                        while self.paused:
                            time.sleep(1)
                            continue

                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "OutBound")))
                        time.sleep(10)

                        flight_rows = driver.find_elements(By.CLASS_NAME, "lineresult-main")

                        flight_date = current_date.strftime("%Y-%m-%d")
                        
                        current_day_flights = []

                        for row in flight_rows:
                            try:
                                flight_code = row.find_element(By.CLASS_NAME, "f_code").text.strip()
                                flight_time = row.find_element(By.CLASS_NAME, "f_time").text.strip()
                                flight_price = row.find_element(By.CLASS_NAME, "f_price").text.strip()

                                flight_info = {
                                    "Ngày bay": flight_date,
                                    "Mã chuyến bay": flight_code,
                                    "Thời gian bay": flight_time,
                                    "Giá vé": flight_price
                                }
                                current_day_flights.append(flight_info)
                                self.log(f"Tìm thấy chuyến bay: {flight_code} - {flight_time} - {flight_price}")
                            except Exception as e:
                                self.log(f"Lỗi khi xử lý chuyến bay: {str(e)}")
                                continue

                        all_flights.extend(current_day_flights)
                        
                        save_to_json(all_flights)
                        
                        self.log(f"Đã lưu dữ liệu cho ngày {flight_date}")
                        self.log(f"Tìm thấy {len(current_day_flights)} chuyến bay")
                        self.log("------------------------")

                    except Exception as e:
                        self.log(f"Lỗi khi xử lý ngày {current_date.strftime('%Y-%m-%d')}: {str(e)}")
                        save_to_json(all_flights)
                        continue

                self.log("Đã hoàn thành việc thu thập dữ liệu")

            except Exception as e:
                self.log(f"Lỗi: {str(e)}")
            finally:
                if self.close_after.get():
                    driver.quit()
                    self.log("Đã đóng trình duyệt")

        finally:
            self.running = False
            self.paused = False
            
            def enable_controls():
                self.start_button.configure(state="normal")
                self.pause_button.configure(state="disabled")
                self.notebook.tab(1, state="normal") 
                self.notebook.tab(2, state="normal") 
            
            self.root.after(0, enable_controls)

    def toggle_headless(self):
        if self.headless.get():
            self.close_browser_checkbox.configure(state="disabled")
            self.close_after.set(True)
        else:
            self.close_browser_checkbox.configure(state="normal")

    def on_closing(self):
        try:
            if self.running:
                if tk.messagebox.askokcancel("Thoát", "Chương trình đang chạy. Bạn có chắc muốn thoát?"):
                    try:
                        import psutil
                        for proc in psutil.process_iter(['name']):
                            try:
                                if 'chrome' in proc.name().lower():
                                    proc.kill()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except ImportError:
                        pass
                    
                    self.running = False
                    self.paused = False
                    
                    self.root.destroy()
                    
                    os._exit(0)
            else:
                self.root.destroy()
                
                os._exit(0)
        except Exception as e:
            print(f"Lỗi khi đóng chương trình: {str(e)}")
            os._exit(1) 

    def update_destination_options(self, event=None):
        current_departure = self.departure.get()
        available_destinations = [city for city in self.airport_codes.keys() if city != current_departure]
        self.destination['values'] = sorted(available_destinations)
        if self.destination.get() == current_departure:
            self.destination.set(available_destinations[0])

    def update_departure_options(self, event=None):
        current_destination = self.destination.get()
        available_departures = [city for city in self.airport_codes.keys() if city != current_destination]
        self.departure['values'] = sorted(available_departures)
        if self.departure.get() == current_destination:
            self.departure.set(available_departures[0])

def main():
    root = tk.Tk()
    app = FlightScraperUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()