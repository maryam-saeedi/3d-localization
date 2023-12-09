import pygame
import cv2
import numpy as np
import time
import subprocess

class ImageRect:
    def __init__(self,base_image_path,hover_image_path,select_image_path,width,height,pos):
        
        #image
        self.base_image = cv2.resize(cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED), (width,height))
        self.hover_image = cv2.resize(cv2.imread(hover_image_path, cv2.IMREAD_UNCHANGED), (width,height))
        self.select_image = cv2.resize(cv2.imread(select_image_path, cv2.IMREAD_UNCHANGED), (width,height))
        self.width = width
        self.height = height
        self.pos = pos

    def draw(self, screen, status="base"):
        if status == "base":
            image = self.base_image
        elif status == "hover":
            image = self.hover_image
        elif status == "select":
            image = self.select_image

        if len(image.shape)==2:
            image = np.stack((image,image,image,image), axis=-1)
            mode = "BGRA"
        elif image.shape[2]==4:
            mode = "BGRA"
        elif image.shape[2]==3:
            mode = "BGR"
        screen.blit(pygame.image.frombuffer(image.tobytes(), (self.width,self.height), mode), self.pos)

    def get_rect(self):
        return [self.pos[0], self.pos[1], self.width, self.height]

class ImageButton:
    def __init__(self,image, hover_image ,width,height,pos,func, clickable=True, **args):
        #Core attributes 
        self.pressed = False

        #image
        # image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        image = cv2.resize(image, (width,height))
        # hover_image = cv2.imread(hover_image_path, cv2.IMREAD_UNCHANGED)
        hover_image = cv2.resize(hover_image, (width,height))
        self.image = image
        self.hover_image = hover_image
        self.width = width
        self.height = height
        self.pos = pos
        self.clickable = clickable
        self.isClicked = 0

        # function
        self.func = func
        self.args = args

    def draw(self, screen):
        screen.blit(pygame.image.frombuffer(self.image.tobytes(), (self.image.shape[1],self.image.shape[0]), "RGBA"), self.pos)
        if self.clickable:
            self.check_click()
        if self.isClicked:
            screen.blit(pygame.image.frombuffer(self.hover_image.tobytes(), (self.width,self.height), "RGBA"), self.pos)

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        top_rect = pygame.Rect(self.pos,(self.width,self.height))
        if top_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed == True:
                    self.func(**self.args)
                    self.isClicked = True
                    self.pressed = False

class Button:
    def __init__(self,text,width,height,pos,func, clickable=True, color='#50938a', **args):
        #Core attributes 
        self.pressed = False
        self.original_y_pos = pos[1]
        self.clickable = clickable

        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.color = color
        self.disable_color = '#798483'

        #text
        self.text_surf = pygame.font.Font(None,32).render(text,True,'#ffffff')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

        # function
        self.func = func
        self.args = args

    def draw(self, screen):
        # elevation logic 
        self.top_rect.y = self.original_y_pos
        self.text_rect.center = self.top_rect.center 

        pygame.draw.rect(screen, self.color if self.clickable else self.disable_color , self.top_rect,border_radius = 6)
        screen.blit(self.text_surf, self.text_rect)
        if self.clickable:
            self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            # self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed == True:
                    self.func(**self.args)
                    self.pressed = False

    
class InputBox:

    def __init__(self, x, y, w, h, func=None, enable=True, color_active=(0,0,0), color_inactive=(50,50,50), text='', **args):
        self.FONT = pygame.font.Font('tahoma.ttf', 28)
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = self.color_active
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.enable = enable
        self.func = func
        self.args = args
        self.cursor_blink_interval = 70
        self.cursor_blink = 0

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = True
                    self.text = ''
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = self.color_active if self.active else self.color_inactive
            if event.type == pygame.KEYDOWN:
                if self.active:
                    # if event.key == pygame.K_RETURN:
                    #     if self.func:
                    #         self.func(**self.args)
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        unicode_char = event.unicode
                        if unicode_char and unicode_char.isprintable():
                            self.text += unicode_char
                            if self.func:
                                self.func(**self.args)
        
    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.FONT.render(self.text, True, self.color).get_width()+10)
        self.rect.w = width

    def draw(self, screen, events):
        # Blit the text.

        text = self.text
        if self.active:
            if self.cursor_blink < self.cursor_blink_interval//2:
                text+='|'
            self.cursor_blink = (self.cursor_blink+1)%self.cursor_blink_interval
        pygame.draw.rect(screen, (230,230,230,230), self.rect ,border_radius = 6)
        screen.blit(self.FONT.render(text, True, self.color), (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        # pygame.draw.rect(screen, self.color, self.rect, 2)
        if self.enable:
            self.handle_event(events)
   
class Label:

    def __init__(self, x, y, w, h, color=(0,0,0), text=''):
        self.FONT = pygame.font.Font(None, 28)
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        
    def draw(self, screen):
        # Blit the text.
        y = self.y+5
        for line in self.text.split('\n'):
            text = self.FONT.render(line, True, self.color)
            screen.blit(text, (self.x+5, y))
            h = text.get_rect().height
            y += h+10

