import pygame as pg
import sys
import random
import math

class Screen: # main関数内の整理
    def __init__(self, color, wh, title): 
        # fn: 背景画像のパス, wh: 幅高さのタプル title: 画面のタイトル
        pg.display.set_caption(title)
        self.width, self.height = wh # (1600, 900)
        self.disp = pg.display.set_mode((self.width, self.height))
        self.rect = self.disp.get_rect() # Rect
        self.image = pg.Surface((self.width,self.height))
        pg.draw.rect(self.image, color, (0, 0, self.width, self.height))

class Rectangle:
    #クラス変数
    speed = 10 # 球の速度
    key_delta = {
                 pg.K_UP   : [0, -speed],
                 pg.K_DOWN : [0, +speed],
                 }

    def __init__(self, color, xy, wh): #, screen): # self, fn, r, xy):
        # color: 自機の色
        # xy: 初期配置のxy座標（タプル）
        # wh: 四角形の(縦,横）の値（タプル）(横と縦という組み合わせにし、xyと合わせた)
        self.width, self.height = wh
        self.image = pg.Surface((self.width,self.height)) # surface
        self.rect= self.image.get_rect() # rect
        pg.draw.rect(self.image, color, (xy[0]-self.width, xy[1]-self.height, self.width, self.height))   # ボール用Surfaceに円を描く # pygame.draw.rect(Surface, color, (左上のｘ座標、左上のｙ座標、横幅、縦の幅), width=0): return Rec
        self.image.fill(color)
        self.rect.center = xy # center系は元から組み込まれているためcenterx,centeryと変換できている（？）
    
    def update(self, screen):
        key_states = pg.key.get_pressed()
        for key, delta in Rectangle.key_delta.items():
            if key_states[key] == True:
                self.rect.centerx += delta[0]
                self.rect.centery += delta[1]
                if check_bound(screen.rect, self.rect) != (1,1): 
                    self.rect.centerx -= delta[0]
                    self.rect.centery -= delta[1]

