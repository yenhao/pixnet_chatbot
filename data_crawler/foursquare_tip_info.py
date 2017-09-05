import foursquare
import json
import time
global client, data

def createClient():
	global client
	# Construct the client object
	client = foursquare.Foursquare(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')
	# Build the authorization url for your app
	auth_uri = client.oauth.auth_url()
	return client


def getTipInfo(venue_id):
	global client
	new_tips = {'tips':{'id':venue_id, 'items':[]}}
	
	tips = client.venues.tips(venue_id)
	
	if tips['tips']['count'] != 0:
		for item in tips['tips']['items']:
			tmp = {'createdAt':None, 'lang':None, 'text':None, 'agreeCount':None, 'disagreeCount':None, 'count':None} 
			try:
				tmp['createdAt'] = item['createdAt']
			except KeyError:
				tmp['createdAt'] = None
			try:
				tmp['lang'] = item['lang']
			except KeyError:
				tmp['lang'] = None
			try:
				tmp['text'] = item['text']
			except KeyError:
				tmp['text'] = None
			try:
				tmp['agreeCount'] = item['agreeCount']
			except KeyError:
				tmp['agreeCount'] = None
			try:
				tmp['disagreeCount'] = item['disagreeCount']
			except:
				tmp['disagreeCount'] = None
				
			new_tips['tips']['items'].append(tmp)
	else:
		pass

	new_tips['tips']['count'] = tips['tips']['count']

	return new_tips



if __name__ == "__main__":
	global client, data
	data = []
	client = createClient()
	with open('/home/adeline/Documents/food_data/YOUR_FILE_TO_WRITE', 'a') as write_file:	# Example: food_Taipei_City_Tips
		with open('/home/adeline/Documents/food_data/YOUR_FILE_TO_READ') as read_file:		# Example: food_Taipei_City_fb
			print('Getting tips...')
			venues = read_file.readlines()[1700:]
			for i, venue in enumerate(venues):
				if (i+1) % 100 == 0:
					print('{0}/{1} venue has been processed'.format((i+1), len(venues)))
					for ele in data:
						write_file.write('{0}\n'.format(ele))
					data = []
					print('Sleeping for {0} seconds...'.format(round((i+1)/10),1))
					time.sleep(round((i+1)/60),1)
				tips = getTipInfo(json.loads(venue)['id'])
				tips = json.JSONEncoder().encode(tips)
				data.append(tips)
			if data != []:
				for ele in data:
					write_file.write('{0}\n'.format(ele))