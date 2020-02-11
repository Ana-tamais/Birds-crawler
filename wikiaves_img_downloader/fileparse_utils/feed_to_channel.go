package fileparse_utils

import (
	"io/ioutil"
	"os"
	"strings"
	"sync"
)

func ListDir(links_path string) []string {
	//returns an array containing the path to all the files on the listed dir
	var links_files []string

	files, _ := ioutil.ReadDir(links_path)
	for _, f := range files {
		links_files = append(links_files, f.Name())
	}
	return links_files
}

func CreateFolderIfNotExists(name string, parent string) {
	//creates a folder if it does not exist
	//it also formats the string name of the link file
	//Despite poor string formatting, it solves the organizing-folder problem
	fname := strings.ReplaceAll(name, "links_", "")
	fname = strings.ReplaceAll(fname, ".txt", "")
	fullpath := parent + "/" + fname
	if _, err := os.Stat(fullpath); os.IsNotExist(err) {
		os.MkdirAll(fullpath, os.ModePerm)
	}

}

func FeedChannel(file_folder string, file_path string, c chan ImgInfo, wg *sync.WaitGroup) {
	// We read the file from the path, generate its corresponding ImgInfo and feed the object to the channel
	arr := ParseFileToArray(file_folder + "/" + file_path)
	for _, info_from_img := range arr {
		c <- info_from_img
	}

	defer wg.Done()
}
