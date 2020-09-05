#!/usr/bin/env python3

import urllib.request as request
import json, urllib
import traceback
import hashlib
import sys
import os
from dateutil.parser import parse
from datetime import datetime,date,timedelta,timezone

# Hash password if not hashed
#if cfg.admin_password_sha1 == '':
#     cfg.admin_password_sha1=hashlib.sha1(cfg.admin_password.encode()).hexdigest()
#auth_key=''
#print('Hash:'+ cfg.admin_password_sha1)


def retjprint(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def jprint(rawjson):
    #create a formatted string of the python JSON object
    ezjson = retjprint(rawjson)
    print(ezjson)


def get_url():
    return(input('Enter server ip or name: '))


def get_port():
    return(input('Enter port (normally 8096): '))


def get_admin_username():
    return(input('Enter admin username: '))


def get_admin_password():
    password=input('Enter admin password (plain text password used to grab access token; password will not be stored): ')
    return(password)


def get_admin_password_sha1(password):
    #password_sha1=password #input('Enter admin password (password will be hashed in config file): ')
    password_sha1=hashlib.sha1(password.encode()).hexdigest()
    return(password_sha1)


def generate_config():
    server=get_url()
    port=get_port()
    username=get_admin_username()
    password=get_admin_password()
    password_sha1=get_admin_password_sha1(password)

    server_url='http://' + server + ':' + port
    auth_key=get_auth_key(server_url, username, password, password_sha1)

    user_key=list_users(server_url, auth_key)

    not_played_age_movie="100"
    not_played_age_episode="100"
    not_played_age_video="100"
    not_played_age_trailer="100"

    config_file=''
    config_file += "server_url='http://"+ server +":"+ port +"'\n"
    config_file += "admin_username='"+ username +"'\n"
    config_file += "admin_password_sha1='"+ password_sha1 +"'\n"
    config_file += "access_token='"+ auth_key +"'\n"
    config_file += "user_key='"+ user_key +"'\n"
    config_file += "DEBUG=0\n"
    #config_file += "#----------------------------------------------------------#\n"
    #config_file += "#-1=Disable deleting for media type (movie, episode, video, trailer)#\n"
    #config_file += "# 0-365000=Delete media type once it has been watched x days ago#\n"
    #config_file += "#100=default#\n"
    config_file += "not_played_age_movie="+ not_played_age_movie +"\n"
    config_file += "not_played_age_episode="+ not_played_age_episode +"\n"
    config_file += "not_played_age_video="+ not_played_age_video +"\n"
    config_file += "not_played_age_trailer="+ not_played_age_trailer +"\n"
#    config_file += "not_played_age_audio="+ not_played_age_audio +"\n"
#    config_file += "not_played_age_season_folder="+ not_played_age_season_folder +"\n"
#    config_file += "not_played_age_tvchannel="+ not_played_age_tvchannel +"\n"
#    config_file += "not_played_age_program="+ not_played_age_program +"\n"
    #config_file += "#----------------------------------------------------------#\n"
    #config_file += "#----------------------------------------------------------#\n"
    #config_file += "#0=Disable deleting ALL media types#\n"
    #config_file += "#1=Enable deleteing ALL media types once past 'not_played_age_*' days ago#\n"
    #config_file += "#0=default#\n"
    config_file += "remove_files=0\n"
    #config_file += "#----------------------------------------------------------#\n"
    #config_file += "#----------------------------------------------------------#\n"
    #config_file += "#0=Ok to delete favorite of media type once past not_played_age_* days ago#\n"
    #config_file += "#1=Do no delete favorite of media type#\n"
    #config_file += "#(1=default)#\n"
    config_file += "ignore_favorites_movie=1\n"
    config_file += "ignore_favorites_episode=1\n"
    config_file += "ignore_favorites_video=1\n"
    config_file += "ignore_favorites_trailer=1"
#    config_file += "ignore_favorites_audio=1"
#    config_file += "ignore_favorites_season_folder=1"
#    config_file += "ignore_favorites_tvchannel=1"
#    config_file += "ignore_favorites_program=1"
    #config_file += "\n#----------------------------------------------------------#"

    #Create config file next to the script even when cwd is not the same
    cwd = os.getcwd()
    script_dir = os.path.dirname(__file__)
    os.chdir(script_dir)

    f = open("media_cleaner_config.py", "w")
    f.write(config_file)
    f.close()

    os.chdir(cwd)

    print('\n\n-----------------------------------------------------------')
    print('Config file is not setup to delete media')
    print('To delete media set remove_files=1 in media_cleaner_config.py')
    print('-----------------------------------------------------------')
    print('Config file contents:')
    print('-----------------------------------------------------------')
    print(config_file)
    print('-----------------------------------------------------------')
    print('Config file created, try running again')
    print('-----------------------------------------------------------')


#Delete items
def delete_item(itemID):
    #url=url=cfg.server_url + '/emby/Items/' + itemID + '?api_key='+ auth_key
    url=url=cfg.server_url + '/emby/Items/' + itemID + '?api_key='+ cfg.access_token
    req = request.Request(url,method='DELETE')
    if bool(cfg.DEBUG):
        print(itemID)
        print(url)
        print(req)
    if bool(cfg.remove_files):
        try:
            request.urlopen(req)
        except Exception:
            print('generic exception: ' + traceback.format_exc())
    else:
        return


def get_auth_key(server_url, username, password, sha1_password):
    #Get Auth Token for admin account
    #values = {'Username' : username, 'Password' : password_sha1}
    values = {'Username' : username, 'Password' : sha1_password, 'Pw' : password}
    DATA = urllib.parse.urlencode(values)
    DATA = DATA.encode('ascii')

    headers = {'X-Emby-Authorization' : 'Emby UserId="'+ username  +'", Client="media_cleaner", Device="media_cleaner", DeviceId="media_cleaner", Version="0.1", Token=""'}

    req = request.Request(url=server_url + '/emby/Users/AuthenticateByName', data=DATA,method='POST', headers=headers)

    with request.urlopen(req) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)

            #DEBUG
            #jprint(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    return(data['AccessToken'])


