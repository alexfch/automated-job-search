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

    def save_cookies_to_file(self, file_name_or_path="cookies.json"):
        file_name_or_path = os.path.join(os.getenv('PROJECT_PATH'), file_name_or_path)
        cookies = str(self.page.context.cookies())
        text_file = open(file_name_or_path, "w")
        text_file.write(cookies)
        text_file.close()
