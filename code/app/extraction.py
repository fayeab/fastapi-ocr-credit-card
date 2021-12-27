import cv2
import regex
import imutils
import pytesseract

type_carte = {"4": "Visa",
              "5": "MasterCard"}


def extract_infos_carte(image):
    # Convert from BGR to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Binariser l'image 
    ret, thresh = cv2.threshold(hsv[:, :, 1], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Trouver les contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)
    # Trouver les contours de la surface maximumal
    c = max(cnts, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    thresh_card = thresh[y:y+h, x:x+w].copy()
    # OCR
    res_ocr = pytesseract.image_to_string(thresh_card)
    pattern = r'\d{16}'
    textes = [x.replace(" ", "")
                 for x in res_ocr.split('\n') if len(x.strip()) > 0]
    textes = [texte for texte in textes  if regex.match(pattern, texte)]
    res = {}
    if textes:
        carte_num = textes[0]
        carte_type = type_carte.get(carte_num[0])
        res['carte_num'] = carte_num
        res['carte_type'] = carte_type
    return res
