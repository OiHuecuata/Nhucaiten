import tkinter as tk
from flight_scraper_ui import FlightScraperUI

def main():
    root = tk.Tk()
    app = FlightScraperUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
