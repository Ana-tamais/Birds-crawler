package main

import (
	"fmt"
	"sync"
	"time"
	"wikiaves_img_downloader/fileparse_utils"   //some utils to extract the data from the files
	"wikiaves_img_downloader/images_downloader" //our main download function
)

func main() {
	// SETTING OUR GLOBAL VARIABLES
	// No command line parse arguments due to my lazyness
	c := make(chan fileparse_utils.ImgInfo, 4000000)
	var wg_feed_channel sync.WaitGroup
	LINKS_FOLDER := "images/links_image"
	STORE_FOLDER := "images/downloaded_images"
	ROUTINE_NUMBER := 200 //It is the best in order to avoid crashing
	start_feeding := time.Now()
	for _, filename := range fileparse_utils.ListDir(LINKS_FOLDER) {
		wg_feed_channel.Add(1)
		fileparse_utils.CreateFolderIfNotExists(filename, STORE_FOLDER)
		go fileparse_utils.FeedChannel(LINKS_FOLDER, filename, c, &wg_feed_channel)
		//sequential waits because if anything goes wrong we can start over from a checkpoint
		//btw this was an error but otherwise I would have to treat errors on the whole code and it would never be done
		wg_feed_channel.Wait()
	}
	//Some time seeking
	elapsed_feeding := time.Since(start_feeding)
	fmt.Println("Unpacking took %s", elapsed_feeding)
	fmt.Println(len(c))

	//Just separing stuff for the crawl time
	var wg_download sync.WaitGroup

	//Just create goroutines for concurrent requesting
	start_crawling := time.Now()
	for i := 0; i < ROUTINE_NUMBER; i++ {
		wg_download.Add(1)
		go images_downloader.DownloadFile(c, &wg_download, STORE_FOLDER)

	}

	//After that we wait and print our time metrics
	wg_download.Wait()
	elapsed_crawling := time.Since(start_crawling)
	fmt.Println("Crawling took %s", elapsed_crawling)
}