class Ball:
    # クラス変数
    vx, vy = (0, 0) # 他でも値を変えられるようにクラス変数で速度を補完
    def __init__(self, color, r, vxy, screen, df = 1):
        # color: ボールの色, r: ボール（円）の半径, 
        # vxy: ボールの速度のタプル,
        # screen: 描画用Screenオブジェクト
        self.image = pg.Surface((2*r,2*r)) # ボール用のSurface
        self.image.set_colorkey((0,0,0)) # 黒色部分を透過する
        pg.draw.circle(self.image, color, (r,r), r)   # ボール用Surfaceに円を描く
        self.rect = self.image.get_rect() # ボール用Rect
        # 初期位置。開始と同時に終わらないように、一番左の真ん中からスタートするようにする。
        self.rect.centerx = 2*r # 画面をこえてしまわないように0ではなくボールの半径以上は間をあける。念のため直径分。
        #self.rect.centery = screen.rect.height/2
        self.rect.centery = random.randint(0+r,screen.rect.height-r) #大矢航輔
        Ball.vx, Ball.vy = vxy # クラス変数に初速度を代入
        self.ivx, self.ivy = vxy # 計算で使うために、初速度を固定の値として取得 # Initial velocity
        self.df = df
    
    def update(self, screen, rectangle, time=0):
        # screen: 画面, rectangle: 自機
        # time: 現在の時間, df: 何秒ごとに加速するか
        # ボールの速度を変更させる場合
        speed = (time // self.df)
        xs, ys  =  (speed + self.ivx, speed + self.ivy)# 10秒ごとにボールの速度が変化する
        Ball.vx = +xs if Ball.vx > 0 else -xs
        Ball.vy = +ys if Ball.vy > 0 else -ys
        # 壁（ウィンドウの縁）に当たった際の反射
        x, y = check_bound(screen.rect, self.rect)
        Ball.vx *= x # 横方向に画面外なら，横方向速度の符号反転
        Ball.vy *= y # 縦方向に画面外なら，縦方向速度の符号反転
        # 長方形の自機に当たった際の反射
        x, y = check_bound_rectangle(rectangle.rect, self.rect)
        Ball.vx *= x # 自機の左右の側面に当たると、横方向速度の符号反転
        Ball.vy *= y # 自機の上下の側面に当たると、縦方向速度の符号反転
        self.rect.move_ip(Ball.vx, Ball.vy)


def main():
    clock = pg.time.Clock()
    
    # 下地
    screen = Screen("black", (1600, 900), "壁打ちテニスゲーム")
    screen.disp.blit(screen.image, (0,0))           

    # 自機
    rects = Rectangle("white", (1400, 400), (20, 200))

    # ボール
    ball = Ball((255,0,0), 10, (+2, +2), screen, 5)
    
    # 時間
    time = 0
    fonto =pg.font.SysFont("nsimsun",70) # nsimsun meiryo
    fonto2 = pg.font.SysFont('snapitc', 100) #大矢航輔
    endmessage = fonto2.render("Press Enter to Over", True, "red") # 終了後のメッセージ #大矢航輔
    #time = Time(100, "white", "Press Enter to Over")
    

    overflag = False # ゲームが終了するかの判断のためのフラッグ

    while True:
        # 背景の描写
        screen.disp.blit(screen.image, (0,0))
        for event in pg.event.get():
            if event.type == pg.QUIT: return       # ✕ボタンでmain関数から戻る

        # 自機の移動
        rects.update(screen)
        #rects.draw(screen.disp)
        screen.disp.blit(rects.image, rects.rect)
        
        # 終了判定
        if screen.rect.right < ball.rect.right: overflag = True
        ## 画面の右をボールが超えたら
        if overflag:
            key_states = pg.key.get_pressed()
            if key_states[pg.K_RETURN] == True: return # ENTERを押した時、終了する
            screen.disp.blit(timetxt, (50, 50)) # 記録表示
            screen.disp.blit(endmessage, (200, screen.height/2)) # ENTERを押すよう誘導
            lvltxt = fonto.render("速度{:2f}".format(math.sqrt(ball.vx**2 + ball.vy**2)),True,"yellow") #アライ
            screen.disp.blit(lvltxt,(50,150))
        ## まだラリーが続いているならば
        else:
            # ボールの移動
            ball.update(screen, rects, time)
            #balls.draw(screen.disp)
            screen.disp.blit(ball.image, ball.rect)
            
            # 現在の時間表示
            time += clock.get_rawtime()/1000
            timetxt = fonto.render("{}秒ごとに加速".format(ball.df)+str(round(time,2)),True,"yellow") #大矢航輔
            screen.disp.blit(timetxt,(50,50))
            lvltxt = fonto.render("速度{:2f}".format(math.sqrt(ball.vx**2 + ball.vy**2)),True,"yellow") #アライ
            screen.disp.blit(lvltxt,(50,150))

        pg.display.update()  # 画面の更新
        clock.tick(1000) 
    
# 右以外の壁に当たったかどうかの判定
def check_bound(sc_r, obj_r): # 画面用Rect, ｛自機，ボール｝Rect
    # 画面内：+1 / 画面外：-1
    x, y = +1, +1
    if obj_r.left < sc_r.left: x = -1 # 左の壁に当たった場合、反射
    if obj_r.top  < sc_r.top  or sc_r.bottom < obj_r.bottom: y = -1 # 上下の壁に当たった場合、反射
    return x, y

def check_bound_rectangle(rec_r, ball_r): # 長方形の自機に当たった場合、どの面でも反射するようにする
    x, y = +1, +1
    # 左右の側面に当たった時の判定
    if rec_r.top < ball_r.centery < rec_r.bottom:
        if rec_r.left < ball_r.right and ball_r.centerx < rec_r.centerx: x = -1 # 左側面に当たった場合の反射。主に使う面。
        if ball_r.left < rec_r.right and rec_r.centerx < ball_r.centerx: x = -1 # 右側面に当たった場合の反射。今回のゲームの仕様では使われない。
    # 上下の側面に当たった時の判定
    if rec_r.left < ball_r.centerx < rec_r.right:
        if rec_r.top < ball_r.bottom and ball_r.centery < rec_r.centery: y = -1 # 上側面に当たった場合の反射
        if ball_r.top < rec_r.bottom and rec_r.centery < ball_r.centery: y = -1 # 下側面に当たった場合の反射
    return x, y

if __name__ == "__main__":
    pg.init() 
    main()
    pg.quit()
    sys.exit()