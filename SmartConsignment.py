from phBot import *
import QtBind
from threading import Timer
import struct
import time
import math
import itertools

pName = 'SmartConsignment'
pVersion = '1.0.0'
pUrl = 'https://raw.githubusercontent.com/rawsly/phbot-plugins/main/SmartConsignment.py'

# ACTION CONSTANTS
SELECT_CONS = ['0x7045', '24 02 00 00']
ENTER_CONS = ['0x7046', '24 02 00 00 23']
# CLOSE_SEARCH = ['0x7507']
# CLOSE_CONSIGMENT = ['0x704B', '24 02 00 00']
SEARCH_OPCODE = '0x750C'
BUY_OPCODE = '0x750A'
SEARCH_RESULT_OPCODE = '0xB50C'
BUY_PACK_START_INDEX_LEN = [1, 2]
BUY_PACK_CHAR_INDEX_LEN = [2, -1]
BUY_PACK_CHAR_SUFFIX_INDEX_LEN = [0, 4]
BUY_PACK_ITEM_INDEX_LEN = [3, 4]
NUMBER_OF_ELEMENTS_FOR_EACH_DATA_EL = 7
NUMBER_OF_ATTEMPS = itertools.count()
IS_SEARCH_AVAILABLE = True
DURATION_TO_SEARCH_AGAIN_AS_SEC = 11

# FILTER CONSTANTS
ALCHEMY_ATTRIBUTE = [SEARCH_OPCODE, "XX 00 25 00 00 00 ** 00 00"] # kırmızı taşlar
ALCHEMY_ELIXIR = [SEARCH_OPCODE, "XX 00 21 00 00 00 00 00 00"] # elixir
ALCHEMY_ALCHEMIC = [SEARCH_OPCODE, "XX 00 24 00 00 00 ** 00 00"] # yeşil taşlar

CH_ACC_NECKLACE = [SEARCH_OPCODE, "XX 00 0A 00 00 00 ** 00 00"] # necklace
CH_ACC_EARRING = [SEARCH_OPCODE, "XX 00 0B 00 00 00 ** 00 00"] # earring
CH_ACC_RING = [SEARCH_OPCODE, "XX 00 0C 00 00 00 ** 00 00"] # necklace

CH_SWORD = [SEARCH_OPCODE, "XX 00 01 00 00 00 ** 00 00"] # sword
CH_BLADE = [SEARCH_OPCODE, "XX 00 02 00 00 00 ** 00 00"] # blade
CH_SPEAR = [SEARCH_OPCODE, "XX 00 03 00 00 00 ** 00 00"] # spear
CH_GLAIVE = [SEARCH_OPCODE, "XX 00 04 00 00 00 ** 00 00"] # glaive
CH_BOW = [SEARCH_OPCODE, "XX 00 05 00 00 00 ** 00 00"] # bow
CH_SHIELD = [SEARCH_OPCODE, "XX 00 06 00 00 00 ** 00 00"] # shield

CH_ARMOR = [SEARCH_OPCODE, "XX 00 07 00 00 00 ** 00 00"] # armor
CH_PRO = [SEARCH_OPCODE, "XX 00 08 00 00 00 ** 00 00"] # pro
CH_GARMENT = [SEARCH_OPCODE, "XX 00 09 00 00 00 ** 00 00"] # garment

JOB_WEAPON = [SEARCH_OPCODE, "XX 00 3A 00 00 00 00 00 00"] # job weapon
JOB_PRO = [SEARCH_OPCODE, "XX 00 3B 00 00 00 ** 00 00"] # job pro items
JOB_ACC = [SEARCH_OPCODE, "XX 00 3C 00 00 00 ** 00 00"] # job item acc
JOB_UPGRADE = [SEARCH_OPCODE, "XX 00 3D 00 00 00 ** 00 00"] # job plus + blue
JOB_ITEMS = [SEARCH_OPCODE, "XX 00 3E 00 00 00 00 00 00"] # stone, ticket etc.

gui = QtBind.init(__name__, pName)



# UI ELEMENTS
searchBtn = QtBind.createButton(gui, 'onSearch', 'Search', 526, 20) # search button

WINDOW_HEIGHT = 230
WINDOW_WIDTH = 500
WINDOW_LEFT_START = 100
WINDOW_TOP_START = 50
DROPDOWN_WIDTH = 150
DROPDOWN_HEIGHT = 21
UI_ELEMENTS_GAP = 10

typeDropdown = QtBind.createCombobox(gui, WINDOW_LEFT_START, DROPDOWN_HEIGHT, DROPDOWN_WIDTH, DROPDOWN_HEIGHT) # type dropdown
degreeDropdown = QtBind.createCombobox(gui, WINDOW_LEFT_START + DROPDOWN_WIDTH + UI_ELEMENTS_GAP, DROPDOWN_HEIGHT, DROPDOWN_WIDTH, DROPDOWN_HEIGHT) # degree dropdown

