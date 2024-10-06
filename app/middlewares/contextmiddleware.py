from contextvars import ContextVar, Token
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

REQUEST_ID_CTX_KEY = "request_id"

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for generating uniqueid for each request
    Args:
        BaseHTTPMiddleware : starlette base middleware
    """
    _request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)
    
    @staticmethod
    def get_request_id() -> str:
        return RequestContextMiddleware._request_id_ctx_var.get()
    

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = request.headers.get("X-Request-Id", str(uuid4()))
            
        request_id_token = RequestContextMiddleware._request_id_ctx_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            RequestContextMiddleware._request_id_ctx_var.reset(request_id_token)
        
        return response