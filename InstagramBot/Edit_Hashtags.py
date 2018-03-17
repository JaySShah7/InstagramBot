import pprint
from Hashtags import Hashtags
import os
backup=list(Hashtags)
def AddHashtag():
    
    print('Enter hashtag: (case sensitive)')
    ht=input()
    for i in range(len(Hashtags)):
        if Hashtags[i]['Hashtag'].lower()==ht.lower():
            print("Hashtag already exists! Edit hashtag:")
            EditHashtag()
            return
    print("\nEnter keywords. Type 'x' to exit.")
    keywords=[ht.lower()]
    keyword=''
    while keyword!='x':
        keyword=input('Enter keyword:')
        if keyword!='x' and keyword!='':
            keyword=keyword.lower()
            keywords.append(keyword)
    entry={'Hashtag':ht,
                'Keywords':list(set(keywords))}
    pprint.pprint(entry)

    if input("Confirm addition? y/n").lower() == 'y':
        print('Saving..')
        Hashtags.append(entry)

def DeleteHashtag():
    global Hashtags
    
    keyword=input("Which hashtag do you want to delete?").lower()
    for i in range(len(Hashtags)):
        flag=0
        for j in range(len(Hashtags[i]['Keywords'])):
            if keyword in Hashtags[i]['Keywords'][j] and flag==0:
                print("\n")
                pprint.pprint(Hashtags[i])
                if input("Confirm deletion? y/n").lower() == 'y':
                    del Hashtags[i]

                    return
                flag=1
               
def EditHashtag():
    global Hashtags
    
    keyword=input("Which hashtag do you want to edit?").lower()
    for i in range(len(Hashtags)):
        flag=0
        for j in range(len(Hashtags[i]['Keywords'])):
            if keyword in Hashtags[i]['Keywords'][j] and flag==0:
                print("\n")
                pprint.pprint(Hashtags[i])
                if input("Edit hashtag?").lower()=='y':
                    
                    answer=input('1.Edit hashtag\n2.Edit keywords\nAnything else:exit\n\nEnter choice:')
                    if answer=='1':
                        answer=input("Enter new hashtag (case sensitive): ")
                        if(input("Change hashtag from "+Hashtags[i]['Hashtag']+" to "+answer+"?")).lower()=='y':                            
                            
                            Hashtags[i]['Hashtag']=answer
                            Hashtags[i]['Keywords'].append(answer.lower())
                            Hashtags[i]['Keywords']=list(set(Hashtags[i]['Keywords']))
                    elif answer=='2':
                        print("Enter keywords. Type 'x' to exit\n\n")
                        keywords=[Hashtags[i]['Hashtag'].lower()]
                        keyword=''
                        while keyword!='x':
                            keyword=input('Enter keyword:')
                            if keyword!='x' and keyword!='':
                                keyword=keyword.lower()
                                keywords.append(keyword)
                        if(input("Confirm edits?").lower())=='y':
                            Hashtags[i]['Keywords']=keywords
                            Hashtags[i]['Keywords']=list(set(Hashtags[i]['Keywords']))
                           
                    return
                flag=1

def SaveChanges():
    answer=input("Save changes? ")
    if answer.lower().startswith("y"):
        try:
            os.unlink('Hashtags.py')
        except:
            pass
        file=open('Hashtags.py', 'w', encoding='utf-8')
        file.write('Hashtags= '+pprint.pformat(Hashtags)+'\n')
        file.close()
        print("Saved.")

def RapidAdd():
    print("Rapid add mode. 'exit' to exit.")
    while True:
        ht=input("Hashtag:")
        for i in range(len(Hashtags)):
            if Hashtags[i]['Hashtag'].lower()==ht.lower():
                print("Overwriting existing hashtag.")
                
        if ht.lower()=='exit':
            return
        if ht.lower()=='x':
            print("type 'exit' to exit!")
            continue
        if ht=='':
            print("Enter a valid hashtag!:")
            continue
        keywords=[ht.lower()]
        keyword=' '
        while keyword!='x' and keyword!='':
            keyword=input('Enter keyword:')
            if keyword!='x' and keyword!='':
                keyword=keyword.lower()
                keywords.append(keyword)
        Hashtags.append({'Hashtag':ht,
                         'Keywords':list(set(keywords))})
        
        
                    
def MainMenu():
    global Hashtags
    while True:
        print("\n\n\n------HASHTAG EDITOR------\n\n\n")
        print("1.Add Hashtag\n2.Delete Hashtag\n3.Edit Hashtag\n4.Undo all changes\n5.View all hashtags\n'X' for save and exit.\n\n")
        ans=input("Option: ")
        if ans=='1':
            AddHashtag()
        if ans=='2':
            DeleteHashtag()
        if ans=='3':
            EditHashtag()
        if ans=='4':
            Hashtags=list(backup)
        if ans=='5':
            pprint.pprint(Hashtags)
        if ans.lower()=='x':
            SaveChanges()
            return
        if ans.lower().startswith('rapid'):
            RapidAdd()

MainMenu()


pprint.pprint(Hashtags)
    
        
