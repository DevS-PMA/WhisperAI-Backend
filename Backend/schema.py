from pydantic import BaseModel, EmailStr

class userCreate (BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str


class userLogin (BaseModel):
    email: EmailStr
    password: str

def serializeUserCreate (data: userCreate) -> dict:
    return {
        'id': str (data['_id']),
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'email': data['email'],
        'password': data['password']
    }
