import praw,re,requests,pprint,importlib,os, time, datetime, urllib.request,string
from bs4 import BeautifulSoup
from PIL import Image
from InstagramAPI import InstagramAPI
from AuthenticationInfo import *

import logging
from logging.handlers import RotatingFileHandler
logger=logging.getLogger(__name__)
handler=RotatingFileHandler('InstagramBot.log', maxBytes=100000, backupCount=1)
logger.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

try:
    import Posts
except:
    pass
    logger.info("Couldn't initially import Posts.")

try:
    from Hashtags import Hashtags
except:
    Hashtags=[]



def SavePosts(posts):
    try:
        os.unlink('Posts.py')
    except:
        pass
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


def AddHashtags(text, hashtaglist):
    txt=text
    for punct in string.punctuation:
        txt=txt.replace(punct, "")
    txt=txt.lower()

    for i in range(len(hashtaglist)):
        found=False
        for n in range(len(hashtaglist[i]['Keywords'])):
            if hashtaglist[i]['Keywords'][n].lower() in txt:
                found=True
        if found==True:
            text+=" #"+hashtaglist[i]['Hashtag']

    text+=" #MUFC"

    return text
            
                           
                           
        

def MakeCaptions(posts):
    def capital(string):
        string=string[0].upper()+string[1:]
        return string
    
    for i in range(len(posts)):
    
        text=posts[i]['Title']
        
        if text.lower().startswith('i '):
            text='I' + text[1:]
        text= text.replace(' I ', ' a fan')    
        text==text.replace('. a fan ', '. A fan ')
        text==text.replace('! a fan ', '! A fan ')
        
        sentences=text.split('. ')
        sentences=[capital(sentence) for sentence in sentences]
        text='. '.join(sentences)
        

        sentences=text.split('! ')
        sentences=[capital(sentence) for sentence in sentences]
        text='! '.join(sentences)

        
        sentences=text.split('? ')
        sentences=[capital(sentence) for sentence in sentences]
        text='? '.join(sentences)
                
        text=AddHashtags(text, Hashtags)
        
        posts[i]['Title']=text
        
    return posts


def CropToInstagram(filename):
    img=Image.open(filename)
    x,y=img.size
    
    if x/y>16/9: #horizontal
        new_x=y*16/9
        left_x=  x/2 - new_x/2
        right_x=  x/2 + new_x/2

        img=img.crop((left_x, 0, right_x, y))
        #img.show()
        
        logger.info('Horizontal Image Cropped')

    elif x/y<4/5: #vertical
        new_y=x*5/4
        top_y=  y/2 - new_y/2
        
        bottom_y=  top_y+new_y
        
        img=img.crop((0, top_y, x, bottom_y))
        
        #img.show()
        logger.info('Vertical Image Cropped')

    #if filename[-3:]=='png':
    try:
        
        new_name=filename[:-3]+'jpg'
        img=img.convert('RGB')
        os.unlink(filename)
        img.save(new_name)
        filename=new_name
    except Exception as e:
        logger.error(e)

    
    return filename
      

        



def RedditLogIn():
    rdt=praw.Reddit(username=redditusername, client_id=client_ID, client_secret=secret, user_agent='Test Bot')
    logger.info('Reddit logged in.')
    return rdt




def GetPosts(reddit, max_images=10): #creates image folder, saves images, returns dictionary Posts
    counter=0
    minimum_post_score=75
    Posts=[]
    subreddit=reddit.subreddit('reddevils')
    for submission in subreddit.top('day', limit=60):
        #if direct image link
        if submission.score > minimum_post_score:
            if IsImageLink(submission.url) and counter<max_images:
                try:
                    img=requests.get(submission.url)
                    filename=str(counter)+'.'+IsImageLink(submission.url)
                    filename=os.path.join('images', filename)
                    imagefile=open(filename, 'wb')
                    imagefile.write(img.content)
                    imagefile.close()
                    logger.info('Image saved: '+filename)
                    logger.info(submission.title)
                    filename=CropToInstagram(filename)
                    Posts.append({'File':filename, 'Title':submission.title}) #dictionary format
                    logger.info('Database appended.')
                    counter+=1
                except Exception as e:
                    logger.error(e)

            #if imgur link
            elif str(submission.url).lower().startswith('https://imgur.com') or str(submission.url).lower().startswith('http://imgur.com') and counter<max_images:
                try:
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
                    filename=CropToInstagram(filename)
                    logger.info(submission.title)

                    Posts.append({'File':filename, 'Title':submission.title}) #dictionary format
                    logger.info('Database appended.')
                    counter+=1
                except Exception as e:
                    logger.error(e)

    Posts=MakeCaptions(Posts)
    return Posts



def CreateDatabase(number_posts=10):
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
        
    posts=GetPosts(reddit,number_posts)
    SavePosts(posts)

    
    logger.info("Datebase created.")



def InstagramBot(starting_time=11, number_of_posts=12):
    instagram = InstagramAPI(instagramusername, instagrampassword)
    while True:
        if(instagram.isLoggedIn):
            logger.info("Logged in to Instagram.")
            try:
                CreateDatabase(number_of_posts)

                try:
                    importlib.reload(Posts)
                    logger.info("Datebase reloaded.")
                except:
                    import Posts
                    logger.info("Couldnt reload posts. Datebase imported first time.")
                
                starting_time=11   #time to start posts each day 

                counter=len(Posts.Posts)
                for i in range(0, counter):
                    try:
                        
                        instagram.uploadPhoto(Posts.Posts[i]['File'], Posts.Posts[i]['Title'])
                        logger.info('post uploaded!')
                        time.sleep(3600)
                    except Exception as e:
                        logger.error('couldnt upload photo.')
                        logger.error(e)
                        pass
                    
                current_time=datetime.datetime.now().hour
                wait_time= starting_time-current_time
                if wait_time <0:
                    wait_time=24+wait_time
                logger.info('Sleeping {} hours.'.format(str(wait_time)))
                time.sleep(wait_time*60*60)      
            
            except Exception as e:
                logger.error(e)
                time.sleep(900)
                
                continue

            
           
                                 
        else:
            
            logger.warning("Not logged in.")
            try:
                instagram.login()
            except:
                logger.error("Cant log in.")
                time.sleep(900)


#CreateDatabase(12)
InstagramBot(11, 12)
