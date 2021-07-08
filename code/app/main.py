import io
import cv2 
from typing import List
import uvicorn
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile, Request, Form
from extraction import extract_infos_carte
from pydantic import BaseModel


app = FastAPI()

# La reponse JSON
class Extraction(BaseModel):
    fichier_nom: str
    fichier_type: str
    info_extraites: dict = {}

class inputRequest(BaseModel):
    image_str : str

@app.post("/ocr_upload", response_model=Extraction)
async def extract_upload(file: UploadFile = File(...)):

    # S'assurer que le fichier chargé est une image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, 
                            detail="Le fichier fourni n'est pas une image")

    image_string = await file.read()
    image = cv2.imdecode(np.frombuffer(image_string,
                                       np.uint8), 
                         cv2.IMREAD_COLOR)

    reponse = extract_infos_carte(image)

    return {
        "fichier_nom": file.filename,
        "fichier_type": file.content_type,
        "info_extraites": reponse,
    }

@app.post("/ocr_image_string")
async def extract_string(request: inputRequest):
    image_bytes = request.image_str.encode('ISO-8859-1')
    image_array = np.fromstring(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, 
                         cv2.IMREAD_COLOR)

    return extract_infos_carte(image)


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000)