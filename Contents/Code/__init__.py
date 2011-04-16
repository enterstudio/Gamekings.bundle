import re

TITLE    = 'Gamekings'
BASE_URL = 'http://www.gamekings.tv'
VIDEO    = '%s/videos' % BASE_URL
CATEGORY = '%s/category/%%s/page/%%d' % BASE_URL
PLAYLIST = '%s/wp-content/themes/gk2010/playlist2.php?id=%%s' % BASE_URL
XSPF_NS  = {'xspf':'http://xspf.org/ns/0/'}
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/gamekings', MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  MediaContainer.art       = R(ART)
  MediaContainer.title1    = TITLE
  MediaContainer.viewGroup = 'List'
  DirectoryItem.thumb      = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16'

####################################################################################################
def MainMenu():
  dir = MediaContainer()

  # The first list option is different from the rest (it misses the "class" attribute and has a wrong videoId (-1, while the real videoId for "All videos" is 3)
  dir.Append(Function(DirectoryItem(Playlist, title='Alle video\'s', thumb=R(ICON)), id='videos', title='Alle video\'s'))

  # All top level menu items
  list = HTML.ElementFromURL(VIDEO, errors='ignore').xpath('//select[@id="cat"]/option[@class="level-0"]')

  for menuitem in list:
    id    = menuitem.get('value')
    title = menuitem.xpath('./text()')[0].strip()

    # Check to see if an item has 'sub'-items (siblings with class="level-1")
    if len(menuitem.xpath('./following-sibling::*')) == 0 or menuitem.xpath('./following-sibling::*')[0].get('class') == 'level-0':
      dir.Append(Function(DirectoryItem(Playlist, title=title, thumb=R(ICON)), id=id, title=title))
    else:
      siblings = menuitem.xpath('./following-sibling::*')
      sub = []
      for sib in siblings:
        sibid    = sib.get('value')
        sibtitle = sib.xpath('./text()')[0].strip()
        siblevel = sib.get('class')

        if siblevel == 'level-0':
          break;
        else:
          sub.append([sibid, sibtitle])

      dir.Append(Function(DirectoryItem(Subcategory, title=title, thumb=R(ICON)), sub=sub))

  return dir

####################################################################################################
def Subcategory(sender, sub):
  dir = MediaContainer(title2=sender.itemTitle)

  for (id, title) in sub:
    dir.Append(Function(DirectoryItem(Playlist, title=title, thumb=R(ICON)), id=id, title=title))

  return dir

####################################################################################################
def Playlist(sender, id, title, page=1):
  dir = MediaContainer(viewGroup='InfoList', title2=title)
  content = HTML.ElementFromURL(CATEGORY % (id, page), errors='ignore')

  for video in content.xpath('//section[@id="archiefoverzicht"]/article/a'):
    url = video.get('href')
    title = video.xpath('./h2')[0].text_content().strip()
    date = video.xpath('./p[@class="col"]')[0].text.split(' ', 1)[0]
    summary = video.xpath('./p[2]')[0].text

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=summary, thumb=Function(GetEpisodeThumb, url=url)), url=url))

  # Pagination
  try:
    # Find out how many pages there are in total
    total_pages = re.search('Pagina (\\d+) van (\\d+)', content.xpath('//ul[@id="paginate"]')[0].text_content()).group(2)

    # Add a 'More...' element if there is more than one page with videos
    if page < int(total_pages):
      dir.Append(Function(DirectoryItem(Playlist, title='Meer...', thumb=R(ICON)), id=id, title=title, page=page+1))
  except:
    pass

  return dir

####################################################################################################
def PlayVideo(sender, url):
  video_page = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
  x = re.search("showVideo\('([^']+)','([^']+)'", video_page)
  playlist = XML.ElementFromURL(PLAYLIST % x.group(2))
  url = playlist.xpath('//xspf:track/xspf:identifier[text()="' + x.group(1) + '"]/../xspf:location', namespaces=XSPF_NS)[0].text
  return Redirect(url)

####################################################################################################
def GetThumb(url):
  if url is not None:
    try:
      data = HTTP.Request(url.replace(' ', '%20'), cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      pass
  return Redirect(R(ICON))

####################################################################################################
def GetEpisodeThumb(url):
  try:
    video_page = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK)
    thumb = video_page.xpath('//img[@id="videocover"]')[0].get('src')
  except:
    thumb = None
  return GetThumb(thumb)
