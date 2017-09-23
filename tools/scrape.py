#!/usr/bin/python3

from io import BytesIO
import json
import subprocess
import sys
from urllib.request import urlopen
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup


SITE="http://www.findaride.org"

def _url_to_soup(url):
    page = urlopen(url)
    return BeautifulSoup(page, "html.parser")


def _js_url_to_soup(service_url):
    cmd = ["google-chrome", "--headless", "--disable-gpu", "--dump-dom",
           service_url]
    output = subprocess.run(cmd, stdout=subprocess.PIPE)
    if output.returncode != 0:
        raise output
    return BeautifulSoup(BytesIO(output.stdout), "html.parser")


def _row_filter(class_str):
    return class_str and class_str.startswith("field-name-field")


def _column_filter(class_str):
    return class_str and class_str == "columns"


def _cost_filter(class_str):
    return class_str == "group-cost-wrapper"


def _get_field_name(class_values):
    prefix = "field-name-field-"
    try:
        field_name = [v for v in class_values if v.startswith(prefix)][0]
        return field_name[len(prefix):]
    except IndexError:
        return None


def parse_service(service_url):
    soup = _js_url_to_soup(service_url)

    fields = {}
    title = soup.find("div", attrs={"class":
                                    lambda c: c == "field-name-title"})
    if title:
        fields["title"] = title.get_text()

    desc = soup.find("div", attrs={"class": "field field-name-body"})
    if desc:
        fields["description"] = desc.get_text()

    rows = soup.find_all("div", attrs={"class": _row_filter})
    for row in rows:
        field_name = _get_field_name(row["class"])
        if field_name is None:
            continue

        cols = row.find_all("div", attrs={"class": _column_filter})
        for col in cols:
            if "fields-wrapper" in col["class"]:
                fields[field_name] = [span.get_text() for span in col.find_all("span")]

    # cost is a special div for some reason?
    # <div class="group-cost-wrapper field-group-div row">
    cost = soup.find("div", attrs={"class": _cost_filter})
    if cost:
        costs = {}
        for div in cost.find_all("div"):
            field_name = _get_field_name(div["class"])
            if field_name is None:
                continue

            costs[field_name] = div.find_all(text=True)

        fields["cost"] = costs

    return fields


def get_service_urls():
    service_urls = []
    # there's 4 pages, missing pages return a 200 not 404
    # one way to scrape until not found would be looking for
    # "Sorry we cannot find any results matching your selection."
    # with div class view-empty
    for i in range(4):
        params = urlencode({"page": i})
        url = "{}?{}".format(urljoin(SITE, "/provider-list"), params)
        soup = _url_to_soup(url)
        services = soup.find_all("div", attrs={"class":
                                               "field field-name-title"})
        for service in services:
            link = service.find("a", href=True)
            service_url = urljoin(SITE, link['href'])
            yield service_url


def main():
    with open("../data/service_urls.json") as f:
        service_urls = json.load(f)
    services = {}
    for service_url in service_urls:
        sys.stderr.write(service_url + "\n")
        fields = parse_service(service_url)
        services[service_url] = fields

    print(json.dumps(services, indent=2))

if __name__ == "__main__":
    main()
