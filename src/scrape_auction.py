#!/bin/python3
import time
from typing import List, Dict
from datetime import datetime as DT
import pytz
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import csv

SITE_URL = 'http://govdeals.com'
MAKES = [
    'ford', # Ford | FORD
]
MODELS = [
    'taurus', # Taurus | Interceptor Taurus | Police Taurus
    'fpis',   # FPIS (ford police interceptor sedan)
    'sedan',  # police/interceptor sedan
]
DATA_FILE = 'data.csv'

# https://www.selenium.dev/documentation/webdriver/

class SiteHelper:
    
    WAIT_TIMEOUT = 30 # seconds
    RESULTS_PER_PAGE = 120 # Use 24 for development of multipage logic
    RESET_MAKE_TEXT = 'Select Make'
    
    def __init__(self, site_url):
        self._max_models = None # Number of models when "Select Make" is selected as make select option
        self._adv_search_uri = '/advanced-search/'
        self._site_url = site_url
        self._driver = webdriver.Chrome()
        self._driver.get(self._site_url)
        self._driver.maximize_window() # Hope for display of all elements with responsive layout
        self.accept_cookies()
    
    def quit(self):
        self._driver.quit()    
    
    def accept_cookies(self, timeout = WAIT_TIMEOUT):
        try:
            self.wait_and_click_by_id('onetrust-accept-btn-handler', timeout = 5)
            print('Accepted cookies')
        except TimeoutException:
            print("Failed to accept cookies; Likely already accepted")
            
    def wait_by_id(self, elem_id, timeout = WAIT_TIMEOUT):
        is_elem_disp = lambda d : d.find_element(By.ID, elem_id).is_displayed()
        wait = WebDriverWait(self._driver, timeout = timeout)
        wait.until(is_elem_disp)
         
    def wait_and_click_by_id(self, elem_id, timeout = WAIT_TIMEOUT):
        self.wait_by_id(elem_id, timeout = timeout)
        self._driver.find_element(By.ID, elem_id).click()
    
    def wait_and_get_select_options_by_id(self, elem_id, timeout = WAIT_TIMEOUT):
        self.wait_by_id(elem_id, timeout = timeout)
        select = Select(self._driver.find_element(By.ID, elem_id))
        return select.options
    
    def wait_and_select_option_by_id(self, elem_id, option: str, timeout = WAIT_TIMEOUT):
        self.wait_by_id(elem_id, timeout = timeout)
        select = Select(self._driver.find_element(By.ID, elem_id))
        select.select_by_visible_text(option)
    
    def reset_advanced_search(self):
        uri = self._site_url + self._adv_search_uri 
        self._driver.get(uri) 
        # TODO: Wait for page to load
    
    def advanced_search(self, make_model):
        self.reset_make()
        self.select_make(make_model['make'])
        self.select_model(make_model['model'])
        self.wait_and_click_by_id('btnAdvancedSearch')
        # TODO: Wait for page to load
   
    def reset_make(self, timeout = WAIT_TIMEOUT):
        self.wait_and_select_option_by_id('make', self.RESET_MAKE_TEXT)
        if self._max_models is None:
            print('First call to method reset_make() is dwelling to allow models options to load')
            time.sleep(5) # Dwell to let the models items update
            model_opts = self.wait_and_get_select_options_by_id('model', timeout = timeout)
            self._max_models = len(model_opts)
            print('Initialized member _max_models to %d' % self._max_models)
        else:
            is_max_models = lambda d : len(Select(d.find_element(By.ID, 'model')).options) == self._max_models
            wait = WebDriverWait(self._driver, timeout = timeout)
            wait.until(is_max_models)
        
    def select_make(self, make: str, timeout = WAIT_TIMEOUT):
        self.wait_and_select_option_by_id('make', make, timeout = timeout)
        if self._max_models is None:
            print('Selected make without first initializing member _max_models; You should call reset_make() first!')
            time.sleep(5)
        else:
            is_not_max_models = lambda d : len(Select(d.find_element(By.ID, 'model')).options) != self._max_models
            wait = WebDriverWait(self._driver, timeout = timeout)
            wait.until(is_not_max_models)
        
    def select_model(self, model, timeout = WAIT_TIMEOUT):
        self.wait_and_select_option_by_id('model', model, timeout = timeout)

    def build_make_model_list(self, makes: List[str], models: List[str], timeout = WAIT_TIMEOUT) -> List[Dict]:
        # Initialize make reset functionality
        self.reset_make()
        make_model = []
        make_opts = set()
        for make in makes:
            tmp = [x.text for x in self.wait_and_get_select_options_by_id('make', timeout = timeout)]
            make_opts.update(filter_options_by_text_match(tmp, make))
        make_opts = list(make_opts)
        for make_opt in make_opts:
            self.reset_make()
            self.select_make(make_opt)
            model_opts = set()
            for model in models:
                tmp = [x.text for x in self.wait_and_get_select_options_by_id('model', timeout = timeout)]
                model_opts.update(filter_options_by_text_match(tmp, model))
            model_opts = list(model_opts)
            for model_opt in model_opts:
                make_model.append({'make': make_opt, 'model': model_opt})
        return make_model
    
    def select_results_per_page(self, num_results_per_page: int = 120, timeout = WAIT_TIMEOUT):
        option = '%d per page' % num_results_per_page
        self.wait_and_select_option_by_id('selectDisplayRows', option, timeout = timeout)
    
    def build_asset_uris_from_make_model(self, make_model, timeout = WAIT_TIMEOUT):
        self.reset_advanced_search()
        self.advanced_search(make_model)
        self.select_results_per_page(self.RESULTS_PER_PAGE) # Use 24 for testing multi page results
        time.sleep(2) # Race on the number of results
        num_results = int(
            self._driver\
                .find_element(By.ID, 'divResultsSectionHeader')\
                .find_element(By.TAG_NAME, 'h5')\
                .text.strip().split()[0]
        )
        # print('Found %d results' % num_results)

        # Find all search URIs
        if num_results > self.RESULTS_PER_PAGE:
            time.sleep(2) # dwell until implementing wait
            page_items = self._driver.find_elements(By.CSS_SELECTOR, '.page-item')
            page_links = [item.find_element(By.TAG_NAME, 'a') for item in page_items]
            results_urls = [self._site_url + link.get_dom_attribute('href') for link in page_links]
        else:
            results_urls = [self._driver.current_url]
        
        # print('List of results URLs:')
        # for url in results_urls:
        #     print('- %s' % url) 
            
        asset_uris = []       
        for results_url in results_urls:
            self._driver.get(results_url)
            time.sleep(2)
            # NOTE: The NAME lnkAssetDetails will find two anchors per asset
            # I'm planning to keep this generic locator for future-proofing
            # Just deduplicate the list for uniqueness of asset URIs using a set
            asset_links = self._driver.find_elements(By.NAME, 'lnkAssetDetails')
            asset_uris.extend(list({link.get_dom_attribute('href') for link in asset_links}))
            # print('asset_uris: %d' % len(asset_uris))
        
        assert len(asset_uris) == num_results, 'Incorrect number of asset URIs collected; results: %d, uris: %d' % (num_results, len(asset_uris))
        # print('Found %d asset URIs' % len(asset_uris))
        # print('List of asset URIs:')
        # for uri in asset_uris:
        #     print('- %s' % uri)
        print('Found %d assets for make/model: %s %s' % (num_results, make_model['make'], make_model['model']))
        return asset_uris

    def get_data_from_asset_uri(self, asset_uri):
        self._driver.get(self._site_url + asset_uri)
        time.sleep(2)
       
        data = {}
        data['SITE_URL'] = self._site_url
        data['ASSET_URI'] = asset_uri
        
        # Current bid dollar value
        self.wait_by_id('currentBid')
        # Strip and split to discard USD suffix
        current_bid_string = self._driver.find_element(By.ID, 'currentBid').text.strip().split()[0]
        # Replace commas and dollar sign
        current_bid_number = float(current_bid_string.replace(',','').replace('$',''))
        # print('Current bid: $%1.2f' % current_bid_number)
        data['CURRENT_BID'] = current_bid_number
        
        # Closing date
        closing_date_string = self._driver\
            .find_element(By.TAG_NAME, 'app-ux-timer')\
            .find_element(By.CSS_SELECTOR, 'p span span')\
            .text.strip()[1:-1] # Remove parenthesis
        # => 'Dec 18, 2024 07:45 AM MST'
        closing_date_string = 'Dec 18, 2024 07:45 AM MST'
        format_string = "%b %d, %Y %I:%M %p %Z"
        # Convert to UTC
        tz_string = closing_date_string.split()[-1]
        is_dst = 'S' in tz_string.upper()
        local = pytz.timezone(tz_string)
        naive_dt = DT.strptime(closing_date_string, format_string)
        # Supply is_dst for robustness during TZ transitions
        aware_dt = local.localize(naive_dt, is_dst = is_dst)
        closing_date_utc = aware_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        # print('Closing date: %s' % closing_date_utc)
        data['CLOSING_DATE_UTC'] = closing_date_utc
        
        # Product location text and map url
        product_location_link = self._driver.find_element(By.ID, 'lnkAssetDetailLocation')
        product_location_text = product_location_link.text.strip()
        product_location_map_url = product_location_link\
            .find_element(By.XPATH, '..')\
            .get_dom_attribute('href')
        # print('Location: %s' % product_location_text)
        # print('Map URL: %s' % product_location_map_url)
        data['LOCATION'] = product_location_text
        data['MAP_URL'] = product_location_map_url
        
        # Extract data from table
        rows = self._driver.find_elements(By.CSS_SELECTOR, 'div.row.description-body')
        for row in rows:
            try:
                key = row.find_element(By.CSS_SELECTOR, 'div h5').text.strip()
            except: # TODO: Make this restrictive
                continue
            if key is None:
                continue
            key = key.replace(':', '').replace(' ', '_').upper()
            value = row.find_element(By.CSS_SELECTOR, 'div p').text.strip()
            data[key] = value
        # for k, v in data.items():
        #     print("data[%s] = %s" % (k, v))
        return data
    
        