def list_users(server_url, auth_key):
    #Get all users - DEBUG
    with request.urlopen(server_url +'/emby/Users?api_key=' + auth_key) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)

            #DEBUG
            #jprint(data)
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
    try:
        date_time_last_watched = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.0000000+00:00')
    except ValueError:
        try:
            date_time_last_watched = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.0000000Z')
        except Exception:
            date_time_last_watched = 'unknown date time format'
    except:
        date_time_last_watched = 'unknown date time format'

    if bool(cfg.DEBUG):
        #DEBUG
        print(date_time_last_watched)

    if not (date_time_last_watched == 'unknown date time format'):
        date_time_delta = date_time_now - date_time_last_watched
        s_date_time_delta = str(date_time_delta)
        days_since_watched = s_date_time_delta.split(' day')[0]
        if ':' in days_since_watched:
            days_since_watched = 'Watched <1 day ago'
        elif days_since_watched == '1':
            days_since_watched = 'Watched ' + days_since_watched + ' day ago'
        else:
            days_since_watched = 'Watched ' + days_since_watched + ' days ago'
    else:
        days_since_watched='0'
    return(days_since_watched)


def get_season_episode(season_number, episode_number):
    season_num = str(season_number)
    season_num = season_num.zfill(2)

    episode_num = str(episode_number)
    episode_num = episode_num.zfill(2)

    season_episode = 's' + season_num + '.e' + episode_num
    return(season_episode)


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
            if bool(cfg.DEBUG):
                #print debug data to file
                cwd = os.getcwd()
                script_dir = os.path.dirname(__file__)
                os.chdir(script_dir)
                f = open("media_cleaner.debug", "w")
                f.write(retjprint(data))
                f.close()
                os.chdir(cwd)
                #print debug data to buffer
                #jprint(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    #Go through all items and get ones not played in X days
    cut_off_date_movie=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_movie)
    cut_off_date_episode=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_episode)
    cut_off_date_video=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_video)
    cut_off_date_trailer=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_trailer)
    deleteItems=[]

    for item in data['Items']:
        if (item['Type'] == 'Movie'):
            if (
               (cfg.not_played_age_movie >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_movie > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.ignore_favorites_movie) or not item['UserData']['IsFavorite'])
               ):
                try:
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'MovieID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Delete Movie: \n\n' + str(item))
                    exit(1)
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'MovieID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Keep Movie: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
        elif (item['Type'] == 'Episode'):
            if (
               (cfg.not_played_age_episode >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_episode > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.ignore_favorites_episode) or not item['UserData']['IsFavorite'])
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'EpisodeID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Delete Episode: \n\n' + str(item))
                    exit(1)
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'EpisodeID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Keep Episode: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
        elif (item['Type'] == 'Video'):
            if (
               (item['Type'] == 'Video') and
               (cfg.not_played_age_video >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_video > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.ignore_favorites_video) or not item['UserData']['IsFavorite'])
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'VideoID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Delete Video: \n\n' + str(item))
                    exit(1)
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate'])  + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'VideoID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Keep Video: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
        elif (item['Type'] == 'Trailer'):
            if (
               (cfg.not_played_age_trailer >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_trailer > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.ignore_favorites_trailer) or not item['UserData']['IsFavorite'])
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'TrailerID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Delete Trailer: \n\n' + str(item))
                    exit(1)
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_watched(item['UserData']['LastPlayedDate'])  + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ' + 'TrailerID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                    print('Error encountered - Keep Trailer: \n\n' + str(item))
                    exit(1)
                print(':[KEEPING] - ' + item_details)
        else: #(item['Type'] == 'Unknown')
            try:
                item_details=item['Type'] + ' - ' + item['Name'] + ' - Favorite: ' + str(item['UserData']['IsFavorite'])  + ' - ID: ' +  item['Id']
            except (KeyError):
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
                print('Error encountered - Keep Unknown: \n\n' + str(item))
                exit(1)
            print(':[KEEPING UNKNOWN MEDIA TYPE] - ' + item_details)

    print('-----------------------------------------------------------')
    return(deleteItems)


