import datetime
import requests
from requests_html import HTML # older equivalent is beautifulsoup4
import pandas as pd
import os


def url_to_txt(url, save=False, filename = "world.html"):
    now = datetime.datetime.now()
    year = now.year

    # GET DATA
    r = requests.get(url)      # get html from the website
    if r.status_code == 200:   # success
        html_text = r.text

        # SAVE TO FILE
        if save:
            with open(f"{year}-{filename}", "w") as f:
                f.write(html_text)
        return html_text
    return None

def localise_table(r_html):
    table_class = ".imdb-scroll-table" # class of a table (div in fact) we are looking for
    # table_class = "#imdb-scroll-table" # id of a table

    r_table = r_html.find(table_class)  #it's a list
    if len(r_table) == 1:
        # print(r_table[0].text)
        return r_table[0]
    return[]

def table_to_list(table):
    rows = table.find("tr")

    header_row = rows[0]
    header_cols = header_row.find("th")
    header_names = [x.text for x in header_cols]

    table_data = []

    for row in rows[1:]:
        cols = row.find("td")   # get cells
        row_data = [col.text for col in cols]
        # for i, col in enumerate(cols):
        #     print(i, col.text, '\n')
        table_data.append(row_data)
    return header_names, table_data

def save_to_csv(header_names, table_data, filename):
    df = pd.DataFrame(table_data, columns=header_names)

    # create a dir
    BASEDIR = os.path.dirname(__file__) # this file path
    path = os.path.join(BASEDIR, 'data')
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join('data', f'{filename}.csv')

    df.to_csv(filepath, index=False)

def url_to_csv(year=2020, filename="movies"):
    url = f"https://www.boxofficemojo.com/year/world/{year}/"

    html_text = url_to_txt(url) # get HTML text
    if html_text == None: return False
    r_html = HTML(html=html_text) # convert to an object
    parsed_table = localise_table(r_html) # get table object
    header_names, table_data = table_to_list(parsed_table) # convert it to a nice list
    save_to_csv(header_names, table_data, filename+str(year))

    return True


if __name__ == "__main__":
    # GET A TABLE FROM A WEBSITE AND SAVE IT TO CSV FILE
    start = 2022
    how_many_years = 3

    for i in range(start-how_many_years+1, start+1):
        finished = url_to_csv(i)
        if finished:
            print("finished", i)
        else:
            print("Year", i, "not found")
