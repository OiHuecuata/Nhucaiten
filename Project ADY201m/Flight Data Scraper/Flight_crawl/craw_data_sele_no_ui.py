from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime, timedelta

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
    # chrome_options.add_argument("--headless")

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

def main():
    start_date = datetime(2025, 4, 27)  
    
    num_days = 7 
    
    search_flights(start_date, num_days)

if __name__ == "__main__":
    main()

# Craw data with terminal only
# Can't run automatic
# Use for explain my project idea
