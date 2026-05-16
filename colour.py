import cv2
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Suppress the Tkinter root window
Tk().withdraw()

# Prompt the user to select an image file
img_path = askopenfilename(title="Select an Image File", filetypes=[
                           ("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])

if not img_path:
    print("No file selected. Exiting.")
    exit()

# Path to the dataset
dataset_path = r"C:\Users\PMYLS\OneDrive - Higher Education Commission\Desktop\habibaa\project AI\venv\color_detection\colors_dataset.csv"

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
        d = abs(R - int(csv.loc[i, "R"])) + abs(G -
                                                int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
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
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 800, 600)
cv2.setMouseCallback('image', draw_function)

if img is None:
    print("Unable to load the selected image. Please choose a valid image file.")
    exit()

print("Double-click anywhere on the image to get color details. Press Esc to exit.")

while True:
    display_img = img.copy()

    if clicked:
        total_rgb = r + g + b
        if total_rgb == 0:
            red_percentage = green_percentage = blue_percentage = 0.0
        else:
            red_percentage = (r / total_rgb) * 100
            green_percentage = (g / total_rgb) * 100
            blue_percentage = (b / total_rgb) * 100

        color_name = get_color_name(r, g, b)
        hex_value = f'#{r:02X}{g:02X}{b:02X}'
        text = (f'{color_name} | R={r} G={g} B={b} | '
                f'Hex={hex_value} | Red={red_percentage:.1f}% '
                f'Green={green_percentage:.1f}% Blue={blue_percentage:.1f}%')

        (text_width, text_height), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        rectangle_width = min(text_width + 30, display_img.shape[1] - 40)
        rectangle_height = text_height + 20

        cv2.rectangle(display_img, (20, 20), (20 + rectangle_width,
                                              20 + rectangle_height), (b, g, r), -1)

        text_color = (0, 0, 0) if (r + g + b) >= 600 else (255, 255, 255)
        cv2.putText(display_img, text, (30, 45), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, text_color, 1, cv2.LINE_AA)

        print(f'Selected color: {color_name} | R={r} G={g} B={b} | Hex={hex_value} | '
              f'Red={red_percentage:.1f}% Green={green_percentage:.1f}% Blue={blue_percentage:.1f}%')
        clicked = False

    cv2.imshow("image", display_img)

    if cv2.waitKey(20) & 0xFF == 27:
        break

cv2.destroyAllWindows()
