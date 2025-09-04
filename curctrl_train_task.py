
from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy.visual import Circle
from psychopy.visual import ShapeStim
from psychopy.visual import Rect

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
                      channel_format='int32', source_id='psycho_marker_004')
    outlet = pylsl.stream_outlet(info)  

############################
    win_size=(480, 360)

    win = Window(size=win_size, fullscr=False)

    # Initialize a (global) clock
    # clock = Clock()

    # # Initialize Keyboard
    # kb = Keyboard()

    ### START BODY OF EXPERIMENT ###

    # instruction_stim = ImageStim(win, 'images/instruction_mi_train.PNG')
    # left_arrow = ImageStim(win, 'images/left_arrow.PNG')
    # right_arrow = ImageStim(win, 'images/right_arrow.PNG')

    # instruction_stim.draw()

    instruction_text = TextStim(win,'''Imagine movements or relax as the signs showing...
                                                for example:
Imagine lifting weight your right hand when ball goes down, and relax when the ball goes up

Press any key to begin''')
    instruction_text.draw()

    win.flip()

    # outlet.push_sample(markers['test'])

    event.waitKeys()

    outlet.push_sample(markers['begin'])

    stim_circle = Circle(win,radius=10,edges=128,units='pix',
        fillColor=[1,0.5,0.5625])
    stim_circle.draw()

    left_right_rect_width = 20
    rect_pos_horizontal = int((win_size[0]-left_right_rect_width)/2)
    # print(rect_pos_horizontal)

    face_color_not_active = [0.4375,0.5,0.5625]
    face_color_active = [1,0.5,0.5625]


    left_rect = Rect(win,width=left_right_rect_width,height=50,units='pix',pos=(-rect_pos_horizontal, 0), 
        fillColor=face_color_not_active)

    right_rect = Rect(win,width=left_right_rect_width,height=50,units='pix',pos=(rect_pos_horizontal, 0), 
        fillColor=face_color_not_active)

    # left_rect.draw()
    # right_rect.draw()

    top_bottom_rect_height = 20
    rect_pos_vertical = int((win_size[1]-top_bottom_rect_height)/2)
    # print(rect_pos_vertical)

    top_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,rect_pos_vertical), 
        fillColor=face_color_not_active)

    bottom_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,-rect_pos_vertical), 
        fillColor=face_color_not_active)

    top_bottom_rect_thr = int(win_size[1]/2-top_bottom_rect_height)

    # top_rect.draw()
    # bottom_rect.draw()

    second_counter = TextStim(win,'0')
    second_counter.size=0.3

    def draw_all():
        # right_rect.draw()
        # left_rect.draw()
        top_rect.draw()
        bottom_rect.draw()

    for i in range(trial_num):

        print("remain trials: "+str(trial_num - i))
        draw_all()
        stim_circle.draw()

        second_counter.setText('3')
        second_counter.draw()
        win.flip()
        m_wait(1)
        draw_all()
        second_counter.setText('2')
        stim_circle.draw()
        second_counter.draw()
        win.flip()
        m_wait(1)
        draw_all()
        second_counter.setText('1')
        stim_circle.draw()
        second_counter.draw()
        win.flip()
        m_wait(1)
        
        rn = random.randint(1, 100)

        delta_pos = (0,0)

        if not rn % 2:
            second_counter.setText('imagine lifting weight')
            delta_pos = (0,3)
            outlet.push_sample(markers['curctrl_up'])
        else:
            second_counter.setText('relax')
            delta_pos = (0,-3)
            outlet.push_sample(markers['curctrl_down'])

        draw_all()
        stim_circle.draw()
        second_counter.draw()
        win.flip()
        m_wait(1)

        # print(top_bottom_rect_thr)
        # print(stim_circle.pos[1])

        while int(stim_circle.pos[1])>-top_bottom_rect_thr and int(stim_circle.pos[1])<top_bottom_rect_thr:
            stim_circle.pos += delta_pos
            stim_circle.draw()
            draw_all()
            win.flip()
            m_wait(0.02)

        if stim_circle.pos[1]>0:
            top_rect.fillColor = face_color_active
        else:
            bottom_rect.fillColor = face_color_active

        draw_all()
        win.flip()

        outlet.push_sample(markers['trial_end'])
        m_wait(1)

        stim_circle.pos=(0,0)
        bottom_rect.fillColor=face_color_not_active
        top_rect.fillColor=face_color_not_active

        second_counter.setText('rest')
        second_counter.draw()
        win.flip()
        m_wait(rest_duration)

    ### END BODY OF EXPERIMENT ###

    # Finish experiment by closing window and quitting

    # pylsl.
    win.close()
    quit()

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    run_stim()
