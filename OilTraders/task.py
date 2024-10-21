# # tasks.py
# from datetime import datetime, timedelta
# from background_task import background
# from .models import NewEntry
# from .views import send_sms

# @background(schedule=60)  # Schedule this task to run every 60 seconds
# def send_reminders():
#     today = datetime.now().date()
#     entries = NewEntry.objects.all()

#     for entry in entries:
#         next_changing_date = entry.next_changing_date
#         days_since_last_check = (today - next_changing_date).days

#         if days_since_last_check % 10 == 0:
#             message = f"Hi {entry.name}, please check your vehicle readings."
#             send_sms(entry.phone_number, message)
