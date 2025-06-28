import tkinter as tk
from tkinter import Canvas, Label, Button
from PIL import Image, ImageTk, ImageSequence
import cv2
import threading
import numpy as np
import time

# ==== GIF Handling Thread Class ====
class AnimatedGIF(Label):
    def __init__(self, master, path, delay=100):
        im = Image.open(path)
        seq = []
        try:
            while True:
                seq.append(im.copy())
                im.seek(len(seq))
        except EOFError:
            pass
        self.frames = [ImageTk.PhotoImage(img.resize((500, 400))) for img in seq]
        self.delay = delay
        self.idx = 0
        Label.__init__(self, master, image=self.frames[0], bg='black')
        self.after(self.delay, self.play)

    def play(self):
        self.configure(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self.play)

# ==== OpenCV Tracking Using Specific Algorithm ====
def start_tracking(window):
    lower_color = np.array([29, 86, 6])
    upper_color = np.array([64, 255, 255])
    cap = cv2.VideoCapture(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        blurred = cv2.GaussianBlur(frame, (9, 9), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower_color, upper_color)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0 and radius > 8:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        cv2.imshow("Tennis Ball Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ==== GUI Setup ====
def run_gui():
    root = tk.Tk()
    root.title("Tennis Ball Tracker")
    root.geometry("500x500")
    root.configure(bg="black")

    Label(root, text="SOROUSH", fg="white", font=("Helvetica", 8, "italic"), bg="black").place(x=10, y=475)
    gif = AnimatedGIF(root, "assets/tennis.gif", delay=80)
    gif.place(x=0, y=0)

    def show_button():
        start_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    def launch_tracking():
        threading.Thread(target=start_tracking, args=(root,), daemon=True).start()

    start_btn = Button(root, text="Start", command=launch_tracking)
    root.after(2000, show_button)

    root.mainloop()

run_gui()
