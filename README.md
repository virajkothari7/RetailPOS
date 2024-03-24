# RetailPOS

RetailPOS is a comprehensive Point of Sale (POS) system designed for Windows, Mac, and Linux operating systems, developed using Python and Kivy. It facilitates day-to-day business transactions and inventory management within a single local setup, without any subscription fees. The code is customizable to meet individual requirements, making it an ideal starting point for those seeking to operate a POS system locally. Additionally, RetailPOS can interface with thermal receipt printers and cash drawers when configured appropriately, program leverages the python-escpos library for communication. It's important to note that this program does not support customer displays and payment gateways, making it as cash-register style POS systems.

<br>

**Ensure you have the following dependencies installed. Install libusb and Kivy for appropriate Platform.**

  - Python 3
  - Kivy and KivyMD
  - LibUSB (libusb)
    
<br>

## Installation and Downloading

To get started with RetailPOS, follow these steps:


### Download Instruction

- Manual Download (Option 1)
  
  You can manually download the zip file from [here](https://github.com/virajkothari7/RetailPOS/archive/refs/heads/main.zip).
  Click on "Code" and select "Download ZIP".

- Git Clone (Option 2)
  
  If you prefer using Git, you can clone the repository using the following command:

      git clone https://github.com/virajkothari7/RetailPOS.git

### Installation Instructions
- Navigate to the directory where RetailPOS is located.  

      cd [Path to RetailPOS]

- Install the required packages using pip:

      pip install -r requirements.txt

- Run the program:

      python main.py

<br>

## Screenshots

<br><br>
<table>
  <tr>
    <td><img src=https://github.com/virajkothari7/RetailPOS/blob/main/screensShots/snapshot2.png></td>
    <!-- <td><img src=https://github.com/virajkothari7/RetailPOS/blob/main/screensShots/snapshot.png>></td> -->
  </tr>
  <tr>
    <td><img src=https://github.com/virajkothari7/RetailPOS/blob/main/screensShots/snapshot1.png>></td>
    <td><img src=https://github.com/virajkothari7/RetailPOS/blob/main/screensShots/snapshot10.png>></td>
  </tr>
</table>
<br> 
<br>

## Running on Raspberry Pi

  RetailPOS is compatible with Raspberry Pi, however, it may run slower.  
  If you'd like to try to run on Raspberry Pi, update sudo and install required dependancy.
  
  ```
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt install python3-setuptools git-core python3-dev
  sudo apt-get install libusb-1.0-0-dev
  ```
  
    sudo apt install pkg-config libgl1-mesa-dev libgles2-mesa-dev	libgstreamer1.0-dev	gstreamer1.0-plugins-{bad, base, good, ugly}	gstreamer1.0-{omx,alsa} libmtdev-dev	xclip xsel libjpeg-dev
  
   If the above code gives an error, run the following command:
          
    sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  
  To run program, follow **Installation and Downloading** section.
  Use **sudo python** if you have trouble running regular **python** command.

    
    
  
     
