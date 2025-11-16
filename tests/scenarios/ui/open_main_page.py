from contexts import opened_app
from vedro import given, scenario, then, when


@scenario("Open main page")
async def _():
    with given:
        page = await opened_app()

    with when:
        await page.goto("/")

    with then:
        assert await page.title() == "CodeAir"

        title_element = page.locator(".title")
        assert await title_element.text_content() == "Welcome to CodeAir"

        button_element = page.locator(".button")
        assert await button_element.text_content() == "Sign in with GitLab"
