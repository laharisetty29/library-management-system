from datetime import datetime,timedelta
now=datetime.now()
due=now+datetime.timedelta(days=14)
print("Now:", now)
print("Due Date:" ,due)