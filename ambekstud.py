import requests, json
from bs4 import BeautifulSoup

BASE_URL = r"https://www.uni-potsdam.de"
INDEX_URL = fr"{BASE_URL}/de/ambek/index"

index_data = requests.get(INDEX_URL)
index_soup = BeautifulSoup(index_data.content, "html.parser")

links = [ln['href'] for ln in index_soup.select("ul.up-subpagenav-list.dl-submenu li:not(.has-sub) a")]

possible_links = []

if "/de/ambek/retro" in links:
    links.remove("/de/ambek/retro")

print(f"TODO: {len(links)}")
try:
    for link in links:
        URL = BASE_URL + link

        print(f"Parsing {link}")
        linked_data = requests.get(URL)
        linked_soup = BeautifulSoup(linked_data.content, "html.parser")

        title_tags = linked_soup.select("h4, h3, h2")
        title_tags = [t for t in title_tags if "Studierendenschaft" in t.string.split() or "Studentenschaft" in t.string.split()]
        
        if len(title_tags) == 0:
            if "Studierendenschaft" in linked_data.text or \
               "Studentenschaft" in linked_data.text:
               print("ALERT! Stud. gefunden, aber kein title_tag. Enter zum fortfahren")
               input()
            continue

        ambek_id = linked_soup.find("h2").string

        if title_tags[0].nextSibling is not None:
            box = title_tags[0].nextSibling
        elif title_tags[0].parent.nextSibling is not None:
            box = title_tags[0].parent.nextSibling
        else:
            box = title_tags[0].parent.parent.nextSibling

        orders = box.find_all("a")
        
        for order in orders:
            possible_links += [{ "ambek_id": ambek_id, "link": order['href'], "title": order.string.strip() }]
except Exception as e:
    print("ERROR!", e)
finally:
    table_html = ""

    for pl in possible_links:
        table_html += f"<tr><td>{pl['ambek_id']}</td><td>{pl['title']}</td><td><a href=\"{pl['link']}\">Link</a></td>"

    f = open("index.html", "r")
    fc = f.read()
    f.close()
    before, relevant = fc.split("<!-- BEGIN REPLACEMENT AREA -->")
    relevant, after = fc.split("<!-- END REPLACEMENT AREA -->")

    newc = before + "<!-- BEGIN REPLACEMENT AREA -->" + table_html + "<!-- END REPLACEMENT AREA -->" + after
    f = open("index.html", "w")
    f.write(newc)
    f.close()