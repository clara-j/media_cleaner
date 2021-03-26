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


def convert2json(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def print2json(rawjson):
    #create a formatted string of the python JSON object
    ezjson = convert2json(rawjson)
    print(ezjson)


#emby or jellyfin?
def get_brand():
    defaultbrand='emby'
    print('0:emby\n1:jellyfin')
    brand=input('Enter number for server branding (default ' + defaultbrand + '): ')
    if (brand == ''):
        return(defaultbrand)
    elif (brand == '0'):
        return(defaultbrand)
    elif (brand == '1'):
        return('jellyfin')
    else:
        print('Invalid choice. Default to emby.')
        return(defaultbrand)


#ip address or url?
def get_url():
    defaulturl='http://localhost'
    url=input('Enter server ip or name (default ' + defaulturl + '): ')
    if (url == ''):
        return(defaulturl)
    else:
        if (url.find('://',3,7) >= 0):
            return(url)
        else:
           #print('No http:// or https:// entered.')
           url='http://' + url
           print('Assuming server ip or name is: ' + url)
           return(url)


#http or https port?
def get_port():
    defaultport='8096'
    valid_port=False
    while (valid_port == False):
        print('If you have not explicity changed this option, press enter for default.')
        print('Space for no port.')
        port=input('Enter port (default ' + defaultport + '): ')
        if (port == ''):
            valid_port=True
            return(defaultport)
        elif (port == ' '):
            valid_port=True
            return('')
        else:
            try:
                port_float=float(port)
                if ((port_float % 1) == 0):
                    port_int=int(port_float)
                    if ((int(port_int) >= 1) and (int(port_int) <= 65535)):
                        valid_port=True
                        return(str(port_int))
                    else:
                        print('\nInvalid port. Try again.\n')
                else:
                    print('\nInvalid port. Try again.\n')
            except:
                print('\nInvalid port. Try again.\n')


#base url?
def get_base(brand):
    defaultbase='emby'
    #print('If you are using emby press enter for default.')
    if (brand == defaultbase):
        print('Using "/' + defaultbase + '" as base url')
        return(defaultbase)
    else:
        print('If you have not explicity changed this option in jellyfin, press enter for default.')
        print('For example: http://example.com/<baseurl>')
        base=input('Enter base url (default /' + defaultbase + '): ')
        if (base == ''):
            return(defaultbase)
        else:
            if (base.find('/',0,1) == 0):
                return(base[1:len(base)])
            else:
                return(base)


#admin username?
def get_admin_username():
    return(input('Enter admin username: '))


#admin password?
def get_admin_password():
    #print('Plain text password used to grab access token; hashed password stored in config file.')
    print('Plain text password used to grab access token; password not stored in config file.')
    password=input('Enter admin password: ')
    return(password)


#used of hashed password to be removed in future
#hash admin password
#def get_admin_password_sha1(password):
#    #password_sha1=password #input('Enter admin password (password will be hashed in config file): ')
#    password_sha1=hashlib.sha1(password.encode()).hexdigest()
#    return(password_sha1)


#get user input needed to build the media_cleaner_config.py file
def generate_config():
    print('-----------------------------------------------------------')
    server_brand=get_brand()

    print('-----------------------------------------------------------')
    server=get_url()
    print('-----------------------------------------------------------')
    port=get_port()
    print('-----------------------------------------------------------')
    server_base=get_base(server_brand)
    if (len(port)):
        server_url=server + ':' + port + '/' + server_base
    else:
        server_url=server + '/' + server_base
    print('-----------------------------------------------------------')

    username=get_admin_username()
    print('-----------------------------------------------------------')
    password=get_admin_password()
    print('-----------------------------------------------------------')

    auth_key=get_auth_key(server_url, username, password)
    user_key=list_users(server_url, auth_key)
    print('-----------------------------------------------------------')
    whitelist=list_library_folders(server_url, auth_key)
    print('-----------------------------------------------------------')

    not_played_age_movie="-1"
    not_played_age_episode="-1"
    not_played_age_video="-1"
    not_played_age_trailer="-1"
    not_played_age_audio="-1"

    config_file=''
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# 0-365000000 - Delete media type once it has been watched x days ago\n"
    config_file += "# -1 : to disable managing specified media type\n"
    config_file += "# (-1 : default)\n"
    config_file += "# Audio media is a work in progress...\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "not_played_age_movie=" + not_played_age_movie + "\n"
    config_file += "not_played_age_episode=" + not_played_age_episode + "\n"
    config_file += "not_played_age_video=" + not_played_age_video + "\n"
    config_file += "not_played_age_trailer=" + not_played_age_trailer + "\n"
    config_file += "not_played_age_audio=" + not_played_age_audio + "\n"
    #config_file += "not_played_age_tvchannel=" + not_played_age_tvchannel + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Favoriting a series or season will treat all child episodes as if they are favorites\n"
    config_file += "# Favoriting an artist, album-artist, or album will treat all child tracks as if they are favorites\n"
    config_file += "# 0 - Ok to delete movie played not_played_age_movie=x days ago\n"
    config_file += "# 1 - Do no delete movie played not_played_age_movie=x days ago\n"
    config_file += "# Same applies for other media types (episodes, trailers, etc...)\n"
    config_file += "# (1 - default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "keep_favorites_movie=1\n"
    config_file += "keep_favorites_episode=1\n"
    config_file += "keep_favorites_video=1\n"
    config_file += "keep_favorites_trailer=1\n"
    config_file += "keep_favorites_audio=1\n"
    #config_file += "keep_favorites_tvchannel=1\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Whitelisting a library folder will treat all child media as if they are favorites\n"
    config_file += "# ('' - default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "whitelisted_library_folders='" + whitelist + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# 0 - Disable the ability to delete media (dry run mode)\n"
    config_file += "# 1 - Enable the ability to delete media\n"
    config_file += "# (0 - default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "remove_files=0\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#------------DO NOT MODIFY BELOW---------------------------#\n"
    config_file += "server_brand='" + server_brand + "'\n"
    config_file += "server_url='" + server_url + "'\n"
    config_file += "admin_username='" + username + "'\n"
    config_file += "access_token='" + auth_key + "'\n"
    config_file += "user_key='" + user_key + "'\n"
    config_file += "DEBUG=0\n"
    #config_file += "#----------------------------------------------------------#"

    #Create config file next to the script even when cwd (Current Working Directory) is not the same
    cwd = os.getcwd()
    script_dir = os.path.dirname(__file__)
    if (script_dir == ''):
        #script must have been run from the cwd
        #set script_dir to cwd (aka this directory) to prevent error when attempting to change to '' (aka a blank directory)
        script_dir=cwd
    os.chdir(script_dir)
    f = open("media_cleaner_config.py", "w")
    f.write(config_file)
    f.close()
    os.chdir(cwd)

    print('\n\n-----------------------------------------------------------')
    print('Config file is not setup to manage media types.')
    print('-----------------------------------------------------------')
    print('To manage media types open media_cleaner_config.py in a text editor:')
    print('    Set \'not_played_age_movie\' to zero or a positive number')
    print('    Set \'not_played_age_episode\' to zero or a positive number')
    print('    Set \'not_played_age_video\' to zero or a positive number')
    print('    Set \'not_played_age_trailer\' to zero or a positive number')
    print('    Set \'not_played_age_audio\' to zero or a positive number')
    print('-----------------------------------------------------------')
    print('Config file is in dry run mode to prevent deleting media types.')
    print('-----------------------------------------------------------')
    print('To delete media types open media_cleaner_config.py in a text editor:')
    print('    Set \'remove_files=1\' in media_cleaner_config.py')
    print('-----------------------------------------------------------')
    print('Edit the config file and try running again.')
    print('-----------------------------------------------------------')


#api call to delete items
def delete_item(itemID):
    url=url=cfg.server_url + '/Items/' + itemID + '?api_key=' + cfg.access_token
    req = request.Request(url,method='DELETE')
    if bool(cfg.DEBUG):
        #DEBUG
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


#api call to get admin account authentication token
def get_auth_key(server_url, username, password):
    #login info
    values = {'Username' : username, 'Pw' : password}
    #DATA = urllib.parse.urlencode(values)
    #DATA = DATA.encode('ascii')
    DATA = convert2json(values)
    DATA = DATA.encode('utf-8')

    headers = {'X-Emby-Authorization' : 'Emby UserId="'+ username  +'", Client="media_cleaner", Device="media_cleaner", DeviceId="media_cleaner", Version="0.3", Token=""', 'Content-Type' : 'application/json'}

    req = request.Request(url=server_url + '/Users/AuthenticateByName', data=DATA, method='POST', headers=headers)

    with request.urlopen(req) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)

            #DEBUG
            #print('get auth key data)
            #print2json(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    return(data['AccessToken'])


