import foursquare
import json

global 	data, client, count

def create_client():
	# Construct the client object
	client = foursquare.Foursquare(client_id='L1UFPLBHBD5SMXN1UFXH4YJBMUANZRTEUYBYOFV5VDE5AWOF', client_secret='GG4F1N4ROEIQNMGNVQXATCU1VKLO30RNC0J3N11ZP25DE0U2')

	# Build the authorization url for your app
	auth_uri = client.oauth.auth_url()
	# result = client.venues.search(params={'intent':'browse','sw':'24.7131,120.8784','ne':'24.8541,121.0332', 'categoryId':'4d4b7105d754a06374d81259', 'limit':50})
	# result = client.venues.search(params={'intent':'match','ll':'25.0800,121.4400', 'categoryId':'4d4b7105d754a06374d81259', 'limit':50})
# result = client.venues.search(params={'intent':'match','near':'Taiwan TW','city':'新竹市','categoryId':'4d4b7105d754a06374d81259', 'limit':50})
	return client


def check_region(sw_lat, sw_lng, ne_lat, ne_lng):
	global client, count, data
	count += 1
	print('check_region {0}'.format(count))

	sw = '{0},{1}'.format(sw_lat, sw_lng)
	ne = '{0},{1}'.format(ne_lat, ne_lng)


	result = client.venues.search(params={'intent':'browse','sw':sw, 'ne':ne, 'categoryId':'4d4b7105d754a06374d81259', 'limit':50})

	if (len(result['venues']) == 50) and ((float(ne_lat)-float(sw_lat)) > 0.000009 or (float(ne_lng)-float(sw_lng)) > 0.000009):
		
		cen_lat = (float(sw_lat) + float(ne_lat)) / 2
		cen_lng = (float(sw_lng) + float(ne_lng)) / 2

		check_region(str(cen_lat), str(cen_lng), ne_lat, ne_lng)	# Right-UP
		check_region(sw_lat, str(cen_lng), str(cen_lat), ne_lng)	# Right-DOWN
		check_region(str(cen_lat), sw_lng, sw_lat, str(cen_lng))	# LEFT-UP
		check_region(sw_lat, sw_lng, str(cen_lat), str(cen_lng))	# LEFT-DOWN

	else:
		data.append(result)


def dict_json():
	global data
	out_folder = '/home/adeline/Documents/food_data/'
	filename = 'food_Taipei_City'
	for i in range(len(data)):
		for venue in data[i]['venues']:
			try:
				del venue['allowMenuUrlEdit']
				del venue['beenHere']
			except KeyError:
				pass
			try:
				del venue['location']['address']
			except KeyError:
				pass
			try:
				del venue['location']['cc']
			except KeyError:
				pass
			try:
				del venue['location']['city']
			except KeyError:
				pass
			try:
				del venue['location']['country']
			except KeyError:
				pass
			try:
				del venue['location']['crossStreet']
			except KeyError:
				pass
			try:
				del venue['location']['labeledLatLngs']
			except KeyError:
				pass
			try:	
				del venue['location']['specials']
			except KeyError:
				pass
			try:	
				del venue['location']['venueChains']
			except KeyError:
				pass
			try:
				del venue['location']['verified']
			except KeyError:
				pass
			try:
				del venue['location']['state']
			except KeyError:
				pass
			venue = json.JSONEncoder().encode(venue)
			with open(out_folder+filename, 'a') as open_file:
				open_file.write('{0}\n'.format(venue))


if __name__ == "__main__":
	global data, client, count
	data = []
	client = create_client()
	count = 0
	# check_region('24.7131', '120.8784', '24.8541', '121.0332')	# Hsinchu City
	check_region('24.9605', '121.4570', '25.2110', '121.6660')	# Taipei City
	# check_region('24.6731', '121.2827', '25.3003', '122.0075')	# New Taipei City
	dict_json()