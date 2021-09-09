#!/usr/bin/python
# coding: utf-8

########################

import sys
import os
import os.path
import io
import urllib
import xbmc
import xbmcgui

from resources.lib.helper import *
from resources.lib.adapter import *

########################

class HdRezka(object):
    def __init__(self,call,params):
        
        log('Main :: HdRezka > __init__')
        log(call)
        log(params,json=True)

        self.monitor = xbmc.Monitor()
        self.window_stack = []
        self.dialog_cache = {}
        self.call_params = {}
        self.call = call
        self.wid = 10000
        self.rezka_id = params.get('dataid')
        self.movie_url = params.get('url')
        if self.movie_url: self.movie_url = self.movie_url.replace('^','/')
        self.season = params.get('season')

        winprop('script.hdrezka.video-language_code', DEFAULT_LANGUAGE)

        busydialog()

        if call == 'playitem':
            self.play()
        elif call == 'textviewer':
            textviewer(params)
        elif call == 'translators':
            self.translators()
        elif call == 'episode':
            self.setEpisode(params.get('set'))
        elif call == 'resolution':
            self.resolutions()
        elif call == 'clearAll':
            self.releaseAll()
        else:

            if self.rezka_id:
                self.call_params = {}
                self.entry_point()

        busydialog(close=True)

    ''' Collect all data by the tmdb_id and build the dialogs.
    '''
    def entry_point(self):
        
        self.call_params['call'] = self.call
        self.call_params['dataid'] = self.rezka_id
        self.call_params['url'] = self.movie_url
        self.call_params['season'] = self.season
        self.request = self.call + str(self.rezka_id)

        busydialog()

        dialog = self.fetch_video()

        busydialog(close=True)

        ''' Open next dialog if information has been found. If not open the previous dialog again.
        '''
        if dialog:
            self.dialog_cache[self.request] = dialog
            self.dialog_manager(dialog)

        elif self.window_stack:
            self.dialog_history()

        else:
            self.quit()


    def fetch_video(self):
        
        data = HDRVideos(self.call_params)
        if not data['details']:
            return

        Skiner(data['seasons'],data['translate'])
        
        dialog = DialogVideo('script-rezka-video.xml', ADDON_PATH, 'default', '1080i',
                             details=data['details'],
                             cast=data['cast'],
                             crew=data['director'],
                             seasons=data['seasons'],
                             translate=data['translate'],
                             tmdb_id=self.rezka_id
                             )
        handle_resolution()
       
        return dialog


    def play(self):
        pl = winprop('script.hdrezka.video-playlist.json')
        res = winprop('script.hdrezka.video-resolution')
        file = pl[res]
        xbmc.executebuiltin('Dialog.Close(all)')
        xbmc.executebuiltin('PlayMedia(%s)' % file)


    def releaseAll(self):
        xbmc.executebuiltin('ClearProperty(script.hdrezka.video-resolution,home)')
        winprop('script.hdrezka.video-post_id', clear=True)
        winprop('script.hdrezka.video-post_url', clear=True)
        winprop('script.hdrezka.video-ctrl_favs', clear=True)
        winprop('script.hdrezka.video-translators.json', clear=True)
        winprop('script.hdrezka.video-translator_id', clear=True)
        winprop('script.hdrezka.video-translator_initial_id', clear=True)
        winprop('script.hdrezka.video-episode_id', clear=True)
        winprop('script.hdrezka.video-episode_initial_id', clear=True)
        winprop('script.hdrezka.video-playlist.json', clear=True)
        winprop('script.hdrezka.video-resolution', clear=True)
        winprop('script.hdrezka.video-pref_resolution', clear=True)

    def translators(self):
        tid = winprop('script.hdrezka.video-translator_id')
        tlist = {}
        for ttl, info in winprop('script.hdrezka.video-translators.json').items():
            tlist[ttl] = info['id']
            
        option = select_dialog_small(tlist,tid)
        if option > -1 and str(option) != tid:
            busydialog()
            
            winprop('script.hdrezka.video-translator_id',str(option))

            links = rezka_handle_translator_links()
            if links:
                log(links,json=True)
                winprop('script.hdrezka.video-playlist.json', links)
                handle_resolution()
            else:
                rezka_error('Unable retrieve the Movie Links')

        busydialog(close=True)
            

    def setEpisode(self,option):
        curr = winprop('script.hdrezka.video-episode_id')
        if option != curr:
            
            busydialog()
            
            winprop('script.hdrezka.video-episode_id', option)
            se = option.split('_')

            links = rezka_handle_episode_links(int(se[0]), int(se[1]))
            
            if links:
                log(links,json=True)
                winprop('script.hdrezka.video-playlist.json', links)
                handle_resolution()
            else:
                rezka_error('Unable retrieve the Movie Links')

        busydialog(close=True)
        

    def resolutions(self):
        rid = winprop('script.hdrezka.video-resolution')
        rList = list(winprop('script.hdrezka.video-playlist.json').keys())    
        option = select_dialog_resolution_small(rList,rid)
        if option > -1 and rList[option] != rid:
            busydialog()

            winprop('script.hdrezka.video-pref_resolution', str(rList[option]))

            handle_resolution()


        busydialog(close=True)
            

    ''' Dialog handler. Creates the window history, reopens dialogs from a stack
        or cache and is responsible for keeping the script alive.
    '''
    def dialog_manager(self,dialog):
        dialog.doModal()

        try:
            next_id = dialog['id']
            next_call = dialog['call']
            next_season = dialog['season']

            if next_call == 'youtube':
                while condition('Player.HasMedia | Window.IsVisible(busydialog) | Window.IsVisible(busydialognocancel) | Window.IsVisible(okdialog)') and not self.monitor.abortRequested():
                    self.monitor.waitForAbort(1)

                self.dialog_manager(dialog)

            if next_call == 'back':
                self.dialog_history()

            if next_call == 'close':
                raise Exception

            if not next_id or not next_call:
                raise Exception

            self.window_stack.append(dialog)
            self.rezka_id = next_id
            self.call = next_call
            self.season = next_season
            self.request = next_call + str(next_id) + str(next_season)

            if self.dialog_cache.get(self.request):
                dialog = self.dialog_cache[self.request]
                self.dialog_manager(dialog)
            else:
                self.entry_point()

        except Exception:
            self.quit()

    def dialog_history(self):
        if self.window_stack:
            dialog = self.window_stack.pop()
            self.dialog_manager(dialog)
        else:
            self.quit()

    def quit(self):
        del self.call_params
        del self.window_stack
        del self.dialog_cache
        quit()



