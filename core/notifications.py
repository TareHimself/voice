
from turtle import title

from notifypy.notify import Notify
from os import path, getcwd


def send_notification(title: str, message: str):
    notification = Notify()
    notification.application_name = "Voice Assistant"
    notification.title = title
    notification.message = message
    notification.icon = path.join(getcwd(), 'assets', 'icon.png')
    notification.send()
