import random
import math
import requests
import json


API_Keys = [
    "GOOGLE_PLACES_API_KEY_1",
    "GOOGLE_PLACES_API_KEY_2"
]


def get_place_details(placeid, lang):
    key = API_Keys[random.randint(0, len(API_Keys)-1)]
    url = 'https://maps.googleapis.com/maps/api/place/details/json?'+ \
                    'placeid='+placeid+'&'+ \
                    'language='+lang+'&'+ \
                    'key='+ key
    r = requests.get(url)
    res = json.loads(r.text)
    
    try:
        if 'reviews' in res['result']:
            rev = res['result']['reviews']
        else:
            rev = []
        return {"place ID":placeid, "reviews":rev}
    except Exception as e:
        print(key)
        print(res)
        raise KeyError("Error")

def export_to_file(data):
    with open("google_restaurant_reviews.taipei", 'w') as fp:
        fp.write(json.dumps(data))


if __name__ == "__main__":
    with open('google_restaurant_places.taipei') as data_file:    
        doc = json.load(data_file)
    data = []
    for place in doc:
        data.append(get_place_details(place['place ID'], 'en'))
        data.append(get_place_details(place['place ID'], 'zh-TW'))
    export_to_file(data)