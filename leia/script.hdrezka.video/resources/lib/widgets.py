#!/usr/bin/python
# coding: utf-8

########################

import routing
from xbmcgui import ListItem
from xbmcplugin import *
from datetime import date

from resources.lib.helper import *
from resources.lib.adapter import *


########################
ICON_PATH = 'special://home/addons/script.hdrezka.video/resources/thumbnails/'
INDEX_MENU = {
    'movie': {
        'name': ADDON.getLocalizedString(32156),
        'route': 'movie_listing',
        'icon': ICON_PATH+'category/movie.jpg',
        'folder': True,
        'menu': [
            { 'name': ADDON.getLocalizedString(32100), 'call': 'western', 'icon': ICON_PATH+'film/Western.jpg' },
            { 'name': ADDON.getLocalizedString(32101), 'call': 'family', 'icon': ICON_PATH+'film/Family.jpg' },
            { 'name': ADDON.getLocalizedString(32102), 'call': 'fantasy', 'icon': ICON_PATH+'film/Fantasy.jpg' },
            { 'name': ADDON.getLocalizedString(32103), 'call': 'biographical', 'icon': ICON_PATH+'film/Biographical.jpg' },
            { 'name': ADDON.getLocalizedString(32104), 'call': 'arthouse', 'icon': ICON_PATH+'film/Art-House.jpg' },
            { 'name': ADDON.getLocalizedString(32105), 'call': 'action', 'icon': ICON_PATH+'film/Action.jpg' },
            { 'name': ADDON.getLocalizedString(32106), 'call': 'military', 'icon': ICON_PATH+'film/War.jpg' },
            { 'name': ADDON.getLocalizedString(32107), 'call': 'detective', 'icon': ICON_PATH+'film/Detectives.jpg' },
            { 'name': ADDON.getLocalizedString(32108), 'call': 'crime', 'icon': ICON_PATH+'film/Crime.jpg' },
            { 'name': ADDON.getLocalizedString(32109), 'call': 'adventures', 'icon': ICON_PATH+'film/Adventure.jpg' },
            { 'name': ADDON.getLocalizedString(32110), 'call': 'drama', 'icon': ICON_PATH+'film/Drama.jpg' },
            { 'name': ADDON.getLocalizedString(32111), 'call': 'sport', 'icon': ICON_PATH+'film/Sport.jpg' },
            { 'name': ADDON.getLocalizedString(32112), 'call': 'fiction', 'icon': ICON_PATH+'film/Sci-fi.jpg' },
            { 'name': ADDON.getLocalizedString(32113), 'call': 'comedy', 'icon': ICON_PATH+'film/Comedy.jpg' },
            { 'name': ADDON.getLocalizedString(32114), 'call': 'melodrama', 'icon': ICON_PATH+'film/RomCom.jpg' },
            { 'name': ADDON.getLocalizedString(32115), 'call': 'thriller', 'icon': ICON_PATH+'film/Thriller.jpg' },
            { 'name': ADDON.getLocalizedString(32116), 'call': 'horror', 'icon': ICON_PATH+'film/Horror.jpg' },
            { 'name': ADDON.getLocalizedString(32117), 'call': 'musical', 'icon': ICON_PATH+'film/Musical.jpg' },
            { 'name': ADDON.getLocalizedString(32118), 'call': 'historical', 'icon': ICON_PATH+'film/History.jpg' },
            { 'name': ADDON.getLocalizedString(32119), 'call': 'documentary', 'icon': ICON_PATH+'film/Documentary.jpg' },
            { 'name': ADDON.getLocalizedString(32120), 'call': 'erotic', 'icon': ICON_PATH+'film/Erotic.jpg' },
            { 'name': ADDON.getLocalizedString(32121), 'call': 'kids', 'icon': ICON_PATH+'film/Childy.jpg' },
            { 'name': ADDON.getLocalizedString(32122), 'call': 'travel', 'icon': ICON_PATH+'film/Travel.jpg' },
            { 'name': ADDON.getLocalizedString(32123), 'call': 'cognitive', 'icon': ICON_PATH+'film/Cognitive.jpg' },
            { 'name': ADDON.getLocalizedString(32124), 'call': 'theatre', 'icon': ICON_PATH+'film/Theatre.jpg' },
            { 'name': ADDON.getLocalizedString(32125), 'call': 'concert', 'icon': ICON_PATH+'film/Concert.jpg' },
            { 'name': ADDON.getLocalizedString(32126), 'call': 'standup', 'icon': ICON_PATH+'film/Standup.jpg' },
            { 'name': ADDON.getLocalizedString(32127), 'call': 'short', 'icon': ICON_PATH+'film/Short-film.jpg' },
            { 'name': ADDON.getLocalizedString(32128), 'call': 'our', 'icon': ICON_PATH+'film/Russian.jpg' },
            { 'name': ADDON.getLocalizedString(32129), 'call': 'ukrainian', 'icon': ICON_PATH+'film/Ukrainian.jpg' },
            { 'name': ADDON.getLocalizedString(32130), 'call': 'foreign', 'icon': ICON_PATH+'film/Foreign.jpg' },

        ]
    },
    'series': {
        'name': ADDON.getLocalizedString(32157),
        'route': 'series_listing',
        'icon': ICON_PATH+'category/serials.jpg',
        'folder': True,
        'menu': [
            { 'name': ADDON.getLocalizedString(32106), 'call': 'military', 'icon': ICON_PATH+'serials/War.jpg' },
            { 'name': ADDON.getLocalizedString(32105), 'call': 'action', 'icon': ICON_PATH+'serials/Action.jpg' },
            { 'name': ADDON.getLocalizedString(32104), 'call': 'arthouse', 'icon': ICON_PATH+'serials/Art-House.jpg' },
            { 'name': ADDON.getLocalizedString(32114), 'call': 'melodrama', 'icon': ICON_PATH+'serials/RomCom.jpg' },
            { 'name': ADDON.getLocalizedString(32115), 'call': 'thriller', 'icon': ICON_PATH+'serials/Thriller.jpg' },
            { 'name': ADDON.getLocalizedString(32116), 'call': 'horror', 'icon': ICON_PATH+'serials/Horror.jpg' },
            { 'name': ADDON.getLocalizedString(32109), 'call': 'adventures', 'icon': ICON_PATH+'serials/Adventure.jpg' },
            { 'name': ADDON.getLocalizedString(32101), 'call': 'family', 'icon': ICON_PATH+'serials/Family.jpg' },
            { 'name': ADDON.getLocalizedString(32112), 'call': 'fiction', 'icon': ICON_PATH+'serials/Sci-fi.jpg' },
            { 'name': ADDON.getLocalizedString(32102), 'call': 'fantasy', 'icon': ICON_PATH+'serials/Fantasy.jpg' },
            { 'name': ADDON.getLocalizedString(32110), 'call': 'drama', 'icon': ICON_PATH+'serials/Drama.jpg' },
            { 'name': ADDON.getLocalizedString(32111), 'call': 'sport', 'icon': ICON_PATH+'serials/Sport.jpg' },
            { 'name': ADDON.getLocalizedString(32113), 'call': 'comedy', 'icon': ICON_PATH+'serials/Comedy.jpg' },
            { 'name': ADDON.getLocalizedString(32107), 'call': 'detective', 'icon': ICON_PATH+'serials/Detectives.jpg' },
            { 'name': ADDON.getLocalizedString(32108), 'call': 'crime', 'icon': ICON_PATH+'serials/Crime.jpg' },
            { 'name': ADDON.getLocalizedString(32118), 'call': 'historical', 'icon': ICON_PATH+'serials/History.jpg' },
            { 'name': ADDON.getLocalizedString(32103), 'call': 'biographical', 'icon': ICON_PATH+'serials/Biographical.jpg' },
            { 'name': ADDON.getLocalizedString(32100), 'call': 'western', 'icon': ICON_PATH+'serials/Western.jpg' },
            { 'name': ADDON.getLocalizedString(32119), 'call': 'documentary', 'icon': ICON_PATH+'serials/Documentary.jpg' },
            { 'name': ADDON.getLocalizedString(32117), 'call': 'musical', 'icon': ICON_PATH+'serials/Musical.jpg' },
            { 'name': ADDON.getLocalizedString(32131), 'call': 'realtv', 'icon': ICON_PATH+'serials/Real-Tv.jpg' },
            { 'name': ADDON.getLocalizedString(32132), 'call': 'telecasts', 'icon': ICON_PATH+'serials/Telecasts.jpg' },
            { 'name': ADDON.getLocalizedString(32126), 'call': 'standup', 'icon': ICON_PATH+'serials/Standup.jpg' },
            { 'name': ADDON.getLocalizedString(32120), 'call': 'erotic', 'icon': ICON_PATH+'serials/Erotic.jpg' },
            { 'name': ADDON.getLocalizedString(32133), 'call': 'russian', 'icon': ICON_PATH+'serials/Russian.jpg' },
            { 'name': ADDON.getLocalizedString(32129), 'call': 'ukrainian', 'icon': ICON_PATH+'serials/Ukrainian.jpg' },
            { 'name': ADDON.getLocalizedString(32130), 'call': 'foreign', 'icon': ICON_PATH+'serials/Foreign.jpg' },

        ]
    },
    'cartoons': {
        'name': ADDON.getLocalizedString(32158),
        'route': 'cartoons_listing',
        'icon': ICON_PATH+'category/cartoons.jpg',
        'folder': True,
        'menu': [
            { 'name': ADDON.getLocalizedString(32110), 'call': 'drama', 'icon': ICON_PATH+'cartoon/Dramma.jpg' },
            { 'name': ADDON.getLocalizedString(32134), 'call': 'fairytale', 'icon': ICON_PATH+'cartoon/Tales.jpg' },
            { 'name': ADDON.getLocalizedString(32105), 'call': 'action', 'icon': ICON_PATH+'cartoon/Action.jpg' },
            { 'name': ADDON.getLocalizedString(32113), 'call': 'comedy', 'icon': ICON_PATH+'cartoon/Comedy.jpg' },
            { 'name': ADDON.getLocalizedString(32101), 'call': 'family', 'icon': ICON_PATH+'cartoon/Family.jpg' },
            { 'name': ADDON.getLocalizedString(32112), 'call': 'fiction', 'icon': ICON_PATH+'cartoon/Fantastic.jpg' },
            { 'name': ADDON.getLocalizedString(32102), 'call': 'fantasy', 'icon': ICON_PATH+'cartoon/Fantasy.jpg' },
            { 'name': ADDON.getLocalizedString(32115), 'call': 'thriller', 'icon': ICON_PATH+'cartoon/Triller.jpg' },
            { 'name': ADDON.getLocalizedString(32116), 'call': 'horror', 'icon': ICON_PATH+'cartoon/Horrors.jpg' },
            { 'name': ADDON.getLocalizedString(32109), 'call': 'adventures', 'icon': ICON_PATH+'cartoon/Adventure.jpg' },
            { 'name': ADDON.getLocalizedString(32111), 'call': 'sport', 'icon': ICON_PATH+'cartoon/Sports.jpg' },
            { 'name': ADDON.getLocalizedString(32123), 'call': 'cognitive', 'icon': ICON_PATH+'cartoon/Cognitive.jpg' },
            { 'name': ADDON.getLocalizedString(32117), 'call': 'musical', 'icon': ICON_PATH+'cartoon/Musical.jpg' },
            { 'name': ADDON.getLocalizedString(32121), 'call': 'kids', 'icon': ICON_PATH+'cartoon/Childly.jpg' },
            { 'name': ADDON.getLocalizedString(32135), 'call': 'anime', 'icon': ICON_PATH+'cartoon/Anime.jpg' },
            { 'name': ADDON.getLocalizedString(32136), 'call': 'soyzmyltfilm', 'icon': ICON_PATH+'cartoon/Soviet.jpg' },
            { 'name': ADDON.getLocalizedString(32137), 'call': 'multseries', 'icon': ICON_PATH+'cartoon/Serials.jpg' },
            { 'name': ADDON.getLocalizedString(32138), 'call': 'adult', 'icon': ICON_PATH+'cartoon/Adult.jpg' },
            { 'name': ADDON.getLocalizedString(32139), 'call': 'full-length', 'icon': ICON_PATH+'cartoon/Full-Length.jpg' },
            { 'name': ADDON.getLocalizedString(32128), 'call': 'our', 'icon': ICON_PATH+'cartoon/Russian.jpg' },
            { 'name': ADDON.getLocalizedString(32130), 'call': 'foreign', 'icon': ICON_PATH+'cartoon/Foreign.jpg' },


        ]
    },
    'animation': {
        'name': ADDON.getLocalizedString(32159),
        'route': 'animation_listing',
        'icon': ICON_PATH+'category/anime.jpg',
        'folder': True,
        'menu': [
            { 'name': ADDON.getLocalizedString(32106), 'call': 'military', 'icon': ICON_PATH+'anime/War.jpg' },
            { 'name': ADDON.getLocalizedString(32110), 'call': 'drama', 'icon': ICON_PATH+'anime/Dramma.jpg' },
            { 'name': ADDON.getLocalizedString(32107), 'call': 'detective', 'icon': ICON_PATH+'anime/Detectives.jpg' },
            { 'name': ADDON.getLocalizedString(32115), 'call': 'thriller', 'icon': ICON_PATH+'anime/Triller.jpg' },
            { 'name': ADDON.getLocalizedString(32113), 'call': 'comedy', 'icon': ICON_PATH+'anime/Comedy.jpg' },
            { 'name': ADDON.getLocalizedString(32112), 'call': 'fiction', 'icon': ICON_PATH+'anime/Fantastic.jpg' },
            { 'name': ADDON.getLocalizedString(32102), 'call': 'fantasy', 'icon': ICON_PATH+'anime/Fantasy.jpg' },
            { 'name': ADDON.getLocalizedString(32109), 'call': 'adventures', 'icon': ICON_PATH+'anime/Adventure.jpg' },
            { 'name': ADDON.getLocalizedString(32140), 'call': 'romance', 'icon': ICON_PATH+'anime/Romantic.jpg' },
            { 'name': ADDON.getLocalizedString(32118), 'call': 'historical', 'icon': ICON_PATH+'anime/Historical.jpg' },
            { 'name': ADDON.getLocalizedString(32116), 'call': 'horror', 'icon': ICON_PATH+'anime/Horror.jpg' },
            { 'name': ADDON.getLocalizedString(32141), 'call': 'mystery', 'icon': ICON_PATH+'anime/Mistic.jpg' },
            { 'name': ADDON.getLocalizedString(32117), 'call': 'musical', 'icon': ICON_PATH+'anime/Musical.jpg' },
            { 'name': ADDON.getLocalizedString(32120), 'call': 'erotic', 'icon': ICON_PATH+'anime/Erotic.jpg' },
            { 'name': ADDON.getLocalizedString(32105), 'call': 'action', 'icon': ICON_PATH+'anime/Actions.jpg' },
            { 'name': ADDON.getLocalizedString(32142), 'call': 'fighting', 'icon': ICON_PATH+'anime/Kung-Fu.jpg' },
            { 'name': ADDON.getLocalizedString(32143), 'call': 'samurai', 'icon': ICON_PATH+'anime/Samurai-Action.jpg' },
            { 'name': ADDON.getLocalizedString(32111), 'call': 'sport', 'icon': ICON_PATH+'anime/Sports.jpg' },
            { 'name': ADDON.getLocalizedString(32144), 'call': 'educational', 'icon': ICON_PATH+'anime/Educational.jpg' },
            { 'name': ADDON.getLocalizedString(32145), 'call': 'everyday', 'icon': ICON_PATH+'anime/Everyday.jpg' },
            { 'name': ADDON.getLocalizedString(32146), 'call': 'parody', 'icon': ICON_PATH+'anime/Parody.jpg' },
            { 'name': ADDON.getLocalizedString(32147), 'call': 'school', 'icon': ICON_PATH+'anime/School.jpg' },
            { 'name': ADDON.getLocalizedString(32121), 'call': 'kids', 'icon': ICON_PATH+'anime/Childy.jpg' },
            { 'name': ADDON.getLocalizedString(32134), 'call': 'fairytale', 'icon': ICON_PATH+'anime/Tales.jpg' },
            { 'name': ADDON.getLocalizedString(32148), 'call': 'kodomo', 'icon': ICON_PATH+'anime/Kodomo.jpg' },
            { 'name': ADDON.getLocalizedString(32149), 'call': 'shoujoai', 'icon': ICON_PATH+'anime/Sedze-i.jpg' },
            { 'name': ADDON.getLocalizedString(32150), 'call': 'shoujo', 'icon': ICON_PATH+'anime/Syodzyo.jpg' },
            { 'name': ADDON.getLocalizedString(32151), 'call': 'shounen', 'icon': ICON_PATH+'anime/Syonen.jpg' },
            { 'name': ADDON.getLocalizedString(32152), 'call': 'shounenai', 'icon': ICON_PATH+'anime/Syonen-i.jpg' },
            { 'name': ADDON.getLocalizedString(32153), 'call': 'ecchi', 'icon': ICON_PATH+'anime/Etti.jpg' },
            { 'name': ADDON.getLocalizedString(32154), 'call': 'mahoushoujo', 'icon': ICON_PATH+'anime/Maho-syodze.jpg' },
            { 'name': ADDON.getLocalizedString(32155), 'call': 'mecha', 'icon': ICON_PATH+'anime/Meha.jpg' },


        ]
    },
    'new': {
        'name': ADDON.getLocalizedString(32160),
        'route': 'new_listing',
        'icon': ICON_PATH+'category/new.jpg',
        'folder': True,
        'menu': [],
    },
    'announce': {
        'name': ADDON.getLocalizedString(32161),
        'route': 'announce_listing',
        'icon': ICON_PATH+'category/announce.jpg',
        'folder': True,
        'menu': [],
    },
    'collections': {
        'name': ADDON.getLocalizedString(32162),
        'route': 'collections_listing',
        'icon': ICON_PATH+'category/collections.jpg',
        'folder': True,
        'menu': [],
    },
    'search': {
        'name': ADDON.getLocalizedString(32005),
        'icon': ICON_PATH+'category/search.jpg',
        'route': 'search_listing',
        'folder': True,
        'menu': [],
    },
}


