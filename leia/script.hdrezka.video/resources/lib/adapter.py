#!/usr/bin/python
# coding: utf-8

########################

import xbmc
import xbmcgui
import requests
import datetime
import locale
import re
from urllib import urlencode
from bs4 import BeautifulSoup
from resources.lib.helper import *


########################

ACCEPT_TAGS = {
                'рейтинги' : 'rating',
                'входит в списки' : 'list',
                'дата выхода' : 'release_date',
                'страна' : 'country',
                'режиссер' : 'director',
                'жанр' : 'genre',
                'время' : 'runtime',
                'из серии' : 'series',
                'возраст' : 'ages',
                'слоган':'tagline',
                'кинопоиск':'kinopoisk',}

########################


class HDRVideos(object):
    def __init__(self,call_request):
        self.result = {}
        self.call = call_request['call']
        self.rezka_id = call_request['dataid']
        self.url = call_request['url']
        self.tvshow = False

        if self.rezka_id:
            cache_key = self.call + str(self.rezka_id)
            self.details = get_cache(cache_key)

            if not self.details:
                self.details = rezka_movie_details(action=self.call,
                                          call=self.url,
                                          rezka_id=self.rezka_id,
                                          show_error=True
                                          )

                #log(self.details,json=True)

                write_cache(cache_key, self.details,cache_time=0.1)

            if not self.details:
                return

            self.result['details'] = self.get_details() #!!!!!
            self.result['cast'] = self.get_persons(self.details['cast'])
            try: self.result['director'] = self.get_persons(self.details['director'])
            except: pass
            self.result['seasons'] = self.details.get('seasons',{})


            winprop('script.hdrezka.video-post_id', str(self.rezka_id))
            winprop('script.hdrezka.video-post_url', self.url)
            winprop('script.hdrezka.video-ctrl_favs', self.details.get('ctrl_favs',"0"))
            
            winprop('script.hdrezka.video-translators.json', self.details.get('translators',{}))
            winprop('script.hdrezka.video-translator_id', self.details.get('translator_id',"0"))
            winprop('script.hdrezka.video-translator_initial_id', self.details.get('translator_id',"0"))
            
            winprop('script.hdrezka.video-episode_id', self.details.get('episode_id',"0_0"))
            winprop('script.hdrezka.video-episode_initial_id', self.details.get('episode_id',"0_0"))
            
            winprop('script.hdrezka.video-playlist.json', self.details.get('play_links',{}))
            winprop('script.hdrezka.video-resolution', self.details.get('resolution',"0"))
            winprop('script.hdrezka.video-pref_resolution', DEFAULT_RESOLUTION)



    def __getitem__(self, key):
        return self.result.get(key, '')

    def get_details(self):
        li = list()
        list_item = rezka_handle_movie(self.details,full_info=True)
        li.append(list_item)
        return li

    def get_persons(self,persons):
        li = list()
        for item in persons:
            item['label2'] = item.get('original_name', '')
            list_item = rezka_handle_credits(item)
            li.append(list_item)

        return li


    def get_seasons(self):
        seasons = self.details.get('seasons')
        li = list()
        if seasons:
            for s,e in seasons:
                if len(e) == 0:
                    continue
                list_item = rezka_handle_seasons(s,e)
                li.append(list_item)
        return li


    def get_yt_videos(self):
        cache_key = 'ytvideos' + str(self.rezka_id)
        videos = get_cache(cache_key)
        li = list()

        if not videos:
            videos = self.details['videos']['results']

            ''' Add EN videos next to the user configured language
            '''
            if DEFAULT_LANGUAGE != FALLBACK_LANGUAGE:
                videos_en = tmdb_query(action=self.call,
                                        call=self.rezka_id,
                                        get='videos',
                                        use_language=False
                                        )

                videos_en = videos_en.get('results')
                videos = videos + videos_en

            ''' Check online status of all videos to prevent dead links
            '''
            online_videos = []
            for item in videos:
                request = requests.head('https://img.youtube.com/vi/%s/0.jpg' % str(item['key']))
                if request.status_code == requests.codes.ok:
                    online_videos.append(item)

            videos = online_videos
            write_cache(cache_key, videos)

        for item in videos:
            if item['site'] == 'YouTube':
                list_item = tmdb_handle_yt_videos(item)
                if not list_item == 404:
                    li.append(list_item)

        return li

