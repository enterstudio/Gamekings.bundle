NAME = 'Gamekings'
BASE_URL = 'http://www.gamekings.tv'
VIDEO = '%s/videos' % BASE_URL
CATEGORY = '%s/category/%%s/page/%%d' % BASE_URL

RE_NEXT_PAGE = Regex('Pagina (\\d+) van (\\d+)')

####################################################################################################
def Start():

  ObjectContainer.title1 = NAME
  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'

####################################################################################################
@handler('/video/gamekings', NAME)
def MainMenu():

  oc = ObjectContainer()

  # The first list option is different from the rest (it's missing the "class" attribute)
  oc.add(DirectoryObject(
    key = Callback(Playlist, id='videos', category_title='Alle video\'s'),
    title = 'Alle video\'s'
  ))

  # All top level menu items
  list = HTML.ElementFromURL(VIDEO).xpath('//select[@id="cat"]/option[@class="level-0"]')

  for item in list:
    id = item.get('value')
    title = item.xpath('./text()')[0].strip()

    # Check to see if an item has 'sub'-items (siblings with class="level-1")
    if len(item.xpath('./following-sibling::*')) == 0 or item.xpath('./following-sibling::*/@class')[0] == 'level-0':
      oc.add(DirectoryObject(
        key = Callback(Playlist, id=id, category_title=title),
        title = title
      ))
    else:
      siblings = item.xpath('./following-sibling::*')
      sub = []

      for s in siblings:
        sib_id = s.get('value')
        sib_title = s.xpath('./text()')[0].strip()
        sib_level = s.get('class')

        if sib_level == 'level-0':
          break
        else:
          sub.append([sib_id, sib_title])

      oc.add(DirectoryObject(
        key = Callback(Subcategory, sub=sub, category_title=title),
        title = title
      ))

  return oc

####################################################################################################
@route('/video/gamekings/category', sub=list)
def Subcategory(sub, category_title):

  oc = ObjectContainer(title2=category_title)

  for (id, title) in sub:
    oc.add(DirectoryObject(
      key = Callback(Playlist, id=id, category_title=title),
      title = title
    ))

  return oc

####################################################################################################
@route('/video/gamekings/playlist', page=int)
def Playlist(id, category_title, page=1):

  oc = ObjectContainer(title2=category_title)
  content = HTML.ElementFromURL(CATEGORY % (id, page))

  for video in content.xpath('//section[@id="archiefoverzicht"]/article/a'):
    url = video.get('href')

    if '/videos/' not in url:
      continue

    try:
      title = video.xpath('./h2/text()')[0].strip()
    except:
      title = video.xpath('./h2')[0].text_content().strip()

    summary = video.xpath('./p[2]')[0].text
    date = video.xpath('./p[@class="col"]')[0].text.split(' ', 1)[0]
    date = Datetime.ParseDate(date).date()
    thumb = video.xpath('./img/@src')[0].replace(' ', '%20')

    if '-75x75' in thumb:
      thumb = '%s.jpg' % thumb.rsplit('-75x75')[0]

    oc.add(VideoClipObject(
      url = url,
      title = title,
      summary = summary,
      originally_available_at = date,
      thumb = Resource.ContentsOfURLWithFallback(thumb)
    ))

  # Pagination
  try:
    # Find out how many pages there are in total
    total_pages = RE_NEXT_PAGE.search(content.xpath('//ul[@id="paginate"]')[0].text_content()).group(2)

    # Add a 'More...' element if there is more than one page with videos
    if page < int(total_pages):
      oc.add(NextPageObject(
        key = Callback(Playlist, id=id, category_title=category_title, page=page+1),
        title = 'Meer...'
      ))
  except:
    pass

  return oc
