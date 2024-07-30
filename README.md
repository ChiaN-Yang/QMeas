# QMeas
<a href="#"><img src="https://img.shields.io/badge/python-v3.9+-blue.svg?logo=python&style=for-the-badge" /></a>

## Summary
This is a set of instrument control and automated measurement software. The instruments to be controlled include a dilution refrigerator (a system that operates at a hundredth of a degree above absolute zero), a superconducting magnet, a lock-in amplifier, and a Source Measure Unit device. The main functions of the software are to control instrument outputs, pre-schedule future outputs or readings of physical quantities, and perform real-time plotting of instrument readings.

## Features
- **Add Instruments Arbitrarily**: We have created an extensible module, allowing new instruments to be added without changing the code.
- **Execute Experiments Arbitrarily**: We provide a tree widget to arrange experiments, enabling any scheduling achievable by loops.
- **One-to-Many Dynamic Plotting**: Unlike market-available plotting methods, one-to-many dynamic plotting allows user to verify experimental results during the experiment.
- **Quick Access to Past Experiments**: The software saves the user's experimental schedule during execution, and this file can be directly imported.
- **Automatic Range Switching**: Users can decide whether to let the program automatically calculate the read values and switch to the appropriate range.
- **Accidental Save**: If the user accidentally closes the program, it retains a temporary file of the data, so re-measurement is unnecessary.
- **Sample Safety Assurance**: Prevents instrument pulses caused by incorrect settings from damaging the device.

## objectives
This program needs to have the following functions:
1. **Automatic Detection of Available I/O Buses and Scanning for User-Added Drivers**: The software should automatically detect available I/O buses and scan for drivers added by the user.
2. **Instrument Selection and Connection**: Allow users to select the type of instrument, I/O bus, and instrument name to connect to the instrument. If the connection is successful, it should be displayed on the screen list; if the connection fails, an error message should be reported.
3. **Remove Connected Instruments**: Allow users to remove already connected instruments.
4. **Control Panel for Experiment Steps**: Provide a control panel that allows users to decide the steps of the experiment.
5. **Choose Save Location**: Allow users to decide where to save the files.
6. **Real-Time Plotting**: Draw real-time plots of the data.
7. **Selective Data Display**: Allow users to display only specific data on the screen.
8. **Pause or Stop Experiments at Any Time**: Enable users to pause or stop the experiment at any time.
9. **Export Results**: Export the results as images and CSV files, with the file names customizable by the user.

## Architecture
The program is divided into three parts: Connection, Measurement, and Graph.
- **Connection**: Responsible for scanning available I/O buses and connecting instruments to the main program.
- **Measurement**: Manages the experimental workflow. During the experiment, it directs the Connection to operate the instruments to read values and set values. It also sends signals to the Graph to update real-time plots and save measurement data.
- **Graph**: Receives signals from Measurement and updates the charts accordingly.

![program structure](https://i.imgur.com/ueL3XPM.png)

## Flow Chart
![Flow chart](https://i.imgur.com/y2yFStr.png)

## Demo
Detailed Process Reference[Video](https://youtu.be/omZaGmend-w): Below is a segmented description with images.
1. Connection

    As shown in the image below, in the top section of the interface (Available VISA Address and instrument type blocks), the program will automatically detect available I/O buses and drivers. Users can sequentially click on the instrument address and type, enter the instrument name, and click Connect to connect the instrument to the program.

    ![connection interface](https://i.imgur.com/7VUJIYb.png)
    
2. Measurement

    In the top left corner, select the connected instrument. The methods that can be operated on the instrument will appear in the bottom left corner. As shown in the example image below, if the user wants the instrument to output voltage, clicking Control will add it to the top right instrument output area. If the user wants to read the voltage, clicking Read will add it to the bottom right instrument measurement area. It is worth noting that the Control section adds instruments using the add child and add sibling methods. Using these two methods, the user can build a tree structure to arrange the experimental process.

    ![measurement interface](https://i.imgur.com/AjdLssa.png)

3. Graph

    The charting section will plot in a one-to-many manner.

    ![graph interface](https://i.imgur.com/5yTZuUy.png)

## Design
1. Connection

    This part is the instrument connection interface, designed using PyQt5 for the frontend. For driver detection, all drivers will inherit from the driver interface, ensuring that all instruments have four functions: power on, power off, read value, and write value.

2. Measurement

    For the experimental scheduling part, a tree data structure is used. Currently, this is implemented with a list, where the first element is the child, and all subsequent elements are siblings. This structure allows users to arrange any desired experimental steps. It is important to note that the experiment process starts from the current output value of the instrument to protect the sample from damage due to sudden pulses.

3. Graph

    For plotting, threads are used for parallel computation. This allows users to perform long experimental steps without the plotting process becoming unresponsive.

## File Descriptions
```
main.py : Entry point of the program.

data ： Temporary data storage.

drivers : Contains instrument driver files.

modpack : Stores modified modules.

qtdesign : Backup of the UI files created with QtDesign.

ui : Configures the frontend interface of the main program.

utils : Modules required for executing the main program.
```

## Installation
Before run this program, you need to install package below:
- PyQt5
- PyQtGraph
- PyVISA
- Pymeasure
- Numpy
- Labdrivers
- NIDAQmx
- QCoDes
- QCoDes_contrib_drivers
- QDarkStyle

In vscode, it can be installed with pip:

    python -m pip install -r requirements.txt

## Hint
transfer .ui to .py:

    pyuic5 -x "./qtdesign/main_window_qt.ui" -o "./ui/main_window_qt.py"
