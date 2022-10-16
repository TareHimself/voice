
from turtle import title

from notifypy.notify import Notify
from os import path,getcwd

def SendNotification(title,message):
	notification = Notify()
	notification.application_name = "Voice Assistant"
	notification.title = title
	notification.message = message
	notification.icon = path.join(getcwd(),'assets','icon.png')
	notification.send()