from birds_crawler import * 
import argparse

parser = argparse.ArgumentParser(description= 'crawl all photos or sounds from a bird specie on wikiaves.com.br')
parser.add_argument('--specie', type=str,
                    help='a bird specie to crawl')
args = parser.parse_args()

classe = BirdCrawler(store_path = '/home/aninha/Documents/Birds_Project', photo = False)
classe.crawl([args.specie])