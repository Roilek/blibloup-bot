import ast
import os
from dotenv import load_dotenv
from datetime import datetime
import openai


load_dotenv()

DEFAULT_MODEL = "gpt-3.5-turbo"
openai.api_key = os.getenv("OPENAI_KEY")


def prompt(prompt_str: str) -> str:
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "user", "content": prompt_str}
        ]
    )
    finish_reason = completion.choices[0].finish_reason
    if finish_reason == "stop":
        answer = completion.choices[0].message.content
    else:
        answer = f"Finish reason is '{finish_reason}', which is not 'stop', the expected value... something bad " \
                 f"happened!"

    return answer


def extract_date(prompt_str: str) -> str:
    current_date = datetime.now().strftime("%A %d %B %Y %Hh%Mmn")
    prompt_str = f"Extract the date with format 20230518T100000 for the following text: {prompt_str}."
    prompt_str += "Answer nothing more than "
    prompt_str += f"the formatted date. Note that current date is: {current_date}."
    return prompt(prompt_str)


def extract_event(event_data: str) -> dict[str, datetime, datetime]:
    current_date = datetime.now()
    prompt_str = "Note that current date and time is " + datetime.now().strftime("%A %d %B %Y %H:%M") + "\n"
    prompt_str += "Note that if no date is provided, you should indicate one anyway, try your best!\n"
    prompt_str += "Note that if no time is provided, you should indicate one anyway, try your best!\n"
    prompt_str += "Note that the result will be parsed as a dict by ast lib, it should therefore only consist of a string immediately interpretable as dict without any comment.\n"
    prompt_str += "If no time is specified, try not to create an all date event but instead a coherent timeslot.\n"
    prompt_str += "Create a dict-like object with the following fields. Date should follow iso format:\n"
    prompt_str += "'name':\n"
    prompt_str += "'start':\n"
    prompt_str += "'end':\n\n"
    prompt_str += "Based on the following data:\n"
    prompt_str += event_data.encode('utf-8').decode('unicode-escape')

    result = prompt(prompt_str)
    dict_result = ast.literal_eval(result)
    dict_result["start"] = datetime.fromisoformat(dict_result["start"])
    dict_result["end"] = datetime.fromisoformat(dict_result["end"])

    return dict_result


if __name__ == "__main__":
    current_date = datetime.now().strftime("%A %d %B %Y %Hh%Mmn")
    print(extract_event("Petit déjeuner à l'EPFL lundi"))