#api call to get all user accounts
#then choose account this script will use to delete watched media
#choosen account does NOT need to have "Allow Media Deletion From" enabled
def list_users(server_url, auth_key):
    #Get all users
    with request.urlopen(server_url + '/Users?api_key=' + auth_key) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)

            #DEBUG
            #print('list users')
            #print2json(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    valid_user=False
    while (valid_user == False):
        i=0
        for user in data:
            print(str(i) +' - '+ user['Name'] + ' - ' + user['Id'])
            i += 1

        user_number=input('Enter number of user to track: ')

        try:
            user_number_float=float(user_number)
            if ((user_number_float % 1) == 0):
                user_number_int=int(user_number_float)
                if ((user_number_int >= 0) and (user_number_int < i)):
                    valid_user=True
                else:
                    print('\nInvalid number. Try again.\n')
            else:
                print('\nInvalid number. Try again.\n')
        except:
            print('\nInvalid number. Try again.\n')

    userID=data[user_number_int]['Id']
    return(userID)


#api call to get library folders
#then choose which folders to whitelist
def list_library_folders(server_url, auth_key):
    #get all library paths
    with request.urlopen(server_url + '/Library/VirtualFolders?api_key=' + auth_key) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)

            #DEBUG
            #print('list library folders')
            #print2json(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    #define empty dictionary
    libraryfolders_dict={}
    #define empty set
    libraryfolders_set=set()

    stop_loop=False
    while (stop_loop == False):
        i=0
        for path in data:
            for subpath in range(len(path['LibraryOptions']['PathInfos'])):
                if ('NetworkPath' in path['LibraryOptions']['PathInfos'][subpath]):
                    if not (path['LibraryOptions']['PathInfos'][subpath]['NetworkPath'] in libraryfolders_set):
                        print(str(i) + ' - ' + path['LibraryOptions']['PathInfos'][subpath]['Path'] + ' - (' + path['LibraryOptions']['PathInfos'][subpath]['NetworkPath'] +')')
                        libraryfolders_dict[i]=path['LibraryOptions']['PathInfos'][subpath]['NetworkPath']
                    else:
                        #show blank entry
                        print(str(i) + ' - ')
                else: #('Path' in path['LibraryOptions']['PathInfos'][subpath]):
                    if not(path['LibraryOptions']['PathInfos'][subpath]['Path'] in libraryfolders_set):
                        print(str(i) + ' - ' + path['LibraryOptions']['PathInfos'][subpath]['Path'])
                        libraryfolders_dict[i]=path['LibraryOptions']['PathInfos'][subpath]['Path']
                    else:
                        #show blank entry
                        print(str(i) + ' - ')
                i += 1

        if (i >= 1):
            print('Enter number of library folder to whitelist.')
            print('Media in whitelisted library folders will NOT be deleted.')
            path_number=input('Leave blank for none or when finished: ')
        else:
            path_number=''

        try:
            if (path_number == ''):
                stop_loop=True
                print('')
            else:
                path_number_float=float(path_number)
                if ((path_number_float % 1) == 0):
                    path_number_int=int(path_number_float)
                    if ((path_number_int >= 0) and (path_number_int < i)):
                        libraryfolders_set.add(libraryfolders_dict[path_number_int])
                        if (len(libraryfolders_set) >= i):
                            stop_loop=True
                            print('')
                        else:
                            stop_loop=False
                            print('')

                        #DEBUG
                        #print('selected library folders')
                        #print(libraryfolders_set)
                    else:
                        print('\nInvalid number. Try again.\n')
                else:
                    print('\nInvalid number. Try again.\n')
        except:
            print('\nInvalid number. Try again.\n')

    if (libraryfolders_set == set()):
        return('')
    else:
        i=0
        whitelistpaths=''
        for libfolders in libraryfolders_set:
            if (i == 0):
                #libfolders = libfolders.replace('\"','\\\"')
                whitelistpaths = libfolders.replace('\'','\\\'')
            else:
                #libfolders = libfolders.replace('\"','\\\"')
                whitelistpaths = libfolders.replace('\'','\\\'') + ',' + whitelistpaths
            i += 1

        return(whitelistpaths)


