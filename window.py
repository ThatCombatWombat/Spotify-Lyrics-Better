import tkinter as tk

class TransparentTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transparent Text App")
        
        # Set the window size
        self.root.geometry("400x300")
        
        # Make the background color of the window fully transparent
        self.root.configure(bg='black')  # Use a solid color for transparency
        self.root.attributes('-transparentcolor', 'black')  # Make 'black' color transparent
        
        # Create a Label widget with visible text
        self.label = tk.Label(root, text="Hello, Transparent World!", font=("Arial", 24), fg="white", bg="black")
        self.label.pack(expand=True)
        
        # Bind mouse events for window dragging
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)

        # Initial position for dragging
        self.x = 0
        self.y = 0

    def on_click(self, event):
        # Record the initial click position
        self.x = event.x_root
        self.y = event.y_root

    def on_drag(self, event):
        # Calculate the movement delta
        delta_x = event.x_root - self.x
        delta_y = event.y_root - self.y
        
        # Move the window by the delta
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")
        
        # Update the initial position
        self.x = event.x_root
        self.y = event.y_root

if __name__ == "__main__":
    root = tk.Tk()
    app = TransparentTextApp(root)
    root.mainloop()
