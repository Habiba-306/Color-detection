# 🎨 Color Picker & Percentage Analyzer

A Python desktop application built with **OpenCV**, **Pandas**, and **Tkinter** that acts as an interactive color eyedropper. Simply double-click anywhere on your image to extract precise RGB values, view color component percentages, and instantly cross-reference the pixel data against a CSV dataset to find the closest matching human-readable color name.

---

## ✨ Features

* **Interactive Eyedropper:** Double-click anywhere on the image preview window to sample exact pixel data in real-time.
* **Smart Color Lookup:** Calculates the Manhattan distance ($|R_1 - R_2| + |G_1 - G_2| + |B_1 - B_2|$) between sampled pixels and a custom CSV database to identify the closest official color name.
* **Component Breakdown:** Computes and displays the exact percentage contributions of Red, Green, and Blue channels within the target pixel.
* **Dynamic UI Overlay:** Generates a custom-padded top banner filled with the sampled color. Automatically adapts the overlay text color (black or white) based on background luminance for optimal readability.

---

## 🛠️ Prerequisites & Installation

Ensure you have **Python 3.8+** installed on your system.

### 1. Setup Project Environment

Save the main script to your project folder.

### 2. Install Dependencies

Install the required computer vision and data manipulation libraries via `pip`:

```bash
pip install opencv-python pandas

```

*(Note: `tkinter` is included directly within standard Python distributions).*

### 3. Setup the Color Dataset

The application relies on an external CSV dataset to map raw RGB values to string names. Ensure you have your dataset file saved at the path targeted by the script:

```text
c:\Users\PMYLS\Desktop\habiba\project AI\venv\colors_dataset.csv

```

*(If your project is running in a different environment or folder structure, update the `dataset_path` variable inside the script to point to your absolute CSV file path).*

#### **Expected CSV Structure (`colors_dataset.csv`)**

The file should contain rows without a header in the following format:

```csv
air_force_blue_raf,Air Force Blue (Raf),#5d8aa8,93,138,168
alice_blue,Alice Blue,#f0f8ff,240,248,255
alizarin_crimson,Alizarin Crimson,#e32636,227,38,54

```

---

## 🚀 Usage

Launch the script directly from your terminal:

```bash
python color_picker.py

```

### Application Controls:

1. **Select File:** A native file explorer dialog will immediately prompt you to open an image (`.jpg`, `.jpeg`, `.png`, or `.bmp`).
2. **Sample Pixels:** Once the OpenCV preview window opens, **double-click the left mouse button** over any area of the image to update the color banner at the top left.
3. **Exit:** Press the **`Esc`** key on your keyboard while focused on the image window to close the application cleanly.

---

## 📝 License

This project is developed for academic purposes at the University of Haripur.
All rights reserved © 2026.
