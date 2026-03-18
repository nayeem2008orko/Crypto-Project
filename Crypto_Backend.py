# GOAL- Create a cryptocurrency API App
# which shows six cryptocurrencies at a time, and shows their value right now compared to a month ago
# if their value right now is higher, it gets labelled as a "popping currency" if not then it gets labelled
# as "going down, bet against it!" (ideas for the frontend)
# the currencies will be selected in a random order from a list of 12 currencies
# but there will be a drop-down box which filters based on increasing currencies or decreasing currencies
# if the user chooses either one, there will be two seperate lists carrying six of them each, seperate from the random-list
# these two lists will need if statements for selecting increasing/decreasing currencies from the API, then appended to the list
# OPTIONAL: Make a button which returns a data visualisation which has a bar chart comparing all currencies' current prices
#           Base the bar chart's Y axis on percent increases in each coin's price, rather than comparing raw price
#           for each coin, and just set the bar chart's X axis as the coin names

import requests
import random
from datetime import datetime, timedelta, UTC
import os
import matplotlib.pyplot as plot
from flask import Flask, render_template

try:
    randomised_coinlist = []
    params = {
        "vs_currency": "usd",
    }
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets", params=params)
    crypto_data = response.json()

    counter = 0
    for coin in crypto_data:
        x = coin["id"]
        y = coin["current_price"]
        randomised_coinlist.append({"coin_name": x, "current_price": y})
        counter += 1
        if counter >= 12:
            break
    random.shuffle(randomised_coinlist)
    print("Data retrieved, over and out")
except (TypeError, ValueError, KeyError):
    print("The rate limit hasn't refreshed yet")

date = datetime.now(UTC) - timedelta(days=5)
formatted_date = date.strftime("%d-%m-%Y")

for coin_dict in randomised_coinlist:
    history_response = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin_dict['coin_name']}/history?date={formatted_date}",
        params=params)
    try:
        history_price = history_response.json()["market_data"]["current_price"]["usd"]
        coin_dict["price_5days_ago"] = history_price
    except KeyError:
        coin_dict["price_5days_ago"] = None

increasing_coinlist = []
decreasing_coinlist = []
for coin_dict in randomised_coinlist:
    if coin_dict["price_5days_ago"] == None:
        continue

    elif coin_dict["current_price"] > coin_dict["price_5days_ago"]:
        increasing_coinlist.append({"coin_name": coin_dict["coin_name"], "price": coin_dict["current_price"],
                                     "old_price":coin_dict["price_5days_ago"]})
    else:
        decreasing_coinlist.append({"coin_name": coin_dict["coin_name"], "price": coin_dict["current_price"],
                                    "old_price":coin_dict["price_5days_ago"]})


# 9-11 coins have full data, out of 12
valid_coins = []
valid_coins = increasing_coinlist + decreasing_coinlist

image_url_dict = {
    "binance": "https://public.bnbstatic.com/20190405/eb2349c3-b2f8-4a93-a286-8f86a62ea9d8.png",
    "ripple": "https://cdn.freebiesupply.com/logos/large/2x/ripple-2-logo-png-transparent.png",
    "bitcoin": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/250px-Bitcoin.svg.png",
    "whitebit": "https://images.seeklogo.com/logo-png/45/1/whitebit-logo-png_seeklogo-458554.png",
    "ethereum": "https://www.citypng.com/public/uploads/preview/hd-ethereum-eth-purple-logo-sign-png-701751694771769kxirapfr36.png",
    "dogecoin": "https://www.citypng.com/public/uploads/preview/hd-official-dogecoin-logo-icon-coin-png-701751694779741xtjsr9sobd.png",
    "tron": "https://cdn-icons-png.flaticon.com/512/12114/12114250.png",
    "solana": "https://images.seeklogo.com/logo-png/42/1/solana-sol-logo-png_seeklogo-423095.png",
    "usds": "https://icons.veryicon.com/png/o/miscellaneous/ionicons/logo-usd-1.png",
    "usd-coin": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/USD_Coin_logo_%28cropped%29.png/330px-USD_Coin_logo_%28cropped%29.png",
    "figure-heloc": "https://s3-eu-west-1.amazonaws.com/tpd/logos/5bd0d13d3b29100001fb37a4/0x0.png"
}

os.makedirs("Coin_Images", exist_ok=True)

for key, value in image_url_dict.items():
    with open(f"Coin_Images/{key}_coin.png", "wb") as file:
        response = requests.get(value)
        file.write(response.content)

increasing_keys = []
for coin_dict in increasing_coinlist:
    target_key = coin_dict["coin_name"]
    increasing_keys.append(target_key)

decreasing_keys = []
for coin_dict in decreasing_coinlist:
    target_key = coin_dict["coin_name"]
    decreasing_keys.append(target_key)

increasing_percents = []
for price_dict in increasing_coinlist:
    new = price_dict["price"]
    old = price_dict["old_price"]
    percent = ((new - old)/old) * 100
    increasing_percents.append(percent)

decreasing_percents = []
for price_dict in decreasing_coinlist:
    new = price_dict["price"]
    old = price_dict["old_price"]
    percent = ((new - old)/old) * 100
    decreasing_percents.append(percent)

os.makedirs("Coin_Graphs", exist_ok=True)

plot.figure(figsize=(14, 5))
plot.bar(increasing_keys, increasing_percents)
plot.xlabel("Currencies")
plot.ylabel("Percentage Change")
plot.title("Cryptocurrency Increases")
plot.savefig("Coin_Graphs/increasing_graph.svg")
plot.show()

plot.figure(figsize=(14, 5))
plot.ylim(0, -0.01)
plot.bar(decreasing_keys, decreasing_percents)
plot.xlabel("Currencies")
plot.ylabel("Percentage Change")
plot.title("Cryptocurrency Decreases")
plot.savefig("Coin_Graphs/decreasing_graph.svg")
plot.show()


# FOR THE FRONTEND: Make a folder called static inside the .venv, and put the coin graph and coin images folders in it
#                   AND create a folder called templates, inside it create a html file called valid_coins_entry
app = Flask(__name__)

@app.route("/")
def first_page():
    return render_template("valid_coins_entry.html", coins=valid_coins, increasing=increasing_coinlist,
                           decreasing=decreasing_coinlist)

if __name__ == "__main__":
    app.run(debug=True)
