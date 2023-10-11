import os

from typing import Any, Generator

from dotenv import load_dotenv
import openai
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


load_dotenv()


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture
def browser_type(playwright: Playwright, browser_name: str, request
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
def browser(browser_type: BrowserType, request, browser_type_launch_args) -> Generator[Browser, None, None]:
    browser = browser_type.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture
def browser_context_args(browser_context_args):
    if browser_context_args.get("record_video_dir"):
        browser_context_args["record_video_dir"] = "videos/"
    return browser_context_args


@pytest.fixture
def context(browser: Browser, request, browser_context_args) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(
        **browser_context_args
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
def before_and_after_test(context: BrowserContext, request):
    os.environ["BASE_URL"] = request.config.getoption('--base-url')  # it is needed for using in page object classes
    os.environ["PROJECT_PATH"] = str(request.config.rootpath)  # os.path.dirname(os.path.abspath(__file__))
    os.environ["COOKIES_FILE_PATH"] = os.path.join(os.environ["PROJECT_PATH"], "cookies.json")
    os.environ["GOOGLE_CREDENTIALS"] = os.path.join(os.environ["PROJECT_PATH"], "utilities/credentials.json")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if os.path.exists(os.environ["COOKIES_FILE_PATH"]):
        text_file = open(os.environ["COOKIES_FILE_PATH"], "r")
        text_cookies = text_file.read()
        list_dict_cookies = list(eval(text_cookies))
        context.clear_cookies()
        context.add_cookies(list_dict_cookies)
    yield


def pytest_addoption(parser: Any) -> None:
    # the below two options (--env and --profile) are not used meanwhile
    # and are needed just as example how to set a list of available options for environments and profiles
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        help="Application environment under test",
        choices=("qa", "uat", "prod"))
    parser.addoption(
        "--profile", "--p",
        action="store",
        default="smoke",
        help="Configuration of a test set, browser, device, etc",
        choices=("smoke", "regression"))


@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)


@pytest.fixture
def home_page(page: Page):
    return HomePage(page)


@pytest.fixture
def jobs_page(page: Page):
    return JobsPage(page)
