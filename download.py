import getpass
import api
import urllib
import urllib3
import os

# Edit this for Auto-login
# USERNAME = ""
# PASSWORD = ""
AUTO_DELETE = False


def select_show():
    shows = simple.get_shows()
    for val, show in enumerate(shows):
        # Only display shows with recordings (>0)
        if int(show['recordings']) != 0:
            print str(val) + ": " + show['name'].encode('utf-8') + " [" + show['recordings'] + " episodes]"
    show_id = raw_input("Select show (#): ")
    print "-" * 25
    if show_id.lower() == 'a' or show_id == '':
        print "Download all shows, all episodes"
        download_all_shows(shows)
    else:                # Specific show selected, pass that along to select_episode
        show = shows[int(show_id)]
        select_episode(show)


def select_episode(show):
    """
    Display list of episodes from show[] to choose form. BYPASSED by download_all_shows()
    """
    group_id = show['group_id']
    episodes = simple.get_episodes(group_id)
    episodes = generate_filename_menu(episodes, show)
    episode_id = raw_input("Select episode (#) or [A]ll Episodes (default): ")

    # Download one (or all) of the episodes with a call to download_episode()
    if episode_id == 'A' or episode_id == 'a' or episode_id == '':
        print "Downloading All files.."
        for x in range(len(episodes)):
            episode = episodes[x]
            download_episode(show, episode)
    else:
        episode = episodes[int(episode_id)]
        download_episode(show, episode)


def generate_filename_menu(episodes, show):
    for val, episode in enumerate(episodes):
        # Does not have Series / Episode numbers (probably a movie)
        if episode['season'] == 0:
            if show['name'] != episode['title']:
                episode['filename'] = show['name'] + " - " + episode['title'].encode('utf-8')
            else:
                episode['filename'] = show['name']
        else:
            # Display season and episode numbers
            episode['season'] = str(episode['season']).zfill(2)         # Pad with leading 0 if < 10
            episode['episode'] = str(episode['episode']).zfill(2)        # Pad with leading 0 if < 10
            episode['filename'] = "{name} - S{season}E{episode} - {title}".format(
                name=show['name'],
                season=episode['season'],
                episode=episode['episode'],
                title=episode['title']
                )
        episode['filename'] = episode['filename'] + "[" + episode['channel'] + "]"
        episode['filename'] = episode['filename'].replace(":", "-")
        episode['filename'] = episode['filename'].replace("'", "")
        print str(val) + ": " + episode['filename'].encode('utf-8')
    return episodes


def download_episode(show, episode):
    instance_id = episode['instance_id']
    item_id = episode['item_id']
    quality = 2
    group_id = show['group_id']
    file_name = episode['filename'] + '.mp4'

    url = simple.retrieve_episode_mp4(group_id, instance_id, item_id, quality)
    print "Downloading " + file_name
    (filename, headers) = urllib.urlretrieve(url, file_name)
    print "File size: ", os.path.getsize(file_name) >> 20, "MB"
    if AUTO_DELETE:
        url = "https://stv-p-api1-prod.rsslabs.net/content/actionjson/mediaserver/"
        url += simple.sid
        url += "/instance/"
        url += instance_id
        url += "?filetype=all"
        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
        http.request('DELETE', url, headers=headers)  # Gives a SSL Cert error. Not sure why..? Need to add 'assert_hostname=False' perhaps?
        print "[" + episode['filename'] + "] deleted from Simple.TV"


def download_all_shows(shows):
    for val, show in enumerate(shows):
        show = shows[val]
        # Only download shows with recordings
        if int(show['recordings']) != 0:
            print "\nDownloading " + show['name']
            group_id = show['group_id']
            episodes = simple.get_episodes(group_id)
            episodes = generate_filename_menu(episodes, show)
            for x in range(len(episodes)):
                episode = episodes[x]
                download_episode(show, episode)

if __name__ == "__main__":
    username = USERNAME if 'USERNAME' in locals() else raw_input("Enter email: ")
    password = PASSWORD if 'PASSWORD' in locals() else getpass.getpass("Enter password: ")
    print "Logging in...\n"
    print "Auto Delete set to {}, this can be changed in the settings section of download.py".format(str(AUTO_DELETE))
    print "-" * 25
    simple = api.SimpleTV(username, password)

    # Loop back to main menu
    while True:
        select_show()
