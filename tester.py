import time

import schedule
import aware_scheduler

if __name__ == "__main__":
    schedule.every().day.at("19:15:00", "America/New_York").do(print, "Time")

    while True:
        schedule.run_pending()
        time.sleep(1)