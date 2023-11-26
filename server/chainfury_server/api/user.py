import jwt
from fastapi import HTTPException
from passlib.hash import sha256_crypt
from sqlalchemy.orm import Session
from fastapi import Request, Response, Depends, Header
from typing import Annotated

from chainfury_server.utils import logger, Env
import chainfury_server.database as DB
import chainfury.types as T


def login(auth: T.ApiAuth, db: Session = Depends(DB.fastapi_db_session)):
    user: DB.User = db.query(DB.User).filter(DB.User.username == auth.username).first()  # type: ignore
    if user is not None and sha256_crypt.verify(auth.password, user.password):  # type: ignore
        token = jwt.encode(
            payload=DB.JWTPayload(username=auth.username, user_id=user.id).to_dict(),
            key=Env.JWT_SECRET(),
        )
        return {"msg": "success", "token": token}
    else:
        return {"msg": "failed"}


def sign_up(auth: T.ApiSignUp, db: Session = Depends(DB.fastapi_db_session)):
    user: DB.User = db.query(DB.User).filter(DB.User.username == auth.username).first()  # type: ignore
    user_exists = user is not None
    user: DB.User = db.query(DB.User).filter(DB.User.email == auth.email).first()  # type: ignore
    email_exists = user is not None
    if user_exists and email_exists:
        raise HTTPException(status_code=400, detail="Username and email already registered")
    elif user_exists:
        raise HTTPException(status_code=400, detail="Username is taken")
    elif email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_exists or email_exists:
        return {"msg": "failed"}
    user = DB.User(
        username=auth.username,
        email=auth.email,
        password=sha256_crypt.hash(auth.password),
    )  # type: ignore
    db.add(user)
    db.commit()
    token = jwt.encode(
        payload=DB.JWTPayload(username=auth.username, user_id=user.id).to_dict(),
        key=Env.JWT_SECRET(),
    )
    return {"msg": "success", "token": token}


def change_password(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: T.ApiChangePassword,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    if sha256_crypt.verify(inputs.old_password, user.password):
        password = sha256_crypt.hash(inputs.new_password)
        user.password = password  # type: ignore
        db.commit()
        return T.ApiResponse(message="success")
    else:
        resp.status_code = 400
        return T.ApiResponse(message="password incorrect")
