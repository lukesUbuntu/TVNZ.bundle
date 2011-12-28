import re

####################################################################################################

TITLE = 'TVNZ'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

URL_BASE = "http://tvnz.co.nz"
URL_NAVIGATION = "http://tvnz.co.nz/content/ps3_navigation/ps3_xml_skin.xml"
URL_SERVICE = "tvnz://%s"

####################################################################################################

def Start():
  Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")
  Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")

  # Setup the artwork associated with the plugin
  ObjectContainer.art = R(ART)
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = "List"
    
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)

####################################################################################################

@handler('/video/tvnz', TITLE)
def MainMenu():
  oc = ObjectContainer()

  nav = XML.ElementFromURL(URL_NAVIGATION)
  for item in nav.xpath("//MenuItem"):

    title = item.get('title')
    url = item.get('href')
    type = item.get('type')

    if type == "shows":    
      oc.add(DirectoryObject(key = Callback(EpisodeMenu, title = title, url = url), title = title))
    elif type == "alphabetical":
      oc.add(DirectoryObject(key = Callback(AlphabeticalMenu, title = title, url = url), title = title))

  return oc

####################################################################################################

def AlphabeticalMenu(title, url):
  oc = ObjectContainer()

  nav = XML.ElementFromURL(URL_BASE + url)
  for item in nav.xpath("//Letter"):

    title = item.get('label')
    oc.add(DirectoryObject(
      key = Callback(ShowMenu, title = title, url = url, letter = title), 
      title = title))

  return oc

####################################################################################################

def ShowMenu(title, url, letter):
  oc = ObjectContainer()

  nav = XML.ElementFromURL(URL_BASE + url)
  nav_string = "//Letter[@label = '%s']/Show" % letter
        
  for item in nav.xpath(nav_string):

    title = item.get('title')
    url = item.get('href')
    oc.add(DirectoryObject(
      key = Callback(EpisodeMenu, title = title, url = url), 
      title = title))

  return oc

####################################################################################################

def EpisodeMenu(title, url):
  oc = ObjectContainer()

  nav = XML.ElementFromURL(URL_BASE + url)
  for item in nav.xpath("//Episode"):

    ref = item.get('href')
    title = item.get('title')
    subtitle = item.get('sub-title')
    thumb = item.get('src')
    summary = item.text

    episode_details = item.get('episode').split('|')
    episode_details = [ detail.strip() for detail in episode_details ]

    # [Optional] The series and episode number of the video
    series = None
    episode = None
    index_descriptor = episode_details[0]
    try:
      index_dict = re.match("Series (?P<series>[0-9]+), Episode (?P<episode>[0-9]+)", index_descriptor).groupdict()
      series = int(index_dict['series'])
      episode = int(index_dict['episode'])
    except: pass

    # [Optional] The date/time the video was aired
    date = None
    try: date = Datetime.ParseDate(episode_details[1])
    except: pass

    # The duration of the video
    duration_text = episode_details[2]
    duration_dict = re.match("(?P<hours>[0-9]+):(?P<mins>[0-9]+):(?P<secs>[0-9]+)", duration_text).groupdict()
    hours = int(duration_dict['hours'])
    mins = int(duration_dict['mins'])
    secs = int(duration_dict['secs'])
    duration = ((((hours * 60) + mins) * 60) + secs) * 1000
      
    oc.add(EpisodeObject(
      url = URL_SERVICE % ref,
      title = title,
      show = title,
      summary = summary,
      thumb = thumb,
      duration = duration,
      season = series,
      index = episode,
      originally_available_at = date))
      
  return oc