DEFAULT_ART = {
    'icon': 'DefaultFolder.png',
    'thumb': 'special://home/addons/script.hdrezka.video/resources/icon.png'
}

########################

plugin = routing.Plugin()

# entrypoint
@plugin.route('/')
def index():
    cats = ['search', 'movie', 'series', 'cartoons', 'new', 'announce', 'collections'] if RESTRICTED else ['search', 'movie', 'series', 'cartoons', 'animation', 'new', 'announce', 'collections']        
    for i in cats:
        item =  INDEX_MENU[i]
        li_item = ListItem(item['name'])
        li_item.setArt({'icon': 'DefaultFolder.png','thumb': item['icon']})
        xbmcplugin.addDirectoryItem(plugin.handle,
                         plugin.url_for(eval(item['route'])),
                         li_item, item['folder'])

    _sortmethods()
    xbmc.executebuiltin('Container.SetViewMode(%d)' % 50)
    xbmcplugin.endOfDirectory(plugin.handle)


# actions
@plugin.route('/info/<call>/<dataid>/<link>')
def dialog(call,dataid,link):
    execute('RunScript(script.hdrezka.video,call=%s,dataid=%s,url=%s)' % (call,dataid,link))

    
@plugin.route('/search')
@plugin.route('/search/<call>')
@plugin.route('/search/<call>/<param>/<page>')
def search_listing(call=None,param=None,page=1,pages=1):
    if not param:
        query = DIALOG.input(xbmc.getLocalizedString(19133), type=xbmcgui.INPUT_ALPHANUM)
        if query and query.strip() != '':
            param = {
                    "do": 'search',
                    "subaction": 'search',
                    "q": query
                }
    if param:
        if isinstance(param, str): param = eval(param)
        _listing('search','search',page,pages,param)
    
