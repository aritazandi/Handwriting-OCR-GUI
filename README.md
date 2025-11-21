# Handwriting-OCR-GUI
A clean and fast Python desktop application (GUI) for converting user-drawn handwriting into digital text using Tkinter and the Tesseract OCR engine.
## ✨ Key Features

This project is designed to provide an efficient and responsive handwriting-to-text conversion experience:

* **Graphical User Interface (GUI):** Built with **Tkinter** to provide a dedicated, user-friendly interface for drawing and viewing results.
* **Customizable Canvas:** Allows users to draw handwriting with the mouse on a white canvas, featuring **real-time adjustable brush size and color**.
* **Advanced Image Preprocessing:** Utilizes **PIL/OpenCV** to significantly improve handwriting quality before OCR, including:
    * **Smart Scaling:** Intelligent resizing to increase the clarity of drawn characters.
    * **Contrast Enhancement & Sharpening:** Highlighting the strokes against the background.
    * **Thresholding:** Converting the image to a binary black-and-white format for optimal reading by the Tesseract engine.
* **Asynchronous Processing (Threading):** The resource-intensive OCR analysis runs in a **separate thread** to prevent the GUI from freezing, ensuring a smooth user experience.
* **Dedicated Results Panel:** Displays the recognized digital text in a scrollable and distinct area.
