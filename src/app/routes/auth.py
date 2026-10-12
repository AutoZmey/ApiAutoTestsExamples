from fastapi import APIRouter, Depends, HTTPException, status
from src.app import database
from src.app.models import Token, UserLogin, UserRegister, UserResponse
from src.app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegister):
    existing = database.get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    hashed_pw = hash_password(req.password)
    user = database.create_user(
        email=req.email,
        password_hash=hashed_pw,
        full_name=req.full_name,
        role=req.role or "user",
    )
    return user


@router.post("/login", response_model=Token)
def login(req: UserLogin):
    user_row = database.get_user_by_email(req.email)
    if not user_row or not verify_password(req.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = database.get_user_by_id(user_row["id"])
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )

    return Token(access_token=access_token, token_type="bearer", user=user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
