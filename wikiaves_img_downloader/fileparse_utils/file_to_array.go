package fileparse_utils

import (
	"bufio"
	"log"
	"os"
	"strings"
)

type ImgInfo struct {
	//object to store the image info
	Link string
	Id   string
}

func ParseFileToArray(path string) []ImgInfo {

	/*
		get all the link-specie_id ImgInfo objects for the text file
		it also does a simple formatting on the strings to remove some characters
	*/

	var arr []ImgInfo

	file, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		txt := scanner.Text()
		split_txt := strings.Split(txt, ",")

		//generate our format-corrected link and specie id
		link := strings.ReplaceAll(split_txt[0], "'", "")
		link = strings.ReplaceAll(link, "[", "")
		id := strings.ReplaceAll(split_txt[1], "]", "")

		arr = append(arr, ImgInfo{Link: link, Id: id})
	}

	return arr
}

func (img_info ImgInfo) GetFilename() string {
	//Crates the file name from the ImgInfo class instance

	id := img_info.Id
	split_txt := strings.Split(img_info.Link, "/")
	return id + "_" + split_txt[len(split_txt)-1]

}
