import os
from bs4 import BeautifulSoup
import re
path = os.path.join("data_folder", "watch-history.html")

with open(path, "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "lxml")

general_list = []
matches = soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp")
for i in matches:
    captured_list = []
    # skip the ads
    if i.find(string=lambda t: t and t.strip().startswith("Details:")):
        continue

    sub_content = i.find("div", "content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
    # find the links (should be 2)
    matches = sub_content.find_all("a")

    # skip abnormalities
    if (len(matches)) < 2:
        continue

    # find the link, and title for both video and channel
    for i in matches:
        captured_list.append(i.get("href"))
        captured_list.append(i.get_text(strip=True))

    # add the timestamp
    captured_list.append(list(sub_content.stripped_strings)[-1])

    general_list.append(captured_list)

