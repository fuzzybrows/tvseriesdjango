import os, sys
import random
from urllib import quote
from django.conf import settings

proj_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tvseriesdownloaddjango.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from clint.textui import progress
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
from tvseriesdownloaddjango import settings
from o2tvseries.models import Show, Season, Episode

headers = {'user-agent': settings.USER_AGENT}


prompts = {1: "Please enter show name: ",
           3: "Please enter the show_name, season and episode number as guided by the prompts",
           4: "Please enter show name: "}

def input():
    options = dict([(1, "New Show"),
               (2, "Update Show Repertoire"),
               (3, "Download Specific Episode"),
               (4, "Pre-populate db for single show"),
                (5,"Pre-populate db for all Shows"),
                (6, "Update Show URLs")])

    for num, text in options.iteritems():
        print "{}, {}".format(num, text)

    try:
        action_item = int(raw_input("Please enter a number: "))

        if action_item not in options.keys():
            raise ValueError("Invalid Input Please Try again")
        return action_item

    except:
       raise



def get_show_group_url(input):
    first_letter = input[0][0]
    if first_letter < 'd':
        pageurl = '/a'
    elif first_letter >= 'd' and first_letter < 'g':
        pageurl = '/d'
    elif first_letter >= 'g' and first_letter < 'j':
        pageurl = '/g'
    elif first_letter >= 'j' and first_letter < 'm':
        pageurl = '/j'
    elif first_letter >= 'm' and first_letter < 'p':
        pageurl = '/m'
    elif first_letter >= 'p' and first_letter < 's':
        pageurl = '/p'
    elif first_letter >= 's' and first_letter < 'v':
        pageurl = '/s'
    elif first_letter >= 'v' and first_letter < 'y':
        pageurl = '/v'
    elif first_letter >= 'y':
        pageurl = '/y'
    else:
        raise ValueError("Invalid Entry Please check your response and try again")
    return settings.SOURCE_URL + pageurl


def openurl(url):
    data = requests.get(url, headers=headers)
    return data.content

def get_a_tags(url):
    html = openurl(url)
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a')
    return tags


def get_show_url(show_name):
    """
    Obtains Proper Show Name and Show Index URL
    :param show_name: given name
    :return: 2 tuple of Show Url and Proper Show Name
    """
    show_name_lower = show_name.lower()
    show_name_list = show_name_lower.split(' ')
    show_group_url = get_show_group_url(show_name_list)
    group_home_a_tags = get_a_tags(show_group_url)
    _, last_page_number = find_last_page(group_home_a_tags)

    for page_number in range(1, int(last_page_number) + 1):
        page_url = "{}/page{}.html".format(show_group_url, page_number)
        page_tags = get_a_tags(page_url)
        for tag in page_tags:
            checker = tag.string and show_name_lower and show_name_lower == tag.string.lower()
            if checker:
                return (tag.get('href'), tag.string)
            else:
                checker = tag.string and show_name_list[0] and show_name_list[0] in tag.string.lower()
                if len(show_name_list) > 1:
                    checker = checker and show_name_list[1] and show_name_list[1] in tag.string.lower()
                if len(show_name_list) > 2:
                    checker = checker and show_name_list[2] and show_name_list[2] in tag.string.lower()
                if checker:
                    return (tag.get('href'), tag.string)

    raise ValueError("Show: {} cannot be found at {}".format(show_name, settings.SOURCE_URL))

def find_last_page(index_page_a_tags):
    for item in index_page_a_tags:
        if item.string and item.string.startswith('Last') and re.search("page\d+\.html$", item.get('href')):
            url, page_no = item.get('href'), re.search("page(\d+)\.html$", item.get('href')).group(1)
            return url, page_no
    return None

def get_season_no(x):
    return int(re.search("\d+$", x).group(0))

def get_show_seasons(show_name):
    """
    Gets urls for all the seasons of the supplied Show name
    :param show_name: Name of show to be processed
    :return: a sorted list of 2 Tuples containing Season Name and Season URL
    """
    show_url, proper_show_name = get_show_url(show_name)
    show, _ = Show.objects.get_or_create(title=proper_show_name, active=True, defaults=dict(show_url=show_url))
    tags = get_a_tags(show_url)
    seasons = []
    for tag in tags:
        checker = tag.string and re.search('season\s\d+', tag.string.lower())
        if checker:
            seasons.append((tag.string, tag.get('href')))
    result =  sorted(seasons, key=lambda x: get_season_no(x[0]))
    for season in result:
        s, _ = Season.objects.update_or_create(title=season[0], season_no=get_season_no(season[0]),
                                               season_url=season[1], show=show)
    return result