# common
@plugin.route('/movie')
@plugin.route('/movie/<call>')
@plugin.route('/movie/<call>/<page>')
def movie_listing(call=None,page=1,pages=1):
    _listing('movie', call, page, pages)

@plugin.route('/series')
@plugin.route('/series/<call>')
@plugin.route('/series/<call>/<page>')
def series_listing(call=None,page=1,pages=1):
    _listing('series', call, page, pages)

@plugin.route('/cartoons')
@plugin.route('/cartoons/<call>')
@plugin.route('/cartoons/<call>/<page>')
def cartoons_listing(call=None,page=1,pages=1):
    _listing('cartoons', call, page, pages)

@plugin.route('/animation')
@plugin.route('/animation/<call>')
@plugin.route('/animation/<call>/<page>')
def animation_listing(call=None,page=1,pages=1):
    _listing('animation', call, page, pages)

@plugin.route('/new')
@plugin.route('/new/<call>')
@plugin.route('/new/<call>/<page>')
def new_listing(call=None,page=1,pages=1):
    _listing('new', 'pass', page, pages)

@plugin.route('/announce')
@plugin.route('/announce/<call>')
@plugin.route('/announce/<call>/<page>')
def announce_listing(call=None,page=1,pages=1):
    _listing('announce', 'pass', page, pages)

