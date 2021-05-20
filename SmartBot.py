from phBot import *
import QtBind
from threading import Timer
import json
import os
from urllib import request, parse

pName = 'SmartBot'
pVersion = '1.0.0'
pUrl = 'https://raw.githubusercontent.com/rawsly/phbot-plugins/main/SmartBot.py'

path = get_config_dir() + pName + "\\"
gui = QtBind.init(__name__, pName)
apiUrl = "http://localhost:8000"

emailLabel = QtBind.createLabel(gui,'Email', 30, 30)
emailTextbox = QtBind.createLineEdit(gui, "rawsly@gmail.com", 30, 50, 200, 20)
PasswordLabel = QtBind.createLabel(gui, 'Password', 30, 80)
PasswordTextbox = QtBind.createLineEdit(gui, "123456", 30, 100, 200, 20)
connectBtn = QtBind.createButton(gui, 'handleConnectionBtn', 'Connect', 30, 125) # search button

connectionStatus = False

def handleConnectionBtn():
  if connectionStatus == True:
    disconnect()
    enableFields()
  else:
    userId = connect()
    if userId is not None:
      char = getCharData(userId)
      if char is not None:
        saveConfig(userId, char['charId'])
        disableFields()
        updateCharData()
      else:
        disconnect()
        enableFields()
  
def connect():
  data = {
    'email': QtBind.text(gui, emailTextbox),
    'password': QtBind.text(gui, PasswordTextbox)
  }
  return post('/connect', data)

def createChar(userId):
  name = get_character_data()['name']
  server = get_character_data()['server']
  data = { "userId": userId, "name": name, "server": server }
  return post('/create-char', data)

def getCharData(userId):
  char = createChar(userId)
  if char is None or char == "":
    log("Create failed.")
    return None
  else:
    global connectionStatus
    connectionStatus = True
    return char

def disconnect():
  global connectionStatus
  connectionStatus = False
  charData = readConnectedCharData()
  isDisconnected = post('/disconnect', charData)
  if isDisconnected:
    clearConfig()

def disableFields():
  QtBind.setEnabled(gui, emailTextbox, False)
  QtBind.setEnabled(gui, PasswordTextbox, False)
  QtBind.clear(gui, emailTextbox)
  QtBind.clear(gui, PasswordTextbox)
  QtBind.setText(gui, connectBtn, "Disconnect")

def enableFields():
  QtBind.setEnabled(gui, emailTextbox, True)
  QtBind.setEnabled(gui, PasswordTextbox, True)
  QtBind.setText(gui, connectBtn, "Connect")

def getConfig():
	return path + get_character_data()['server'] + "_" + get_character_data()['name'] + ".json"

def saveConfig(userId, charId):
  data = {}
  data["userId"] = userId
  data["charId"] = charId
  with open(getConfig(),"w") as f:
    f.write(json.dumps(data, indent=4))

def loadConfig():
  data = readConnectedCharData()
  if "userId" in data and "charId" in data and data['userId'] != "" and data['charId'] != "":
    char = getCharData(data['userId'])
    if char is not None:
      disableFields()
      updateCharData()

def clearConfig():
  saveConfig("", "")

Timer(1.0, loadConfig, ()).start()

def terminate():
	os.kill(os.getpid(), 9)

def post(route, data, headers={ "Content-Type": "application/json", "Accept": "application/json" }):
  url = apiUrl + route
  req = request.Request(url=url, data=json.dumps(data).encode('utf-8'), headers=headers)
  response = request.urlopen(req)
  return json.loads(response.read().decode('utf8'))

def readConnectedCharData():
  if os.path.exists(getConfig()):
    data = {}
    with open(getConfig(),"r") as f:
      data = json.load(f)
      return data

def updateCharData():
  data = readConnectedCharData()
  charData = get_character_data()
  charPos = get_position()
  data['charData'] = charData
  data['charData']['position'] = charPos
  post('/update-char-data', data)
  Timer(5.0, updateCharData, ()).start()

def create_path():
  if not os.path.exists(path):
    os.makedirs(path)
    log('Plugin: [%s] folder has been created' % name)

create_path()

log("Plugin: SmartBot is loaded successfully.")