def list_delete_items(deleteItems):
    #List items to be deleted
    print ('\n')
    print('-----------------------------------------------------------')
    print('Summary Of Deleted Media:')
    if not bool(cfg.remove_files):
        print('* Trial Run          *')
        print('* remove_files=0     *')
        print('* No Media Deleted   *')
    print('-----------------------------------------------------------')

    if len(deleteItems) > 0:
        for item in deleteItems:
            if item['Type'] == 'Movie':
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Episode':
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + item['Id']
            elif item['Type'] == 'Video':
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Trailer':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            else: # item['Type'] == 'Unknown':
                pass
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
        not hasattr(cfg, 'server_url') or
        not hasattr(cfg, 'admin_username') or
        not hasattr(cfg, 'admin_password_sha1') or
        not hasattr(cfg, 'access_token') or
        not hasattr(cfg, 'user_key') or
        not hasattr(cfg, 'ignore_favorites_movie') or
        not hasattr(cfg, 'ignore_favorites_episode') or
        not hasattr(cfg, 'ignore_favorites_video') or
        not hasattr(cfg, 'ignore_favorites_trailer') or
        not hasattr(cfg, 'remove_files') or
        not hasattr(cfg, 'not_played_age_movie') or
        not hasattr(cfg, 'not_played_age_episode') or
        not hasattr(cfg, 'not_played_age_video') or
        not hasattr(cfg, 'not_played_age_trailer') #or
       ):
        if (
            not hasattr(cfg, 'server_url') or
            not hasattr(cfg, 'admin_username') or
            not hasattr(cfg, 'admin_password_sha1') or
            not hasattr(cfg, 'access_token') or
            not hasattr(cfg, 'user_key')
           ):
                url=get_url()
                port=get_port()
                server_url='http://'+ url +':'+ port
                username=get_admin_username()
                password=get_admin_password()
                password_sha1=get_admin_password_sha1(password)
                auth_key=get_auth_key(server_url, username, password, password_sha1)
                if not hasattr(cfg, 'user_key'):
                    user_key=list_users(server_url, auth_key)

        print('-----------------------------------------------------------')
        print('ATTENTION!!!')
        print('Old or incomplete config in use.')
        print('1) Add the below config values(s) to media_cleaner_config.py.')
        print('Or')
        print('2) Delete media_cleaner_config.py and run this again to create an updated config.')
        print('-----------------------------------------------------------')
        print('Using default config value(s) of:')
        print('-----------------------------------------------------------')

        if not hasattr(cfg, 'server_url'):
            print('server_url=\'' + str(server_url) + '\'')
            setattr(cfg, 'server_url', server_url)
        if not hasattr(cfg, 'admin_username'):
            print('admin_username=\'' + str(username) + '\'')
            setattr(cfg, 'admin_username', username)
        if not hasattr(cfg, 'admin_password_sha1'):
            print('admin_password_sha1=\'' + str(password_sha1) + '\'')
            setattr(cfg, 'admin_password_sha1', password_sha1)
        if not hasattr(cfg, 'access_token'):
            print('access_token=\'' + str(auth_key) + '\'')
            setattr(cfg, 'access_token', auth_key)
        if not hasattr(cfg, 'user_key'):
            print('user_key=\'' + str(user_key) + '\'')
            setattr(cfg, 'user_key', user_key)

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

        if not hasattr(cfg, 'remove_files'):
            print('remove_files=0')
            setattr(cfg, 'remove_files', 0)

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

#auth_key=get_auth_key(cfg.server_url, cfg.admin_username, cfg.admin_password_sha1)
#deleteItems=get_items(cfg.server_url, cfg.user_key, auth_key)
deleteItems=get_items(cfg.server_url, cfg.user_key, cfg.access_token)
list_delete_items(deleteItems)
