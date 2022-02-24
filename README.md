# RetailPOS
This is a fully Retail POS System for Windows, Mac and Linux System built on Python and Kivy.
<br><br>
Working on document for better understanding
<br><br>
### Installing and Downloading 
    >> You can manually download zip file from here, click on Code and select Download Zip 
    >> Optional: Git, Install Git. If zip downloaded no need to install Git.
        git clone https://github.com/virajkothari7/RetailPOS.git

    >> Requirements: 
          Python 3
          Kivy and KivyMD
          LibUSB [libusb] 
#### Before Running Program Please install libusb and Kivy for appropriate Platform 
    cd [Path to RetailPOS]
    pip install -r requirements.txt
    python main.py
<br><br>
## Raspberry Pi 

I first wanted to run POS on Raspberry Pi hence I went with kivy as it is cross-platform. However Kivy or This app runs noticable slow in Pi-400 as of Feb'22. Might also be my setup which I tried on, if you find success on Raspberry-Pi keep me updated.

#### Raspberry Pi Commands if you would like to give it a try

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt install python3-setuptools git-core python3-dev
    sudo apt-get install libusb-1.0-0-dev

    sudo apt install pkg-config libgl1-mesa-dev libgles2-mesa-dev	libgstreamer1.0-dev	gstreamer1.0-plugins-{bad, base, good, ugly}	gstreamer1.0-{omx,alsa} libmtdev-dev	xclip xsel libjpeg-dev
    *** [If above code gives error don't worry just run code below and move forward]
    sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  
    cd [directory_path to RetailPOS]
    *** You can try without sudo or sudo whichever works for running python scripts.
    sudo pip install -r requirements.txt
    sudo python main.py
    
<br>

    
    
  
     
