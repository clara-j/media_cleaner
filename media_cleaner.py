#!/usr/bin/env python3

import urllib.request as request
import json, urllib
import hashlib
import sys
from dateutil.parser import parse
from datetime import datetime,date,timedelta,timezone

# Hash password if not hashed
#if cfg.admin_password_sha1 == '':
#     cfg.admin_password_sha1=hashlib.sha1(cfg.admin_password.encode()).hexdigest()
#auth_key=''
#print('Hash:'+ cfg.admin_password_sha1)

def generate_config():
    server=input("Enter server ip or name: ")
    port=input('Enter port (normally 8096)" ')
    username=input('Enter admin username: ')
    password=input('Enter admin password (password will be hashed in config file): ')
    password_hash=hashlib.sha1(password.encode()).hexdigest()

    server_url='http://'+ server +':'+ port 
    auth_key=get_auth_key(server_url,username, password_hash)

    user_kay=list_users(server_url, auth_key)


    not_played_age="100"

    config_file=''
    config_file += "server_url='http://"+ server +":"+ port +"'\n"
    config_file += "user_key='"+ user_kay +"'\n"
    config_file += "not_played_age="+ not_played_age +"\n"
    config_file += "admin_username='"+ username +"'\n"
    config_file += "admin_password_sha1='"+ password_hash +"'\n"
    config_file += "remove_files=0\n"
    config_file += "video_action='delete'\n"
    config_file += "movie_action='delete'\n"
    config_file += "episode_action='delete'\n"
    config_file += "DEBUG=0\n"

    f = open("media_cleaner_config.py", "w")
    f.write(config_file)
    f.close()
    print('\n\nConfig file created, try running again')
    print('Config file is setup not to delete files, to enable change remove_files to 1')
    print(config_file)

#Delete items
def delete_item(itemID):
    if not bool(cfg.remove_files):
        return

    url=url=cfg.server_url + '/emby/Items/' + itemID + '?api_key='+ auth_key
    if bool(cfg.DEBUG):
        print(url)
    req = request.Request(url,method='DELETE')
    request.urlopen(req)




def get_auth_key(server_url, username, password):
    #Get Auth Token for admin account
    values = {'Username' : username, 'Password': password}
    DATA = urllib.parse.urlencode(values)
    DATA = DATA.encode('ascii')

    print (server_url)

    headers = {'X-Emby-Authorization': 'Emby UserId="'+ username  +'", Client="media_cleaner", Device="media_cleaner", DeviceId="media_cleaner", Version="0.1", Token="'}

    req = request.Request(url=server_url + '/emby/Users/AuthenticateByName', data=DATA,method='POST', headers=headers)

    with request.urlopen(req) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    return(data['AccessToken'])





def list_users(server_url, auth_key):
    #Get all users - DEBUG
    with request.urlopen(server_url +'/emby/Users?api_key=' + auth_key) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
        else:
            print('An error occurred while attempting to retrieve data from the API.')
    i=0
    for user in data:
        print(str(i) +':'+ user['Name'] + ' - ' + user['Id'])
        i += 1

    user_number=input('Enter number for user to track: ')
    userID=data[int(user_number)]['Id']
    return(userID)

def get_items(server_url, user_key, auth_key):
    #Get list of all played items
    url=server_url + '/emby/Users/' + user_key  + '/Items?Recursive=true&IsPlayed=true&api_key=' + auth_key
    if bool(cfg.DEBUG):
        print(url)
    with request.urlopen(url) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
        else:
            print('An error occurred while attempting to retrieve data from the API.')


    #Go through all items and get ones not played in X days
    cut_off_date=datetime.now(timezone.utc) - timedelta(cfg.not_played_age)
    deleteItems=[]

    for item in data['Items']:
        item_details=item['Type'] +' - '+ item['Name'] +' - ' + item['UserData']['LastPlayedDate'] + ' - ' + item['UserData']['Key'] + ' - ' + item['Id']
        if (
                cut_off_date  > parse(item['UserData']['LastPlayedDate']) and ( 
                (item['Type'] == 'Movie' and cfg.movie_action == 'delete') or
                (item['Type'] == 'Episode' and cfg.episode_action == 'delete') or
                (item['Type'] == 'Video' and cfg.video_action == 'delete') )
                ):
            print('Delete - ' + item_details)
            deleteItems.append(item)
        else:
            print('Keep   - ' + item_details)
    return(deleteItems)


def list_items(deleteItems):
    #List items to be deleted
    print('\n\nItems to be deleted')
    for item in deleteItems:
        item_details=item['Name'] + ' - ' + item['UserData']['LastPlayedDate'] + ' - ' + item['UserData']['Key'] + ' - ' + item['Id']
        print('----' + item_details)
        delete_item(item['Id'])


try:
    import media_cleaner_config as cfg
    test=cfg.DEBUG
except (AttributeError, ModuleNotFoundError):
    generate_config()
    exit(0)

auth_key=get_auth_key(cfg.server_url, cfg.admin_username, cfg.admin_password_sha1)
deleteItems=get_items(cfg.server_url, cfg.user_key, auth_key)
list_items(deleteItems)
