import getpass
import api
import sys
import urllib
import urllib3
import os
import base64

username = raw_input("Enter email: ")
password = getpass.getpass("Enter password: ")
#username = ""                                      # edit this for Auto-login
#password = ""                                      # edit this for Auto-login
auto_delete = False                                 # Change to False to disable, True to enable.
print "Logging in...\n"
print "Auto Delete set to " + str(auto_delete) + ", this can be changed in the settings section of download.py"
print "-----------------------"
simple = api.SimpleTV(username, password)

# Select show
def selectShow():
	shows = simple.get_shows()
	for val,show in enumerate(shows):    
		if int(show['recordings']) != 0:		  # Only display shows with recordings (>0). Side effect = skipped numbers.
			print str(val) + ": " + show['name'].encode('utf-8') + " [" + show['recordings'] + " episodes]"
	show_id = raw_input("Select show (#): ")
	print "-----------------------"
#	while int(show_id) >= len(shows):  # Ask again if number out of bounds
#		print "Error: Number was out of bounds. Please select again.\n\n\n"
#		show_id = raw_input("Select show (#) or [A]ll Shows & Episodes (default): ")
	if show_id == 'A' or show_id == 'a' or show_id == '':
		print "Download all shows, all episodes"
		downloadAllShows(shows)
	else:				# Specific show selected, pass that along to selectEpisode
		show = shows[int(show_id)]
#		group_id = show['group_id']  # probably don't need this because it's part of show[], which is being passed.
		selectEpisode(show)

# Select episode
def selectEpisode(show):		# Display list of episodes from show[] to choose from. BYPASSED by downloadAllShows()!!
	group_id 	= show['group_id']
	episodes 	= simple.get_episodes(group_id)
	episodes 	= generateFilename_Menu(episodes, show)
	episode_id 	= raw_input("Select episode (#) or [A]ll Episodes (default): ")
	# Download one (or all) of the episodes with a call to downloadEpisode()
	if episode_id == 'A' or episode_id == 'a' or episode_id == '':		# Download all available episodes
		print "Downloading All files.."
		for x in range(len(episodes)):
			episode = episodes[x]
			downloadEpisode(show, episode)
	else:																# Download single specified episode
		episode = episodes[int(episode_id)]
		downloadEpisode(show, episode)

def generateFilename_Menu(episodes, show):
	for val,episode in enumerate(episodes):
		if episode['season'] == 0: 		# Does not have Series/Episode Numbers (probably a movie)
			if show['name'] != episode['title']:
				episode['filename'] = show['name'] + " - " + episode['title'].encode('utf-8')
			else:
				episode['filename'] = show['name']
		else:								# Display Season & Episode Numbers
			episode['season'] = str(episode['season']).zfill(2) 		# Pad with leading 0 if < 10
			episode['episode'] = str(episode['episode']).zfill(2)		# Pad with leading 0 if < 10
			episode['filename'] = show['name'] + " - S" + str(episode['season']) + "E" + str(episode['episode']) + " - " + episode['title'].encode('utf-8')
		print str(val) + ": " + episode['filename'].encode('utf-8')		# Print episode menu	
	return episodes

# Download
def downloadEpisode(show, episode):
	instance_id = episode['instance_id']
	item_id     = episode['item_id']
	quality     = 2
	group_id	= show['group_id']
	file_name	= episode['filename'] + '.mp4'
	counter 	= 0
	
#	print "Retrieving download url"
	url = ""
	url = simple.retrieve_episode_mp4(group_id, instance_id, item_id, quality)
	print "Downloading " + file_name
#	print url
	(filename, headers) = urllib.urlretrieve(url, file_name)
	print "File size: " , os.path.getsize(file_name) >> 20 , "MB"
	if auto_delete == True:
		url= "https://stv-p-api1-prod.rsslabs.net/content/actionjson/mediaserver/"
		url += simple.sid
		url += "/instance/"
		url += instance_id
		url += "?filetype=all"
		http = urllib3.PoolManager()
		headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
		r = http.request('DELETE', url, headers=headers) # Gives a SSL Cert error. Not sure why..? Need to add 'assert_hostname=False' perhaps?
		print "[" + episode['filename'] + "] deleted from Simple.TV"

def downloadAllShows(shows):
	for val,show in enumerate(shows):    
		show = shows[val]
		if int(show['recordings']) != 0:		  # Only download shows with recordings (>0).
			print "\nDownloading " + show['name']
			group_id 	= show['group_id']
			episodes	= simple.get_episodes(group_id)
			episodes	= generateFilename_Menu(episodes, show)
			for x in range(len(episodes)):
		            episode = episodes[x]
		            downloadEpisode(show, episode)

# Main
while True:
	selectShow()
