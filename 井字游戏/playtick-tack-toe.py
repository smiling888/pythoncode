#coding=utf-8
#打印出井字游戏的背景模板
#X | X | X 
#X | X | X 
#X | X | X
#在这里print map[2-i][j],使用了逗号，以保证他们在同一行被打印出来
def print_board():
    for i in range(0,3):
        for j in range(0,3):
            print map[2-i][j],
            if j != 2:
                print "|",
        print ""
 
def check_done():
#会检查水平和垂直方向，是不是有三格是相同、并且不为空
    for i in range(0,3):
        if map[i][0] == map[i][1] == map[i][2] != " " \
        or map[0][i] == map[1][i] == map[2][i] != " ":
            print turn, "won!!!"
            return True
 
    if map[0][0] == map[1][1] == map[2][2] != " " \
    or map[0][2] == map[1][1] == map[2][0] != " ":
        print turn, "won!!!"
        return True
 
    if " " not in map[0] and " " not in map[1] and " " not in map[2]:
        print "Draw"
        return True
 
    return False
#turn：该谁走了
#map：游戏的背景地图
#done：这个游戏到底有木有结束
 
turn = "X"
map = [[" "," "," "],
       [" "," "," "],
       [" "," "," "]]
done = False
 
while done != True:
    print_board()
 
    print turn, "'s turn"
    print
 
    moved = False
    while moved != True:
        print "Please select position by typing in a number between 1 and 9, see below for which number that is which position..."
        print "7|8|9"
        print "4|5|6"
        print "1|2|3"
        print
 				#错误处理，比如玩家输入”Hello”，程序不能就这么退出了。
        try:
            pos = input("Select: ")
            #检查他走的这一步能不能走：
            if pos <=9 and pos >=1:
            #位置1：Y = 1/3 = 0, X = 1%3 = 1; x -= 1 = 0
						#位置2：Y = 2/3 = 0, X = 2%3 = 2; X -= 1 = 1
						#位置3：Y = 3/3 = 1, X = 3%3 = 0; X = 2, Y -= 1 = 0
                Y = pos/3
                X = pos%3
                if X != 0:
                    X -=1
                else:
                     X = 2
                     Y -=1
 
                if map[Y][X] == " ":
                    map[Y][X] = turn
                    moved = True
                    done = check_done()
 
                    if done == False:
                        if turn == "X":
                            turn = "O"
                        else:
                            turn = "X"
 
        except:
            print "You need to add a numeric value"