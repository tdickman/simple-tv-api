from xml.etree import ElementTree as et
from BeautifulSoup import BeautifulSoup
import requests
import json
import re


class SimpleTV:
    def __init__(self, username, password):
        self.remote = None
        self.date = '2014%2F1%2F16+1%3A56%3A5'
        self.s = requests.Session()
        self._login(username, password)

    def _login(self, username, password):
        url = 'https://us.simple.tv/Auth/SignIn'
        data = {
            'UserName': username,
            'Password': password,
            'RememberMe': 'true'
            }
        r = self.s.post(url, params=data)
        resp = json.loads(r.text)
        if 'SignInError' in resp:
            print "Error logging in"
            raise('Invalid login information')
        # self.sid = resp['MediaServerID']
        # Retrieve streaming urls
        r = self.s.get('https://us-my.simple.tv/')
        soup = BeautifulSoup(r.text)
        info = soup.find('section', {'id': 'watchShow'})
        self.account_id = info['data-accountid']
        self.sid = self.media_server_id = info['data-mediaserverid']
        r = self.s.get("https://us-my.simple.tv/Data/RealTimeData"
                       "?accountId={}&mediaServerId={}"
                       "&playerAlternativeAvailable=false".format(self.account_id, self.media_server_id))
        resp = json.loads(r.text)
        self.local_base = resp['LocalStreamBaseURL']
        self.remote_base = resp['RemoteStreamBaseURL']
        return True

    def get_shows(self):
        url = 'https://us-my.simple.tv/Library/MyShows'
        url += '?browserDateTimeUTC=' + self.date
        url += '&mediaServerID=' + self.sid
        url += '&browserUTCOffsetMinutes=-300'
        r = self.s.get(url)
        root = et.fromstring(r.text)
        shows = []
        for show in root:
            data = {}
            div = show.find('div')
            info = show.find('figcaption')
            data['group_id'] = show.attrib['data-groupid']
            data['image'] = div.find('img').attrib['src']
            data['name'] = info.find('b').text
            data['recordings'] = info.find('span').text
            shows.append(data)
        return shows

    def get_episodes(self, group_id):
        url = 'https://us-my.simple.tv/Library/ShowDetail'
        url += '?browserDateTimeUTC=' + self.date
        url += '&browserUTCOffsetMinutes=-300'
        url += '&groupID=' + group_id
        r = self.s.get(url)
        soup = BeautifulSoup(r.text)
        e = soup.find('div', {'id': 'recorded'}).findAll('article')
        episodes = []
        for episode in e:
            data = {}
            # Skip failed episodes for now
            try:
                epiList = episode.findAll('b')
                if len(epiList) == 3:   # Figure out if it's a Show or a Movie
                    data['season'] = int(epiList[1].text)
                    data['episode'] = int(epiList[2].text)
                else:
                    data['season'] = 0
                    data['episode'] = 0
                data['channel'] = str(epiList[0].text)
                links = episode.find('a', {'class': 'button-standard-watch'})
                data['item_id'] = links['data-itemid']
                data['instance_id'] = links['data-instanceid']
                data['title'] = episode.h3.find(
                    text=True,
                    recursive=False
                    ).rstrip()
            except:
                continue
            episodes.append(data)
        return episodes

    def _get_stream_urls(self, group_id, instance_id, item_id):
        url = 'https://us-my.simple.tv/Library/Player'
        url += '?browserUTCOffsetMinutes=-300'
        url += '&groupID=' + group_id
        url += '&instanceID=' + instance_id
        url += '&itemID=' + item_id
        url += '&isReachedLocally=' + ("False" if self.remote else "True")
        r = self.s.get(url)
        soup = BeautifulSoup(r.text)
        s = soup.find('div', {'id': 'video-player-large'})
        if self.remote:
            base = self.remote_base
        else:
            base = self.local_base
        req_url = base + s['data-streamlocation']
        stream_base = "/".join(req_url.split('/')[:-1]) + "/"
        # Get urls for different qualities
        # First time through, autodetect if remote
        if self.remote is None:
            try:
                r = self.s.get(req_url, timeout=5)
                self.remote = False
            except:
                self.remote = True
                return self._get_stream_urls(group_id, instance_id, item_id)
        r = self.s.get(req_url)
        urls = []
        for url in r.text.split('\n'):
            if url[-3:] == "3u8":
                urls.append(url)
        return {'base': stream_base, 'urls': urls}

    def retrieve_episode_mp4(self, group_id, instance_id, item_id, quality):
        '''Specify quality using int for entry into m3u8. Typically:
        0 = 500000, 1 = 1500000, 2 = 4500000
        '''
        s_info = self._get_stream_urls(group_id, instance_id, item_id)
        # Modify url for h264 mp4 :)
        url_m3u8 = s_info['base'] + s_info['urls'][int(quality)]
    m = re.match(".*hls-(?P<number>\d)\Wm3u8", url_m3u8)
    url = re.sub('hls-\d.m3u8', "10" + m.group("number"), url_m3u8)
    return url
