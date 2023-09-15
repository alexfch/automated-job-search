import os
import re
import time
import typing

from playwright.sync_api import Page, expect, Locator

from pages.base_page import BasePage


class JobsSearchResultsPanel:

    def __init__(self, page: Page):
        self._page = page
        self.job_cards = self._page.locator("div.job-card-container")
        self.pagination = Pagination(self._page)
        self._footer = self._page.locator("footer.global-footer-compact")
        self._results_label = page.locator("div.jobs-search-results-list__subtitle")

    def scroll_bottom_of_jobs_search_results(self):
        """
                The method scrolls to the bottom of jobs list panel to load all results.
                By default, LinkedIn loads up to 7 jobs.

                :return:
                """
        self.job_cards.nth(0).hover(position={"x": 50, "y": 10})  # hover mouse over the jobs list panel
        time_start = time.time()
        while not self.is_all_jobs_loaded() and time.time() - time_start < 1:
            self._page.mouse.wheel(delta_x=0, delta_y=200)

    def is_all_jobs_loaded(self):
        expected_count = min(
            25,  # default number per page
            int(re.search(re.compile("\d{1,4}"), self._results_label.text_content()).group())
        )
        return self.job_cards.count() == expected_count


class JobsPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_results = JobsSearchResultsPanel(self.page)
        self._no_results_found = self.page.locator("div.jobs-search-no-results-banner")

    def collect_jobs_by_criteria(
        self,
        job_title_pattern=None,
        location_patterns=None,
        job_type_patterns=None,
        location_and_type_patterns: list[typing.Pattern[str]] = None
    ):
        if self._no_results_found.is_visible():
            return [], []

        # find matching cards
        cards_match = []
        all_cards_on_page = []
        cards_dont_match = []

        def iterate_cards_on_the_page():
            """
            Analyze job results currently displayed on the page
            :return:
            """
            self.search_results.scroll_bottom_of_jobs_search_results()

            # read all cards
            for i in range(self.search_results.job_cards.count()):
                card = JobCard(self.search_results.job_cards.nth(i))
                all_cards_on_page.append(
                    {"title": card.title,
                     "url": os.environ["BASE_URL"] + re.compile(r"/jobs/view/\d{10}").search(card.url).group(),
                     "company": card.company,
                     "location_and_type": card.location_and_type
                     })

            # filter the results by location and type matching one of the patterns
            for i in range(len(all_cards_on_page)):
                for pattern in location_and_type_patterns:
                    if pattern.search(all_cards_on_page[i]["location_and_type"]):
                        cards_match.append(all_cards_on_page[i])
                        break

            # for debugging purposes save all 'non matches' to a separate list and then to file
            cards_dont_match.extend([x for x in all_cards_on_page if x not in cards_match])

        while True:
            iterate_cards_on_the_page()
            if not self.search_results.pagination.has_next():
                break
            self.search_results.pagination.go_to_next()

        return cards_match, cards_dont_match


class JobCard:

    def __init__(self, locator: Locator):
        self._locator = locator
        self._title_locator = "div.artdeco-entity-lockup__title a"
        self.title = locator.locator(self._title_locator).text_content().strip()
        self.company = locator.locator("div.artdeco-entity-lockup__subtitle").text_content().strip()
        self.url = locator.locator(self._title_locator).get_attribute("href")
        self.location_and_type = locator.locator(
            "div.artdeco-entity-lockup__caption li.job-card-container__metadata-item").text_content().strip()

    def click(self):
        self._locator.click()
        expect(self._locator).to_have_css("div.jobs-search-results-list__list-item--active")


class Pagination:

    def __init__(self, page: Page):
        self._pagination_locator = "div.jobs-search-results-list__pagination"
        self._pagination_panel = page.locator(self._pagination_locator)
        self._current_page = page.locator(f"{self._pagination_locator} button[aria-current]")
        self._next_page = page.locator(f"{self._pagination_locator} li:has(> button[aria-current]) +li>button")
        self._page = page

    def has_next(self) -> bool:
        try:
            if self._pagination_panel.is_visible():
                self._pagination_panel.scroll_into_view_if_needed()
                time.sleep(1)
        finally:
            return self._next_page.is_visible()

    def go_to_next(self):
        if self.has_next():
            next_number = str(int(self._current_page.text_content().strip()) + 1)
            self._next_page.click()
            expect(self._current_page).to_contain_text(next_number)

