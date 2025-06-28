import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import cv2
import threading

class TennisBallTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tennis Ball Tracker")
        self.root.configure(bg="black")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Canvas for video feed
        self.canvas = tk.Canvas(root, width=600, height=400, bg="black", highlightthickness=1, highlightbackground="white")
        self.canvas.pack()

        # Copyright label
        self.copyright = tk.Label(root, text="SOROUSH", font=("Arial", 9, "italic"),
                                  fg="white", bg="black")
        self.copyright.place(x=10, y=480)

        # Load and animate GIF
        self.gif = Image.open("tennis.gif")
        self.frames = [ImageTk.PhotoImage(img.resize((150, 150))) for img in ImageSequence.Iterator(self.gif)]
        self.gif_index = 0
        self.label_gif = tk.Label(root, bg="black")
        self.label_gif.place(relx=0.5, rely=0.5, anchor="center")
        self.animate_gif()

        # Start button (fade-in after 2 seconds)
        self.start_button = ttk.Button(root, text="Start", command=self.start_app)
        self.root.after(2000, lambda: self.start_button.place(relx=0.5, rely=0.85, anchor="center"))

    def animate_gif(self):
        self.label_gif.configure(image=self.frames[self.gif_index])
        self.gif_index = (self.gif_index + 1) % len(self.frames)
        self.root.after(100, self.animate_gif)

    def start_app(self):
        self.label_gif.destroy()
        self.start_button.destroy()
        self.track_tennis_ball()

    def track_tennis_ball(self):
        cap = cv2.VideoCapture(0)  # Change index if needed
        lower = (29, 86, 30)
        upper = (64, 255, 255)

        def loop():
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                frame = cv2.resize(frame, (600, 400))
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for c in contours:
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    if radius > 10:
                        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(rgb))
                self.canvas.imgtk = img
                self.canvas.create_image(0, 0, anchor="nw", image=img)

        threading.Thread(target=loop, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = TennisBallTrackerApp(root)
    root.mainloop()
