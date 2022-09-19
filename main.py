# Imports

# for soup find
from bs4 import BeautifulSoup as bs
# uses a automated web browser for automations
from selenium import webdriver
# some important modules for selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
# for data & time data
from datetime import datetime as dt
from datetime import time
import time as t 
# for setting up a default timezone
from pytz import timezone
# for connecting to the telegram bot using the token
import telebot
# used to connect to the firebase server
import firebase_admin
from firebase_admin import credentials, firestore
# module for getting dictionary difference/changes made
import dictdiffer  
 

# Chrome options for selenium server
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

# Intitialisation of firestore database
cred = credentials.Certificate("NAME_OF_FIREBASE_CREDENTIALS")
database = firebase_admin.initialize_app(cred)
db = firestore.client(database)

# Helps to set timezone to INDIA
tz = timezone("Asia/Kolkata")

# These emojis are used in the messages sent  by the bot
tick = "✔️"
cross = "❌"
exclamation = "❗"

# Users list
users = []

# Get TeleBot Token from the database
bot = telebot.TeleBot("TOKEN_TELEGRAM_BOT")

# This is the timeout required to run the SEND function again and again
timeout = 900

# swiggy/zomato link for the preffered restaurants
zlink = "https://www.zomato.com/kanpur/urban-vada-pav-ashok-nagar/order"
slink = "https://www.swiggy.com/restaurants/urban-vada-pav-harsh-nagar-ashok-nagar-kanpur-416347"


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or dt.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


# get current time ex: 12:45 PM
def get_date():
    now = dt.now(tz)
    current_time = now.strftime("%I:%M %p")
    return str(current_time)


def getList(dict):
    return dict.keys()


# Here you will grab the list of users from the database
#doc_users = db.collection("Users").document("users")
#users_db = doc_users.get().to_dict()
#USERS = list(getList(users_db))

def get_Swiggy_menu():
    current_swiggy_data = {}
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(slink)
    source = driver.page_source
    soup = bs(source, "html.parser")
    menu = soup.find_all("div", attrs={"class": "_2dS-v"})
    for categories in menu:
        try:
            category = categories.find_all("div" , attrs={"class": "_2wg_t"})
            category_name = categories.find("h2", attrs={"class": "M_o7R _27PKo"}).get_text()
        except:
            category_name = categories.find("h2", attrs={"class": "M_o7R"}).get_text()
        # print(category_name)
        if "Recommended" not in category_name:
            category_name_data = {}
            for item in category:
                    # print(item)
                    item_name = item.find("h3",attrs={"class": "styles_itemNameText__3ZmZZ"}).getText()
                    item_price = item.find("span", attrs={"class": "rupee"}).getText()
                    item_status = item.find("div", attrs={"class": "styles_itemImageContainer__3Czsd"}).getText()
                    if "ADD" in item_status:
                        print("Add")
                    elif "Unavailable" in item_status:
                        print("Unavailable")
                    else:
                        print("continue")
                        continue
#                    a = item_name + " " + item_price
                    category_name_data[item_name] = item_price
                    # print(category_name_data)
            current_swiggy_data[category_name] = category_name_data
#            print(current_swiggy_data)
    return current_swiggy_data


def get_Zomato_menu():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(zlink)
    current_zomato_data = {}
    for i in range(2,20):
        try:
                category_name = driver.find_element(by=By.XPATH, value=f"/html/body/div[1]/div/main/div/section[4]/section/section[2]/section[{i}]/h4").get_attribute("innerHTML")
                if category_name != "" and category_name != "Recommended":
                    items = []
                    for j in range(1,25):                                        
                        try:
                            item_name = driver.find_element(by=By.XPATH, value=f"/html/body/div[1]/div/main/div/section[4]/section/section[2]/section[{i}]/div[2]/div[{j}]/div/div/div[2]/div/div/h4").get_attribute("innerHTML")
                            try:
                                item_price = driver.find_element(by=By.XPATH, value=f"/html/body/div[1]/div/main/div/section[4]/section/section[2]/section[{i}]/div[2]/div[{j}]/div/div/div[2]/div/div/div[2]/span").get_attribute("innerHTML")
                            except:
                                item_price = driver.find_element(by=By.XPATH, value=f"/html/body/div[1]/div/main/div/section[4]/section/section[2]/section[{i}]/div[2]/div[{j}]/div/div/div[2]/div/div/div/span").get_attribute("innerHTML")
                            item_price = item_price[1:]
                            listing = [item_name, item_price]
                            items.append(listing)
                        except:
                            pass
                    category_name_data = {}
                    for i in items:
                        item_name = i[0] 
                        item_price = i[1]
                        category_name_data[item_name] = item_price
                    current_zomato_data[category_name] = category_name_data
        except:
            pass
    return current_zomato_data


