import tkinter as tk
from tkinter import Canvas, Label, Button
from PIL import Image, ImageTk, ImageSequence
import cv2
import threading
import time

# ==== GIF Handling Thread Class ====
class AnimatedGIF(Label):
    def __init__(self, master, path, delay=100):
        im = Image.open(path)
        seq = []
        try:
            while True:
                seq.append(im.copy())
                im.seek(len(seq))  # Skip to next frame
        except EOFError:
            pass
        self.frames = [ImageTk.PhotoImage(img.resize((200, 200))) for img in seq]
        self.delay = delay
        self.idx = 0
        Label.__init__(self, master, image=self.frames[0], bg='black')
        self.after(self.delay, self.play)

    def play(self):
        self.configure(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self.play)

# ==== OpenCV Tracking ====
def start_tracking(window):
    cap = cv2.VideoCapture(1)
    lower = (29, 86, 6)
    upper = (64, 255, 255)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            for c in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
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

    # Add watermark
    Label(root, text="SOROUSH", fg="white", font=("Helvetica", 8, "italic"), bg="black").place(x=10, y=475)

    # Add animated GIF
    gif = AnimatedGIF(root, "assets/tennis.gif", delay=80)
    gif.place(x=150, y=100)

    # Add start button with fade-in effect
    def show_button():
        start_btn.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    start_btn = Button(root, text="Start", command=lambda: threading.Thread(target=start_tracking, args=(root,), daemon=True).start())
    root.after(2000, show_button)

    root.mainloop()

run_gui()
