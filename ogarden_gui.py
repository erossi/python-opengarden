#!/usr/bin/python
#
# OpenGardenGui: a gui to control the OpenGarden appliance.
#
# Copyright (C) 2011-2015 Alessandro Dotti Contra <alessandro@hyboria.org>
#
# This software is free software and is released under the terms of
# the GPL version 3.
#
# Release: 0.3

#====================
# Modules
#====================

from Tkinter import *
import tkMessageBox
import tkFileDialog
import os
import sys
import platform
import time
import calendar
import subprocess
import ConfigParser
import locale
import gettext
from program import program
from opengarden import *

#====================
# Localization
#====================

def init_localization():
    """ Set the correct language for the application
    """
    locale.setlocale(locale.LC_ALL, '')    # Use user's preferred locale
    loc = locale.getdefaultlocale()        # Locale in use
    t = gettext.translation('opengarden', 'locale', loc, fallback=True)
    t.install()

init_localization()

#====================
# Global data
#====================

appName = "Open Garden"

appliance = OpenGarden() #The appliance
device = None #Which port the appliance is connected to

isConnected = False #Connection with the appliance
maxPrograms = 19 #Maximum nuber of programs the appliance can store
selectedProgram = False #Track which program is being currently selected
toSave = False #Track if the list of programs needs to be saved
toSync = False #Track if the list of programs nedds to be synced

form = False #Add/Edit program form
config = False #Configure appliance form
gui = False #Configure GUI form
test = False #Test appliace form
note = False #Note editor window

programs = [] #List of programs
noteContent = '' #Notes associated with programs

days = (_("mon"),_("tue"),_("wed"),_("thu"),_("fri"),_("sat"),_("sun"))
valveSettings = {"bistable":_("Bistable BATT"), "monostable":"24Vac"}
alarmSettings = {"HIGH":"HIGH = N.C.", "LOW":"LOW = N.O."}
noteMarker = "#Notes begin here\n"
tempSettings = {'celsius':'Celsius','fahrenheit':'Fahrenheit'}
displayTemp = "celsius" #Display temperatures in celsius degrees by default

#====================
# Interface layout settings
#====================

fmtButtonWidth = 20
fmtPadding = 5

#====================
# Callbacks
#====================

def exit():
    """
    Exit program
    """
    global isConnected,toSave

    #Check if the appliance is connected, then disconnect
    if isConnected:
        disconnect()
    
    #Check if the programs list needs to be saved
    if toSave:
        if askSave():
            savePrograms()

    mainWindow.quit()

def connect():
    """ Connect the appliance, Sync time and get the stored programs list and check alarms
    """
    global isConnected,appliance,device,programs,toSave

    try:
        appliance.connect(device)
    except:
        showError(_("Unable to connect to the appliance"))
        isConnected = False
    else:
        if not appliance.version:
            showError(_("Unknown appliance"))
        else:
            isConnected = True

            #Get appliance's information
            appliance.load()

            #Sync appliance's time
            appliance.time(calendar.timegm(time.localtime()))

            #Check if the programs list needs to be saved
            if toSave:
                if askSave():
                    savePrograms()

            #Load programs
            programs = decodePrograms(appliance.programs)
            loadPrograms()
            enableButton(configureButton)
            enableButton(testButton)
            if len(programs) > 0:
                enableButton(saveButton)
            disableButton(syncButton)

            #Check alarms
            setAlarmStatus(appliance.get_alarm())
            enableButton(alarmButton)

    setConnectorStatus()

def disconnect():
    """ Disconnect the appliance
    """
    global isConnected, toSync

    #Check if the program list has to be synced
    if toSync:
        if askSync():
            syncAppliance()

    appliance.disconnect()
    isConnected = False
    setConnectorStatus()
    setAlarmStatus(None)

    #Disable buttons
    disableButton(configureButton)
    disableButton(testButton)
    disableButton(syncButton)
    disableButton(alarmButton)

def addProgram():
    """ Add a new program
    """
    displayProgramForm("add")

