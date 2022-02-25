#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#wuziqi.py
#Author:xutao

from graphics import *#导入graphics中的所有函数
import datetime
###
num = [[0 for a in range(16)] for a in range(16)] #棋盘大小16*16
dx = [1,1,0,-1,-1,-1,0,1] 
dy = [0,1,1,1,0,-1,-1,-1]#dx,dy共同构成共8个方向向量v
is_end = False #结束标志
firstPlay = 1 #先手标志
start = 1 #轮换下棋标志
ai = 1 #电脑下棋标志
F1_max=-99999 #剪枝变量初始化
F2_min=99999
list=[] #保存已画棋子
RESTART_FLAG = False
QUIT_FLAG = False
##图形界面
win = GraphWin("Game_AI",550,500)#设置画布尺寸
computerFirst = Text(Point(500,140),"")
playerFirst = Text(Point(500,180),"")
notice = Text(Point(500,220),"") #提示轮到谁落子
notice.setFill('red')#colour of notice
QUIT = Text(Point(50,475),"退出")
QUIT.setFill('grey')
RESTART = Text(Point(150,475),"重玩")
RESTART.setFill('green')
timeShow = Text(Point(330,475),"") #显示落子耗时
timeShow.setFill('orange')

#初始化棋盘和各变量
def init():
    global is_end,start,firstPlay,RESTART_FLAG
    is_end=False
    start=1
    firstPlay=1
    RESTART_FLAG=False
    QUIT_FLAG=False
    for i in range(16):
        for j in range(16):
            if(num[i][j]!=0):
                num[i][j]=0
    for i in range(len(list)):
        list[-1].undraw()
        list.pop(-1)
    computerFirst.setText("电脑先手")
    playerFirst.setText("玩家先手")
    notice.setText("")
    timeShow.setText("耗时")

#描述棋盘
def drawWin():
    win.setBackground('skyblue')
    for i in range(0,451,30):
        line=Line(Point(i,0),Point(i,450))
        line.draw(win)
    for j in range(0,451,30):
        line=Line(Point(0,j),Point(450,j))
        line.draw(win)
    Oval(Point(10,460),Point(90,490)).draw(win)
    Oval(Point(110,460),Point(190,490)).draw(win)
    Oval(Point(460,125),Point(540,155)).draw(win)
    Oval(Point(460,165),Point(540,195)).draw(win)
    computerFirst.draw(win)
    playerFirst.draw(win)
    notice.draw(win)
    timeShow.draw(win)
    QUIT.draw(win)
    RESTART.draw(win)
#判断该点是否在棋盘范围内
def inBound(x,y):
    if(x>=0 and x<=15 and y>=0 and y<=15): return True
    else: return False
#判断该点是否可落子，即是否在棋盘内且没有落子
def place_able(x,y): 
    if(inBound(x,y) and num[x][y]==0): return True
    else: return False
#(x,y)位置的棋子颜色和i是否相同
def sameColor(x,y,i):
    if(inBound(x,y) and num[x][y]==i): return True
    else: return False
#在给定的向量v方向上，和该点同色棋子的个数，不包括该点本身
def numInline(x,y,v):
    i=x+dx[v]; j=y+dy[v]
    s=0; ref=num[x][y]
    if(ref==0): return 0
    while(sameColor(i,j,ref)):
        s=s+1; i=i+dx[v]; j=j+dy[v]
    return s
#该点四个方向里(即v不区分正负)，活四局势的个数
def liveFour(x,y):
    key=num[x][y]; s=0
    for u in range(4):
        samekey=1
        samekey,i=numofSamekey(x,y,u,1,key,samekey)
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(samekey==4):
            s=s+1
    return s
#该点八个方向里(即v区分正负)，冲四局势的个数
def addTofour(x,y):
    key=num[x][y]; s=0
    for u in range(8):
        samekey=0; flag=True; i=1
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key) or flag):
            if(not sameColor(x+dx[u]*i,y+dy[u]*i,key)):
                if(flag and inBound(x+dx[u]*i,y+dy[u]*i) and num[x+dx[u]*i][y+dy[u]*i]!=0):
                    samekey-=10
                flag=False
            samekey+=1
            i+=1
        i-=1
        if(not inBound(x+dx[u]*i,y+dy[u]*i)):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(samekey==4):
            s+=1
    return s-liveFour(x,y)*2
