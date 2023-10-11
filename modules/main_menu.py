import re
import time

from playwright.sync_api import Page, expect, LocatorAssertions


class MainMenu:

    def __init__(self, page: Page):
        self._search_input = page.locator("[id].jobs-search-box__keyboard-text-input")
        self._search_main_div = page.locator("div.relative", has=self._search_input)
        self._location_input = page.locator("div.jobs-search-box__input--location").get_by_role("combobox")
        self._home_button = page.get_by_title('Home')
        self._my_network_button = page.get_by_title('My Network')
        self._jobs_button = page.get_by_title('Jobs')
        self._messaging_button = page.get_by_title('Messaging')
        self._notifications_button = page.get_by_title('Notifications')
        self._search_result_text = page.locator("#results-list__title")
        self._jobs_panel = page.locator(".jobs-home-scalable-nav:visible")
        self._no_results_found_text = page.locator("div.jobs-search-no-results-banner")

    def chose_location(self, location):
        self._location_input.fill(location)
        time.sleep(2)
        self._location_input.press('Enter')
        expect(self._location_input).not_to_be_focused()
        try:
            expect(self._search_result_text).to_have_text(re.compile(fr"{location}.*"), timeout=10000)
        except:
            expect(self._no_results_found_text).to_be_visible()
        return self

    def search(self, query):
        while query not in self._search_main_div.inner_html():
            print("self._search.text_content(): " + self._search_input.text_content())
            self._search_input.fill(query)
            time.sleep(2)
        self._search_input.press('Enter')
        try:
            expect(self._search_result_text).to_have_text(re.compile(fr"{query}.*"), timeout=10000)
        except:
            expect(self._no_results_found_text).to_be_visible()
        return self

    def go_to_home(self):
        self._home_button.click()
        return self

    def go_to_my_network(self):
        self._my_network_button.click()
        return self

    def go_to_jobs(self):
        self._jobs_button.click()
        expect(self._jobs_panel).to_be_visible()
        return self
