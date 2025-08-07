from fastapi import APIRouter, status, HTTPException
from Backend.database import userData
from Backend.schema import userCreate, userLogin, serializeUserCreate
from Backend.utils import harshPassword, verifyPassword, createToken, getCurrentUser
from datetime import timedelta

auth_router = APIRouter (prefix="/auth", tags=["auth"])

@auth_router.post ("/create")
async def create_account (user: userCreate):
    if userData is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")

    existingUser = await userData.find_one ({'email': user.email})
    if existingUser:
        raise HTTPException (status_code=400, detail=f"Email address {user.email} already in use")

    harshedPassword = harshPassword (user.password)
    user.password = harshedPassword

    result = await userData.insert_one (dict(user))
    return {'message': f"Account {user.email} created successfully"}


@auth_router.post ("/login")
async def login (user: userLogin):
    if userData is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized")

    print (user)
    existingUser = await userData.find_one ({'email': user.email})
    if not existingUser:
        raise HTTPException (status_code=400, detail="Invalid email or password")

    print ("Pass User")
    existingUser = serializeUserCreate (existingUser)

    if not verifyPassword(plainPassword=user.password, harshedPassword=existingUser['password']):
        raise HTTPException (status_code=400, detail="Invalid email or password")

    data = {'email': existingUser['email'], 'firstName': existingUser['firstName'], 'lastName': existingUser['lastName'], 'id': existingUser['id']}
    token = await createToken (data=data, expires=timedelta(minutes=5))

    return {'user': data, 'token': token, 'token_type': 'Bearer', 'message': f"Login to {data['email']} successful"}