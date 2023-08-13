############## INITIALIZATION ##############

from __future__ import unicode_literals
import pygame as pg
import os
import threading
import webbrowser
import easing_functions as easing
from youtubesearchpython import VideosSearch
import yt_dlp
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
import clipboard

try: import glob
except: os.system('pip3 install glob'); import glob

Tk().withdraw()
pg.init()

windowx = 640
windowy = 480
clock = pg.time.Clock()
fps = 60

screen = pg.display.set_mode((windowx,windowy), pg.RESIZABLE)
running = True
pg.display.set_caption('YTD')

halfx = windowx//2
halfy = windowy//2

fonts = {}

for i in glob.glob('res/fonts/*.ttf'):
    i = i.replace('\\','/')
    fonts[i] = []
    for j in range(150):
        try:
            fonts[i].append(pg.font.Font(i, j))
        except:
            fonts[i].append(None)


# text drawing functions

def render_text_top(text='', pos=(0,0), color=(255,255,255), size=18, style='regular', center=False, right=False, antialias=True, surface=screen, rotation=0):

    '''
(approximate) aligning points:
,-----------.
| ①   ②   ③ |
|  T E X T  |
`-----------'

① - default aligning using render_text_top
② - center=True
③ - right=True
    '''

    try:
        font = fonts[f'res/fonts/{style}.ttf'][size]
    except:
        try:
            font = fonts[f'res/fonts/regular.ttf'][size]
        except:
            font = pg.font.Font(f'res/fonts/regular.ttf', size)
    rtext = font.render(text, antialias, color)
    if rotation != 0:
        rtext = pg.transform.rotate(rtext, rotation)
    btext = rtext.get_rect()
    if center == True:
        btext.midtop = pos[0],pos[1]
    elif right == True:
        btext.topright = pos[0],pos[1]
    else:
        btext.topleft = pos[0],pos[1]
    surface.blit(rtext, btext)
    return font.size(text)

def render_text_center(text='', pos=(0,0), color=(255,255,255), size=18, style='regular', center=False, right=False, antialias=True, surface=screen, rotation=0):

    '''
(approximate) aligning points:
,-----------.
| ①T E②X T③ |
`-----------'

① - default aligning using render_text_center
② - center=True
③ - right=True
    '''

    try:
        font = fonts[f'res/fonts/{style}.ttf'][size]
    except:
        try:
            font = fonts[f'res/fonts/regular.ttf'][size]
        except:
            font = pg.font.Font(f'res/fonts/regular.ttf', size)
    rtext = font.render(text, antialias, color)
    if rotation != 0:
        rtext = pg.transform.rotate(rtext, rotation)
    btext = rtext.get_rect()
    if center == True:
        btext.center = pos[0],pos[1]
    elif right == True:
        btext.midright = pos[0],pos[1]
    else:
        btext.midleft = pos[0],pos[1]
    surface.blit(rtext, btext)
    return font.size(text)

# returns text size

def get_text_size(text='', size=18, style='regular'):
    try:
        font = fonts[f'res/fonts/{style}.ttf'][size]
    except:
        try:
            font = fonts[f'res/fonts/regular.ttf'][size]
        except:
            font = pg.font.Font(f'res/fonts/regular.ttf', size)
    return font.size(text)

# app variables

img = {
    'loadingcircle': pg.image.load('res/images/loadingcircle.png')
}

menu = 'selectvideo'
submenu = 0

loaded_videos = []
selected_videos = []

loading = ''
loading_len = 0
loading_int = 0

input_data = ''
cursor_pos = 0

scroll = 0
scroll_vel = 0

delete_data_timer = 0

loading_anim_key = 0

tooltip_text = ''
show_tooltip = False
tooltip_anim = 0

selected_codec = 0
audiocodecs = ['webm','mp3','wav']
save_path = os.getcwd().replace('\\','/').rstrip('/')+'/out/'

alerts = []


def alert(text, type='normal'):
    alerts.append({
        'text': text,
        'type': type,
        'key': 200,
        'anim': 0
    })

