from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time 
import json
import os

wg_gesucht_output_file_path = "wg-gesucht-output.json"
sent_offers_file_path = "wg-gesucht_offers_sent.json"

message = "Lieber {},\n\nich hoffe, dass diese Nachricht dich gut erreicht. Mein Name ist Hedi Ben Fradj, und ich bin kürzlich auf Ihr Wohnungsangebot gestoßen, das sofort mein Interesse geweckt hat. Ich schreibe Ihnen, um mein starkes Interesse an der Immobilie zu bekunden und um mich weiter zu erkundigen.\n\nErlauben Sie mir, Ihnen ein wenig Hintergrundwissen über mich zu vermitteln: Ich bin ein 25-jähriger Software-Ingenieur aus Tunesien, der seit eineinhalb Jahren in Deutschland lebt. Mein Umzug nach Deutschland war sowohl durch persönliche als auch berufliche Entwicklungsmöglichkeiten motiviert. Ich habe das Glück, bei einem renommierten IT-Unternehmen angestellt zu sein, das mir einen stabilen und gut bezahlten Job bietet.\n\nEine meiner wichtigsten Prioritäten während meiner Zeit in Deutschland ist es, in die lokale Kultur und Sprache einzutauchen. Ich habe mich dem Erlernen der deutschen Sprache gewidmet, und Ihr Wohnungsangebot scheint mir eine ausgezeichnete Möglichkeit zu sein, diese Reise fortzusetzen und gleichzeitig einen komfortablen und sicheren Lebensraum zu schaffen.\n\nBesonders beeindruckt hat mich die Lage Ihrer Wohnung, die Größe, die perfekt zu meinen Anforderungen passt, und das Vorhandensein einer separaten Küche. Diese Merkmale entsprechen genau dem, was ich von einer neuen Wohnung erwarte.\n\nBitte lassen Sie mich wissen, ob die Wohnung noch verfügbar ist und ob ich der glückliche Mieter sein kann, der sie bekommt.\n\nIch werde Ihnen gerne alle erforderlichen Informationen zukommen lassen.\n\Mit besten Grüßen,\n\nHedi Ben Fradj."

wg_gesucht_offers= []
sent_offers=[]

wg_gesucht_login = "example@domain.exp"
wg_gesucht_password = "**********" # better add this to env variable 

with open(wg_gesucht_output_file_path, "r") as json_file:
    # Load the JSON data from the file into a Python dictionary
    wg_gesucht_offers = json.load(json_file)

with open(sent_offers_file_path, "r") as json_file:
    # Load the JSON data from the file into a Python dictionary
    sent_offers = json.load(json_file)

chrome_driver_path = '/home/hedi_ben_fraj/chromedriver'
print("Number of offers :",len(wg_gesucht_offers))
driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get('https://www.wg-gesucht.de/')  # Replace with the URL of the website you want to visit
time.sleep(1)
accept_cookies_button = driver.find_element(By.CSS_SELECTOR,"#cmpwelcomebtnyes > a")
accept_cookies_button.click()
time.sleep(1)
my_account_button = driver.find_element(By.CSS_SELECTOR,'#main-nav-wrapper > nav.navbar.navbar-default.desktop_nav.hidden-xs.hidden-sm > div.nav.navbar-nav.navbar-right > div > a')
my_account_button.click()
time.sleep(1)
email_input = driver.find_element(By.ID,'login_email_username')
email_input.send_keys(wg_gesucht_login)
time.sleep(1)
password_input = driver.find_element(By.ID,'login_password')
password_input.send_keys(wg_gesucht_password)
time.sleep(1)
login_button = driver.find_element(By.ID,'login_submit')
login_button.click()
time.sleep(1)
for offer in wg_gesucht_offers:
    print("Checking Offer needs processing")

    if offer["href"] in sent_offers:
        print("Message already sent to offer, SKipping!!")
        continue

    message_link = offer["href"][:26] + "nachricht-senden/" + offer["href"][26:]
    driver.get(message_link)
    time.sleep(2)
    try:
        accept_element = driver.find_element(By.ID,'sicherheit_bestaetigung')
        accept_element.click()
    except Exception as e:
        print("didn't find the cookies element")
    time.sleep(1)
    tenant_name = "kunde"
    try:
        tenant_name_raw_text = driver.find_element(By.CSS_SELECTOR,'#start_new_conversation > div:nth-child(5) > div.col-xs-10.col-sm-12 > label > b')
    except Exception as e:
        print("Couldn't get tenant name attempt div=5")
    try:
        tenant_name_raw_text = driver.find_element(By.CSS_SELECTOR,'#start_new_conversation > div:nth-child(6) > div.col-xs-10.col-sm-12 > label > b')
    except Exception as e:
        print("Couldn't get tenant name attempt div=6")
    tenant_name_pieces = tenant_name_raw_text.text.split(' ')[2:]
    tenant_name = " ".join(tenant_name_pieces).replace(":","")
    message_element = driver.find_element(By.ID,"message_input")
    formatted_string = message.format(tenant_name)
    message_element.send_keys(formatted_string)

    #submit message
    print("SENDING MESSAGE")
    try:
        send_message_button = driver.find_element(By.CSS_SELECTOR,'#messenger_form > div:nth-child(1) > div:nth-child(6) > button.btn.wgg_blue.pull-right.create_new_conversation')
    except Exception as e:
        print("Couldn't get the submit button attempt div=6")
    try:
        send_message_button = driver.find_element(By.CSS_SELECTOR,'#messenger_form > div:nth-child(1) > div:nth-child(5) > button.btn.wgg_blue.pull-right.create_new_conversation')
    except Exception as e:
        print("Couldn't get the submit button attempt div=5")
    send_message_button.click()
    time.sleep(1)
    sent_offers.append(offer["href"])
  
if os.path.exists(sent_offers_file_path):
    print("removing file")
    os.remove(sent_offers_file_path)    
print("writing")
with open(sent_offers_file_path, "w") as file:
    print("writing file")
    file.write(json.dumps(sent_offers))
    
input('Press ENTER to exit')