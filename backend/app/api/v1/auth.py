"""
auth.py
Handles user registration and login.
"""
from fastapi import APIRouter, HTTPException, status
import bcrypt
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import create_access_token
from app.core.supabase_client import supabase

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    # Check if email already exists
    existing = supabase.table("users").select("user_id").eq("email", data.email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Insert new user
    new_user = supabase.table("users").insert({
        "full_name": data.full_name,
        "email": data.email,
        "password_hash": hashed_password,
        "phone": data.phone,
        "age": data.age,
        "gender": data.gender,
        "role": "patient"
    }).execute()

    user = new_user.data[0]

    # Create JWT token
    token = create_access_token({
        "sub": user["user_id"],
        "email": user["email"],
        "role": user["role"]
    })

    return TokenResponse(
        access_token=token,
        user_id=user["user_id"],
        full_name=user["full_name"],
        role=user["role"]
    )

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    # Find user by email
    result = supabase.table("users").select("*").eq("email", data.email).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = result.data[0]

    # Verify password
    if not bcrypt.checkpw(data.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token({
        "sub": user["user_id"],
        "email": user["email"],
        "role": user["role"]
    })

    return TokenResponse(
        access_token=token,
        user_id=user["user_id"],
        full_name=user["full_name"],
        role=user["role"]
    )