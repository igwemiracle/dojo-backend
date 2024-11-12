from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authenticate.jwt_handler import create_access_token
from models.schemas import RegisterUserSchema, Token
from database.connection import get_db
from routes.crud import get_user_by_email, createRegisteredUser

register = APIRouter()

@register.post("/auth/register", response_model=Token)
async def registerUser(user_data: RegisterUserSchema, db: AsyncSession = Depends(get_db)):
    username = user_data.username
    email = user_data.email
    password = user_data.password
    confirm_password = user_data.confirm_password

    user_exist = await get_user_by_email(email=email, db=db)
    if user_exist:
        return JSONResponse(
            {"error_message": "User with this email already exists. Please use a different email."},
            status_code=status.HTTP_400_BAD_REQUEST
        )  
    if password != confirm_password:
        return JSONResponse(
            {"error_message": "Passwords do not match."},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    access_token = create_access_token(username=username)
    creat_user = await createRegisteredUser(
        username=username,
        email=email,
        hashed_password=password,
        db=db)
    db.add(creat_user)
    await db.commit()
    await db.refresh(creat_user)

    return JSONResponse(
        {
            "redirect_url": f"/account?username={username}&loggedin=True",
            "access_token": access_token,
            "token_type": "Bearer"
         },
        status_code=status.HTTP_201_CREATED
    )