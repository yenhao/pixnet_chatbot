import json
from fb_fanpage_info import *

out_folder = '/home/adeline/Documents/food_data/'
filename = 'food_New_Taipei_City'
venues = []
with open(out_folder + filename) as open_file:
	for venue in open_file.readlines():
		venues.append(json.loads(venue))




for venue in venues:
	with open('/home/adeline/Documents/food_data/food_New_Taipei_City_2', 'a') as open_file:

		venue_id = None
		venue['fb'] = {}
		try:
			venue_id = venue['contact']['facebook']
	
		except KeyError:
			venue['fb']['category'] = None
			venue['fb']['checkings'] = None
			venue['fb']['overall_start_rating'] = None
			venue['fb']['phone'] = None
			venue['fb']['rating_count'] = None
			venue['fb']['restaurant_services'] = None
			venue['fb']['restaurant_specialties'] = None
			venue['fb']['talking_about_count'] = None
			venue['fb']['website'] = None
			venue = json.JSONEncoder().encode(venue)
			open_file.write('{0}\n'.format(venue))
			continue
	
		response = getTarget(venue_id)
		try:
			venue['fb']['category'] = response['category']
			venue['fb']['checkings'] = response['checkins']
			venue['fb']['overall_start_rating'] = response['overall_star_rating']
			venue['fb']['phone'] = response['phone']
			venue['fb']['rating_count'] = response['rating_count']
			venue['fb']['restaurant_services'] = response['restaurant_services']
			venue['fb']['restaurant_specialties'] = response['restaurant_specialties']
			venue['fb']['talking_about_count'] = response['talking_about_count']
			venue['fb']['website'] = response['website']
		except Exception as e:
			venue['fb'][str(e)] = None
			pass
		venue = json.JSONEncoder().encode(venue)
		open_file.write('{0}\n'.format(venue))