def search(video, limit=10):
    return VideosSearch(video, limit).result()['result']

def reload_videos():
    global selected_videos, loaded_videos, menu, loading, loading_len, scroll, scroll_vel, running, loading_int

    if len(selected_videos) == 0:
        alert('No videos to download', 'error')
    
    else:
        menu = 'loading'
        loading_len = len(selected_videos)
        loaded_videos = []
        loading_int = 0

        for i in selected_videos:
            try:
                loading = i
                video = search(i)
                
            except Exception as e:
                alert(e, 'error')
                video = None

            loaded_videos.append([video, 0])

            loading_int += 1

            if not running:
                return

        menu = 'downloadvideo'
        scroll = 0
        scroll_vel = 0

def download_videos():
    global loaded_videos, menu, loading, loading_len, scroll, scroll_vel
    global running, loading_int, save_path, selected_codec, audiocodecs

    if len(loaded_videos) == 0:
        alert('No videos to download', 'error')
    
    else:
        menu = 'videoloading'
        loading_len = len(loaded_videos)
        loading_int = 0
        codec = audiocodecs[selected_codec]

        if codec == 'webm':
            options = {'ratelimit':99999999999999, 'outtmpl':f'{save_path}/%(title)s.%(ext)s'}
        else:
            options = {'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': codec,'preferredquality': '192'}], 'ratelimit':99999999999999, 'outtmpl':f'{save_path}%(title)s.%(ext)s'}

        with yt_dlp.YoutubeDL(options) as ydl:
            for video in loaded_videos:
                try:
                    if len(video[0]) > 0:
                        loading = video[0][video[1]] ['title']
                        ydl.download(video[0][video[1]] ['link'])
                except Exception as e:
                    alert(e, 'error')

                loading_int += 1

                if not running:
                    return

        menu = 'finished'
        scroll = 0
        scroll_vel = 0

def load_from_file():
    global selected_videos
 
    path = askopenfilename()

    if len(path) > 0:
        try:
            with open(path, encoding='utf-8') as f:
                paths = f.read().split('\n')

            for i in paths:
                if i != '':
                    selected_videos.append(i)

            filename = path.replace('\\','/').split('/')[-1]

            alert(f'Loaded {len(paths)} names from {filename}')

        except Exception as e:
            alert(e, 'error')

def choose_save_dir():
    global save_path

    path = askdirectory()

    if len(path) > 0:
        save_path = path.replace('\\','/').rstrip('/')+'/'


def tooltip(text):
    global tooltip_text, show_tooltip, tooltip_anim

    if tooltip_anim < 20:
        tooltip_anim += 1
    show_tooltip = True
    tooltip_text = text


# main loop

while running:

############## INPUT ##############

    events = pg.event.get()
    mouse_pos = pg.mouse.get_pos()
    mouse_press = pg.mouse.get_pressed(5)
    mouse_moved = pg.mouse.get_rel()
    keys = pg.key.get_pressed()
    lmb_up = False

    screen.fill((10,13,17))



