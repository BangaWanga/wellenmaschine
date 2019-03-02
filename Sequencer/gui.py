import pygame

class Gui:
    def __init__(self):
        (width, height) = (500, 600)
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill((255, 255, 255))

        # initialize window geometry
        self.initBoardRects(left=50, top=50, width=400)     # init chessboard
        self.resetButtonRect = pygame.Rect(200, 500, 100, 50)   # init rect of reset button
        self.notchDownButtonRect = pygame.Rect(100, 500, 50, 50)   # init rect of notch down button
        self.notchUpButtonRect = pygame.Rect(350, 500, 50, 50)   # init rect of noth up button


    def initBoardRects(self, left, top, width):
        rectWidth = int(width / 8.)
        self.boardRects = []
        for yIndex in range(8):
            for xIndex in range(8):
                self.boardRects.append(
                    pygame.Rect((left + xIndex * rectWidth, left + yIndex * rectWidth, rectWidth, rectWidth)))

    def draw_window(self):
        self.drawBoard(self.screen)
        self.drawButtons(self.screen)
        pygame.display.flip()

    def drawButtons(self, screen):
        bgcol = (90, 155, 255)

        # draw reset (or 'tap' button)
        pygame.draw.rect(screen, bgcol, self.resetButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('Tap Beat', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.resetButtonRect.x + self.resetButtonRect.width / 2
        textrect.centery = self.resetButtonRect.y + 0.9 * self.resetButtonRect.height / 2
        screen.blit(text_surface, textrect)

        # draw notch down button
        pygame.draw.rect(screen, bgcol, self.notchDownButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('<<', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.notchDownButtonRect.x + self.notchDownButtonRect.width / 2
        textrect.centery = self.notchDownButtonRect.y + self.notchDownButtonRect.height / 2
        screen.blit(text_surface, textrect)

        # draw notch up button
        pygame.draw.rect(screen, bgcol, self.notchUpButtonRect)
        # draw label
        font = pygame.font.SysFont('Times New Roman', 20)
        text_surface = font.render('>>', True, (255, 255, 255, 255), bgcol)
        textrect = text_surface.get_rect()
        textrect.centerx = self.notchUpButtonRect.x + self.notchUpButtonRect.width / 2
        textrect.centery = self.notchUpButtonRect.y + self.notchUpButtonRect.height / 2
        screen.blit(text_surface, textrect)

    def drawBoard(self, screen):
        """ Method for optionally drawing the current state of the sequencer """

        # below, draw a light green where the current step is (blit this surface there)
        currentStepSurf = pygame.Surface((self.boardRects[0].width, self.boardRects[0].width))
        currentStepSurf.set_alpha(100)
        currentStepSurf.fill((0, 255, 0))


        # ignoring this because track is part of the sequencer
        # where should it go?????

        # # loop through the chessboard fields (stored in self.boardRects list, row-wise)
        # for i, currentRect in enumerate(self.boardRects):
        #     # Check if the corresponding sequence has a 1 for the current field
        #     isRed = self.track.sequences[3 * (i // 16), i % 16]
        #     isGreen = self.track.sequences[3 * (i // 16) + 1, i % 16]
        #     isBlue = self.track.sequences[3 * (i // 16) + 2, i % 16]
        #
        #     if isRed or isGreen or isBlue:
        #         pygame.draw.rect(screen, (isRed * 255, isGreen * 255, isBlue * 255), currentRect)
        #     else:  # if not set, just draw black or white chessboard-style
        #         isWhite = ((i + (i // 8) % 2) % 2 == 0)
        #         pygame.draw.rect(screen, (isWhite * 255, isWhite * 255, isWhite * 255), currentRect)
        #
        #     # draw a light green where the current step is
        #     if i % 16 == self.count:
        #         screen.blit(currentStepSurf, currentRect)
