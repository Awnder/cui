import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import http.client
from dotenv import load_dotenv
import os
import json
import jc_nfl_team_stats
import jc_nfl_team_listing_v1_data
import jc_nfl_season_year_x

# predict score for eagles and chiefs - 2 predictions
# 2 models - one for each team or 1 model run twice
# 1) collect data
# 2) clean & normalize
# --- API Data missing 2020 carolina panthers - can drop, choose mean
# --- sigmoid standardization
# --- 2014 jets vs bills game postponed - some fields dne or 0
# 3) choose features
# --- training features must be all available for predictions
# --- ex: can't do passing yards for QB current game bc you only know that after the game is done
# --- instead, use passing yards for season(s) average
# 4) train / chose model
# --- always set y values are the score (bc thats what youre trying to predict)
# 5) predict

# some approaches
# 1) historical results (might have less data available)
# --- T1: y=score offRank(T1) defRank(T2) avgPointsPerGame(T1) 
# --- T2: y=score offRank(T2) defRank(T1) avgPointsPerGame(T2) -- remember to ensure for/against values are correct
# 2) seasonal results for eagles and chiefs
# --- T1: y=score totalPassYards(T1) totalRushYards(T1) takeaways(T1) avgPointsPerGame(T1)
# --- T2: y=score totalPassYards(T2) totalRushYards(T2) takeaways(T2) avgPointsPerGame(T2)
# 3) hybrid

def run_agent(url: str, headers: dict):
	""" Run the agent to scrape the given URL """
	request = urllib.request.Request(url, headers=headers)
	with urllib.request.urlopen(request) as response:
		content = response.read().decode('UTF-8')

	return content

def parse_bs4_content(content: str):
	""" Parse the content of the webpage """
	soup = BeautifulSoup(content, "html.parser")
	html = soup.html
	body = html.body
	print(body)

def _configure_headers():
	""" Configure the headers for the request """
	mozilla = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
	applewebkit = 'AppleWebKit/537.36 (KHTML, like Gecko)'
	chrome = 'Chrome/97.0.4692.71 Safari/537.36'
	safari = 'Safari/537.36'
	user_contact_info = '** Webscraping project to predict Superbowl winners (contact: andrew.shiroma@eagles.cui.edu) **'
	custom_user_agent = f"{mozilla} {applewebkit} {chrome} {safari} {user_contact_info}"

	return {
		'User-Agent': custom_user_agent
	}

def retrieve_api_data(url: str, restapi: str, data_directory: str=None, enable_rest_request=False) -> dict:
    """
    Wrapper function to retrieve data from a REST API. Will load data if url matches filename in current directory. Otherwise, will make a request to the REST API and save data as json file.
    Parameters:
        url (str): URL to make a request to
        restapi (str): REST API URL
        data_directory (str): directory to save data. leave blank to use current directory
        enable_rest_request (bool): disables REST request as precaution to avoid unnecessary costs
    Returns:
        dict: json data from REST API or file. Returns None if file doesn't exist or incorrect api url request
    """
    url_cleaned = url
    if url_cleaned[0] == '/':
        url_cleaned = url_cleaned[1:] # requests have a '/' at the beginning, need to remove bc files don't start with /
    url_cleaned = url_cleaned.replace('/', '_') # replace '/' with '_' to match file format (otherwise will create folders)
    url_cleaned = url_cleaned.replace('?', '_') # replace '?' with '_' to match file format 
    url_cleaned = url_cleaned.replace('=', '_') # replace '=' with '_' to match file format

    if enable_rest_request:
        data = _rest_request(url, restapi)

        save_json_data(f'{url_cleaned}.json', data)
        return load_json_data(f'{url_cleaned}.json')
    else:
        if data_directory is None:
            current_dir_files = os.listdir(os.getcwd())
        else:
            current_dir_files = os.listdir(data_directory) 

        for file in current_dir_files:
            if file == f'{url_cleaned}.json':
                return load_json_data(f'{url_cleaned}.json')


def _rest_request(url: str, restapi: str) -> str:
    """ Makes a request to the REST API """
    conn = http.client.HTTPSConnection(restapi)

    load_dotenv()
    
    headers = {
        'x-rapidapi-key': os.getenv('RAPID_NFL_API_KEY'),
        'x-rapidapi-host': os.getenv('RAPID_NFL_API_HOST')
    }

    conn.request("GET", url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode('utf-8')

def save_json_data(filename: str, data: str) -> None:
    """ Takes a desired filename and json string data and dumps into file """
    with open(filename, 'w') as fout:
        json_string_data = json.dumps(data)
        fout.write(json_string_data)
        
def load_json_data(filename: str) -> dict:
    """ Takes a filename and loads json data from file """
    json_data = None
    with open(filename) as fin:
        json_data = json.load(fin)

    json_data = json.loads(json_data)
    return json_data

def parse_json_data(json_filename: str, csv_filename: str, function_name: str) -> dict:
    """ Parse existing json file and create a csv """
    if function_name == 'nfl_team_stats':
        jc_nfl_team_stats.parse_json_data(json_filename, csv_filename)
    elif function_name == 'nfl-team-listing_v1_data':
        jc_nfl_team_listing_v1_data.parse_json_data(json_filename, csv_filename)
    elif function_name == 'nfl-season_year_x':
         jc_nfl_season_year_x.parse_json_data(json_filename, csv_filename)


if __name__ == '__main__':
    get_route = '/nfl-season?year=2020'
    restapi = 'api-nfl-v1.p.rapidapi.com'
    # headers = _configure_headers()
    # content = run_agent(url, headers)	
    # parse_bs4_content(content)
    # retrieve_api_data(get_route, restapi, enable_rest_request=True)

    
    # PARSING JSON DATA
    # parse_json_data('api_data/nfl_team_stats.json', 'api_data/nfl_team_stats_parsed.csv', 'nfl_team_stats')
    # parse_json_data('api_data/nfl-team-listing_v1_data.json', 'api_data/nfl_team_listing_v1_parsed.csv', 'nfl-team-listing_v1_data')
    parse_json_data('api_data/nfl-season_year_2020.json', 'api_data/nfl_season_year_2020_parsed.csv', 'nfl-season_year_x')

# INSTRUCTIONS:
# 1) Identify important nfl information in this sample of json data.
# 2) Create a python function named parse_json_data to that takes a file name that contains this specific json data, extracts important features and values, and saves extracted features and values to a csv file. Pay special attention to how the json data is stored. Ensure that any code takes into account any string, list, or dictionary wrapping around the data and processes it properly.