def editProgram():
    """ Edit the currently selected program
    """
    global selectedProgram, programs

    displayProgramForm("edit",programs[selectedProgram])

def closeProgramForm():
    """ Close add/edit program form (cancel action)
    """
    form.destroy()

def closeTestForm():
    """ Close appliance test form (cancel action)
    """
    test.destroy()

def closeGuiForm():
    """ Close GUI configuration form (cancel action)
    """
    gui.destroy()

def closeConfigForm():
    """ Close appliance configuration form (cancel action)
    """
    config.destroy()

def processProgram(action):
    """ Get program data from form, validate them and
    create/update a program.
    """
    data = validateProgram()
    if data:
        storeProgram(action,data)
        form.destroy()

def checkDay(day):
    """ Check if a day was choosen in the program add/edit form
    """
    return not day.get()

def storeProgram(action,data):
    """ Store a program in the programs list
    """
    global programs,selectedProgram

    if action == "add":
        p = program()
    else:
        p = programs[selectedProgram]

    p.startTime(data['start'])
    p.length(data['length'])
    p.line(data['line'])
    p.days(data['days'])

    if action == "add":
        programs.append(p)
    else:
        programs[selectedProgram] = p

    #Track the change to the list of programs
    global toSave, toSync
    toSave = True
    toSync = True
    loadPrograms()

    #Enable relevant buttons
    enableButton(saveButton)
    if isConnected:
        enableButton(syncButton)

def selectedProgram(event):
    """ Track which program has been selected in the programsList
    listbox
    """
    global selectedProgram

    if event.widget.curselection():
        selectedProgram = int(event.widget.curselection()[0])    #The selected program

        #Enable relevant buttons
        enableButton(editButton)
        enableButton(deleteButton)

def deleteProgram():
    """ Delete the currently selected program
    """
    global selectedProgram, programs, toSave, toSync
    del programs[selectedProgram]
    toSave = True
    toSync = True
    loadPrograms()

def savePrograms():
    """ Save the current programs list to file.
    """
    global programs, toSave, noteContent, noteMarker

    fileName = tkFileDialog.asksaveasfilename(title=_("Save programs"),filetypes=[(_("Data"),"*.dat")])
    if len(fileName) > 0:
        try:
            f = open(fileName, "wb")
        except:
            showError(_("Can't save data file"))
            return
        #Save programs
        for program in encodePrograms(programs):
            f.write(program)
        #Save notes
        f.write(noteMarker)
        f.write(noteContent)
        f.close()
        disableButton(saveButton)
        toSave = False

def readPrograms():
    """ Read a list of programs from a previously saved data file.
    """
    global programs,isConnected,toSync,toSave,noteContent,noteMarker

    if isConnected and toSync:
        if askSync():
            syncAppliance()

    if toSave:
        if askSave():
            savePrograms()

    fileName = tkFileDialog.askopenfilename(title=_("Load programs"),filetypes=[(_("Data"),"*.dat")])
    if len(fileName) > 0:
        try:
            f = open(fileName, "rb")
        except:
            showError(_("Can't read data file"))
            return
        lines = f.readlines()
        plines = []        #Lines representing programs

        #Separate programs and notes
        storeProgram = True
        for line in lines:
            if line == noteMarker:
                storeProgram = False
                continue
            if storeProgram:
                plines.append(line)
            else:
                noteContent = noteContent + line
        f.close()

        #Decode programs (if any)
        if plines:
            programs = decodePrograms(plines)
            loadPrograms()
            toSync = True

def syncAppliance():
    """ Sync the appliance.
    """
    global programs, toSync

    appliance.programs = encodePrograms(programs)
    appliance.save()
    toSync = False

    disableButton(syncButton)

def configGui(tempOptions,temp):
    """ Config GUI
    """
    global gui
    global displayTemp

    displayTemp = setFromLabel(tempSettings,temp.get())
    gui.destroy()

