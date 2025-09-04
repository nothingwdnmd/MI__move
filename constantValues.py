# -*- coding: utf-8 -*-

EVT_WIN_CMD_OPEN_COM			= "evt_win_cmd_open_com"
EVT_WIN_CMD_CLOSE_COM			= "evt_win_cmd_close_com"
EVT_WIN_CMD_CON_DEV				= "evt_win_cmd_con_dev"
EVT_WIN_QUIT					= "evt_win_quit"

SERIAL_CMD_FALSH_LED            ="{\"cmd\":\"flash led\"}"
SERIAL_CMD_STOP_DISCONNECT      ="{\"cmd\":\"stop recording disconnect\"}"
SERIAL_ACK_OK                   ="{\"ack\":\"ok\"}"

EVT_DEV_CON_SETUP_DONE			="evt setup done"
EVT_DEV_DISCONNECT				="evt disconnect"

# SERIAL_CMD_START_RECORDING      ="{\"cmd\":\"start recording\"}"
# SERIAL_CMD_STOP_RECORDING       ="{\"cmd\":\"stop recording\"}"


# EVT_WIN_BTN_FLASH_LED	        = "evt_win_btn_click_flash_led"
# EVT_WIN_BTN_START_RECORDING	    = "evt_win_btn_click_start_recording"
# EVT_WIN_BTN_STOP_RECORDING	    = "evt_win_btn_click_stop_recording"
# EVT_WIN_BTN_STOP_DISCONNECT 	= "evt_win_btn_click_stop_disconnect"
DUMMY_STR 						= '0'



EVT_WIN_BTN_CLICK_OPEN_CLOSE	= "evt_win_btn_click_open_close"
EVT_WIN_BTN_CLICK_SET_MAC		= "evt_win_btn_click_set_mac"
EVT_WIN_CMD_TO_BLE				= "evt_win_cmd_to_ble"
EVT_WIN_QUIT					= "evt_win_quit"
EVT_WIN_MI_TRAIN				= "evt_win_mi_trian"
EVT_WIN_MI_TEST					= "evt_win_mi_test"
EVT_WIN_EYE_OC					= "evt_win_eye_oc"
EVT_WIN_AUOB					= "evt_win_auditory_odd_ball"
EVT_WIN_CURCTRL_TRAIN 			= "evt_win_btn_curctrl_train"
EVT_WIN_CURCTRL					= "evt_win_btn_curctrl"

EVT_WIN_GENERATW_MODEL			= "evt_win_generate_model"
EVT_WIN_GENERATW_CURCTRL_MODEL	= "evt_win_generate_curctrl_model"

DUMMY_INT 						= 0
# WIN_CMD_SERIAL_OPEN			    = 1
# WIN_CMD_SERIAL_CLOSE		    = 2
# WIN_CMD_SET_MAC				    = 3

EVT_SERIAL_OPEN_SUC				="evt_serial_open_suc"
EVT_SERIAL_OPEN_FAILED			="evt_serial_open_failed"
EVT_SERIAL_CLOSE_SUC			="evt_serial_close_suc"
SERIAL_SIMULATOR				="signal generator"

EVT_SERIAL_TEST          		="test"


# SERIAL_CMD_REQUEST_INFO         ="{\"request\":\"device information\"}"

CH_NUM							=8



LOG_INFO_INGNORE				="state ok"

JSON_RECV_KEY_MAC               ="mac"
JSON_RECV_KEY_PACKET_NUM        ="pkn"

JSON_RECV_KEY_EVT				="evt"
JSON_RECV_KEY_ALPHA_AMP			="alp"

JSON_RECV_KEY_DATA				="data"
JSON_RECV_KEY_DATA_EEG			="eeg"
JSON_RECV_KEY_DATA_ACC			="acc"
JSON_RECV_KEY_CH_NUM			="chn"

JSON_COM_KEY_STR				="COM"
JSON_MAC_KEY_STR				="MAC"

JSON_CH_SHOW_KEY_STR			="CH"


Json_file_name					="user_config.json"
Json_file_curve_form_setting	="user_config_curve_form.json"

DUMMY_MAC						="00:00:00:00:00:00"