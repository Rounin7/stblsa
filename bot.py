# bot.py
# The code for our bot

import cfg
import utils
import socket, requests, json
import re
import time, threading
from time import sleep
import urllib2
import numpy as np

#TODO move all mulithread functions to seperate file

#Gives a thread for a command
def thread_def(command,par=()):
    if par != ():
        arg = (par,)
    else:
        arg = par
    t1 = threading.Thread(target=command,args=arg)
    t1.daemon = True
    return t1

#test threading
def test1(s):
    utils.chat(s,"Test begun WutFace")
    sleep(20)
    utils.chat(s,"Test ended succesfully PogChamp")
    return(0)

#the puns Kreygasm
def pun(s):
    try:
        response = urllib2.urlopen("http://www.punoftheday.com/cgi-bin/randompun.pl")
        page_source = response.read().splitlines()
        for i in page_source:
            if i[0:3]=="<p>":
                THE_PUN = i[3:-4] + " haHAA"
                break
        utils.chat(s,THE_PUN)
    except urllib2.HTTPError, err:
        utils.chat(s,"There is no god. Pun server dead: {}".format(err.code))
    sleep(10)

#mine
def mine(s):
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    utils.chat(s,":truck: coming your way ANELE")
    while True:
        response = s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            
            if not utils.isOp(username) and np.random.uniform(0,1)<0.2:
                utils.timeout(s,username,5)
                utils.chat(s, username+" got hit by a truck ANELE")
                break
        sleep(1)


def main():
    
    cfg.NICK = raw_input("Enter nick:")
    cfg.PASS = "oauth:"+raw_input("Enter oauth:")
    cfg.CHAN = raw_input("Enter channel:")
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Mod list things
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    try:
        cfg.oplist = json.load(open("mods.txt"))
    except ValueError:
        cfg.oplist[cfg.NICK] = "mod"
        json.dump(cfg.oplist,open("mods.txt","w"))

    if cfg.NICK not in cfg.oplist:
        cfg.oplist[cfg.NICK] = "mod"
        json.dump(cfg.oplist,open("mods.txt","w"))
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Networking functions
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(cfg.CHAN).encode("utf-8"))

    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    #Dict for running multithread commands
    current_threads = {}

    while True:
        response = s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            #~ print(response)
            
            
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #Linear mod commands
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if message.strip()[0:5] == "!mod " and utils.isOp(username):
                usr = re.sub("[^\w]"," ",message.strip()).split()[1].lower()
                cfg.oplist[usr] = "mod"
                json.dump(cfg.oplist,open("mods.txt","w"))
                utils.chat(s, usr+" probably modded LUL")

            if message.strip()[0:5] == "!mods":
                modsstr=""
                for user in cfg.oplist:
                    modsstr=modsstr+" [{}] ".format(user)
                utils.chat(s, "Mods:"+modsstr)

            
            if message.strip()[0:7] == "!unmod " and utils.isOp(username):
                usr = re.sub("[^\w]"," ",message.strip()).split()[1].lower()
                if usr != cfg.NICK:
                    if usr in cfg.oplist:
                        del cfg.oplist[usr]
                        json.dump(cfg.oplist,open("mods.txt","w"))
                        utils.chat(s, usr+" probably unmodded LUL")
                    else:
                        utils.chat(s, usr+" is not a mod FeelsBadMan")
                else:
                    utils.chat(s, "Don't you dare SwiftRage")

                
            if message.strip()[0:3] == "!t " and utils.isOp(username):
                usr = re.sub("[^\w]"," ",message.strip()).split()[1]
                if len(re.sub("[^\w]"," ",message.strip()).split()) > 2:
                    timeS = re.sub("[^\w]"," ",message.strip()).split()[2]
                    utils.timeout(s,usr,timeS)
                else:
                    timeS = 600
                    utils.timeout(s,usr,timeS)
                utils.chat(s, usr+" timed out for "+str(timeS)+" s")
            
            if message.strip() == "!time" and utils.isOp(username):
                utils.chat(s, "Current time: " + time.strftime("%I:%M %p %Z on %A, %B %d, %Y."))

            if message.strip() == "!poop":
                utils.timeout(s,username,60)
                utils.chat(s, username+" just pooped himself, he'll take a minute to clean up.")

                
            if message.strip()[0:8] == "!invite " and utils.isOp(username):
                usr = re.sub("[^\w]"," ",message.strip()).split()[1]
                details = {}
                details["irc_channel"] = cfg.CHAN
                details["username"] = usr
                url_inv = "http://chatdepot.twitch.tv/room_memberships?oauth_token="+cfg.PASS[6:]
                r = requests.post(url_inv,details)
                utils.chat(s, usr+" invited PogChamp " + "(Status: " + str(r.status_code) + ")")
            
            if message.strip() == "!faq":
                utils.chat(s, "It was a happy little accident that you ended up here CoolStoryBob")
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            for thr in current_threads.keys():
                if not current_threads[thr].isAlive():
                    del current_threads[thr]
            
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #Multithread mod commands
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            if message.strip() == "!test" and "test1" not in current_threads.keys() and utils.isOp(username):
                current_threads["test1"]=thread_def(test1,s)
                current_threads["test1"].start()
            
            if message.strip() == "!pun" and "pun" not in current_threads.keys():
                current_threads["pun"]=thread_def(pun,s)
                current_threads["pun"].start()
            
            if message.strip() == "!mine" and "mine" not in current_threads.keys():
                current_threads["mine"]=thread_def(mine,s)
                current_threads["mine"].start()
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        sleep(1)
    utils.chat(s, "Bye everyone :)");
if __name__ == "__main__":
    main()


















