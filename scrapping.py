import requests
from bs4 import BeautifulSoup


def candidate_list():
    url = "https://agepoly.ch/candidatures-agepoly-2023-2024/"
    response = requests.get(url)
    content = response.text
    soup = BeautifulSoup(content, "html.parser")
    candidate_sections = soup.find_all("h4", class_='h5')
    candidates = {}
    # Iterate through the candidate sections
    for h4 in candidate_sections:
        # Find previous h5
        h5 = h4.find_previous('h5')
        if not h5:
            continue
        # Find strong in h5
        position = h5.find('strong').text.strip().split(" – ")[0].split("\n")[0]
        if position not in candidates:
            candidates[position] = []
        candidates[position].append(h4.text.strip())
    return candidates


def get_html_candidats() -> str:
    """Get the list of candidates from the AGE Poly website."""
    candidates = candidate_list()
    html = ""
    for position, candidats in candidates.items():
        html += f"<b>{position}</b>\n"
        for candidat in candidats:
            html += f"\t• {candidat}\n"
        html += "\n"
    return html


if __name__ == "__main__":
    print(get_html_candidats())