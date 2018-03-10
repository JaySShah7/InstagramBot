import praw,re,requests,pprint,importlib,os, time, datetime, urllib.request
from bs4 import BeautifulSoup
from PIL import Image
from InstagramAPI import InstagramAPI
from AuthenticationInfo import *
try:
    import Posts
except:
    pass

import logging
from logging.handlers import RotatingFileHandler
logger=logging.getLogger(__name__)
handler=RotatingFileHandler('InstagramBot.log', maxBytes=100000, backupCount=1)
logger.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def SavePosts(posts):
    file=open('Posts.py', 'w', encoding='utf-8')
    file.write('Posts= '+pprint.pformat(posts)+'\n')
    file.close()


    
def IsImageLink(url):  #checks if url is image, returns image type (png,jpg, jpeg)
    LinkRegex=re.compile('((https:|http:)?\/\/.*\.(png|jpg|jpeg))')
    results=LinkRegex.findall(url)
    if results:
        return results[0][2]
    else:
        return False




def CropToInstagram(filename):
    img=Image.open(filename)
    x,y=img.size
    
    if x/y>16/9: #horizontal
        new_x=y*16/9
        left_x=  x/2 - new_x/2
        right_x=  x/2 + new_x/2

        img=img.crop((left_x, 0, right_x, y))
        #img.show()
        img.save(filename)
        logger.info('Horizontal Image Cropped')

    elif x/y<4/5: #vertical
        new_y=x*5/4
        top_y=  y/2 - new_y/2
        
        bottom_y=  top_y+new_y
        
        img=img.crop((0, top_y, x, bottom_y))
        img.save(filename)
        #img.show()
        logger.info('Vertical Image Cropped')

        



def RedditLogIn():
    rdt=praw.Reddit(username=redditusername, client_id=client_ID, client_secret=secret, user_agent='Test Bot')
    logger.info('Reddit logged in.')
    return rdt




def GetPosts(reddit, max_images=10): #creates image folder, saves images, returns dictionary Posts
    counter=0
    Posts=[]
    subreddit=reddit.subreddit('reddevils')
    for submission in subreddit.top('day', limit=50):
        #if direct image link
        if IsImageLink(submission.url) and counter<max_images:
            img=requests.get(submission.url)
            filename=str(counter)+'.'+IsImageLink(submission.url)
            filename=os.path.join('images', filename)
            imagefile=open(filename, 'wb')
            imagefile.write(img.content)
            imagefile.close()
            logger.info('Image saved: '+filename)
            logger.info(submission.title)
            CropToInstagram(filename)
            Posts.append({'File':filename, 'Title':submission.title}) #dictionary format
            logger.info('Database appended.')
            counter+=1

        #if imgur link
        elif str(submission.url).lower().startswith('https://imgur.com') or str(submission.url).lower().startswith('http://imgur.com') and counter<max_images:
            
            html_page = urllib.request.urlopen(submission.url)
            soup = BeautifulSoup(html_page, 'lxml') 
            images = []
            for img in soup.findAll('img'):
                images.append('https:'+img.get('src'))

            img=requests.get(images[0])
            filename=str(counter)+'.'+images[0][-3:]
            filename=os.path.join('images', filename)
            imagefile=open(filename, 'wb')
            imagefile.write(img.content)
            imagefile.close()
            logger.info('Image saved: '+filename)
            CropToInstagram(filename)
            logger.info(submission.title)

            Posts.append({'File':filename, 'Title':submission.title}) #dictionary format
            logger.info('Database appended.')
            counter+=1

    return Posts



def CreateDatabase():
    reddit=RedditLogIn()
    #delete pre existing images
    
    if not os.path.exists('images'):
        os.makedirs('images')
    for filename in os.listdir('images'):
        filepath = os.path.join('images', filename)
        try:
            os.unlink(filepath)
        except:
            pass
        
    posts=GetPosts(reddit,10)
    SavePosts(posts)

    
    logger.info("Datebase created.")
    try:
        importlib.reload(Posts)
    except:
        import Posts
    logger.info("Datebase reloaded.")




def InstagramBot():
    instagram = InstagramAPI(instagramusername, instagrampassword)
    while True:
        if(instagram.login()):
            logger.info("Logged in to Instagram.")
            try:
                CreateDatabase()
            except Exception as e:
                logger.info('couldnt create Database')
                logger.info(e)
                time.sleep(600)
                continue

            
            starting_time=11   #time to start posts each day
            current_time=datetime.datetime.now().hour
            wait_time= starting_time-current_time
            if wait_time <0:
                wait_time=24+wait_time
            time.sleep(wait_time*60*60)         

            counter=len(Posts.Posts)
            for i in range(0, counter):
                try:
                    #todo: aspect ratio crop
                    instagram.uploadPhoto(Posts.Posts[i]['File'], Posts.Posts[i]['Title'])
                    logger.info('post uploaded!')
                    time.sleep(3600)
                except:
                    logger.error('couldnt upload photo.')
                    pass
                                 
        else:
            logger.error("Couldnt log in to Instagram.")
            time.sleep(900) #try again in 15 min






InstagramBot()
