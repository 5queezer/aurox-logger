import os

from fastapi import Request
from fastapi.security import APIKeyQuery
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from app.models import AuroxSignal

assert os.getenv('WEBHOOK_PASSWORD')
password = os.getenv('WEBHOOK_PASSWORD')


class APIKeyJson(APIKeyQuery):
    async def __call__(self, request: Request) -> AuroxSignal | None:
        json = await request.json()
        api_key: str = json.get(self.model.name)
        password_mismatch = api_key != password
        if not api_key or password_mismatch:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return AuroxSignal(**json)
