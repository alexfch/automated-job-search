import json
import os
import re

import pytest

from pages.home import HomePage
from pages.jobs import JobsPage
from pages.login import LoginPage

jobs_to_search = ["head of qa", "qa automation manager", "qa automation lead"]


@pytest.mark.parametrize("job_title", jobs_to_search)
def test_something(job_title, context, login_page: LoginPage, home_page: HomePage, jobs_page: JobsPage) -> None:
    # navigate to jobs page
    if not context.cookies():
        login_page.navigate()
        login_page.sign_in(os.getenv('LINKEDIN_LOGIN'), os.getenv('LINKEDIN_PASSWORD'))
        home_page.save_cookies_to_file()

    home_page.navigate()
    home_page.main_menu.go_to_jobs()

    # search by job title
    jobs_page.main_menu.search(job_title)

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
            re.compile(r"(Toronto|Mississauga|Oakville|Burlington), ON(?: \(.*\))?"),  # any job in these cities
            re.compile(r"(Cambridge|Waterloo), ON \(.*(Remote|Hybrid)\)"),  # remote or hybrid job in these cities
            re.compile(r".*\(Remote\)"),  # remote job at any location
        ]
    )

    def save_to_file(file_name, data):
        if not isinstance(data, list) or len(data) == 0:
            return

        with open(file_name, "r+") as f:
            c = f.read().replace("'", "\"")
            file_content = [] if c == "" else json.loads(c)
            new_content = file_content + data
            distinct_list = [dict(t) for t in {tuple(d.items()) for d in new_content}]
            pretty_content = json.dumps(distinct_list, indent=2)
            f.seek(0)
            f.write(pretty_content)

    save_to_file("job-candidates.json", collected_job_cards)
    save_to_file("dont-match.json", dont_match)

    # let ChatGPT chose jobs by relevant job titles

    # exclude known jobs (both that passed and not passed job description evaluation)
    # -- IMPLEMENT LATER BUT DESIGN WITH IT IN MIND

    # let chatgpt evaluate job description

    # save url if the job meets the criteria

    # in a separate collection save urls of the jobs that pass job description evaluation