#Get count of days since last watched
def get_days_since_played(date_last_played):
    #Get current time
    date_time_now = datetime.utcnow()

    #Keep the year, month, day, hour, minute, and seconds
      #split date_last_played after seconds
    try:
        split_date_micro_tz = date_last_played.split(".")
        date_time_last_played = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.' + split_date_micro_tz[1])
    except (ValueError):
        date_time_last_played = 'unknown date time format'

    if bool(cfg.DEBUG):
        #DEBUG
        print(date_time_last_played)

    if not (date_time_last_played == 'unknown date time format'):
        date_time_delta = date_time_now - date_time_last_played
        s_date_time_delta = str(date_time_delta)
        days_since_played = s_date_time_delta.split(' day')[0]
        if ':' in days_since_played:
            days_since_played = 'Played <1 day ago'
        elif days_since_played == '1':
            days_since_played = 'Played ' + days_since_played + ' day ago'
        else:
            days_since_played = 'Played ' + days_since_played + ' days ago'
    else:
        days_since_played='0'
    return(days_since_played)


#get season and episode numbers
def get_season_episode(season_number, episode_number):
    season_num = str(season_number)
    season_num_len=len(str(season_number))

    episode_num = str(episode_number)
    episode_num_len=len(str(episode_num))

    #at the least; print season.episode with 2-digits zero padded
    #if season or episode has more than 2-digits print x-digits zero padded
    if (season_num_len <= 2) and (episode_num_len <= 2):
        season_num = season_num.zfill(2)
        episode_num = episode_num.zfill(2)
    elif (season_num_len >= episode_num_len):
        season_num = season_num.zfill(season_num_len)
        episode_num = episode_num.zfill(season_num_len)
    else: #(season_num_len < episode_num_len):
        season_num = season_num.zfill(episode_num_len)
        episode_num = episode_num.zfill(episode_num_len)

    season_episode = 's' + season_num + '.e' + episode_num
    return(season_episode)


