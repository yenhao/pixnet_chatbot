import foursquare
import json

global 	data, client

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
	global client
	print('check_region')
	# print(sw_lat, sw_lng)
	# print(ne_lat, ne_lng)
	sw = '{0},{1}'.format(sw_lat, sw_lng)
	ne = '{0},{1}'.format(ne_lat, ne_lng)
	# print('sw: ', sw)
	# print('ne: ', ne)

	result = client.venues.search(params={'intent':'browse','sw':sw, 'ne':ne, 'categoryId':'4d4b7105d754a06374d81259', 'limit':50})
	# print('result: ', result)
	if (len(result['venues']) == 50) and ((float(ne_lat)-float(sw_lat)) > 0.000009 or (float(ne_lng)-float(sw_lng)) > 0.000009):
		
		cen_lat = (float(sw_lat) + float(ne_lat)) / 2
		cen_lng = (float(sw_lng) + float(ne_lng)) / 2

		check_region(str(cen_lat), str(cen_lng), ne_lat, ne_lng)	# Right-UP
		check_region(sw_lat, str(cen_lng), str(cen_lat), ne_lng)	# Right-DOWN
		check_region(str(cen_lat), sw_lng, sw_lat, str(cen_lng))	# LEFT-UP
		check_region(sw_lat, sw_lng, str(cen_lat), str(cen_lng))	# LEFT-DOWN

	else:
		data.append(result)



if __name__ == "__main__":
	global data, client
	data = []
	client = create_client()
	check_region('24.7131', '120.8784', '24.8541', '121.0332')
