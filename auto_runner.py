import schedule
import time
import subprocess
import datetime

def run_job():
    print(f"\n {datetime.datetime.now().strftime('%H:%M:%S')} -  Checking for new HR mails...")
    try:
        subprocess.run(["python", "main.py"], check=True)
        print(" Resume scan completed.\n")
    except subprocess.CalledProcessError as e:
        print(f" Error running main.py: {e}\n")

schedule.every(15).seconds.do(run_job)

print(" Auto Resume Scanner started (Testing Mode - every 15 sec)...")

run_job()

while True:
    schedule.run_pending()
    time.sleep(5)