############## PROCESSING EVENTS ##############

    for event in events:
        if event.type == pg.QUIT:
            running = False 

        if event.type == pg.VIDEORESIZE:
            windowx = event.w
            windowy = event.h
            if windowx <= 640:
                windowx = 640
            if windowy <= 480:
                windowy = 480
            halfx = windowx//2
            halfy = windowy//2
            screen = pg.display.set_mode((windowx,windowy), pg.RESIZABLE)

        if event.type == pg.MOUSEWHEEL:
            scroll_vel -= event.y*15

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            lmb_up = True


        if event.type == pg.KEYDOWN:
            if menu == 'selectvideo':
                if event.key == pg.K_BACKSPACE:
                    try:
                        input_data = list(input_data)
                        input_data.pop(cursor_pos-1)
                        input_data = ''.join(input_data)
                        cursor_pos -= 1
                    except:
                        input_data = ''.join(input_data)
                
                elif event.key == pg.K_RETURN and len(input_data) > 0:
                    selected_videos.append(input_data)
                    input_data = ''
                    cursor_pos = 0

                elif event.key == pg.K_LEFT:
                    cursor_pos -= 1
                
                elif event.key == pg.K_RIGHT:
                    cursor_pos += 1

                elif event.key == pg.K_v and keys[pg.K_LCTRL]:
                    try:
                        input_data = list(input_data)
                        input_data.insert(cursor_pos,clipboard.paste())
                        input_data = "".join(input_data)
                        cursor_pos += len(clipboard.paste())
                        alert('Pasted!')
                    except Exception as e:
                        input_data = "".join(input_data)
                        alert(e, 'error')

                elif event.key == pg.K_c and keys[pg.K_LCTRL]:
                    try:
                        clipboard.copy(input_data)
                        alert('Copied!')
                    except Exception as e:
                        alert(e, 'error')

                
                elif event.unicode.isprintable() and len(event.unicode) > 0:
                    try:
                        input_data = list(input_data)
                        input_data.insert(cursor_pos,event.unicode)
                        input_data = ''.join(input_data)
                        cursor_pos += len(event.unicode)
                    except:
                        pass


            if cursor_pos < 0:
                cursor_pos = 0
            if cursor_pos > len(input_data):
                cursor_pos = len(input_data)




