import getpass
import api
import sys
import urllib

username = raw_input("Enter email: ")
password = getpass.getpass("Enter password: ")
print "Logging in..."
simple = api.SimpleTV(username, password)

# Select show
shows = simple.get_shows()
for val,show in enumerate(shows):
    print str(val) + ": " + show['name'].encode('utf-8')
show_id = input("Select show (#): ")
show = shows[show_id]
group_id = show['group_id']

# Select episode
episodes = simple.get_episodes(group_id)
for val,episode in enumerate(episodes):
    print str(val) + ": " + episode['title'].encode('utf-8')
episode_id = input("Select episode (#): ")
episode = episodes[episode_id]

# Download
instance_id = episode['instance_id']
item_id     = episode['item_id']
quality     = 2
file_name = show['name'] + " - " + episode['title'] + '.mp4'
counter = 0
print "Retrieving download url"
url = simple.retrieve_episode_mp4(group_id, instance_id, item_id, quality)
print "Downloading..."
(filename, headers) = urllib.urlretrieve(url, file_name)
