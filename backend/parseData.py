import sys
import socket
import threading
from _thread import *
import time


print_lock = threading.Lock()

user_list = []
song_list = []
vote_list = []
username_list = []
usermap_list = []
duration = 0


def user_thread(c):
    print("Started client thread")

    while True:
        try:

            # Data parsing
            data = c.recv(256).decode("utf8")

            # Check if user is connected
            if not data or len(data) == 0:
                break
            print(data)
            # Parse data
            split =  data.split()
            duration = split[len(split)-1]
            split =  data.split(" ", 1)
            
            if split[0] == "song":
                song_list.append(split[1])
                vote_list.append(1)
                pos0 = user_list.index(c)
                usermap_list.append(username_list[pos0])
                
            if split[0] == "rsong" :
                pos = song_list.index(split[1])
                song_list.remove(split[1]) 
                vote_list.pop(pos)
            if split[0] == "vote" :
                split = data.split()
                end = split[len(split) -1]
                pos2 = song_list.index(split[1])
                vote_list[pos2] += int(end)
            
            if split[0] == "name" :
                username_list.append(split[1])
                
            
            print(song_list)
            print(vote_list)
            print(frontend_thread("updateque"))
            #for v in user_list :
             #  c.send(frontend_thread("updateQue"))

        except ConnectionResetError:
           break

    
    # User disconected
    c.close()

 
def frontend_thread(theirstr) :
    duration = vstream.duration
    if theirstr == "updateque"  :
        que = ""
        for i in range(len(song_list)) :
            que += (song_list[i].replace(" ", "_") + " " + str(vote_list[i]))+ " " + usermap_list[i].replace(" ", "_") + " " + duration + ","
        que[0:len(que)-2]
        print("List: " + que)
        return que

'''
def user_thread(data):
    # Data parsing

    split =  data.split(" ", 1)
    
    if split[0] == "song":
        song_list.append(split[1])
        vote_list.append(1)
        #pos0 = user_list.index(c)
        #user_map_list = username_list[pos0]
    if split[0] == "rsong" :
        pos = song_list.index(split[1])
        song_list.remove(split[1]) 
        vote_list.pop(pos)
    if split[0] == "vote" :
        split = data.split()
        end = split[len(split) -1]
        pos2 = song_list.index(split[1])
        vote_list[pos2] += int(end)
    print(song_list)
    print(vote_list)
    print(username_list)
    if split[0] == "name" :
        pos3 = user_list.index(c)
        username_list[pos3] = split[1]


print(user_thread("song middle child"))
print(user_thread("song hoo's man is this"))
print(user_thread("song morinin"))
print(user_thread("rsong middle child"))
print(user_thread("vote morinin -1"))
print(frontend_thread("updateque"))

'''

         
def server_thread():
   # Start server
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind(('', 53312))
   s.listen(100)
 
   print("Server Started!")
 
   while True:
       # Wait for new connection
       c, addr = s.accept()
 
 
       print("Got new connection!")
 
       user_list.append(c)
 
       nthread = threading.Thread(target = user_thread, args = (c, ))
       nthread.start()
# Start listening for connections
sthread = threading.Thread(target = server_thread, args = ( ))
sthread.start()
