from birds_crawler import * 
import argparse

parser = argparse.ArgumentParser(description= 'crawl all photos or sounds from a bird specie on wikiaves.com.br')
parser.add_argument('--id', type=str,
                    help='set id to crawl')
parser.add_argument('--dir', type=str,
                    help='set directory path to save image/audio')
args = parser.parse_args()

classe = BirdCrawler(store_path = args.dir)
classe.crawl([args.id])
classe.save_all_photos([args.id])