ALL_DEGREES = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
JOB_DEGREES = ["1", "2", "3"]
DEFAULT_DEGREES = ["1"]

LAST_DROPDOWN_VALUE = 'Attribute Stone'

SEPERATOR = '---'

DROPDOWN_ITEMS = dict({
	'Attribute Stone': ALCHEMY_ATTRIBUTE, 
	'Alchemic Stone': ALCHEMY_ALCHEMIC,
	'Elixir': ALCHEMY_ELIXIR,
	'-1-': [],
	'Necklace': CH_ACC_NECKLACE,
	'Earring': CH_ACC_EARRING,
	'Ring': CH_ACC_RING,
	'-2-': [],
	'Sword': CH_SWORD,
	'Blade': CH_BLADE,
	'Spear': CH_SPEAR,
	'Glaive': CH_GLAIVE,
	'Bow': CH_BOW,
	'Shield': CH_SHIELD,
	'-3-': [],
	'Armor': CH_ARMOR,
	'Protector': CH_PRO,
	'Garment': CH_GARMENT,
	'-4-': [],
	'Job Weapon': JOB_WEAPON,
	'Job Protector': JOB_PRO,
	'Job Accessory': JOB_ACC,
	'Job Upgrade': JOB_UPGRADE,
	'Job Items': JOB_ITEMS
})

for key in DROPDOWN_ITEMS.keys():
	if key.startswith('-'):
		QtBind.append(gui, typeDropdown, SEPERATOR)
	else:
		QtBind.append(gui, typeDropdown, key)

for degree in ALL_DEGREES:
	QtBind.append(gui, degreeDropdown, degree)

searchResults = QtBind.createList(gui, WINDOW_LEFT_START, WINDOW_TOP_START, WINDOW_WIDTH, WINDOW_HEIGHT)

# QtBind.setEnabled(gui, searchBtn, False)


def onSearch():
	update_search_status(False)
	log(str(NUMBER_OF_ATTEMPS))
	if str(NUMBER_OF_ATTEMPS) == 'count(0)':
		select_consignment()
	Timer(1.5, search_consignment, ()).start()
	Timer(1.5 + DURATION_TO_SEARCH_AGAIN_AS_SEC, update_search_status, [True]).start()

def update_search_status(status):
	QtBind.setEnabled(gui, searchBtn, status)

def select_consignment():
	Timer(0.5, custom_inject_joymax, [SELECT_CONS]).start()
	Timer(1, custom_inject_joymax, [ENTER_CONS]).start()

def search_consignment():
	typeValue = QtBind.text(gui, typeDropdown)
	degreeValue = QtBind.text(gui, degreeDropdown)
	if typeValue != SEPERATOR:
		custom_inject_joymax(format_opcode_degree(DROPDOWN_ITEMS[typeValue], '{:02X}'.format(degreeValue)))


def inject(strOpcode, strData, encrypted=False):
	if strOpcode and strData:
		data = bytearray()
		operation_code = int(strOpcode, 16)
		strData = strData.replace(' ','')
		strDataLen = len(strData)
		if not strDataLen % 2 == 0:
			log("Plugin: Error, data needs to be a raw of bytes")
			return
		for i in range(0,int(strDataLen),2):
			data.append(int(strData[i:i+2],16))
		inject_joymax(operation_code, data, encrypted)


def parse_search_result(data):
    return partition_arr(split_trim_data(data), NUMBER_OF_ELEMENTS_FOR_EACH_DATA_EL)

def format_opcode_degree(operation, param="00"):
	operation_code, data = operation[0], operation[1]
	if increase_number_of_attempts() == 0:
		data = data.replace("XX", "01")
	else:
		data = data.replace("XX", "02")

	data = data.replace("**", param)
	return [operation_code, data]

def custom_inject_joymax(operation, encrypted=False):
	# Opcode or Data is not empty
	strOpcode, strData = operation[0], operation[1]
	inject(strOpcode, strData, encrypted)

def split_trim_data(data):
    actual_data = data[8:]
    arr = actual_data.split("00")
    filtered_arr = [item for item in arr if item is not " "]

    return [item.strip() for item in filtered_arr][:-1] # removing unneccessary last element
        
def partition_arr(arr, n):
    result = list()
    for i in range(len(arr) // n):
        start = i * n
        end = start + n
        result.append(arr[start:end])
    
    return result

def increase_number_of_attempts():
	return next(NUMBER_OF_ATTEMPS)


log("SmartConsignment is loaded.")