# -*- coding: utf-8 -*-

from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy.visual import Circle
from psychopy.visual import ShapeStim
import pylsl

from psychopy import event
import random
import json

trial_num = 100
image_duration = 4
rest_duration = 2


with open('task_markers.json', 'r') as file:
    markers = json.load(file)

def m_wait(t):
    cl = Clock()
    while cl.getTime() < t:
        keys = event.getKeys()
        # if len(keys)>0:
        #     print(keys)
        if 'escape' in keys:
            win.close()
            quit()


def run_stim():
    global win
##############

    id_num = random.randint(1, 10000)
    name_str = 'psycho_marker_'+str(id_num)
    info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,
                      channel_format='int32', source_id='psycho_marker_001')
    outlet = pylsl.stream_outlet(info)  

############################

    win = Window(size=(480, 360), fullscr=False)

    instruction_text = TextStim(win,'''Imagine movements as the signs showing...
                                                for example:
Imagine grasp a cup in front of you with your left hand when arm when ← light up, and imagine using your right hands when → light up

Press any key to begin''')
    instruction_text.draw()

    win.flip()

    # outlet.push_sample(markers['test'])

    event.waitKeys()

    outlet.push_sample(markers['begin'])

    second_counter = TextStim(win,'0')
    second_counter.size=0.3

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


        print("remain trials: "+str(trial_num - i))
        draw_all()
        second_counter.setText('3')
        second_counter.draw()
        win.flip()
        m_wait(1)
        draw_all()
        second_counter.setText('2')
        second_counter.draw()
        win.flip()
        m_wait(1)
        draw_all()
        second_counter.setText('1')
        second_counter.draw()
        win.flip()
        m_wait(1)
        
        rn = random.randint(1, 100)


        if not rn % 2:
            # left_arrow.draw()
            left_tri.fillColor=face_color_tri
            draw_all()
            win.flip()
            outlet.push_sample(markers['left'])
            m_wait(image_duration)
        else:
            # right_arrow.draw()
            right_tri.fillColor=face_color_tri
            draw_all()
            win.flip()
            outlet.push_sample(markers['right'])
            m_wait(image_duration)

        left_tri.fillColor='none'
        right_tri.fillColor='none'
        draw_all()

        second_counter.setText('rest')
        second_counter.draw()
        win.flip()
        m_wait(rest_duration)


    ### END BODY OF EXPERIMENT ###

    # Finish experiment by closing window and quitting

    win.close()
    quit()

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    run_stim()


