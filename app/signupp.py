from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine,select
from sqlmodel import SQLModel,Session,Field
from models import Valid_user,User,UserInDB
from dotenv import load_dotenv
# from jose import jwt, JWTError
# to get a string like this run:
# openssl rand -hex 32
import os
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30







ele = os.getenv("db_url")
db_url = ele
db = create_engine(db_url)

def create_table():
    SQLModel.metadata.create_all(db)
create_table()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="loginn")

app = FastAPI()

def get_sess():
    with Session(db) as sess:
        print("started")
        yield sess
        print("sess gonna close")
        
sess = Annotated[Session,Depends(get_sess)]


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str,sess:sess):
    statemnt = select(UserInDB).where(UserInDB.username==username)
    result = sess.exec(statemnt).first()
    return result
    
def get_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("sub")
        return {"user": user}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.post('/loginn')
def login_client(userr:Valid_user,sess:sess):
    ele = get_user(userr.username,sess)
    print(ele)
    # print(ele.model_dump())
    if ele:
        passs = verify_password(userr.password,ele[0].hashed_password)
        if passs:
            token_data = {"sub":ele[0].username}
            access_token = get_token(token_data)
            return {"acces_token":access_token,"token_type":"bearer"}

        else:
            return "worng pass"
    else:
        return "wrong_username"
    

    
@app.post("/create")
def crete_user(user:Valid_user,sess:sess):
    hashpass = get_password_hash(user.password)
    user_in_db = UserInDB(
        username = user.username,
        email = user.email,
        full_name = user.full_name,
        disabled=user.disabled,
        hashed_password=hashpass
    )
    sess.add(user_in_db)
    sess.commit()
    return {"username": user_in_db.username, "email": user_in_db.email, "full_name": user_in_db.full_name}









