from urllib.parse import quote
import urllib.error
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
import urllib.request

def get_video(search): 
   newSearch = quote(search)
   url = ("http://www.youtube.com/results?search_query=") + newSearch
   req = urllib.request.Request(url)
   oreq = urlopen(req)
   webpage = oreq.read()
   soup = bs(webpage, 'html.parser')
   vids = soup.find(attrs = { 'class':'yt-uix-tile-link' })
 
   vidx = 'http://www.youtube.com/' + vids['href']
   if "channel" in vidx:
      return 'http://www.youtube.com/' + soup.findAll(attrs = { 'class':'yt-uix-tile-link' })[1]['herf']

   return vidx
 
def next_video(newUrl):
   req = urllib.request.Request(newUrl)
   oreq = urlopen(req)
   webpage = oreq.read()
   soup = bs(webpage, 'html.parser')
   vids = soup.find(attrs = { 'class': 'content-link spf-link yt-uix-sessionlink spf-link' })

   return 'https://www.youtube.com/' + vids['href']
