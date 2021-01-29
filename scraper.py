# === libs ===

from urllib.request import urlopen, Request # open URLs; Request to fix blocked user-agent: https://stackoverflow.com/questions/16627227/
from bs4 import BeautifulSoup # BeautifulSoup; parsing HTML
import ssl # fix certificate issue: https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
import certifi # fix certificate issue: https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
import sys # exit()
from datetime import datetime # calculate script's run time
import re # regex; extract substrings
import pickle # storage data; https://wiki.python.org/moin/UsingPickle
import os # show notification on macOS; https://stackoverflow.com/questions/17651017/python-post-osx-notification
import webbrowser # open browser 
import time # delay execution; https://stackoverflow.com/questions/3327775/can-the-execution-of-statements-in-python-be-delayed
from alive_progress import alive_bar # progress bar
import pync # macOS notification

# === start + run time ===

print ("Starting...")
start = datetime.now()  # run time

# === URL to scrape ===

page_url = "https://eskarbonka.wosp.org.pl/5jcgfw" # *NOTE: Traceback; This is probably because of 'mod_security' or some similar server security feature which blocks known spider/bot user agents (urllib uses something like python urllib/3.3.0, it's easily detected). // https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping 

# === file to store data ===

filename = "value.pk" 

# === scrape ===

print ("Opening page...")
print (page_url) # debug
request = Request(page_url, headers={'User-Agent': 'XYZ/3.0'}) # fix: Request -> blocked user agent
page = urlopen(request, timeout=3, context=ssl.create_default_context(cafile=certifi.where())) # fix: context -> certificate issue

print ("Scraping page...")
soup = BeautifulSoup(page, 'html.parser')  # parse the page

get_content = soup.find("div", {"class":"wosp-price-ind text-big mt-5 mb-3"}).text # get div content
value = re.search("[0-9]+", get_content) # extract only numbers

try: # might crash on first run
    with open(filename, 'rb') as file: # load your data back to memory so we can save new value; NOTE: b = binary
        stored_value = pickle.load(file)
except IOError:
    print ("First run - no file exists.")

value = int(value[0]) # select first match from regex
# value =  # debug
# print ("value is", type(value)) # debug
# print ("stored_value is", type(stored_value)) # debug

# === store value for further use ===

try:
    with open(filename, 'wb') as file: # open pickle file
        pickle.dump(value, file) # dump your data into the file
except IOError: 
    print ("""File doesn't exist.""")
    
# === compare values ===

try: # first run failsafe 

    stored_value = stored_value 

    if value == stored_value: 
        print ("Nothing has changed. The current amount is:", value, "PLN.") # debug
        pync.notify(f'"W eSkarbonce jest {value} zł."', title='eSkarbonka', subtitle='Nic się nie zmieniło.', open="https://eskarbonka.wosp.org.pl/5jcgfw", contentImage="https://upload.wikimedia.org/wikipedia/en/thumb/1/14/WO%C5%9AP.svg/1200px-WO%C5%9AP.svg.png", sound="Funk") # appIcon="" doesn't work 

    if value > stored_value: 
        print ("""There's more! New amount:""", value, """PLN. It's""", value-stored_value, "PLN more!") # debug
        pync.notify(f'"W eSkarbonce jest teraz {value} zł."', title='eSkarbonka', subtitle=f'"Jest więcej o {value-stored_value} zł!"', open="https://eskarbonka.wosp.org.pl/5jcgfw", contentImage="https://upload.wikimedia.org/wikipedia/en/thumb/1/14/WO%C5%9AP.svg/1200px-WO%C5%9AP.svg.png", sound="Funk")

    if value < stored_value: 
        print ("Something is wrong... The new amount is lower than the previous amount.") # debug
        pync.notify(f'"W eSkarbonce jest teraz {value} zł."', title='eSkarbonka', subtitle='Coś jest nie tak... Jest mniej niż było.', open="https://eskarbonka.wosp.org.pl/5jcgfw", contentImage="https://upload.wikimedia.org/wikipedia/en/thumb/1/14/WO%C5%9AP.svg/1200px-WO%C5%9AP.svg.png", sound="Funk")

except NameError:
    print ("""First run, couldn't compare to anything.""")

# === run time ===

print ("Script run time:", datetime.now()-start)