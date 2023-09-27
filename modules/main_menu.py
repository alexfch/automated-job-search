import re
import time

from playwright.sync_api import Page, expect, LocatorAssertions


class MainMenu:

    def __init__(self, page: Page):
        self._search = page.locator("[id].jobs-search-box__keyboard-text-input")
        self._location = page.locator("div.jobs-search-box__input--location").get_by_role("combobox")
        self._home = page.get_by_title('Home')
        self._my_network = page.get_by_title('My Network')
        self._jobs = page.get_by_title('Jobs')
        self._messaging = page.get_by_title('Messaging')
        self._notifications = page.get_by_title('Notifications')
        self._search_result_text = page.locator("#results-list__title")
        self._jobs_panel = page.locator(".jobs-home-scalable-nav:visible")
        self._no_results_found = page.locator("div.jobs-search-no-results-banner")

    def chose_location(self, location):
        self._location.fill(location)
        time.sleep(2)
        self._location.press('Enter')
        expect(self._location).not_to_be_focused()
        try:
            expect(self._search_result_text).to_have_text(re.compile(fr"{location}.*"), timeout=10000)
        except:
            expect(self._no_results_found).to_be_visible()
        return self

    def search(self, query):
        self._search.fill(query)
        time.sleep(2)
        self._search.press('Enter')
        try:
            expect(self._search_result_text).to_have_text(re.compile(fr"{query}.*"), timeout=10000)
        except:
            expect(self._no_results_found).to_be_visible()
        return self

    def go_to_home(self):
        self._home.click()
        return self

    def go_to_my_network(self):
        self._my_network.click()
        return self

    def go_to_jobs(self):
        self._jobs.click()
        expect(self._jobs_panel).to_be_visible()
        return self
