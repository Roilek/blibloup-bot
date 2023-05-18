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


if __name__ == "__main__":
    current_date = datetime.now().strftime("%A %d %B %Y %Hh%Mmn")
    find_date = "Lundi prochain"
    print(current_date)
    print(prompt(f"Extract the date with format DD/MM/YYYY HhMmn for the following text: {find_date}. Answer nothing more than "
                f"the formatted date. Note that current date is: {current_date}."))

