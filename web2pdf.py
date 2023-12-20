import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import numpy as np



def downloadPage(site, chapter):
    '''gets all iamges form web page that are named via only numerical characters
    all photos that have the same width as the majority of photos are combined into one PDF file
    photos are then deleted'''
    # get images from web page, stolen from https://stackoverflow.com/a/46143318/20375434
    response = requests.get(site)
    imgNum = 0
    imageWidths = {} # names of each image as key, width as data

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img['src'] for img in img_tags]

    
    for url in urls:
        filename = re.search(r'/([0-9]+[.](jpg|png))$', url) # regex changed to match only numerical image names to avoid other bullshit on page
        if not filename:
            # print("Regex didn't match with the url: {}".format(url))
            continue
        with open(os.path.join('processing', filename.group(1)), 'wb') as f:
            if 'http' not in url:
                # sometimes an image source can be relative 
                # if it is provide the base url which also happens 
                # to be the site variable atm. 
                url = '{}{}'.format(site, url)
            response = requests.get(url)
            f.write(response.content) 
            try: # added because on chapter 167, there is a reference to a '01.jpg' even though the manga starts on 02
                imageWidths[filename.group(1)] = Image.open(os.path.join('processing', filename.group(1))).width
                imgNum += 1
            except:
                pass


    # combine images into PDF, stolen from https://stackoverflow.com/a/63574364/20375434
    imagelist = []
    im1 = 0 # base for everything else
    
    for key in imageWidths.keys():
        if imageWidths[key] != np.median([x for x in imageWidths.values()]): # filter out images that are different widths, because they are usually extras from third parties
            continue

        image = Image.open(os.path.join('processing', key))
        im = image.convert('RGB')

        if im1 == 0:
            im1 = im
        else:
            imagelist.append(im)

    im1.save(os.path.join('chapters', f'chapter_{chapter}.pdf'), save_all=True, append_images=imagelist, quality=95)

    for key in imageWidths.keys():
        os.remove(os.path.join('processing', key))

def downloadEveryChapter(chapter=1):
    '''enter the chapter you would like to start downloading from
    can't do it for when the URL format is changed for seemingly no reason, like chapter 141'''
    website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-{chapter}/'
    while(200 == requests.head(website).status_code): # true if website exists (and isn't a redirection)
        print(f'downloading chapter: {chapter}')
        if chapter == 141:
            website = 'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-141-end-of-season-2/'
        else:
            website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-{chapter}/'
        downloadPage(website, chapter)
        chapter += 1
        



def main():
    #downloadPage('https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-1/', 1)
    downloadEveryChapter(167) # value is hard coded, just change it here
    print('ALL DONE!')

    # testing stuff
    #response = requests.head('https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-999/')
    #print(response.status_code)

if __name__ == "__main__":
    main()