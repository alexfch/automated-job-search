import os
import pathlib

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
    new_page.close()


@pytest.fixture(autouse=True)
def before_and_after_test(context: BrowserContext, request):
    os.environ["BASE_URL"] = request.config.getini('base_url')
    os.environ["PROJECT_PATH"] = str(request.config.rootpath)  # os.path.dirname(os.path.abspath(__file__))
    os.environ["COOKIES_FILE_PATH"] = os.path.join(
        os.getenv('PROJECT_PATH'),
        request.config.getini('cookies_file_name')
    )
    os.environ["JOB_CANDIDATES_FILE_PATH"] = os.path.join(
        os.getenv('PROJECT_PATH'),
        request.config.getini('job_candidates_file_name')
    )
    os.environ["DONT_MATCH_FILE_PATH"] = os.path.join(
        os.getenv('PROJECT_PATH'),
        request.config.getini('dont_match_file_name')
    )

    text_file = open(os.environ["COOKIES_FILE_PATH"], "r")
    text_cookies = text_file.read()
    list_dict_cookies = list(eval(text_cookies))
    context.clear_cookies()
    context.add_cookies(list_dict_cookies)
    yield


def pytest_addoption(parser: Any) -> None:
    parser.addini("headless", help="Browser mode", default=True)
    parser.addini("cookies_file_name", help="Cookies file name", default=None)
    parser.addini("cookies_file_name", help="Cookies file name", default=True)
    parser.addini("job_candidates_file_name", help="Job candidates file name", default=True)
    parser.addini("dont_match_file_name", help="Don't match file name", default=True)
    parser.addini("alluredir", help="Allure report directory", default=None)


@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)


@pytest.fixture
def home_page(page: Page):
    return HomePage(page)


@pytest.fixture
def jobs_page(page: Page):
    return JobsPage(page)