''' Show & movie dialog
'''
class DialogVideo(xbmcgui.WindowXMLDialog):
    def __init__(self,*args,**kwargs):
        self.first_load = True
        self.action = {}

        self.rezka_id = kwargs['tmdb_id']
        self.details = kwargs['details']
        self.cast = kwargs['cast']
        self.crew = kwargs['crew']
        self.seasons = kwargs['seasons']
        self.translate = kwargs['translate']
        

    def __getitem__(self,key):
        return self.action[key]

    def __setitem__(self,key,value):
        self.action[key] = value

    def onInit(self):
        execute('ClearProperty(script.hdrezka.video-nextcall,home)')

        if self.first_load:
            self.add_items()

    def add_items(self):
        self.first_load = False

        index = 10051
        li = [self.details, self.cast, self.crew]

        for items in li:
            try:
                clist = self.getControl(index)
                clist.addItems(items)
            except RuntimeError as error:
                log('Control with id %s cannot be filled. Error --> %s' % (str(index), error), DEBUG)
                pass
            index = 10053 if index == 10051 else index+1

    def onAction(self,action):
        if action.getId() in [92,10]:
            self.action['id'] = ''
            self.action['season'] = ''
            self.action['call'] = 'back' if action.getId() == 92 else 'close'
            self.quit()

    def onClick(self,controlId):
        next_id = xbmc.getInfoLabel('Container(%s).ListItem.Property(id)' % controlId)
        next_call = xbmc.getInfoLabel('Container(%s).ListItem.Property(call)' % controlId)
        next_season = xbmc.getInfoLabel('Container(%s).ListItem.Property(call_season)' % controlId)

        if next_call in ['person','movie','tv'] and next_id:
            if next_id != str(self.rezka_id) or next_season:
                self.action['id'] = next_id
                self.action['call'] = next_call
                self.action['season'] = next_season
                self.quit()

        elif next_call == 'image':
            FullScreenImage(controlId)

        elif next_call == 'youtube':
            self.action['id'] = ''
            self.action['season'] = ''
            self.action['call'] = 'youtube'
            xbmc.Player().play('plugin://plugin.video.youtube/play/?video_id=%s' % xbmc.getInfoLabel('Container(%s).ListItem.Property(ytid)' % controlId))
            self.quit()

    def quit(self):
        close_action = self.getProperty('onclose')
        onnext_action = self.getProperty('onnext')
        onback_action = self.getProperty('onback_%s' % self.getFocusId())

        if self.action.get('call') and self.action.get('id'):
            execute('SetProperty(script.hdrezka.video-nextcall,true,home)')
            if onnext_action:
                execute(onnext_action)

        if self.action.get('call') == 'back' and onback_action:
            execute(onback_action)

        else:
            if close_action:
                execute(close_action)
            self.close()

