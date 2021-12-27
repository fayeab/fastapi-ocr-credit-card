import json
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from passlib.apps import custom_app_context


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def create_access_token(username: str):
    """
    Creer un token d'acces

    Parameters
    ----------
    username : str
        username 
    
    Returns
    -------
    str
        JWT encode
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire, 'scope': 'access_token'}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token):
    """
    Validation du token et extraction de l'utilisateur depuis le token
    
    Parameters
    ----------
    token : str
        Token d'identification

    Returns
    -------
    TokenData
        Username
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data

class User:
    def __init__(self, username, hashed_password=None):
        """
        Classe des Users

        Parameters
        ----------
        username : string
            Nom d'utilisateur
        
        Returns
        -------
        str
            Password hashe
        """
        self.username = username
        self.password_hash = hashed_password

    def hash_password(self, password):
        self.password_hash = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password_hash)


def load_users(path_file_password=None, default_username=None, default_password=None):
    """
    Charger les utilisateurs depuis le fichier config (possibilite d'utiliser une base de donnees) 

    Parameters
    ----------
    path_file_password : string
        path json conntenant users / passwords hashes
    default_username : string
        default username
    default_password : string
        default password
    Returns
    -------
       dict
           Dictionnaire contenant les utilsateurs {username: hashed_pwd}
    """
    try:
        with open(path_file_password) as file:
            passwords = json.load(file)
    except FileNotFoundError:
        passwords = {}
    if default_username and default_password:
        user = User(default_username)
        user.hash_password(default_password)
        passwords[user.username] = user.password_hash
        with open(path_file_password, 'w') as file:
            json.dump(passwords, file)
    return passwords


def verify_user(users, username, password):
    """
    Verifier si l'utilisateur doit acceder a l'application
    
    Parameters
    ----------
    users: dict
        Dictionnaire contenant l'ensemble des utilisateurs de l'application {username: hashed_pwd}
    username : string
        username a verifier
    password :  string
        password non hashé a verifier
    
    Returns
    -------
    boolean
        False ou username
    """
    if username not in users:
        return False
    user = User(username, users[username])
    if not user.verify_password(password):
        return False
    return username