#get additional item info needed to determine if parent of item is favorite
#get additional item info needed to determine if media item is in whitelist
def get_additional_item_info(server_url, user_key, itemId, auth_key):
    #Get additonal item information
    url=server_url + '/Users/' + user_key  + '/Items/' + itemId + '?api_key=' + auth_key

    if bool(cfg.DEBUG):
        #DEBUG
        print('-----------------------------------------------------------')
        print(url)
    with request.urlopen(url) as response:
        if response.getcode() == 200:
            source = response.read()
            itemInfo = json.loads(source)
            if bool(cfg.DEBUG):
                #DEBUG
                print('get_additional_item_info')
                print2json(itemInfo)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    return(itemInfo)


#determine if track, album or artist is set to favorite
#def get_isfav_MUSICtaa(isfav_MUSICtaa, item, server_url, user_key, auth_key):
    #work in progress


#determine if episode, season, or series is set to favorite
def get_isfav_TVess(isfav_TVess, item, server_url, user_key, auth_key):
    #Check if episode's favorite value already exists in dictionary
    if not item['Id'] in isfav_TVess['episode']:
        #Store if this episode is marked as a favorite
        isfav_TVess['episode'][item['Id']] = item['UserData']['IsFavorite']
    #Check if season's favorite value already exists in dictionary
    if not item['SeasonId'] in isfav_TVess['season']:
        #Store if the season is marked as a favorite
        isfav_TVess['season'][item['SeasonId']] = get_additional_item_info(server_url, user_key, item['SeasonId'], auth_key)['UserData']['IsFavorite']
    #Check if series' favorite value already exists in dictionary
    if not item['SeriesId'] in isfav_TVess['series']:
        #Store if the series is marked as a favorite
        isfav_TVess['series'][item['SeriesId']] = get_additional_item_info(server_url, user_key, item['SeriesId'], auth_key)['UserData']['IsFavorite']
    if bool(cfg.DEBUG):
        #DEBUG
        print('-----------------------------------------------------------')
        print('Episode is favorite: ' + str(isfav_TVess['episode'][item['Id']]))
        print(' Season is favorite: ' + str(isfav_TVess['season'][item['SeasonId']]))
        print(' Series is favorite: ' + str(isfav_TVess['series'][item['SeriesId']]))

    #Check if episode, season, or series is a favorite
    if (
       (isfav_TVess['episode'][item['Id']]) or
       (isfav_TVess['season'][item['SeasonId']]) or
       (isfav_TVess['series'][item['SeriesId']]) #or
       ):
        #Either the episode, season, or series is set as a favorite
        itemisfav_TVess=True
    else:
        #Neither the episode, season, or series is set as a favorite
        itemisfav_TVess=False

    return(itemisfav_TVess)


#determine if media item is in whitelisted folder
def get_iswhitelisted(itemPath):
    #read whitelist configuration variable
    whitelist=cfg.whitelisted_library_folders
    whitelistentries=whitelist.split(',')

    item_is_whitelisted=False
    #determine if media item's path matches one of the whitelist folders
    for path in whitelistentries:
        if not (path == ''):
            if (itemPath.startswith(path)):
                item_is_whitelisted=True

                if bool(cfg.DEBUG):
                    #DEBUG
                    print('whitelist folder comparison')
                    print(path + ' : ' + itemPath)

                return(item_is_whitelisted)
            else:
                item_is_whitelisted=False
        else:
            item_is_whitelisted=False
    return(item_is_whitelisted)


