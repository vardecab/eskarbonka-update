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

# === start + run time ===

print ("Starting...")
start = datetime.now()  # run time

# === URL to scrape ===

page_url = "https://eskarbonka.wosp.org.pl/5jcgfw" # *NOTE: Traceback; This is probably because of 'mod_security' or some similar server security feature which blocks known spider/bot user agents (urllib uses something like python urllib/3.3.0, it's easily detected). // https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping 

# === macOS notification ===

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

# === file to store value ===

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
# value = 110 # debug
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
        # !FIX: translate back to PL and encode special characters
        print ("Nothing has changed. The current amount is:", value, "PLN.")
        notify("eskarbonka-update", "Nothing has changed.") # macOS notification
    if value > stored_value: 
        print ("""There's more! New amount:""", value, """PLN. It's""", value-stored_value, "PLN more!")
        notify("eskarbonka-update", "We have more!") # TODO: add value
        # !FIX: can't have "That's" due to EOF problems
        pause_duration = 5 # wait 5 seconds before opening
        print ("Waiting for", pause_duration, "seconds before opening URL...")
        with alive_bar(pause_duration, bar="circles", spinner="dots_waves") as bar: # progress bar
            for second in range(0,pause_duration): # wait 5 seconds in total
                time.sleep(1) # wait 5 x 1 sec
                bar() # update progress bar
        webbrowser.open(page_url) # open URL
    if value < stored_value: 
        print ("Something is wrong... The new amount is lower than the previous amount.")
        notify("eskarbonka-update", "Something is wrong... The new amount is lower than the previous amount.")
except NameError:
    print ("""First run, couldn't compare to anything.""")

# === run time ===

print ("Script run time:", datetime.now()-start)