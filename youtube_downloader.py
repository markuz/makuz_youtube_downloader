#!/usr/bin/env python
import sys
import urlparse
import gdata.youtube
import gdata.youtube.service
from optparse import OptionParser
import os
import StringIO
import urllib2
from libmyd import YOUTUBE_DEVELOPER_KEY

yt_service = gdata.youtube.service.YouTubeService()
yt_service.developer_key = YOUTUBE_DEVELOPER_KEY

def GetAndPrintVideoFeed(uri):
  yt_service = gdata.youtube.service.YouTubeService()
  feed = yt_service.GetYouTubeVideoFeed(uri)
  for entry in feed.entry:
    PrintEntryDetails(entry) 

def PrintEntryDetails(entry):
    #print dir(entry)
    print entry.media.title.text.center(80,'=')
    print 'Video published on: %s ' % entry.published.text
    print 'Video description: %s' % entry.media.description.text
    print 'Video category: %s' % entry.media.category[0].text
    print 'Video tags: %s' % entry.media.keywords.text
    print 'Video watch page: %s' % entry.media.player.url
    print 'Video flash player URL: %s' % entry.GetSwfUrl()
    print 'Video duration: %s' % entry.media.duration.seconds
    # show alternate formats
    for alternate_format in entry.media.content:
            print 'Alternate format'
            for i in dir(alternate_format):
                if i.startswith("_"):continue
                n = getattr(alternate_format, i)
                print i,'=', n 

    # show thumbnails
    #for thumbnail in entry.media.thumbnail:
    #    print 'Thumbnail url: %s' % thumbnail.url

def GetEntry(uri):
    #Know the entry..
    parse = urlparse.urlparse(uri)
    query = parse.query.split("&")
    vid = ''
    for part in query:
        if part.startswith("v="):
            vid = part[2:]
            break
    if not vid:
        return
    print (parse, vid)
    entry = yt_service.GetYouTubeVideoEntry(video_id=vid)
    return entry

parser= OptionParser()
options, args = parser.parse_args()


urls = []
for i in args:
    if os.path.isfile(i):
        f = open(i, 'rb')
        urls += f.readlines()[:]
        f.close()
    else:
        urls.append(i)

for url in urls:
    entry = GetEntry(url)
    if not entry:
        continue
    PrintEntryDetails(entry)
    for alternate in entry.media.content:
        if 'isDefault' not in alternate.extension_attributes:
            print alternate.url
            data_url = alternate.url
            break

    print "data_url",data_url
    data = urllib2.urlopen(data_url)
    content_length = data.info()['Content-Length']
    stream = StringIO.StringIO()
    byte_counter =0
    while True:
        data_block = data.read(1024)
        data_block_size = len(data_block)
        if not data_block_size:
            break
        byte_counter += data_block_size
        stream.write(data_block)
        print "saved %d/%s"%(byte_counter, content_length)
    f = open(entry.media.title.text + ".flv", 'w')
    f.write(stream.getvalue())
    f.close()
    sys.exit()

