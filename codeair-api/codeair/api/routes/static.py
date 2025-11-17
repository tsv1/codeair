from codeair.config import Config
from litestar import Router, get
from litestar.response import File

__all__ = ["static_router"]


@get(["/", "/{path:path}"], exclude_from_auth=True)
async def serve_index() -> File:
    index_path = Config.App.STATIC_DIR / "index.html"
    return File(path=index_path,
                media_type="text/html",
                content_disposition_type="inline")


static_router = Router(
    path="",
    route_handlers=[serve_index],
)
