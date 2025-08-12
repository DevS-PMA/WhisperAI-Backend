from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import timedelta
import os

from Backend.database import userData
from Backend.schema import serializeUserCreate
from Backend.utils import createToken, harshPassword, verifyPassword

# Pydantic model to receive the token from the frontend
class GoogleToken(BaseModel):
    token: str

google_auth_router = APIRouter(prefix="/auth/google", tags=["auth"])

@google_auth_router.post("/login")
async def google_login(google_token: GoogleToken):
    """
    Handles Google Sign-in/Sign-up by verifying the ID token from the frontend.
    """
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID not found in environment variables."
        )

    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            google_token.token,
            requests.Request(),
            google_client_id
        )

        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token."
        )

    # 1. Check if the user exists in the database
    existingUser = await userData.find_one({'email': email})

    if existingUser:
        # User exists, check if they have a Google ID
        if 'googleId' not in existingUser:
            # Existing user signed up with email/password. Link their Google account.
            # This is an optional feature. For this implementation, we will update the user to include the googleId.
            await userData.update_one({'email': email}, {'$set': {'googleId': google_id}})
            existingUser['googleId'] = google_id
            
        existingUser = serializeUserCreate(existingUser)
        
    else:
        # 2. If the user does not exist, create a new user account
        new_user_data = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'googleId': google_id,
            # We don't need a password for Google-signed-up users
            'password': harshPassword("google_auth_placeholder_password")
        }
        result = await userData.insert_one(new_user_data)
        
        # Create a serialized user object for the response
        new_user_data['_id'] = result.inserted_id
        existingUser = serializeUserCreate(new_user_data)
    
    # 3. Create and return a JWT token for the session
    data = {'email': existingUser['email'], 'id': existingUser['id']}
    token = await createToken(data=data, expires=timedelta(minutes=60))

    return {
        'user': data,
        'token': token,
        'token_type': 'Bearer',
        'message': f"Login for {email} successful"
    }