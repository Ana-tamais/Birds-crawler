import os
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
from selenium.webdriver.firefox.options import Options
import requests
import time
import threading
import json

class BirdCrawler:
    """
    Class of crawler of wikiaves.com.br. 
    It works with the following approach: It gets a initial link and gather all species names and links to crawl
    their information (photo or audio). Then it access the link of all the species you want to crawl and scroll
    down the page until there's no more information to be shown. Then it gets all html and save each information 
    on a directory that it created (if photo, the format is .jpg, if audio, the format is .mp3)
    
    """
    
    def __init__(self, store_path = '',
                 initial_link = 'https://www.wikiaves.com.br/especies.php?t=t',
                 photo = True,
                 firefox_path = 'geckodriver'):
        
        self.specie = {}
        self.count_photo = {}
        self.path = store_path
        self.browser = None
        self.soup = None
        self.photo = photo
        self.num_species = None
        self.firefox_path = firefox_path
        self.initial_link = initial_link
        self.my_filename = {}
        self.file_photo = {}
        self.r = {}
        self.pag = {}
        self.count = {}
        
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
    
    def create_dir_images(self):
        try:
            os.mkdir(self.path + '/images')
            for specie in range(1, self.num_species + 1):
                os.mkdir(self.path + '/images/id_{}'.format(str(10000 + specie)))
        except:
            print('/images and /images/id_number already exist')
            
    def create_dir_linksimage(self):
        try:
            os.mkdir(self.path + '/links_image')
        except:
            print('/links_image already exist')

    
    def get_id(self):
        for k in range(1, self.num_species+1):
            self.count_photo['{}'.format(10000 + k)] = None
            self.specie['{}'.format(10000 + k)] = None
            
    def create_dependencies(self, id_):
        self.my_filename['{}'.format(id_)] = os.path.join(self.path + '/links_image/links_{}.txt'.format(id_))
        self.file_photo['{}'.format(id_)] = open(self.path + '/links_image/links_{}.txt'.format(id_), 'w')
        self.r['{}'.format(id_)] = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p=1'.format(id_))
        self.r['{}'.format(id_)] = self.r['{}'.format(id_)].json()
    
    def count_photo_and_specie(self, id_):
        self.count_photo['{}'.format(id_)] = self.r['{}'.format(id_)]['registros']['total']
        try:
            self.specie['{}'.format(id_)] = self.r['{}'.format(id_)]['registros']['itens']['1']['sp']['idwiki']
        except:
            print("no image, id = ", id_)
            
    def get_json(self, id_):
        self.r['{}'.format(id_)] = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p={}'.format(id_, str(self.pag['{}'.format(id_)])))
        self.r['{}'.format(id_)] = self.r['{}'.format(id_)].json()
        self.count['{}'.format(id_)] = 1
    
    def get_image_links(self, id_):
        self.create_dependencies(id_)
        self.count_photo_and_specie(id_)
        self.pag['{}'.format(id_)] = 1
        while self.r['{}'.format(id_)]['registros']['itens'] != {}:
            self.get_json(id_)
            while self.count['{}'.format(id_)] < 22:
                try:
                    self.file_photo['{}'.format(id_)].write("[" + self.r['{}'.format(id_)]['registros']['itens']['{}'.format(str(self.count['{}'.format(id_)]))]['link'].replace('#', 'q') + ', {}]'.format(id_) + '\n')
                except KeyboardInterrupt:
                    print('KeyboardInterrupt')
                    break
                except:
                    break
                self.count['{}'.format(id_)] += 1
            self.pag['{}'.format(id_)] += 1
        self.file_photo['{}'.format(id_)].close()
    
    def get_all_links(self, ids):
        for id_ in ids:
            self.get_image_links(id_)

    
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
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                break
                break
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
        self.create_dir_images()
        self.create_dir_linksimage()
        self.get_id()
        self.get_all_links(species)
        self.browser.close()
        fim = time.time()
        print(fim-inicio)


def use_thread(ids):
    inicio = time.time()
    classes = {}
    ids_species = []
    for id_ in range(int(ids[0]), int(ids[0]) + 316):
        ids_species.append(str(id_))

    threads = []
    for id_ in range(0, len(ids_species)):
        classes['{}'.format(id_)] = BirdCrawler(store_path = '/home/aninha/Documents/Birds_Project')
        threads.append(threading.Thread(target=classes['{}'.format(id_)].get_all_links, args = ([str(ids_species[id_])],)))
    for i in threads:
        try:
            i.start()
        except:
            print(1)
            i.stop()
    for i in threads:
        i.join()
    final = time.time()
    print(final - inicio)
    
    

