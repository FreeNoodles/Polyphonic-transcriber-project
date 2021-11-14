#!/usr/bin/env python
# coding: utf-8

# In[1]:


import librosa
from librosa import display
import matplotlib.pyplot as plt
import scipy
import os
from mido import MidiFile
import pandas as pd
import numpy as np
import csv
import multiprocessing as mp
import shutil
import sounddevice as sd
import guitarpro as gp
import guitarpro.utils
import madmom


# In[2]:


def __calculateBeatDuration(beatObject,tempo):
    """" Calculates length of a beat """
    tupletNominator = beatObject.duration.tuplet.times #for possibility of triplets or more
    tupletDenominator = beatObject.duration.tuplet.enters
    
    quarterBeatDuration = (60.0 / tempo)
    time = quarterBeatDuration / ((beatObject.duration.value) / (beatObject.duration.value * (4/beatObject.duration.value)))
    time = time * (tupletNominator/tupletDenominator)
    if(beatObject.duration.isDotted):
        time = time * 1.5
        
    return time


def __checkTempoChange(beatObject):
    """ Check if the tempo has changed """
    if(beatObject.effect.mixTableChange is not None and beatObject.effect.mixTableChange.tempo is not None):
        isChanged = True
    else:
        isChanged = False
        
    return isChanged



# In[50]:



# pathSong1 = r'D:\PolyPhonic\data\gp3\Albeniz, Isaac - Leyenda.gp3.gp3'
# pathSong2 = r'D:\PolyPhonic\data\gp3\Mozart - Turkish March (2).gp4.gp3'
# pathSong3 = r'D:\PolyPhonic\data\gp3\Lizst, Franz - Liebesträume.gp3'
# pathSong4 =  r'D:\PolyPhonic\data\gp3\Tarrega, Francisco - Capricho arabe (2).gp3.gp3'
# pathSong5 = r'D:\PolyPhonic\data\gp3\8 Foot Sativa - Believer.gp4.gp3'
# pathSong6 = r'D:\PolyPhonic\data\gp3\Bass Pandora - Fallen Angel.gp3.gp3'
# songParsed = gp.parse()

# onsetTimeValues = []

# ##version 3

# counter = 0
# onsetTime = 0
# measureBeginRepeatGroup = None
# with open(r"C:\Users\Gebruiker\Desktop\Aerosmith_beats.csv",'w',newline='') as labels_file_guitar: #trimming down data

#     for track in songParsed.tracks:
#         measureTempo = track.song.tempo
#         startRepeatGroupLoop = False
#         for index,measure in enumerate(track.measures):  
#             measureDuration = 0 
#             measureInfo = "|"
            
                    

#             if(startRepeatGroupLoop):
#                 print('Started***********************')
#                 iteration = 1
#                 while (iteration <= measureEndRepeatGroup.repeatClose): ## Loop n times as indicated by the repeatClose number
#                     for measure in track.measures[(measureBeginRepeatGroup.number - 1): (measureEndRepeatGroup.number)]:
                    
#                         for beat in measure.voices[0].beats: ##check everybeat; Sharp Beat doesn't return mixTableChange.
#                             if(__checkTempoChange(beat)):
#                                 measureTempo =  beat.effect.mixTableChange.tempo.value

#                         if(iteration == measure.header.repeatAlternative and measure.header.repeatAlternative > 0 ):
#                             print('--------------------------------BREAK')
#                             break
                            
#                         print(f'-------------{measureInfo} {measure.number} tempo: {measureTempo} TimeSignature:{measure.timeSignature.denominator.value}/{measure.timeSignature.numerator}')
#                         for voice in measure.voices:
#                             for beat in voice.beats:
#                                 counter += 1
#                                 for note in beat.notes:
#                                     print(f'-------------({note.string},{note.value}) beat:{counter} - {onsetTime}  - effect:{note.effect.isDefault}')
                                             
#                                 onsetTimeValues.append(onsetTime)
#                                 measureDuration += __calculateBeatDuration(beat,measureTempo)
#                                 onsetTime += __calculateBeatDuration(beat,measureTempo)                   
#                     iteration +=1
           
#                 measure = track.measures[measureEndRepeatGroup.number] ##begin from end of repeat        
#                 ## --------------------------------------------->>>>>>>> measureBeginRepeatGroup = None 
#                 startRepeatGroupLoop = False     
                
#             for beat in measure.voices[0].beats: ##check everybeat; Sharp Beat doesn't return mixTableChange.
#                 if(__checkTempoChange(beat)):
#                     measureTempo =  beat.effect.mixTableChange.tempo.value
    
            
#             if(measure.header.isRepeatOpen):
#                 measureBeginRepeatGroup = measure
#                 print(measure.number)
                
