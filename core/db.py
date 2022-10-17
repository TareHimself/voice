import sqlite3
from core.constants import DATA_PATH
from os import path
db = sqlite3.connect(path.join(DATA_PATH, "persistent.db"))
