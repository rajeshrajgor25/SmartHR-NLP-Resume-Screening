import schedule
import time
import subprocess

def run_job():
    print("🔍 Checking for new HR mails...")
    subprocess.run(["python", "main.py"])

schedule.every(10).minutes.do(run_job)

print("🚀 Auto Resume Scanner started...")
while True:
    schedule.run_pending()
    time.sleep(60)
