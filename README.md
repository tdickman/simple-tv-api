simple-tv-api
=============
This is an api for accessing and playing back Simple.tv recordings.

Downloading Recordings
======================

This is an interactive python script used to download recordings from your simple.tv device to your local computer. Recordings are placed in the current directory with the name 'episode.ts'.

Example usage:

```python download.py```


API Server
==========

Example usage:

```python server.py [username] [password]```

This starts a webserver that can be accessed on port 8080. To get started, access the following url in your browser:

```http://localhost:8080 ```

-> This returns a list of shows recorded on your device.

Make another request using the 'url' parameter of each to access a list of episodes for the given show.

```http://localhost:8080/episodes?group_id=fffffff-ffff-ffff-ffff-ffffffffffff ```

-> This returns a list of episodes for the given show.

Again use the url parameter (notice the common theme here :) ), to download or stream the episode to your computer. For example, paste this url in vlc to watch on your linux machine. No silverlight support required.

```http://localhost:8080/stream?group_id=fffffff-ffff-ffff-ffff-ffffffffffff&instance_id=fffffff-ffff-ffff-ffff-ffffffffffff&item_id=fffffff-ffff-ffff-ffff-ffffffffffff ```

Optionally append ?quality=0 or 1 or 2 to change the quality.

Uses
====

This can be used to assemble an alternative web client for simple tv, download recordings, etc. The possibilities are endless!
