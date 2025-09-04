# -*- coding: utf-8 -*-

from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy.visual import Circle
from psychopy.visual import ShapeStim
from psychopy import event
import random

import pylsl
from lslReceiver import MarkerInlet
import json

trial_num = 10
image_duration = 3
wanted_inlets = ['predict_marker_1']

with open('task_markers.json', 'r') as file:
    markers = json.load(file)

def m_wait(t):
    cl = Clock()
    r=0
    while cl.getTime() < t:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            quit()

        for inlet in inlets:
            ts,d = inlet.pull_data()
            if not len(ts)>0:
                continue

            if (inlet.name[:14] == 'predict_marker'):

                if d[0]==markers['predict_right']:
                    print('predict_right!!!')
                    r=2
                    break
                elif d[0]==markers['predict_left']:
                    print('predict_left!!!')
                    r=1
                    break
                else:
                    pass

        if r!=0:
            break

    return r



def check_marker_inlet():
    for inl in inlets:
        print(inl.name)
        if inl.name[:14] == 'predict_marker':
            return 's'
    return 'f'


def run_task():
    global win,lslRcv,inlets
##############


    id_num = random.randint(1, 10000)
    name_str = 'psycho_marker_'+str(id_num)
    info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,
                      channel_format='int32', source_id='psycho_marker_003')
    outlet = pylsl.stream_outlet(info)  

    inlets=[]
    streams = pylsl.resolve_streams()
    for info in streams:
        if wanted_inlets is not None: # if not none, then only search for this specific inlet; if is none, then search all
            if info.source_id() in wanted_inlets:
                print('Adding inlet: ' + info.name())
                if info.type() == 'Markers':
                    inlets.append(MarkerInlet(info,'Markers'))

    if (check_marker_inlet()=='s'):
        print('suc')
    else:
        print('failed, quit')
        # win.close()
        quit()

    print('continue...')

# ############################


    win = Window(size=(480, 360), fullscr=False)


    instruction_text = TextStim(win,'''Imagine movements as the signs showing

when the “image...” shows up: image one of the movement your imaged in your training session;
then wait for the prediction result

Press any key to begin''')
    instruction_text.draw()

    win.flip()

    event.waitKeys()

    outlet.push_sample(markers['begin'])

    center_text = TextStim(win,'0')
    center_text.size=0.2

    instruction_press_key_text = TextStim(win,'Press any key to begin',pos=(0, -120),units='pix')



    stim_circle = Circle(win,radius=80,edges=128,units='pix',
        fillColor=[0.4375,0.5,0.5625])
    stim_circle.draw()

    p1 = (-200, 0)
    p2 = (-100, 50)
    p3 = (-120,0)
    p4 = (-100, -50)

    left_tri = ShapeStim(win, fillColor='none',  
                             vertices=[p1, p2, p3, p4], lineColor='black',units='pix',
                             opacity=0.5)
    left_tri.draw()


    p5 = (200, 0)
    p6 = (100, 50)
    p7 = (120,0)
    p8 = (100, -50)

    right_tri = ShapeStim(win, fillColor='none',
                             vertices=[p5, p6, p7, p8], lineColor='black',units='pix',
                             opacity=0.5)
    right_tri.draw()

    face_color_tri = [0.4627,0.9333,0.7765]

    def draw_all():
        left_tri.draw()
        right_tri.draw()
        stim_circle.draw()


    for i in range(trial_num):

        print("remain trials: "+str(trial_num - i))

        left_tri.fillColor='none'
        right_tri.fillColor='none'

        draw_all()
        center_text.setText('3')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()
        center_text.setText('2')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()
        center_text.setText('1')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()
        center_text.setText('image.')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()
        center_text.setText('image..')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()

        center_text.setText('image...')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()

        center_text.setText('image....')
        center_text.draw()
        win.flip()
        m_wait(1)
        draw_all()

        outlet.push_sample(markers['mi_end'])

        center_text.setText('wait for result...')
        center_text.draw()
        win.flip()
        a = m_wait(5)

        print(a)

        if a == 1:
            left_tri.fillColor=face_color_tri
        elif a == 2:
            right_tri.fillColor=face_color_tri
        else:
            center_text.setText('failed...')

        draw_all()
        instruction_press_key_text.draw()
        win.flip()
        event.waitKeys()

    ### END BODY OF EXPERIMENT ###

    # Finish experiment by closing window and quitting
    win.close()
    quit()

if __name__ == '__main__':
    run_task()
