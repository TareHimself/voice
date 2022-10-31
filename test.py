from tkinter import N
import pyautogui
import pyscreeze
from PIL import Image, ImageGrab
import dxcam
import time
import keyboard

key_1_state = 0

key_2_state = 0


def on_press_1(e):
    global key_1_state
    key_1_state = 1


def on_release_1(e):
    global key_1_state
    key_1_state = 0


def on_press_2(e):
    global key_2_state
    key_2_state = 1


def on_release_2(e):
    global key_2_state
    key_2_state = 0


keyboard.on_press_key(key='z', callback=on_press_1)
keyboard.on_press_key(key='x', callback=on_press_2)
keyboard.on_release_key(key='z', callback=on_release_1)
keyboard.on_release_key(key='x', callback=on_release_2)

camera = dxcam.create(output_color='GRAY')
buffer = []
try:
    while True:
        frame = camera.grab()
        if frame is not None:
            mouseX, mouseY = pyautogui.position()
            buffer.append([frame, mouseX, mouseY, key_1_state, key_2_state])
            print('Captured {} frames'.format(len(buffer)), end='\r')
        time.sleep(0.05)

except KeyboardInterrupt as e:
    print('')
    print('Saving {} frames'.format(len(buffer)))
    for i in range(len(buffer)):
        frame, x, y, k1, k2 = buffer[i]
        print(frame)
        Image.fromarray(frame, mode='RGB').save(
            'frames/frame_{}_{}_{}_{}_{}.png'.format(i, x, y, k1, k2))

# image.fromarray().convert('L').show()
# pyscreeze.screenshot('test.png')
# pyautogui.displayMousePosition()
