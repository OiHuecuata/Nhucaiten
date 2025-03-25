from supabase import create_client, Client
from supabase.client import ClientOptions
import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.supabase = None
        self.db_type = "off"
        self.save_interval = 1
        self.days_count = 0
        
    def connect_mysql(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                return True, "Kết nối MySQL thành công!"
        except Error as e:
            return False, f"Lỗi kết nối MySQL: {e}"
            
    def connect_supabase(self, url, key):
        try:
            self.supabase = create_client(
                url, 
                key,
                options=ClientOptions(
                    postgrest_client_timeout=10,
                    storage_client_timeout=10,
                    schema="public",
                )
            )
            return True, "Kết nối Supabase thành công!"
        except Exception as e:
            return False, f"Lỗi kết nối Supabase: {e}"
            
    def main_print(self):
        print("Hoàn Đẹp Trai.")
            
    def save_to_database(self, flights_data):
        if not flights_data:
            return False, "Không có dữ liệu để lưu"
            
        self.days_count += 1
        print(f"[DEBUG] days_count: {self.days_count}, save_interval: {self.save_interval}")
        
        if self.days_count < self.save_interval:
            return True, f"Đợi đủ {self.save_interval} ngày để lưu (hiện tại: {self.days_count})"
            
        try:
            if self.db_type == "mysql":
                if not self.connection or not self.connection.is_connected():
                    return False, "Chưa kết nối MySQL"
                    
                cursor = self.connection.cursor()
                for flight in flights_data:
                    sql = """INSERT INTO flights 
                            (departure, destination, flight_date, airline, 
                             flight_code, flight_time, price) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, tuple(flight.values()))
                self.connection.commit()
                print(f"[DEBUG] Đã lưu vào MySQL")
                
            elif self.db_type == "supabase":
                if not self.supabase:
                    return False, "Chưa kết nối Supabase"
                
                formatted_flights = []
                for flight in flights_data:
                    duration = flight["Thời gian bay"]
                    price_info = flight["Giá vé"]
                    
                    formatted_flight = {
                        "Mã chuyến bay": flight["Mã chuyến bay"],
                        "Ngày bay": flight["Ngày bay"],
                        "Điểm đi": flight["Điểm đi"],
                        "Điểm đến": flight["Điểm đến"],
                        "Hãng bay": flight["Hãng bay"],
                        "Giờ cất cánh": duration[0:5] + ":00",
                        "Giờ hạ cánh": duration[8:13] + ":00",
                        "Giá vé": price_info[:-4].replace(",",""),
                        "Đơn vị": price_info[-3:]
                    }
                    formatted_flights.append(formatted_flight)

                print(f"[DEBUG] Chuẩn bị lưu {len(formatted_flights)} bản ghi lên Supabase")
                self.supabase.table("Flight_Information").upsert(formatted_flights).execute()
                print(f"[DEBUG] Đã lưu thành công lên Supabase")
                
            self.days_count = 0
            return True, f"✅ Đã lưu {len(flights_data)} bản ghi lên {self.db_type.upper()}"
            
        except Exception as e:
            print(f"[DEBUG] Lỗi khi lưu: {str(e)}")
            return False, f"❌ Lỗi lưu dữ liệu: {e}"
            
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def force_save_to_database(self, flights_data):
        if not flights_data:
            return False, "Không có dữ liệu để lưu"
            
        try:
            if self.db_type == "mysql":
                if not self.connection or not self.connection.is_connected():
                    return False, "Chưa kết nối MySQL"
                    
                cursor = self.connection.cursor()
                for flight in flights_data:
                    sql = """INSERT INTO flights 
                            (departure, destination, flight_date, airline, 
                             flight_code, flight_time, price) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, tuple(flight.values()))
                self.connection.commit()
                
            elif self.db_type == "supabase":
                if not self.supabase:
                    return False, "Chưa kết nối Supabase"
                
                formatted_flights = []
                for flight in flights_data:
                    duration = flight["Thời gian bay"]
                    price_info = flight["Giá vé"]
                    
                    formatted_flight = {
                        "Mã chuyến bay": flight["Mã chuyến bay"],
                        "Ngày bay": flight["Ngày bay"],
                        "Điểm đi": flight["Điểm đi"],
                        "Điểm đến": flight["Điểm đến"],
                        "Hãng bay": flight["Hãng bay"],
                        "Giờ cất cánh": duration[0:5] + ":00",
                        "Giờ hạ cánh": duration[8:13] + ":00",
                        "Giá vé": price_info[:-4].replace(",",""),
                        "Đơn vị": price_info[-3:]
                    }
                    formatted_flights.append(formatted_flight)

                print(f"[DEBUG] Chuẩn bị lưu {len(formatted_flights)} bản ghi lên Supabase")
                self.supabase.table("Flight_Information").upsert(formatted_flights).execute()
                print(f"[DEBUG] Đã lưu thành công lên Supabase")
                
            self.days_count = 0
            return True, f"✅ Đã lưu nốt {len(flights_data)} bản ghi còn lại lên {self.db_type.upper()}"
            
        except Exception as e:
            print(f"[DEBUG] Lỗi khi lưu: {str(e)}")
            return False, f"❌ Lỗi lưu dữ liệu: {e}"

def main():
    main = DatabaseManager()
    main.main_print()

if __name__=="__main__":
    main