def configAppliance(site,siteOptions,valve,led,alarm):
    """ Config the appliance
    """
    global appliance
    global config

    appliance.sunsite = siteOptions.index(site.get())
    appliance.valve = setFromLabel(valveSettings,valve.get())
    appliance.led = led.get()
    appliance.alarm = setFromLabel(alarmSettings,alarm.get())
    appliance.save()
    config.destroy()

def checkAlarms():
    """ Check if there are active alarms
    """
    global appliance
    setAlarmStatus(appliance.get_alarm())

def openNoteEditor():
    """ Open the note editor
    """
    global note, noteContent

    #Build the editor window
    note = Toplevel(mainWindow)
    note.title(_("Notes"))

    #Add text widget with scrollbar
    text = Text(note, background='white')
    scroll = Scrollbar(note)
    text.configure(yscrollcommand=scroll.set)
    text.grid(row=0, column=0, columnspan=3, padx=fmtPadding, pady=fmtPadding, sticky=N+W+E+S)
    scroll.grid(row=0, column=3, sticky=N+S)

    #Display note content
    text.insert(END,noteContent)
    text.focus()

    #Disable Notes button
    disableButton(notesButton)

    #Bind note editor events
    note.protocol("WM_DELETE_WINDOW", closeNoteEditor)
    note.bind('<Key>', lambda event, widget = text: storeNoteContent(event,widget))

def closeNoteEditor():
    """ Close the note editor
    """
    #Enable Notes button
    enableButton(notesButton)
    note.destroy()

def storeNoteContent(event,widget):
    """ Store note content. event (a key pressed) is ignored.
    """
    global noteContent, toSave

    #Get note content
    noteContent = widget.get(1.0,END)[:-1] #The last character is always a \n

    #Mark programs list as changed
    toSave = True
    enableButton(saveButton)

#====================
# General functions
#====================

def ogTemp(temp):
    """ Return temperature according to GUI settings
    """
    global displayTemp
    if displayTemp == 'fahrenheit':
        return (float(temp) * 9/5) + 32
    else:
        return temp

def showError(string):
    """ Display an error message.
    """
    tkMessageBox.showerror(title=_("Error"), message=string)

def setConnectorStatus():
    """ Set Connector's attributes based on the status
    of the connection with the appliance
    """
    if isConnected :
        connectButton.configure(text=_("Disconnect"), command=disconnect)
        connectLabel.configure(text=_("Connected"))
    else:
        connectButton.configure(text=_("Connect"), command=connect)
        connectLabel.configure(text=_("Not connected"))

def setAlarmStatus(alarm):
    """ Display alarm status information in the bottom bar
    """
    if alarm == None:
        alarmStatus.configure(text="")
    else:
        if alarm == "ON":
            alarmStatus.configure(text=_("Warning! Alarms reported"),fg="red")
        else:
            alarmStatus.configure(text=_("No alarm reported"),fg="black")

def disableButton(button):
    """ Disable a button
    """
    button.configure(state=DISABLED)

def enableButton(button):
    """ Enable a button
    """
    button.configure(state=ACTIVE)

def makeModal(window,parent):
    """ Turn window into a modal dialog.
    """
    window.focus_set()
    window.grab_set()
    window.transient(parent)
    window.wait_window(window)