def filter_options_by_text_match(options: List[str], text: str, strategy: str = 'contains') -> List[WebElement]:
    match strategy:
        case 'contains':
            return [opt for opt in options if text.lower() in opt.lower()]
        case 'startswith':
            return [opt for opt in options if opt.lower().startswith(text.lower())]
        case 'equals':
            return [opt for opt in options if opt.lower() == text.lower()]

if __name__ == '__main__':
    
    with Display():
        
        # Initialize site to advanced search page
        site = SiteHelper(SITE_URL)
        site.reset_advanced_search()
        
        # Build matrix of make/model to search
        make_model = site.build_make_model_list(MAKES, MODELS)
        # make_model = [ # Use this for development testing
        #     {'make': 'Ford',
        #      'model': 'Taurus'},
        # ]
        
        # Print out make/model combinations
        print('Found the following make/model combinations to search:')
        for mm in make_model:
            print('- %s/%s' % (mm['make'], mm['model']) )
        
        # Build a list of asset URIs for the list of makes/models
        asset_uris = set()
        for mm in make_model:
            asset_uris.update(site.build_asset_uris_from_make_model(mm))
        asset_uris = list(asset_uris)
        print("Total number of URIs found: %d" % len(asset_uris))
        
        # Load previous data and make list of URIs
        prev_data = []
        with open(DATA_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile,
                                    quotechar = '"',
                                    quoting = csv.QUOTE_MINIMAL)
            for row in reader:
                prev_data.append(row)
        prev_asset_uris = []
        for el in prev_data:
            prev_asset_uris.append(el['ASSET_URI'])

        # Filter out new URIs that are exclusive of previous URIs
        asset_uris = list(set(asset_uris) - set(prev_asset_uris))
        print('Exclusive URIs to be updated: %d' % len(asset_uris))

        new_data = []
        for asset_uri in asset_uris:
            print('Appending data for asset URI \'%s\'' % asset_uri)
            new_data.append(site.get_data_from_asset_uri(asset_uri))

        data = prev_data + new_data
        
        # Remap list of dict into dict of list
        # out = {}
        # for el in data:
        #     for k, v in el.items():
        #         if k not in out.keys():
        #             out[k] = []
        #         out[k].append(v)
        # print(out)
        fieldnames = list(prev_data[0].keys())
        new_keys = set()
        for el in new_data:
            new_keys.update(el.keys())
        for k in new_keys:
            if k not in fieldnames:
                print('Adding key \'%s\' to fieldnames' % k)
                fieldnames.append(k)
        
        with open(DATA_FILE, 'w') as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames = fieldnames,
                                    quotechar = '"',
                                    quoting = csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(data)
        
        
        time.sleep(10)
        
        site.quit()