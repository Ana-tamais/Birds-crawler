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
    It works with the following approach: It gets a initial link and gather all species id (10001 ~ 12000). 
    Then it generates a link which contains a json with all information we need (.jpg links on s3 amazon,
    number of photos from each specie and the specie's name. The .jpg links for each specie will gonna be
    exported by a .txt on the format ['link', id] with a lot of links. This information is going to be catched
    by the go program and saved on the local memory.
    
    """
    
    def __init__(self, store_path = '',
                 initial_link = 'https://www.wikiaves.com.br/especies.php?t=t',
                 firefox_path = 'geckodriver'):
        """
        attributes:
        
        specie: dictionary which has the following format {id: specie name}
        count_photo: dictionary which has the following format {id: count of the number of photos from this specie}
        path: path where all the data is going to be stored
        browser: we are going to use it to navigate on internet
        soup: use this to work with html code and gather page's information (the number of birds species)
        num_species: number of birds species (1890 on 10/02/2020)
        firefox_path: where geckodriver is stored
        my_filename: name of the .txt which contains all .jpg links from one specie
        file_photo: dictionary which has the following format {id: open(some_path, 'w')}
        r: used to get the json from the page and work with it to get the information we need (.jpg links,
                                                                                               count of photos
                                                                                               and specie's name)
        pag: count the page's number from the link where the json is stored
        count: iterate the number of the .jpg link we are saving
        """
        
        self.specie = {}
        self.count_photo = {}
        self.path = store_path
        self.browser = None
        self.soup = None
        self.num_species = None
        self.firefox_path = firefox_path
        self.initial_link = initial_link
        self.my_filename = {}
        self.file_photo = {}
        self.r = {}
        self.pag = {}
        self.count = {}
        
    def connect_to_internet(self):
        """
        It uses selenium to connect to internet
        """
        firefox_profile = webdriver.FirefoxProfile()
        options = Options()
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(firefox_profile=firefox_profile,
                                         options=options,
                                         executable_path=self.firefox_path)
    def get_num_species(self):
        """
        Get the number of birds species (1890 on 10/02/2020)
        """
        self.browser.get(self.initial_link)
        html = self.browser.page_source
        self.soup = BeautifulSoup(html, 'html.parser')
        self.num_species = self.soup.find_all(class_ = 'font-blue-soft')[-1].text[:4]
        self.num_species = int(self.num_species)
            
    def create_dir_linksimage(self):
        """
        It creates the path where we are going to store the .jpg links
        """
        try:
            os.mkdir(self.path + '/links_image')
        except:
            print('/links_image already exist')

    
    def get_id(self):
        """
        It creates the id for 1890 species based on the site's id (10001 until 11890)
        """
        for k in range(1, self.num_species+1):
            self.count_photo['{}'.format(10000 + k)] = None
            self.specie['{}'.format(10000 + k)] = None
            
    def create_dependencies(self, id_):
        """
        Create some dependent variables to not have the concurrency problem in the threads
        """
        self.my_filename['{}'.format(id_)] = os.path.join(self.path + '/links_image/links_{}.txt'.format(id_))
        self.file_photo['{}'.format(id_)] = open(self.path + '/links_image/links_{}.txt'.format(id_), 'w')
        self.r['{}'.format(id_)] = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p=1'.format(id_))
        try:
            self.r['{}'.format(id_)] = self.r['{}'.format(id_)].json()
        except ValueError:
            print("No json, id = ", id_)
    
    def count_photo_and_specie(self, id_):
        """
        It gets the number of photos and the specie's name
        """
        try:
            self.count_photo['{}'.format(id_)] = self.r['{}'.format(id_)]['registros']['total']
            self.specie['{}'.format(id_)] = self.r['{}'.format(id_)]['registros']['itens']['1']['sp']['idwiki']
        except:
            print("no image, id = ", id_)
            
    def get_json(self, id_):
        """
        It does a request to the page we want to get the json and 
        set count to 1 because we are starting a new page
        """
        self.r['{}'.format(id_)] = requests.get('https://www.wikiaves.com.br/getRegistrosJSON.php?tm=f&t=s&s={}&o=mp&o=mp&p={}'.format(id_, str(self.pag['{}'.format(id_)])))
        self.r['{}'.format(id_)] = self.r['{}'.format(id_)].json()
        self.count['{}'.format(id_)] = 1
    
    def get_image_links(self, id_):
        """
        It uses the previous functions (create_dependencies, count_photo_and_specie) to start getting the .jpg 
        links. Then iterate for all json pages to get all .jpg links from an specie, and save it on a .txt file
        with the following format: ['.jpg link', id]
        """
        self.create_dependencies(id_)
        self.count_photo_and_specie(id_)
        self.pag['{}'.format(id_)] = 1
        try:
            while self.r['{}'.format(id_)]['registros']['itens'] != {}:
                self.get_json(id_)
                while self.count['{}'.format(id_)] < 22:
                    try:
                        self.file_photo['{}'.format(id_)].write("['" + self.r['{}'.format(id_)]['registros']['itens']['{}'.format(str(self.count['{}'.format(id_)]))]['link'].replace('#', 'q') + "'" + ', {}]'.format(id_) + '\n')
                    except KeyboardInterrupt:
                        print('KeyboardInterrupt')
                        break
                    except requests.exceptions.ConnectionError:
                        print('Timeout, id = ', id_)
                    except:
                        break
                    self.count['{}'.format(id_)] += 1
                self.pag['{}'.format(id_)] += 1
            self.file_photo['{}'.format(id_)].close()
        except requests.exceptions.ConnectionError:
            print('Timeout, id = ', id_)
        except:
            print("No json, id = ", id_)
            
    def get_all_links(self, ids):
        """
        It gets all .jpg links from a list of species and does it sequentially
        """
        for id_ in ids:
            self.get_image_links(id_)
        
    def crawl(self, species):
        """
        Crawl function is our main function. It is where all the previous functions are used to extract all
        the .jpg links from api
        """
        inicio = time.time()
        self.connect_to_internet()
        self.get_num_species()
        self.create_dir_linksimage()
        self.get_id()
        self.get_all_links(species)
        self.browser.close()
        fim = time.time()
        print(fim-inicio)



def use_thread(ids, store_path, count, num_threads):
    count = int(count)
    num_threads = int(num_threads)
    inicio = time.time()
    classes = {}
    ids_species = []
    for id_ in range(int(ids[0]), int(ids[0]) + count):
        ids_species.append(str(id_))

    threads = []
    for id_ in range(0, len(ids_species), num_threads):
        classes['{}'.format(id_)] = BirdCrawler(store_path = store_path)
        threads.append(threading.Thread(target=classes['{}'.format(id_)].get_all_links, 
                                        args = ([str(int(ids_species[id_]) + k) for k in range(num_threads)]
                                                ,)))
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
    
    