def displayProgramForm(action, program=None):
    """ Display the form to add or edit a program.
    """
    global form

    title = _("New program") if action == "add" else _("Modify program")

    form = Toplevel(mainWindow)
    form.title(title)

    #Program's line
    lineLabel = Label(form, text=_("Line"))
    lineLabel.grid(row=0, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    lineSpin = Spinbox(form, name="line", width=(fmtButtonWidth - fmtPadding)/2, from_=1, to=8, justify=RIGHT)
    lineSpin.grid(row=0, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)

    #Program's start hour/minute
    startLabel = Label(form, text=_("Start (HH:MM)"))
    startLabel.grid(row=1, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    startHourSpin = Spinbox(form, name="startHour", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=23, justify=RIGHT)
    startHourSpin.grid(row=1, column=1, sticky=W, padx=fmtPadding, pady=fmtPadding)
    startMinuteSpin = Spinbox(form, name="startMinute", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=59, justify=RIGHT)
    startMinuteSpin.grid(row=1, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)

    #Program's lenght
    lenghtLabel = Label(form, text=_("Duration (HH:MM)"))
    lenghtLabel.grid(row=2, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    lengthHourSpin = Spinbox(form, name="lengthHours", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=23, justify=RIGHT)
    lengthHourSpin.grid(row=2, column=1, sticky=W, padx=fmtPadding, pady=fmtPadding)
    lengthMinuteSpin = Spinbox(form, name="lengthMinutes", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=59, justify=RIGHT)
    lengthMinuteSpin.grid(row=2, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)
    
    #Days of week
    (mon, tue, wed, thu, fri, sat, sun) = (IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar())
    chkMonday = Checkbutton(form, name=days[0], text=days[0].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=mon, command=(lambda day=mon: checkDay(day)))
    chkMonday.grid(row=4, column=0, sticky=W, padx=fmtPadding, pady=fmtPadding)
    chkTuesday = Checkbutton(form, name=days[1], text=days[1].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=tue, command=(lambda day=tue: checkDay(day)))
    chkTuesday.grid(row=4, column=0, sticky=E, padx=fmtPadding, pady=fmtPadding)
    chkWednesday = Checkbutton(form, name=days[2], text=days[2].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=wed, command=(lambda day=wed: checkDay(day)))
    chkWednesday.grid(row=4, column=1, sticky=W, padx=fmtPadding, pady=fmtPadding)
    chkThursday = Checkbutton(form, name=days[3], text=days[3].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=thu, command=(lambda day=thu: checkDay(day)))
    chkThursday.grid(row=4, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)
    chkFriday = Checkbutton(form, name=days[4], text=days[4].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=fri, command=(lambda day=fri: checkDay(day)))
    chkFriday.grid(row=5, column=0, sticky=W, padx=fmtPadding, pady=fmtPadding)
    chkSaturday = Checkbutton(form, name=days[5], text=days[5].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=sat, command=(lambda day=sat: checkDay(day)))
    chkSaturday.grid(row=5, column=0, sticky=E, padx=fmtPadding, pady=fmtPadding)
    chkSunday = Checkbutton(form, name=days[6], text=days[6].capitalize(), width=(fmtButtonWidth - fmtPadding)/2, variable=sun, command=(lambda day=sun: checkDay(day)))
    chkSunday.grid(row=5, column=1, sticky=W, padx=fmtPadding, pady=fmtPadding)

    #Ok button
    okButton = Button(form, width=fmtButtonWidth, text="Ok", command=(lambda: processProgram(action)))
    okButton.grid(row=6, column=0, padx=fmtPadding, pady=fmtPadding)

    #Cancel button
    cancelButton = Button(form, width=fmtButtonWidth, text=_("Cancel"), command=closeProgramForm)
    cancelButton.grid(row=6, column=1, padx=fmtPadding, pady=fmtPadding)

    #In case of edit request, load the form with the appropriate values
    if program:
        (hour,minute) = program.startTime().split(':')
        startHourSpin.delete(0,END)
        startHourSpin.insert(0,hour)
        startMinuteSpin.delete(0,END)
        startMinuteSpin.insert(0,minute)

        length = int(program.length())
        hours = length / 60
        minutes = length % 60
        lengthHourSpin.delete(0,END)
        lengthHourSpin.insert(0,hours)
        lengthMinuteSpin.delete(0,END)
        lengthMinuteSpin.insert(0,minutes)

        lineSpin.delete(0,END)
        lineSpin.insert(0,program.line())

        for day in program.days():
            form.nametowidget(day).invoke()

    makeModal(form,mainWindow)

def displayGuiForm():
    """ Display the form to configure the GUI
    """
    global gui
    gui = Toplevel(mainWindow)
    gui.title(_("Configure GUI"))

    #Display temperature
    tempLabel = Label(gui, text=_("Display temperatures"))
    tempLabel.grid(row=0, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    tempOptions = tempSettings.values()
    tempVar = StringVar()
    tempVar.set(tempSettings[displayTemp])
    tempMenu = OptionMenu(gui, tempVar, *tempOptions)
    tempMenu.grid(row=0, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    #Apply button
    applyButton = Button(gui, width=fmtButtonWidth, text=_("Apply"), command=(lambda: configGui(tempSettings,tempVar)))
    applyButton.grid(row=1, column=0, padx=fmtPadding, pady=fmtPadding)

    #Cancel button
    cancelButton = Button(gui, width=fmtButtonWidth, text=_("Cancel"), command=closeGuiForm)
    cancelButton.grid(row=1, column=1, padx=fmtPadding, pady=fmtPadding)

    makeModal(gui,mainWindow)

def displayConfigForm():
    """ Display the form to configure the appliance
    """
    global config
    global appliance
    global displayTemp

    config = Toplevel(mainWindow)
    config.title(_("Configure appliance"))

    row = 0

    #Appliance's version
    idLabel = Label(config, text=_("Appliance version"))
    idLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    idValueLabel = Label(config, text=appliance.version)
    idValueLabel.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    # Appliance's serial number
    idLabel = Label(config, text=_("Serial number"))
    idLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    idValueLabel = Label(config, text=appliance.serial)
    idValueLabel.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    # Appliance's time
    idLabel = Label(config, text=_("Date"))
    idLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    idValueLabel = Label(config, \
            text=time.strftime("%d %b %Y %H:%M:%S", \
            time.gmtime(int(appliance.time()))))
    idValueLabel.grid(row=row, column=1, padx=fmtPadding, \
            pady=fmtPadding, sticky=N+W)
    row+=1

    #Temperature
    temperature = appliance.temperature()

    tempLabel = Label(config, text=_("Temperature"))
    tempLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    tempValueLabel = Label(config, text=ogTemp(temperature[0]))
    tempValueLabel.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    avgTempLabel = Label(config, text=_("24h avg. temperature"))
    avgTempLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    avgTempValueLabel = Label(config, text=ogTemp(temperature[1]))
    avgTempValueLabel.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row*=1

    dfactorLabel = Label(config, text="D Factor")
    dfactorLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    dfactorValueLabel = Label(config, text=temperature[2])
    dfactorValueLabel.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    #Site
    siteLabel = Label(config, text=_("Average external temperature"))
    siteLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    if displayTemp == 'fahrenheit':
        siteOptions =(_("75 to 93 degrees"), _("68 to 90 degrees"), \
                _("59 to 77 degrees"))
    else:
        siteOptions =(_("24 to 34 degrees"), _("20 to 32 degrees"), \
                _("15 to 25 degrees"))

    siteVar = StringVar()
    siteVar.set(siteOptions[int(appliance.sunsite)])
    siteMenu = OptionMenu(config, siteVar, *siteOptions)
    siteMenu.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    #Valve
    valveLabel = Label(config, text=_("Valve type"))
    valveLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    valveOptions = valveSettings.values()
    valveVar = StringVar()
    valveVar.set(valveSettings[appliance.valve])
    valveMenu = OptionMenu(config, valveVar, *valveOptions)
    valveMenu.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    #Led
    ledLabel = Label(config, text=_("Leds configuration"))
    ledLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    ledOptions =("ON", "OFF")
    ledVar = StringVar()
    ledVar.set(appliance.led)
    ledMenu = OptionMenu(config, ledVar, *ledOptions)
    ledMenu.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    #Alarms
    alarmLabel = Label(config, text=_("Alarm level"))
    alarmLabel.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    alarmOptions = alarmSettings.values()
    alarmVar = StringVar()
    alarmVar.set(alarmSettings[appliance.alarm])
    alarmMenu = OptionMenu(config, alarmVar, *alarmOptions)
    alarmMenu.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    row+=1

    #Apply button
    applyButton = Button(config, width=fmtButtonWidth, text=_("Apply"), command=(lambda: configAppliance(siteVar,siteOptions,valveVar,ledVar,alarmVar)))
    applyButton.grid(row=row, column=0, padx=fmtPadding, pady=fmtPadding)

    #Cancel button
    cancelButton = Button(config, width=fmtButtonWidth, text=_("Cancel"), command=closeConfigForm)
    cancelButton.grid(row=row, column=1, padx=fmtPadding, pady=fmtPadding)

    makeModal(config,mainWindow)

def displayTestForm():
    """ Display the form to test the appliance
    """
    global test
    global appliance

    test = Toplevel(mainWindow)
    test.title(_("Test appliance"))

    warnLabel = Label(test, text=_("Warning! The test will reset appliance's programming"))
    warnLabel.grid(row=0, column=0, columnspan=2, padx=fmtPadding, pady=fmtPadding, sticky=N+W)

    #Test start hour/minute
    startLabel = Label(test, text=_("Start time (HH:MM)"))
    startLabel.grid(row=1, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    startHourSpin = Spinbox(test, name="startHour", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=23, justify=RIGHT)
    startHourSpin.grid(row=1, column=1, sticky=W, padx=fmtPadding, pady=fmtPadding)
    startMinuteSpin = Spinbox(test, name="startMinute", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=59, justify=RIGHT)
    startMinuteSpin.grid(row=1, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)

    #Test lenght per sector
    lenghtLabel = Label(test, text=_("Duration per line (MM)"))
    lenghtLabel.grid(row=2, column=0, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
    lengthSpin = Spinbox(test, name="length", width=(fmtButtonWidth - fmtPadding)/2, from_=0, to=59, justify=RIGHT)
    lengthSpin.grid(row=2, column=1, sticky=E, padx=fmtPadding, pady=fmtPadding)

    #Ok button
    okButton = Button(test, width=fmtButtonWidth, text="Ok", command=createTestPrograms)
    okButton.grid(row=3, column=0, padx=fmtPadding, pady=fmtPadding)

    #Cancel button
    cancelButton = Button(test, width=fmtButtonWidth, text=_("Cancel"), command=closeTestForm)
    cancelButton.grid(row=3, column=1, padx=fmtPadding, pady=fmtPadding)

    makeModal(test,mainWindow)

def validateProgram():
    """ Check if the data for the program are valid.

    Return a dictionary with program parameters or False.
    """
    global days

    data = {}

    startHour = int(form.nametowidget("startHour").get())
    startMinute = int(form.nametowidget("startMinute").get())
    if 0 <= startHour <= 23 and 0 <= startMinute <= 59:
        data['start'] = str(startHour).zfill(2) + ":" + str(startMinute).zfill(2)
    else:
        showError(_("Wrong start time: %s:%s") % (startHour, startMinute))
        return False

    lengthHours = int(form.nametowidget("lengthHours").get())
    lengthMinutes = int(form.nametowidget("lengthMinutes").get())
    if (0 <= lengthHours <= 23 and 1 <= lengthMinutes <=59) or (1 <= lengthHours <= 23 and 0 <= lengthMinutes <=59):
        data['length'] = str(lengthHours * 60 + lengthMinutes)
    else:
        showError(_("Wrong duration: %s:%s") % (lengthHours, lengthMinutes))
        return False

    line = int(form.nametowidget("line").get())
    if 1 <= line <= 8:
        data['line'] = str(line)
    else:
        showError(_("Wrong line number: %s") % line)
        return False

    pdays = []
    for day in days:
        if form.nametowidget(day).invoke():
            pdays.append(day)
    if pdays:
        data['days'] = pdays
    else:
        showError(_("No day was specified"))
        return False

    return data

def loadPrograms():
    """ Load stored programs in the programs list widget
    """
    global programs, maxPrograms, isConnected

    #Load programs list (empty it first)
    programsList.delete(0, END)
    for p in programs:
        programsList.insert(END, p.asString())

    #If we have the maximum number of programs already, prevent new programs
    #from being created
    if len(programs) >= maxPrograms:
        disableButton(newButton)

    #Enable save button
    enableButton(saveButton)

    #Enable sync button if the appliance is connected
    if isConnected:
        enableButton(syncButton)

def decodePrograms(programs):
    """ Decode programs read from the appliance.
    Programs are stored as comma separated strings,
    each field having the following meaning:

    0 - the id
    1 - start time (four digits, two for the hour and two for the minutes)
    2 - duration in minutes
    3 - days of week (hex bitmapped)
    4 - output line

    Returns an array of program objects.
    """
    global days

    prgs = []

    for prog in programs:
        p = program()
        data = prog.split(',')
        p.startTime(data[1][:2]+':'+data[1][2:])
        p.length(int(data[2]))
        p.line(int(data[4])+1)

        d = []
        for n,i in enumerate(days):
            if (2**n) & int(data[3], 16):
                d.append(i)

        p.days(d)
        prgs.append(p)

    return prgs

def encodePrograms(programs):
    """ Encode programs in an appliance supported format.
    See decodePrograms for format details.

    Returns an array of encoded program strings.
    """
    global days
    prgs = []

    for program in programs:
        i = 0
        #Bitmap the days
        d = 0
        for day in program.days():
            i = days.index(day)
            d = d | 2**i

        #Create the encoded program string
        p = "%02d,%s,%03d,%2s,%d\n" % (i, \
            "".join(program.startTime().split(':')), \
            int(program.length()), \
            hex(d)[2:], \
            int(program.line())-1)

        prgs.append(p)
        i += 1

    return prgs

def askSync():
    """ Ask the user if the program list has to be synced.
    """
    return tkMessageBox.askyesno(_("Warning!"), _("Programs list was modified. Sync anyway?"))

def askSave():
    """ Ask the user if the program list has to be saved.
    """
    return tkMessageBox.askyesno(_("Warning!"), _("Programs list was modified. Save to disk?"))

def createTestPrograms():
    """ Create a set of programs to test the appliance.
    WARNING: this will delete the current programs and reset the appliance.
    """
    global programs, days, toSave

    #Get test start time 
    startHour = int(test.nametowidget("startHour").get())
    startMinute = int(test.nametowidget("startMinute").get())

    if not (0 <= startHour <= 23 and 0 <= startMinute <= 59):
        showError(_("Wrong start time: %s:%s") % (startHour, startMinute))
        return False

    length = int(test.nametowidget("length").get())
    if not 0 < length <= 59:
        showError(_("Wrong test duration: %s") % length)
        return False

    #Get appliance time and calculate if the test is today or tomorrow.
    #If test time is earlier than current appliance time test will be performed
    #tomorrow

    day = None

    now = time.gmtime(float(appliance.time()))

    if startHour < now[3]:
        day = now[6] + 1
    elif startHour == now[3]:
        if startMinute <= now[4]:
            day = now[6] + 1
        else:
            day = now[6]
    else:
        day = now[6]

    #Empty programs list
    programs = []

    #Create test programs
    for i in range(8):
        data = {}
        data['start'] = str(startHour).zfill(2) + ":" + str(startMinute).zfill(2)
        data['length'] = length
        data['line'] = i+1
        data['days'] = (days[day],)
        storeProgram('add',data)

        #Evalute date and time of next program
        startMinute += length + 1
        if startMinute > 59:
            startHour += 1
            startMinute -=60
            if startHour > 23:
                startHour -= 24
                day += 1

    #Sync appliance
    syncAppliance()
    toSave = False

    test.destroy()

def probeDevice(platform):
    """ Probe which device the appliance is connected to.
    """
    if platform == "Windows":
        portNumber = subprocess.call("OpenGardenUSB.exe")
        if portNumber < 1000:
                device = "COM" + str(portNumber)
        else:
                device = "COM25"
    elif platform == "Linux":
        device = "/dev/ttyUSB0"
    else:
        device = "COM25"
    return device

def setFromLabel(settings,value):
    """ Return the setting corresponding to the given label
    """
    for setting, label in settings.iteritems():
        if label == value:
            return setting
    return None

#====================
# The main window
#====================

#The main window itself

mainWindow = Tk()
mainWindow.title(appName)

mainWindow.protocol("WM_DELETE_WINDOW", exit)

#Connect button and status (label). This widgets toghether are identified as
#"Connector"
connectButton = Button(width=fmtButtonWidth)
connectLabel = Label()
#Configure GUI button
guiButton = Button(width=fmtButtonWidth, text=_("Configure GUI"), command=displayGuiForm)
#Configure appliance button
configureButton = Button(width=fmtButtonWidth, text=_("Configure appliance"), command=displayConfigForm)
#Test appliance button
testButton = Button(width=fmtButtonWidth, text=_("Test appliance"), command=displayTestForm)
#Load programs list from disk button
loadButton = Button(width=fmtButtonWidth, text=_("Load programs list"), command=readPrograms)
#Save programs list to disk button
saveButton = Button(width=fmtButtonWidth, text=_("Save programs list"), command=savePrograms)
#Exit button
exitButton = Button(text=_("Exit"), command=exit, width=fmtButtonWidth)
#New program button
newButton = Button(width=fmtButtonWidth, text=_("New program"), command=addProgram)
#Edit program button
editButton = Button(width=fmtButtonWidth, text=_("Modify program"), command=editProgram)
#Delete program button
deleteButton = Button(width=fmtButtonWidth, text=_("Delete program"), command=deleteProgram)
#Sync appliance button
syncButton = Button(width=fmtButtonWidth, text=_("Sync appliance"), command=syncAppliance)
#Programs list widget
programsList = Listbox(height=maxPrograms, selectmode=SINGLE)
programsList.bind("<<ListboxSelect>>", selectedProgram)
#Alarms status bar
alarmStatus = Label()
alarmButton = Button(text=_("Check alarms"), command=checkAlarms, width=fmtButtonWidth)
#Manage notes button
notesButton = Button(width=fmtButtonWidth, text=_("Notes"), command=openNoteEditor)

#Place items on the grid
connectButton.grid(row=0, column=0, padx=fmtPadding, pady=fmtPadding)
loadButton.grid(row=0, column=1, padx=fmtPadding, pady=fmtPadding)
saveButton.grid(row=0, column=2, padx=fmtPadding, pady=fmtPadding)
exitButton.grid(row=0, column=3, padx=fmtPadding, pady=fmtPadding)
connectLabel.grid(row=1, column=0, columnspan=2, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
guiButton.grid(row=1, column=2, padx=fmtPadding, pady=fmtPadding)
configureButton.grid(row=1, column=3, padx=fmtPadding, pady=fmtPadding)
notesButton.grid(row=1, column=1, padx=fmtPadding, pady=fmtPadding)
newButton.grid(row=3, column=0, padx=fmtPadding, pady=fmtPadding)
editButton.grid(row=3, column=1, padx=fmtPadding, pady=fmtPadding)
deleteButton.grid(row=3, column=2, padx=fmtPadding, pady=fmtPadding)
syncButton.grid(row=3, column=3, padx=fmtPadding, pady=fmtPadding)
programsList.grid(row=2, column=0, columnspan=4, padx=fmtPadding, pady=fmtPadding, sticky=N+W+E+S)
alarmStatus.grid(row=4, column=0, columnspan=3, padx=fmtPadding, pady=fmtPadding, sticky=N+W)
alarmButton.grid(row=4, column=2, padx=fmtPadding, pady=fmtPadding)
testButton.grid(row=4, column=3, padx=fmtPadding, pady=fmtPadding)

#Set interface initial status
setConnectorStatus()
disableButton(saveButton)
disableButton(editButton)
disableButton(deleteButton)
disableButton(syncButton)
disableButton(configureButton)
disableButton(testButton)
disableButton(alarmButton)

#====================
# Start the main loop
#====================

# Set on wich device the appliance is connected to

device = probeDevice(platform.system())

# Start GUI

mainWindow.mainloop()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
