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

def get_url():
    return(input('Enter server ip or name: '))

def get_port():
    return(input('Enter port (normally 8096): '))

def get_admin_username():
    return(input('Enter admin username: '))

def get_admin_password():
    password=input('Enter admin password (plain text password used to grab access token; password will not be stored): ')
    return(password)

def generate_config():
    server=get_url()
    port=get_port()
    username=get_admin_username()
    password=get_admin_password()

    server_url='http://'+ server +':'+ port
    auth_key=get_auth_key(server_url,username, password)

    user_key=list_users(server_url, auth_key)

    not_played_age_movie="100"
    not_played_age_episode="100"
    not_played_age_video="100"
    not_played_age_trailer="100"

    config_file=''
    config_file += "server_url='http://"+ server +":"+ port +"'\n"
    config_file += "admin_username='"+ username +"'\n"
    config_file += "access_token='"+ auth_key +"'\n"
    config_file += "user_key='"+ user_key +"'\n"
    config_file += "DEBUG=0\n"
#    config_file += "#----------------------------------------------------------#\n"
#    config_file += "#-1=Disable deleting for media type (movie, episode, video, trailer)#\n"
#    config_file += "# 0-365000=Delete media type once it has been watched x days ago#\n"
#    config_file += "#100=default#\n"
    config_file += "not_played_age_movie="+ not_played_age_movie +"\n"
    config_file += "not_played_age_episode="+ not_played_age_episode +"\n"
    config_file += "not_played_age_video="+ not_played_age_video +"\n"
    config_file += "not_played_age_trailer="+ not_played_age_trailer +"\n"
#    config_file += "#----------------------------------------------------------#\n"
#    config_file += "#----------------------------------------------------------#\n"
#    config_file += "#0=Disable deleting ALL media types#\n"
#    config_file += "#1=Enable deleteing ALL media types once past 'not_played_age_*' days ago#\n"
#    config_file += "#0=default#\n"
    config_file += "remove_files=0\n"
#    config_file += "#----------------------------------------------------------#\n"
#    config_file += "#----------------------------------------------------------#\n"
#    config_file += "#0=Ok to delete favorite of media type once past not_played_age_* days ago#\n"
#    config_file += "#1=Do no delete favorite of media type#\n"
#    config_file += "#(1=default)#\n"
    config_file += "ignore_favorites_movie=1\n"
    config_file += "ignore_favorites_episode=1\n"
    config_file += "ignore_favorites_video=1\n"
    config_file += "ignore_favorites_trailer=1"
#    config_file += "\n#----------------------------------------------------------#"

    f = open("media_cleaner_config.py", "w")
    f.write(config_file)
    f.close()
    print('\n\n-----------------------------------------------------------')
    print('Config file is not setup to delete files; to enable file delete set remove_files=1')
    print('Config file contents:')
    print('-----------------------------------------------------------')
    print(config_file)
    print('-----------------------------------------------------------')
    print('Config file created, try running again')
    print('-----------------------------------------------------------')


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
    #values = {'Username' : username, 'Password' : password}
    values = {'Username' : username, 'Pw' : password}
    DATA = urllib.parse.urlencode(values)
    DATA = DATA.encode('ascii')

    headers = {'X-Emby-Authorization' : 'Emby UserId="'+ username  +'", Client="media_cleaner", Device="media_cleaner", DeviceId="media_cleaner", Version="0.1", Token=""'}

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


def get_days_since_watched(date_last_played):

    #Get current time
    date_time_now = datetime.utcnow()
    #Keep the year, month, day, hour, minute, and second
    date_time_last_watched = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.0000000+00:00')
    date_time_delta = date_time_now - date_time_last_watched
    s_date_time_delta = str(date_time_delta)
    days_since_watched = s_date_time_delta.split(' day')[0]
    if ':' in days_since_watched:
        days_since_watched ='Watched <1 day ago'
    else:
        days_since_watched = 'Watched ' + days_since_watched + ' days ago'
    return(days_since_watched)


