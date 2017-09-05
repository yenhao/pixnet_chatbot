import foursquare
import json
import time
global client, data

def createClient():
	global client
	# Construct the client object
	# client = foursquare.Foursquare(client_id='L1UFPLBHBD5SMXN1UFXH4YJBMUANZRTEUYBYOFV5VDE5AWOF', client_secret='GG4F1N4ROEIQNMGNVQXATCU1VKLO30RNC0J3N11ZP25DE0U2')
	# client = foursquare.Foursquare(client_id='CJDUDEUGWR2JUSOJVHIXC3YFICHH2VFVCLHMTB4EMGE5RBKG', client_secret='CHLFN4I0GRBZ30OEPVYIRHGKXC4SSE4RZYVUMKKMS4ECNXUQ')
	# client = foursquare.Foursquare(client_id='P5U2CXX1J2OMF4DWDE05S5JBXYZMRR4OODPQT4BUNRNSDRE1', client_secret='RJQIU4H13SZQ3H41RMMF25WQL1F0COD2JBUVDGFKETELJEVY')
	client = foursquare.Foursquare(client_id='JBM14FCYVKHKEH4PNCINGTUSE0KNADOYJJM3NSXTSTFJUZ2O', client_secret='AHDDBJAM3FTAU3AMJHVSYDOVATTI1AGCKLWVHPRSTMINLWOH')
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
	with open('/home/adeline/Documents/food_data/food_Taipei_City_tips', 'a') as write_file:
		with open('/home/adeline/Documents/food_data/food_Taipei_City_fb') as read_file:
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