import http.client
import os
from dotenv import load_dotenv
import json

def rest_request():
	conn = http.client.HTTPSConnection("nfl-api-data.p.rapidapi.com")

	load_dotenv()
	
	headers = {
		'x-rapidapi-key': os.getenv("RAPID_NFL_API_KEY"),
		'x-rapidapi-host': os.getenv("RAPID_NFL_API_HOST")
	}

	conn.request("GET", "/nfl-team-statistics?year=2023&id=22", headers=headers)

	res = conn.getresponse()
	data = res.read()

	return data.decode('utf-8')
def save_json_data(filename, data):
    with open(filename, 'w') as fout:
        json_string_data = json.dumps(data)
        fout.write(json_string_data)
        
def load_json_data(filename):
    json_data = None
    with open(filename) as fin:
        json_data = json.load(fin)

    json_data = json.loads(json_data)
    return json_data

# data = rest_request() # NOTE THIS WILL COST
# save_json_data('nfl_team_stats.json', data)

jdata = load_json_data('nfl_team_stats.json')
categories = jdata['statistics']['splits']['categories'] # a list of categories for each team
catkeys = categories[0].keys() # dictionary of valid keys
catkeys = ['displayName', 'stats']

print(categories[1]['stats'])

# for i in range(len(categories)):
#     print(categories[i]['stats'])

for i in range(len(categories[0]['stats'])):
    print(f'category: {categories[0]["stats"][i]}')

# with open('nfl_team_stats_parsed.csv', 'w') as fout:
#     fout.write(','.join(catkeys) + '\n')
#     for i in range(len(categories)):
#         stats = categories[i]['stats']
#         values = []
#         for j in range(len(stats)):
#             values.append(str(stats[j]))
#         fout.write(categories[i]['displayName'] + ',' + ','.join(values) + '\n')