def get_items(server_url, user_key, auth_key):
    #Get list of all played items
    print('-----------------------------------------------------------')
    print('Start...')
    print('Cleaning media for server at: ' + server_url)
    print('-----------------------------------------------------------')
    print('\n')
    print('-----------------------------------------------------------')
    print('Get List Of Watched Media')
    print('-----------------------------------------------------------')
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
    cut_off_date_movie=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_movie)
    cut_off_date_episode=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_episode)
    cut_off_date_video=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_video)
    cut_off_date_trailer=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_trailer)
    deleteItems=[]

    for item in data['Items']:
        if   (
             (cfg.not_played_age_movie >= 0) and
             (cut_off_date_movie > parse(item['UserData']['LastPlayedDate'])) and
             (not bool(cfg.ignore_favorites_movie) or not item['UserData']['IsFavorite']) and
             (item['Type'] == 'Movie')
             ):
            try:
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'MovieID: ' + item['Id']
            except (KeyError):
                print('Error encounter: \n\n' + str(item))
                exit(1)
            print(':*[DELETE] - ' + item_details)
            deleteItems.append(item)
        elif (
             (cfg.not_played_age_episode >= 0) and
             (cut_off_date_episode > parse(item['UserData']['LastPlayedDate'])) and
             (not bool(cfg.ignore_favorites_episode) or not item['UserData']['IsFavorite']) and
             (item['Type'] == 'Episode')
             ):
            try:
                item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'EpisodeID: ' + item['Id']
            except (KeyError):
                print('Error encounter: \n\n' + str(item))
                exit(1)
            print(':*[DELETE] - ' + item_details)
            deleteItems.append(item)
        elif (
             (cfg.not_played_age_video >= 0) and
             (cut_off_date_video > parse(item['UserData']['LastPlayedDate'])) and
             (not bool(cfg.ignore_favorites_video) or not item['UserData']['IsFavorite']) and
             (item['Type'] == 'Video')
             ):
            try:
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'VideoID: ' + item['Id']
            except (KeyError):
                print('Error encounter: \n\n' + str(item))
                exit(1)
            print(':*[DELETE] - ' + item_details)
            deleteItems.append(item)
        elif (
             (cfg.not_played_age_trailer >= 0) and
             (cut_off_date_trailer > parse(item['UserData']['LastPlayedDate'])) and
             (not bool(cfg.ignore_favorites_trailer) or not item['UserData']['IsFavorite']) and
             (item['Type'] == 'Trailer')
             ):
            try:
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'TrailerID: ' + item['Id']
            except (KeyError):
                print('Error encounter: \n\n' + str(item))
                exit(1)
            print(':*[DELETE] - ' + item_details)
            deleteItems.append(item)
        else:
            if   item['Type'] == 'Movie':
                try:
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'MovieID: ' + item['Id']
                except (KeyError):
                    print('Error encounter: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
            elif item['Type'] == 'Episode':
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'EpisodeID: ' + item['Id']
                except (KeyError):
                    print('Error encounter: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
            elif item['Type'] == 'Video':
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate'])  + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'VideoID: ' + item['Id']
                except (KeyError):
                    print('Error encounter: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
            elif item['Type'] == 'Trailer':
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate'])  + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'TrailerID: ' + item['Id']
                except (KeyError):
                    print('Error encounter: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
            else: #item['Type'] == 'Unknown':
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate'])  + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + item['Type'] + 'ID: ' +  item['Id']
                except (KeyError):
                    print('Error encounter: \n\n' + str(item))
                    exit(1)
                print(':[ERROR!!] - ' + item_details)
                print(':[KEEPING] - ' + item_details)
    print('-----------------------------------------------------------')
    return(deleteItems)


def list_items(deleteItems):
    #List items to be deleted
    print ('\n')
    print('-----------------------------------------------------------')
    print('Summary Of Deleted Media:')
    print('-----------------------------------------------------------')
    if len(deleteItems) > 0:
        for item in deleteItems:
            if item['Type'] == 'Movie':
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Episode':
                item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Video':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Trailer':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            else: # item['Type'] == 'Unknown':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            delete_item(item['Id'])
            print('[DELETED] ' + item_details)
    else:
        print('[NO ITEMS TO DELETE]')
    print('-----------------------------------------------------------')
    print('\n')
    print('-----------------------------------------------------------')
    print('Done.')
    print('-----------------------------------------------------------')


try:
    import media_cleaner_config as cfg
    test=cfg.DEBUG

    if (
        not hasattr(cfg, 'ignore_favorites_movie') or
        not hasattr(cfg, 'ignore_favorites_episode') or
        not hasattr(cfg, 'ignore_favorites_video') or
        not hasattr(cfg, 'ignore_favorites_trailer') or
        not hasattr(cfg, 'not_played_age_movie') or
        not hasattr(cfg, 'not_played_age_episode') or
        not hasattr(cfg, 'not_played_age_video') or
        not hasattr(cfg, 'not_played_age_trailer') or
        not hasattr(cfg, 'access_token')
        ):
        if not hasattr(cfg, 'access_token'):
            url=get_url()
            port=get_port()
            server_url='http://'+ url +':'+ port
            setattr(cfg, 'server_url', server_url)
            username=get_admin_username()
            setattr(cfg, 'admin_username', username)
            password=get_admin_password()
            auth_key=get_auth_key(server_url, username, password)

        print('-----------------------------------------------------------')
        print('ATTENTION!!!')
        print('Old or incomplete config in use.')
        print('1) Add the below config options to media_cleaner_config.py.')
        print('Or')
        print('2) Delete media_cleaner_config.py and run this again to create an updated config.')
        print('-----------------------------------------------------------')
        print('Using default value of:')
        print('-----------------------------------------------------------')

        if not hasattr(cfg, 'access_token'):
            print('access_token=\'' + str(auth_key) + '\'')
            setattr(cfg, 'access_token', auth_key)

        if not hasattr(cfg, 'ignore_favorites_movie'):
            print('ignore_favorites_movie=1')
            setattr(cfg, 'ignore_favorites_movie', 1)
        if not hasattr(cfg, 'ignore_favorites_episode'):
            print('ignore_favorites_episode=1')
            setattr(cfg, 'ignore_favorites_episode', 1)
        if not hasattr(cfg, 'ignore_favorites_video'):
            print('ignore_favorites_video=1')
            setattr(cfg, 'ignore_favorites_video', 1)
        if not hasattr(cfg, 'ignore_favorites_trailer'):
            print('ignore_favorites_trailer=1')
            setattr(cfg, 'ignore_favorites_trailer', 1)

        if not hasattr(cfg, 'not_played_age_movie'):
            print('not_played_age_movie=100')
            setattr(cfg, 'not_played_age_movie', 100)
        if not hasattr(cfg, 'not_played_age_episode'):
            print('not_played_age_episode=100')
            setattr(cfg, 'not_played_age_episode', 100)
        if not hasattr(cfg, 'not_played_age_video'):
            print('not_played_age_video=100')
            setattr(cfg, 'not_played_age_video', 100)
        if not hasattr(cfg, 'not_played_age_trailer'):
            print('not_played_age_trailer=100')
            setattr(cfg, 'not_played_age_trailer', 100)
        print('-----------------------------------------------------------')
        print ('\n')

except (AttributeError, ModuleNotFoundError):
    generate_config()
    exit(0)

deleteItems=get_items(cfg.server_url, cfg.user_key, cfg.access_token)
list_items(deleteItems)
