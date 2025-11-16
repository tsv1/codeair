from codeair.api import create_app
from codeair.config import Config as cfg

# Export 'app' so uvicorn can find it when running from CLI:
# uvicorn codeair.start_server:app --host 0.0.0.0 --port 8080 --reload
# This allows uvicorn to import and access the 'app' object from this module
__all__ = ["app"]

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "codeair.start_server:app",
        host=cfg.App.HOST,
        port=cfg.App.PORT,
        reload=cfg.App.DEBUG,
    )
