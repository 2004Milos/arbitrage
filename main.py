import requests
import datetime
import json
from datetime import datetime
import os
import time as TimeLib
import random
import smtplib
from email.mime.text import MIMEText


def check_arbitrage(odds1, odds2):
    x = (1 / odds1 + 1 / odds2) 
    return x < 1

def find_arbitrages(match, headers):
    #sleep tako da daluje da je covek
    sleep_duration = random.uniform(0.005, 1.1)
    TimeLib.sleep(sleep_duration)

    arbs = []
    url = f"https://kvote.rs/api/v1/full/match?sport=Tennis&id={match['id']}&packageType=undefined"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch match id", match['id'])
        return

    full_match = response.json()
    try:
        time = datetime.fromtimestamp(float(match['startTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        time = str(match['startTime'])

    max_1 = (0, "")
    max_2 = (0, "")
    max_ps1 = (0, "")
    max_ps2 = (0, "")
    max_ds1 = (0, "")
    max_ds2 =  (0, "")

    # List of bookmakers
    bookmakers = ["MaxBet", "Admiral", "BetOle", "OktagonBet", "PinnBet", "PlanetWin", "SoccerBet", "SuperBet"]

    # Iterate through each bookmaker
    for bookmaker in bookmakers:
        if bookmaker in full_match:
            if 'K1' in full_match[bookmaker]:
                if(full_match[bookmaker]['K1'] > max_1[0]):
                    max_1 = (full_match[bookmaker]['K1'], bookmaker)
            if 'K2' in full_match[bookmaker]:
                if(full_match[bookmaker]['K2'] > max_2[0]):
                    max_2 = (full_match[bookmaker]['K2'], bookmaker)
            if 'PS1' in full_match[bookmaker]:
                if(full_match[bookmaker]['PS1'] > max_ps1[0]):
                    max_ps1 = (full_match[bookmaker]['PS1'], bookmaker)
            if 'PS2' in full_match[bookmaker]:
                if(full_match[bookmaker]['PS2'] > max_ps2[0]):
                    max_ps2 = (full_match[bookmaker]['PS2'], bookmaker)
            if 'DS1' in full_match[bookmaker]:
                if(full_match[bookmaker]['DS1'] > max_ds1[0]):
                    max_ds1 = (full_match[bookmaker]['DS1'], bookmaker)
            if 'DS2' in full_match[bookmaker]:
                if(full_match[bookmaker]['DS2'] > max_ds2[0]):
                    max_ds2 = (full_match[bookmaker]['DS2'], bookmaker)
                    
    # Check if arbitrage opportunities exists

    if max_1[0] != 0 and max_2[0] != 0:
        if check_arbitrage(max_1[0], max_2[0]):
            u1, u2, p = uplate_i_profit(max_1[0], max_2[0])
            print(f"Type: 12\nMatch: {match['home']} vs {match['away']}\nOdds1: {max_1[0]}, Odds2: {max_2[0]}\nTime: {time}\nUplata 1:{u1} Uplata 2:{u1}\nSiguran Profit: {p}\n\n---------------------------------\n")
        
            arbs.append({
                "type": "12",
                "Player1": match['home'],
                "Player2": match['away'],
                "Odds1": max_1[0],
                "Odds2": max_2[0],
                "Time": time,
                "Uplata1": u1,
                "Uplata2": u2,
                "Kladionica1": max_1[1],
                "Kladionica2": max_2[1],
                "Profit": p,
            })

    if max_ps1[0] != 0 and max_ps2[0] != 0:
        if check_arbitrage(max_ps1[0], max_ps2[0]):
            u1, u2, p = uplate_i_profit(max_ps1[0], max_ps2[0])
            print(f"Type: PS1PS2\nMatch: {match['home']} vs {match['away']}\nOdds1: {max_ps1[0]}, Odds2: {max_ps2[0]}\nTime: {time}\nUplata 1:{u1} Uplata 2:{u1}\nSiguran Profit: {p}\n\n---------------------------------\n")
        
            arbs.append({
                "type": "PS1PS2",
                "Player1": match['home'],
                "Player2": match['away'],
                "Odds1": max_ps1[0],
                "Odds2": max_ps2[0],
                "Time": time,
                "Uplata1": u1,
                "Uplata2": u2,
                "Kladionica1": max_ps1[1],
                "Kladionica2": max_ps2[1],
                "Profit": p,
            })
    
    if max_ds1[0] != 0 and max_ds2[0] != 0:
        if check_arbitrage(max_ds1[0], max_ds2[0]): 
            u1, u2, p = uplate_i_profit(max_ds1[0], max_ds2[0])
            print(f"Type: DS1DS2\nMatch: {match['home']} vs {match['away']}\nOdds1: {max_ds1[0]}, Odds2: {max_ds2[0]}\nTime: {time}\nUplata 1:{u1} Uplata 2:{u1}\nSiguran Profit: {p}\n\n---------------------------------\n")
        
            arbs.append({
                "type": "DS1DS2",
                "Player1": match['home'],
                "Player2": match['away'],
                "Odds1": max_ds1[0],
                "Odds2": max_ds2[0],
                "Time": time,
                "Uplata1": u1,
                "Uplata2": u2,
                "Kladionica1": max_ds1[1],
                "Kladionica2": max_ds2[1],
                "Profit": p,
            })
        
    return arbs

def uplate_i_profit(odds1, odds2):
    x = 1 / odds1 + 1 / odds2
    s1 = 100*1/odds1/x
    s2 = 100*1/odds2/x
    return s1,s2,min(s1*odds1, s2*odds2) - 100


if not os.path.exists("arbitrages"):
    os.makedirs("arbitrages")
if not os.path.exists("raw"):
    os.makedirs("raw")


print("Authenticating...")
url = "https://www.kvote.rs/api/v1/auth/authenticate"
payload = {
    "username": "tunepologame@gmail.com",
    "password": "kiklopovski"
}
response = requests.post(url, json=payload)

if response.status_code != 200:
    print("Failed to authenticate")
    exit()

token = response.json()["token"]

print("Successfully authenticated")
print("Token:", token)


print("Fetching matches...")
url = "https://kvote.rs/api/v1/all-sports/matches?timeFilter=2592000000"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.9",
    "Authorization": "Bearer "+token, #eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0dW5lcG9sb2dhbWVAZ21haWwuY29tIiwiaWF0IjoxNzI0MDAwMzkxLCJleHAiOjE3MjQwMTExOTF9.4ldBBTtP5nHO9Qg88QEY1DEv2mRw_RGKGMHzjITuoQA
    "Connection": "keep-alive",
    "Host": "kvote.rs",
    "Referer": "https://kvote.rs/home",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Failed to fetch matches")
    exit()

data = response.json()

print("Successfully fetched matches")

timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
filename = os.path.join("raw", f'fetch_{timestamp}.json')

print("Saving to " + filename + " json file...")

# Save JSON data to a file
with open(filename, 'w') as json_file:
    json.dump(data, json_file, indent=4)
print("Successfully saved")


print("Checking for arbitrage opportunities...")
arbitrages = []
curr = 1
for match in data['Tennis']['Ostalo']:
    found = find_arbitrages(match, headers)
    arbitrages.extend(found)
    print(f"{curr}/{len(data['Tennis']['Ostalo'])}")
    curr = curr + 1

print()
print("Found", len(arbitrages), "arbitrage opportunities:")


if len(arbitrages) > 0:
    arbitrages.sort(key=lambda x: x['Profit'], reverse=True)
    print(f"Saving arbitrage opportunities to arbitrage_{timestamp}.json")
    with open(os.path.join("arbitrages", f'arbitrage_{timestamp}.json'), 'w') as json_file:
        json.dump(arbitrages, json_file, indent=4)
    print("Successfully saved")

    print("Sending email...")
    subject = f"Arbitrages_{timestamp}"
    body = json.dumps(arbitrages, indent=4)
    sender = "zaharije48@gmail.com"
    recipients = ["tunepologame@gmail.com", "nikolamark50@gmail.com"]
    password = "uodp brkn wkwe wtez"
    #Kanister123

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
