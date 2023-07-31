import datetime
import os

from conf.settings import BASE_DIR

print(datetime.date(2021, 1, 1))
delivery_start_time = datetime.time(16, 0)
print(delivery_start_time)
delivery_end_time = datetime.time((delivery_start_time.hour + 2), 0).strftime("%H:%M")
print(delivery_end_time)

current_date = datetime.date.today()
tomorrow = current_date + datetime.timedelta(days=1)

print(tomorrow)

picture_path = os.path.join(BASE_DIR, '/images/cakes/bozhansi.jpeg')
print(picture_path)