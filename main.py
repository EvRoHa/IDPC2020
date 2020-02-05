import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore


def main():
    #soup = download_results()
    #results = build_results_array(soup)
    #export_results_to_csv(results)
    #frame = export_results_to_pandas(results)
    frame = pd.read_csv('Iowa 2020 Democratic Party Caucus Results Afternoon 2-5-2020 (corrected).csv', index_col=[0,1], header=0)
    foo = resample_results(frame, 100000, 1099)
    #Show_SDE_Distribution(foo,
    #                      {'Buttigieg': 363, 'Sanders': 338, 'Warren': 246, 'Biden': 210, 'Klobuchar': 170, 'Yang': 14})
    Show_Final_Distribution(foo,
                          {'Buttigieg': 27030, 'Sanders': 28220, 'Warren': 22254, 'Biden': 14176})


def Show_SDE_Distribution(result_frame, pub):
    foo = result_frame.loc[:, (result_frame > 10.0).any(axis=0)].filter(regex=(r'SDE'))
    ax = foo.plot.kde()

    for key, val in pub.items():
        print('{} score in {} percentile'.format(key, percentileofscore(result_frame['{}_SDE'.format(key)], val)))
        ax.axvline(val, 0, 0.5)
    plt.show()

def Show_Final_Distribution(result_frame, pub):
    foo = result_frame.loc[:, (result_frame > 100.0).any(axis=0)].filter(regex=(r'Final_Expression'))
    ax = foo.plot.kde()

    for key, val in pub.items():
        print('{} score in {} percentile'.format(key, percentileofscore(result_frame['{}_Final_Expression'.format(key)], val)))
        ax.axvline(val, 0, 30000)
    plt.show()

def build_results_array(soup):
    return [extract_headers(soup)] + extract_results(soup)


def download_results():
    url = 'https://results.thecaucuses.org/'
    return fetch_url(url)


def export_results_to_csv(arr):
    with open('Iowa 2020 Democratic Party Caucus Results.csv', 'w+', newline='') as csvout:
        csvr = csv.writer(csvout)
        csvr.writerows(arr)  # Build the rows


def export_results_to_pandas(arr):
    foo = np.array(arr)
    return pd.DataFrame(data=foo[1:, 2:], index=foo[1:, 0:2], columns=foo[0, 2:], dtype=float)


def extract_headers(soup):
    def clean_string(s):
        return s.replace(' ', '_')

    def find_head(sp, type):
        return sp.find('ul', {'class': type}).findAll('li')

    def find_table(sp):
        return sp.find('div', {'class': 'jsx-2178318319 precinct-table'})

    # Get the results table
    table = find_table(soup)

    # Extract the headers
    head = [clean_string(h.text) for h in find_head(table, 'thead')]

    # forward fill any blank headers with the last candidate name
    for i in range(len(head)):
        if len(head[i]) == 0:
            head[i] = head[i - 1]

    # Extract the subheaders
    subhead = [clean_string(sh.text) for sh in find_head(table, 'sub-head')]

    # Join the headers and subheaders to make complete headings
    return ['_'.join(x).rstrip('_') for x in list(zip(head, subhead))]


def extract_results(soup):
    results = []

    counties = soup.select('div[class*="precinct-rows"]')  # Get the counties

    for county in counties:
        for row in county.findAll('ul'):
            # The county isn't listed for each precinct, so it must be forward filled
            r = [county.find('div', {'class': 'precinct-county'}).text.replace(' ', '_')]

            skip = False

            # clean up each cell then append it to build the row
            for col in (row.findAll('li')):
                if col.text == 'Total':
                    skip = True
                    break
                try:
                    r.append(float(col.text.replace(',', '')))
                except ValueError:
                    t = re.sub(r'-|/', ' ', col.text)
                    r.append(re.sub(r'\s+', '_', t))

            if not skip:
                # append the new row
                results.append(r)

    return results


def fetch_url(url):
    return bs(requests.get(url).text, features="html.parser")


def resample_results(df, n, k, p=None):
    results = {x: [] for x in df.columns.values}

    for i in range(n):
        foo = take_sample(df, k, p)
        foo = summarize_results(foo)
        for x in foo.index.values:
            results[x].append(foo[x])

    return pd.DataFrame.from_dict(results)


def take_sample(df, k, p=None):
    return df.sample(n=k, weights=p)


def summarize_results(df):
    return df.sum(axis=0)


main()