#get watched media items; track media items ready to be deleted
def get_items(server_url, user_key, auth_key):
    #Get list of all played items
    print('')
    print('-----------------------------------------------------------')
    print('Start...')
    print('Cleaning media for server at: ' + server_url)
    print('-----------------------------------------------------------')
    print('\n')
    print('-----------------------------------------------------------')
    print('Get List Of Watched Media:')
    print('-----------------------------------------------------------')

    url=server_url + '/Users/' + user_key  + '/Items?Recursive=true&IsPlayed=true&SortBy=Type,SeriesName,ParentIndexNumber,IndexNumber,Name&SortOrder=Ascending&api_key=' + auth_key

    if bool(cfg.DEBUG):
        #DEBUG
        print(url)

    with request.urlopen(url) as response:
        if response.getcode() == 200:
            source = response.read()
            data = json.loads(source)
            if bool(cfg.DEBUG):
                #DEBUG
                print('played_media_data')
                print2json(data)
        else:
            print('An error occurred while attempting to retrieve data from the API.')

    #Go through all items and get ones not played in X days
    cut_off_date_movie=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_movie)
    cut_off_date_episode=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_episode)
    cut_off_date_video=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_video)
    cut_off_date_trailer=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_trailer)
    cut_off_date_audio=datetime.now(timezone.utc) - timedelta(cfg.not_played_age_audio)
    deleteItems=[]

    #define empty dictionary for favorited TV Series', Seasons, and Episodes
    isfav_TVess={'episode':{},'season':{},'series':{}}
    #define empty dictionary for favorited Artists', Albums, and Audio-Tracks
    isfav_MUSICtaa={'track':{},'album':{},'artist':{}}

    #Determine if media item is to be deleted or kept
    for item in data['Items']:
        #find movie media items ready to delete
        if (item['Type'] == 'Movie'):
            #Get if media item is whitelisted
            item_info=get_additional_item_info(server_url, user_key, item['Id'], auth_key)
            itemIsWhiteListed=get_iswhitelisted(item_info['Path'])
            if (
               (cfg.not_played_age_movie >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_movie > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.keep_favorites_movie) or not item['UserData']['IsFavorite']) and
               (not itemIsWhiteListed)
               ):
                try:
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'MovieID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Delete Movie: \n' + str(item))
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'MovieID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Keep Movie: \n' + str(item))
                print(':[KEEPING] - ' + item_details)
        #find tv-episode media items ready to delete
        elif (item['Type'] == 'Episode'):
            #Get if episode, season, or series is set as favorite
            itemisfav_TVess=get_isfav_TVess(isfav_TVess, item, server_url, user_key, auth_key)
            #Get if media item is whiteliested
            item_info=get_additional_item_info(server_url, user_key, item['Id'], auth_key)
            itemIsWhiteListed=get_iswhitelisted(item_info['Path'])
            if (
               (cfg.not_played_age_episode >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_episode > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.keep_favorites_episode) or (not itemisfav_TVess)) and
               (not itemIsWhiteListed)
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(itemisfav_TVess) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'EpisodeID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Delete Episode: \n' + str(item))
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(itemisfav_TVess) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'EpisodeID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Keep Episode: \n' + str(item))
                print(':[KEEPING] - ' + item_details)
        #find video media items ready to delete
        elif (item['Type'] == 'Video'):
            #Get if media item is whiteliested
            item_info=get_additional_item_info(server_url, user_key, item['Id'], auth_key)
            itemIsWhiteListed=get_iswhitelisted(item_info['Path'])
            if (
               (item['Type'] == 'Video') and
               (cfg.not_played_age_video >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_video > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.keep_favorites_video) or not item['UserData']['IsFavorite']) and
               (not itemIsWhiteListed)
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'VideoID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Delete Video: \n' + str(item))
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'VideoID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Keep Video: \n' + str(item))
                print(':[KEEPING] - ' + item_details)
        #find trailer media items ready to delete
        elif (item['Type'] == 'Trailer'):
            #Get if media item is whiteliested
            item_info=get_additional_item_info(server_url, user_key, item['Id'], auth_key)
            itemIsWhiteListed=get_iswhitelisted(item_info['Path'])
            if (
               (cfg.not_played_age_trailer >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_trailer > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.keep_favorites_trailer) or not item['UserData']['IsFavorite']) and
               (not itemIsWhiteListed)
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'TrailerID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Delete Trailer: \n' + str(item))
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'TrailerID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Keep Trailer: \n' + str(item))
                print(':[KEEPING] - ' + item_details)
        #find audio media items ready to delete
        elif (item['Type'] == 'Audio'):
            #Get if media item is whiteliested
            item_info=get_additional_item_info(server_url, user_key, item['Id'], auth_key)
            itemIsWhiteListed=get_iswhitelisted(item_info['Path'])
            if (
               (cfg.not_played_age_audio >= 0) and
               (item['UserData']['PlayCount'] >= 1) and
               (cut_off_date_audio > parse(item['UserData']['LastPlayedDate'])) and
               (not bool(cfg.keep_favorites_audio) or not item['UserData']['IsFavorite']) and
               (not itemIsWhiteListed)
               ):
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' -  Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'TrackID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Delete Audio: \n' + str(item))
                print(':*[DELETE] - ' + item_details)
                deleteItems.append(item)
            else:
                try:
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - ' + 'TrackID: ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('\nError encountered - Keep Audio: \n' + str(item))
                print(':[KEEPING] - ' + item_details)
        #idk what these are; keep them
        else: #(item['Type'] == 'Unknown')
            try:
                if bool(cfg.DEBUG):
                    item_details=item['Type'] + ' - ' + item['Name'] + ' - Favorite: ' + str(item['UserData']['IsFavorite']) + ' - ID: ' + item['Id']
            except (KeyError):
                if bool(cfg.DEBUG):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    #DEBUG
                    print('\nError encountered - Keep Unknown Media Type: \n' + str(item))
            if bool(cfg.DEBUG):
                print(':[KEEPING ' + str(item['Type'])  + ' MEDIA TYPE] - ' + item_details)

    if len(data['Items']) <= 0:
        print('[NO WATCHED ITEMS]')

    if bool(cfg.DEBUG):
        print('-----------------------------------------------------------')
        print('')
        print('isfav_TVess: ')
        print(isfav_TVess)
        print('')
        print('isfav_MUSICtaa: ')
        print(isfav_MUSICtaa)
        print('')

    print('-----------------------------------------------------------')
    print('\n')
    return(deleteItems)


