# Birds-crawler

Here we gonna crawl imagens and audios from wikiaves.com.br and use deep learning to classify bird's species

For crawling:

  We have a class (BirdCrawler) which requires store_path, photo (photo = True) or audio (photo = False) and a list of the species you want to gather information as input;
  
  It works with the following approach: It gets a initial link and gather all species names and links to crawl their information (photo or audio). Then it access the link of all the species you want to crawl and scroll down the page until there's no more information to be shown. Then it gets all html and save each information on a directory that it created (if photo, the format is .jpg, if audio, the format is .mp3)
  
For modeling:

  (Soon)