#该点四个方向里活三（v不区分正负），以及八个方向里断三（v区分正负）的个数
def liveThree(x,y):
    key=num[x][y]; s=0
    for u in range(4):
        samekey=1
        samekey,i=numofSamekey(x,y,u,1,key,samekey)
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(not place_able(x+dx[u]*(i+1),y+dy[u]*(i+1))):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(not place_able(x+dx[u]*(i-1),y+dy[u]*(i-1))):
            continue
        if(samekey==3):
            s+=1
    for u in range(8):
        samekey=0; flag=True; i=1
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key) or flag):
            if(not sameColor(x+dx[u]*i,y+dy[u]*i,key)):
                if(flag and inBound(x+dx[u]*i,y+dy[u]*i) and num[x+dx[u]*i][y+dy[u]*i]!=0):
                    samekey-=10
                flag=False
            samekey+=1
            i+=1
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(inBound(x+dx[u]*(i-1),y+dy[u]*(i-1)) and num[x+dx[u]*(i-1)][y+dy[u]*(i-1)]==0):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not place_able(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(samekey==3):
            s+=1
    return s
#该点在四个方向里，是否有六子或以上连线
def isOvernum(x,y):
    flag=False
    for u in range(4):
        if((numInline(x,y,u)+numInline(x,y,u+4))>4):
            flag=True
    return flag
#该黑子点是否是禁手点，黑子禁手直接判输
def ban(x,y):
    if(sameColor(x,y,3-firstPlay)):
        return False
    flag=((liveThree(x,y)>1) or (isOvernum(x,y)) or ((liveFour(x,y)+addTofour(x,y))>1))
    return flag
#统计在u方向上，和key值相同的点的个数，即和key同色的连子个数
def numofSamekey(x,y,u,i,key,sk):
    if(i==1):
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key)):
            sk+=1
            i+=1
    elif(i==-1):
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key)):
            sk+=1
            i-=1
    return sk,i
#游戏是否结束，如果有五子连线
def gameOver(x,y):
    global is_end
    for u in range(4):
        if((numInline(x,y,u)+numInline(x,y,u+4))>=4):
            is_end=True
            return True
    return False
#评估函数，对该点落子后的局势进行估分
def evaluate(x,y):
    global is_end
    if(ban(x,y)): #出现禁手，估价0
        return 0
    if(gameOver(x,y)): #五子连线,估价10000
        is_end=False
        return 10000
    score=liveFour(x,y)*1000+(addTofour(x,y)+liveThree(x,y))*100 #评估函数中，设置活四1000分，冲四和活三100分
    for u in range(8):
        if(inBound(x+dx[u],y+dy[u]) and num[x+dx[u]][y+dy[u]]!=0):#该落点的八个方向上相邻点在界内且已有棋子落点则分数加一/如玩家（0，0），则电脑会落点（1，1）
            score=score+1
    return score
#博弈树第一层
def layer1():
    global F1_max
    F1_max=-99999
    if(num[8][8]==0 and firstPlay==ai):
        return go(8,8) #电脑落子首选棋盘中心点
    point_x=-1; point_y=-1
    for x in range(16):    
        for y in range(16):
            if(not place_able(x,y)):
                continue
            num[x][y]=ai
            temp_score=evaluate(x,y)
            if(temp_score==0): #出现禁手，跳过此落点
                num[x][y]=0; continue
            if(temp_score==10000):#五子连线，直接落子
                return go(x,y)
            temp_score=layer2() #递归查询博弈树第二层
            num[x][y]=0
            if(temp_score>F1_max): #取极大
                F1_max=temp_score; point_x=x; point_y=y
    go(point_x,point_y)
#博弈树第二层
def layer2():
    global F2_min
    F2_min=99999
    for x in range(16):    
        for y in range(16):
            if(not place_able(x,y)):
                continue
            num[x][y]=3-ai
            temp_score=evaluate(x,y)
            if(temp_score==0):
                num[x][y]=0; continue
            if(temp_score==10000):#对手五子连线
                num[x][y]=0; return -10000
            temp_score=layer3(temp_score)
            if(temp_score<F1_max): #F1层剪枝
                num[x][y]=0; return -10000
            num[x][y]=0
            if(temp_score<F2_min): #取极小
                F2_min=temp_score
    return F2_min
