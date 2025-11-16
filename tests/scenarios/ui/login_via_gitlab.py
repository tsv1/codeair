import re
from asyncio import sleep

from config import Config as cfg
from contexts import opened_app, registered_user
from vedro import given, scenario, then, when


@scenario("Login via GitLab")
async def _():
    with given:
        page = await opened_app()
        await page.goto("/")

        user = await registered_user()

        # Click "Sign in with GitLab" button
        await page.locator(".button").click()

        # Fill in GitLab login form
        await page.get_by_test_id("username-field").fill(user.username)
        await page.get_by_test_id("password-field").fill(user.password)
        await page.get_by_test_id("sign-in-button").click()

    with when:
        # await page.get_by_test_id("authorization-button").click() - sometimes the button is not found
        await page.evaluate("document.querySelector('form').submit()")

    with then:
        await page.wait_for_url(f"{cfg.APP_URL}/search")

        navbar_text = await page.locator(".navbar-link").inner_text()
        assert navbar_text == user.username
