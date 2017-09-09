from bs4 import BeautifulSoup
import requests
import time
import json
import sys
import os
import requests.packages.urllib3.util.ssl_
#print(requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

SITE = 'https://www.ptt.cc'
SITE_SEED = '/bbs/'
SITE_FOOT = '/index.html'
BOARD = str(sys.argv[1])
# full url
SITE_URL = SITE + SITE_SEED + BOARD + SITE_FOOT

def get_page_number():
    html_text = session.get(SITE_URL, cookies={'over18': '1'}, verify = True)
    soup = BeautifulSoup(html_text.text.encode('utf-8'), 'html.parser')
    class_found = soup.find_all('a', {'class': 'btn wide'})
    #print (class_found[1]['href'])
    page_link = class_found[1]['href']
    start_index = page_link.find('index') + 5
    end_index = page_link.find('.html')
    num = page_link[start_index : end_index]
    page_number = int(num) + 1

    return page_number

def get_link(start_page, end_page):
    print("Get Link...")
    link_file = open(BOARD + '_article_links.txt', 'w')
    full = ''
    for index in range(start_page, end_page+1):
        page_url = SITE + SITE_SEED + BOARD + '/index' + str(index) + '.html'
        html_text = session.get(page_url, cookies={'over18': '1'}, verify = True)
        soup = BeautifulSoup(html_text.text.encode('utf-8'), 'html.parser')
        link_list = soup.find_all('div', {'class': 'title'})
    
        for link in link_list:
            if link.find('a') is not None:
                article_link = link.find('a')['href']
                link_file.write(SITE + article_link + '\n')

    link_file.close()

def get_article():
    print("Get article...")
    article_list = []
    with open(BOARD + '_article_links.txt') as fp:
        for line in fp:
            html_text = session.get(line.strip('\n'), cookies={'over18': '1'}, verify = True)
            soup = BeautifulSoup(html_text.text.encode('utf-8'), 'html.parser')
            article_id = line.split('/')[5]
            end_index = article_id.find('.html')
            article_id = article_id[0 : end_index]
            # print (article_id)

            author = ''
            title = ''
            post_time = ''
            try:
                article_meta = soup.find_all('div', {'class': 'article-metaline'})
                if article_meta:
                    title = article_meta[1].find('span', {'class': 'article-meta-value'}).string if article_meta[1].find('span', {'class': 'article-meta-value'}) else title
                    try:
                        if '食記' in title:
                            print("{0}\t{1}".format(article_id, title))
                            author = article_meta[0].find('span', {'class': 'article-meta-value'}).string if article_meta[0].find('span', {'class': 'article-meta-value'}) else author
                            
                            post_time = article_meta[2].find('span', {'class': 'article-meta-value'}).string if article_meta[2].find('span', {'class': 'article-meta-value'}) else post_time

                            push_list = []
                            push_num = 0
                            boo_num = 0
                            arrow_num = 0
                            main_content = soup.find('div', {'id': 'main-content'})
                            # find all pushes
                            pushes = main_content.find_all('div', {'class': 'push'})
                            for item in pushes:
                                if not item.find('span', {'class': 'push-tag'}):
                                    continue
                                push_tag = item.find('span', {'class': 'push-tag'}).string.strip(' ')
                                push_user = item.find('span', {'class': 'push-userid'}).string
                                push_content = item.find('span', {'class': 'push-content'}).getText()
                                # remove ': '
                                push_content = push_content[2:]
                                # print (push_content)
                                push_time = item.find('span', {'class': 'push-ipdatetime'}).string.strip('\n')
                                push_list.append({'push_tag': push_tag, 'push_user': push_user, 'push_content': push_content, 'push_time': push_time})
                                if push_tag == '推':
                                    push_num += 1
                                elif push_tag == '噓':
                                    boo_num += 1
                                else:
                                    arrow_num += 1
                            
                            # remove all meta tags
                            removed_elements = main_content.find_all('div', {'class': 'article-metaline'})
                            for element in removed_elements:
                                element.decompose()
                            try:
                                main_content.find('div', {'class': 'article-metaline-right'}).decompose()
                            except:
                                continue

                            removed_elements = main_content.find_all('span', {'class': 'f2'})
                            for element in removed_elements:
                                element.decompose()

                            # remove all pushes
                            for item in pushes:
                                item.decompose()

                            # get article main content
                            main_content = main_content.getText()

                            article = {
                                'Article_id': article_id,
                                'Board': BOARD,
                                'Title': title,
                                'Author': author,
                                'Post_time': post_time,
                                'Content': main_content,
                                'Push_num': push_num,
                                'Boo_num': boo_num,
                                'Arrow_num': arrow_num,
                                'Pushes': push_list
                            }

                            article_list.append(article)
                        else:
                            continue
                    except TypeError as e:
                        print(e)
                        continue
            except IndexError as e:
                print(e)
                continue
    
    fp.close()

    file_name = BOARD + '_article_' + str(time.strftime("%Y%m%d")) + '.json'
    article_file = open(file_name, 'w', encoding='utf-8')
    article_file.write(json.dumps(article_list, indent=4, ensure_ascii=False))
    article_file.close()


if __name__ == "__main__":
    session = requests.session()
    # get total page number
    total_page = get_page_number()
    print ("Total Page:{0}".format(total_page))

    start_page = int(sys.argv[2])
    if int(sys.argv[3]) == -1:
        end_page = total_page
    else:
        end_page = int(sys.argv[3])

    # find and store all article links
    get_link(start_page, end_page)

    # get and store all article content
    get_article()