#博弈树第三层
def layer3(p2):
    keyp=-99999
    for x in range(16):    
        for y in range(16):
            if(not place_able(x,y)):
                continue
            num[x][y]=ai
            temp_score=evaluate(x,y)
            if(temp_score==0):
                num[x][y]=0; continue
            if(temp_score==10000):
                num[x][y]=0; return 10000
            if(temp_score-p2*2>F2_min): #F2层剪枝
                num[x][y]=0; return 10000
            num[x][y]=0
            if(temp_score-p2*2>keyp): #取极大
                keyp=temp_score-p2*2
    return keyp

#选手下棋
def playerGo():
    p=win.getMouse()
    if(Restart(p) or Quit(p)): return
    x=round(p.getX()/30)
    y=round(p.getY()/30)
    if(place_able(x,y)): go(x,y)
    else: playerGo()

#落下一子并且判断游戏是否结束
def go(x,y):
    global is_end
    c=Circle(Point(x*30,y*30),13)#棋子大小和落子位置
    if(start==ai):
        num[x][y]=ai
        if(firstPlay==ai): c.setFill('black')
        else: c.setFill('white')
    else:
        num[x][y]=3-ai
        if(firstPlay==ai): c.setFill('white')
        else: c.setFill('black')
    c.draw(win)
    list.append(c)
    if(ban(x,y)):
        if(start==ai):
            notice.setText("电脑禁手,玩家赢!\n点击重玩")
        else:
            notice.setText("玩家禁手,电脑获胜!\n点击重玩")
        is_end=True
    elif(gameOver(x,y)):
        if(start==ai):
            notice.setText("电脑获胜!\n点击重玩")
        else:
            notice.setText("玩家赢!\n点击重玩")

##是否重新开始游戏
def Restart(p):
    global RESTART_FLAG
    x=p.getX(); y=p.getY()
    if((abs(150-x)<40) and (abs(475-y)<15)): #restart
        init()
        RESTART_FLAG=True
        notice.setText("重新开始")
        time.sleep(1)
        return True
    else:
        return False
##是否退出游戏
def Quit(p):
    global QUIT_FLAG, is_end
    x=p.getX(); y=p.getY()
    if((abs(50-x)<40) and (abs(475-y)<15)): #quit
        init()
        QUIT_FLAG=True
        is_end=True
        notice.setText("退出")
        time.sleep(1)
        return True
    else:
        return False

##选择先后手,选择后显示AI、棋手黑白子情况
def whoStart(p):
    global start,firstPlay
    x=p.getX(); y=p.getY()
    if((abs(500-x)<40) and (abs(140-y)<15)): #AI 先手
        start=1
        firstPlay=1
        computerFirst.setText("电脑执黑")
        playerFirst.setText("玩家执白")
        return True
    elif((abs(500-x)<40) and (abs(180-y)<15)): #玩家先手
        start=2
        firstPlay=2
        computerFirst.setText("电脑执白")
        playerFirst.setText("玩家执黑")
        return True
    else:
        return False
##*************************************************##
#main function
if __name__=='__main__':
    init()#初始化棋盘
    drawWin()#棋盘图形界面
    notice.setText("选择先手方")
    p=win.getMouse() #鼠标获取点
    while(not whoStart(p) and not Quit(p)):
        p=win.getMouse() #除了开始和退出，点击界面其他点无效
    while(not is_end):
        RESTART_FLAG=False
        #选择先后手
        if(start==ai):
            begin=datetime.datetime.now()
            notice.setText("电脑正在下棋...")
            layer1()
            end=datetime.datetime.now()
            dur=end-begin
            message="电脑本次耗时"+str(dur)
            timeShow.setText(message)  
        else:
            begin=datetime.datetime.now() 
            notice.setText("玩家下棋...")
            playerGo()
            end=datetime.datetime.now()
            dur=end-begin
            message="你本次耗时"+str(dur)
            timeShow.setText(message)  
        start=3-start
        if(RESTART_FLAG):
            notice.setText("选择先手方")
            p=win.getMouse()
            while(not whoStart(p) and not Quit(p)):
                p=win.getMouse()
        elif(not QUIT_FLAG and is_end):
            p=win.getMouse()
            while(not Restart(p) and not Quit(p)):
                p=win.getMouse()
            if(RESTART_FLAG):
                notice.setText("选择先手方")
                p=win.getMouse()
                while(not whoStart(p) and not Quit(p)):
                    p=win.getMouse()
