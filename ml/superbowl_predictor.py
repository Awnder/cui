import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler


def run_agent(url: str, headers: dict):
	""" Run the agent to scrape the given URL """
	request = urllib.request.Request(url, headers=headers)
	with urllib.request.urlopen(request) as response:
		content = response.read().decode('UTF-8')

	return content

def parse_content(content: str):
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

if __name__ == '__main__':
	url = 'https://www.espn.com/nfl/stats'
	headers = configure_headers()
	content = run_agent(url, headers)	
	parse_content(content)