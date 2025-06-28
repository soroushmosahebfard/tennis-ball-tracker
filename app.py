import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk, ImageSequence
import cv2
import threading
import numpy as np

class TennisBallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tennis Ball Tracker")
        self.root.geometry("700x600")
        self.root.configure(bg='black')

        # Create canvas for OpenCV feed
        self.canvas = tk.Canvas(self.root, width=640, height=480, bg='black')
        self.canvas.pack(pady=20)

        # Load the tennis ball spinning animation
        self.label = Label(self.root, bg='black')
        self.label.place(x=280, y=180)
        self.load_animation("assets/tennis.gif")

        # Start button (hidden initially)
        self.start_btn = Button(self.root, text="Start", font=("Helvetica", 14), command=self.start_tracking)
        self.start_btn.place(x=320, y=500)
        self.start_btn.lower()  # Hide at start

        # Watermark
        self.watermark = Label(self.root, text="SOROUSH", font=("Helvetica", 10, "italic"),
                               fg='white', bg='black')
        self.watermark.place(x=10, y=560)

        # Fade-in start button after 2 sec
        self.root.after(2000, lambda: self.start_btn.lift())

    def load_animation(self, path):
        """Load and animate the spinning tennis ball GIF."""
        self.img = Image.open(path)
        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(self.img)]
        self.frame_idx = 0
        self.animate()

    def animate(self):
        """Play the tennis ball GIF in a loop."""
        self.label.configure(image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.root.after(100, self.animate)

    def start_tracking(self):
        """Start the ball tracking when 'Start' is clicked."""
        self.label.destroy()
        self.start_btn.destroy()
        threading.Thread(target=self.video_loop).start()

    def video_loop(self):
        """The OpenCV camera and ball tracking logic."""
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Mirror the feed
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define tennis ball HSV color range
            lower = np.array([29, 86, 6])
            upper = np.array([64, 255, 255])

            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw circles around detected balls
            for c in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)

            # Add watermark to OpenCV feed
            cv2.putText(frame, "SOROUSH", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)

            # Convert OpenCV frame to Tkinter-compatible format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
            self.canvas.imgtk = imgtk

        cap.release()

# Launch the app
root = tk.Tk()
app = TennisBallApp(root)
root.mainloop()
