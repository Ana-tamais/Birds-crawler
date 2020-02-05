#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
from selenium.webdriver.firefox.options import Options


# In[5]:


class BirdCrawler:
    """
    Class of crawler of wikiaves.com.br. 
    It works with the following approach: It gets a initial link and gather all species names and links to crawl
    their information (photo or audio). Then it access the link of all the species you want to crawl and scroll
    down the page until there's no more information to be shown. Then it gets all html and save each information 
    on a directory that it created (if photo, the format is .jpg, if audio, the format is .mp3)
    
    """
    
    def __init__(self, store_path = '', 
                 initial_link_photo = "https://www.wikiaves.com.br/especies.php?t=t&o=5", 
                 initial_link_sound = "https://www.wikiaves.com.br/especies.php?t=t&o=4",
                 photo = True,
                 html = True):
        """
        inputs:
        store_path, photo (photo = True) or audio (photo = False) and 
        a list of the species you want to gather information
        
        parameters:
        store_path: directory where we store the image/audio files
        initial_link: initial link to start crawling
        bird_link_list_photo: link list with each specie to gather photos
        bird_link_list_sound: link list with each specie to gather audios
        species_list = list with each specie name
        num_photo: list with the number of photos for each specie
        num_sound: list with the number of audios for each specie
        photo (boolean): if True, crawl photo, if False, crawl audio

        """
        self.bird_link_list_photo = [] 
        self.bird_link_list_sound = []
        self.species_list = []
        self.path = store_path
        if photo == True:
            self.initial_link = initial_link_photo
        else:
            self.initial_link = initial_link_sound
        self.num_photo = []
        self.num_sound = []
        self.browser = None
        self.soup = None
        self.photo = photo
        self.html = html
        
    def connect_to_internet(self):
        """
        It uses selenium to connect to internet
        """
        firefox_profile = webdriver.FirefoxProfile()
        options = Options()
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(firefox_profile = firefox_profile, options = options)
    
    def get_list_link_num(self):
        """
        It gets the list of links to be accessed and the number of information for each specie
        """
        for especie in self.soup.find_all(class_="font-blue"):
            if especie.get('href') is not None and ("https://www.wikiaves.com.br/" + especie.get('href'))[42] == "f":
                self.bird_link_list_photo.append("https://www.wikiaves.com.br/" + especie.get('href'))
                self.num_photo.append(especie.text)
            elif especie.get('href') is not None and ("https://www.wikiaves.com.br/" + especie.get('href'))[42] == "s":
                self.bird_link_list_sound.append("https://www.wikiaves.com.br/" + especie.get('href'))
                self.num_sound.append(especie.text)

            
    def get_species(self):
        """
        It gets a list to store the species names
        """
        for especie in self.soup.find_all(class_="font-green-dark"):
            if especie.text not in self.species_list:
                self.species_list.append(especie.text)
        
    def get_information(self):
        """
        It runs the function get_list_link_num and get_species to get all information we need from the initial_link
        """
        self.browser.get(self.initial_link)
        html = self.browser.page_source
        self.soup = BeautifulSoup(html, "html.parser")
        self.get_list_link_num()
        self.get_species()
        
    def create_dir(self):
        """
        Create the directories to store sound or image
        """
        if self.photo == True:
            try:
                os.mkdir(self.path + "/images")
                for especie in self.species_list:
                    os.mkdir(self.path + "/images/{}".format(especie))
            except:
                a = 'a'
            if self.html == True:
                try:
                    os.mkdir(self.path + '/links_image')
                except:
                    a = 'a'
        elif self.photo == False:
            try:
                os.mkdir(self.path + '/sounds')
                for especie in self.species_list:
                    os.mkdir(self.path + "/sounds/{}".format(especie))
            except:
                a = 'a'
            if self.html == True:
                try:
                    os.mkdir(self.path + '/links_sound') 
                except:
                    a = 'a'
    
    def export_links_to_txt(self):
        """
        Export all links which will be accessed to a .txt
        """
        if self.photo == True:
            file_photo = open(self.path + "/links_image.txt", "w")
            for k in range(len(self.bird_link_list_photo)):
                file_photo.write(self.bird_link_list_photo[k] + "\n")
        else:
            file_sound = open("links_sound.txt", "w")
            for k in range(len(self.bird_link_list_sound)):
                file_sound.write(self.bird_link_list_sound[k] + "\n")
    
    def import_links_from_txt(self):
        """
        It imports .txt file which stores all links that will be accessed
        """
        if self.photo == True:
            links_photo = open(self.path +"/links_photo.txt", "r")
            links_photo = links_photo.read()
            links_photo = links_photo.split("\n")[:-1]
            return links_photo
        else:
            links_sound = open(self.path + "/links_sound.txt", "r")
            links_sound = links_sound.read()
            links_sound = links_sound.split("\n")[:-1]
            return links_sound
        
        
    def crawl_one_photo_link(self, especie):
        """
        It crawls only 1 link, exactly the one you instantiated with "especie"
        """
        list_links = self.import_links_from_txt()
        for k in range(len(self.species_list)):
            if self.species_list[k] in especie:
                self.browser.get(list_links[k])
                i = 0
                for j in range(1000000):
                    if j % 10 == 0:
                        html = self.browser.page_source
                        self.soup = BeautifulSoup(html, 'html.parser')
                        imagens = self.soup.find_all(class_ = "img-responsive")
                        del html
                        self.soup = None
                    if len(imagens) >= int(self.num_photo[k]):
                        break
                    if j % 100 == 0:
                        print(j, "iterations")
                    self.browser.execute_script("window.scrollTo(0, {})".format(2000 + i))
                    i += 2000
                if self.html == True:
                    self.save_links_image(self.browser, especie)
                self.save_images(self.browser, especie)
    
    def crawl_one_audio_link(self, especie):
        """
        It crawls only 1 link, exactly the one you instantiated with "especie"
        """
        list_links = self.import_links_from_txt()
        for k in range(len(self.species_list)):
            if self.species_list[k] == especie:
                self.browser.get(list_links[k])
                i = 0
                for j in range(1000000):
                    if j % 100 == 0:
                        html = self.browser.page_source
                        self.soup = BeautifulSoup(html, 'html.parser')
                        sounds = self.soup.find_all(class_ = 'mejs-container svg wikiaves-player progression-single progression-skin progression-minimal-dark progression-audio-player mejs-audio')
                        del html
                        self.soup = None
                    if len(sounds) >= int(self.num_sound[k]):
                        break
                    if j % 100 == 0:
                        print(j, "iterations")
                    self.browser.execute_script("window.scrollTo(0, {})".format(2000 + i))
                    i += 2000
                if self.html == True:
                    self.save_links_sound(self.browser, especie)
                self.save_sounds(self.browser, especie)
    
    def save_sounds(self, browser, especie):
        """
        After scroll down all the page on crawl_one_audio_link, it saves the html and save all audios on
        the directory
        """
        if self.html == False:
            html = browser.page_source
            self.soup = BeautifulSoup(html, 'html.parser')
            sounds = self.soup.find_all(class_ = 'mejs-container svg wikiaves-player progression-single progression-skin progression-minimal-dark progression-audio-player mejs-audio')
            i = 1
            for sound in range(len(sounds)):
                try:
                    save = sounds[sound]['src']
                    my_filename = os.path.join(self.path + "/sounds/{}/".format(especie) + "{}{}.mp3".format(especie, i))
                    with open(my_filename, 'w') as handle:
                        print(file=handle)
                    urllib.request.urlretrieve(save, self.path + '/sounds/{}/'.format(especie) + '{}{}.mp3'.format(especie, i)) 
                    i += 1
                except:
                    a = 'a'
            del html
            self.soup = None
            del sounds
            
    def save_information(self, especie):
        if self.photo == True:
            my_filename = os.path.join(self.path + "/links_image/links_{}.txt".format(especie))
            links = open(my_filename, "r")
            links = links.read()
            links = links.split('\n')[:-1]
            i = 1
            for link in range(len(links)):
                try:
                    file_ = os.path.join(self.path + "/images/{}/".format(especie) + "{}{}.jpg".format(especie, i))
                    with open(file_, 'w') as handle:
                        print(file=handle)
                    urllib.request.urlretrieve(links[link], self.path + '/images/{}/'.format(especie) + '{}{}.jpg'.format(especie, i))
                    i += 1
                except:
                    a = 'a'
            del links
        else:
            my_filename = os.path.join(self.path + "/links_sound/links_{}.txt".format(especie))
            links = open(my_filename, "r")
            links = links.read()
            links = links.split('\n')[:-1]
            i = 1
            for link in range(len(links)):
                try:
                    file_ = os.path.join(self.path + "/sounds/{}/".format(especie) + "{}{}.mp3".format(especie, i))
                    with open(file_, 'w') as handle:
                        print(file=handle)
                    urllib.request.urlretrieve(links[link], self.path + '/sounds/{}/'.format(especie) + '{}{}.mp3'.format(especie, i))
                    i += 1
                except:
                    a = 'a'
            del links

    def save_images(self, browser, especie):
        """
        After scroll down all the page on crawl_one_photo_link, it saves the html and save all photos on
        the directory
        """
        if self.html == False:
            html = browser.page_source
            self.soup = BeautifulSoup(html, 'html.parser')
            imagens = self.soup.find_all(class_ = 'img-responsive')
            for imagem in range(len(imagens)):
                save = imagens[imagem]['src']
                my_filename = os.path.join(self.path + "/images/{}/".format(especie) + '{}{}.jpg'.format(especie, imagem))
                with open(my_filename, "w")as handle:
                    print(file=handle)
                urllib.request.urlretrieve(save, self.path + "/images/{}/".format(especie) + '{}{}.jpg'.format(especie, imagem))
            del html
            self.soup = None
            del imagens            
    
    def save_links_image(self, browser, especie):
        """
        Save and export image or audio links to be saved before on directory
        """
        html = browser.page_source
        self.soup = BeautifulSoup(html, 'html.parser')
        links = self.soup.find_all(class_= 'img-responsive')
        my_filename = os.path.join(self.path + "/links_image/links_{}.txt".format(especie))
        with open(my_filename, "w") as handle:
            for link in range(len(links)):                
                save = (links[link]['src'] + "\n")
                handle.write(save)
                
    def save_links_sound(self, browser, especie):
        html = browser.page_source
        self.soup = BeautifulSoup(html, 'html.parser')
        links = self.soup.find_all(class_ = 'mejs-container svg wikiaves-player progression-single progression-skin progression-minimal-dark progression-audio-player mejs-audio')
        my_filename = os.path.join(self.path + "/links_sound/links_{}.txt".format(especie))
        with open(my_filename, 'w') as handle:
            for link in range(len(links)):
                try:
                    save = (links[link]['src'] + '\n')
                    handle.write(save)
                except:
                    a = 'a'
    
    def crawl_lots_of_photo_links(self, especies):
        """
        It uses the function crawl_one_photo_link to crawl all the species from the input list
        """
        for especie in especies:
            self.crawl_one_photo_link(especie)
        
    def crawl_lots_of_sound_links(self, especies):
        """
        It uses the function crawl_one_audio_link to crawl all the species from the input list
        """
        for especie in especies:
            self.crawl_one_audio_link(especie)
    
    def save_all_information(self, especies):
        for especie in especies:
            self.save_information(especie)
    
    def crawl(self, especies):
        """
        It uses all the previous function to execute our crawl
        """
        print("Starting program...")
        self.connect_to_internet()
        print("Connected to internet!")
        self.get_information()
        print("All information were collected!")
        self.create_dir()
        print("All directories were created")
        self.export_links_to_txt()
        print("Exported links to txt!")
        if self.photo == True:
            self.crawl_lots_of_photo_links(especies)
            print("All photos were crawled")
        else:
            self.crawl_lots_of_sound_links(especies)
            print("All sounds were crawled")
        self.browser.close()
    
    
    
    


# In[6]:


#classe = BirdCrawler(store_path = '/home/aninha/Documents/Birds_Project', photo = False)


# In[8]:


#classe.crawl(["urumutum"])
#classe.save_all_information(['urumutum'])


# In[ ]:




