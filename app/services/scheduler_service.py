from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()

def scheduled_forecast_task():
    print(f"Running scheduled forecast at {datetime.now()}")
    # Logic to run forecasts for all active datasets would go here

def init_scheduler():
    scheduler.add_job(func=scheduled_forecast_task, trigger="interval", hours=24)
    scheduler.start()
