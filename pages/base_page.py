import os
import pathlib

from playwright.sync_api import Page

from modules.main_menu import MainMenu
from modules.filtering import FiltersPanel


class BasePage:

    def __init__(self, page: Page) -> None:
        self.page = page
        self.main_menu = MainMenu(page)
        self.filters_panel = FiltersPanel(page)

    def save_cookies_to_file(self):
        cookies = str(self.page.context.cookies())
        text_file = open(os.environ["COOKIES_FILE_PATH"], "w")
        text_file.write(cookies)
        text_file.close()
