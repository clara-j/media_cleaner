# Script
## media_cleaner.py
This script will go through all played movies, tv episodes, videos, trailers, and audio for the specified user; deleting any media past the specified played age cut off.

# Configuration
## media_cleaner_config.py
The first time you run the script it will attempt to create the config file by asking a few questions.

## Configuration Contents
#### Media will be deleted once it has been played the configured number of days ago:
```python
#----------------------------------------------------------#
# Delete media type once it has been played x days ago
#   0-365000000 - number of days to wait before deleting played media
#  -1 : to disable managing specified media type
# (-1 : default)
#----------------------------------------------------------#
not_played_age_movie=-1
not_played_age_episode=-1
not_played_age_video=-1
not_played_age_trailer=-1
not_played_age_audio=-1
```
#### When enabled, media will not be deleted if it is marked as a favorite:
```python
#----------------------------------------------------------#
# Favoriting a series, season, or network-channel will treat all child episodes as if they are favorites
# Favoriting an artist, album-artist, or album will treat all child tracks as if they are favorites
#  0 : ok to delete movie played not_played_age_movie=x days ago
#  1 : do no delete movie played not_played_age_movie=x days ago
# (1 : default)
# Same applies for other media types (episodes, trailers, etc...)
#----------------------------------------------------------#
keep_favorites_movie=1
keep_favorites_episode=1
keep_favorites_video=1
keep_favorites_trailer=1
keep_favorites_audio=1
```
#### Additional options for determining if an audio track should be considered marked as a favorite based on specified metadata item:
```python
#----------------------------------------------------------#
# Advanced audio favorites configuration bitmask
#     Requires keep_favorites_audio=1
#  xxxxA - keep audio tracks based only on the first artist listed in the track's 'artist' metadata is favorited
#  xxxBx - keep audio tracks based only on the first artist listed in the tracks's 'album artist' metadata is favorited
#  xxCxx - work In Progress...
#  xDxxx - work In Progress...
#  Exxxx - work In Progress...
#  0 bit - disabled
#  1 bit - enabled
# (00001 - default)
#----------------------------------------------------------#
keep_favorites_audio_advanced='00001'
```
#### Dependent on the above "advanced audio options", determines if only the first metadata item should be considered or all metadata items should be considered:
```python
#----------------------------------------------------------#
# Advanced audio favorites all configuration bitmask
#     Requires matching keep_favorites_audio_advanced bitmask is enabled
#  xxxxa - xxxxA must be enabled above; will use ALL artists listed in the track's 'artist' metadata
#  xxxbx - xxxBx must be enabled above; will use ALL artists listed in the track's 'album artist' metadata
#  xxcxx - work In Progress...
#  xdxxx - work In Progress...
#  exxxx - work In Progress...
#  0 bit - disabled
#  1 bit - enabled
# (00000 - default)
#----------------------------------------------------------#
keep_favorites_audio_advanced_any='00000'
```
#### Media in these library folders will be treated as if they are all marked as a favorite (i.e. media will not be deleted):
```python
#----------------------------------------------------------#
# Whitelisting a library folder will treat all child media as if they are favorites
# ('' - default)
#----------------------------------------------------------#
whitelisted_library_folders='smb://hieroglyph/Pharaoh/xbmc/Movies'
```
#### Allows the script to be run without deleting media (i.e. for testing and setup); Set to 1 when ready for "production":
```python
#----------------------------------------------------------#
# 0 - Disable the ability to delete media (dry run mode)
# 1 - Enable the ability to delete media
# (0 - default)
#----------------------------------------------------------#
remove_files=0
```
#### Created first time the script runs; Do **_NOT_** edit these:
```python
#------------DO NOT MODIFY BELOW---------------------------#

#----------------------------------------------------------#
# Server branding chosen during setup
#  0 - 'emby'
#  1 - 'jellyfin'
# Server URL created during setup
# Admin username chosen during setup
# Access token requested from server during setup
# User key of account to monitor played media chosen during setup
#----------------------------------------------------------#
server_brand='xyz'
server_url='http://localhost.abc:8096/basename'
admin_username='Username'
access_token='0123456789abcdef0123456789abcdef0'
user_key='abcdef0123456789abcdef0123456789a'
DEBUG=0
```

# Usage
Make media_cleaner.py executable and run ./media_cleaner.py.  If no conifg file is found it will prompt you to create one.  Once done you can run the script again to view files that will be deleted

# Requirements
* python3
* python-dateutil

# First Run
* $ /path/to/python3.x /path/to/media_cleaner.py
* You may get the below python error if the python-dateutil module is not installed
   - ModuleNotFoundError: No module named 'dateutil' python-dateutil
* For Ubuntu/Linux Mint type systems you can install the python-dateutil module with the following commands:
   - $ sudo apt-get update
   - $ sudo apt-get upgrade -y
   - $ sudo apt-get install python3-pip -y
   - $ sudo pip3 install -U pip
   - $ sudo pip3 install python-dateutil
* For other operating systems
   - tbd or Google it

# Donation
If you find this useful and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jason%2ep%2eclara%40gmail%2ecom&lc=CA&item_name=Jason%20Clara&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
