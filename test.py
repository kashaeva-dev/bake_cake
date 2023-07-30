import datetime
import os

from conf.settings import BASE_DIR


url = '/images/cakes/bozhansi.jpeg'
picture_path = os.path.join(BASE_DIR, url.lstrip('/'))
print(BASE_DIR)
print(picture_path)