import pygame
import const
import mainMenu.theme as theme

def drawDialogueBox(screen, text, image=None, typewrite=True):
    if not hasattr(drawDialogueBox, "charIndex"):
        drawDialogueBox.charIndex = 0

    if not hasattr(drawDialogueBox, "timer"):
        drawDialogueBox.timer = 0

    if not hasattr(drawDialogueBox, "finished"):
        drawDialogueBox.finished = False

    if not hasattr(drawDialogueBox, "lastText"):
        drawDialogueBox.lastText = ""

    if drawDialogueBox.lastText  != text:
        drawDialogueBox.charIndex = 0
        drawDialogueBox.timer     = 0
        drawDialogueBox.finished  = False
        drawDialogueBox.lastText  = text




    #sizing
    screenW, screenH = screen.get_size()
    boxW = int(screenW)
    boxH = int(screenH * 0.25)
    boxX = (screenW - boxW) // 2
    boxY = screenH - boxH - 20

    #draw box
    pygame.draw.rect(screen, theme.bgMid, (boxX, boxY, boxW, boxH), border_radius=10)
    pygame.draw.rect(screen, theme.accentDim, (boxX, boxY, boxW, boxH), 3, border_radius=10)
    imgSize = int(boxH * 0.75)
    imgRect = pygame.Rect(boxX + 15, boxY + (boxH - imgSize) // 2,imgSize,imgSize)

    if image is not None:
        scaledImg = pygame.transform.scale(image,(imgSize, imgSize))
        screen.blit(scaledImg,imgRect)







    #typeWrite
    fullText = text

    if typewrite and not drawDialogueBox.finished:
        drawDialogueBox.timer += 1


        typeWriterSpeed = 2 #higher is slower


        if drawDialogueBox.timer >= typeWriterSpeed:
            drawDialogueBox.timer = 0

            if drawDialogueBox.charIndex < len(fullText):
                drawDialogueBox.charIndex += 1
            else:
                drawDialogueBox.finished = True

        shownText = fullText[:drawDialogueBox.charIndex]

    else:
        shownText = fullText
        drawDialogueBox.finished = True


    #genshin would never
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:

        if not drawDialogueBox.finished:
            drawDialogueBox.charIndex = len(fullText)
            drawDialogueBox.finished = True

        else:
            drawDialogueBox.charIndex = 0
            drawDialogueBox.timer = 0
            drawDialogueBox.finished = False
            drawDialogueBox.lastText = ""

            return True

    font        = pygame.font.SysFont(const.fontTextBasic, 30)
    textX       = imgRect.right + 15
    textY       = boxY + 20

    maxWidth    = boxW - imgSize - 50

    words       = shownText.split(" ")
    lines       = []
    currentLine = ""

    for word in words:
        testLine = currentLine + word + " "

        if font.size(testLine)[0] <= maxWidth:
            currentLine = testLine
        else:
            lines.append(currentLine)
            currentLine = word + " "

    lines.append(currentLine)

    for i, line in enumerate(lines):
        rendered = font.render(line, True, theme.textPrimary)
        screen.blit(rendered, (textX, textY + (i * 30)))

    if drawDialogueBox.finished:
        continueText = font.render("[SPACE]", True, (200, 200, 200))
        screen.blit(continueText,(boxX + boxW - 110, boxY + boxH - 35))

    return False


