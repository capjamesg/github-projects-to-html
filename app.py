import datetime
import os

import jinja2
import requests

USER = "capjamesg"
ROOT_DIR = "/home/jam/gh/"
OUT_FILE = "/home/jam/james-coffee-blog/pages/templates/wiki/projects.html"
TEMPLATE = jinja2.Template(open(os.path.join(ROOT_DIR, "template.html")).read())

url = f"https://api.github.com/users/{USER}/repos?sort=updated&direction=desc&per_page=100"

final_results = []

next = 1
langs = set()

while next:
    response = requests.get(url + f"&page={next}")

    for result in response.json():
        if result["fork"] or result["private"]:
            continue
        final_results.append(
            {
                "url": result["html_url"],
                "name": result["name"],
                "description": result["description"] or "",
                "language": result["language"] or "",
                "topics": ", ".join([f"#{topic}" for topic in result["topics"]]).strip(
                    ", "
                )
                if result["topics"]
                else [],
                "archived": result["archived"] or False,
                "updated": datetime.datetime.strptime(
                    result["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%b %d, %Y"),
            }
        )
        if result["language"]:
            langs.add(result["language"])

    next = response.links.get("next", {}).get("url")

    if not next:
        break

with open(OUT_FILE, "w") as f:
    f.write(TEMPLATE.render(projects=final_results, languages=sorted(langs)))
