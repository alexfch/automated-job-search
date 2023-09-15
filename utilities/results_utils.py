import json


def save_distinct_jobs_list(path_to_file, new_jobs):
    if not isinstance(new_jobs, list) or len(new_jobs) == 0:
        return

    existing_jobs = read_from_file(path_to_file)
    distinct_list = [dict(t) for t in {tuple(d.items()) for d in existing_jobs + new_jobs}]
    save_to_file(path_to_file, distinct_list)


def read_from_file(path_to_file):
    with open(path_to_file, "r") as f:
        c = f.read().replace("'", "\"")
        file_content = [] if c == "" else json.loads(c)
    return file_content


def save_to_file(path_to_file, content):
    with open(path_to_file, "w") as f:
        pretty_content = json.dumps(content, indent=2)
        f.write(pretty_content)
