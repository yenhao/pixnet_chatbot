import requests, os, time, json
import argparse, sys
from datetime import datetime

from multiprocessing import Pool


app_id = '455473691321590'
app_secret = 'ea74b6c26e87e75095aacbcd18d5b0db'

token = 'access_token=' + app_id + '|' + app_secret

def getRequests(url):
    requests_result = requests.get(url, headers={'Connection':'close'}).json()
    time.sleep(0.01)

    return requests_result

def getTarget(target):

    #Get list of feed id from target.
    feeds_url = 'https://graph.facebook.com/v2.10/' + target + '/?fields=name,location,checkins,overall_star_rating,about,affiliation,band_interests,category,company_overview,contact_address,country_page_likes,description,rating_count,record_label,restaurant_services,restaurant_specialties,schedule,talking_about_count,username,website,phone,general_info&' + token

    feed_list = getRequests(feeds_url)
    
    return feed_list



### Example ###

# target = 'appledaily.tw'
# print(getTarget(target))
# {'phone': '(02)6601-3456', 'talking_about_count': 889100, 'about': '24小時陪你看新聞，我們是最勁爆、最八卦、最貼近大家生活的台灣蘋果日報！我們的網站是 http://www.appledaily.com.tw', 'category': 'Media/News Company', 'description': '投訴爆料請Email至news@appledaily.com.tw，電話：0809-012-555 ，WhatsApp：0971-012-555 ， 傳真：0809-013-666 ，投訴爆料請Email至news@appledaily.com.tw，電話：0809-012-555 ，WhatsApp：0971-012-555 ， 傳真：0809-013-666 ', 'name': '蘋果日報', 'rating_count': 0, 'id': '232633627068', 'company_overview': '【蘋果日報網站】\n《蘋果日報》網站是台灣率先以「圖像式+文字」完整呈現新聞報導內容的新聞類網站，自2003年5月創站以來，豐富多彩的圖文式新聞呈現，向來獲得廣大讀者的喜愛！並在提供讀者更完整、更優質的內容，以及為了加深讀者對《蘋果日報》的品牌印象。\n\n【蘋果日報網站得獎紀錄】\n2008.03 亞洲媒體大獎(Ifra)-最佳網路媒體(Best in Online Media)\n\n【未來展望】\n《蘋果日報》一向強調「給讀者要看的報導」，因此吸引了大量的閱聽眾；我們在網站內容的經營除了與趨勢潮流結合之外，也隨時因應現有政經局勢更改原訂的方向與計畫，以期不被淘汰。未來，《蘋果》將繼續在現有的基礎上，更深耕內容的深度與廣度，朝華人世界中最豐富、互動、多元新聞網站目標邁進。\n\n', 'website': 'http://www.appledaily.com.tw', 'username': 'appledaily.tw', 'checkins': 6132, 'location': {'country': 'Taiwan', 'city': 'Taipei', 'longitude': 121.58148765564, 'latitude': 25.064978020181}}

