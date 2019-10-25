# media_cleaner
This script will go through all watched videos and delete any for a specific user that is older then a defined cutt off.

# Config file 
The first time you run the script it will attempt to create the config file for you by asking a few questions

filename: media_cleaner_config.py

* server_url='http://server:8096' - Server url for Emby server
* user_key='XXXXXXXXXXX'  - UserID of the user that script check watched status for
* not_played_age=100  - How many days since last watched date
* admin_username='UserName'  - Username for Admin user with access to delete files
* admin_password_sha1='YYYYYYYYYYYYY'  - SHA1 hashed password value
* remove_files=0  - 0 means trial run, no delete.  1 means remove files

# Usage
Make media_cleaner.py executable and run ./media_cleaner.py.  If no conifg file is found it will prompt you to create one.  Once done you can run the script again to view files that will be deleted

# Requirements
* python3

# Donation
If you find this useful and you would like to support please the use option below.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=jason%2ep%2eclara%40gmail%2ecom&lc=CA&item_name=Jason%20Clara&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
