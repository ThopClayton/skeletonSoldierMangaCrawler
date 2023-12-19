import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os



def downloadPage(site, chapter):
    # get images from web page, stolen from https://stackoverflow.com/a/46143318/20375434
    response = requests.get(site)
    imgNum = 0

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img['src'] for img in img_tags]

    
    for url in urls:
        filename = re.search(r'/([0-9]+[.](jpg|gif|png))$', url) # regex changed to match only numerical image names to avoid other bullshit on page
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
            imgNum += 1


    # combine images into PDF, stolen from https://stackoverflow.com/a/63574364/20375434
    imagelist = []
    im1 = Image.open(os.path.join('processing', '2.jpg')).convert('RGB') # base for everything else. 1.jpg not part of manga for all chapters but the first, oh well.
    for i in range(3, imgNum): # don't care about imgNum.jpg because it appears to be a note by the translator
        image = Image.open(os.path.join('processing', f'{i}.jpg'))
        im = image.convert('RGB')
        imagelist.append(im)

    im1.save(os.path.join('chapters', f'chapter_{chapter}.pdf'), save_all=True, append_images=imagelist, quality=95)
    #os.system('rm *.jpg')
    for i in range(1, imgNum+1):
        os.remove(os.path.join('processing', f'{i}.jpg'))

def downloadEveryChapter():
    chapter = 1
    website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-{chapter}/'
    while(200 == requests.head(website).status_code): # true if website exists (and isn't a redirection)
        website = f'https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-{chapter}/'
        downloadPage(website, chapter)
        chapter += 1
        



def main():
    #downloadPage('https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-1/', 1)
    downloadEveryChapter()
    print('ALL DONE!')

    # testing stuff
    #response = requests.head('https://skeleton-soldier.online/manga/skeleton-soldier-couldnt-protect-the-dungeon-chapter-1-999/')
    #print(response.status_code)

if __name__ == "__main__":
    main()