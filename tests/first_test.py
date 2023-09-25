import os
import re

import pytest

from pages.home import HomePage
from pages.jobs import JobsPage
from pages.login import LoginPage
from utilities import results_utils, chatgpt
from settings import candidates_file_name, dont_matches_file_name

jobs_to_search = ["head of quality assurance",
                  "qa manager",
                  "qa automation lead",
                  "qa automation engineer"]

jobs_in_locations = ["Canada", "United States"]

job_description_criteria = ["Python", "Automation"]

# TODO rename first_test module
# TODO bring configuration settings to a consistent approach
# TODO setup parametrized test with reading data from a file
# TODO move the main functionality from Test to WebApp (based on Ember)
# TODO replace json files with MongoDB
# TODO create unit tests for the main functionality
# TODO test installation instruction
# TODO evaluate job description and remove irrelevant jobs from the results list


@pytest.mark.parametrize("job_title", jobs_to_search)
@pytest.mark.parametrize("location", jobs_in_locations)
def test_search_jobs_by_criteria(job_title, location, context, login_page: LoginPage, home_page: HomePage, jobs_page: JobsPage) -> None:
    # navigate to jobs page
    if not context.cookies():
        login_page.navigate()
        login_page.sign_in(os.getenv('LINKEDIN_LOGIN'), os.getenv('LINKEDIN_PASSWORD'))
        home_page.save_cookies_to_file()

    home_page.navigate()
    home_page.main_menu.go_to_jobs()

    # search by job title and location
    jobs_page.main_menu \
        .search(job_title) \
        .chose_location(location)

    # set filters
    jobs_page.filters_panel.show_all_filters() \
        .set_filter("Date posted", "Past 24 hours") \
        .set_filter("Experience level", "Mid-Senior level") \
        .set_filter("Industry", ["Software Development", "IT Services and IT Consulting",
                                 "Technology, Information and Internet", "Information Technology & Services"]) \
        .show_results()

    # find by location and job type
    collected_job_cards, dont_match = jobs_page.collect_jobs_by_criteria(
        location_and_type_patterns=[
            re.compile(r"Ontario, Canada.*"),  # hybrid or remote jobs in Ontario
            re.compile(r"(Toronto|Mississauga|Oakville|Burlington), ON(?: \(.*\))?"),  # any job in these cities
            re.compile(r"(Cambridge|Waterloo), ON \(.*(Remote|Hybrid)\)"),  # remote or hybrid job in these cities
            re.compile(r".*\(Remote\)"),  # remote job at any location
        ]
    )

    # exclude already present dont-matches
    # save the remains to job-candidates
    results_utils.save_distinct_jobs_list(candidates_file_name, collected_job_cards)
    results_utils.save_distinct_jobs_list(dont_matches_file_name, dont_match)


def test_exclude_irrelevant_job_titles_classic():
    job_titles = results_utils.get_titles_from_file(candidates_file_name)
    job_titles = list(dict.fromkeys(job_titles))

    key_words = ["quality", "test", "qa ", "automation", "sdet"]
    relevant_titles = [title for title in job_titles for kw in key_words if kw.lower() in title.lower()]

    irrelevant_titles = [x for x in job_titles if x not in relevant_titles]
    irrelevant_jobs = results_utils.get_jobs_from_file_by_titles(irrelevant_titles, candidates_file_name)
    results_utils.save_distinct_jobs_list(dont_matches_file_name, irrelevant_jobs)

    results_utils.filter_jobs_in_file_by_titles(relevant_titles, candidates_file_name)


@pytest.mark.skip(reason="the prompt is not ready yet.")
def test_exclude_irrelevant_job_titles_chatgpt():
    # let ChatGPT chose jobs with relevant job titles
    job_titles = results_utils.get_titles_from_file(candidates_file_name)
    job_titles = list(dict.fromkeys(job_titles))
    relevant_titles = chatgpt.get_relevant_titles(job_titles)

    # irrelevant_titles = [x for x in job_titles if x not in relevant_titles]
    # irrelevant_jobs = results_utils.get_jobs_from_file_by_titles(irrelevant_titles, candidates_file_name)
    # results_utils.save_distinct_jobs_list(dont_matches_file_name, irrelevant_jobs)

    # results_utils.filter_jobs_in_file_by_titles(relevant_titles, candidates_file_name)