#list and delete items past watched threshold
def list_delete_items(deleteItems):
    #List items to be deleted
    print('-----------------------------------------------------------')
    print('Summary Of Deleted Media:')
    if not bool(cfg.remove_files):
        print('* Trial Run           *')
        print('* remove_files=0      *')
        print('* No Media Deleted    *')
        print('* Items = ' + str(len(deleteItems)))
        print('-----------------------------------------------------------')
    else:
        print('* Items Deleted = ' + str(len(deleteItems)) + '    *')
        print('-----------------------------------------------------------')

    if len(deleteItems) > 0:
        for item in deleteItems:
            if item['Type'] == 'Movie':
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Episode':
                try:
                    item_details=item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                except (KeyError):
                    item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('Error encountered - Delete Episode: \n\n' + str(item))
            elif item['Type'] == 'Video':
                item_details='  ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Trailer':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Audio':
                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            else: # item['Type'] == 'Unknown':
                pass
            #Delete media item
            delete_item(item['Id'])
            print('[DELETED] ' + item_details)
    else:
        print('[NO ITEMS TO DELETE]')

    print('-----------------------------------------------------------')
    print('\n')
    print('-----------------------------------------------------------')
    print('Done.')
    print('-----------------------------------------------------------')
    print('')


#Check select config variables are an expected value
def cfgVarValCheck():
    #need to find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop
    test=cfg.not_played_age_movie
    if (
        not ((type(test) is int) and
        (test >= -1) and
        (test <= 365000000))
       ):
        raise TypeError('not_played_age_movie must be an integer; valid range -1 thru 365000000')

    test=cfg.not_played_age_episode
    if (
        not ((type(test) is int) and
        (test >= -1) and
        (test <= 365000000))
       ):
        raise TypeError('not_played_age_episode must be an integer; valid range -1 thru 365000000')

    test=cfg.not_played_age_video
    if (
        not ((type(test) is int) and
        (test >= -1) and
        (test <= 365000000))
       ):
        raise TypeError('not_played_age_video must be an integer; valid range -1 thru 365000000')

    test=cfg.not_played_age_trailer
    if (
        not ((type(test) is int) and
        (test >= -1) and
        (test <= 365000000))
       ):
        raise TypeError('not_played_age_trailer must be an integer; valid range -1 thru 365000000')

    test=cfg.not_played_age_audio
    if (
        not ((type(test) is int) and
        (test >= -1) and
        (test <= 365000000))
       ):
        raise TypeError('not_played_age_audio must be an integer; valid range -1 thru 365000000')

    test=cfg.keep_favorites_movie
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('keep_favorites_movie must be an integer; valid values 0 and 1')

    test=cfg.keep_favorites_episode
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('keep_favorites_episode must be an integer; valid values 0 and 1')

    test=cfg.keep_favorites_video
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('keep_favorites_video must be an integer; valid values 0 and 1')

    test=cfg.keep_favorites_trailer
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('keep_favorites_trailer must be an integer; valid values 0 and 1')

    test=cfg.keep_favorites_audio
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('keep_favorites_audio must be an integer; valid values 0 and 1')

    test=cfg.whitelisted_library_folders
    if (
        not (type(test) is str)
       ):
        raise TypeError('whitelisted_library_folders must be a string')

    test=cfg.remove_files
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('remove_files must be an integer; valid values 0 and 1')

    test=cfg.server_brand
    if (
        not (type(test) is str)
       ):
        raise TypeError('server_brand must be a string')

    test=cfg.server_url
    if (
        not (type(test) is str)
       ):
        raise TypeError('server_url must be a string')

    test=cfg.admin_username
    if (
        not (type(test) is str)
       ):
        raise TypeError('admin_username must be a string')

    test=cfg.access_token
    if (
        not (type(test) is str)
       ):
        raise TypeError('access_token must be a string')

    test=cfg.user_key
    if (
        not (type(test) is str)
       ):
        raise TypeError('user_key must be a string')

    test=cfg.DEBUG
    if (
        not ((type(test) is int) and
        (test >= 0) and
        (test <= 1))
       ):
        raise TypeError('DEBUG must be an integer; valid values 0 and 1')