@plugin.route('/collections')
@plugin.route('/collections/<call>')
@plugin.route('/collections/<call>/<page>')
def collections_listing(call=None,page=1,pages=1):    
    call = call if call else 'collect'
    _listing('collections', call, page, pages)

def _listing(directory, call, page, pages,query={}):
    wid = None 
    route = '%s_listing' % directory
    category = _dict_match('name', INDEX_MENU[directory]['menu'], 'call', call)

    if _previouspage(page):
        
        li_item = ListItem(ADDON.getLocalizedString(32056))
        li_item.setArt(DEFAULT_ART)
        li_item.setProperty('SpecialSort', 'top')
        
        if call == 'search':
            
            xbmcplugin.addDirectoryItem(plugin.handle,
                             plugin.url_for(eval(route), call, query, int(page)-1),
                             li_item, True)
        else:
            
            xbmcplugin.addDirectoryItem(plugin.handle,
                         plugin.url_for(eval(route), call, int(page)-1),
                         li_item, True)

    if not call:
        
        result = None
        for i in INDEX_MENU[directory].get('menu'):
            if i['call'] in ['horror','erotic'] and RESTRICTED:
                continue
            li_item = ListItem(i.get('name'))
            li_item.setArt({'icon': 'DefaultFolder.png','thumb': i['icon']})
            xbmcplugin.addDirectoryItem(plugin.handle,
                             plugin.url_for(eval(route), i.get('call')),
                             li_item, True)
        wid = 50
        _category(category=INDEX_MENU[directory]['name'])

    elif call == 'pass':
        
        result, pages = _query(directory, '', params={'page': page})

    elif call == 'search':
        query['page'] = page
        result, pages = _query(directory, call, params=query)
        
    elif call == 'collect':
        
        result = None
        colletion_menu = rezka_collections()
        for i in colletion_menu:
            li_item = ListItem(i.get('name'))
            li_item.setArt({'icon': 'DefaultFolder.png','thumb': i.get('icon')})
            xbmcplugin.addDirectoryItem(plugin.handle,
                             plugin.url_for(eval(route), i.get('call')),
                             li_item, True)
        _category(category=INDEX_MENU[directory]['name'])
        wid = 50
    
    else:
        result, pages = _query(directory, call, params={'page': page})

    if result:
        _add(result, directory)
        _category(directory, category)

    if _nextpage(page, pages):
        
        li_item = ListItem(xbmc.getLocalizedString(33078))
        li_item.setArt(DEFAULT_ART)
        li_item.setProperty('SpecialSort', 'bottom')
        
        if call == 'search':
            
            xbmcplugin.addDirectoryItem(plugin.handle,
                             plugin.url_for(eval(route), call, query, int(page)+1),
                             li_item, True)
        else:
            
            xbmcplugin.addDirectoryItem(plugin.handle,
                         plugin.url_for(eval(route), call, int(page)+1),
                         li_item, True)

    _sortmethods()
    if wid:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % wid)
    xbmcplugin.endOfDirectory(plugin.handle)

