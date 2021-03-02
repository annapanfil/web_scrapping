# import datetime
import requests
from requests_html import HTML
import re
from pprint import pprint
from prettytable import PrettyTable


def url_to_txt(url) -> str:
    # GET DATA
    r = requests.get(url)      # get html from the website
    if r.status_code == 200:   # success
        html_text = r.text
        return html_text
    return None

def table_to_list(table) -> tuple:
    rows = table.find("tr")

    header_row = rows[0]     #TODO: 1. too
    header_cols = header_row.find("th")
    header_names = [x.text for x in header_cols]

    table_data = []

    for row in rows[2:]:
        cols = row.find("td")   # get cells
        row_data = [col.text for col in cols]
        table_data.append(row_data)
    return header_names, table_data

def parse_data(header_names, table_data, funds) -> dict:
    for i in range(len(table_data)): # remove empty fields
        table_data[i] = table_data[i][2:]

    my_funds = {}
    for fund in table_data:
        for name in funds.keys():
            if re.search(name+"\\n", fund[0], re.IGNORECASE):
                m = re.match("\d+\.\d+", fund[2])
                my_funds[name] = float(m.group())*funds[name]
    #
    # my_funds = [[fund[0], fund[2]] for fund in table_data if fund[0] in funds_names]
    return my_funds

    # df = pd.DataFrame(table_data, columns=header_names)
    # print(df)



def find_data(date) -> tuple:
    url = f"https://investors.pl/fundusze-inwestycyjne/?d=c&cd={date}"

    html_text = url_to_txt(url) # get HTML text
    if html_text == None: return False
    # print(html_text)

    r_html = HTML(html=html_text) # convert to an object
    table = r_html.find(".table-funds")[0] # find the table
    header_names, table_data = table_to_list(table)

    return header_names, table_data


if __name__ == "__main__":
    """ENTER YOUR TRANSACTIONS HERE"""
    transactions = {"05-02-2021": {"Investor Obligacji": 500, "Investor zrównoważony":100, "nowych technologii":200}, "02-02-2021": {"Akcji spółek wzrostowych":1,"Investor Obligacji":10}}

    all_funds = {}
    for trans in transactions.values():
        for fund in trans.items():
            if fund[0] in all_funds.keys():
                all_funds[fund[0]] += trans[fund[0]]
            else: all_funds.update([fund])

    today_data = find_data("")
    today_prices = parse_data(*today_data, all_funds)

    buy_prices = {}
    for date in transactions.keys():
        buy_data = find_data(date)
        buy_prices.update(parse_data(*buy_data, transactions[date]))

    x = PrettyTable()
    x.field_names = ["Nazwa funduszu", "Ilość jednostek", "Zysk [PLN]"]
    x.align["Nazwa funduszu"] = "l"
    x.align["Ilość jednostek"] = "r"
    x.align["Zysk"] = "r"

    profits = {}
    total = 0
    for name in today_prices.keys():
        profits[name] = today_prices[name]-buy_prices[name]
        total += profits[name]
        x.add_row([name, all_funds[name], round(profits[name], 2)])

    print(x)
    print(f"\nW sumie: {total:.2f}\n")
