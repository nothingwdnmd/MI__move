# -*- coding: utf-8 -*-

from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy import sound
from psychopy import event
# import pygame
import random
import pylsl
import json


trial_num = 4
trial_duration = 30

with open('task_markers.json', 'r') as file:
    markers = json.load(file)

def m_wait(t):
    cl = Clock()
    while cl.getTime() < t:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            quit()


def run_stim():
    global win
##############
    id_num = random.randint(1, 10000)
    name_str = 'psycho_marker_'+str(id_num)
    info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,
                      channel_format='int32', source_id='psycho_marker_002')
    outlet = pylsl.stream_outlet(info)  

############################
    # markers = {
    #     'left': [1],
    #     'right': [2],
    #     'eye_open': [3],
    #     'eye_close': [4],
    #     'begin':[99],
    #     'test':[100]
    # }
    win = Window(size=(480, 360), fullscr=False)

    ### START BODY OF EXPERIMENT ###

    # instruction_stim = ImageStim(win, 'images/instruction_eyeoc.PNG')

    # instruction_stim.draw()

    instruction_text = TextStim(win,'''Open or close your eyes with instructions

Watch the ‘+’ when it shows up;
Close your eyes when ‘Close eyes’ shows up until you hear the ‘Du...’ sound

Press any key to begin''')
    instruction_text.draw()

    win.flip()

    # outlet.push_sample(markers['test'])

    event.waitKeys()

    outlet.push_sample(markers['begin'])

    fix_char = TextStim(win,'+')
    close_eye_char = TextStim(win,'close eyes')

    for i in range(trial_num):

        print("remain trials: "+str(trial_num - i))

        if i % 2:
            mySound = sound.Sound('A')
            mySound.play()
            fix_char.draw()
            win.flip()
            outlet.push_sample(markers['eye_open'])
            m_wait(trial_duration)
        else:
            mySound = sound.Sound('B')
            mySound.play()
            close_eye_char.draw()
            win.flip()
            outlet.push_sample(markers['eye_close'])
            m_wait(trial_duration)


    ### END BODY OF EXPERIMENT ###

    # Finish experiment by closing window and quitting
    mySound = sound.Sound('A')
    mySound.play()
            
    win.close()
    quit()


if __name__ == '__main__':
    # test1.py executed as script
    # do something
    run_stim()