#             if(measure.header.repeatClose > 0):
#                 measureEndRepeatGroup = measure
#                 startRepeatGroupLoop = True
#                 if(measureBeginRepeatGroup is None):
#                     measureBeginRepeatGroup = track.measures[0]
              
 
#             print(f'{measureInfo} {measure.number} tempo: {measureTempo} TimeSignature:              {measure.timeSignature.denominator.value}/{measure.timeSignature.numerator}')
#             for voice in measure.voices:
#                 for beat in voice.beats:
#                     counter += 1
                    
#                     for note in beat.notes:
#                         print(f'({note.string},{note.value}) beat:{counter} - {onsetTime} - effect:{note.effect.isDefault} beatChange: {__checkTempoChange(note.beat)}')
                        
#                     onsetTimeValues.append(onsetTime)
#                     measureDuration += __calculateBeatDuration(beat,measureTempo)
#                     onsetTime += __calculateBeatDuration(beat,measureTempo)
#             print(f'measureTempoisChanged: {__checkTempoChange(beat)} measureDuration: {measureDuration} repeatClose: {measure.header.repeatClose} repeatAlternative: {measure.header.repeatAlternative} repeatOpen: {measure.header.isRepeatOpen}')
# print(f'elapsedTime: {onsetTime} s\nbeats: {counter} songLength: {onsetTime + __calculateBeatDuration(beat,measureTempo)}')



# Make beat slices 1second long by filling or cutting the end of the beat?

# In[17]:


def transcribeGP3toTab(pathGP3File):
    """" Transcribe a GP3file to readable Tablature; 
    
         returns: list of beats in the form of [time,[listNotes]]
    
    """
    songParsed = gp.parse(pathGP3File)
    onsetTime = 0
    beatNotesList = []
    beatsList =[]
    measureBeginRepeatGroup = None
    
    for track in songParsed.tracks:
        measureTempo = track.song.tempo
        startRepeatGroupLoop = False   
        for index,measure in enumerate(track.measures):  
 
          
            if(startRepeatGroupLoop):
                iteration = 1
                while (iteration <= measureEndRepeatGroup.repeatClose):    
                                
                    for measure in track.measures[(measureBeginRepeatGroup.number -1): (measureEndRepeatGroup.number)]:
                             
                        for beat in measure.voices[0].beats: ##check everybeat; Sharp Beat doesn't return mixTableChange.
                            if(__checkTempoChange(beat)):
                                measureTempo =  beat.effect.mixTableChange.tempo.value
                        
                        if(iteration == measure.header.repeatAlternative and measure.header.repeatAlternative > 0 ):
                            break
                                       
                        for voice in measure.voices:
                            for beat in voice.beats:
                                for note in beat.notes:
                                    stringFretPair = (note.string,note.value)
                                    beatNotesList.append(stringFretPair)                                
                                rowBeat = [onsetTime,beatNotesList[:]]
                                beatsList.append(rowBeat)
                                beatNotesList.clear()
                                onsetTime += __calculateBeatDuration(beat,measureTempo)

                    iteration +=1
                            
                                
                measure = track.measures[measureEndRepeatGroup.number] ##begin from end of repeat        
                ## ---------------------------------------------->>>>>measureBeginRepeatGroup = None 
                startRepeatGroupLoop = False     
            
            for beat in measure.voices[0].beats: ##check everybeat; Sharp Beat doesn't return mixTableChange.
                if(__checkTempoChange(beat)):
                    measureTempo =  beat.effect.mixTableChange.tempo.value

            
            if(measure.header.isRepeatOpen):
                measureBeginRepeatGroup = measure
                
            if(measure.header.repeatClose > 0):
                measureEndRepeatGroup = measure
                startRepeatGroupLoop = True       
                if(measureBeginRepeatGroup is None):
                    measureBeginRepeatGroup = track.measures[0]                
           
            for voice in measure.voices:
                for beat in voice.beats:
                    for note in beat.notes:
                        stringFretPair = (note.string,note.value)
                        beatNotesList.append(stringFretPair)
                        
                    rowBeat = [onsetTime,beatNotesList[:]]
                    beatsList.append(rowBeat) 
                    beatNotesList.clear()
                    onsetTime += __calculateBeatDuration(beat,measureTempo)    

    
    return beatsList,onsetTime


# # Transforming StringFretPair to Decimal

# In[ ]:


dictionary_stringFret = {}
counter = 0
for string in range(1,7):
    for fret in range(0,25):
        dictionary_stringFret[counter] = (string,fret)
        counter += 1
dictionary_stringFret


# In[ ]:


def transformStringFretPair(beatList):
    """" Transform a stringFret pair into it's decimal representation """
    beatListTranscribed = []
    for row in beatList:
        placeHolderList = []
        placeHolderList.append(row[0])
        for column in row[1]:
            for key,value in dictionary_stringFret.items():
                if(column == value):
                    placeHolderList.append(key)
        beatListTranscribed.append(placeHolderList)

    return beatListTranscribed


# In[ ]:




