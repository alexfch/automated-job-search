import json
import os


def absolute_path(file_name):
    return os.path.join(os.getenv('PROJECT_PATH'), file_name)


def save_distinct_jobs_list(path_to_file, new_jobs):
    if not isinstance(new_jobs, list) or len(new_jobs) == 0:
        return

    existing_jobs = read_from_file(absolute_path(path_to_file))
    existing_urls = [job["url"] for job in existing_jobs]

    unique_new_jobs = [dict(t) for t in {tuple(d.items()) for d in new_jobs}]
    new_urls = [job["url"] for job in unique_new_jobs]

    diff_urls = list(set(new_urls) - set(existing_urls))
    diff_jobs = [job for job in unique_new_jobs if job["url"] in diff_urls]

    combined_list = existing_jobs + diff_jobs

    save_to_file(absolute_path(path_to_file), combined_list)


def get_titles_from_file(path_to_file):
    jobs_list = read_from_file(absolute_path(path_to_file))
    return [job["title"] for job in jobs_list]


def get_jobs_from_file_by_titles(titles, path_to_file):
    existing_jobs = read_from_file(absolute_path(path_to_file))
    return [job for job in existing_jobs if job['title'] in titles]


def filter_jobs_in_file_by_titles(titles, path_to_file):
    filtered_jobs = get_jobs_from_file_by_titles(titles, absolute_path(path_to_file))
    save_to_file(absolute_path(path_to_file), filtered_jobs)


def update_job(new_job, path_to_file):
    jobs = read_from_file(path_to_file)
    for job in jobs:
        if job.url == new_job.url:
            jobs.remove(job)
            jobs.append(new_job)
            break
    save_to_file(path_to_file, jobs)


def read_from_file(path_to_file):
    with open(absolute_path(path_to_file), "r") as f:
        c = f.read()
        file_content = json.loads(c) if c != "" else []
    return file_content


def save_to_file(path_to_file, content):
    with open(absolute_path(path_to_file), "w") as f:
        pretty_content = json.dumps(content, indent=2)
        f.write(pretty_content)
