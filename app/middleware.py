from starlette.middleware.base import BaseHTTPMiddleware
import time

from starlette.responses import JSONResponse, Response
import logging
logger = logging.getLogger()


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
            'url': str(request.url),
            'method': request.method
        }
        try:
            return await call_next(request)
        except Exception as ex:
            info['status'] = 'error'
            info['type'] = repr(ex)
            info['exception'] = ex.__dict__
            logger.error(ex.__dict__)
            return JSONResponse(info)

