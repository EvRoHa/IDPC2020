import requests
from bs4 import BeautifulSoup as bs
import re
import csv


def main():
    url = 'https://results.thecaucuses.org/'
    soup = fetch_url(url)

    with open('Iowa 2020 Democratic Caucus Results.csv', 'w+', newline='') as csvout:
        csvr = csv.writer(csvout)
        csvr.writerow(extract_headers(soup))
        csvr.writerows(extract_results(soup))


def fetch_url(url):
    return bs(requests.get(url).text, features="html.parser")


def extract_headers(soup):
    table = soup.find('div', {'class': 'jsx-2178318319 precinct-table'})
    head = [h.text.replace(' ', '_') for h in table.find('ul', {'class': 'thead'}).findAll('li')]

    for i in range(len(head)):
        if len(head[i]) == 0:
            head[i] = head[i - 1]
    subhead = [sh.text.replace(' ', '_') for sh in table.find('ul', {'class': 'sub-head'}).findAll('li')]
    return ['_'.join(x).rstrip('_') for x in list(zip(head, subhead))]


def extract_results(soup):
    results = []
    counties = soup.select('div[class*="precinct-rows"]')
    for county in counties:
        for row in county.findAll('ul'):
            r = [county.find('div', {'class': 'precinct-county'}).text.replace(' ', '_')]
            for col in (row.findAll('li')):
                t = re.sub(r'-|/', ' ', col.text)
                r.append(re.sub(r'\s+', '_', t))
            results.append(r)
    return results


main()
