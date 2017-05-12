import requests
from bs4 import BeautifulSoup as bs4
import re
import json
import time
from selenium import webdriver
import phonenumbers
import pandas as pd
import csv
import os
os.chdir('C:\\Users\\Stevens\\Desktop\\BIA_660\\Project')

#=======================================================================================
'''
scraping urls and storing in list to iterate through for individual posts
'''

# url to build beautifulsoup loop
base_url = 'https://newyork.craigslist.org/search/hhh'
end_url = '&availabilityMode=0&excats=18-1-20-1-1-17-7-34-22-22-1&max_bathrooms=1&max_bedrooms=1&min_bathrooms=1&min_bedrooms=1'

all_data = []
def get_urls(url = 'https://newyork.craigslist.org/search/hhh'):

    # empty dictionary to store urls
    urls = []
    # for each page in results page
    for page in range(0, 23):
        # build url
        if page == 0:
            url = base_url
        else:
            url = base_url + '?s=' + str (page * 120) + end_url

        # retrieve urls
        rsp = requests.get(url,headers = { 'User-Agent': 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01', })
        body = bs4(rsp.text, 'html.parser')
        listings = body.find_all('li', class_='result-row')

        # store urls in list
        for listing in listings:
            urls.append('https://newyork.craigslist.org' + listing.a['href'])

        time.sleep(1)  # seconds

    # write list to csv
    with open('urls.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for row in urls:
            writer.writerow([row])

    return urls

# run script
urls = get_urls()

#=======================================================================================
'''
scraping individual posts
'''

# loop through list of urls
for apt in urls:

    # pause each iteration so don't get blocked by craigslist
    time.sleep (1)

    apt = 'https://newyork.craigslist.org/mnh/abo/6097149837.html'
    # get html code with beautifulsoup
    rsp = requests.get(apt)
    body = bs4(rsp.text, 'html.parser')

    # create empty dictionary to store variables
    attribute_dict = {}

    # Extract phone numbers
    # try:
    #     phone_pres = {'showcontact': True}
    #     show_contact = body.findAll('a', {'class': "showcontact"}, phone_pres)
    #     if show_contact is not None:
    #         driver = webdriver.Chrome('C:/Users/Stevens/Desktop/Python/chromedriver.exe')
    #         driver.get(apt)
    #         driver.find_element_by_xpath("""//*[@id="postingbody"]/a""").click()
    #         time.sleep(2)
    #
    #         source = driver.page_source
    #         driver.quit()
    #
    #         x = source.split("""<section id="postingbody">""")[1].split('</section>')[0]
    #         for match in phonenumbers.PhoneNumberMatcher(x, "US"):
    #             attribute_dict['phone'] = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
    # except:
    #     pass

    # Extract Location
    # try:
    #    loc_pres = {'data-latitude': True, 'data-longitude': True}
    #   location = body.find('div', {'class': 'viewposting'}, attrs= loc_pres)
    #
    #    if location:
    #        attribute_dict['latitutde'] = location["data-latitude"]
    #        attribute_dict['longitude'] = location['data-longitude']
    # except:
    #    pass

    # extract borough
    try:
        borough = body.find('li', {'class': 'crumb subarea'})
        attribute_dict['borough'] = borough.text.replace('\n', "").replace('>', "")
    except:
        pass

    # extract parenthesis in title
    try:
        parenthesis = body.findAll('span', {'class': 'postingtitletext'})
        parenthesis = parenthesis[0].small
        attribute_dict['parenthesis'] = parenthesis.text.strip().replace("(", "").replace(")", "")
    except:
        pass

    #extract availability
    try:
        attribute_dict['availability'] = body.find('span', class_='housing_movein_now property_date')['data-today_msg']
        attribute_dict['date_available'] = body.find('span', class_='housing_movein_now property_date')['data-date']
    except:
        pass

    # extract post id, datetime, and update datetime
    try:
        posted_info = body.findAll('div', {'class': 'postinginfos'})[0].text.strip().split('\n')

        for info in posted_info:
            if 'post id:' in info:
                attribute_dict['post_id'] = info.replace('post id: ', '')

            if 'posted:' in info:
                attribute_dict['post_date'] = info.replace('posted: ', '').split(' ')[0]

            if 'posted:' in info:
                attribute_dict['post_time'] = info.replace('posted: ', '').split(' ')[-1]

            if 'updated:' in info:
                attribute_dict['update_date'] = info.replace('updated: ', '').split(' ')[0]

            if 'updated:' in info:
                attribute_dict['update_time'] = info.replace('updated: ', '').split(' ')[-1]
    except:
        pass

    # Extract title
    try:
        attribute_dict['title'] = body.find('span', {'id': 'titletextonly'}).text
    except:
        pass

    # Extract price
    try:
        attribute_dict['price'] = body.find('span', {'class': 'price'}).text
    except:
        pass

    # Extract number of images
    try:
        attribute_dict['images'] = body.find('span', {'class': 'slider-info'}).text.split(' ')[-1]
    except:
        pass

    # Extract bed, bath, size, type, pets, laundry, parking, smoking, furnished
    try:
        attributes = []
        attributes_data = body.findAll('p', class_='attrgroup')
        attributes = attributes_data[0].findAll('span') + attributes_data[1].findAll('span')
        attributes2 = [item.text.strip().split('\n')[0] for item in attributes]

        for attribute in attributes2:
            if 'BR' in attribute:
                attribute_dict['bedroom'] = attribute.split(' / ')[0].replace('BR', '')

            if 'Ba' in attribute:
                attribute_dict['bathroom'] = attribute.split(' / ')[1].replace('Ba', '')

            if 'ft' in attribute:
                attribute_dict['square_footage'] = attribute.replace('ft2', '')

            if 'listed by' in attribute:
                attribute_dict['listed_by'] = attribute.replace('listed by: ', '')

            if attribute in ['apartment', 'condo', 'cottage/cabin', 'duplex', 'flat',
                             'house', 'in-law', 'loft', 'townhouse', 'manufactured', 'assisted living', 'land']:
                attribute_dict['housing_type'] = attribute

            if 'cat' in attribute:
                attribute_dict['cat'] = attribute

            if 'dog' in attribute:
                attribute_dict['dog'] = attribute

            if 'furnished' in attribute:
                attribute_dict['furnished'] = attribute

            if attribute in ['w/d in unit', 'laundry in bldg', 'laundry on site', 'w/d hookups']:
                attribute_dict['laundry'] = attribute

            if attribute in ['carport', 'attached garage', 'detached garage', 'off-street parking',
                             'street parking', 'valet parking']:
                attribute_dict['parking'] = attribute

            if 'smoking' in attribute:
                attribute_dict['smoking'] = attribute
     except:
        pass

    # got old post id if re-posted
    js = body.findAll('script', {'type': 'text/javascript'})[3]
    try:
        a = re.compile('var repost_of = (.*)')
        for script in js:
            if script:
                m = a.search(script.string)
                y = m.group(0)
                attribute_dict['post_id_old'] = y.split(' ')[-1].strip(';')
    except:
        attribute_dict['post_id_old'] = 'NA'

    # Extract the description of the property
    try:
        description = body.find('section', {'id': 'postingbody'}).text.replace("\n", " ").strip()
        attribute_dict['description'] = re.sub("\s\s+", " ", description).replace('QR Code Link to This Post ', "")
    except:
        pass

    # Extract fees and conditions
    try:
        requirements = body.findAll('ul', {'class': 'notices'})
        attribute_dict['requirements']= re.sub(r'[^\w]', ' ', requirements[0].text.strip().split(':')[1])
    except:
        pass

    # store attributes in pandas array
    attribute_dict = pd.Series(attribute_dict, name=id)
    all_data.append(attribute_dict)

# change pandas array into dataframe and save for processing
all_data_df = pd.DataFrame(all_data)
all_data_df.to_csv(r'C:\Users\Stevens\Desktop\BIA_660\Project\sample_data.csv', encoding='utf-8')

#=======================================================================================
'''
find which posts have been removed to classify as spam
'''

# initiate empty list of urls to read from csv
urls_check = []

# read each row from csv and store in list
with open('urls.csv', "r") as f_obj:
    reader = csv.reader(f_obj)
    for row in reader:
        urls_check.append(" ".join(row))

# create new file for storing removed posts
with open('post_removed_sample.csv','w') as f:
    writer=csv.writer(f, delimiter=',')

    # loop through urls to scrape reason for removal if removed
    for apt in urls_check:

        # sleep so servers do not ban
        time.sleep (1)

        #get beautifulsoup driver
        rsp = requests.get(apt, headers={'User-Agent': 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01', })
        body = bs4(rsp.text, 'html.parser')

        # scrape reason if removed and write to csv
        if body.find ('div', {'class': 'removed'}) is not None:
            reason = body.find ('div', {'class': 'removed'}).text.replace('\n', "").strip()
            writer.writerow([apt, reason])



sample scam: https://newyork.craigslist.org/brk/abo/6085127951.html
sample delete: https://newyork.craigslist.org/mnh/abo/6074767516.html

apt = 'https://newyork.craigslist.org/brk/abo/6085127951.html'
rsp = requests.get(apt, headers={'User-Agent': 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01', })
body = bs4(rsp.text, 'html.parser')

if body.find ('div', {'class': 'removed'}) is not None:
    reason = body.find ('div', {'class': 'removed'}).text.replace ('\n', "").strip ()
    print([apt, reason])



