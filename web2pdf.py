import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import shutil

# TODO
# format all images to be the same width


def downloadPage(site, chapter):
    '''gets all iamges form web page that are named via only numerical characters
    all photos that have the same width as the majority of photos are combined into one PDF file
    photos are then deleted'''
    # get images from web page, stolen from https://stackoverflow.com/a/46143318/20375434
    response = requests.get(site)
    imgNum = 0
    imageWidths = {} # names of each image as key, width as data
    imageHeights = {}

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img['src'] for img in img_tags]

    
    for url in urls:
        filename = re.search(r'/([0-9]+[.](jpg|png|webp))$', url) # regex changed to match only numerical image names to avoid other bullshit on page
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
                imageHeights[filename.group(1)] = Image.open(os.path.join('processing', filename.group(1))).height
                imgNum += 1
            except:
                pass


    # combine images into PDF, stolen from https://stackoverflow.com/a/63574364/20375434
    imagelist = []
    im1 = 0 # base for everything else
    
    for key in imageWidths.keys():
        # ch 55 randomly changes image widths MULTIPLE TIMES for seemingly no reason. ch 56 then resumes having homogeneous widths
        # since multiple different groups have done the translating, there is no single way to filter out non-manga content despite my efforts 
        #if (imageHeights[key] / imageWidths[key] <= 1.5):
        #    continue

        image = Image.open(os.path.join('processing', key))
        im = image.convert('RGB')

        if im1 == 0:
            im1 = im
        else:
            imagelist.append(im)

    im1.save(os.path.join('chapters', f'chapter_{chapter}.pdf'), save_all=True, append_images=imagelist, quality=95)

    for key in imageWidths.keys():
        os.remove(os.path.join('processing', key))

def getLink4chapter(chapter):
    if chapter == 141: # chapter 141 has its own unique link for some reason...
        website = 'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-141-end-of-season-2/'
    else:
        # looks like they gave up on using a volume, chapter format @ ch. 202 and beyond
        if chapter <= 201:
            website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-{chapter}/'
        else:
            website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-{chapter}/'

    return website

def downloadEveryChapter(chapter=1):
    '''enter the chapter you would like to start downloading from'''
    website = getLink4chapter(chapter)
    webCode = requests.head(website).status_code
    # true if website exists (and isn't a redirection)
    while(webCode == 200):
        print(f'downloading chapter: {chapter}')
        downloadPage(website, chapter)
        chapter += 1
        website = getLink4chapter(chapter)
        webCode = requests.head(website).status_code

    if webCode == 301:
        print(f'code {webCode}: That should mean we have run out of chapters to download!')
    else:
        print(f"code {webCode}: I'm not sure why we would encounter that. Please contact me on discord via 'thop.'")
        



def main():
    for file in os.scandir('processing'):
        os.remove(file)
    while(1):
        inp = input('enter the chapter number you would like to start downloading from.\nclose this window to shut down this program.\n>>>')
        if not inp.isdigit() or int(inp) < 1:
            print("please enter an integer value greater or equal to 1!")
            continue
        inp = int(inp) # done after check to ensure it is actually an integer and not a string cast to int
        downloadEveryChapter(inp) 
        print('ALL DONE!')
        return 0
    # testing stuff
    #response = requests.head('https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-260/')
    #print(response.status_code)

if __name__ == "__main__":
    main()