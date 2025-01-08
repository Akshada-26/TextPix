import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf
import pyttsx3
import wikipediaapi

class App:
    def __init__(self, master):
        self.master = master
        master.title("Image Search and Description App")

        # Calculate half of the screen size
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        half_width = screen_width // 2
        half_height = screen_height // 2

        # Set the background image
        self.set_background_image()

        # Create GUI components
        self.create_gui(half_width, half_height)

    def create_gui(self, width, height):
        # Container
        self.container = tk.Frame(self.master, width=width, bd=3, relief="solid", bg="#ffffff")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Gradient background
        self.draw_gradient_background()

        # Load Logo and set it as background
        self.load_logo_as_background()

        # Select Image
        self.select_image_button = tk.Button(self.container, text="Select an Image", command=self.select_image)
        self.select_image_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Image Display
        self.selected_image_label = tk.Label(self.container, text="Selected Image:")
        self.selected_image_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.selected_image = tk.Label(self.container)
        self.selected_image.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Predicted Objects
        self.predicted_objects_label = tk.Label(self.container, text="Top Predicted Objects:")
        self.predicted_objects_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.predicted_objects_text = tk.Text(self.container, height=4, width=30)
        self.predicted_objects_text.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Wikipedia Information
        self.wikipedia_info_label = tk.Label(self.container, text="Wikipedia Information:")
        self.wikipedia_info_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Expand the Wikipedia text widget to cover the entire background area
        self.wikipedia_text = tk.Text(self.container, height=14, width=30, wrap=tk.WORD)
        self.wikipedia_text.grid(row=7, column=0, padx=10, pady=10, sticky="wens")
        self.container.grid_rowconfigure(7, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Speak Button
        self.speak_button = tk.Button(self.container, text="Speak", command=self.perform_search_and_speak)
        self.speak_button.grid(row=8, column=0, padx=10, pady=10, sticky="w")

    def set_background_image(self):
        try:
            background_image = Image.open("gui_background.jpg")
            background_image = background_image.resize((self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
            background_photo = ImageTk.PhotoImage(background_image)

            background_label = tk.Label(self.master, image=background_photo)
            background_label.image = background_photo
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Raise the background label to the background
            background_label.lower()
        except FileNotFoundError:
            print("Image file 'gui_background.jpg' not found.")
        except Exception as e:
            print(f"An error occurred while setting the background image: {e}")

    def draw_gradient_background(self):
        # Use a Canvas widget for drawing lines
        gradient_canvas = tk.Canvas(self.container, width=self.container.winfo_reqwidth(), height=self.container.winfo_reqheight())
        gradient_canvas.grid(row=0, column=0, sticky="nsew")

        gradient = ["#FDBB2D", "#3D7EAA", "#86C232", "#F54768"]
        for i in range(400):
            color = gradient[i % 4]
            gradient_canvas.create_line(i, 0, i, gradient_canvas.winfo_height(), fill=color)

    def load_logo_as_background(self):
        try:
            logo_image = Image.open("logo-no-background.png")
            logo_image = logo_image.resize((self.container.winfo_reqwidth(), self.container.winfo_reqheight()))

            # Create a PhotoImage object for the logo
            logo_photo = ImageTk.PhotoImage(logo_image)

            # Create a label for the background image and place it behind other components
            background_label = tk.Label(self.container, image=logo_photo, bg="#ffffff")
            background_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")

            # Raise the background label to the background
            background_label.lower()

            # Keep a reference to the PhotoImage to prevent garbage collection
            background_label.image = logo_photo

        except FileNotFoundError:
            print("Image file 'logo-no-background.png' not found.")
        except Exception as e:
            print(f"An error occurred while loading the logo: {e}")

    def select_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", ".png;.jpg;*.jpeg")])
        if file_path:
            self.display_selected_image(file_path)
            self.predict_and_display_info(file_path)

    def display_selected_image(self, file_path):
        image = Image.open(file_path)
        image.thumbnail((150, 150))
        image_tk = ImageTk.PhotoImage(image)

        self.selected_image.config(image=image_tk)
        self.selected_image.image = image_tk

    def perform_search_and_speak(self):
        try:
            model = tf.keras.applications.MobileNetV2(weights='imagenet')

            # Load and preprocess the selected image
            img = Image.open(self.selected_image_path).resize((224, 224))
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(
                tf.keras.preprocessing.image.img_to_array(img)[tf.newaxis, ...])

            predictions = model.predict(img_array)
            decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]

            # Display predicted objects
            predicted_objects = [label.replace("", " ") for (_, label, _) in decoded_predictions]
            self.predicted_objects_text.delete(1.0, tk.END)
            self.predicted_objects_text.insert(tk.END, "\n".join(predicted_objects))

            # Use the Wikipedia API to fetch information about the top predicted object
            wiki_wiki = wikipediaapi.Wikipedia(
                language='en',
                extract_format=wikipediaapi.ExtractFormat.WIKI,
                user_agent="YourAppName/1.0"
            )
            predicted_object = decoded_predictions[0][1]
            page = wiki_wiki.page(predicted_object)

            # Display Wikipedia information
            if page.exists():
                self.wikipedia_text.delete(1.0, tk.END)
                self.wikipedia_text.insert(tk.END, page.summary)
            else:
                self.wikipedia_text.delete(1.0, tk.END)
                self.wikipedia_text.insert(tk.END, f"No information found for {predicted_object} on Wikipedia.")

            # Speaking the Wikipedia information and predicted objects
            self.text_to_speech(page.summary)
            self.text_to_speech("\n".join(predicted_objects))

        except Exception as e:
            print(f"An error occurred: {e}")

    def text_to_speech(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def predict_and_display_info(self, file_path):
        self.selected_image_path = file_path

        try:
            model = tf.keras.applications.MobileNetV2(weights='imagenet')

            # Load and preprocess the selected image
            img = Image.open(file_path).resize((224, 224))
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(
                tf.keras.preprocessing.image.img_to_array(img)[tf.newaxis, ...])

            predictions = model.predict(img_array)
            decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]

            # Display predicted objects
            predicted_objects = [label.replace("", " ") for (_, label, _) in decoded_predictions]
            self.predicted_objects_text.delete(1.0, tk.END)
            self.predicted_objects_text.insert(tk.END, "\n".join(predicted_objects))

            # Use the Wikipedia API to fetch information about the top predicted object
            wiki_wiki = wikipediaapi.Wikipedia(
                language='en',
                extract_format=wikipediaapi.ExtractFormat.WIKI,
                user_agent="YourAppName/1.0"
            )
            predicted_object = decoded_predictions[0][1]
            page = wiki_wiki.page(predicted_object)

            # Display Wikipedia information
            if page.exists():
                self.wikipedia_text.delete(1.0, tk.END)
                self.wikipedia_text.insert(tk.END, page.summary)
            else:
                self.wikipedia_text.delete(1.0, tk.END)
                self.wikipedia_text.insert(tk.END, f"No information found for {predicted_object} on Wikipedia.")

        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
