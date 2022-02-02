import requests
import json
import time
import csv
import datetime
import requests_cache
import re


USER_AGENT = 'Last.fm Bar Chart Race'
API_KEY = '57ee3318536b23ee81d6b27e36997cde'

headers = {
	'user-agert': USER_AGENT
}

payload = {
	'method': 'user.getRecentTracks',
	'limit': 200,
	'user': ' ',
	'page': 1,
	'from': 0,
	'api_key': API_KEY,
	'format': 'json'
}

artists = {}
dates = []

requests_cache.install_cache()

def getInformation():
	re1 = re.compile(r"[<>/{}[\]~`?!.@#$%^&*()+=|]"); # List of illegal characters for username
	while True:
		print("Enter username: ")
		payload['user'] = input()
		if re1.search(payload['user']):
			print("\nInvalid username\n")
		else:
			break



def printJson(object):
	text = json.dumps(object, sort_keys=True, indent=4)
	print(text)


def convertToCSV():
	sums = {}
	for artist in artists:
		sum = 0
		sums[artist] = {'artist': artist}
		for date in dates:
			if date in artists[artist]:
				sum += artists[artist][date]
				sums[artist][date] = sum

	#print(sums)

	dates.insert(0, 'artist')

	output_filename = payload['user'] + "-processed.csv"
	with open(output_filename, 'w', encoding="utf-8") as out:
		csvOut = csv.DictWriter(out, dates)
		csvOut.writeheader()
		for artist in sums:
			csvOut.writerow(sums[artist])


def makeList(jsonList):
	try:
		for entry in jsonList['recenttracks']['track']:
			if "@attr" in entry:
				continue
			artist = entry['artist']['#text']
			initial_date = entry['date']['#text'].rstrip()
			try:
				raw_date = datetime.datetime.strptime(initial_date, "%d %b %Y, %H:%M")
				date = raw_date.strftime("%Y %B")
			except ValueError:
				date = "No Date"

			if artist not in artists:
				artists[artist] = {}
			if date not in artists[artist]:
				artists[artist][date] = 1
			else:
				artists[artist][date] += 1
			if date not in dates:
				dates.insert(0, date)

	except KeyError: # Sometimes the API doesn't work properly
		print ("Having some difficulties... Please wait.", end='\r')
		time.sleep(10)
		payload['page'] -= 1


def getTracks():
	r = requests.get('http://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
	totalPages = int(r.json()['recenttracks']['@attr']['totalPages'])
	while payload['page'] <= totalPages:
		r = requests.get('http://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
		#printJson(r.json())
		#exit(0)
		
		if not getattr(r, 'from_cache', False): # If not in the cache
			time.sleep(0.25) # Sleep for a bit so we don't overuse the API

		makeList(r.json())
		print (str(payload['page']) + " pages completed                    ", end='\r')
		payload['page'] += 1


if __name__ == '__main__':
	getInformation()
	getTracks()
	convertToCSV()
	print ("")
	print ("Task finished!")