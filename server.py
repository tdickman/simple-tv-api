import api
import cherrypy
import sys
import json

class SimpleServer(object):
    def __init__(self, username, password):
        self.s = api.SimpleTV(username, password)

    @cherrypy.expose
    def index(self):
        shows = self.s.get_shows()
        # Generate urls
        for show in shows:
            show['url'] = '/episodes?group_id=' + \
                    show['group_id']
        return json.dumps(shows)

    @cherrypy.expose
    def episodes(self, group_id):
        episodes = self.s.get_episodes(group_id)
        # Generate urls
        for episode in episodes:
            episode['url'] = '/stream' + \
                    '?group_id='    + group_id + \
                    '&instance_id=' + episode['instance_id'] + \
                    '&item_id='     + episode['item_id']
        return json.dumps(episodes)

    @cherrypy.expose
    def stream(self, group_id, instance_id, item_id, quality='0'):
        return self.s.retrieve_episode(group_id, instance_id, item_id, quality)

    stream._cp_config = {'response.stream': True}
    cherrypy.server.socket_host = '0.0.0.0'

if  __name__ =='__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    cherrypy.quickstart(SimpleServer(username, password))
