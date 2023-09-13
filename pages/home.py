from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate(self):
        self.page.goto('/')
        return self
