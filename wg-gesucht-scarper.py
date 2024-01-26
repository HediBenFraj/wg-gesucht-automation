from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from googletrans import Translator
import time 
import asyncio
import json
import os


async def handle_ad_button(driver):
    while True:
        ad_button = await check_condition(driver)

        if ad_button:
            # Perform some work
            await close_button(ad_button)

        # Sleep for a while before checking again (you can adjust the sleep duration)
        await asyncio.sleep(3)

async def check_condition(driver):
    try:
        button = driver.find_element(By.ID,"dismiss-button") 
        return button
        print("found it ")
    except Exception as e:
        print("ad button non existant")
        return False

async def close_button(ad_button):
    ad_button.click()

def filter_offers_by_price(driver,offers):
    filtered = []
    for offer in offers:
        offer_id = offer.get_attribute("id") 
        price_element = driver.find_element(By.CSS_SELECTOR,"#{} > div > div.col-sm-8.card_body > div.row.noprint.middle > div:nth-child(1) > b".format(offer_id))
        price = int(price_element.text.split()[0])
        if price >= 500:
            filtered.append(offer)
    return filtered

async def main_process(driver,final_offers):
    # Initiate translator
    translator = Translator()
    
    # get all offers from offer list 
    offers = driver.find_elements(By.CSS_SELECTOR, "[id*='liste-details-ad']")
    
    # filter out hidden offers
    initial_filtered_offers = [offer for offer in offers if "hidden" not in offer.get_attribute("id") ]
        
    #filter out offers with price < 500
    price_fitered_offers = filter_offers_by_price(driver,initial_filtered_offers)


    # start handeling filtered offers
    i = 0
    print("Found {} offers".format(len(price_fitered_offers)))
    while i<len(price_fitered_offers):
        try:
            print("######### 0000")
            filtered_offer= price_fitered_offers[i]
            print("############# PROCESSING OFFFER ############\n\n")
            offer_id = filtered_offer.get_attribute("id") 
            final_offer = {}
            link = driver.find_element(By.CSS_SELECTOR,"#{} > div > div.col-sm-8.card_body > div:nth-child(1) > div.col-sm-12.flex_space_between > h3 > a".format(offer_id))   
            price_element = driver.find_element(By.CSS_SELECTOR,"#{} > div > div.col-sm-8.card_body > div.row.noprint.middle > div:nth-child(1) > b".format(offer_id))
            surface_element = driver.find_element(By.CSS_SELECTOR,"#{} > div > div.col-sm-8.card_body > div.row.noprint.middle > div.col-xs-3.text-right > b".format(offer_id))
            final_offer['price'] =price_element.text
            final_offer['surface'] = surface_element.text
            final_offer['href']= link.get_attribute("href")
            location = "koln"
            print("######### 1111")
            try:
                location = link.get_attribute("href").split('/')[3].split(".")[0].split("-")[4:]
            except Exception as e:
                print('Error while parsing location')
                
            final_offer['location'] = " ".join(location)

            link.send_keys(Keys.CONTROL + Keys.RETURN)
            time.sleep(3)
            try: 
                driver.switch_to.window(driver.window_handles[1])
                features_elements = driver.find_elements(By.CSS_SELECTOR,"#main_column > div:nth-child(8) > div > div > div > div > div > div")
                features = []
                for feature_index,features_element in enumerate(features_elements):
                    print("translating feature {} out of {}".format(feature_index+1,len(features_elements)))
                    translated_feature = translator.translate(features_element.text, src="de", dest="en")
                    print(translated_feature.text)
                    features.append(translated_feature.text)

                description_tabs_elements = driver.find_elements(By.CSS_SELECTOR,"#main_column > div:nth-child(9) > div:nth-child(1) > div > div")
                description = {}
                print("################### WE HAVE "+str(len(description_tabs_elements))+"Tabs\n")
                for tab_element in description_tabs_elements:
                    try:
                        print("####### getting and traslation tab text ")
                        tab_element.click()
                        description_section_id = tab_element.get_attribute("data-text")[1:]
                        description_element = driver.find_element(By.ID,description_section_id)
                        translated_tab_text = translator.translate(tab_element.text, src="de", dest="en")
                        translated_description =  translator.translate(description_element.text, src="de", dest="en")
                        description[translated_tab_text.text] = translated_description.text
                    except Exception as e:
                        print("Couldn't read tab")
                final_offer["features"] = features
                final_offer["description"] = description
               
                final_offers.append(final_offer)
                i = i+1  
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    print("Error")
         
            except Exception as e:
                print("Can't open new offer")
           
        except Exception as e:
            print("Can't load page, AD PROBLEM PRObably")
   
async def count_matching_criterias(offers):
    required_criterias = ['own kitchen','Own bathroom','Laminate','Balcony','furnished','Washing machine']
    for offer in offers:
        print("\n")
        matching_criteria = 0
        for feature in offer['features']:
            for criteria in required_criterias:
                if criteria in feature:
                    print("Found matcing criteria")
                    matching_criteria = matching_criteria + 1
                    break  # Exit the loop once the substring is found
        offer["matching_criteria_number"] = matching_criteria


if __name__ == "__main__":

    # Set the path to the ChromeDriver executable
    chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'  # Update with the actual path to chromedriver
    
    # Create a Chrome WebDriver instance
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    offers = []
  
    # Navigate to a website
    driver.get('https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Koeln.73.1.1.0.html?offer_filter=1&city_id=73&sort_order=0&noDeact=1&categories%5B%5D=1&rent_types%5B%5D=2&sMin=25&rMax=800&radDis=5000&fur=1&sin=2&exc=2&kit=1&img_only=1')  # Replace with the URL of the website you want to visit
    time.sleep(1)
    accept_cookies_button = driver.find_element(By.CSS_SELECTOR,"#cmpwelcomebtnyes > a")
    accept_cookies_button.click()

    loop = asyncio.get_event_loop()
 
    loop.create_task(handle_ad_button(driver))

    loop.run_until_complete(main_process(driver,offers))

    loop.run_until_complete(count_matching_criterias(offers))

    sorted_offers = sorted(offers, key=lambda x: x["matching_criteria_number"], reverse=True)
    
    
    print("#### Processed {} offers".format(len(sorted_offers)))
    output_file_name = "wg-gesucht-output.json"
    if os.path.exists(output_file_name):
        print("removing file")
        os.remove(output_file_name)    
    print("riting")
    with open(output_file_name, "w") as file:
        print("writing file")
        file.write(json.dumps(sorted_offers))
    # Close the WebDriver when done

 

# Perform actions on the webpage
# Example: Find an element by its ID and click it
# driver.find_element_by_id('element_id').click()