def get_episodes(show_name, season):
    """
    Gets the list of episode urls for the supplied show and season
    :param show_name: a string of the show to be downloaded
    :param season: an int of the season to download
    :return: a sorted list of show episode urls
    """
    seasons = get_show_seasons(show_name)
    show_url, proper_show_name = get_show_url(show_name)
    show = Show.objects.filter(title=proper_show_name).last()
    try:
        season_number = int(season)

    except TypeError as e:
        raise

    try:
        season_home_url = Season.objects.get(season_no=season_number, show=show).season_url
    except Season.DoesNotExist as e:
        print "{} has no season {}".format(show_name, season_number)
        raise
    tags = get_a_tags(season_home_url)
    last_page_no = find_last_page(tags)
    episodes = []
    last_page_no = 1 if not last_page_no else last_page_no[1]

    for page_number in range(1, int(last_page_no) + 1):
        page_url = "{}/page{}.html".format(season_home_url[:-11], page_number)
        page_tags = get_a_tags(page_url)
        for tag in page_tags:
            checker = tag.string and re.search('episode\s\d+', tag.string.lower())
            if checker:
                episodes.append((tag.string, tag.get('href')))
    return sorted(episodes, key=lambda x: int(re.search("episode\s(\d+)", x[0].lower()).group(1)))

def rand_seed(endpoint=5):
    return random.randrange(1, endpoint)


def construct_download_url(show_name, season_name, filename):
    url = "{protocol}://d{rand_seed}.{domain_name}/" \
          "{show_name}/{season_name}/{filename}".format(protocol=settings.PROTOCOL,
                                                        rand_seed=rand_seed(),
                                                        domain_name=settings.DOMAIN_NAME,
                                                        show_name=show_name,
                                                        season_name=season_name,
                                                        filename=filename)
    return quote(url, safe=":/")

def get_referrer_link(episode_url, show_name, season_name, format='mp4'):
    """
    Method that obtains referrer link of supplied episode
    :param episode_url: url for episode to be downloaded
    :show_name: Name of show
    :season_name: Name/Title of Season eg "Season 01"
    :param format: format of episode to be downloaded 3gp/mp4
    :return: a 2-Tuple containing referrer link and filename
    """
    tags = get_a_tags(episode_url)
    result = {}

    for tag in tags:
        if tag.string:
            if tag.string.lower().endswith(format):
                url = construct_download_url(show_name, season_name, tag.string)
                if format == 'mp4':
                    hd = lq = ""
                    if 'HD' in tag.string:
                        hd = (url, tag.string)
                    else:
                        lq = (url, tag.string)
                    result[format] = hd if hd else lq
                else:
                    result[format] = (url, tag.string)
    return result[format]

