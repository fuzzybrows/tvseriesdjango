import os, sys

proj_path = "/Users/oreoluwa/Desktop/Projects/tvseriesdownloaddjango"
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
import requests
import re
from tvseriesdownloaddjango import settings
from o2tvseries.models import Show, Season, Episode

headers = {'user-agent': settings.USER_AGENT}


prompts = {1: "Please enter show name: ",
           3: "Please enter the show_name, season and episode number as guided by the prompts"}

def input():
    options = dict([(1, "New Show"),
               (2, "Update Show Repertoire"),
               (3, "Download Specific Episode")])

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
        print (first_letter, 'Group A')
        pageurl = '/a'
    elif first_letter >= 'd' and first_letter < 'g':
        print(first_letter, 'Group D')
        pageurl = '/d'
    elif first_letter >= 'g' and first_letter < 'j':
        print(first_letter, 'Group G')
        pageurl = '/g'
    elif first_letter >= 'j' and first_letter < 'm':
        print (first_letter, 'Group J')
        pageurl = '/j'
    elif first_letter >= 'm' and first_letter < 'p':
        print (first_letter, 'Group M')
        pageurl = '/m'
    elif first_letter >= 'p' and first_letter < 's':
        print (first_letter, 'Group P')
        pageurl = '/p'
    elif first_letter >= 's' and first_letter < 'v':
        print (first_letter, 'Group S')
        pageurl = '/s'
    elif first_letter >= 'v' and first_letter < 'y':
        print (first_letter, 'Group V')
        pageurl = '/v'
    elif first_letter >= 'y':
        print (first_letter, 'Group Y')
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


def get_show_seasons(show_name):
    show_url, _ = get_show_url(show_name)
    tags = get_a_tags(show_url)
    seasons = []
    for tag in tags:
        checker = tag.string and re.search('season\s\d+', tag.string.lower())
        if checker:
            seasons.append((tag.string, tag.get('href')))
    return sorted(seasons, key=lambda x: int(re.search("\d+$", x[0]).group(0)))


def get_episodes(show_name, season):
    """
    Gets the list of episode urls for the supplied show and season
    :param show_name: a string of the show to be downloaded
    :param season: an int of the season to download
    :return: a sorted list of show episode urls
    """
    seasons = get_show_seasons(show_name)
    try:
        season_number = int(season)

    except TypeError as e:
        raise

    try:
        season_home_url = seasons[season_number - 1][1]
    except IndexError as e:
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

def get_referrer_link(episode_url, format='mp4'):
    """
    Method that obtains referrer link of supplied episode
    :param episode_url: url for episode to be downloaded
    :param format: format of episode to be downloaded 3gp/mp4
    :return: a 2-Tuple containing referrer link and filename
    """
    tags = get_a_tags(episode_url)
    result = {}

    for tag in tags:
        if tag.string:
            if tag.string.lower().endswith(format):
                if format == 'mp4':
                    hd = lq = ""
                    if 'HD' in tag.string:
                        hd = (tag.get('href'), tag.string)
                    else:
                        lq = (tag.get('href'), tag.string)
                    result[format] = hd if hd else lq
                else:
                    result[format] = (tag.get('href'), tag.string)
    return result[format]

def download_file(referrer_link, download_path, file_name, show_name, season):
    print referrer_link, download_path, file_name, show_name, season
    folder_path = "{}/{}/{}".format(download_path, show_name, season)
    full_file_save_path = "{}/{}".format(folder_path, file_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, 0o777)

    result = requests.get(str(referrer_link), stream=True, headers=headers)

    with open(full_file_save_path, 'wb') as f:
        file_size = int(result.headers.get('content-length'))
        for chunk in progress.bar(result.iter_content(chunk_size=1024), expected_size=(file_size / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

def download_specific_episode(action_item):
    print prompts[action_item]
    show_name = raw_input("Enter the Show Name eg. 'Arrow': ")
    _, proper_show_name = get_show_url(show_name)
    seasons = get_show_seasons(show_name)
    season_number = raw_input(
        "This show has {no_of_seasons} seasons, Please enter a number from 1 - {no_of_seasons}: ".format(
            no_of_seasons=len(seasons)))
    try:
        season = seasons[int(season_number) - 1][0]

        episodes = get_episodes(show_name, season_number)

        episode_no = raw_input("Please enter the episode No: ")

        episode_no = int(episode_no)

        episode_no = episode_no if len(str(episode_no)) > 1 else '0{}'.format(episode_no)
        for url in episodes:
            if ('Episode' in url[0] and str(episode_no) in url[0]):
                print url, episode_no
        episode_url = [url[1] for url in episodes if ('Episode' in url[0] and str(episode_no) in url[0])][0]
    except:
        print "Invalid Entry, please try again"
        raise
    referrer_link, file_name = get_referrer_link(episode_url)
    download_file(referrer_link, settings.DOWNLOAD_PATH, file_name, proper_show_name, season)


def new_show(input):
    url, _ = get_show_url(input)


if __name__ == "__main__":
    action_item = input()
    if action_item == 1:
        input_value = raw_input(prompts[action_item])
        for episode, url in get_episodes(input_value, 1):
            print get_referrer_link(url, 'mp4')
    elif action_item == 3:
        download_specific_episode(action_item)