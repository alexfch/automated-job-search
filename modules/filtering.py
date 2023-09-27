import re
import time
import typing

from multipledispatch import dispatch
from playwright.sync_api import Page, expect, Locator


class WaitFilterEvents:

    def __init__(self, page: Page):
        self._no_results_found = page.locator("div.jobs-search-no-results-banner")
        self._results_container = page.locator("ul.scaffold-layout__list-container")
        self.filter_toolbar_buttons = \
            page.locator("#search-reusables__filters-bar button.search-reusables__filter-pill-button")

    def expect_filter_toolbar_shows_selected_filters(self):
        for r in range(5):
            aria_labels = ""
            for i in range(self.filter_toolbar_buttons.count()):
                label = self.filter_toolbar_buttons.nth(i).get_attribute("aria-label")
                if label:
                    aria_labels = aria_labels + label
            if "filter is currently applied" in aria_labels \
                    or "filters are applied" in aria_labels:
                break
            time.sleep(0.5)

    def expect_filtering_results_loaded(self, expect_results_available=True):
        if expect_results_available:
            expect(self._results_container).to_be_visible()
        else:
            expect(self._no_results_found).to_be_visible()


class FiltersToolbar:

    def __init__(self, page: Page):
        self._page = page
        self._panel_locator = '#search-reusables__filters-bar'
        self._date_posted = \
            FilterToolbarItem(page,
                              f"{self._panel_locator} div[data-basic-filter-parameter-name='timePostedRange']")
        self._experience_level = page.locator(
            f"{self._panel_locator} div[data-basic-filter-parameter-name='experience']")
        self._all_filters = page.locator(
            f"{self._panel_locator} button[aria-label^='Show all filters']")

    def show_all_filters(self):
        self._all_filters.click()

    def defect_workaround_check_date_posted_selection(self, expected_value):
        if expected_value in self._date_posted.toolbar_button.text_content():
            return
        self._date_posted.toolbar_button.click()
        self._date_posted.options_dropdown.set_filter(expected_value).show_results()


class FilterToolbarItem:

    def __init__(self, page: Page, container_selector):
        self._main_container = page.locator(container_selector)
        self.options_dropdown = FiltersModal(page, self._main_container)
        self.toolbar_button = self._main_container.locator("button.search-reusables__filter-pill-button")


class FiltersModal(WaitFilterEvents):

    def __init__(self, page: Page, main_locator: Locator = None):
        super().__init__(page)
        self._page = page
        self.main_container = \
            page.locator("div[data-test-modal-container]") if not main_locator \
            else main_locator.locator("div.reusable-search-filters-trigger-dropdown__content")
        self._show_results_button = self.main_container.locator("button", has_text=re.compile("Show.*result?"))

    @dispatch(str, (str, list), skip_if_absent=bool)
    def set_filter(self, label, options, skip_if_absent=True):
        filter_item = ModalFilterCategory(self.main_container, label)

        single_option = options[0] if isinstance(options, list) else options

        if filter_item.is_of_role("checkbox"):
            filter_item.check(options, skip_if_absent)
        elif filter_item.is_of_role("radio"):
            filter_item.select(single_option, skip_if_absent)
        elif filter_item.is_of_role("switch"):
            filter_item.switch(single_option)
        else:
            Exception("Unknown type of filter item")
        return self

    @dispatch((str, list), skip_if_absent=bool)
    def set_filter(self, options, skip_if_absent=True):
        return self.set_filter("", options, skip_if_absent=skip_if_absent)

    def set_filters(self, options, skip_if_absent=True):
        for category, option in options.items():
            self.set_filter(category, option, skip_if_absent=skip_if_absent)

        all_options_checked = True
        try:
            expect(self._show_results_button).to_contain_text(re    .compile(r"Show.*result?"), timeout=20000)
        except:
            all_options_checked = False

        for category, option in options.items():
            all_options_checked = self.is_checked(category, option, skip_if_absent)
            print(f"{category}. {option}. selected: {all_options_checked}")
            if not all_options_checked:
                break

        """This additional verification whether all options are checked is needed as a workaround for an
         intermittent defect when all selected options are reset to default before 'Show results' is clicked"""
        if all_options_checked:
            self.show_results()
        else:
            print("Some of filter options were reset. Options selection is repeated")
            self.set_filters(options, skip_if_absent)

    def show_results(self):
        results_available = True if "Show 0 results" not in self._show_results_button.text_content() else False
        self._show_results_button.click()
        expect(self.main_container).not_to_be_visible()
        self.expect_filter_toolbar_shows_selected_filters()

    def is_checked(self, label, options, skip_if_absent=True):
        filter_item = ModalFilterCategory(self.main_container, label)

        single_option = options[0] if isinstance(options, list) else options

        if filter_item.is_of_role("checkbox"):
            return filter_item.checked(options, skip_if_absent)
        elif filter_item.is_of_role("radio"):
            return filter_item.selected(single_option, skip_if_absent)
        elif filter_item.is_of_role("switch"):
            return filter_item.switched(single_option)
        else:
            Exception("Unknown type of filter item")


class ModalFilterCategory:

    def __init__(self, main_category: Locator, category_label=""):
        self._category = \
            main_category.locator("fieldset", has_text=category_label) \
            if category_label != "" \
            else main_category.locator("fieldset")
        self._available_options = self._category.locator("input").all()

    def is_of_role(self, role):
        """ verifies the type of a web element: checkbox, radio, switch, etc."""
        return len(self._category.get_by_role(role).all()) > 0

    def select(self, option: str, skip_if_absent: bool):
        element = self._category.get_by_label(option)
        if not element.is_visible() and skip_if_absent:
            return

        for i in range(6):
            element.locator("+label").click()
            if element.is_checked():
                break
            time.sleep(0.5)

    def check(self, options_to_check: str | list, skip_if_absent: bool):
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

    def selected(self, option: str, skip_if_absent: bool):
        element = self._category.get_by_label(option)
        if not element.is_visible() and skip_if_absent:
            return True
        return element.is_checked()

    def checked(self, options_to_check: str | list, skip_if_absent: bool):
        if isinstance(options_to_check, str):
            return self.selected(options_to_check, skip_if_absent)
        else:
            all_checked = False
            for option in options_to_check:
                all_checked = self.selected(option, skip_if_absent)
            return all_checked

    def switched(self, to_state: typing.Literal["On", "Off"]):
        to_state = 'true' if to_state.lower() == 'on' else 'false'
        status_attribute = "aria-checked"
        current_state = self._available_options[0].__getattribute__(status_attribute)
        return current_state == to_state