def update_Swiggy_data(current_swiggy_data):
    swiggy_menu_db = db.collection("SwiggyMenu").document("Menu")
    swiggy_menu_db.set(current_swiggy_data)
def update_Zomato_data(current_zomato_data):
    swiggy_menu_db = db.collection("ZomatoMenu").document("Menu")
    swiggy_menu_db.set(current_zomato_data)


def get_Swiggy_db_data():
    swiggy_menu_db = db.collection("SwiggyMenu").document("Menu")
    return swiggy_menu_db.get().to_dict()
def get_Zomato_db_data():
    zomato_menu_db = db.collection("ZomatoMenu").document("Menu")
    return zomato_menu_db.get().to_dict()


def check_Changes_Swiggy_data(current_swiggy_data,db_swiggy_data):
    list_changes = []
    for diff in list(dictdiffer.diff(db_swiggy_data,current_swiggy_data)):         
        list_changes.append(diff)
    return list_changes
def check_Changes_Zomato_data(current_zomato_data,db_zomato_data):
    list_changes = []
    for diff in list(dictdiffer.diff(db_zomato_data,current_zomato_data)):         
        list_changes.append(diff)
    return list_changes



def main():
  if is_time_between(time(9, 00), time(22, 15), dt.now(tz).time()):
        swiggy_db = db.collection("Swiggy").document("Status")
        swiggy_status = swiggy_db.get().to_dict().get("Status") 
        if swiggy_status != "Offline":
            current_swiggy_menu = get_Swiggy_menu()
            changes = check_Changes_Swiggy_data(current_swiggy_menu,get_Swiggy_db_data())
            if changes != []:
                current_swiggy_menu = get_Swiggy_menu()
                changes = check_Changes_Swiggy_data(current_swiggy_menu,get_Swiggy_db_data())
            print(changes)
            if len(changes) == 0:
                pass
            else:
                text = "Swiggy :\n"
                for i in changes:
                    if i[0] == "change":
                        namings = i[1].split(".")
                        a = exclamation + " " + str(namings[1]) +" changes from " + str(i[2][0]) + " to " + str(i[2][1]) + "\n"
                        text = text + a
                    elif i[0] == "remove":
                        for j in i[2]:
                            (p,q) = j
                            a = cross + " " + str(p) + " removed" + "\n"
                            text = text + a
                    elif i[0] == "add":
                        for j in i[2]:
                            (p,q) = j
                            a = tick + " " + str(p) + " added" + "\n"
                            text = text + a
                for i in users:
                    bot.send_message(i,text)
                update_Swiggy_data(current_swiggy_menu)
            print(get_date())
        
        zomato_db = db.collection("Zomato").document("Status")
        zomato_status = zomato_db.get().to_dict().get("Status")   
        if zomato_status != "Offline":
            current_zomato_menu = get_Zomato_menu()
            changes = check_Changes_Zomato_data(current_zomato_menu,get_Zomato_db_data())
            if changes != []:
                current_zomato_menu = get_Zomato_menu()
                changes = check_Changes_Zomato_data(current_zomato_menu,get_Zomato_db_data())
            print(changes)
            if len(changes) == 0:
                    pass
            else:
                    text = "Zomato :\n"
                    for i in changes:
                        if i[0] == "change":
                            namings = i[1].split(".")
                            a = exclamation + " " + str(namings[1]) +" changes from " + str(i[2][0]) + " to " + str(i[2][1]) + "\n"
                            text = text + a
                        elif i[0] == "remove":
                            for j in i[2]:
                                (p,q) = j
                                a = cross + " " + str(p) + " removed" + "\n"
                                text = text + a
                        elif i[0] == "add":
                            for j in i[2]:
                                (p,q) = j
                                a = tick + " " + str(p) + " added" + "\n"
                                text = text + a
                    for i in users:
                        bot.send_message(i,text)
                    update_Zomato_data(current_zomato_menu)
            print(get_date())
            
  else:
    pass

#main()
while True:
    try:
        main()
        t.sleep(300)
    except Exception as e:
        print(e)
    t.sleep(5)

