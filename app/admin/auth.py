from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.exceptions import IncorrectEmailOrPasswordException
from app.users.auth import authenticate_user, create_access_token
from app.users.dependenies import get_current_user
from jose import jwt
from app.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        user = await authenticate_user(email, password)
        if user: 
            access_token = create_access_token({"sub": str(user.id), "email":email})
            if jwt.decode(access_token, settings.SECRET_KEY)["role"] == "admin":
                request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False
       
        user = get_current_user(token)

        if not user:
            return False 
         
        return True
    
authentication_backend = AdminAuth(secret_key="...")