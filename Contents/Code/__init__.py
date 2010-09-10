import re
from base64 import b64decode

####################################################################################################

PLUGIN_TITLE                    = 'Gamekings'
PLUGIN_PREFIX                   = '/video/gamekings'

BASE_URL                        = 'http://www.gamekings.tv'
VIDEO_CATEGORIES                = '%s/index/category/videos/' % BASE_URL
VIDEOS                          = '%s/wp-content/themes/default/filter-latest.php?Acat=%%s&page=%%s' % BASE_URL

# Default artwork and icon(s)
PLUGIN_ARTWORK                  = 'art-default.png'
PLUGIN_ICON_DEFAULT             = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1         = PLUGIN_TITLE
  MediaContainer.viewGroup      = 'List'
  MediaContainer.art            = R(PLUGIN_ARTWORK)

  # Set the default cache time
  HTTP.CacheTime = 1800
  HTTP.Headers['User-agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.4) Gecko/20100611 Firefox/3.6.4'

####################################################################################################

def MainMenu():
  dir = MediaContainer()

  # The first list option is different from the rest (it misses the "class" attribute and has a wrong videoId (-1, while the real videoId for "All videos" is 3)
  dir.Append(Function(DirectoryItem(Playlist, title='Alle video\'s', thumb=R(PLUGIN_ICON_DEFAULT)), id=3, title='Alle video\'s'))

  # All top level menu items
  list = HTML.ElementFromURL(VIDEO_CATEGORIES, errors='ignore').xpath('//select[@id="cat"]/option[@class="level-0"]')

  for menuitem in list:
    id    = menuitem.get('value')
    title = menuitem.xpath('./text()')[0].strip()

    # Check to see if an item has 'sub'-items (siblings with class="level-1")
    if len(menuitem.xpath('./following-sibling::*')) == 0 or menuitem.xpath('./following-sibling::*')[0].get('class') == 'level-0':
      dir.Append(Function(DirectoryItem(Playlist, title=title, thumb=R(PLUGIN_ICON_DEFAULT)), id=id, title=title))
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

      dir.Append(Function(DirectoryItem(Sub, title=title, thumb=R(PLUGIN_ICON_DEFAULT)), title=title, sub=sub))

  return dir

####################################################################################################

def Sub(sender, title, sub):
  dir = MediaContainer(title2=title)

  for item in sub:
    dir.Append(Function(DirectoryItem(Playlist, title=item[1], thumb=R(PLUGIN_ICON_DEFAULT)), id=item[0], title=item[1]))

  return dir

####################################################################################################

def Playlist(sender, id, title, page=1):
  dir = MediaContainer(viewGroup='Details', title2=title)

  content = HTML.ElementFromURL(VIDEOS % (id, page), errors='ignore')
  vids = content.xpath('//a[@class="filterlist"]')

  for video in vids:
    link        = video.get('href')
    title       = video.xpath('./b/text()')[0].strip()

    # Change date notation to 'day-month-year' (Dutch)
    date        = video.xpath('./small[not(@class="excerpt")]/text()')[0].strip().split(' | ')[0].split('-')
    date        = date[1] + '-' + date[0] + '-' + date[2]

    description = ' '.join( video.xpath('./small[@class="excerpt"]/*/text()') ).strip()
    thumb       = video.xpath('./img[@class="reviewpic"]')[0].get('src').replace(' ', '%20')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, thumb=BASE_URL + thumb), link=link))

  # Pagination
  # Past all text nodes from witihn the DIV 'Ajax-pager' together...
  pages = ' '.join( content.xpath('//div[@id="Ajax-pager"]/text()') ).strip()

  # ...and find out how many pages there are in total
  totalPages = re.search(' van (\\d+)', pages).group(1)

  # Add a 'More...' element if there is more than one page with videos
  if page < int(totalPages):
    dir.Append(Function(DirectoryItem(Playlist, title='Meer...', thumb=R(PLUGIN_ICON_DEFAULT)), id=id, title=title, page=page+1))

  return dir

####################################################################################################

def PlayVideo(sender, link):
  playerHtml = HTTP.Request(link, errors='ignore').content

  # Find the id of the video
  videoId = re.search('playlist2\.php\?id=(.+)\'\)', playerHtml).group(1)
  video   = b64decode( videoId ).split(',')
  url     = (video[2] + video[0]).replace(' ', '%20')

  return Redirect(url)
