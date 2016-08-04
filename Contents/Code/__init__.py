NAME = 'Gamekings'
BASE_URL = 'http://www.gamekings.nl/category/videos/page/%d/'

####################################################################################################
def Start():

  ObjectContainer.title1 = NAME
  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

####################################################################################################
@handler('/video/gamekings', NAME)
def MainMenu():

  return Videos()

####################################################################################################
@route('/video/gamekings/videos', page=int)
def Videos(page=1):

  oc = ObjectContainer()
  html = HTML.ElementFromURL(BASE_URL % (page))

  for video in html.xpath('//div[@class="postcontainer"]/div[contains(@class, "post")]'):

    title = video.xpath('./h3[contains(@class, "post__title") and not(contains(@class, "premium"))]/a/text()')

    if len(title) < 1:
        continue

    url = video.xpath('./a/@href')[0]
    summary = video.xpath('./p[@class="post__summary"]/text()')[0].strip()
    thumb = video.xpath('./a/img/@data-original')[0]

    date = video.xpath('.//span[@class="meta__item"]/text()')[0]
    date = Datetime.ParseDate(date).date()

    oc.add(VideoClipObject(
      title = title[0].strip(),
      url = url,
      summary = summary,
      thumb = Resource.ContentsOfURLWithFallback(thumb),
      originally_available_at = date
    ))

  if page < 50:

    oc.add(NextPageObject(
      key = Callback(Videos, page=page+1),
      title = "Meer video's..."
    ))

  return oc
