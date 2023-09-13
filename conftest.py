import os

from typing import Any, Generator

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Playwright,
    sync_playwright, Page,
)

from pages.home import HomePage
from pages.jobs import JobsPage
from pages.login import LoginPage


@pytest.fixture
def playwright() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture
def browser_type(playwright: Playwright, browser_name: str
                 ) -> Generator[BrowserType, None, None]:
    browser_type = None
    if browser_name == "chromium":
        browser_type = playwright.chromium
    elif browser_name == "firefox":
        browser_type = playwright.firefox
    elif browser_name == "webkit":
        browser_type = playwright.webkit
    assert browser_type
    yield browser_type


@pytest.fixture
def browser(browser_type: BrowserType, request) -> Generator[Browser, None, None]:
    browser = browser_type.launch(
        headless=eval(request.config.getini('headless'))
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser, request) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(
        base_url=request.config.getini('base_url')
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext, request):
    new_page = context.new_page()
    yield new_page
    new_page.screenshot(full_page=True, path=f"{os.environ.get('PYTEST_CURRENT_TEST')}.png")
    new_page.close()


@pytest.fixture(autouse=True)
def before_and_after_test(context: BrowserContext):
    text_file = open("cookies.json", "r")
    text_cookies = text_file.read()
    list_dict_cookies = list(eval(text_cookies))
    context.clear_cookies()
    context.add_cookies(list_dict_cookies)
    yield


def pytest_addoption(parser: Any) -> None:
    parser.addini("base_url", help="LinkedIn base url", default=None)
    parser.addini("headless", help="Browser mode", default=True)


@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)


@pytest.fixture
def home_page(page: Page):
    return HomePage(page)


@pytest.fixture
def jobs_page(page: Page):
    return JobsPage(page)