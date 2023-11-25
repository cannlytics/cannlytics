
# Standard imports:
from datetime import datetime
import os
from typing import Any, Optional

# External imports:
import cv2
from PIL import Image
import numpy as np
try:
    from pyzbar import pyzbar
except:
    print('Unable to import `zbar` library. This tool is used for decoding QR codes.')


def scan_qr_code(
        filename: Any,
        width: Optional[int] = 1024,
        temp_path: Optional[str] = '/tmp'
    ) -> str:
    """Scan an image for a QR code or barcode and return any data.
    Args:
        filename (str): A path to an image with a barcode or qr code.
        width (int): The base width to resize the image.
        temp_path (str): The path to store temporary files.
    Returns:
        (str): Returns the data from the decoded QR code.
    """
    # Handle the filename.
    if isinstance(filename, str):
        image = cv2.imread(filename)
    elif isinstance(filename, np.ndarray):
        image = filename
    else:
        try:
            image = cv2.imread(filename.filename)
        except:
            raise ValueError('`filename` must be a string or Image.')
    
    # Handle invalid images.
    if image is None:
        raise ValueError('`filename` must be a valid image.')

    # If the temp path has any extension, then use it as the outfile.
    if os.path.splitext(temp_path)[1] != '':
        outfile = temp_path

    # Otherwise, create a temporary file to store the image.
    else:
        if not os.path.exists(temp_path): os.makedirs(temp_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        outfile = os.path.join(temp_path, f'{timestamp}.png')

    # Load the image, apply grayscale, Gaussian blur, and Otsu's threshold.
    # Use morphology to find and connect text contours.
    # Finally, filter for any QR code.
    qr_code_found = False
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)
        area = cv2.contourArea(c)
        ar = w / float(h)
        if len(approx) == 4 and area > 1000 and (ar > .85 and ar < 1.3):
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 3)
            cv2.imwrite(outfile, original[y: y + h, x: x + w])
            qr_code_found = True

    # If a QR code was not found, then return None.
    if not qr_code_found:
        return None

    # If a width is given, then resize the image to facilitate
    # QR code reading. Calculates the height based on the new width
    # and the original aspect ratio.
    if width:
        img = Image.open(outfile)
        w_percent = (width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        img.save(outfile)

    # Read the resized image again (important) and try to decode QR codes.
    code = None
    image = Image.open(outfile)
    codes = pyzbar.decode(image)
    if codes:
        code = codes[0].data.decode('utf-8')
    return code
