NAME = 'Gamekings'
BASE_URL = 'http://www.gamekings.nl/category/videos/'
TAG_ID = '?tag_id='

####################################################################################################
def Start():

  ObjectContainer.title1 = NAME
  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

####################################################################################################
@handler('/video/gamekings', NAME)
def MainMenu():

  oc = ObjectContainer()
  html = HTML.ElementFromURL(BASE_URL)

  for filter in html.xpath('//ul[@class="filters__list"]/li'):

    id = filter.xpath('./label/input/@value')[0]
    title = filter.xpath('./label/text()')[0].strip()

    oc.add(DirectoryObject(
      key = Callback(Filter, id=id, title=title),
      title = title
    ))

  return oc

####################################################################################################
@route('/video/gamekings/filter/{id}')
def Filter(id, title):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL('%s%s%s' % (BASE_URL, TAG_ID, id))

  for video in html.xpath('//div[@class="postcontainer"]/div[contains(@class, "post")]'):

    url = video.xpath('./a/@href')[0]
    title = video.xpath('./h3[@class="post__title"]/a/text()')[0].strip()
    summary = video.xpath('./p[@class="post__summary"]/text()')[0].strip()
    thumb = video.xpath('./a/img/@data-original')[0]

    date = video.xpath('.//span[@class="meta__item"]/text()')[0]
    date = Datetime.ParseDate(date).date()

    oc.add(VideoClipObject(
      url = url,
      title = title,
      summary = summary,
      thumb = Resource.ContentsOfURLWithFallback(thumb),
      originally_available_at = date
    ))

  return oc
