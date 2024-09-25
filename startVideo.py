import os

import shutil
from datetime import datetime
import subprocess
import time

#start the rclone mount to OneDrive from the connectrclone.sh file


#Global Commands
# Get the day of the week and time of day
dow = datetime.now().strftime('%A')
tod = datetime.now().strftime("%-I%p") #format 7PM
#get the min from the time
mod = datetime.now().strftime('%M')
# Set the flag to check if VLC process is already open
print("Day of the Week: "+dow+", time of day: "+tod+", min of day: "+mod)
vlc_process = None
#Set the current file name
current_file_mtime = ""
current_file_name = ""


def get_recent_file():
    day_of_week = datetime.now().strftime('%A')
    time_of_day = datetime.now().strftime("%-I%p")
    min_of_day = int(datetime.now().strftime('%M'))
    session_times = ["7AM", "8AM", "9AM"] #session announcement for morning session locations 7-10am
    opening_closing_session_times = ["5PM","6PM"] #saturday/thursday opening/closing session location 5-7pm
    evening_sessions = ["Saturday","Thursday"] #evening session days
    celebration_times = ["7PM","8PM","9PM"] #video playing times for thursday 7-10pm
    connected = False
    while connected is False:
        try:
            #if the time of day is around the time of session
            if time_of_day in session_times:
                directory = "/home/fortadmin/OneDrive/" + day_of_week + "/Session"
                            
            elif time_of_day in celebration_times and day_of_week == "Thursday":
                directory = "/home/fortadmin/OneDrive/" + day_of_week + "/Celebration_Video"
                
            elif time_of_day in opening_closing_session_times and day_of_week in evening_sessions:
                directory = "/home/fortadmin/OneDrive/" + day_of_week + "/Evening_Session"
                    
            else:
                # Construct directory path based on the day of the week
                directory = "/home/fortadmin/OneDrive/" + day_of_week + "/General_Announcements"
                if not os.listdir(directory):
                    return "/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4"
                
        except OSError as e:
            #if the file is not found - wait for connection to happen
            print("File not found: check internet connection")
            time.sleep(60)
            continue #run the last downloaded file
        finally:
            if not os.path.isdir(directory) or not os.listdir(directory):
                directory = "/home/fortadmin/OneDrive/" + day_of_week + "/General_Announcements"
                if not os.listdir(directory):
                    return "/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4"
            # Get the list of .mp4 files in the directory
            files = sorted((os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp4')), key=os.path.getmtime, reverse=True)
            connected = True
    # Return the path of the most recent .mp4 file, or None if no such file exists
    return files[0] if files else None

def stop_vlc():
    global vlc_process
    if vlc_process and vlc_process.poll() is None:
        # Terminate the VLC process gracefully
        vlc_process.terminate()
        vlc_process.wait()

def start_vlc(recent_file):
    global vlc_process
    # Start VLC with the recent file
    try:
        vlc_process = subprocess.Popen(['vlc', recent_file, '--loop', '--fullscreen', '--no-video-title-show'])
    except:
        print("There was a error opening the file")#play the welcome to camp file while the file is downloading
        if vlc_process is None or vlc_process.poll() is not None:
            #display the for logo if there are no files in the days directory
            start_vlc("/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4")
        #if the welcome to camp file is already running then dont change anything
        elif recent_file == "/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4":
            print("The file is the same")
        else:
            #else start the welcome to camp
            time.sleep(60)
            stop_vlc()
            time.sleep(4)
            start_vlc("/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4")
        

def savefile_desktop(recent_file):
    print("Recent file: " + recent_file)
    #copy the most recent file to the desktop
    filename = "/home/fortadmin/Desktop/Pi-Kiosk-App/running_file.mp4"

    try:
        #copy the new file to the desktop file
        dest = shutil.copyfile(recent_file, filename)
        #pause the system to let it catch up
        time.sleep(5)
        print("File saved: ", dest)
    except shutil.SameFileError:
        print("Source and destination file are the same.")
    except:
        print("There was another error")
    return filename

while True:
    
    try:
        #get the most recent created file and get the modification date
        recent_file = get_recent_file() # day of the week info is found in the function
        print(type(recent_file))
        recent_mtime = os.path.getmtime(recent_file)
        #check to see if the new file was made at a different time than the current running file
        if current_file_mtime != recent_mtime or current_file_name != recent_file:
            #if there is a running vlc process
            stop_vlc()    
            #save the new file to the desktop to play from
            filename = savefile_desktop(recent_file)
            #save the new files info to be compared later
            current_file_mtime = recent_mtime
            current_file_name = recent_file
           
        #if there is no vlc process running then start or restart the video
        if vlc_process is None or vlc_process.poll() is not None:
               # Start VLC with the recent file
               start_vlc(filename)
               
        #if none of these if statements are triggered just continue on and do nothing
        
        
        # Sleep for a while before checking again (to avoid constant checking)
        time.sleep(60)
        print("After time")
        
    except OSError:
        print("There was an error in the file system")
        pass #continues to search for files
    except TypeError:
        print("There was no files in the directory")
        recent_file = "/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4"
         #if there is no vlc process running then start or restart the video
        if vlc_process is None or vlc_process.poll() is not None:
            #display the for logo if there are no files in the days directory
            start_vlc(recent_file)
        elif recent_file == "/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4":
            print("The file is the same")
        else:
            stop_vlc()
            time.sleep(4)
            start_vlc("/home/fortadmin/Desktop/Pi-Kiosk-App/WelcometoCamp.mp4")
        continue


