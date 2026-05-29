# hardcoded tutorial level
# 0-1, 0-2, 0-3, 0-4
from mainMenu.subMenu.settings import loadSettings
from gameHelpers.display.dialogueBox import drawDialogueBox
import const, os, pygame


tutorialDialogueFirstOn  = True
tutorialDialogueSecondOn = True
tutorialDialogue2xOn     = True
tutorialDialogueArrowOn  = True
tutorialGotGunOn         = True

tutorialMatching ={
    1:
    [[-1, 12, -2],   #basic movement
    [1 , 1 ,  1]],
    2:
    [[-1, -7, -8, -2],   #gun teach breakables to the player and interactions
     [1, 1, 1, 1]],
    3:
    [[-1,-9,-2],           #shop and first enemy
     [1,-4, 1]],
    4:
    [[-1, 33, -3,-2],           #simple miniboss
     [1,-4,1,1]]

}

loadedSettings = loadSettings()

tutorialDialogueFirst =  (
    f"welcome to The Amazing Digital Dungeon! to interact use [{pygame.key.name(loadedSettings['keybinds']['interact']).upper()}],"
    f" to shoot use [{pygame.key.name(loadedSettings['keybinds']['shoot']).upper()}] but youll need a gun for that."
    f" Worry not (main character)! You can obtain a gun on the next layer, just go to the room on the right "
    f"then up the elevator and interact with the chest. Also, if you hate me you can press "
    f"[{pygame.key.name(loadedSettings['keybinds']['interact']).upper()}] to skip my yap sesh. "
    f" Also you may not pass while im  yapping because I said so. Oh you're still here! Let me tell you a secret..."
    f" You can dodge by pressing [{pygame.key.name(loadedSettings['keybinds']['dodge']).upper()}]"
)

tutorialDialogueSecond = (
    f"Oh my! You made it! I know, such treacherous journey to get here! I am absolutely flabbergasted at your ability to navigate"
    f" these most complex mazes... Oh would you look at that——its a chest! I bet you could get a gun from that chest by interacting"
    f" with it. Use [{pygame.key.name(loadedSettings['keybinds']['interact']).upper()}] to open it. I'll see you on the other side."
)

tutorialDialogueSecondSecond = (
    f"Amazing! You made it and got yourself a nice gun! I hope you remember how to shoot because i'm not going to remind you."
    f"Oh look! An impassible barrier! I sure hope that theres some way to pass it... otherwise that would be really bad game design..."
    f"hey remember that gun you got? those boxes look breakable. I sure wonder what would happen if you shot them"
)

tutorialArrowRoom  = (
    f"Oh look! a big arrow! I sure wonder what it's pointing at! I bet there could be something good... or someone important... Anyways!"
    f" There will be enemies in the next room, beware!"
)

def resetTutorial():
    global tutorialDialogueFirstOn,tutorialDialogueSecondOn,tutorialDialogue2xOn,tutorialDialogueArrowOn,tutorialGotGunOn
    tutorialDialogueFirstOn  = True
    tutorialDialogueSecondOn = True
    tutorialDialogue2xOn     = True
    tutorialDialogueArrowOn  = True
    tutorialGotGunOn         = True

def runTutorial(screen, clock, currentLayerID, currentRoomID, playerObj):
    # tutorial first
    global tutorialDialogueFirstOn,tutorialDialogueSecondOn,tutorialDialogue2xOn,tutorialDialogueArrowOn,tutorialGotGunOn

    if currentRoomID == 12 and currentLayerID == [0, 1]:
        if tutorialDialogueFirstOn:
            finishedDial = drawDialogueBox(screen, tutorialDialogueFirst, clock, typewrite=True,
                                           image=os.path.join(const.caineDir, "caineFirst.png"))
            if finishedDial:
                tutorialDialogueFirstOn = False
                playerObj.doorsLocked = False

    # tutorial floor 2
    if currentLayerID[1] == 2:
        if currentRoomID == -7:
            if tutorialDialogueSecondOn:
                playerObj.doorsLocked = True
                finishedDial = drawDialogueBox(screen, tutorialDialogueSecond, clock, typewrite=True,
                                               image=os.path.join(const.caineDir, "caineFirst.png"))
                if finishedDial:
                    tutorialDialogueSecondOn = False
                    playerObj.doorsLocked = False

            if len(playerObj.obtainedGuns) > 0 and tutorialGotGunOn:
                finishedDial = drawDialogueBox(screen, "WOWZERS ! YOU GOT A GUN!!!!!", clock, typewrite=True,
                                               image=os.path.join(const.caineDir, "bubbleFirst.png"))
                if finishedDial:
                    tutorialGotGunOn = False

        if currentRoomID == -8:
            if tutorialDialogue2xOn:
                playerObj.doorsLocked = True
                finishedDial = drawDialogueBox(screen, tutorialDialogueSecondSecond, clock, typewrite=True,
                                               image=os.path.join(const.caineDir, "broadCaster.png"))
                if finishedDial:
                    tutorialDialogue2xOn = False
                    playerObj.doorsLocked = False

    if currentLayerID[1] == 3:

        if currentRoomID == -9:
            if tutorialDialogueArrowOn:
                playerObj.doorsLocked = True
                finishedDial = drawDialogueBox(screen, tutorialArrowRoom, clock, typewrite=True)
                if finishedDial:
                    tutorialDialogueArrowOn = False
                    playerObj.doorsLocked = False