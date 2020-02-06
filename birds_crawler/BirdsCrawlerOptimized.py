import os
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
from selenium.webdriver.firefox.options import Options
import requests
import time

class BirdCrawler:
    def __init__(self, store_path = '',
                 initial_link = 'https://www.wikiaves.com.br/especies.php?t=t',
                 photo = True,
                 firefox_path = './geckodriver'):
        
        self.specie = {}
        self.count_photo = {}
        self.count_sound = {}
        self.path = store_path
        self.browser = None
        self.soup = None
        self.photo = photo
        self.num_species = None
        self.firefox_path = firefox_path
        self.initial_link = initial_link
        
    def connect_to_internet(self):
        firefox_profile = webdriver.FirefoxProfile()
        options = Options()
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(firefox_profile=firefox_profile,
                                         options=options,
                                         executable_path=self.firefox_path)
    def get_num_species(self):
        self.browser.get(self.initial_link)
        html = self.browser.page_source
        self.soup = BeautifulSoup(html, 'html.parser')
        self.num_species = self.soup.find_all(class_ = 'font-blue-soft')[-1].text[:4]
        self.num_species = int(self.num_species)

    
    def create_dir_photo(self):
        try:
            os.mkdir(self.path + '/images')
            for specie in range(1, self.num_species + 1):
                os.mkdir(self.path + '/images/id_{}'.format(str(10000 + specie)))
        except:
            print('/images and /images/id_number already exist')
        try:
            os.mkdir(self.path + '/links_image')
        except:
            print('/links_image already exist')
    
    def create_dir_sound(self):
        try:
            os.mkdir(self.path + '/sounds')
            for specie in range(1, self.num_species + 1):
                os.mkdir(self.path + '/sounds/id_{}'.format(str(10000 + specie)))
        except:
            print('/sounds and /sounds/id_number already exist')
        try:
            os.mkdir(self.path + '/links_sound')
        except:
            print('/links_sound already exist')
    
    def create_dir(self):
        if self.photo == True:
            self.create_dir_photo()
        else:
            self.create_dir_sound()
    
    def get_id(self):
        for k in range(1, self.num_species+1):
            self.count_photo['{}'.format(10000 + k)] = None
            self.count_sound['{}'.format(10000 + k)] = None
            self.specie['{}'.format(10000 + k)] = None
    
    def get_image_links(self, id_):
        my_filename = os.path.join('./links_image/links_{}.txt'.format(id_))
        file_photo = open(my_filename, 'w')
        r = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p=1'.format(id_))
        r = r.json()
        self.count_photo['{}'.format(id_)] = r['registros']['total']
        self.specie['{}'.format(id_)] = r['registros']['itens']['1']['sp']['idwiki']
        pag = 1
        while r['registros']['itens'] != {}:
            r = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p={}'.format(id_, str(pag)))
            r = r.json()
            for link in range(1, 21):
                try:
                    file_photo.write(r['registros']['itens']['{}'.format(str(link))]['link'] + '\n')
                except:
                    break
            pag += 1
        file_photo.close()
    
    def get_all_image_links(self, ids):
        for id_ in ids:
            self.get_image_links(id_)
            
    def get_sound_links(self, id_):
        my_filename = os.path.join('./links_sound/links_{}.txt'.format(id_))
        file_sound = open(my_filename, 'w')
        r = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=s&t=s&s={}&o=mp&o=mp&p=1'.format(id_))
        r = r.json()
        self.count_sound['{}'.format(id_)] = r['registros']['total']
        self.specie['{}'.format(id_)] = r['registros']['itens']['1']['sp']['idwiki']
        pag = 1
        while r['registros']['itens'] != {}:
            r = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=s&t=s&s={}&o=mp&o=mp&p={}'.format(id_, str(pag)))
            r = r.json()
            for link in range(1, 21):
                try:
                    file_photo.write(str(r['registros']['itens']['{}'.format(link)]['link'] + '\n'))
                except:
                    break
            pag += 1
        file_sound.close()
        
    def get_all_sound_links(self, ids):
        for id_ in ids:
            self.get_sound_links(id_)
    
    def get_all_links(self, ids):
        if self.photo == True:
            self.get_all_image_links(ids)
        else:
            self.get_all_sound_links(ids)
    
    def save_photo(self, id_):
        my_filename = os.path.join(self.path + '/links_image/links_{}.txt'.format(id_))
        links = open(my_filename, 'r')
        links = links.read()
        links = links.split('\n')[:-1]
        i = 1
        for link in range(len(links)):
            try:
                links[link] = links[link].replace('#', 'q')
                file_ = os.path.join(self.path + '/images/id_{}/'.format(id_) + '{}_{}.jpg'.format(id_, i))               
                urllib.request.urlretrieve(links[link], self.path + '/images/id_{}/'.format(id_) + '{}_{}.jpg'.format(id_, i))
            except:
                print('link not added')
            i += 1
        del links
    
    def save_all_photos(self, ids):
        for id_ in ids:
            inicio = time.time()
            self.save_photo(id_)
            fim = time.time()
            print("Time = ", fim-inicio)
            print("Number of photos = ", self.count_photo['{}'.format(id_)])
        
        
    def crawl(self, species):
        inicio = time.time()
        self.connect_to_internet()
        self.get_num_species()
        self.create_dir()
        self.get_id()
        self.get_all_links(species)
        self.browser.close()
        fim = time.time()
        print(fim-inicio)