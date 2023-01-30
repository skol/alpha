import base64
import os
from datetime import timedelta, datetime

from PIL import Image
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import get_db
from app.models import User, Chat
from app.schemas import UserCreate, TokenData

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "da88bd0c69240d559d950421f945c88980feb7019691781439d8c44a9d47ff35"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _make_avatar_with_resolution(user_id: int, content: bytes, resolution: int = 0):
    """
    Создаем аву с заданным разрешением. Если указан 0, то сохраняем оригинал.
    :param user_id:
    :param content:
    :param resolution:
    :return:
    """
    upload_dir = "{}/../../avatar".format(os.path.dirname(os.path.abspath(__file__)))
    full_path = "{}/img_{}.draft".format(upload_dir, user_id)
    if resolution == 50:
        resolution_str = "_050_"
        MAX_SIZE = (50, 50)
    elif resolution == 100:
        resolution_str = "_100_"
        MAX_SIZE = (100, 100)
    elif resolution == 400:
        resolution_str = "_400_"
        MAX_SIZE = (400, 400)
    else:
        resolution_str = ""
    with open(full_path, "wb") as f:
        f.write(content)
    img = Image.open(full_path)
    extensions = Image.registered_extensions()
    filtered_ext = [ext for ext, fmt in extensions.items() if fmt == img.format]
    img.close()
    if len(filtered_ext) > 0:
        file_ext = filtered_ext[0]
        new_path = "{}/img_{}{}{}".format(upload_dir, user_id, resolution_str, file_ext)
        os.rename(full_path, new_path)
        if resolution > 0:
            img = Image.open(new_path)
            img.thumbnail(MAX_SIZE)
            img.save(new_path)
            img.close()
        return new_path
    return None


def _save_avatar(user: User, content: str):
    image_as_bytes = str.encode(content)
    img_recovered = base64.b64decode(image_as_bytes)
    user.avatar = _make_avatar_with_resolution(user.id, img_recovered, 0)
    if user.avatar:
        user.ava400 = _make_avatar_with_resolution(user.id, img_recovered, 400)
        user.ava100 = _make_avatar_with_resolution(user.id, img_recovered, 100)
        user.ava050 = _make_avatar_with_resolution(user.id, img_recovered, 50)
    return user


def create_user(db: Session, user: UserCreate):
    fake_hashed_password = user.password + "_not_really_hashed"
    db_user = User(phone=user.phone, name=user.name, hashed_password=fake_hashed_password)
    avatar_data = user.avatar
    user.avatar = None
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if avatar_data:
        db_user = _save_avatar(db_user, avatar_data)
        db.commit()
        db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()


def update_user(db: Session, user_id: int, phone: str = None, name: str = None, password: str = None, avatar: str = None) -> User:
    instance: User = db.query(User).filter(User.id == user_id).first()
    update_it = False
    if phone is not None:
        instance.phone = phone
        update_it = True
    if name is not None:
        instance.name = name
        update_it = True
    if password is not None:
        update_it = True
        fake_hashed_password = password + "_not_really_hashed"
        instance.hashed_password = fake_hashed_password
    if avatar:
        instance = _save_avatar(instance, avatar)
        update_it = True
    if update_it:
        db.commit()
    return instance


def set_active_chat(db: Session, user_id: int, chat_id: int) -> User:
    instance: User = db.query(User).filter(User.id == user_id).first()
    chat: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not(chat is None):
        instance.active_chat_id = chat_id
        db.commit()
    return instance


def get_chats(db: Session, user_id: int):
    return db.query(Chat).filter(Chat.members.any(user_id=user_id)).all()


def get_group_chats(db: Session, user_id: int):
    return db.query(Chat).filter(creator_id=user_id).all()


# === примитивная заглушка вместо полноценной авторизации, чтобы запустить проект ===


def verify_password(plain_password, hashed_password):
    return (plain_password + "_not_really_hashed") == hashed_password


def get_password_hash(password):
    return password + "_not_really_hashed"


def authenticate_user(phone: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_phone(db, phone)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception
        token_data = TokenData(phone=phone)
    except JWTError:
        raise credentials_exception
    user = get_user_by_phone(db, token_data.phone)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
