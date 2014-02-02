import getpass
import api
import sys

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
file_name = show['name'] + " - " + episode['title'] + '.ts'
counter = 0
print "Downloading..."
with open(file_name, 'w') as f:
    for data in simple.retrieve_episode(group_id, instance_id, item_id, quality):
        f.write( data )
        counter += 1
        message = "\rDownloading, " + str(counter) + " blocks complete"
        print message,
        sys.stdout.flush()
