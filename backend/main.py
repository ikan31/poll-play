import sys
import socket
import threading
from _thread import *
import time
import vlc
import pafy
import stream
import webscrape
import keyboard
 
username_list = []
user_list = []
votes = []

song_list = []
vote_list = []
usermap_list = []

duration = -1

vstream = None
playing = False
current_song = ""
password = ""
running = True
 
 
def change_vote(ind, val):
    global votes

    votes[ind] = val

def user_thread(c, ci):
    global song_list
    global vote_list
    global usermap_list

    global votes
    global user_list
    global username_list

    global running
    global playing

    print("Started client thread")
   
    while True:
        try:
            # Data parsing
            data = c.recv(256).decode("utf8").replace('\n', '').replace('\r', '')

            # Check if user is connected
            if not data or len(data) == 0:
                break
                print("Data on " + str(ci) + " - " + data)
            # Parse 
            split =  data.split(" ", 1)
            if split[0] == "pause" :
                vstream.pause()
            elif split[0] == "end" :
                running = False
                break
            elif split[0] == "play" :
                vstream.play()
            elif split[0] == "song":
                song_list.append(split[1])
                vote_list.append(1)
                pos0 = user_list.index(c)
                usermap_list.append(username_list[pos0])

                votes[pos0] = votes[pos0].zfill(len(song_list))
            elif split[0] == "admin" :
                if split[1] == "password":
                    c.sendall("admin success".encode())
            elif split[0] == "rsong" :
                pos = song_list.index(split[1])
                song_list.remove(split[1]) 
                vote_list.pop(pos)
            elif split[0] == "vote":
                # Get all pieces
                split2 = data.split(" ")
                # Grab vote
                vote = split2[len(split2) - 1]
                # Find song name
                song = split[1][0:len(split[1]) - len(vote) - 1]
                # Get song index
                pos2 = song_list.index(song)
                
                #print(votes)

                who = user_list.index(c)
                uvote = votes[who]
                val = uvote[pos2]
                
                #print("VAL " + votes[who])
                #print("Vote: " + val + " " + vote)

                # change vote
                if val == "0" and vote == "1":
                    vote_list[pos2] += 1
                elif val == "0" and vote == "-1":
                    vote_list[pos2] -= 1
                elif val == "2" and vote == "1":
                    vote_list[pos2] += 2
                elif val == "1" and vote == "-1":
                    vote_list[pos2] -= 2
                elif val == "1" and vote == "0":
                    vote_list[pos2] -= 1
                elif val == "2" and vote == "0":
                    vote_list[pos2] += 1
                else:
                    print("Voting fucked up somehow val: " + val + " vote: " + vote)

                nstr = ""
                if vote == "-1":
                    vote = "2"
                for i in range(0, len(song_list)):
                    if i == pos2:
                        #print("adding vote val " + vote)
                        nstr += vote
                    else:
                         nstr += votes[who][i]
                #print("new vote " + nstr)

                #votes = newvotes
                change_vote(who, nstr)
            elif split[0] == "name":
                username_list.append(split[1])
            elif split[0] == "seek":
                vstream.set_time(int(split[1]) * 1000)
            elif split[0] == "next":
                vstream.stop()
                playing = False
            
                
            print(song_list)
            print(vote_list)
            qdata = frontend_thread("updateque") + "\n"
            for v in user_list:
                try:
                    v.sendall(qdata.encode("utf8"))
                except OSError:
                   # print("Invalid socket")
                   continue
            

            
        except ConnectionResetError:
           break
        except ValueError:
            print("Invalid song")
    
    ind = user_list.index(c)
    user_list.pop(ind)
    username_list.pop(ind)
    #votes.pop[ind]
    # User disconected
    c.close()

 
def frontend_thread(theirstr):
    global duration

    if vstream == None:
        duration = -1
    else:
        zz = True

    if theirstr == "updateque":
        que = ""
        for i in range(len(song_list)) :
            que += (song_list[i].replace(" ", "_") + " " + str(vote_list[i])) + " " + usermap_list[i].replace(" ", "_") + " " + str(duration) + ","
        print("List: " + que)
        if len(que) == 0: return " "
        return que
 
def server_thread():
   # Start server
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind(('', 53312))
   s.listen(100)
 
   print("Server Started!")
   
   while running:
       print("Waiting for next client")
       # Wait for new connection
       c, addr = s.accept()
 
       print("Got new connection!")
 
       user_list.append(c)

       votes.append("".zfill(len(song_list)))
 
       nthread = threading.Thread(target = user_thread, args = (c, len(user_list) - 1) )
       nthread.daemon = True
       nthread.start()
 
 
def play_video(next):
    global vstream
    global current_song
    global duration

    global playing
   
    try:
        # Get song URL
        song_url = webscrape.get_video(current_song)
        
        if next:
           song_url = webscrape.next_video(song_url)
          
        # Stream song
        vstream, current_song, duration = stream.stream_video(song_url)
        vstream.play()
        
        temp = str(duration).split(":")
        durationf = float(temp[0])*360 + float(temp[1])*60 + float(temp[0])
        duration = str(durationf)
        
        print("Playing " + current_song)
        #print("****DURATION****: " + duration)
        playing = True
        
        qdata = frontend_thread("updateque") + "\n"
        
        for v in user_list:
            try:
                v.sendall(qdata.encode("utf8"))
            except OSError:
                continue #print("Invalid socket") 
    except ValueError:
        return False

        

    
 
 
 
 
# Start listening for connections
sthread = threading.Thread(target = server_thread, args = ( ))
sthread.daemon = True
sthread.start()
 
f = open("admin.txt","r") 
password = f.read()

while running:
   if keyboard.is_pressed('p'):
       running = False
       playing = True
   if not playing:
       if len(song_list) == 0 and current_song == "":
           #print("No songs")
           time.sleep(1)
           continue
       elif len(song_list) == 0:
           print("Finding recommended song from " + current_song)
          
           play_video(True)
       else:
           print("Finding next song...")
           # Get song to be played
           highest = -101
           for i, vote in (list(enumerate(vote_list))):
               if vote > highest:
                   highest = i
          
           current_song = song_list[highest]
 
           # Remove it from list
           song_list.remove(current_song)
           vote_list.remove(vote_list[highest])
 
           # Play song
           play_video(False)

  
   # Wait until song is done
   while not vstream == None and not vstream.get_state() == vlc.State.Ended and playing and running and not keyboard.is_pressed('p'):
       time.sleep(1)
   print("Song ended")
   if not vstream == None:
       vstream.stop()
   playing = False

print("Done")
sys.exit()
