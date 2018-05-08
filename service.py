#!/usr/bin/env python
# -*- coding: utf-8 -*-

#5.8.2017 - Steven M. Schacht - DigitaleServiceAnzeige kurz: DSA Ausf. B-2 
#Fuer BMW e46 und e39

import xbmcaddon
import xbmcvfs
import xbmcgui
import xbmc
import os
import sys
import time
import socket
from datetime import datetime
from time import sleep


#------------------Funktionen------------------#
#Kilometerstand aus dem Kombi abfragen mit TCP,TCP mit dem command "OBC;GET;ODOMETER"
def send_tcp_command(message):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ok
    clientsocket.settimeout(0.1)  # ok
	
    port = 8089
    try:
        clientsocket.connect(('localhost', port))  # 127.0.0.1 ok
    except:
        raise ValueError

    clientsocket.send(message)  # obc;get;odometer #ok
    # time.sleep(0.2)

    clientsocket.settimeout(0.2)  # auf antwort warten ok

    # time.sleep(0.2)

    clientsocket.settimeout(0.2)  # ok
    clientsocket.shutdown(True)  # ok

    data = clientsocket.recv(50).replace('\n', '')  # antwort nicht groesser 50 nicht weniger 50 ok
    return data

#s.h oben, uebergabe odometer
def get_odometer():
    try:
        odometer = int(send_tcp_command('obc;get;odometer')) #ok
    except ValueError:
        odometer = -1

    if odometer < 0:
        xbmc.executebuiltin('Notification(ERROR:, TCP returns: %s, %d)' % (odometer, time)) #ok
        return 136000 # Um zu verhindern das er quatsch in die variable schreibt, dummywert
    else:
        return odometer #ok
	
#Wert zuruecksetzen in resKmWert[Index] 
def resetPointDSANeuschreiben(indexIntervallWert):
	
	if indexIntervallWert==8 or indexIntervallWert==10 or indexIntervallWert==12:
		if indexIntervallWert == 8: #jahr und monat manuell
			resetJahr = JahrMonat.year + 2
			resetMonat = JahrMonat.month - 1
			_addonSettings_.setSetting(id="Bremsfluessigkeit_Jahr", value=str(resetJahr)) 	#Achtung: 0,1,2,3,4,5,6,7,8,9,10,11 = 12,11,10,9,8,7,6,5,4,3,2,1
			_addonSettings_.setSetting(id="Bremsfluessigkeit_Monat", value=str(resetMonat)) 
		
		if indexIntervallWert == 10:
			resetJahr = JahrMonat.year + 2
			resetMonat = JahrMonat.month - 1
			_addonSettings_.setSetting(id="Hauptuntersuchung_Jahr", value=str(resetJahr))
			_addonSettings_.setSetting(id="Hauptuntersuchung_Monat", value=str(resetMonat))
			
		if indexIntervallWert == 12:
			resetJahr = JahrMonat.year + 2
			resetMonat = JahrMonat.month - 1
			_addonSettings_.setSetting(id="Abgasuntersuchung_Jahr", value=str(resetJahr))
			_addonSettings_.setSetting(id="Abgasuntersuchung_Monat", value=str(resetMonat))
			
		readFile()
		
	else:
		resKmWert[indexIntervallWert] = aktKilometer
		
		_addonSettings_.setSetting(id="insp_I", value=str(resKmWert[0]))
		_addonSettings_.setSetting(id="insp_II", value=str(resKmWert[1]))
		_addonSettings_.setSetting(id="oil", value=str(resKmWert[2]))
		_addonSettings_.setSetting(id="kerzen", value=str(resKmWert[3]))
		_addonSettings_.setSetting(id="micro_filter", value=str(resKmWert[4]))
		_addonSettings_.setSetting(id="br_VA", value=str(resKmWert[6]))
		_addonSettings_.setSetting(id="br_HA", value=str(resKmWert[7]))
		_addonSettings_.setSetting(id="luft_filter", value=str(resKmWert[5]))
		
	
