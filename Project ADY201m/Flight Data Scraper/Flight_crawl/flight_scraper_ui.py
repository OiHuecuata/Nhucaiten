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
import requests
import psutil
from utils import send_telegram_file, send_telegram_message, load_existing_data, save_to_json, save_error_log, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from database_manager import DatabaseManager

class FlightScraperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Scraper")
        self.root.geometry("1200x630+100+100")
        
        wuyrtestfas = ttk.Frame(self.root)
        wuyrtestfas.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,0))
        
        shgfhsdaghj = "ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgQ2jDoG8gbeG7q25nIGLhuqFuIMSR4bq/biB24bubaSBGbGlnaHQgU2NyYXBlciBUb29sIHwgQ8O0bmcgY+G7pSB0aHUgdGjhuq1wIGThu68gbGnhu4d1IGNodXnhur9uIGJheSB8IFBow6F0IHRyaeG7g24gYuG7n2kgTmh1Y2FpdGVuIFRlYW0gKEdyb3VwIDUpICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBNZW1iZXJzOiBOZ3V54buFbiDEkOG7qWMgSG/DoG4gLSBIb8OgbmcgTmfhu41jIEzGsHUgxJDhu6ljIC0gTmd1eeG7hW4gVGhhbmggVHLGsOG7nW5nIFR14bqlbiAtIEh14buzbmggxJDhu6ljIEFuaCB8IERldjogTmd1eeG7hW4gxJDhu6ljIEhvw6Bu"
        try:
            self.wuytwriufgoisfh = base64.b64decode(shgfhsdaghj).decode('utf-8')
        except Exception as e:
            print(f"Lỗi giải mã marquee text: {str(e)}")
            self.wuytwriufgoisfh = "Welcome to Flight Scraper Tool" 
        
        self.iutyiweqrtgewhfg = ttk.Label(wuyrtestfas, text=self.wuytwriufgoisfh, font=('Helvetica', 10))
        self.iutyiweqrtgewhfg.grid(row=0, column=0, sticky="w")
        
        self.kjvshgdsgh = True
        self.ksjgbjkdsgdsf = 0
        self.ksngkjshgaersadofgh = 50 
        
        self.iuweqtsdfhjgb = threading.Thread(target=self.kjlshfgshafgsdaf)
        self.iuweqtsdfhjgb.daemon = True
        self.iuweqtsdfhjgb.start()
        
        self.root.grid_columnconfigure(0, weight=1)  
        self.root.grid_columnconfigure(1, weight=3) 
        self.root.grid_rowconfigure(1, weight=1)
        
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
            "Nha Trang":"NHA",
            "Hải Phòng":"HPH",
            "Cần Thơ":"VCA",
            "Quy Nhơn":"UIH",
            "Thanh Hoá":"THD",
            "Vinh":"VII",
            "Điện Biên":"DIN",
            "Vân Đồn":"VDO",
            "Ban Mê Thuột":"BMV",
            "Pleiku":"PXU",
            "Tuy Hoà":"TBB",
            "Côn Đảo":"VCS",
            "Rạch Giá":"VKG",
            "Đồng Hới":"VDH",
            "Tam Kỳ":"VCL",
            "Cà Mau":"CAH"
        }
        
        self.create_styles()
        
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew") 
        
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew") 
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text="Thủ công ")

        self.auto_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.auto_tab, text=" Tự động ")
        
        self.proxy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_tab, text="  Proxy  ")
        
        self.sql_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sql_tab, text="   SQL   ")
        
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text=" About ")
        
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
        self.create_sql_tab()
        self.asfdgasydfjsafd()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.process_logs()
        
        self.last_processed_message_id = 0
        
        self.telegram_thread = None
        self.telegram_thread_running = False
        self.task = None 

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
        
        ttk.Label(options_frame, text="Thời gian chờ (giây):").grid(row=4, column=0, pady=8, sticky="w")
        self.wait_time = ttk.Spinbox(options_frame, from_=1, to=3600, width=23)
        self.wait_time.set("10")
        self.wait_time.grid(row=4, column=1, pady=8, padx=5, sticky="ew")
        
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(row=5, column=0, columnspan=2, pady=8, sticky="ew")
        
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
        button_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky="ew")
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
        
        status_frame = ttk.LabelFrame(auto_frame, text="Trạng thái task hiện tại", padding=10)
        status_frame.grid(row=1, column=0, pady=10, sticky="ew", padx=10)
        
        ttk.Label(status_frame, text="Task hiện tại:").grid(row=0, column=0, sticky="w", pady=5)
        self.current_task_label = ttk.Label(status_frame, text="Chưa có task nào đang chạy")
        self.current_task_label.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(status_frame, text="Số ngày còn lại:").grid(row=1, column=0, sticky="w", pady=5)
        self.remaining_days_label = ttk.Label(status_frame, text="0")
        self.remaining_days_label.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        file_frame = ttk.Frame(auto_frame)
        file_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        self.config_path = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.config_path, width=30)
        path_entry.grid(row=0, column=0, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Chọn file", command=self.browse_config)
        browse_btn.grid(row=0, column=1, padx=5)

        task_frame = ttk.LabelFrame(auto_frame, text="Danh sách các task", padding="10")
        task_frame.grid(row=3, column=0, pady=10, sticky="nsew")
        
        self.task_text = tk.Text(task_frame, height=10, width=40)
        scrollbar = ttk.Scrollbar(task_frame, orient="vertical", command=self.task_text.yview)
        self.task_text.configure(yscrollcommand=scrollbar.set)
        
        self.task_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_text.configure(state="disabled")
        
        wait_frame = ttk.Frame(auto_frame)
        wait_frame.grid(row=4, column=0, pady=10, sticky="w", padx=10)
        
        ttk.Label(wait_frame, text="Thời gian chờ (giây):").grid(row=0, column=0, padx=5, sticky="w")
        self.auto_wait_time = ttk.Spinbox(wait_frame, from_=1, to=3600, width=10)
        self.auto_wait_time.set("10")
        self.auto_wait_time.grid(row=0, column=1, padx=5)
        
        checkbox_frame = ttk.Frame(auto_frame)
        checkbox_frame.grid(row=5, column=0, pady=10, sticky="w", padx=10)
        
        self.auto_headless = tk.BooleanVar(value=True)
        ttk.Checkbutton(checkbox_frame, text="Chạy ẩn trình duyệt", 
                       variable=self.auto_headless).grid(row=0, column=0, sticky="w")
        
        control_frame = ttk.Frame(auto_frame)
        control_frame.grid(row=7, column=0, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        self.start_auto_btn = ttk.Button(control_frame, text="Bắt đầu tự động", 
                                       command=self.start_auto_scraping,
                                       style='Custom.TButton')
        self.start_auto_btn.grid(row=0, column=0, padx=5, sticky="ew")

        self.pause_auto_btn = ttk.Button(control_frame, text="Tạm dừng", 
                                       command=self.toggle_auto_pause,
                                       state="disabled",
                                       style='Custom.TButton')
        self.pause_auto_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.send_file_btn = ttk.Button(control_frame, text="Gửi file", 
                                      command=self.send_current_file,
                                      style='Custom.TButton')
        self.send_file_btn.grid(row=0, column=2, padx=5, sticky="ew")

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
        self.rotating_api_key = ttk.Entry(self.rotating_frame, width=30)
        self.rotating_api_key.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.rotating_frame, text="Endpoint:").grid(row=1, column=0, pady=5, sticky="w")
        self.rotating_endpoint = ttk.Entry(self.rotating_frame, width=30)
        self.rotating_endpoint.grid(row=1, column=1, pady=5, padx=5)
        
        self.static_frame = ttk.LabelFrame(proxy_frame, text="Cấu hình proxy tĩnh", padding=10)
        self.static_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        ttk.Label(self.static_frame, text="IP:").grid(row=0, column=0, pady=5, sticky="w")
        self.static_ip = ttk.Entry(self.static_frame, width=30)
        self.static_ip.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Port:").grid(row=1, column=0, pady=5, sticky="w")
        self.static_port = ttk.Entry(self.static_frame, width=30)
        self.static_port.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Username:").grid(row=2, column=0, pady=5, sticky="w")
        self.static_username = ttk.Entry(self.static_frame, width=30)
        self.static_username.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(self.static_frame, text="Password:").grid(row=3, column=0, pady=5, sticky="w")
        self.static_password = ttk.Entry(self.static_frame, width=30, show="*")
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
        self.pause_auto_btn.configure(state="normal") 
        self.auto_wait_time.configure(state="disabled")
        self.notebook.tab(0, state="disabled") 
        self.notebook.tab(2, state="disabled") 
        self.notebook.tab(3, state="disabled")
        
        self.running = True
        
        self.start_telegram_monitoring()
        
        thread = threading.Thread(target=self.run_auto_tasks, args=(self.valid_tasks,))
        thread.daemon = True
        thread.start()

    def run_auto_tasks(self, tasks):
        try:
            start_time = datetime.now()
            total_tasks = len(tasks)
            send_telegram_message(f"=======================================")
            send_telegram_message(f"🚀 Bắt đầu quá trình thu thập dữ liệu\n"
                                f"Tổng số task: {total_tasks}\n"
                                f"Thời gian bắt đầu: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")

            all_flights = load_existing_data()
            driver = None

            for i, task in enumerate(tasks, 1):
                if not self.running:
                    break

                task_start_time = datetime.now()
                send_telegram_message(f"📌 Bắt đầu task {i}/{total_tasks}:\n"
                                    f"Từ: {task['dep_city']} đến {task['arr_city']}\n"
                                    f"Ngày bắt đầu: {task['date']}\n"
                                    f"Số ngày: {task['days']}")

                self.log("\n" + "="*40)
                self.log(f"Bắt đầu task {i}/{total_tasks}:")
                self.log(f"Từ {task['dep_city']} đến {task['arr_city']}")
                self.log(f"Ngày bắt đầu: {task['date']}, Số ngày: {task['days']}")
                self.log("="*40 + "\n")

                def update_status():
                    self.current_task_label.config(
                        text=f"Task {i}/{total_tasks}: {task['dep_city']} → {task['arr_city']}"
                    )
                    self.remaining_days_label.config(text=str(task['days']))
                
                self.root.after(0, update_status)

                current_date = datetime.strptime(task['date'], "%d/%m/%Y")
                days_remaining = task['days']

                while days_remaining > 0 and self.running:
                    while self.paused and self.running:
                        time.sleep(1)
                        continue

                    if not self.running:
                        break

                    try:
                        if driver is None:
                            chrome_options = Options()
                            if self.auto_headless.get():
                                chrome_options.add_argument("--headless")
                            chrome_options.add_argument("--disable-gpu")
                            chrome_options.add_argument("--no-sandbox")
                            
                            self.setup_proxy_options(chrome_options)
                            driver = webdriver.Chrome(options=chrome_options)
                            self.log("✅ Đã khởi động trình duyệt thành công")

                            driver.get("https://sanvemaybay.vn/")
                            time.sleep(3)
                            self.log("✅ Đã mở trang web thành công")

                            try:
                                popup_close_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CLASS_NAME, "pum-close"))
                                )
                                popup_close_button.click()
                                self.log("✅ Đã đóng quảng cáo!")
                                time.sleep(2)
                            except Exception:
                                self.log("⚠️ Không tìm thấy popup hoặc đã tự động đóng.")

                            one_way = driver.find_element(By.ID, "one-way")
                            one_way.click()
                            time.sleep(1)
                            self.log("✅ Đã chọn vé một chiều")

                            departure_input = driver.find_element(By.ID, "depinput")
                            departure_input.click()
                            time.sleep(1)

                            choice_departure = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDep']//a[@data-city='{task['dep']}']"))
                            )
                            
                            choice_departure.click()
                            self.log(f"✅ Đã chọn điểm đi: {task['dep_city']}")

                            destination_input = driver.find_element(By.ID, "desinput")
                            destination_input.click()
                            time.sleep(1)

                            choice_destination = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, f"//div[@id='listDes']//a[@data-city='{task['arr']}']"))
                            )
                            choice_destination.click()
                            self.log(f"✅ Đã chọn điểm đến: {task['arr_city']}")

                        try:
                            departure_date_input = driver.find_element(By.ID, "depdate")
                            departure_date_input.click()
                            time.sleep(1)

                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "ui-datepicker-div"))
                            )

                            date_to_select = str(current_date.day)
                            
                            if driver.current_url == "https://sanvemaybay.vn/":  
                                today = datetime.now()
                                months_diff = (current_date.year - today.year) * 12 + (current_date.month - today.month)
                                
                                self.log(f"ℹ️ Cần chuyển {months_diff} tháng")
                                
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
                            self.log(f"✅ Đã chọn ngày: {current_date.strftime('%d/%m/%Y')}")

                            search_button = driver.find_element(By.ID, "btn-tim-ve")
                            search_button.click()
                            self.log("Đang tìm kiếm chuyến bay...")

                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "OutBound")))
                            wait_time = int(self.auto_wait_time.get())
                            self.log(f"Chờ {wait_time} giây trước khi tiếp tục...")
                            time.sleep(wait_time)

                            flight_rows = driver.find_elements(By.CLASS_NAME, "lineresult-main")
                            flight_date = current_date.strftime("%Y-%m-%d")
                            current_day_flights = []

                            self.log("\n" + "-"*50)
                            self.log(f"Các chuyến bay ngày {flight_date}:")
                            self.log("-"*50)

                            for row in flight_rows:
                                try:
                                    flight_code = row.find_element(By.CLASS_NAME, "f_code").text.strip()
                                    flight_time = row.find_element(By.CLASS_NAME, "f_time").text.strip()
                                    flight_price = row.find_element(By.CLASS_NAME, "f_price").text.strip()
                                    
                                    try:
                                        airline_element = row.find_element(By.CLASS_NAME, "airline-name")
                                        airline_name = airline_element.text.strip()
                                    except:
                                        airline_code = flight_code[:2]
                                        airline_name = {
                                            "VN": "Vietnam Airlines",
                                            "VJ": "Vietjet Air",
                                            "BL": "Pacific Airlines",
                                            "QH": "Bamboo Airways",
                                            "VU": "Vietravel Airlines"
                                        }.get(airline_code, "Unknown Airline")
                                        
                                        if flight_code.startswith("VN6"):
                                            airline_name = "Pacific Airlines"

                                    flight_info = {
                                        "Điểm đi": task['dep_city'],
                                        "Điểm đến": task['arr_city'],
                                        "Ngày bay": flight_date,
                                        "Hãng bay": airline_name,
                                        "Mã chuyến bay": flight_code,
                                        "Thời gian bay": flight_time,
                                        "Giá vé": flight_price
                                    }
                                    current_day_flights.append(flight_info)
                                    
                                    self.log(f"🛫 {task['dep_city']} ({task['dep']}) → {task['arr_city']} ({task['arr']})")
                                    self.log(f"{airline_name} - {flight_code}")
                                    self.log(f"Thời gian: {flight_time}")
                                    self.log(f"Giá vé: {flight_price}")
                                    self.log("-"*30)

                                except Exception as e:
                                    self.log(f"Lỗi khi xử lý chuyến bay: {str(e)}")
                                    continue

                            all_flights.extend(current_day_flights)
                            save_to_json(all_flights, self)
                            
                            self.log(f"\nĐã lưu {len(current_day_flights)} chuyến bay cho ngày {flight_date}")
                            if self.db_manager and self.db_manager.db_type != "off":
                                self.log(f"Số ngày đã thu thập: {self.db_manager.days_count}/{self.db_manager.save_interval}")
                            self.log(f"Còn lại {days_remaining - 1} ngày trong task hiện tại")
                            self.log("-"*50 + "\n")

                            current_date += timedelta(days=1)
                            days_remaining -= 1
                            self.root.after(0, lambda: self.remaining_days_label.config(text=str(days_remaining)))

                        except Exception as e:
                            self.log(f"❌ Lỗi khi xử lý ngày {current_date.strftime('%d/%m/%Y')}: {str(e)}")
                            save_error_log(task['dep'], task['arr'], current_date.strftime('%d/%m/%Y'))
                            if driver:
                                driver.quit()
                                driver = None
                                self.log("🔄 Đã đóng trình duyệt để chuẩn bị khởi động lại")
                            current_date += timedelta(days=1)  
                            days_remaining -= 1  
                            self.root.after(0, lambda: self.remaining_days_label.config(text=str(days_remaining)))
                            continue

                    except Exception as e:
                        self.log(f"❌ Lỗi nghiêm trọng: {str(e)}")
                        save_error_log(task['dep'], task['arr'], current_date.strftime('%d/%m/%Y'))
                        if driver:
                            driver.quit()
                            driver = None
                            self.log("🔄 Đã đóng trình duyệt để chuẩn bị khởi động lại")
                        time.sleep(5)
                        continue

                if driver:
                    try:
                        driver.quit()
                    except Exception as e:
                        self.log(f"Lỗi khi đóng trình duyệt: {str(e)}")
                    finally:
                        driver = None
                    self.log(f"✅ Đã hoàn thành task và đóng trình duyệt")

                if self.db_manager and self.db_manager.db_type != "off" and self.db_manager.days_count > 0:
                    all_flights = load_existing_data()
                    success, message = self.db_manager.force_save_to_database(all_flights)
                    if success:
                        self.log(message)
                    else:
                        self.log(f"Lỗi khi lưu dữ liệu cuối: {message}")

            end_time = datetime.now()
            duration = end_time - start_time
            
            final_flights = load_existing_data()
            send_telegram_message(f"🏁 Hoàn thành tất cả các task!\n"
                                f"Tổng thời gian: {duration.total_seconds()/3600:.2f} giờ\n"
                                f"Tổng số bản ghi: {len(final_flights)}")
            send_telegram_message(f"=======================================")

        except Exception as e:
            send_telegram_message(f"❌ Lỗi nghiêm trọng: {str(e)}")
        finally:
            self.running = False
            self.paused = False
            
            def enable_buttons():            
                self.start_auto_btn.configure(state="normal")
                self.pause_auto_btn.configure(state="disabled") 
                self.auto_wait_time.configure(state="normal")
                self.notebook.tab(0, state="normal") 
                self.notebook.tab(2, state="normal") 
                self.notebook.tab(3, state="normal")
            
            self.root.after(0, enable_buttons)

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
            self.log("\n" + "="*40)
            self.log("⏸️ Đã tạm dừng quá trình thu thập dữ liệu")
            self.log("="*40 + "\n")
            send_telegram_message("⏸️ Đã tạm dừng quá trình thu thập dữ liệu")
        else:
            self.pause_button.configure(text="Tạm dừng")
            self.log("\n" + "="*40)
            self.log("▶️ Đang tiếp tục thu thập dữ liệu")
            self.log("="*40 + "\n")
            send_telegram_message("▶️ Đang tiếp tục thu thập dữ liệu")

    def start_scraping(self):
        if not self.running:
            self.running = True
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            self.notebook.tab(1, state="disabled") 
            self.notebook.tab(2, state="disabled")
            
            self.days_remaining = int(self.num_days.get())  
            self.task = None 
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
            days_remaining = self.days_remaining
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

                try:
                    popup_close_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "pum-close"))
                    )
                    popup_close_button.click()
                    self.log("✅ Đã đóng quảng cáo!")
                    time.sleep(2)
                except Exception:
                    self.log("⚠️ Không tìm thấy popup hoặc đã tự động đóng.")

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
                        wait_time = int(self.wait_time.get())
                        self.log(f"Chờ {wait_time} giây trước khi tiếp tục...")
                        time.sleep(wait_time)

                        flight_rows = driver.find_elements(By.CLASS_NAME, "lineresult-main")
                        flight_date = current_date.strftime("%Y-%m-%d")
                        current_day_flights = []

                        self.log("\n" + "-"*50)
                        self.log(f"Các chuyến bay ngày {flight_date}:")
                        self.log("-"*50)

                        for row in flight_rows:
                            try:
                                flight_code = row.find_element(By.CLASS_NAME, "f_code").text.strip()
                                flight_time = row.find_element(By.CLASS_NAME, "f_time").text.strip()
                                flight_price = row.find_element(By.CLASS_NAME, "f_price").text.strip()
                                
                                try:
                                    airline_element = row.find_element(By.CLASS_NAME, "airline-name")
                                    airline_name = airline_element.text.strip()
                                except:
                                    airline_code = flight_code[:2]
                                    airline_name = {
                                        "VN": "Vietnam Airlines",
                                        "VJ": "Vietjet Air",
                                        "BL": "Pacific Airlines",
                                        "QH": "Bamboo Airways",
                                        "VU": "Vietravel Airlines"
                                    }.get(airline_code, "Unknown Airline")
                                    
                                    if flight_code.startswith("VN6"):
                                        airline_name = "Pacific Airlines"

                                flight_info = {
                                    "Điểm đi": dep_city,
                                    "Điểm đến": des_city,
                                    "Ngày bay": flight_date,
                                    "Hãng bay": airline_name,
                                    "Mã chuyến bay": flight_code,
                                    "Thời gian bay": flight_time,
                                    "Giá vé": flight_price
                                }
                                current_day_flights.append(flight_info)
                                
                                self.log(f"🛫 {dep_city} ({dep_city}) → {des_city} ({des_city})")
                                self.log(f"{airline_name} - {flight_code}")
                                self.log(f"Thời gian: {flight_time}")
                                self.log(f"Giá vé: {flight_price}")
                                self.log("-"*30)

                            except Exception as e:
                                self.log(f"Lỗi khi xử lý chuyến bay: {str(e)}")
                                continue

                        all_flights.extend(current_day_flights)
                        save_to_json(all_flights, self)
                        
                        self.log(f"\nĐã lưu {len(current_day_flights)} chuyến bay cho ngày {flight_date}")
                        if self.db_manager and self.db_manager.db_type != "off":
                            self.log(f"Số ngày đã thu thập: {self.db_manager.days_count}/{self.db_manager.save_interval}")
                        self.log(f"Còn lại {days_remaining - 1} ngày trong task hiện tại")
                        self.log("-"*50 + "\n")

                        current_date += timedelta(days=1)
                        days_remaining -= 1
                        self.root.after(0, lambda: self.remaining_days_label.config(text=str(days_remaining)))

                    except Exception as e:
                        self.log(f"❌ Lỗi khi xử lý ngày {current_date.strftime('%d/%m/%Y')}: {str(e)}")

                        save_error_log(self.task['dep'], self.task['arr'], current_date.strftime('%d/%m/%Y'))
                        if driver:
                            driver.quit()
                            driver = None
                            self.log("🔄 Đã đóng trình duyệt để chuẩn bị khởi động lại")
                        current_date += timedelta(days=1) 
                        days_remaining -= 1  
                        self.root.after(0, lambda: self.remaining_days_label.config(text=str(days_remaining)))
                        continue

                if driver:
                    try:
                        driver.quit()
                    except Exception as e:
                        self.log(f"Lỗi khi đóng trình duyệt: {str(e)}")
                    finally:
                        driver = None
                    self.log(f"✅ Đã hoàn thành task và đóng trình duyệt")

                if self.db_manager and self.db_manager.db_type != "off" and self.db_manager.days_count > 0:
                    all_flights = load_existing_data()
                    success, message = self.db_manager.force_save_to_database(all_flights)
                    if success:
                        self.log(message)
                    else:
                        self.log(f"Lỗi khi lưu dữ liệu cuối: {message}")

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
                        self.kjvshgdsgh = False
                        if self.iuweqtsdfhjgb.is_alive():
                            self.iuweqtsdfhjgb.join(timeout=1)
                        
                        self.stop_telegram_monitoring()
                        
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
                self.kjvshgdsgh = False
                if self.iuweqtsdfhjgb.is_alive():
                    self.iuweqtsdfhjgb.join(timeout=1)
                    
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

    def toggle_auto_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_auto_btn.configure(text="Tiếp tục")
            self.log("\n" + "="*40)
            self.log("⏸️ Đã tạm dừng quá trình thu thập dữ liệu")
            self.log("="*40 + "\n")
            send_telegram_message("⏸️ Đã tạm dừng quá trình thu thập dữ liệu")
        else:
            self.pause_auto_btn.configure(text="Tạm dừng")
            self.log("\n" + "="*40)
            self.log("▶️ Đang tiếp tục thu thập dữ liệu")
            self.log("="*40 + "\n")
            send_telegram_message("▶️ Đang tiếp tục thu thập dữ liệu")

    def send_current_file(self):
        send_thread = threading.Thread(target=self.send_telegram_files_threaded)
        send_thread.daemon = True
        send_thread.start()
        
        self.send_file_btn.configure(state="disabled")
        self.root.after(5000, lambda: self.send_file_btn.configure(state="normal"))

    def send_telegram_files_threaded(self):
        try:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            flights = load_existing_data()
            
            self.log("\n" + "="*40)
            self.log("📤 Đang gửi các file dữ liệu đến Telegram...")
            self.log(f"⏰ Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
            self.log("📊 Đang gửi file flights.json...")
            send_telegram_file("flights.json", 
                             f"📊 File dữ liệu hiện tại\n"
                             f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                             f"Tổng số bản ghi: {len(flights)}")
            
            if os.path.exists("error.txt"):
                self.log("⚠️ Đang gửi file error.txt...")
                send_telegram_file("error.txt", 
                                 f"⚠️ File lỗi\n"
                                 f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
            self.log("✅ Đã gửi các file thành công!")
            self.log("="*40 + "\n")
        except Exception as e:
            self.log("\n" + "="*40)
            self.log(f"❌ Lỗi khi gửi file: {str(e)}")
            self.log("="*40 + "\n")

    def create_sql_tab(self):
        self.db_manager = DatabaseManager()
        
        sql_frame = ttk.Frame(self.sql_tab)
        sql_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.db_type = tk.StringVar(value="off")
        ttk.Label(sql_frame, text="Chọn loại database:", 
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, pady=10, sticky="w")
        
        ttk.Radiobutton(sql_frame, text="Tắt", 
                       variable=self.db_type, 
                       value="off",
                       command=self.update_db_options).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        ttk.Radiobutton(sql_frame, text="MySQL (Local)", 
                       variable=self.db_type, 
                       value="mysql",
                       command=self.update_db_options).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        ttk.Radiobutton(sql_frame, text="Supabase (Online)", 
                       variable=self.db_type, 
                       value="supabase",
                       command=self.update_db_options).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.mysql_frame = ttk.LabelFrame(sql_frame, text="Cấu hình MySQL", padding=10)
        self.mysql_frame.grid(row=4, column=0, pady=10, sticky="ew")
        
        ttk.Label(self.mysql_frame, text="Host:").grid(row=0, column=0, pady=5, sticky="w")
        self.mysql_host = ttk.Entry(self.mysql_frame, width=30)
        self.mysql_host.insert(0, "localhost")
        self.mysql_host.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.mysql_frame, text="Database:").grid(row=1, column=0, pady=5, sticky="w")
        self.mysql_db = ttk.Entry(self.mysql_frame, width=30)
        self.mysql_db.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(self.mysql_frame, text="Username:").grid(row=2, column=0, pady=5, sticky="w")
        self.mysql_user = ttk.Entry(self.mysql_frame, width=30)
        self.mysql_user.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(self.mysql_frame, text="Password:").grid(row=3, column=0, pady=5, sticky="w")
        self.mysql_password = ttk.Entry(self.mysql_frame, width=30, show="*")
        self.mysql_password.grid(row=3, column=1, pady=5, padx=5)
        
        self.supabase_frame = ttk.LabelFrame(sql_frame, text="Cấu hình Supabase", padding=10)
        self.supabase_frame.grid(row=5, column=0, pady=10, sticky="ew")
        
        ttk.Label(self.supabase_frame, text="URL:").grid(row=0, column=0, pady=5, sticky="w")
        self.supabase_url = ttk.Entry(self.supabase_frame, width=30)
        self.supabase_url.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.supabase_frame, text="API Key:").grid(row=1, column=0, pady=5, sticky="w")
        self.supabase_key = ttk.Entry(self.supabase_frame, width=30, show="*")
        self.supabase_key.grid(row=1, column=1, pady=5, padx=5)
        
        common_frame = ttk.LabelFrame(sql_frame, text="Cấu hình chung", padding=10)
        common_frame.grid(row=6, column=0, pady=10, sticky="ew")
        
        ttk.Label(common_frame, text="Số ngày thu thập trước khi lưu:").grid(row=0, column=0, pady=5, sticky="w")
        self.save_interval = ttk.Spinbox(common_frame, from_=1, to=100, width=10)
        self.save_interval.set("1")
        self.save_interval.grid(row=0, column=1, pady=5, padx=5)
        
        self.test_conn_btn = ttk.Button(sql_frame, text="Kiểm tra kết nối", 
                                      command=self.test_connection,
                                      style='Custom.TButton')
        self.test_conn_btn.grid(row=7, column=0, pady=20)
        
        self.update_db_options()

    def update_db_options(self):
        db_type = self.db_type.get()
        self.db_manager.db_type = db_type
        self.db_manager.save_interval = int(self.save_interval.get())
        
        if db_type == "mysql":
            self.mysql_frame.grid()
            self.supabase_frame.grid_remove()
            self.test_conn_btn.configure(state="normal")
        elif db_type == "supabase":
            self.mysql_frame.grid_remove()
            self.supabase_frame.grid()
            self.test_conn_btn.configure(state="normal")
        else:
            self.mysql_frame.grid_remove()
            self.supabase_frame.grid_remove()
            self.test_conn_btn.configure(state="disabled")

    def test_connection(self):
        db_type = self.db_type.get()
        success = False
        message = ""
        
        self.db_manager.db_type = db_type
        self.db_manager.save_interval = int(self.save_interval.get())
        
        if db_type == "mysql":
            success, message = self.db_manager.connect_mysql(
                self.mysql_host.get(),
                self.mysql_user.get(),
                self.mysql_password.get(),
                self.mysql_db.get()
            )
        elif db_type == "supabase":
            success, message = self.db_manager.connect_supabase(
                self.supabase_url.get(),
                self.supabase_key.get()
            )
        
        self.log("\n" + "="*40)
        self.log(f"{'✅' if success else '❌'} {message}")
        if success:
            self.log(f"Cấu hình lưu: sau mỗi {self.db_manager.save_interval} ngày")
        self.log("="*40 + "\n")

    def get_last_telegram_message(self):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            response = requests.get(url)
            data = response.json()
            
            if data["ok"] and data["result"]:
                last_message = data["result"][-1]["message"]
                message_id = last_message["message_id"]
                return message_id, last_message.get("text", "")
            return None, ""
        except Exception as e:
            print(f"Lỗi khi lấy tin nhắn Telegram: {str(e)}")
            return None, ""

    def start_telegram_monitoring(self):
        self.telegram_thread_running = True
        self.telegram_thread = threading.Thread(target=self.telegram_monitor_loop)
        self.telegram_thread.daemon = True
        self.telegram_thread.start()

    def stop_telegram_monitoring(self):
        self.telegram_thread_running = False
        if self.telegram_thread:
            self.telegram_thread.join(timeout=1)
            self.telegram_thread = None

    def main_print(self):
        print("Hoàn Đẹp Trai.")

    def telegram_monitor_loop(self):
        while self.telegram_thread_running:
            try:
                message_id, last_message = self.get_last_telegram_message()
                
                if message_id and message_id > self.last_processed_message_id:
                    self.last_processed_message_id = message_id
                    
                    if last_message.startswith("/check"):
                        status_message = (
                            "📊 Trạng thái chương trình:\n"
                            f"🔄 Đang chạy: {'Có' if self.running else 'Không'}\n"
                            f"⏸️ Tạm dừng: {'Có' if self.paused else 'Không'}\n"
                            f"📌 Task hiện tại: {self.current_task_label['text']}\n"
                            f"📅 Số ngày còn lại: {self.remaining_days_label['text']}"
                        )
                        send_telegram_message(status_message)
                        
                    elif last_message.startswith("/file"):
                        self.send_telegram_files_threaded()  
                        
                    elif last_message.startswith("/error"):
                        if os.path.exists("error.txt"):
                            send_telegram_file("error.txt", 
                                             f"⚠️ File lỗi\n"
                                             f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                        else:
                            send_telegram_message("ℹ️ Không có file lỗi")
                
                time.sleep(10)  
                
            except Exception as e:
                print(f"Lỗi trong luồng telegram: {str(e)}")
                time.sleep(10) 

    def asfdgasydfjsafd(self):
        hgjkfdgkfhl = ttk.Frame(self.about_tab)
        hgjkfdgkfhl.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        sdhgfsdafgdsgk = """
        CuKVlOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVkOKVlwrilZEgICAgICAgIEZMSUdIVCBTQ1JBUEVSIFRPT0wgdjIuMCAtIDIwMjUgICAgICAgIOKVkQrilZrilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZDilZ0KCvCfkaUgVEVBTSBOSFVDQUlURU4gKEdST1VQIDUpCuKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAogICDigKIgTmd1eeG7hW4gxJDhu6ljIEhvw6BuCiAgIOKAoiBIb8OgbmcgTmfhu41jIEzGsHUgxJDhu6ljCiAgIOKAoiBOZ3V54buFbiBUaGFuaCBUcsaw4budbmcgVHXhuqVuCiAgIOKAoiBIdeG7s25oIMSQ4bupYyBBbmgKCvCfkrsgVEVDSE5PTE9HSUVTCuKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAogICDigKIgUHl0aG9uICsgU2VsZW5pdW0gKyBUa2ludGVyCiAgIOKAoiBNeVNRTCAvIFN1cGFiYXNlCiAgIOKAoiBUZWxlZ3JhbSBCb3QgSW50ZWdyYXRpb24KICAg4oCiIFByb3h5IFN1cHBvcnQKCvCfk54gQ09OVEFDVArilIDilIDilIDilIDilIDilIDilIDilIDilIAKICAg4oCiIERldiAgICA6IE5ndXnhu4VuIMSQ4bupYyBIb8OgbgogICDigKIgRW1haWwgIDogbmd1eWVuZHVjaG9hbjA1MDFAZ21haWwuY29tCiAgIOKAoiBHaXRodWIgOiBodHRwczovL2dpdGh1Yi5jb20vSG9hbm4wNTAxCgrCqSAyMDI1IEZQVC1BSTE5Qi5BRFkyMDFtCk1hZGUgd2l0aCA8MyBieSBOaHVjYWl0ZW4gVGVhbQo=
        """
        
        try:
            about_text = tk.Text(hgjkfdgkfhl, wrap=tk.WORD, width=50, height=30,
                               font=('Consolas', 10), bg='#f0f0f0', relief=tk.FLAT)
            about_text.grid(row=0, column=0, sticky="nsew")
            
            scrollbar = ttk.Scrollbar(hgjkfdgkfhl, orient="vertical", command=about_text.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            about_text.configure(yscrollcommand=scrollbar.set)
            
            hgjkfdgkfhl.grid_columnconfigure(0, weight=1)
            hgjkfdgkfhl.grid_rowconfigure(0, weight=1)
            
            decoded_content = base64.b64decode(sdhgfsdafgdsgk.strip()).decode('utf-8')
            about_text.insert('1.0', decoded_content)
            about_text.configure(state='disabled') 
            
        except Exception as e:
            error_label = ttk.Label(hgjkfdgkfhl, text=f"Error loading about content: {str(e)}")
            error_label.grid(row=0, column=0, sticky="nsew")

    def kjlshfgshafgsdaf(self):
        while self.kjvshgdsgh:
            try:
                self.ksjgbjkdsgdsf = (self.ksjgbjkdsgdsf + 1) % len(self.wuytwriufgoisfh)
                display_text = self.wuytwriufgoisfh[self.ksjgbjkdsgdsf:] + self.wuytwriufgoisfh[:self.ksjgbjkdsgdsf]
                
                self.root.after(0, lambda t=display_text: self.iutyiweqrtgewhfg.configure(text=t))
                
                time.sleep(self.ksngkjshgaersadofgh / 1000)
            except Exception as e:
                print(f"Lỗi trong marquee thread: {str(e)}")
                time.sleep(1)



if __name__=="__main__":
    root = tk.Tk()
    main = FlightScraperUI(root)
    main.main_print()
