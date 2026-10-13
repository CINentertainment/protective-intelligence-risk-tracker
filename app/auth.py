import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app import models
from app.database import get_db


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
AUTH_COOKIE_NAME = "pirt_access_token"

SECRET_KEY = os.getenv(
    "PIRT_SECRET_KEY",
    "development-only-secret-change-before-deployment",
)

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user: models.User,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])
    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise credentials_exception()

    return user_id


def get_current_user(
    request: Request,
    database: Session = Depends(get_db),
) -> models.User:
    token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise credentials_exception()

    user_id = decode_access_token(token)
    user = database.get(models.User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception()

    return user


CurrentUser = Annotated[
    models.User,
    Depends(get_current_user),
]


def require_roles(
    *allowed_roles: str,
) -> Callable:
    def role_checker(
        current_user: CurrentUser,
    ) -> models.User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to perform "
                    "this action."
                ),
            )

        return current_user

    return role_checker