class Skiner(object):

    def __init__(self,season={},translate={}):
        self.templPath = os.path.join(ADDON_PATH,'resources','lib','template')
        self.template = os.path.join(self.templPath,'skin.xml')
        self.seasFile = os.path.join(self.templPath,'season.xml')
        self.episFile = os.path.join(self.templPath,'episode.xml')
        self.skinFile = os.path.join(ADDON_PATH,'resources','skins','default','1080i','script-rezka-video.xml')
        self.listId = 101
        self.maxId = 101+len(season)
        self.info = season
        self.translate = 'true' if len(translate) > 1 else 'false'

        self.build()

    def build(self):
        lg_seas = ADDON.getLocalizedString(32040)
        lg_epis = ADDON.getLocalizedString(32166)
        with open(self.template, "r") as sf:
            skin = sf.read()
            
        if len(self.info) == 0:
            skin = skin.replace('#_SEASONS_#','')
            skin = skin.replace('{{ is_episode }}','false')
        else:
            
            with open(self.seasFile, "r") as sf:
                seasFile = sf.read()
                
            with open(self.episFile, "r") as sf:
                episFile = sf.read()

            seasons = []
            height = 150
            top = 0
            sn = 0
            for s, e in self.info.items():
                top = height * sn
                season = seasFile
                season = season.replace('{{ top }}',str(top))
                season = season.replace('{{ id }}',str(self.listId))
                season = season.replace('{{ onup }}',str(self.listId-1))
                ondown = self.listId+1 if self.listId+1 < self.maxId else 10053
                season = season.replace('{{ ondown }}',str(ondown))
                season = season.replace('{{ label }}',u'{0} {1}'.format(lg_seas,s))
                

                items = []
                for i in e:
                    episode = episFile
                    episode = episode.replace('{{ label }}',u'{0} {1}'.format(lg_epis,i))
                    episode = episode.replace('{{ onclick }}','RunScript(script.hdrezka.video,call=episode,set={0}_{1})'.format(s,i))
                    items.append(episode)

                season = season.replace('#_EPISODE_#','\n'.join(items))

                seasons.append(season)
                
                self.listId += 1
                sn += 1

            skin = skin.replace('{{ height }}', str(height+top+50))
            
            skin = skin.replace('{{ is_episode }}','true')
            skin = skin.replace('#_SEASONS_#','\n'.join(seasons))


        skin = skin.replace('{{ is_translate }}',self.translate)

        unicode_text = u'{0}'.format(skin)
        encoded_unicode = unicode_text.encode("utf8")

        a_file = open(self.skinFile, "wb")
        a_file.write(encoded_unicode)
