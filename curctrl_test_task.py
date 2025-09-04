
from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy.visual import Circle
from psychopy.visual import ShapeStim
from psychopy import event
import random
from psychopy.visual import Rect

import pylsl
from lslReceiver import MarkerInlet
import json

trial_num = 30
image_duration = 4
wanted_inlets = ['curctrl_marker_1']
rest_duration = 3
trial_time = 20
cursor_step = 7

with open('task_markers.json', 'r') as file:
    markers = json.load(file)


def m_wait(t):
    cl = Clock()
    while cl.getTime() < t:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            quit()


def check_marker_inlet():
    for inl in inlets:
        print(inl.name)
        if inl.name[:14] == 'curctrl_marker':
            return 's'
    return 'f'


def run_task():
    global win,lslRcv,inlets
##############


    id_num = random.randint(1, 10000)
    name_str = 'psycho_marker_'+str(id_num)
    info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,
                      channel_format='int32', source_id='psycho_marker_005')
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

        ####################################################################################
        quit()

    print('continue...')

# ############################
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

    instruction_text = TextStim(win,'''Imagine movements or relax as in the training session...
                                                for example:
Imagine lifting weight to make ball goes up, and relax to make the ball goes down

Press any key to begin''')
    instruction_text.draw()

    win.flip()

    # outlet.push_sample(markers['test'])

    event.waitKeys()

    outlet.push_sample(markers['task_cursor_control'])

    outlet.push_sample(markers['begin'])

    stim_circle = Circle(win,radius=10,edges=128,units='pix',pos=(0,0),
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

    top_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,-rect_pos_vertical), 
        fillColor=face_color_not_active)

    bottom_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,rect_pos_vertical), 
        fillColor=face_color_not_active)

    top_bottom_rect_thr = int(win_size[1]/2-top_bottom_rect_height)

    target_rec = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,-rect_pos_vertical), 
        fillColor=face_color_not_active)

    # top_rect.draw()
    # bottom_rect.draw()

    center_text = TextStim(win,'0')
    center_text.size=0.3
    default_color = center_text.color

    def draw_all():
        # right_rect.draw()
        # left_rect.draw()
        top_rect.draw()
        bottom_rect.draw()


    for i in range(trial_num):

        print("remain trials: "+str(trial_num - i))
        # draw_all()

        rn = random.randint(1, 1000)

        if not rn % 2:
            # top_rect.draw()
            target_rec.pos = (0,-rect_pos_vertical)
            target_on_top_bottom=-1
        else:
            # bottom_rect.draw()
            target_rec.pos = (0,rect_pos_vertical)
            target_on_top_bottom=1

        target_rec.draw()
        stim_circle.draw()
        center_text.setText('4')
        center_text.draw()
        win.flip()
        m_wait(1)

        target_rec.draw()
        stim_circle.draw()
        center_text.setText('3')
        center_text.draw()
        win.flip()
        m_wait(1)

        target_rec.draw()
        stim_circle.draw()
        center_text.setText('2')
        center_text.draw()
        win.flip()
        m_wait(1)

        target_rec.draw()
        stim_circle.draw()
        center_text.setText('1')
        center_text.draw()
        win.flip()
        m_wait(1)
        
        delta_pos = (0,0)


        if target_on_top_bottom<0:
            outlet.push_sample(markers['curctrl_target_bottom'])
        else:
            outlet.push_sample(markers['curctrl_target_top'])


        target_rec.draw()

        stim_circle.draw()
        win.flip()

        rr = 0

        cl = Clock()
        while cl.getTime() < trial_time:
            keys = event.getKeys()
            # if len(keys)>0:
            #     print(keys)
            if 'escape' in keys:
                win.close()
                quit()

            r = 0
            delta_pos = (0,0)

            if (inlets[0].name[:14] == 'curctrl_marker'):
                ts,d = inlets[0].pull_data()
                if not len(ts)>0:
                    continue
            else:
                continue

            if d[0]==markers['mu_rhythm_high']:
                delta_pos = (0,-cursor_step*2)
            elif d[0]==markers['mu_rhythm_low']:
                delta_pos = (0,cursor_step)
            else:
                pass

            stim_circle.pos += delta_pos

            if int(stim_circle.pos[1])>-top_bottom_rect_thr and int(stim_circle.pos[1])<top_bottom_rect_thr:
                pass
            else:
                if target_on_top_bottom>0:
                    if stim_circle.pos[1]>0:
                        target_rec.fillColor = face_color_active
                        rr = 1
                    else:
                        target_rec.fillColor = [1,0,0]
                        stim_circle.fillColor = [1,0,0] #wrong color
                        rr = 2

                else:
                    if stim_circle.pos[1]<0:
                        target_rec.fillColor = face_color_active
                        rr = 1
                    else:
                        target_rec.fillColor = [1,0,0]
                        stim_circle.fillColor = [1,0,0] #wrong color
                        rr = 2

                # print('get edges')
                target_rec.draw()
                stim_circle.draw()
                win.flip()
                break

            target_rec.draw()
            stim_circle.draw()
            win.flip()


        if rr == 0:
            center_text.setText('time out')
            outlet.push_sample(markers['time_out'])
        elif rr == 1:
            center_text.setText('correct')
            center_text.color = face_color_active
            outlet.push_sample(markers['correct'])
        elif rr==2:
            center_text.setText('wrong')
            center_text.color = [1,0,0]
            outlet.push_sample(markers['wrong'])

        target_rec.draw()
        stim_circle.draw()
        center_text.draw()
        win.flip()
        m_wait(0.5) # show the rect light up 

        stim_circle.pos=(0,0)
        target_rec.fillColor=face_color_not_active
        stim_circle.fillColor=[1,0.5,0.5625]
        center_text.color = default_color 

        m_wait(rest_duration)


    win.close()
    quit()

if __name__ == '__main__':
    run_task()
