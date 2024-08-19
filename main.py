import requests
import datetime
import json

def check_arbitrage(odds1, odds2):
    x = (1 / odds1 + 1 / odds2) 
    return x < 1


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

timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
filename = f'fetch_{timestamp}.json'
print("Saving to " + filename + " json file...")

# Save JSON data to a file
with open(filename, 'w') as json_file:
    json.dump(data, json_file, indent=4)
print("Successfully saved")

print("Checking for arbitrage opportunities...")
filtered_matches = []
for match in data['Tennis']['Ostalo']:
    if check_arbitrage(match['odds1'], match['odds2']):
        filtered_matches.append(match)

print("Found", len(filtered_matches), "arbitrage opportunities:")
# Print the filtered matches
for match in filtered_matches:
    print(f"Match: {match['home']} vs {match['away']}, Odds1: {match['odds1']}, Odds2: {match['odds2']}")

