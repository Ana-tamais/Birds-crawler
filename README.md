# Birds-crawler

Here we gonna crawl imagens and audios from wikiaves.com.br and use deep learning to classify bird's species

For crawling:

Non-optimized:
  We have a class (BirdCrawler) which requires store_path, photo (photo = True) or audio (photo = False), a list of the species you want to gather information, firefox_path which is the geckodriver's location (I set by default './geckodriver' on .py file because, if you clone this repository, geckodriver will come together) and html (html = True: save a link list to be crawled and export it. Then, you can use 'save_all_information(<species name>)' and it saves all photo or audio on directory
  
  It works with the following approach: It gets a initial link and gather all species names and links to crawl their information (photo or audio). Then it access the link of all the species you want to crawl and scroll down the page until there's no more information to be shown. Then it gets all html and save each information on a directory that it created (if photo, the format is .jpg, if audio, the format is .mp3)

Optimized:

We have a class (BirdCrawler) which requires store_path, photo (photo = True) or audio (photo = False **not working yet**), a list of the species you want to gather information (we recommend you use just 1 specie), firefox_path which is the geckodriver's location (I set by default './geckodriver' on .py file because, if you clone this repository,geckodriver will come together).

  It works with the following approach: It gets a initial link and gather all species names, species id (10001 until ~11890), a count of photos and audios per specie. Then it access the url where all json file (which countain the information we need) are stored and we use it. So we get the image or audio urls and do a request to save this information on the directory


For modeling:

  (Soon)