########################

class Reader(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36' })

    def get(self,url,r_json=False,show_error=False):
        
        try:
            response = None

            for i in range(1,4): # loop if heavy server load
                try:
                    response = self.session.get(url, timeout=10)

                    if str(response.status_code).startswith('5'):
                        raise Exception(str(response.status_code))
                    else:
                        break

                except Exception:
                    xbmc.sleep(500)

            if not response or response.status_code == 404:
                error = ADDON.getLocalizedString(32019)
                raise Exception(error)

            elif response.status_code == 401:
                error = ADDON.getLocalizedString(32022)
                raise Exception(error)

            elif not response.ok:
                raise Exception('Code ' + str(response.status_code))

            if r_json:
                result = response.json()
            else:
                result = BeautifulSoup(response.text, "html.parser")
                result.prettify()

            if show_error:
                if len(result) == 0 or ('results' in result and not len(result['results']) == 0):
                    error = ADDON.getLocalizedString(32019)
                    raise Exception(error)

            return result

        except Exception as error:
            log('%s --> %s' % (error, url), ERROR)
            if show_error:
                rezka_error(error)

    def post(self,url,payload={},json=False,show_error=False):
        try:
            response = None

            for i in range(1,4): # loop if heavy server load
                try:
                    response = self.session.post(url, data=payload, timeout=10)

                    if str(response.status_code).startswith('5'):
                        raise Exception(str(response.status_code))
                    else:
                        break

                except Exception:
                    xbmc.sleep(500)

            if not response or response.status_code == 404:
                error = ADDON.getLocalizedString(32019)
                raise Exception(error)

            elif response.status_code == 401:
                error = ADDON.getLocalizedString(32022)
                raise Exception(error)

            elif not response.ok:
                raise Exception('Code ' + str(response.status_code))
            
            if json:
                result = response.json()
            else:
                result = BeautifulSoup(response.text, "html.parser")
                result.prettify()

            if show_error:
                if len(result) == 0 or ('results' in result and not len(result['results']) == 0):
                    error = ADDON.getLocalizedString(32019)
                    raise Exception(error)

            return result

        except Exception as error:
            log('%s --> %s' % (error, url), ERROR)
            if show_error:
                rezka_error(error)

########################

reader = Reader()


def rezka_list(action,call=None,get=None,params=None,show_error=False):
    
    result = {"page": 1, "total_pages": 1, "results": []}

    if call != 'search':
        page = None
        if params['page']:
            page = 'page/{}/'.format(params['page'])
            del params['page']

        action = action if action != 'movie' else 'films'
        
        url = urljoin(API_URL, action, call, get, page)
    else:
        #search/?do=search&subaction=search&q=a+b&page=3
        url = urljoin(API_URL, action)
    
    if params:  url = '{0}?{1}'.format(url, urlencode(params))
    else:  url = '{0}/'.format(url)

    #log('rezka_list url = {}'.format(url))

    try:
        
        soup = reader.get(url)
        
        try:
            pCont = soup.find("div", class_="b-navigation")
            try: totP = int(pCont.find_all('a')[-2].text.strip())
            except: totP = 1
            try: curP = [int(el.text.strip()) for el in pCont.find_all('span') if not el.has_attr('class')][0]
            except: curP = 1
            if curP > totP: totP = curP
            result["page"] = curP
            result["total_pages"] = totP
        except: pass
            

        container = soup.find("div", class_="b-content__inline_items")
        items = container.find_all("div",attrs={"data-id":True,"data-url":True})
        for item in items:
            label = {}
            label['id'] = item["data-id"].strip()
            label['url'] = item["data-url"].strip().replace('/','^')
            label['img'] = item.find('img')["src"]
            sc = item.find("div", class_='b-content__inline_item-link')
            label['title'] = sc.find('a').text.strip()
            yc = [e.replace('- ...','').strip() for e in sc.find('div').text.strip().split(',')]
            dig = [d for d in yc if d.isnumeric()]
            
            if len(dig) > 0:
                label['release_date'] = dig[0]
                yc.remove(dig[0])
                
            label['genre'] = yc[-1]
            yc.remove(yc[-1])
            
            label['country'] = ', '.join(yc)

            result["results"].append(dict(label))


        if show_error:
            if len(result) == 0 or ('results' in result and not len(result['results']) == 0):
                error = ADDON.getLocalizedString(32019)
                raise Exception(error)

        return result

    except Exception as error:
        log('%s --> %s' % (error, url), ERROR)
        if show_error:
            rezka_error(error)

def rezka_collections(show_error=False):

    cache_key = 'widgetHDrezkaCollectionsMenu'

    menu = get_cache(cache_key)

    if not menu or not len(menu)>0:

        menu = []
        page = 1
       
        url = "%s/collections/page/%s/" % (API_URL, page)

        #log('rezka_list url = {}'.format(url))

        def get_list(src):
            list_=[]
            for item in src.find_all("div", class_="b-content__collections_item"):
                i = {
                      'name': item.find('a').text.strip(),
                      'call': [el.strip() for el in item["data-url"].strip().split('/') if el.strip()][-1],
                      'icon': item.find('img')["src"],
                    }
                list_.append(i)

            return list_

        try:
            soup = reader.get(url)
            menu = get_list(soup)
            pCont = soup.find("div", class_="b-navigation")
            try: page = int(pCont.find_all('a')[-2].text.strip())
            except: page = 1
        except Exception as error:
            log('%s --> %s' % (error, url), ERROR)
            if show_error:
                rezka_error(error)

        if page > 1:

            for p in range(2,page+1):
                try:
                    url = "%s/collections/page/%s/" % (API_URL, p)
                    soup = reader.get(url)
                    menu.extend(get_list(soup))
                    xbmc.sleep(500)
                except Exception as error:
                    log('%s --> %s' % (error, url), ERROR)
                    if show_error:
                        rezka_error(error)

    if menu and len(menu) > 0:
        write_cache(cache_key,menu,3)

    return menu
        
            

def rezka_handle_movie_list(item):
    icon = item['img'] if item['img'] is not None else ''
    list_item = xbmcgui.ListItem(label=item['title'])
    list_item.setInfo('video', {'title': item['title'],
                                'dbid': item.get('id', ''),
                                'imdbnumber': item['url'],
                                'premiered': item.get('release_date', ''),
                                'country': item.get('country', ''),
                                'genre': item.get('genre', ''),
                                'mediatype': 'movie'}
                                 )
    list_item.setArt({'icon': 'DefaultVideo.png', 'thumb': icon, 'poster': icon, 'fanart': icon})

    return list_item


#def rezka_handle_episode_links(post_id,idt,season_id,episode_id,ctrl_favs):
def rezka_handle_episode_links(season_id,episode_id):
    log("*** rezka_handle_episode_links")
    try:
        post_id = winprop('script.hdrezka.video-post_id')
        ctrl_favs = winprop('script.hdrezka.video-ctrl_favs')
        idt = winprop('script.hdrezka.video-translator_id')
        
        data = {
            "id": post_id,
            "translator_id": idt,
            "season": season_id,
            "episode": episode_id,
            "favs":ctrl_favs,
            "action": "get_stream"
        }

        mt = int(time.time() * 1000)
        url = '{0}/ajax/get_cdn_series/?t={1}'.format(API_URL.rstrip('/'),mt)
        
        response = reader.post(url,data,True,show_error=True)

        if response["success"] == True:
            log('is True')
        else:
            log('is False')
        
        if response["success"]:
            return rezka_handle_extract_links(response["url"])
        else:
            return {}
        
    except Exception as error:
        log('%s --> %s' % (error, 'rezka_handle_episode_links'), ERROR)

def rezka_handle_translator_links():
    log("*** rezka_handle_translator_links")
    try:
        post_id = winprop('script.hdrezka.video-post_id')
        ctrl_favs = winprop('script.hdrezka.video-ctrl_favs')
        idt = winprop('script.hdrezka.video-translator_id')
        camrip = 0
        director = 0
        ads = 0
        for _, i in winprop('script.hdrezka.video-translators.json').items():
            if i['id'] == idt:
                camrip = i['camrip']
                director = i['director']
                break

        if winprop('script.hdrezka.video-episode_id') == "0_0":
            data = {
                "id": post_id,
                "translator_id": idt,
                "is_camrip": camrip,
                "is_ads": ads,
                "is_director": director,
                "favs":ctrl_favs,
                "action": "get_movie"
            }
        else:
            data = {
                "id": post_id,
                "translator_id": idt,
                "favs":ctrl_favs,
                "action": "get_episodes"
            }
       
        mt = int(time.time() * 1000)
        url = '{0}/ajax/get_cdn_series/?t={1}'.format(API_URL.rstrip('/'),mt)

        response = reader.post(url,data,True,show_error=True)

        if response["success"]:
            return rezka_handle_extract_links(response["url"])
        else:
            return {}
        
    except Exception as error:
        log('%s --> %s' % (error, 'rezka_handle_translator_links'), ERROR)


def rezka_handle_extract_links(src):
    urls = {}
    for l in src.split(','):
        t = l.split(']')
        res = t[0].replace('[','').strip()
        for t in t[-1].split('or'):
            t = t.strip().replace('\\','')
            if t[-4:].lower() == '.mp4':
                urls[res] = t
                break
    return urls


def rezka_movie_details(action=None,call=None,rezka_id=None,show_error=False):
    log('rezka_movie_details')
    log('action = %s' %action)

    details = {}

    soup = reader.get(call)
    content = soup.find("div", class_="b-content__main")

    details['ctrl_favs'] = soup.find('input', id='ctrl_favs')['value']

    details['dbid'] = rezka_id
    details["image"] = content.find("img",attrs={"itemprop":"image"})["src"].strip()
    details["cover"] = content.find('a',attrs={'data-imagelightbox':"cover"})['href'].strip()
    details["title"] = content.find('div', class_='b-post__title').text.strip()
    try: details["original_title"] = content.find('div', class_='b-post__origtitle',attrs={"itemprop":"alternativeHeadline"}).text.strip()
    except: details["original_title"] = ''
    details["overview"] = content.find('div', class_='b-post__description_text').text.strip()

    try:
        keys = list(ACCEPT_TAGS.keys())
        for tr in content.find('table', class_='b-post__info').find_all('tr'):
            td = tr.find_all('td')
            if len(td) > 1:
                try:  pref = td[0].text.replace(':','').strip().lower()
                except: pref = ''
                if pref in keys:
                    ttl = ACCEPT_TAGS[pref]
                    if ttl == 'director':
                        details[ttl] = []
                        o = 0
                        for span in td[1].find('div',class_='persons-list-holder').find_all('span',class_='person-name-item'):
                            name = span.text.strip()
                            try: data_id = span['data-id']
                            except: data_id = None
                            try:
                                href = span.find('a')['href']
                                actInfo = getPersonInfo(href)
                                details['director'].append(
                                        {
                                            "order": o,
                                            "name":actInfo['name'],
                                            "original_name":actInfo['original_name'],
                                            "profile_path":actInfo['profile_path'],
                                            "id": data_id})
                            except:
                                details['director'].append(
                                        {
                                            "order": o,
                                            "name":name,
                                            "original_name":name,
                                            "profile_path":None,
                                            "id": data_id})
                            o += 1

                    elif ttl == 'rating':
                        details['rating'] = {}
                        rates=[]
                        votes = 0
                        score = 0
                        for span in td[1].find_all('span', class_='b-post__info_rates'):
                            rid = span.find('a').text.strip().lower()
                            if rid in keys: rid = ACCEPT_TAGS[rid]
                            cRate = float(span.find('span').text.replace(' ','').strip())
                            cVote = int(span.find('i').text.replace('(','').replace(')','').replace(' ','').strip())
                            rates.append(cRate)
                            votes += cVote
                            details['rating'][rid] = '{0} ({1})'.format(cRate,cVote)
                        details['vote_average'] = "{:.1f}".format(sum(rates)/len(rates))
                        details['vote_count'] = str(votes) 
                        
                    elif ttl == 'list':
                        details[ttl] = []
                        for a in td[1].find_all('a'): details[ttl].append(a.text.strip())
                    elif ttl == 'series':
                        details[ttl] = []
                        for a in td[1].find_all('a'): details[ttl].append(a.text.strip())
                    elif ttl in ['country','genre']:
                        details[ttl] = [el.strip() for el in td[1].text.strip().split(',') if el.replace('.','').strip() != '']
                    else:
                        details[ttl] = td[1].text.strip()
            else:
                o = 0
                for act in td[0].find('div',class_='persons-list-holder').find_all('span',class_='item')[1:-1]:
                    if not 'cast' in list(details.keys()): details['cast'] = []
                    
                    try:
                        span = act.find('span',class_="person-name-item")
                        data_id = span['data-id']
                    except: data_id = None
                    name = act.text.strip()
                    try:
                        href = act.find('a')['href']
                        actInfo = getPersonInfo(href)
                        details['cast'].append(
                                {
                                    "order": o,
                                    "name":actInfo['name'],
                                    "original_name":actInfo['original_name'],
                                    "profile_path":actInfo['profile_path'],
                                    "id": span['data-id']}
                            )
                    except:
                        details['cast'].append(
                                    {
                                        "order": o,
                                        "name":name,
                                        "original_name":name,
                                        "profile_path": None,
                                        "id": span['data-id']}
                                )
                    o += 1


        try: 
            details['runtime'] = int([d.strip() for d in details['runtime'].strip().split(' ') if d.strip()][0])
        except:
            details['runtime'] = 0

        try:
            details['release_date'] = details['release_date'].split('го')[0].strip()
        except:
            details['release_date'] = ''

        idt = "0"
        script = ""
        try: idt = content.find('li', class_='b-translator__item active')["data-translator_id"]
        except: pass

        try:
            for el in soup.find_all('script'):
                if str(el).find("initCDNSeriesEvents") > -1:
                    script = str(el)
                    idt = script.split("initCDNSeriesEvents")[-1].split("{")[0]
                    idt = idt.split(",")[1].strip()
                elif str(el).find("initCDNMoviesEvents") > -1:
                    script = str(el)
                    idt = script.split("initCDNMoviesEvents")[-1].split("{")[0]
                    idt = idt.split(",")[1].strip()
        except: pass

        details['translator_id'] = idt
        details['translators'] = {}
        for li in content.find_all('li', class_='b-translator__item'):
            try: camrip = li["data-camrip"].strip()
            except: camrip = "0"
            try: director = li["data-director"].strip()
            except: director = "0"
            details['translators'][li.text.strip()] = {'id':li["data-translator_id"].strip(),
                                                       'camrip': camrip,
                                                       'director': director}
        
            
        subtitles = None

        details['episode_id'] = "0_0"
        tvshow = content.find("div", id="simple-episodes-tabs")
        if tvshow:
            
            details['seasons'] = {}
                
            for li in tvshow.find_all("li", class_="b-simple_episode__item"):
                
                season = li['data-season_id'].strip()
                episode = li['data-episode_id'].strip()

                if 'active' in li['class']:
                    details['episode_id'] = "{0}_{1}".format(season,episode)
                
                if not season in list(details['seasons'].keys()):
                    details['seasons'][season] = []
                    
                details['seasons'][season].append(episode)

        details["play_links"] = getMovieLink(script)
        
        details['full_plot'] = fullPlot(details)

        log(details,json=True,force=True)

        return details
                    
    except Exception as error:
        log('%s --> %s' % (error, call), ERROR)
        if show_error:
            rezka_error(error)

def fullPlot(details):
    info = []
    info.append(details["overview"])
    series = details.get('series',[])
    list_ = details.get('list',[])
    if len(series) > 0: info.append('[COLOR FF12A0C7][B]{0}:[/B][/COLOR][CR]{1}'.format(ADDON.getLocalizedString(32165),rezka_join_items(series)))
    if len(list_) > 0: info.append('[COLOR FF12A0C7][B]{0}:[/B][/COLOR][CR]{1}'.format(ADDON.getLocalizedString(32166),rezka_join_items(list_)))
    #if len(info) > 1 : info.insert(1,'')
    return '[CR][CR]'.join(info)
    


def getPersonInfo(url):
    res = None
    try:
        res = {}
        soup = reader.get(url)
        ttl = soup.find("div", class_="b-post__title")
        res['name'] = ttl.find("span",attrs={"itemprop":"name"}).text.strip()
        res['original_name'] = ttl.find("span",attrs={"itemprop":"alternativeHeadline"}).text.strip()
        idiv = soup.find("div", class_='b-sidecover')
        try: res['profile_path'] = idiv.find('a',attrs={'data-imagelightbox':"cover"})['href'].strip()
        except: res['profile_path'] = idiv.find("img",attrs={"itemprop":"image"})["src"].strip()
    except:pass
    return res


def getMovieLink(script=None):
    urls = {}
    try:
        if script:
            e = '^'
            pattern = ['^streams^',':',e,e]
            #raw = script.text.replace('"',e).replace("'",e)
            raw = script.replace('"',e).replace("'",e)
            for i in range(len(pattern)):
                idx = raw.find(pattern[i])+len(pattern[i])
                raw = raw[idx:] if i < len(pattern)-1 else raw[:idx]

            if raw != script:
                urls = rezka_handle_extract_links(raw[:-1])

    except: pass

    return urls


def rezka_handle_credits(item):
    icon = item['profile_path'] if item['profile_path'] is not None else ''
    list_item = xbmcgui.ListItem(label=item['name'])
    list_item.setLabel2(item['label2'])
    list_item.setArt({'icon': 'DefaultActor_.png', 'thumb': icon, 'poster': icon})
    list_item.setProperty('id', str(item.get('id', '')))

    return list_item

def rezka_handle_seasons(season,episodes):
    season_item = xbmcgui.ListItem(label='s{0}'.format(season))
    season_item.setProperty('season_num',season)
    eLi = []
    for e in episodes:
        episode_item = xbmcgui.ListItem(label='e{0}'.format(e))
        episode_item.setProperty('episode_num',e)
        eLi.append(episode_item)
        
    season_item.setEpisodes(eLi)

    return season_item

def rezka_handle_movie(item,full_info=False,mediatype='movie'):
    #log(item,json=True)
    icon = item['image'] if item['image'] is not None else ''
    backdrop = item['cover'] if item['cover'] is not None else ''

    label = item['title'] or item['original_title']
    originaltitle = item.get('original_title', '')
    duration = item.get('runtime') * 60 if item.get('runtime', 0) > 0 else ''

    premiered = item.get('release_date')
    if premiered in ['2999-01-01', '1900-01-01']:
        premiered = ''

    ratingDetails = item.get('rating', {}) 
        
    resolutions = list(item['play_links'].keys())

    is_playable = '1' if len(item['play_links'])>0 else ''

    list_item = xbmcgui.ListItem(label=label)
    list_item.setInfo('video', {'title': label,
                                'originaltitle': originaltitle,
                                'rating': item.get('vote_average', ''),
                                'votes': int(item.get('vote_count', 0)),
                                'tagline': item.get('tagline', ''),
                                'duration': duration,
                                'plot': item.get('overview', '').replace('&amp;', '&').strip(),
                                'country': rezka_join_items(item.get('country', '')),
                                'genre': rezka_join_items(item.get('genre', '')),
                                'mediatype': mediatype}
                                 )
    list_item.setArt({'icon': 'DefaultVideo.png', 'thumb': icon, 'poster': icon, 'fanart': backdrop})
    list_item.setProperty('id', str(item.get('id', '')))
    list_item.setProperty('play', is_playable)
    list_item.setProperty('resolution', '720p') #!!!
    list_item.setProperty('rating.imdb', ratingDetails.get('imdb', ''))
    list_item.setProperty('rating.kinopoisk', ratingDetails.get('kinopoisk', ''))
    list_item.setProperty('country', rezka_join_items(item.get('country', '')))
    list_item.setProperty('release', item.get('release_date',''))
    list_item.setProperty('ages', item.get('ages',''))
    list_item.setProperty('full_plot', item.get('full_plot',''))
    list_item.setProperty('call', 'movie')

    return list_item


def rezka_join_items_by(item,key_is,value_is,key='name'):
    values = []
    for value in item:
        if value[key_is] == value_is:
            values.append(value[key])

    return get_joined_items(values)

def rezka_join_items(item):
    if isinstance(item,list):
        return get_joined_items(item)
    else:
        return item


def handle_resolution():
    pl = winprop('script.hdrezka.video-playlist.json')
    if len(pl) > 0:
        aRes = list(pl.keys())

        res_value = winprop('script.hdrezka.video-pref_resolution')

        if res_value not in aRes:
            clRes = closestResolution(res_value,aRes)
            if clRes:
                winprop('script.hdrezka.video-resolution', clRes)
            else:
                winprop('script.hdrezka.video-resolution', '0')
        else:
            winprop('script.hdrezka.video-resolution', res_value)
    else:
        winprop('script.hdrezka.video-resolution', '0')

    set_resolution()

def set_resolution():
    if winprop('script.hdrezka.video-resolution') != '0':
        xbmc.executebuiltin('SetProperty(script.hdrezka.video-resolution,%s,home)' % winprop('script.hdrezka.video-resolution') )
    else:
        xbmc.executebuiltin('ClearProperty(script.hdrezka.video-resolution,home)')


def closestResolution(given_value,available):
    res = None
    try:
        
        init = {}
        
        for i in available:
            init[i] = 1100 if i.lower().find('ultra')>-1 else int(i.replace('p','').strip())

        reverse = {v: k for k, v in init.items()}    
        a_list = list(reverse.keys())
        
        #given_value = int(winprop('script.hdrezka.video-pref_resolution')) if winprop('script.hdrezka.video-pref_resolution') != '0' else int(str(DEFAULT_RESOLUTION).replace('p','').strip())

        if given_value in a_list:
            a_list.remove(given_value)

        if a_list and len(a_list) > 0:
            absolute_difference_function = lambda list_value : abs(list_value - given_value)
            closest = min(a_list, key=absolute_difference_function)

            res = reverse[closest]
    except:
        pass
    
    return res

def rezka_error(message=ADDON.getLocalizedString(32019)):
    busydialog(close=True)
    DIALOG.ok(ADDON.getLocalizedString(32000), str(message))

def select_dialog_small(dict,current=None):
    indexlist = {}
    selectionlist = []
    preSelect = -1

    index = 0
    for item, id in dict.items():
        list_item = xbmcgui.ListItem(item)
        selectionlist.append(list_item)
        indexlist[index] = int(id)
        if current and int(current) == int(id):
            preSelect = index
        index += 1

    busydialog(close=True)

    if preSelect > -1:
        selected = DIALOG.select(xbmc.getLocalizedString(424), selectionlist, preselect=preSelect, useDetails=False)
    else:
        selected = DIALOG.select(xbmc.getLocalizedString(424), selectionlist, useDetails=False)

    if selected == -1:
        return -1

    busydialog()

    return indexlist[selected]

def select_dialog_resolution_small(list,current=None):
    indexlist = []
    selectionlist = []
    preSelect = -1
    
    index = 0
    for item in list:
        list_item = xbmcgui.ListItem(item)
        selectionlist.append(list_item)
        indexlist.append(index)
        if current and current == item:
            preSelect = index
        index += 1

    busydialog(close=True)

    if preSelect > -1:
        selected = DIALOG.select(xbmc.getLocalizedString(424), selectionlist, preselect=preSelect, useDetails=False)
    else:
        selected = DIALOG.select(xbmc.getLocalizedString(424), selectionlist, useDetails=False)

    if selected == -1:
        return -1

    busydialog()

    return indexlist[selected]

def get_local_media(force=False):
    local_media = get_cache('local_db')

    if not local_media or force:
        local_media = {}

        local_media['movies'] = query_local_media('movie',
                                                get='VideoLibrary.GetMovies',
                                                properties=['title', 'originaltitle', 'year', 'uniqueid', 'playcount', 'file', 'art']
                                                )

        if local_media:
            write_cache('local_db', local_media, 24)

    return local_media

def query_local_media(dbtype,get,properties):
    items = json_call(get,properties,sort={'order': 'descending', 'method': 'year'})

    try:
        items = items['result']['%ss' % dbtype]
    except Exception:
        return

    local_items = []
    for item in items:
        local_items.append({'title': item.get('title', ''),
                            'originaltitle': item.get('originaltitle', ''),
                            'imdbnumber': item.get('uniqueid', {}).get('imdb', ''),
                            'tmdbid': item.get('uniqueid', {}).get('tmdb', ''),
                            'tvdbid': item.get('uniqueid', {}).get('tvdb', ''),
                            'year': item.get('year', ''),
                            'dbid': item.get('%sid' % dbtype, ''),
                            'playcount': item.get('playcount', ''),
                            'episodes': item.get('episode', ''),
                            'watchedepisodes': item.get('watchedepisodes', ''),
                            'file': item.get('file', ''),
                            'art': item.get('art', {})}
                            )

    return local_items
