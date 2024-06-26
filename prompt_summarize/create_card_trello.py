import re
import requests
import json

API_KEY = "ca3e3ea2884fd0e3811a4bfc7b6e9cab"
API_TOKEN = (
    "ATTAe088d56c84032b60c76954ff7ce67c11b59ec58be849cc8bf9e552dedd56bdf648CB51C9"
)


def parse_tasks(text):
    sections = re.split(r"\n(?=To Do:|Doing:|Done:)", text.strip())
    tasks = {"To Do": [], "Doing": [], "Done": []}

    for section in sections:
        if section.startswith("To Do:"):
            tasks["To Do"] = re.findall(r"\d+\.\s(.+)", section)
        elif section.startswith("Doing:"):
            tasks["Doing"] = re.findall(r"\d+\.\s(.+)", section)
        elif section.startswith("Done:"):
            tasks["Done"] = re.findall(r"\d+\.\s(.+)", section)

    return tasks


def upload_to_trello(tasks):
    headers = {"Accept": "application/json"}
    url = "https://api.trello.com/1/cards"

    idList = {
        "To Do": "66774c5dcebc33d490f463fd",
        "Doing": "66774cb80a97a9f6a3a77b1e",
        "Done": "66774cbcb80d5f2a51abb4d9",
    }

    for status, task_list in tasks.items():
        for task in task_list:
            data = {
                "name": task,
                "desc": f"Task: {task}\nStatus: {status}",
            }
            query = {"key": API_KEY, "token": API_TOKEN, "idList": idList[status]}
            query.update(data)

            response = requests.request("POST", url, headers=headers, params=query)
            print(f"Uploaded task: {task}")
            print(
                json.dumps(
                    json.loads(response.text),
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "),
                )
            )


if __name__ == "__main__":
    with open("tasks.txt", "r") as file:
        text = file.read()

    tasks = parse_tasks(text)
    upload_to_trello(tasks)
