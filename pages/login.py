import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
        self.email_or_phone_input = page.locator("#session_key")
        self.password_input = page.locator("#session_password")
        self.sign_in_button = page.locator("button[data-id=sign-in-form__submit-btn]")

    def navigate(self):
        self.page.goto('/')
        return self

    def sign_in(self, email_or_phone: str, password: str) -> None:
        self.email_or_phone_input.fill(email_or_phone)
        self.password_input.fill(password)
        self.sign_in_button.click()
        expect(self.page).to_have_title(re.compile(r".* Feed | LinkedIn"))

    def close(self):
        self.page.close()
