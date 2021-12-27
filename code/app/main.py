import io
import cv2 
from typing import List
import uvicorn
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile, Depends, status,Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from extraction import extract_infos_carte
from pydantic import BaseModel
from utils import load_users, User, verify_user, Token, create_access_token, decode_access_token
import logging
from config import config

logging.basicConfig(format='%(asctime)s %(message)s')
oauth2_scheme = HTTPBearer()
users = load_users(**config)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)):
    """
    Validation du token et extraction de l'utilisateur depuis le token

    :param token: le token d'identification
    :return: le username
    :raise: credentials_exception
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = decode_access_token(credentials.credentials)
        if token_data.username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return token_data.username


app = FastAPI()


# La reponse JSON
class Extraction(BaseModel):
    fichier_nom: str
    fichier_type: str
    info_extraites: dict = {}

class inputRequest(BaseModel):
    image_str : str

class AuthModel(BaseModel):
    username: str
    password: str

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: AuthModel):
    """
    Endpoint de récupération d'un token

    :param form_data: data json contenant 'username' et 'password'
    :return: {"access_token": access_token, "token_type": "bearer"}
    """
    username = verify_user(users, form_data.username, form_data.password)
    if not username:
        logging.info(f'/token - credential errors for user {form_data.username}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(username)
    logging.info(f'/token - token emitted for user {form_data.username}')
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=Token)
async def read_users_me(current_user: User = Depends(get_current_user)):
    logging.info(f'/users/me - {current_user}')
    return {'login': current_user}

@app.post("/ocr_upload", response_model=Extraction)
async def extract_upload(file: UploadFile = File(...), User = Depends(get_current_user)):

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
async def extract_string(request: inputRequest, User = Depends(get_current_user)):
    image_bytes = request.image_str.encode('ISO-8859-1')
    image_array = np.fromstring(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, 
                         cv2.IMREAD_COLOR)

    return extract_infos_carte(image)


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000)