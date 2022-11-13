import sqlite3
from core.constants import DIRECTORY_DATA
from os import path
db = sqlite3.connect(path.join(DIRECTORY_DATA, "core", "persistent.db"),
                     isolation_level=None, check_same_thread=False)

db.execute('pragma journal_mode=wal')
