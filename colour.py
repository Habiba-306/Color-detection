import cv2
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Suppress the Tkinter root window
Tk().withdraw()

# Prompt the user to select an image file
img_path = askopenfilename(title="Select an Image File",
                           filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])

if not img_path:
    print("No file selected. Exiting.")
    exit()

# Path to the dataset
dataset_path = r"c:\Users\PMYLS\Desktop\habiba\project AI\venv\colors_dataset.csv"

# Load the image
img = cv2.imread(img_path)

# Declare global variables
clicked = False
r = g = b = x_pos = y_pos = 0

# Read the CSV file with pandas and assign column names
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv(dataset_path, names=index, header=None)

# Function to calculate the closest matching color name
def get_color_name(R, G, B):
    minimum = 10000
    cname = "Unknown"
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d < minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# Function to capture mouse click and retrieve color
def draw_function(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b, g, r, x_pos, y_pos, clicked
        clicked = True
        x_pos = x
        y_pos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)

# Setup the OpenCV window and bind the mouse callback function
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

while True:
    # Display the image
    cv2.imshow("image", img)

    if clicked:
        # Calculate total RGB value and percentages
        total_rgb = r + g + b
        red_percentage = (r / total_rgb) * 100
        green_percentage = (g / total_rgb) * 100
        blue_percentage = (b / total_rgb) * 100

        # Construct the text to display
        text = (f'{get_color_name(r, g, b)} R={r} G={g} B={b} | '
                f'Red={red_percentage:.1f}% Green={green_percentage:.1f}% Blue={blue_percentage:.1f}%')

        # Calculate the size of the text to dynamically adjust the rectangle width
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        rectangle_width = text_width + 30  # Adding more padding
        rectangle_height = text_height + 20  # Adding more padding to prevent clipping

        # Draw the background rectangle with more padding for visibility
        cv2.rectangle(img, (20, 20), (20 + rectangle_width, 20 + rectangle_height), (b, g, r), -1)

        # Adjust text color for readability against varying background colors
        text_color = (0, 0, 0) if r + g + b >= 600 else (255, 255, 255)

        # Place the text within the rectangle with some margin (adjust y-position as needed)
        cv2.putText(img, text, (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        clicked = False

    # Break the loop if 'Esc' key is pressed
    if cv2.waitKey(20) & 0xFF == 27:
        break

cv2.destroyAllWindows()
