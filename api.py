from xml.etree import ElementTree as et
from BeautifulSoup import BeautifulSoup
import os
import requests
import urllib
import json
import sys

class SimpleTV:
    def __init__(self, username, password):
        self.remote = True
        self.date = '2014%2F1%2F16+1%3A56%3A5'
        self.s = requests.Session()
        self._login(username, password)

    def _login(self, username, password):
        url = 'https://www.simple.tv/Auth/SignIn'
        data = {
                'UserName'   : username,
                'Password'   : password,
                'RememberMe' : 'true'
                }
        r = self.s.post(url, params=data)
        resp = json.loads(r.text)
        if 'SignInError' in resp:
            print "Error logging in"
            raise('Invalid login information')
        self.sid = resp['MediaServerID']
        # Retrieve streaming urls
        r = self.s.get('https://my.simple.tv/')
        soup = BeautifulSoup(r.text)
        info = soup.find('section', {'id':'watchShow'})
        self.local_base  = info['data-localstreambaseurl']
        self.remote_base = info['data-remotestreambaseurl']
        return True

    def get_shows(self):
        url  = 'https://my.simple.tv/Library/MyShows'
        url += '?browserDateTimeUTC=' + self.date
        url += '&mediaServerID=' + self.sid
        url += '&browserUTCOffsetMinutes=-300'
        r = self.s.get(url)
        root = et.fromstring(r.text)
        shows = []
        for show in root:
            data = {}
            div  = show.find('div')
            info = show.find('figcaption')
            data['group_id']    = show.attrib['data-groupid']
            data['image']      = div.find('img').attrib['src']
            data['name']       = info.find('b').text
            data['recordings'] = info.find('span').text
            shows.append(data)
        return shows

    def get_episodes(self, group_id):
        url  = 'https://my.simple.tv/Library/ShowDetail'
        url += '?browserDateTimeUTC=' + self.date
        url += '&browserUTCOffsetMinutes=-300'
        url += '&groupID=' + group_id
        r = self.s.get(url)
        soup = BeautifulSoup(r.text)
        e = soup.find('div', {'id':'recorded'}).findAll('article')
        episodes = []
        for episode in e:
            data = {}
            # Skip failed episodes for now
            try:
                links = episode.find('a', {'class':'button-standard-watch'})
                data['item_id']     = links['data-itemid']
                data['instance_id'] = links['data-instanceid']
                data['title']       = episode.h3.find(
                                            text=True,
                                            recursive=False
                                            ).rstrip()
            except:
                continue
            episodes.append(data)
        return episodes

    def _get_stream_urls(self, group_id, instance_id, item_id):
        url  = 'https://my.simple.tv/Library/Player'
        url += '?browserUTCOffsetMinutes=-300'
        url += '&groupID=' + group_id
        url += '&instanceID=' + instance_id
        url += '&itemID=' + item_id
        url += '&isReachedRemotely=' + ("True" if self.remote else "False")
        r = self.s.get(url)
        soup = BeautifulSoup(r.text)
        s = soup.find('div', {'id':'video-player-large'})
        if self.remote:
            base = self.remote_base
        else:
            base = self.local_base
        req_url = base + s['data-streamlocation']
        stream_base = "/".join(req_url.split('/')[:-1]) + "/"
        # Get urls for different qualities
        r = self.s.get(req_url)
        urls = []
        for url in r.text.split('\n'):
            if url[-3:] == "3u8":
                urls.append(url)
        return {'base':stream_base, 'urls':urls}

    def retrieve_episode(self, group_id, instance_id, item_id, quality):
        '''Specify quality using int for entry into m3u8. Typically:
        0 = 500000, 1 = 1500000, 2 = 4500000
        '''
        s_info = self._get_stream_urls(group_id, instance_id, item_id)
        r = requests.get(s_info['base'] + s_info['urls'][int(quality)])
        # Parse for lines starting in 'tv'
        chunks = []
        for line in r.text.split('\n'):
            if line[:2] == "tv":
                chunks.append(line)
        for chunk in chunks:
            url = s_info['base'] + chunk
            yield urllib.urlopen(url).read()

if  __name__ =='__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    s = SimpleTV(username, password)
    shows = s.get_shows()
    #for show in shows:
    #    episodes = s.get_episodes(show['show_id'])
    #    show['episodes'] = episodes
    #print shows
    episode = s.get_episodes(shows[1]['group_id'])[0]
    print s.retrieve_episode(
            shows[1]['group_id'],
            episode['instance_id'],
            episode['item_id'],
            0
            )
