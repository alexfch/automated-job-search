import re
import time
import typing

from playwright.sync_api import Page, expect


class FiltersPanel:

    def __init__(self, page: Page):
        self._page = page
        self._panel_locator = '#search-reusables__filters-bar'
        self._date_posted = page.locator(
            f"{self._panel_locator} div[data-basic-filter-parameter-name='timePostedRange']")
        self._experience_level = page.locator(
            f"{self._panel_locator} div[data-basic-filter-parameter-name='experience']")
        self._all_filters = page.locator(
            f"{self._panel_locator} button[aria-label^='Show all filters']")

    def show_all_filters(self):
        self._all_filters.click()
        return AllFiltersPanel(self._page)


class AllFiltersPanel:

    def __init__(self, page: Page):
        self._page = page
        self._panel = page.locator("div[data-test-modal-container]")
        self._show_results = self._panel.locator("button", has_text=re.compile("Show.*result?"))

    def set_filter(self, label, options: str | list, skip_if_absent: bool = True):
        single_option = options[0] if isinstance(options, list) else options

        filter_item = AllFiltersItem(self._page, label)

        if filter_item.is_of_role("checkbox"):
            filter_item.check(options, skip_if_absent)
        elif filter_item.is_of_role("radio"):
            filter_item.select(single_option, skip_if_absent)
        elif filter_item.is_of_role("switch"):
            filter_item.switch(single_option)
        else:
            Exception("Unknown type of filter item")
        return self

    def show_results(self):
        self._show_results.click()
        expect(self._panel).not_to_be_visible()


class AllFiltersItem:

    def __init__(self, page: Page, item_label):
        self._panel_locator = "div[data-test-modal-container]"
        self._category = page \
            .locator(f"{self._panel_locator} fieldset", has_text=item_label)
        self._available_options = self._category.locator("input").all()

    def is_of_role(self, role):
        return len(self._category.get_by_role(role).all()) > 0

    def select(self, option: str, skip_if_absent: bool):
        element = self._category.get_by_label(option)
        if not element.is_visible() and skip_if_absent:
            return
        for i in range(3):
            element.dispatch_event("click")
            if element.is_checked():
                break
            time.sleep(0.5)

    def check(self, options_to_check: str | list, skip_if_absent: bool):
        for element in self._available_options:
            element.uncheck()

        if isinstance(options_to_check, str):
            self.select(options_to_check, skip_if_absent)
        else:
            for option in options_to_check:
                self.select(option, skip_if_absent)

    def switch(self, to_state: typing.Literal["On", "Off"]):
        to_state = 'true' if to_state.lower() == 'on' else 'false'
        status_attribute = "aria-checked"
        current_state = self._available_options[0].__getattribute__(status_attribute)

        if current_state != to_state:
            self._available_options[0].click()
            expect(self._available_options[0]).to_have_attribute(status_attribute, to_state)
