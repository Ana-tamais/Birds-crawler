package images_downloader

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"wikiaves_img_downloader/fileparse_utils"
)

func DownloadFile(c chan fileparse_utils.ImgInfo, wg *sync.WaitGroup, folder string) {

	// Download the data by popping ImgInfo objects from the channel
	defer wg.Done()
	for len(c) > 0 {
		//extract and separe the img info from the channel
		info := <-c
		url := info.Link
		id := info.Id

		//Just get from the channel, generate url, do the request, write the file and close it all to avoid unix complications
		resp, _ := http.Get(url)

		path := folder + "/" + id + "/" + info.GetFilename()
		path = strings.ReplaceAll(path, " ", "")
		// Create the file
		out, _ := os.Create(path)

		// Write the body to file
		_, _ = io.Copy(out, resp.Body)
		resp.Body.Close()
		out.Close()
		fmt.Println(path)
	}
}
