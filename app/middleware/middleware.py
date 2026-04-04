"""
中间件配置模块，负责设置和配置应用程序的中间件
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

# from app.middleware.request_logging_middleware import RequestLoggingMiddleware
from app.middleware.smart_routing_middleware import SmartRoutingMiddleware
from app.core.constants import API_VERSION
from app.core.security import verify_auth_token
from app.log.logger import get_middleware_logger

logger = get_middleware_logger()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证中间件，处理未经身份验证的请求
    """

    async def dispatch(self, request: Request, call_next):
        # 允许特定路径绕过身份验证
        if (
            request.url.path not in ["/", "/auth"]
            and not request.url.path.startswith("/static")
            and not request.url.path.startswith("/gemini")
            and not request.url.path.startswith("/v1")
            and not request.url.path.startswith(f"/{API_VERSION}")
            and not request.url.path.startswith("/health")
            and not request.url.path.startswith("/hf")
            and not request.url.path.startswith("/openai")
            and not request.url.path.startswith("/api/version/check")
            and not request.url.path.startswith("/vertex-express")
            and not request.url.path.startswith("/upload")
        ):

            # 从URL参数中获取auth_token
            auth_token = request.query_params.get("key")

            # 如果URL中没有auth_token，从cookies中获取
            if not auth_token:
                auth_token = request.cookies.get("auth_token")

            # 验证auth_token
            if not auth_token or not verify_auth_token(auth_token):
                logger.warning(f"Unauthorized access attempt to {request.url.path}")
                return RedirectResponse(url="/")
            logger.debug("Request authenticated successfully")

        response = await call_next(request)

        # 如果URL中有auth_token，设置cookie以便后续请求使用
        auth_token_from_url = request.query_params.get("key")
        if auth_token_from_url and auth_token_from_url == request.query_params.get("key"):
            response.set_cookie(key="auth_token", value=auth_token_from_url, httponly=True, max_age=3600)

        return response


def setup_middlewares(app: FastAPI) -> None:
    """
    设置应用程序的中间件

    Args:
        app: FastAPI应用程序实例
    """
    # 添加智能路由中间件（必须在认证中间件之前）
    app.add_middleware(SmartRoutingMiddleware)

    # 添加认证中间件
    app.add_middleware(AuthMiddleware)

    # 添加请求日志中间件（可选，默认注释掉）
    # app.add_middleware(RequestLoggingMiddleware)

    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
