from config import Config as cfg
from playwright.async_api import Page
from vedro import context
from vedro_pw import created_browser_context

__all__ = ["opened_app"]

@context
async def opened_app() -> Page:
    browser_context = await created_browser_context(base_url=cfg.APP_URL)

    page = await browser_context.new_page()

    return page
