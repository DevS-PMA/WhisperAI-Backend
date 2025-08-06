from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from Backend.database import userData
from Backend.schema import serializeUserCreate
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv ()

secretKey = os.getenv ("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
expire = 5

oauth_schema = HTTPBearer ()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def harshPassword (password: str) -> str:
    return pwd_context.hash (password)

def verifyPassword (plainPassword: str, harshedPassword: str) -> bool:
    return pwd_context.verify (plainPassword, harshedPassword)


async def createToken (data: dict, expires: timedelta = None):
    ex = datetime.utcnow () + (expires or timedelta(minutes=5))
    data.update ({"exp": ex})
    return jwt.encode (data, secretKey, algorithm=algorithm)

async def getCurrentUser (credential: HTTPAuthorizationCredentials = Depends(oauth_schema)):
    token = credential.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token",
        headers={"WWW.Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode (token=token, key=secretKey, algorithms=algorithm)
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception

        user = await userData.find_one ({'_id': ObjectId(id)})
        if not user:
            raise credentials_exception
        return serializeUserCreate (user)
    except JWTError:
        raise credentials_exception