#helpers
def _dict_match(get,source,key,value):
    result = [i.get(get) for i in source if i.get(key) == value]
    if result:
        return result[0]


def _add(items,call):

    for item in items:
        list_item = rezka_handle_movie_list(item)
        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(dialog, call, item['id'], item['url']), list_item)

def _category(content='',category='',call=None,info=None):
    if content == 'tv':
        plugincontent = 'tvshows'
    elif content == 'movie':
        plugincontent = 'movies'
    elif content == 'person':
        plugincontent = 'actors'
    elif content:
        plugincontent = content
    else:
        plugincontent = ''

    set_plugincontent(content=plugincontent, category=category)


def _query(content_type,call,get=None,params=None,get_details=False):

    cache_key = 'widget' + content_type + str(call) + str(get) + str(params)

    rmdb = get_cache(cache_key)

    if not rmdb:
        rmdb = rezka_list(action=content_type,
                          call=call,
                          get=get,
                          params=params
                          )

    if rmdb:
        write_cache(cache_key,rmdb,3)

    if not get_details:
        try:
            return rmdb.get('results'), rmdb.get('total_pages')
        except Exception:
            return [], 1

    else:
        return rmdb


def _nextpage(page,pages):
    if int(page) < int(pages) and condition('Window.IsVisible(MyVideoNav.xml)'):
        return True
    return False


def _previouspage(page):
    if int(page) > 1 and condition('Window.IsVisible(MyVideoNav.xml) + !Container.HasParent'):
        return True
    return False


def _sortmethods():
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