#Datei auslesen
def readFile():
	#Kilometerstände beide denen Resettet wurde
	resKmWert[0] = _addonSettings_.getSetting("insp_I")
	resKmWert[1] = _addonSettings_.getSetting("insp_II")
	resKmWert[2] = _addonSettings_.getSetting("oil")
	resKmWert[3] = _addonSettings_.getSetting("kerzen")
	resKmWert[4] = _addonSettings_.getSetting("micro_filter")
	resKmWert[5] = _addonSettings_.getSetting("luft_filter")
	resKmWert[6] = _addonSettings_.getSetting("br_VA")
	resKmWert[7] = _addonSettings_.getSetting("br_HA")
	
	resKmWert[8] = _addonSettings_.getSetting("Bremsfluessigkeit_Jahr")
	resKmWert[9] = _addonSettings_.getSetting("Bremsfluessigkeit_Monat") #Achtung: 0,1,2,3,4,5,6,7,8,9,10,11 = 12,11,10,9,8,7,6,5,4,3,2,1
	resKmWert[9] = int(resKmWert[9]) + 1 #Monat korrigieren Achtung String zu Int!
	resKmWert[10] = _addonSettings_.getSetting("Hauptuntersuchung_Jahr")
	resKmWert[11] = _addonSettings_.getSetting("Hauptuntersuchung_Monat")
	resKmWert[11] = int(resKmWert[11]) + 1
	resKmWert[12] = _addonSettings_.getSetting("Abgasuntersuchung_Jahr")
	resKmWert[13] = _addonSettings_.getSetting("Abgasuntersuchung_Monat")
	resKmWert[13] = int(resKmWert[13]) + 1
	
	#Intervalle
	ausgIntervalle[0] = _addonSettings_.getSetting("Inspektion_1") #NUMBERs
	ausgIntervalle[1] = _addonSettings_.getSetting("Inspektion_2")
	ausgIntervalle[2] = _addonSettings_.getSetting("Oilservice")
	ausgIntervalle[3] = _addonSettings_.getSetting("Zuendkerzen")
	ausgIntervalle[4] = _addonSettings_.getSetting("Microfilter")
	ausgIntervalle[5] = _addonSettings_.getSetting("Luftfilter")
	ausgIntervalle[6] = _addonSettings_.getSetting("Bremsen_VA")
	ausgIntervalle[7] = _addonSettings_.getSetting("Bremsen_HA")
		#ausgIntervalle[10] = _addonSettings_.getSetting("Dieselpartikelfilter") #Ersetzen mit Zuendkerzen
		#ausgIntervalle[11] = _addonSettings_.getSetting("Getriebeservice") 		#ersetzen mit Luftfilter
	
	ausgIntervalle[8] = _addonSettings_.getSetting("Kraftstoff") #ENUM
	ausgIntervalle[9] = _addonSettings_.getSetting("Getriebeart") #ENUM
	
	if ausgIntervalle[8] == "2":
		strBeschreibung[3] = "Dieselpartikelfilter" #so kann ich strBeschreibung manipulieren, aber gestern stand das gleiche da?!?
	else:
		strBeschreibung[3] = "Zündkerzen"
	
	if ausgIntervalle[9] == "1":
		strBeschreibung[5] = "Getriebeservice" #so kann ich strBeschreibung manipulieren, aber gestern stand das gleiche da?!?
	else:
		strBeschreibung[5] = "Luftfilter"
		
			
#Faelligkeit wird berechnet und entsprechendem Status zugeordnet sowie das Datum kontrolliert
def faelligkeitAusfuehren():
	X=0 #Zaehlvariablen auslagern
	U=0
	
	while X < 8: #Er zaehlt ab 1 nicht ab 0, WTF
		aktFaelligkeit[X] = (int(resKmWert[X]) + int(ausgIntervalle[X])) - aktKilometer
		#fuer die ersten 8 Werte
		if aktFaelligkeit[X] < 1000: #Bei faelligkeit in 5000 wird das gelbe warnicon schon angezeigt auf 1000 heruntergesetzt
			if aktFaelligkeit[X] <= 0:
				aktStatus[X] = 2
			else:
				aktStatus[X] = 1
		else:
			aktStatus[X] = 0
		X=X+1
	U=X+1
	
	#wenn faelligkeit in einem monat ansteht -> Gelbes icon 
	while X < 13 and X >= 8 : #fuer jahr und monat ab 8 bis 13 in der liste
		if int(resKmWert[X]) <= JahrMonat.year: 
			if int(resKmWert[X]) == JahrMonat.year and int(resKmWert[U]) == JahrMonat.month-1:
				aktStatus[X] = 2 #rot
				aktStatus[U] = 2 #rot
			else:
				if JahrMonat.month-1 - int(resKmWert[U]) == -1 and int(resKmWert[X]) == JahrMonat.year:
					aktStatus[X] = 1 #gelb
					aktStatus[U] = 1
				else:
					if int(resKmWert[X]) < JahrMonat.year or int(resKmWert[U]) < JahrMonat.month-1:
						aktStatus[X] = 2
						aktStatus[U] = 2
		else:
			aktStatus[X] = 0 
			aktStatus[U] = 0
		X=X+2
		U=X+1
		
		