############# START OF SCRIPT #############

try:
    #try importing the media_cleaner_config.py file
    #if media_cleaner_config.py file does not exsit go to except and create one
    import media_cleaner_config as cfg
    #try setting DEBUG variable from media_cleaner_config.py file
    #if DEBUG does not exsit go to except and completely rebuild the media_cleaner_config.py file
    test=cfg.DEBUG
    #removing DEBUG from media_cleaner_config.py file is sort of configuration reset

    #depending on what is missing from media_cleaner_config.py file; try to only ask for certain input
    if (
        not hasattr(cfg, 'not_played_age_movie') or
        not hasattr(cfg, 'not_played_age_episode') or
        not hasattr(cfg, 'not_played_age_video') or
        not hasattr(cfg, 'not_played_age_trailer') or
        not hasattr(cfg, 'not_played_age_audio') or
        not hasattr(cfg, 'keep_favorites_movie') or
        not hasattr(cfg, 'keep_favorites_episode') or
        not hasattr(cfg, 'keep_favorites_video') or
        not hasattr(cfg, 'keep_favorites_trailer') or
        not hasattr(cfg, 'keep_favorites_audio') or
        not hasattr(cfg, 'remove_files') or
        not hasattr(cfg, 'whitelisted_library_folders') or
        not hasattr(cfg, 'server_brand') or
        not hasattr(cfg, 'server_url') or
        not hasattr(cfg, 'admin_username') or
        not hasattr(cfg, 'access_token') or
        not hasattr(cfg, 'user_key')
       ):
        if (
            not hasattr(cfg, 'server_brand') or
            not hasattr(cfg, 'server_url') or
            not hasattr(cfg, 'admin_username') or
            not hasattr(cfg, 'access_token') or
            not hasattr(cfg, 'user_key') or
            not hasattr(cfg, 'whitelisted_library_folders')
           ):

            if hasattr(cfg, 'server_brand'):
                delattr(cfg, 'server_brand')
            if hasattr(cfg, 'server_url'):
                delattr(cfg, 'server_url')
            if hasattr(cfg, 'admin_username'):
                delattr(cfg, 'admin_username')
            if hasattr(cfg, 'access_token'):
                delattr(cfg, 'access_token')
            if hasattr(cfg, 'user_key'):
                delattr(cfg, 'user_key')
            if hasattr(cfg, 'whitelisted_library_folders'):
                delattr(cfg, 'whitelisted_library_folders')

            print('-----------------------------------------------------------')
            server_brand=get_brand()

            print('-----------------------------------------------------------')
            server=get_url()
            print('-----------------------------------------------------------')
            port=get_port()
            print('-----------------------------------------------------------')
            server_base=get_base(server_brand)
            if (len(port)):
                server_url=server + ':' + port + '/' + server_base
            else:
                server_url=server + '/' + server_base
            print('-----------------------------------------------------------')

            username=get_admin_username()
            print('-----------------------------------------------------------')
            password=get_admin_password()
            print('-----------------------------------------------------------')

            auth_key=get_auth_key(server_url, username, password)
            user_key=list_users(server_url, auth_key)
            print('-----------------------------------------------------------')

            whitelist=list_library_folders(server_url, auth_key)
            print('-----------------------------------------------------------')

        #warn user the configuration file is not complete
        #the missing varibles are not saved and will need to be manually entered the next time the script is run
        #a new media_cleaner_config.py file will need to be completed or manually updated without duplicates
        print('\n')
        print('-----------------------------------------------------------')
        print('ATTENTION!!!')
        print('Old or incomplete config in use.')
        print('1) Delete media_cleaner_config.py and run this again to create a new config.')
        print('   Or')
        print('2) Delete DEBUG from media_cleaner_config.py and run this again to create a new config.')
        print('-----------------------------------------------------------')
        print('Matching value(s) in media_cleaner_config.py ignored.')
        print('Using the below config value(s) for this run:')
        print('-----------------------------------------------------------')

        if not hasattr(cfg, 'not_played_age_movie'):
            print('not_played_age_movie=-1')
            setattr(cfg, 'not_played_age_movie', -1)
        if not hasattr(cfg, 'not_played_age_episode'):
            print('not_played_age_episode=-1')
            setattr(cfg, 'not_played_age_episode', -1)
        if not hasattr(cfg, 'not_played_age_video'):
            print('not_played_age_video=-1')
            setattr(cfg, 'not_played_age_video', -1)
        if not hasattr(cfg, 'not_played_age_trailer'):
            print('not_played_age_trailer=-1')
            setattr(cfg, 'not_played_age_trailer', -1)
        if not hasattr(cfg, 'not_played_age_audio'):
            print('not_played_age_audio=-1')
            setattr(cfg, 'not_played_age_audio', -1)

        if not hasattr(cfg, 'keep_favorites_movie'):
            print('keep_favorites_movie=1')
            setattr(cfg, 'keep_favorites_movie', 1)
        if not hasattr(cfg, 'keep_favorites_episode'):
            print('keep_favorites_episode=1')
            setattr(cfg, 'keep_favorites_episode', 1)
        if not hasattr(cfg, 'keep_favorites_video'):
            print('keep_favorites_video=1')
            setattr(cfg, 'keep_favorites_video', 1)
        if not hasattr(cfg, 'keep_favorites_trailer'):
            print('keep_favorites_trailer=1')
            setattr(cfg, 'keep_favorites_trailer', 1)
        if not hasattr(cfg, 'keep_favorites_audio'):
            print('keep_favorites_audio=1')
            setattr(cfg, 'keep_favorites_audio', 1)

        if not hasattr(cfg, 'whitelisted_library_folders'):
            print('whitelisted_library_folders=\'\'')
            setattr(cfg, 'whitelisted_library_folders', '\'\'')

        if not hasattr(cfg, 'remove_files'):
            print('remove_files=0')
            setattr(cfg, 'remove_files', 0)

        if not hasattr(cfg, 'server_brand'):
            print('server_brand=\'' + str(server_brand) + '\'')
            setattr(cfg, 'server_brand', server_brand)
        if not hasattr(cfg, 'server_url'):
            print('server_url=\'' + str(server_url) + '\'')
            setattr(cfg, 'server_url', server_url)
        if not hasattr(cfg, 'admin_username'):
            print('admin_username=\'' + str(username) + '\'')
            setattr(cfg, 'admin_username', username)
        if not hasattr(cfg, 'access_token'):
            print('access_token=\'' + str(auth_key) + '\'')
            setattr(cfg, 'access_token', auth_key)
        if not hasattr(cfg, 'user_key'):
            print('user_key=\'' + str(user_key) + '\'')
            setattr(cfg, 'user_key', user_key)

        #print('DEBUG=' + str(cfg.DEBUG))

        print('-----------------------------------------------------------')
        print ('\n')

#the except
except (AttributeError, ModuleNotFoundError):
    #we are here because the media_cleaner_config.py file does not exist
    #this is either the first time the script is running or media_cleaner_config.py file was deleted
    #when this happens create a new media_cleaner_config.py file
    #another possible reason we are here...
    #the above attempt to set test=cfg.DEBUG failed likely because DEBUG is missing from the media_cleaner_config.py file
    #when this happens create a new media_cleaner_config.py file
    generate_config()
    #exit gracefully
    exit(0)

#check config values are what we expect them to be
cfgVarValCheck()
#find media items to be deleted
deleteItems=get_items(cfg.server_url, cfg.user_key, cfg.access_token)
#list and delete found media items
list_delete_items(deleteItems)

############# END OF SCRIPT #############
