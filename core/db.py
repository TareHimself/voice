import sqlite3
from core.constants import DIRECTORY_DATA
from os import path
db = sqlite3.connect(path.join(DIRECTORY_DATA, "core", "persistent.db"))