#benachrichtung bei faelligkeit	
def ServiceCheckDialog():
	#warnung bei faelligkeit eines wertes mit gelben oder roten icon
	T=0
	ZY=0 
	while T < 8:
		if aktStatus[T] == 2:
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[T], lineFaellig, time, iconServiceRot))
		T=T+1
	
	if aktStatus[8]  == 2:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[8], lineFaellig, time, iconServiceRot))
	if aktStatus[10] == 2:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[9], lineFaellig, time, iconServiceRot))
	if aktStatus[12] == 2:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[10], lineFaellig, time, iconServiceRot))
	
	
	while ZY < 8:
		if aktStatus[ZY] == 1:
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[ZY], lineFaellig, time, iconServiceGelb))
		ZY=ZY+1
	
	if aktStatus[8]  == 1:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[8], lineFaellig, time, iconServiceGelb))
	if aktStatus[10] == 1:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[9], lineFaellig, time, iconServiceGelb))
	if aktStatus[12] == 1:
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(strBeschreibung[10], lineFaellig, time, iconServiceGelb))
	
		
#-------------------------Variablen & Spezialvariablen----------------------#
author 			= 'Steven'
addon       	= xbmcaddon.Addon()
ADDON_ID 		= addon.getAddonInfo('id')
addonname 		= addon.getAddonInfo('name')
_addonSettings_	= xbmcaddon.Addon(id="script.bmwdsa") #ADDON_ID geht auch

ADDON_PATH 		= addon.getAddonInfo('path')
ADDON_USERPATH 	= os.path.join(xbmc.translatePath('special://userdata'), 'addon_data', ADDON_ID)
JahrMonat		= datetime.now()

FILE_RESET = os.path.join(ADDON_USERPATH, 'resetPointDSA.log') 		#ok
FILE_INTERVALLE = os.path.join(ADDON_USERPATH, 'intervalleDSA.log') #ok

#Notifikationen, standard texte fuer ServiceCheckDialog
lineFaellig = "Bitte Ihren BMW-Service überprüfen." 
lineZurueck = "Service wurde zurückgesetzt!"
lineyesno = "Möchten Sie diesen Wert wirklich zurückstellen?"

time = 5000 #ms fuer die dialogboxen

#Icons beim Start, Notifikation, ServiceCheckDialog
iconServiceGelb	= os.path.join(ADDON_PATH,'resources', 'skins', 'Default','media','gelb.png')
iconServiceRot	= os.path.join(ADDON_PATH,'resources', 'skins', 'Default','media','rot.png')

#Icons bei onClick
#iconKonfig 		= 'konfig.png'
iconInsp 		= 'inspektion.png'
iconInsp2		= 'inspektion2.png' #<-------Autom. aus dem Mediaverzeichnis in /resources/skins/Default/media wenn in WindowXML aufgerufen
iconOil 		= 'oil.png'
iconZK	 		= 'zk.png'
iconMF 			= 'microfilter.png'
iconLF 			= 'filter.png'
iconBV 			= 'bremsenva.png'
iconBH 			= 'bremsenha.png'
iconBF 			= 'bremsfluessigkeit.png'
iconHU 			= 'hu.png'
iconAU 			= 'au.png'

#Aus dem Kombi holen, send_tcp_command gibt: "return answer" Testzwecke:136000
aktKilometer 	= get_odometer()

#strBeschreibung ist alleinstehend und scheinbar nur für ServiceCheckDialog relevant Array lässt sich auch nicht manipulieren.
strBeschreibung	= ["Inspektion I","Inspektion II","Ölservice", "Zündkerzen/Dieselpartikelfilter","Microfilter", "Luftfilter/Getriebeservice","Bremsen vorne","Bremsen hinten","Bremsfluessigkeit","Hauptuntersuchung", "Abgasuntersuchung", "RIPSara13-7-89to14-8-14"]
resKmWert 		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #Kilometerstand bei dem Resettet wurde!
#kmIntervalle	= [25000, 50000, 25000, 80000, 60000, 25000, 30000, 30000]	
ausgIntervalle	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 							#intervalle aus der logfile
aktFaelligkeit 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 			#Faelligkeit in Kilometern
aktStatus		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #0=OK=Gruen, 1=bald=Gelb, 2=faellig=Rot Status

#----------------------MAIN---------------------#

def main(): 
	if not xbmcvfs.exists(ADDON_USERPATH):
		xbmcvfs.mkdir(ADDON_USERPATH)
		
	readFile()
	faelligkeitAusfuehren() 
	ServiceCheckDialog()
	

	
	
if __name__ == '__main__':
	main() #ok