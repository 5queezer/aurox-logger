

from starlette import status
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
import time

from starlette.responses import JSONResponse
import logging
logger = logging.getLogger(__name__)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class CatchAllExceptionsMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        info = {
            'headers': dict(zip(request.headers.keys(), request.headers.values())),
            'path_params': dict(zip(request.path_params.keys(), request.path_params.values())),
            'query_params': dict(zip(request.query_params.keys(), request.query_params.values())),
            'method': request.method
        }
        try:
            return await call_next(request)
        except Exception as ex:
            info['status'] = 'error'
            info['exception'] = str(ex)
            logger.error(str(ex))
            return JSONResponse(info)
