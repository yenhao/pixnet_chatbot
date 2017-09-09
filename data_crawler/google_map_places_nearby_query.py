import random
import math
import requests
import json


API_Keys = [
    "GOOGLE_PLACES_API_KEY_1",
    "GOOGLE_PLACES_API_KEY_2"
]

def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
    R = 6371; # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)  # deg2rad below
    dLon = deg2rad(lon2-lon1) 
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
    d = R * c # Distance in km
    return d

def deg2rad(deg):
    return deg * (math.pi/180)

def check_region(sw_lat, sw_lng, ne_lat, ne_lng):
    global data

    sw = '{0},{1}'.format(sw_lat, sw_lng)
    ne = '{0},{1}'.format(ne_lat, ne_lng)
    
    lat = str((float(sw_lat)+float(ne_lat))/2)
    lng = str((float(sw_lng)+float(ne_lng))/2)
    r = str(getDistanceFromLatLonInKm(float(sw_lat), float(sw_lng), float(ne_lat), float(ne_lng))*1000/2)

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'+ \
                    'location='+lat+','+lng+'&'+ \
                    'radius='+r+'&'+ \
                    'type=restaurant&'+ \
                    'key='+API_Keys[random.randint(0, len(API_Keys)-1)]
    req = requests.get(url)
    res = json.loads(req.text)
    print(url)
    print(len(res['results']))

    if (len(res['results']) == 20) and ((float(ne_lat)-float(sw_lat)) > 0.000009 or (float(ne_lng)-float(sw_lng)) > 0.000009):

        cen_lat = (float(sw_lat) + float(ne_lat)) / 2
        cen_lng = (float(sw_lng) + float(ne_lng)) / 2

        check_region(str(cen_lat), str(cen_lng), ne_lat, ne_lng)	# Right-UP
        check_region(sw_lat, str(cen_lng), str(cen_lat), ne_lng)	# Right-DOWN
        check_region(str(cen_lat), sw_lng, sw_lat, str(cen_lng))	# LEFT-UP
        check_region(sw_lat, sw_lng, str(cen_lat), str(cen_lng))	# LEFT-DOWN

    else:
        for item in res['results']:
            data.append({
                "name":item['name'],
                "place ID":item['place_id']
            })

def export_to_file():
    global data
    with open("google_restaurant_places.taipei", 'w') as fp:
        fp.write(json.dumps(data))


city_geometry = {
    "Keelung City":["25.0525","121.6268","25.1956","121.8084"],
    "Taipei City":["24.9605","121.4570","25.2110","121.6660"],
    "New Taipei City":["24.6731","121.2827","25.3003","122.0075"],
    "Hsinchu City":["24.7131","120.8784","24.8570","121.0332"],
    "Taichung City":["23.9986","120.4607","24.4430","121.4510"],
    "Tainan City":["22.8873","120.0277","23.4138","120.6563"],
    "Hualien City":["23.0978","120.9866","24.3706","121.7736"],
    "Taitung City":["22.6847","121.0262","22.8196","121.2011"],
    "Yilan":["24.3095","121.3167","24.9884","121.9662"],
    "Changhua City":["23.7860","120.2391","24.1963","120.6839"]
}     

if __name__ == "__main__":
	global data
	data = []
	check_region(*city_geometry["Taipei City"])
	export_to_file()  

