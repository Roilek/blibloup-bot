def prompt_data(command: str, fields: list) -> str:
    text = command + '\n'
    for field in fields:
        text += field + ':\n'
    return text


def retrieve_data(text: str) -> dict:
    text_parts = text.split('\n')
    data = {}
    for line in text_parts:
        key, value = line.split(':', 1)
        data[key] = value
    return data