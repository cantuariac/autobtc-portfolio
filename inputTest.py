import time
import threading

run = True
user = True
op = ''
def printing():
    global user
    print()
    while(run):
        if(user):
            print('\033[2JYou typed:', op)
            user = not user
            time.sleep(2)

t=threading.Thread(target=printing)
t.start()
while(run):
    op = input('>')
    user = True
    if op == 'q':
        run = False