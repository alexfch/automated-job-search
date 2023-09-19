import os

import openai


def get_completion(system_message, prompt, model="gpt-3.5-turbo"):
    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": prompt
         }
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message["content"]


def get_relevant_titles(choice_criteria, results: list) -> list:
    criteria_string = "\n".join(choice_criteria) if isinstance(choice_criteria, list) else choice_criteria
    results_string = "\n".join(results)

    system_message = """You will be provided with a list of job titles from Software Development industry. \
        The list will be added under ###JOBS LIST### header.
        The provided list items can contain extra information like listed below. \
        You must ignore this information and operate only with the part that describes the role.
        ###Ignore extra information###
        - domain (e.g. Capital Market)
        - salary (e.g. $200,000/year USD)
        - job type (e.g. remote, hybrid, on-site)
        - seniority level (e.g. Junior, Middle, Senior)
        - country (e.g. Canada, USA)
        - technologies (e.g. Cypress, Java, Python, Mobile, Desktop)

        Task:
        1. First classify the provided list items to 'Quality Assurance', 'Test engineer', 'Test automation', 'Others'.
        2. Then add to the output only 'Quality Assurance', 'Testing', 'Test automation' list items.
        3. Do not add headers, comments or list numeration in the output.
        4. The list items in the output must have exactly the same spelling as they have in the input.
        """

    prompt = f"""###JOBS LIST###
    {results_string}
    """

    print("\nPROMPT:\n" + prompt)
    gpt_response = get_completion(system_message, prompt)
    relevant_titles = gpt_response.split("\n")

    #print("\nGPT RESPONSE\n" + str(relevant_titles))
    test_gpt_response(relevant_titles)

    return relevant_titles


def test_gpt_response(actual):
    expected = [
        'Sr. QA Analyst - Guidewire PolicyCenter Testing',
        'Senior Performance Test Engineer',
        'Sr. Performance Test Engineer',
        'Cypress Test Automation',
        'Backend QA Engineer / Blockchain Protocol Test Engineer',
        'Senior Software Engineer - Quality Automation Engineer in Test (Remote)',
        'Senior Software Engineer in Test I-351 (Hybrid - Toronto)',
        'Senior Software Engineer in Test I - Python-323 (Hybrid - Toronto)',
        'SuccessFactors Systems Testing/QA Specialist',
        'Software Development Engineer in Test',
        'Quality Assurance Test Lead - Capital Markets',
        'SDET (Software Development Engineer in Test)',
        'Intermediate QA Analyst',
        'Analyste QA senior / Senior QA Analyst',
        'Senior QA Programmer',
        'Quality Assurance Lead',
        'Senior Automation QA Analyst'
    ]
    correct = [x for x in actual if x in expected]
    correct_percent = round(len(correct)/len(expected)*100)

    missing = [x for x in expected if x not in actual]
    missing_percent = round(len(missing)/len(expected)*100)

    extra = [x for x in actual if x not in expected]
    extra_percent = round(len(extra) / len(actual) * 100)

    print(f"###CORRECT RESULTS: {correct_percent}% ###\n{correct}\n")
    print(f"###MISSING RESULTS: {missing_percent}% ###\n{missing}\n")
    print(f"###EXTRA RESULTS: {extra_percent}% ###\n{extra}\n")