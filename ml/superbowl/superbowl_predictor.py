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

def configure_headers():
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

def rest_request():
	conn = http.client.HTTPSConnection("nfl-api-data.p.rapidapi.com")

	load_dotenv()
	
	headers = {
		'x-rapidapi-key': os.getenv("RAPID_NFL_API_KEY"),
		'x-rapidapi-host': os.getenv("RAPID_NFL_API_HOST")
	}

	conn.request("GET", "/nfl-team-listing/v1/data", headers=headers)

	res = conn.getresponse()
	data = res.read()

	return data.decode('utf-8')

def parse_rest_request(data: str):
	pass	

def save_json_data(filename, data):
    with open(filename, 'w') as fout:
        json_string_data = json.dumps(data)
        fout.write(json_string_data)
        
def load_json_data(filename):
    with open(filename) as fin:
        json_data = json.load(fin)
        return json_data

if __name__ == '__main__':
	# url = 'https://www.espn.com/nfl/stats'
	# headers = configure_headers()
	# content = run_agent(url, headers)	
	# parse_bs4_content(content)
	pass