############## VIDEOS SELECTOR ##############

    if menu == 'selectvideo':

        # list
        index = 0
        ongoing = 100-scroll

        for i in selected_videos:
            if ongoing > windowy:
                break

            if ongoing+30 >= 0:
                rect = pg.Rect(0,ongoing,windowx,30)

                if index%2 == 0:
                    pg.draw.rect(screen, (20,24,31), rect)

                render_text_center(i, (10,rect.center[1]), style='names')


                #remove button
                btn_rect = pg.Rect(windowx-30,ongoing,30,30)

                if btn_rect.collidepoint(mouse_pos):
                    if mouse_press[0]:
                        pg.draw.rect(screen, (80,84,91), btn_rect)
                    else:
                        if index%2 == 0:
                            pg.draw.rect(screen, (20,24,31), btn_rect)
                        else:
                            pg.draw.rect(screen, (10,13,17), btn_rect)
                    if lmb_up:
                        selected_videos.pop(index)

                    tooltip(f'Remove video')

                else:
                    if index%2 == 0:
                        pg.draw.rect(screen, (20,24,31), btn_rect)
                    else:
                        pg.draw.rect(screen, (10,13,17), btn_rect)

                pg.draw.aaline(screen, (255,255,255), (windowx-20,ongoing+10), (windowx-10,ongoing+20))
                pg.draw.aaline(screen, (255,255,255), (windowx-10,ongoing+10), (windowx-20,ongoing+20))

            ongoing += 30
            index += 1

        if index == 0:
            render_text_center('No videos to download', (halfx,halfy), (110,115,125), 14, center=True)


        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Add videos', (70,20), size=28, style='heavy')
        render_text_top('Paste text from clipboard or enter in the search bar', (70,60), (180,190,206), 16, 'semibold')


        # search button
        btn_rect = pg.Rect(windowx-50,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                threading.Thread(target=reload_videos).start()
            tooltip(f'Search videos')

        pg.draw.line(screen, (20,24,31), (50,10), (50,90))
        pg.draw.aaline(screen, (255,255,255), (windowx-30,40), (windowx-20,50))
        pg.draw.aaline(screen, (255,255,255), (windowx-20,50), (windowx-30,60))
        

        # load from file button
        btn_rect = pg.Rect(0,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                load_from_file()
            tooltip(f'Load videos from file')

        pg.draw.line(screen, (20,24,31), (windowx-51,10), (windowx-51,90))
        pg.draw.aaline(screen, (255,255,255), (30,37+8), (30,53+8))
        pg.draw.aaline(screen, (255,255,255), (20,40+8), (20,53+8))
        pg.draw.aaline(screen, (255,255,255), (20,53+8), (30,53+8))
        pg.draw.aaline(screen, (255,255,255), (23,37+8), (30,37+8))
        pg.draw.aaline(screen, (255,255,255), (23,37+8), (20,40+8))


        # text field
        rect = pg.Rect(0,windowy-30,windowx,30)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_center(input_data, (10,rect.center[1]), style='names')
        size = get_text_size(input_data[0:cursor_pos], style='names')[0]
        pg.draw.line(screen, (255,255,255), (10+size,rect.center[1]), (10+size+1,rect.center[1]), 20)


        # "delete all" bar
        if keys[pg.K_DELETE]:
            delete_data_timer += 1
        elif delete_data_timer > 0:
            delete_data_timer -= 5

        if delete_data_timer < 0:
            delete_data_timer = 0


        if delete_data_timer > 0:
            percentage = delete_data_timer/80
            ease = easing.QuarticEaseOut(0,80,80).ease(delete_data_timer)/80

            pg.draw.line(screen, (200,20,15), (0,windowy), (windowx,windowy), int(ease*20))
            pg.draw.line(screen, (255,90,90), (0,windowy), (percentage*windowx,windowy), int(ease*20))
            render_text_top('KEEP HOLDING TO ERASE', (halfx,windowy-ease*30), size=14, style='semibold', center=True)

        if delete_data_timer > 80:
            delete_data_timer = 0
            selected_videos = []
            alert('Erased links')



############## LOADING MENU ##############

    elif menu == 'loading':

        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Searching videos...', (70,20), size=28, style='heavy')
        render_text_top(str(loading), (70,60), (180,190,206), 16, 'names')


        # loading animation
        loading_anim_key += 1

        if loading_anim_key > 30:
            loading_anim_key = 0

        ease = easing.SineEaseInOut(0,30,30).ease(loading_anim_key)/30
        img['loadingcircle'] = pg.image.load('res/images/loadingcircle.png')
        img['loadingcircle'] = pg.transform.rotate(img['loadingcircle'], 360-(ease*180+loading_anim_key*6))

        rect = img['loadingcircle'].get_rect()
        rect.center = 35,50
        screen.blit(img['loadingcircle'], rect)


        # bar
        percentage = loading_int/loading_len

        pg.draw.line(screen, (80,85,93), (halfx-150,halfy), (halfx+150, halfy), 5)
        pg.draw.line(screen, (200,208,220), (halfx-150,halfy), (halfx-149+percentage*299, halfy), 5)

        render_text_center(f'{loading_int}/{loading_len}', (halfx,halfy+20), (170,176,185), 14, center=True)



############## CHECKING VIDEOS ##############

    elif menu == 'downloadvideo':

        # list
        index = 0
        ongoing = 100-scroll

        for i in loaded_videos:
            if ongoing > windowy:
                break
            
            if ongoing+30 >= 0:
                rect = pg.Rect(0,ongoing,windowx,75)

                if index%2 == 0:
                    pg.draw.rect(screen, (20,24,31), rect)

                try:
                    render_text_top(i[0][i[1]]['title'], (10,ongoing+7), style='names')
                    text_size = render_text_top(f'{i[0][i[1]]["channel"]["name"]}', (10,ongoing+32), size=15, style='names')
                    render_text_top(f'  ·  {i[0][i[1]]["duration"]}', (10+text_size[0],ongoing+32), (200,210,224), 15)
                    render_text_top(selected_videos[index], (10,ongoing+50), (170,175,183), 14, 'names')
                except:
                    render_text_top('No results', (10,ongoing+16), (190,198,210), style='italic')
                    render_text_top(selected_videos[index], (10,ongoing+39), (170,175,183), 14, 'names')

                else:
                    # open in browser button
                    btn_rect = pg.Rect(windowx-30,ongoing,30,37)
                    if index%2 == 0:
                        pg.draw.rect(screen, (20,24,31), btn_rect)
                    else:
                        pg.draw.rect(screen, (10,13,17), btn_rect)

                    if btn_rect.collidepoint(mouse_pos):
                        if mouse_press[0]:
                            pg.draw.rect(screen, (80,84,91), btn_rect)
                        if lmb_up:
                            webbrowser.open_new_tab(i[0][i[1]]['link'])

                        tooltip(f'Open in browser')
                    
                    pg.draw.aaline(screen, (255,255,255), (windowx-13,ongoing+19), (windowx-18,ongoing+24))
                    pg.draw.aaline(screen, (255,255,255), (windowx-13,ongoing+19), (windowx-18,ongoing+14))


                    # change video button
                    btn_rect = pg.Rect(windowx-30,ongoing+37,30,38)
                    if index%2 == 0:
                        pg.draw.rect(screen, (20,24,31), btn_rect)
                    else:
                        pg.draw.rect(screen, (10,13,17), btn_rect)

                    if btn_rect.collidepoint(mouse_pos):
                        if mouse_press[0]:
                            pg.draw.rect(screen, (80,84,91), btn_rect)
                        if lmb_up:
                            i[1] += 1
                            if i[1] >= len(i[0]):
                                i[1] = 0

                        tooltip(f'Change video ({i[1]+1}/{len(i[0])})')
                    
                    pg.draw.aaline(screen, (255,255,255), (windowx-8,ongoing+55), (windowx-11,ongoing+58))
                    pg.draw.aaline(screen, (255,255,255), (windowx-8,ongoing+55), (windowx-11,ongoing+52))
                    pg.draw.aaline(screen, (255,255,255), (windowx-22,ongoing+55), (windowx-19,ongoing+58))
                    pg.draw.aaline(screen, (255,255,255), (windowx-22,ongoing+55), (windowx-19,ongoing+52))

                    pg.draw.aaline(screen, (255,255,255), (windowx-8,ongoing+55), (windowx-22,ongoing+55))


            ongoing += 75
            index += 1

        if index == 0:
            render_text_center('No videos to download', (halfx,halfy), (110,115,125), 14, center=True)


        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Check videos', (70,20), size=28, style='heavy')
        render_text_top('Open videos in browser or see the name and channel', (70,60), (180,190,206), 16, 'semibold')


        # download button
        btn_rect = pg.Rect(windowx-50,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                menu = 'formatselect'

            tooltip(f'Change settings')

        pg.draw.line(screen, (20,24,31), (windowx-51,10), (windowx-51,90))
        pg.draw.aaline(screen, (255,255,255), (windowx-30,40), (windowx-20,50))
        pg.draw.aaline(screen, (255,255,255), (windowx-20,50), (windowx-30,60))


        # go back button
        btn_rect = pg.Rect(0,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                menu = 'selectvideo'
                scroll = 0
                scroll_vel = 0

            tooltip(f'Edit videos')

        pg.draw.line(screen, (20,24,31), (50,10), (50,90))
        pg.draw.aaline(screen, (255,255,255), (30,40), (20,50))
        pg.draw.aaline(screen, (255,255,255), (20,50), (30,60))



############## VIDEO SETTINGS ##############

    elif menu == 'formatselect':

        # codecs
        render_text_top('Available formats', (halfx,130), (200,210,225), 14, 'semibold', True)

        ongoing = halfx-110*(len(audiocodecs)/2)+5
        index = 0

        for i in audiocodecs:
            rect = pg.Rect(ongoing,160,100,50)

            if selected_codec == index:
                pg.draw.rect(screen, (80,87,100), rect, 0, 7)
            else:
                pg.draw.rect(screen, (25,30,38), rect, 0, 7)

            if rect.collidepoint(mouse_pos):
                if selected_codec != index:
                    if mouse_press[0]:
                        pg.draw.rect(screen, (60,68,80), rect, 0, 7)

                    tooltip(f'Change format')
                
                if lmb_up:
                    selected_codec = index

            render_text_center(i, rect.center, size=21, center=True)

            ongoing += 110
            index += 1


        # save path
        render_text_top('Save path', (halfx,250), (200,210,225), 14, 'semibold', True)

        size = get_text_size(save_path)[0]
        btn_rect = pg.Rect(halfx-size/2-15,280, size+30,35)

        pg.draw.rect(screen, (25,30,38), btn_rect, 0, 7)

        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (60,68,80), btn_rect, 0, 7)

            if lmb_up:
                choose_save_dir()

            tooltip(f'Change save path')

        render_text_center(save_path, btn_rect.center, center=True)


        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Change video settings', (70,20), size=28, style='heavy')
        render_text_top('Choose where to save videos and in what format', (70,60), (180,190,206), 16, 'semibold')


        # download button
        btn_rect = pg.Rect(windowx-50,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                threading.Thread(target=download_videos).start()

            tooltip(f'Download videos')

        pg.draw.line(screen, (20,24,31), (windowx-51,10), (windowx-51,90))
        pg.draw.aaline(screen, (255,255,255), (windowx-30,40), (windowx-20,50))
        pg.draw.aaline(screen, (255,255,255), (windowx-20,50), (windowx-30,60))


        # go back button
        btn_rect = pg.Rect(0,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                menu = 'downloadvideo'
                scroll = 0
                scroll_vel = 0

            tooltip(f'Show videos')

        pg.draw.line(screen, (20,24,31), (50,10), (50,90))
        pg.draw.aaline(screen, (255,255,255), (30,40), (20,50))
        pg.draw.aaline(screen, (255,255,255), (20,50), (30,60))



############## DOWNLOADING MENU ##############

    elif menu == 'videoloading':

        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Downloading videos...', (70,20), size=28, style='heavy')
        render_text_top(str(loading), (70,60), (180,190,206), 16, 'names')


        # loading animation
        loading_anim_key += 1

        if loading_anim_key > 30:
            loading_anim_key = 0

        ease = easing.SineEaseInOut(0,30,30).ease(loading_anim_key)/30
        img['loadingcircle'] = pg.image.load('res/images/loadingcircle.png')
        img['loadingcircle'] = pg.transform.rotate(img['loadingcircle'], 360-(ease*180+loading_anim_key*6))

        rect = img['loadingcircle'].get_rect()
        rect.center = 35,50
        screen.blit(img['loadingcircle'], rect)


        # loading bar
        percentage = loading_int/loading_len

        pg.draw.line(screen, (80,85,93), (halfx-150,halfy), (halfx+150, halfy), 5)
        pg.draw.line(screen, (200,208,220), (halfx-150,halfy), (halfx-149+percentage*299, halfy), 5)

        render_text_center(f'{loading_int}/{loading_len}', (halfx,halfy+20), (170,176,185), 14, center=True)



############## DONE MENU ##############

    elif menu == 'finished':

        # list
        index = 0
        ongoing = 100-scroll

        for i in loaded_videos:
            if ongoing > windowy:
                break
            
            if ongoing+30 >= 0:
                rect = pg.Rect(0,ongoing,windowx,60)

                if index%2 == 0:
                    pg.draw.rect(screen, (20,24,31), rect)

                try:
                    render_text_top(i[0][i[1]]['title'], (10,ongoing+7), style='names')
                    text_size = render_text_top(f'{i[0][i[1]]["channel"]["name"]}', (10,ongoing+32), size=15, style='names')
                    render_text_top(f'  ·  {i[0][i[1]]["duration"]}', (10+text_size[0],ongoing+32), (200,210,224), 15)
                except:
                    pass
                else:
                    # open in browser button
                    btn_rect = pg.Rect(windowx-30,ongoing,30,37)
                    if index%2 == 0:
                        pg.draw.rect(screen, (20,24,31), btn_rect)
                    else:
                        pg.draw.rect(screen, (10,13,17), btn_rect)

                    if btn_rect.collidepoint(mouse_pos):
                        if mouse_press[0]:
                            pg.draw.rect(screen, (80,84,91), btn_rect)
                        if lmb_up:
                            webbrowser.open_new_tab(i[0][i[1]]['link'])

                        tooltip(f'Open in browser')
                    
                    pg.draw.aaline(screen, (255,255,255), (windowx-13,ongoing+19), (windowx-18,ongoing+24))
                    pg.draw.aaline(screen, (255,255,255), (windowx-13,ongoing+19), (windowx-18,ongoing+14))

            ongoing += 60
            index += 1

        if index == 0:
            render_text_center('No downloaded videos', (halfx,halfy), (110,115,125), 14, center=True)


        # top bar
        rect = pg.Rect(0,0,windowx,100)
        pg.draw.rect(screen, (14,17,22), rect)

        render_text_top('Done!', (70,20), size=28, style='heavy')
        render_text_top(f'Successfully downloaded {loading_int} video{"s" if loading_int != 1 else ""}', (70,60), (180,190,206), 16, 'names')


        # redownload button
        btn_rect = pg.Rect(0,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                menu = 'selectvideo'
                selected_videos = []
                scroll = 0
                scroll_vel = 0

            tooltip(f'Redownload')

        pg.draw.line(screen, (20,24,31), (50,10), (50,90))
        pg.draw.aaline(screen, (255,255,255), (30,40), (20,50))
        pg.draw.aaline(screen, (255,255,255), (20,50), (30,60))


        # open in explorer button
        btn_rect = pg.Rect(windowx-50,0,50,100)
            
        if btn_rect.collidepoint(mouse_pos):
            if mouse_press[0]:
                pg.draw.rect(screen, (80,84,91), btn_rect)
            if lmb_up:
                os.startfile(save_path)

            tooltip(f'Open in Explorer')

        pg.draw.line(screen, (20,24,31), (windowx-51,10), (windowx-51,90))
        pg.draw.aaline(screen, (255,255,255), (windowx-30,40), (windowx-20,50))
        pg.draw.aaline(screen, (255,255,255), (windowx-20,50), (windowx-30,60))



############## ALERTS ##############

    ongoing = -40

    for i in alerts:
        if i['key'] >= 30:
            if i['anim'] < 30:
                i['anim'] += 1
        else:
            i['anim'] = i['key']

        i['key'] -= 1

        if i['key'] <= 0:
            alerts.remove(i)

        ease = easing.QuarticEaseOut(0,30,30).ease(i['anim'])/30

        size = get_text_size(str(i['text']), 14)[0]
        rect = pg.Rect(halfx-size/2-15,ongoing+ease*50, size+30,40)

        if i['type'] == 'error':
            color = (180,15,10)
        else:
            color = (20,24,31)

        pg.draw.rect(screen, color, rect, 0, 7)
        render_text_center(str(i['text']), rect.center, size=14, center=True)

        ongoing += ease*50



############## MOUSE TOOLTIP ##############

    if tooltip_anim > 0:
        ease = (easing.ExponentialEaseOut(0,20,20).ease(tooltip_anim)+1)/20

        size = get_text_size(tooltip_text, 14)[0]

        if size+mouse_pos[0]+10 > windowx:
            rect = pg.Rect(mouse_pos[0]-ease*(size+10),mouse_pos[1], ease*(size+10),ease*25)

            pg.draw.rect(screen, (20,24,31), rect, 0,0, 7,0,7,7)
            pg.draw.rect(screen, (50,55,64), rect, 2,0, 7,0,7,7)
            
        else:
            rect = pg.Rect(mouse_pos[0],mouse_pos[1], ease*(size+10),ease*25)

            pg.draw.rect(screen, (20,24,31), rect, 0,0, 0,7,7,7)
            pg.draw.rect(screen, (50,55,64), rect, 2,0, 0,7,7,7)

        render_text_center(tooltip_text, rect.center, size=int(ease*14), center=True)
        
    if not show_tooltip and tooltip_anim > 0:
        tooltip_anim -= 1

    show_tooltip = False



############## SCROLLING ##############

    if scroll < 0:
        scroll = 0

    if menu == 'selectvideo':
        if scroll > len(selected_videos)*30-30:
            scroll = len(selected_videos)*30-30
    if menu == 'downloadvideo':
        if scroll > len(loaded_videos)*75-75:
            scroll = len(loaded_videos)*75-75
    if menu == 'finished':
        if scroll > len(loaded_videos)*60-60:
            scroll = len(loaded_videos)*60-60

    scroll += scroll_vel
    scroll_vel /= 1.4



############## UPDATING SCREEN ##############

    pg.display.flip()
    clock.tick(fps)

    if not running:
        pg.quit()