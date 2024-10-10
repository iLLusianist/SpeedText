import pygame as pg
import random
import time
import sys
import sqlite3

class Game:
    def __init__(self):
        #Базовые значения
        print('*** INITIALIZATION GAME ***')
        self.closeGame = False
        self.gameStart = False
        self.gameDone = False 
                
        self.MAX_NAME_LENGTH = 11
        self.LEADERBOARD_COUNT = 33

        #Подключение к БД
        self.connection = sqlite3.connect('SpeedText_Leaderboard.db')
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Leaderboard (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                time INTEGER
                )
                ''')
        except:
            print("*** TABLE 'Leaderboard' NOT CREATED ***")
            sys.exit()
        else:
            print("*** TABLE 'Leaderboard' CREATED ***")
        self.connection.commit()       

        #Базовые значения 
        self.WIDTH = 1400
        self.HEIGHT = 900
        self.BACKGROUND_COLOR = (17, 25, 28)
        self.TEXT_COLOR = (168, 208, 224)
        self.TEXT_SIZE = 40
        self.MENU_TEXT_SIZE = 60
        self.MENU_TEXT_INDENT = 10

        pg.init()

        #Создание шрифтов
        self.fontMenu = pg.font.SysFont("Arial", self.MENU_TEXT_SIZE)
        self.fontGame = pg.font.SysFont("Arial", self.TEXT_SIZE)
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        
        #Определение границ кнопок на главном меню
        self.enterBox = []
        self.menuButtons = [                                                                        
            [self.WIDTH/2-self.fontMenu.size("Старт")[0]/2, 
                self.HEIGHT/2-self.MENU_TEXT_SIZE*1.5-self.MENU_TEXT_INDENT, 
                self.fontMenu.size("Старт")[0], 
                60],
            [self.WIDTH/2-self.fontMenu.size("Рекорды")[0]/2, 
                self.HEIGHT/2-self.MENU_TEXT_SIZE/2, 
                self.fontMenu.size("Рекорды")[0], 
                60],
            [self.WIDTH/2-self.fontMenu.size("Выход")[0]/2, 
                self.HEIGHT/2+self.MENU_TEXT_SIZE/2+self.MENU_TEXT_INDENT, 
                self.fontMenu.size("Выход")[0], 
                60]
        ]
             
    def drawText(self, screen, msg, positionX, positionY, size, color):
        #Рисуем текст по центру (ширина) экрана
        font = pg.font.Font(None, size)
        text = font.render(msg, 1, color)
        textRect = text.get_rect(center=(positionX, positionY))
        screen.blit(text, textRect)

    def getText(self):
        #Пробуем открыть файл с текстом задания и берем случайную строку
        try: 
            f = open('textList.txt').read()
        except:
            print(f'*** FILE {f} NOT OPENED ***')
            sys.exit()
        else:
            print(f"*** FILE 'textList.txt' OPENED ***")
        lines = f.split("\n")
        line = random.choice(lines)
        return line

    def getSuf(self, time):
        #Определение окончания слова в зависимости от числа (минут(а/ы))
        if (time // 10 >=2 and time % 10 == 1) or (time == 1):
            return 'а' 
        elif (time % 10 in [2,3,4]) and (time // 10 != 1):
            return 'ы'
        else:
            return ''
         
    def gameComplited(self):
        #Вывод итогов
        self.screen.fill(self.BACKGROUND_COLOR)
        self.drawText(self.screen, 
                      f"Поздравляю, {self.name}. Со старта прошло: {self.minutes} минут{self.getSuf(self.minutes)} {self.seconds} секунд{self.getSuf(self.seconds)} ", 
                      self.WIDTH/2, self.HEIGHT/2, self.TEXT_SIZE, self.TEXT_COLOR)

        #Попытка записать результат в БД
        try: 
            self.cursor.execute('INSERT INTO Leaderboard (username, time) VALUES (?, ?)', (self.name, self.minutes*60+self.seconds))
        except:
            print(f"***  CAN'T ADD {self.name} / {self.minutes*60+self.seconds} ***")
        else:
            print(f'***  SUCCESSFULLY ADDED {self.name} / {self.minutes*60+self.seconds} ***')
        self.connection.commit()

        pg.display.update()
        time.sleep(3)
        self.runMenu()

    def drawGameScreen(self, started):
        #Вывод меню ввода имени
        self.screen.fill(self.BACKGROUND_COLOR)
        self.drawText(self.screen, self.taskText, self.WIDTH/2, self.HEIGHT/2-100, self.TEXT_SIZE, self.TEXT_COLOR)
        pg.draw.rect(self.screen, self.TEXT_COLOR, self.enterBox, 1)
        if started:
            self.drawText(self.screen, self.inputText, self.WIDTH/2, self.HEIGHT/2, self.TEXT_SIZE, self.TEXT_COLOR)

    def runGame(self):
        #Базовые значения
        self.inputText = ''
        self.taskTextList = []
        self.minutes = 0
        self.seconds = 0
        self.startTime = None
        self.elapsedTime = None
        self.gameDone = False

        #Получение случайного текста и преобразование его в список (перечисленние с конца)
        self.taskText = self.getText()                                                                     
        self.taskTextList = list(self.taskText[::-1])         
        self.enterBox = [self.WIDTH/2-self.fontGame.size(str(self.taskText))[0]/2-15,
                         self.HEIGHT/2-self.TEXT_SIZE/2-15,
                         int(str(self.fontGame.size(self.taskText)[0]))+30,
                         self.TEXT_SIZE+30]

        #Если не нажата кнопка "Начать" или Enter, вывод текста задания и кнопки для начала
        while not self.gameStart:      
            self.drawGameScreen(0)
            self.drawText(self.screen, 'Начать', self.WIDTH/2, self.HEIGHT/2, self.TEXT_SIZE, self.TEXT_COLOR)
            self.drawText(self.screen, "Нажмите 'Начать' или нажмите клавишу Enter", self.WIDTH/2, self.HEIGHT/2+self.TEXT_SIZE*2, 20, self.TEXT_COLOR)
            self.drawText(self.screen, "Для возврата нажмите Esc", self.WIDTH/2, self.HEIGHT-self.TEXT_SIZE, 20, self.TEXT_COLOR)
            pg.draw.rect(self.screen, self.TEXT_COLOR, self.enterBox, 1)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:                                                                 
                    sys.exit()
                #Получение координат мыши для отслеживания нажатия кнопки "Начать" или Enter
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    if (x > self.enterBox[0]) and (x < self.enterBox[0]+self.enterBox[2]) and \
                       (y > self.enterBox[1]) and (y < self.enterBox[1]+self.enterBox[3]):
                            pg.draw.rect(self.screen, self.TEXT_COLOR, self.enterBox, 0)
                            pg.display.update()
                            time.sleep(0.05)
                            self.gameStart = True
                            self.startTime = time.time()  
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.runMenu()
                    if event.key == pg.K_RETURN:
                        pg.draw.rect(self.screen, self.TEXT_COLOR, self.enterBox, 0)
                        pg.display.update()
                        time.sleep(0.05)
                        self.gameStart = True
                        self.startTime = time.time() 

        #Бесконечный цикл, ослеживающий все действия
        while not self.closeGame:                                                                           
            self.drawGameScreen(1) 
            #Вывод прошедшего времени с начала
            self.drawText(self.screen, 
                         (f"Прошло: {self.minutes} минут{self.getSuf(self.minutes)} {self.seconds} секунд{self.getSuf(self.seconds)}"), 
                          self.WIDTH/2, self.HEIGHT/2-60, 25, self.TEXT_COLOR)
            if not self.gameDone:
                self.elapsedTime = time.time() - self.startTime                                         
                self.minutes = int(self.elapsedTime // 60)
                self.seconds = int(self.elapsedTime % 60)

            #Если нажат крестик в окне
            for event in pg.event.get():
                if event.type == pg.QUIT:                                                                   
                    sys.exit()
                        
                #Если нажата клавиша и она совпадает со следующей буквой по заданию
                if event.type == pg.KEYDOWN:                                                                
                    if self.gameStart:
                        if len(self.taskTextList)>=1:                                                       
                            if event.unicode == self.taskTextList[-1]:
                                self.taskTextList.pop()    
                                self.inputText += event.unicode   
                        #Если задание завершено
                        if len(self.taskTextList)==0:
                            self.drawGameScreen(1)
                            self.drawText(self.screen, 
                                         (f"Прошло: {self.minutes} минут{self.getSuf(self.minutes)} {self.seconds} секунд{self.getSuf(self.seconds)}"), 
                                         self.WIDTH/2, self.HEIGHT/2-60, 25, self.TEXT_COLOR)
                            pg.display.update()
                            time.sleep(1)
                            self.gameDone = True
                            self.gameStart = False
                            self.startTime = False                          
                            self.gameComplited()   
            
            pg.display.update()
            
    def drawNameMenu(self):
        #Базовые значения
        self.name = ''
        self.taskText = ''

        #Бесконечный цикл
        while not self.closeGame:            
            #Отрисовка меню
            self.screen.fill(self.BACKGROUND_COLOR)
            pg.draw.rect(self.screen, self.TEXT_COLOR, [self.WIDTH/2-230, self.HEIGHT/2-self.MENU_TEXT_SIZE/2, 460, self.MENU_TEXT_SIZE], 1)
            self.drawText(self.screen, 'Введите имя и нажмите Enter', self.WIDTH/2, self.HEIGHT/2+self.MENU_TEXT_SIZE, 20, self.TEXT_COLOR)
            self.drawText(self.screen, "Для возврата нажмите Esc", self.WIDTH/2, self.HEIGHT-self.TEXT_SIZE, 20, self.TEXT_COLOR)

            #Если введено имя, отображается имя игрока, если нет, отображается надпись "Введите имя"
            if not self.name:
                self.drawText(self.screen, 'Введите имя', self.WIDTH/2, self.HEIGHT/2, self.TEXT_SIZE, self.TEXT_COLOR)
            
            self.drawText(self.screen, self.name, self.WIDTH/2, self.HEIGHT/2, self.MENU_TEXT_SIZE, self.TEXT_COLOR)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:     
                    sys.exit()

                if event.type == pg.KEYDOWN:  
                    if event.key == pg.K_ESCAPE:
                        self.runMenu()
                    if event.key == pg.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == pg.K_RETURN:
                        if len(self.name)>0:
                            if len(self.name)<=self.MAX_NAME_LENGTH:
                                self.runGame()  
                    else:
                        if len(self.name)<self.MAX_NAME_LENGTH:
                            self.name += event.unicode

    def runMenu(self):
        while not self.closeGame:
            #Отрисовка меню
            self.screen.fill(self.BACKGROUND_COLOR)

            #Отрисовка текста кнопок
            self.drawText(self.screen, "Старт", self.WIDTH/2, self.HEIGHT/2-self.MENU_TEXT_SIZE-self.MENU_TEXT_INDENT, self.MENU_TEXT_SIZE, self.TEXT_COLOR)
            self.drawText(self.screen, "Рекорды", self.WIDTH/2, self.HEIGHT/2, self.MENU_TEXT_SIZE, self.TEXT_COLOR)
            self.drawText(self.screen, "Выход", self.WIDTH/2, self.HEIGHT/2+self.MENU_TEXT_SIZE+self.MENU_TEXT_INDENT, self.MENU_TEXT_SIZE, self.TEXT_COLOR)

            #Отрисовка обрамления кнопок
            pg.draw.rect(self.screen, self.TEXT_COLOR, self.menuButtons[0], 1)
            pg.draw.rect(self.screen, self.TEXT_COLOR, self.menuButtons[1], 1)
            pg.draw.rect(self.screen, self.TEXT_COLOR, self.menuButtons[2], 1)

            for event in pg.event.get():
                if event.type == pg.QUIT:     
                    sys.exit()

                #Отслеживание нажатия на 1 из кнопок
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()   
                    if (x > self.menuButtons[2][0]) and (x < self.menuButtons[2][0]+self.menuButtons[2][2]) and \
                       (y > self.menuButtons[2][1]) and (y < self.menuButtons[2][1]+self.menuButtons[2][3]):
                        #Отрисовка эффекта нажатия на кнопку
                        pg.draw.rect(self.screen, (self.TEXT_COLOR), self.menuButtons[2])
                        self.drawText(self.screen, "Выход", self.WIDTH/2, self.HEIGHT/2+self.MENU_TEXT_SIZE+self.MENU_TEXT_INDENT, self.MENU_TEXT_SIZE, self.BACKGROUND_COLOR)
                        pg.display.update()
                        time.sleep(0.1)
                        sys.exit()

                    elif (x > self.menuButtons[1][0]) and (x < self.menuButtons[1][0]+self.menuButtons[1][2]) and \
                         (y > self.menuButtons[1][1]) and (y < self.menuButtons[1][1]+self.menuButtons[1][3]):
                        pg.draw.rect(self.screen, (self.TEXT_COLOR), self.menuButtons[1])
                        self.drawText(self.screen, "Рекорды", self.WIDTH/2, self.HEIGHT/2, self.MENU_TEXT_SIZE, self.BACKGROUND_COLOR)
                        pg.display.update()
                        time.sleep(0.1)
                        self.runLeaderboard()

                    elif (x > self.menuButtons[0][0]) and (x < self.menuButtons[0][0]+self.menuButtons[0][2]) and \
                         (y > self.menuButtons[0][1]) and (y < self.menuButtons[0][1]+self.menuButtons[0][3]):
                        pg.draw.rect(self.screen, (self.TEXT_COLOR), self.menuButtons[0])
                        self.drawText(self.screen, "Старт", self.WIDTH/2, self.HEIGHT/2-self.MENU_TEXT_SIZE-self.MENU_TEXT_INDENT, self.MENU_TEXT_SIZE, self.BACKGROUND_COLOR)
                        pg.display.update()
                        time.sleep(0.1)
                        self.drawNameMenu()                            

                pg.display.update()
          
    def runLeaderboard(self):
        #Получение данных из БД
        self.cursor.execute('SELECT username, time, id FROM Leaderboard ORDER BY time ASC')
        self.leaderboardNames = self.cursor.fetchall()
        self.leaderboardText = ''

        #Отрисовка интерфейса
        while not self.closeGame:
            self.screen.fill(self.BACKGROUND_COLOR)
            self.drawText(self.screen, 'Таблица рекордов', self.WIDTH/2, self.MENU_TEXT_SIZE,self.MENU_TEXT_SIZE, self.TEXT_COLOR)
            self.drawText(self.screen, "Для возврата нажмите Esc", self.WIDTH/2, self.HEIGHT-self.TEXT_SIZE, 20, self.TEXT_COLOR)
            pg.draw.rect(self.screen, self.TEXT_COLOR, [self.WIDTH/2-self.fontMenu.size('Таблица рекордов')[0]/2, 
                                                       self.MENU_TEXT_SIZE/2, self.fontMenu.size('Таблица рекордов')[0], self.MENU_TEXT_SIZE], 1)

            for x in range(0,11):
                pg.draw.rect(self.screen, self.TEXT_COLOR, [self.WIDTH/2-self.WIDTH/8, 
                                                           (self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2)+x*self.TEXT_SIZE*1.6, self.WIDTH/4, 50], 1)
                pg.draw.rect(self.screen, self.TEXT_COLOR, [self.WIDTH/2-self.WIDTH/8*3.5, 
                                                           (self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2)+x*self.TEXT_SIZE*1.6, self.WIDTH/4, 50], 1)
                pg.draw.rect(self.screen, self.TEXT_COLOR, [self.WIDTH/2+self.WIDTH/8*1.5, 
                                                           (self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2)+x*self.TEXT_SIZE*1.6, self.WIDTH/4, 50], 1)

            #Заполнение полей данными из БД
            i = 1           
            for x in self.leaderboardNames:
                self.leaderboardText = f'{x[0]} | {x[1]//60}:{x[1]%60} мин.'
                self.leaderboardFont = pg.font.Font(None, self.TEXT_SIZE).render(self.leaderboardText, 1, self.TEXT_COLOR)
                
                if i<12:
                    self.drawText(self.screen, self.leaderboardText, self.WIDTH/2-self.WIDTH/8*3.5+self.WIDTH/8, 
                                  self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2+(i-1)*self.TEXT_SIZE*1.6+25, self.TEXT_SIZE-10, self.TEXT_COLOR)
                if i>=12 and i<23:
                    self.drawText(self.screen, self.leaderboardText, self.WIDTH/2-self.WIDTH/8+self.WIDTH/8, 
                                  self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2+(i-12)*self.TEXT_SIZE*1.6+25, self.TEXT_SIZE-10, self.TEXT_COLOR)
                if i>=23 and i<34:
                    self.drawText(self.screen, self.leaderboardText, self.WIDTH/2+self.WIDTH/8*1.5+self.WIDTH/8, 
                                  self.MENU_TEXT_SIZE/2+self.TEXT_SIZE*2+(i-23)*self.TEXT_SIZE*1.6+25, self.TEXT_SIZE-10, self.TEXT_COLOR)
                i += 1
                
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.runMenu()

            pg.display.update()
        
Game().runMenu()
