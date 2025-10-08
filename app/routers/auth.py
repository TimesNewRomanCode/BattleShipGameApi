from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegistrationScheme, TokenResponse, RefreshTokenResponse
from app.services.auth import AuthService

from app.core.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/register")
async def registration(
    data: RegistrationScheme,
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
):
    return await service.registration(data, session)


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
    response: Response = Response(),
):
    return await service.login_for_access_token(form_data, session, response)
