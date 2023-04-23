import requests
from bs4 import BeautifulSoup


def get_candidats_agep() -> dict[str, str]:
    """Get the list of candidates from the AGE Poly website."""
    url = "https://agepoly.ch/candidatures-agepoly-2023-2024/"
    response = requests.get(url)
    content = response.text
    soup = BeautifulSoup(content, "html.parser")
    divs = soup.find_all("div", {'class': 'row mb-9 text-center'})
    candidats = {}
    for div in divs:
        h4 = div.find('h4')
        if h4 and h4.text:
            name = h4.text.strip()
            span = div.find('span', {'class': 'd-block text-primary'})
            if span and span.text:
                poste = span.text.strip()
                candidats[name] = poste
    return candidats


def prettify_candidats(candidats: dict[str, str]) -> str:
    """Prettify the candidates list."""
    text = ""
    # For each different value, get the keys and sort them
    for poste in set(candidats.values()):
        names = sorted([name for name, p in candidats.items() if p == poste])
        text += f"**{poste}**\n"
        for name in names:
            text += f"\t- {name}\n"
    return text


if __name__ == "__main__":
    print(prettify_candidats(get_candidats_agep()))