def download_file(referrer_link, download_path, file_name, show_name, season_name, download=True):
    """
    Download actual Video File
    :param referrer_link: A string of the Referrer Link to Download
    :param download_path: A string of the Path to Folder where file will be stored
    :param file_name: A string of the Filename for download
    :param show_name: A string of the  Name of Show being processed
    :param season_name: A string of the Season of Show being processed
    :param download: A boolean stating if File should be downloaded or not
    :return:
    """
    folder_path = "{}/{}/{}".format(download_path, show_name, season_name)
    full_file_save_path = "{}/{}".format(folder_path, file_name)

    result = requests.get(str(referrer_link), stream=True, headers=headers)
    file_size = int(result.headers.get('content-length'))

    if download:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.chmod(folder_path, 0o777)

        with open(full_file_save_path, 'wb') as f:
            for chunk in progress.bar(result.iter_content(chunk_size=1024), expected_size=(file_size / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()

    return dict(save_location=folder_path, file_size=file_size)

def download_specific_episode(show_name):
    show_url, proper_show_name = get_show_url(show_name)
    seasons = get_show_seasons(show_name)
    season_number = raw_input(
        "This show has {no_of_seasons} seasons, Please enter a number from 1 - {no_of_seasons}: ".format(
            no_of_seasons=len(seasons)))
    try:
        season_name, season_url = seasons[int(season_number) - 1]

        db_show, show_created = Show.objects.get_or_create(title=proper_show_name, defaults=dict(show_url=show_url))
        db_season, season_created = Season.objects.get_or_create(title=season_name, show=db_show,
                                                                 defaults=dict(season_url=season_url,
                                                                 season_no=int(season_number)))
        episodes = get_episodes(show_name, season_number)

        episode_no = raw_input("Please enter the episode No: ")

        episode_no = int(episode_no)

        episode_no = episode_no if len(str(episode_no)) > 1 else '0{}'.format(episode_no)
        episode_title, episode_url = [url for url in episodes if ('Episode' in url[0] and str(episode_no) in url[0])][0]
    except:
        print "Invalid Entry, please try again"
        raise
    referrer_link, file_name = get_referrer_link(episode_url, proper_show_name, season_name)
    f = download_file(referrer_link, settings.DOWNLOAD_PATH, file_name, proper_show_name, season_name)
    e, _ = Episode.objects.update_or_create(show=db_show, season=db_season, episode_title=episode_title,
                                            episode_url=episode_url, referrer_link=referrer_link,
                                            file_format=file_name[-3:], file_name=file_name, downloaded=True, **f)


def update_repertoire():
    shows = Show.objects.filter(active=True)
    for show in shows:
        get_show_seasons(show.title)
        seasons = Season.objects.filter(show=show)
        for season in seasons:
            db_episodes = [episode.episode_title for episode in Episode.objects.filter(season=season)]
            show_episodes = get_episodes(show.title, season.season_no)
            print show.title, season.title
            for episode in show_episodes:
                if episode[0] not in db_episodes:
                    referrer_link, file_name = get_referrer_link(episode[1], show.title, season.title)
                    print "Downloading {}".format(file_name)
                    d = download_file(referrer_link=referrer_link, download_path=settings.DOWNLOAD_PATH,
                                      file_name=file_name, show_name=show.title, season_name=season.title,
                                      download=True)
                    e, _ = Episode.objects.update_or_create(show=show, season=season, episode_title=episode[0],
                                                            episode_url=episode[1], referrer_link=referrer_link,
                                                            file_format=file_name[-3:], file_name=file_name,
                                                            downloaded=True, **d)
                else:
                    if len(sys.argv) <= 1:
                        print "{} already downloaded".format(episode[0])

def download_single_show(show_name, download=False):
    show_url, proper_show_name = get_show_url(show_name)
    show, _ = Show.objects.get_or_create(title=proper_show_name, active=True)
    if not show.show_url:
        show.show_url = show_url
        show.save()

    seasons = get_show_seasons(show_name)
    for season_name, season_url in seasons:
        print proper_show_name, season_name
        db_season, _ = Season.objects.get_or_create(title=season_name, show=show, defaults=dict(season_url=season_url,
                                                    season_no=get_season_no(season_name)))
        db_episodes = [episode.episode_title for episode in Episode.objects.filter(season=db_season)]
        for episode_title, episode_url in get_episodes(show_name, get_season_no(season_name)):
            if episode_title not in db_episodes:
                referrer_link, file_name = get_referrer_link(episode_url, proper_show_name, season_name)
                print "Downloading {}".format(file_name)
                f = download_file(referrer_link, settings.DOWNLOAD_PATH, file_name, proper_show_name, db_season.title,
                                  download=download)
                e, _ = Episode.objects.update_or_create(show=show, season=db_season, episode_title=episode_title,
                                                        episode_url=episode_url, referrer_link=referrer_link,
                                                        file_format=file_name[-3:], file_name=file_name,
                                                        downloaded=True, **f)
            else:
                print "{} already downloaded".format(episode_title)

def populate_shows(last_updated=None):
    shows = sorted(list(set([show.title for show in Show.objects.all().order_by('title')] + settings.WATCHED_SHOWS)))

    if last_updated:
        try:
            shows = shows[shows.index(last_updated):]
        except:
            print "No show with specified name"
            return

    for show in shows:
        print "Populating {}".format(show)
        download_single_show(show)

def update_urls():
    shows = Show.objects.all()
    for show in shows:
        show_url, _ = get_show_url(show.title)
        if str(show_url) != str(show.show_url):
            print "Updating {}".format(show.title)
            seasons = get_show_seasons(show.title)
            for season_title, season_url in seasons:
                s = Season.objects.get(show=show, title=season_title)
                s.season_url = season_url
                s.save()
        show.show_url = show_url
        show.save()
    print "Show URLs updated"


def start_program():
    print "Program Started at {}".format(datetime.now())
    action_item = int(sys.argv[1]) if len(sys.argv) > 1 else input()
    if action_item == 1:
        start_time = datetime.now()
        download_single_show(raw_input(prompts[action_item]), download=True)
        duration = datetime.now() - start_time
    elif action_item == 2:
        start_time = datetime.now()
        update_repertoire()
        duration = datetime.now() - start_time
    elif action_item == 3:
        print prompts[action_item]
        start_time = datetime.now()
        download_specific_episode(raw_input("Enter the Show Name eg. 'Arrow': "))
        duration = datetime.now() - start_time
    elif action_item == 4:
        start_time = datetime.now()
        download_single_show(raw_input(prompts[action_item]))
        duration = datetime.now() - start_time
    elif action_item == 5:
        start_time = datetime.now()
        populate_shows()
        duration = datetime.now() - start_time
    elif action_item == 6:
        start_time = datetime.now()
        update_urls()
        duration = datetime.now() - start_time
    print "Task Duration: {}".format(duration)

if __name__ == "__main__":
    start_program()