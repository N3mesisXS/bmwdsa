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
			_addonSettings_.setSetting(id="Bremsfluessigkeit_Jahr", value=str(resetJahr)) 	
			_addonSettings_.setSetting(id="Bremsfluessigkeit_Monat", value=str(resetMonat)) 
		#Achtung: 0,1,2,3,4,5,6,7,8,9,10,11 = 12,11,10,9,8,7,6,5,4,3,2,1 in der *.xml
		
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
#iconKonfig 		= 'konfig.png' #wahrscheinlich nicht notwendig
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
ausgIntervalle	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #intervalle aus der logfile
aktFaelligkeit 	= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #Faelligkeit in Kilometern
aktStatus		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #0=OK=Gruen, 1=bald=Gelb, 2=faellig=Rot Status

#----------------------MAIN---------------------#

def main(): 
	if not xbmcvfs.exists(ADDON_USERPATH):
		xbmcvfs.mkdir(ADDON_USERPATH)
	
	readFile()
	faelligkeitAusfuehren() 
	ServiceCheckDialog()
	
class FensterXML(xbmcgui.WindowXML):
	#bttn codes
	HOCH_TASTE 		= 3
	RUNTER_TASTE 	= 4

	
	def onInit(self):
		#Deklarierung der großen Symbole links im Bild und in den Notifikationen
		self.KonfigIcon = self.getControl(202)
		self.KonfigIcon.setVisible(False)
		
		self.InspektionIcon = self.getControl(100)
		self.InspektionIcon.setVisible(True)
		
		self.InspektionIIIcon = self.getControl(101)
		self.InspektionIIIcon.setVisible(False)
		
		self.OelserviceIcon = self.getControl(102)
		self.OelserviceIcon.setVisible(False)
		
		self.ZuendkerzenIcon = self.getControl(103)
		self.ZuendkerzenIcon.setVisible(False)
		
		self.MicrofilterIcon = self.getControl(104)
		self.MicrofilterIcon.setVisible(False)
		
		self.LuftfilterIcon = self.getControl(105)
		self.LuftfilterIcon.setVisible(False)
		
		self.BremseVAIcon = self.getControl(106)
		self.BremseVAIcon.setVisible(False)
		
		self.BremseHAIcon = self.getControl(107)
		self.BremseHAIcon.setVisible(False)
		
		self.BremsfluessigkeitIcon = self.getControl(108)
		self.BremsfluessigkeitIcon.setVisible(False)
		
		self.HUIcon = self.getControl(109)
		self.HUIcon.setVisible(False)
		
		self.AUIcon = self.getControl(110)
		self.AUIcon.setVisible(False)
		
		#-------
		#deklarierung der blauen zeiger vom icon zum label
		#Für Konfig auch?
		
		self.drtZK = self.getControl(180)
		self.drtZK.setVisible(False)
		
		self.drtMF = self.getControl(181)
		self.drtMF.setVisible(False)
		
		self.drtLF = self.getControl(182)
		self.drtLF.setVisible(False)
		
		self.drtBV = self.getControl(183)
		self.drtBV.setVisible(False)
		
		self.drtIn1 = self.getControl(184)
		self.drtIn1.setVisible(True)
		
		self.drtIn2 = self.getControl(185)
		self.drtIn2.setVisible(False)
		
		self.drtOil = self.getControl(186)
		self.drtOil.setVisible(False)
		
		self.drtBH = self.getControl(187)
		self.drtBH.setVisible(False)
		
		self.drtBF = self.getControl(188)
		self.drtBF.setVisible(False)
		
		self.drtHU = self.getControl(189)
		self.drtHU.setVisible(False)
		
		self.drtAU = self.getControl(190)
		self.drtAU.setVisible(False)
		
		#-------
		#deklarierung der rot, gelb und gruenen symbole in der GUI
		self.InspektionIGruen = self.getControl(133)
		self.InspektionIGruen.setVisible(False)
		
		self.InspektionIGelb = self.getControl(144)
		self.InspektionIGelb.setVisible(False)
		
		self.InspektionIRot = self.getControl(145)
		self.InspektionIRot.setVisible(False)
		
		if aktStatus[0] == 0:
			self.InspektionIGruen.setVisible(True)
		else:
			self.InspektionIGruen.setVisible(False)
		
		if aktStatus[0] == 1:
			self.InspektionIGelb.setVisible(True)
		else:
			self.InspektionIGelb.setVisible(False)
		
		if aktStatus[0] == 2:
			self.InspektionIRot.setVisible(True)
		else:
			self.InspektionIRot.setVisible(False)
			
		self.InspektionIIGruen = self.getControl(134)
		self.InspektionIIGruen.setVisible(False)
		
		self.InspektionIIGelb = self.getControl(146)
		self.InspektionIIGelb.setVisible(False)
		
		self.InspektionIIRot = self.getControl(147)
		self.InspektionIIRot.setVisible(False)
		
		if aktStatus[1] == 0:
			self.InspektionIIGruen.setVisible(True)
		else:
			self.InspektionIIGruen.setVisible(False)
		
		if aktStatus[1] == 1:
			self.InspektionIIGelb.setVisible(True)
		else:
			self.InspektionIIGelb.setVisible(False)
		
		if aktStatus[1] == 2:
			self.InspektionIIRot.setVisible(True)
		else:
			self.InspektionIIRot.setVisible(False)
		
		self.OelGruen = self.getControl(135)
		self.OelGruen.setVisible(False)
		
		self.OelGelb = self.getControl(148)
		self.OelGelb.setVisible(False)
		
		self.OelRot = self.getControl(149)
		self.OelRot.setVisible(False)
		
		if aktStatus[2] == 0:
			self.OelGruen.setVisible(True)
		else:
			self.OelGruen.setVisible(False)
		
		if aktStatus[2] == 1:
			self.OelGelb.setVisible(True)
		else:
			self.OelGelb.setVisible(False)
		
		if aktStatus[2] == 2:
			self.OelRot.setVisible(True)
		else:
			self.OelRot.setVisible(False)
			
		self.KerGruen = self.getControl(136)
		self.KerGruen.setVisible(False)
		
		self.KerGelb = self.getControl(150)
		self.KerGelb.setVisible(False)
		
		self.KerRot = self.getControl(151)
		self.KerRot.setVisible(False)
		
		if aktStatus[3] == 0:
			self.KerGruen.setVisible(True)
		else:
			self.KerGruen.setVisible(False)
		
		if aktStatus[3] == 1:
			self.KerGelb.setVisible(True)
		else:
			self.KerGelb.setVisible(False)
		
		if aktStatus[3] == 2:
			self.KerRot.setVisible(True)
		else:
			self.KerRot.setVisible(False)
		
		self.MFGruen = self.getControl(137)
		self.MFGruen.setVisible(False)
		
		self.MFGelb = self.getControl(152)
		self.MFGelb.setVisible(False)
		
		self.MFRot = self.getControl(153)
		self.MFRot.setVisible(False)
		
		if aktStatus[4] == 0:
			self.MFGruen.setVisible(True)
		else:
			self.MFGruen.setVisible(False)
		
		if aktStatus[4] == 1:
			self.MFGelb.setVisible(True)
		else:
			self.MFGelb.setVisible(False)
		
		if aktStatus[4] == 2:
			self.MFRot.setVisible(True)
		else:
			self.MFRot.setVisible(False)
			
		self.LFGruen = self.getControl(138)
		self.LFGruen.setVisible(False)
		
		self.LFGelb = self.getControl(154)
		self.LFGelb.setVisible(False)
		
		self.LFRot = self.getControl(155)
		self.LFRot.setVisible(False)
		
		if aktStatus[5] == 0:
			self.LFGruen.setVisible(True)
		else:
			self.LFGruen.setVisible(False)
		
		if aktStatus[5] == 1:
			self.LFGelb.setVisible(True)
		else:
			self.LFGelb.setVisible(False)
		
		if aktStatus[5] == 2:
			self.LFRot.setVisible(True)
		else:
			self.LFRot.setVisible(False)
			
		self.BVGruen = self.getControl(139)
		self.BVGruen.setVisible(False)
		
		self.BVGelb = self.getControl(156)
		self.BVGelb.setVisible(False)
		
		self.BVRot = self.getControl(157)
		self.BVRot.setVisible(False)
		
		if aktStatus[6] == 0:
			self.BVGruen.setVisible(True)
		else:
			self.BVGruen.setVisible(False)
		
		if aktStatus[6] == 1:
			self.BVGelb.setVisible(True)
		else:
			self.BVGelb.setVisible(False)
		
		if aktStatus[6] == 2:
			self.BVRot.setVisible(True)
		else:
			self.BVRot.setVisible(False)
			
		self.BHGruen = self.getControl(140)
		self.BHGruen.setVisible(False)
		
		self.BHGelb = self.getControl(158)
		self.BHGelb.setVisible(False)
		
		self.BHRot = self.getControl(159)
		self.BHRot.setVisible(False)
		
		if aktStatus[7] == 0:
			self.BHGruen.setVisible(True)
		else:
			self.BHGruen.setVisible(False)
		
		if aktStatus[7] == 1:
			self.BHGelb.setVisible(True)
		else:
			self.BHGelb.setVisible(False)
		
		if aktStatus[7] == 2:
			self.BHRot.setVisible(True)
		else:
			self.BHRot.setVisible(False)
			
		self.BFGruen = self.getControl(141)
		self.BFGruen.setVisible(False)
		
		self.BFGelb = self.getControl(160)
		self.BFGelb.setVisible(False)
		
		self.BFRot = self.getControl(161)
		self.BFRot.setVisible(False)
		
		if aktStatus[8] == 0:
			self.BFGruen.setVisible(True)
		else:
			self.BFGruen.setVisible(False)
		
		if aktStatus[8] == 1:
			self.BFGelb.setVisible(True)
		else:
			self.BFGelb.setVisible(False)
		
		if aktStatus[8] == 2:
			self.BFRot.setVisible(True)
		else:
			self.BFRot.setVisible(False)
			
		self.HUGruen = self.getControl(142)
		self.HUGruen.setVisible(False)
		
		self.HUGelb = self.getControl(162)
		self.HUGelb.setVisible(False)
		
		self.HURot = self.getControl(163)
		self.HURot.setVisible(False)
		
		if aktStatus[10] == 0:
			self.HUGruen.setVisible(True)
		else:
			self.HUGruen.setVisible(False)
		
		if aktStatus[10] == 1:
			self.HUGelb.setVisible(True)
		else:
			self.HUGelb.setVisible(False)
		
		if aktStatus[10] == 2:
			self.HURot.setVisible(True)
		else:
			self.HURot.setVisible(False)
			
		self.AUGruen = self.getControl(143)
		self.AUGruen.setVisible(False)
		
		self.AUGelb = self.getControl(164)
		self.AUGelb.setVisible(False)
		
		self.AURot = self.getControl(165)
		self.AURot.setVisible(False)
		
		if aktStatus[12] == 0:
			self.AUGruen.setVisible(True)
		else:
			self.AUGruen.setVisible(False)
		
		if aktStatus[12] == 1:
			self.AUGelb.setVisible(True)
		else:
			self.AUGelb.setVisible(False)
		
		if aktStatus[12] == 2:
			self.AURot.setVisible(True)
		else:
			self.AURot.setVisible(False)
		#------------------------------
		
		
		#label rechts außen
		self.MAIN = self.getControl(200)
		self.MAIN.setLabel("Service")
		
		self.Konfig = self.getControl(201)
		self.Konfig.setLabel("Konfiguration")
		
		self.Inspektion1 = self.getControl(122)
		self.Inspektion1.setLabel(str(aktFaelligkeit[0])+" km")
		
		self.Inspektion2 = self.getControl(123)
		self.Inspektion2.setLabel(str(aktFaelligkeit[1])+" km")
		
		self.Oelservice = self.getControl(124)
		self.Oelservice.setLabel(str(aktFaelligkeit[2])+" km")
		
		self.Zuendkerzen = self.getControl(125)
		self.Zuendkerzen.setLabel(str(aktFaelligkeit[3])+" km")
		
		self.Microfilter = self.getControl(126)
		self.Microfilter.setLabel(str(aktFaelligkeit[4])+" km")
		
		self.Luftfilter = self.getControl(127)
		self.Luftfilter.setLabel(str(aktFaelligkeit[5])+" km")
		
		self.BremsenVA = self.getControl(128)
		self.BremsenVA.setLabel(str(aktFaelligkeit[6])+" km")
		
		self.BremsenHA = self.getControl(129)
		self.BremsenHA.setLabel(str(aktFaelligkeit[7])+" km")
		
		self.Bremsfluessigkeit = self.getControl(130)
		self.Bremsfluessigkeit.setLabel(str(resKmWert[9])+" / "+str(resKmWert[8]))
		
		self.HU = self.getControl(131)
		self.HU.setLabel(str(resKmWert[11])+" / "+str(resKmWert[10]))
		
		self.AU = self.getControl(132)
		self.AU.setLabel(str(resKmWert[13])+" / "+str(resKmWert[12]))

		#Buttons Navigation, label links/mittig
		self.BtnKonfig		= self.getControl(201)
		self.BtnInspektion1 = self.getControl(111)
		self.BtnInspektion2 = self.getControl(112)
		self.BtnOil 		= self.getControl(113)
		self.BtnZK 			= self.getControl(114)
		self.BtnMF 			= self.getControl(115)
		self.BtnLF	 		= self.getControl(116)		
		self.BtnBV 			= self.getControl(117)
		self.BtnBH 			= self.getControl(118)
		self.BtnBF 			= self.getControl(119)
		self.BtnHU 			= self.getControl(120)
		self.BtnAU 			= self.getControl(121)
		
		#Navigation
		self.BtnKonfig.setNavigation(self.BtnInspektion1,self.BtnInspektion1,self.BtnInspektion1,self.BtnInspektion1)
		self.BtnInspektion1.setNavigation(self.BtnAU,self.BtnInspektion2,self.BtnKonfig,self.BtnInspektion1)
		self.BtnInspektion2.setNavigation(self.BtnInspektion1,self.BtnOil,self.BtnKonfig,self.BtnInspektion2)
		self.BtnOil.setNavigation(self.BtnInspektion2,self.BtnZK,self.BtnKonfig,self.BtnOil)
		self.BtnZK.setNavigation(self.BtnOil,self.BtnMF,self.BtnKonfig,self.BtnZK)
		self.BtnMF.setNavigation(self.BtnZK,self.BtnLF,self.BtnKonfig,self.BtnMF)
		self.BtnLF.setNavigation(self.BtnMF,self.BtnBV,self.BtnKonfig,self.BtnLF)
		self.BtnBV.setNavigation(self.BtnLF,self.BtnBH,self.BtnKonfig,self.BtnBV)
		self.BtnBH.setNavigation(self.BtnBV,self.BtnBF,self.BtnKonfig,self.BtnBH)
		self.BtnBF.setNavigation(self.BtnBH,self.BtnHU,self.BtnKonfig,self.BtnBF)
		self.BtnHU.setNavigation(self.BtnBF,self.BtnAU,self.BtnKonfig,self.BtnHU)
		self.BtnAU.setNavigation(self.BtnHU,self.BtnInspektion1,self.BtnKonfig,self.BtnAU)
		
		if ausgIntervalle[8] == "2": #Wenn Diesel wird Zuendkerzen mit DPF ersetzte
			self.BtnZK.setLabel("Dieselpartikelfilter") #LOGO ändern
			
		if ausgIntervalle[9] == "1": #Wenn Getriebeservice gewuenscht dann wird Luftfilter ersetzt
			self.BtnLF.setLabel("Getriebeservice") #LOGO ändern
		
	def onClick(self, controlID):
		if (controlID == 201): #Konfigurations Buttons
			ok = xbmcaddon.Addon().openSettings()
			self.close()
			
	
		if (controlID == 111): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(0) 	#resetfunktion ausfuehren
				faelligkeitAusfuehren()			#faelligkeit neu berechnen
				self.Inspektion1.setLabel(str(aktFaelligkeit[0])+" km") #label setzen
				self.InspektionIGelb.setVisible(False)
				self.InspektionIRot.setVisible(False)
				self.InspektionIGruen.setVisible(True) #Gruenes icon anzeigen und Rot und Gelb unsichtbar machen
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp))
			
			
		if (controlID == 112): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(1)
				faelligkeitAusfuehren()
				self.Inspektion2.setLabel(str(aktFaelligkeit[1])+" km")
				self.InspektionIIGelb.setVisible(False)
				self.InspektionIIRot.setVisible(False)
				self.InspektionIIGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp2))
			
		if (controlID == 113): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(2)
				faelligkeitAusfuehren()
				self.Oelservice.setLabel(str(aktFaelligkeit[2])+" km")
				self.OelGelb.setVisible(False)
				self.OelRot.setVisible(False)
				self.OelGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconOil))
			
		if (controlID == 114): #BUTTONID #RESETFUNKTION
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(3)
					
				faelligkeitAusfuehren()
				self.Zuendkerzen.setLabel(str(aktFaelligkeit[3])+" km")
				self.KerGelb.setVisible(False)
				self.KerRot.setVisible(False)
				self.KerGruen.setVisible(True)
			
				if ausgIntervalle[8] == "2": #Wenn Diesel wird Zuendkerzen mit DPF ersetzt
					xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp))
				else:
					xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconZK))
			
		if (controlID == 115): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(4)
				faelligkeitAusfuehren()
				self.Microfilter.setLabel(str(aktFaelligkeit[4])+" km")
				self.MFGelb.setVisible(False)
				self.MFRot.setVisible(False)
				self.MFGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconMF))
			
		if (controlID == 116): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(5)
					
				faelligkeitAusfuehren()
				self.Luftfilter.setLabel(str(aktFaelligkeit[5])+" km")
				self.LFGelb.setVisible(False)
				self.LFRot.setVisible(False)
				self.LFGruen.setVisible(True)
			
				if ausgIntervalle[9] == "1": #Getriebe
					xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp))
				else:
					xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconLF))
			
		if (controlID == 117): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(6)
				faelligkeitAusfuehren()
				self.BremsenVA.setLabel(str(aktFaelligkeit[6])+" km")
				self.BVGelb.setVisible(False)
				self.BVRot.setVisible(False)
				self.BVGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconBV))
			
		if (controlID == 118): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(7)
				faelligkeitAusfuehren()
				self.BremsenHA.setLabel(str(aktFaelligkeit[7])+" km")
				self.BHGelb.setVisible(False)
				self.BHRot.setVisible(False)
				self.BHGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconBH))
			
		if (controlID == 119): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(8)
				faelligkeitAusfuehren()
				self.Bremsfluessigkeit.setLabel(str(resKmWert[9])+" / "+str(resKmWert[8]))
				self.BFGelb.setVisible(False)
				self.BFRot.setVisible(False)
				self.BFGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconBF))
			
		if (controlID == 120): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(10)
				faelligkeitAusfuehren()
				self.HU.setLabel(str(resKmWert[11])+" / "+str(resKmWert[10]))
				self.HUGelb.setVisible(False)
				self.HURot.setVisible(False)
				self.HUGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconHU))
			
		if (controlID == 121): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(12)
				faelligkeitAusfuehren()
				self.AU.setLabel(str(resKmWert[13])+" / "+str(resKmWert[12]))
				self.AUGelb.setVisible(False)
				self.AURot.setVisible(False)
				self.AUGruen.setVisible(True)
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconAU))
	#focus schmeisst Exception raus, keine Ahnung was er hat, schein wohl ein problem mit der onFocus funktion selber zu sein, funktioniert dennoch
	def onFocus(self, controlID):
		if (controlID == 201):
			self.KonfigIcon.setVisible(True) 
		else:
			self.KonfigIcon.setVisible(False)
	
		if (controlID == 111):
			self.InspektionIcon.setVisible(True) 
			self.drtIn1.setVisible(True)
		else:
			self.InspektionIcon.setVisible(False)
			self.drtIn1.setVisible(False)
			
		if (controlID == 112):
			self.InspektionIIIcon.setVisible(True)
			self.drtIn2.setVisible(True)
		else:
			self.InspektionIIIcon.setVisible(False)
			self.drtIn2.setVisible(False)
			
		if (controlID == 113):
			self.OelserviceIcon.setVisible(True)
			self.drtOil.setVisible(True)
		else:
			self.OelserviceIcon.setVisible(False)
			self.drtOil.setVisible(False)
			
		if (controlID == 114):
			if ausgIntervalle[8] == "2":
				self.InspektionIcon.setVisible(True)
			else:
				self.ZuendkerzenIcon.setVisible(True)
				
			self.drtZK.setVisible(True)
		else:
			self.ZuendkerzenIcon.setVisible(False)
			self.drtZK.setVisible(False)
			
		if (controlID == 115):
			self.MicrofilterIcon.setVisible(True)
			self.drtMF.setVisible(True)
		else:
			self.MicrofilterIcon.setVisible(False)
			self.drtMF.setVisible(False)
			
		if (controlID == 116):
			if ausgIntervalle[9] == "1":
				self.InspektionIcon.setVisible(True)
			else:
				self.LuftfilterIcon.setVisible(True)
				
			self.drtLF.setVisible(True)
		else:
			self.LuftfilterIcon.setVisible(False)
			self.drtLF.setVisible(False)
			
		if (controlID == 117):
			self.BremseVAIcon.setVisible(True)
			self.drtBV.setVisible(True)
		else:
			self.BremseVAIcon.setVisible(False)
			self.drtBV.setVisible(False)
			
		if (controlID == 118):
			self.BremseHAIcon.setVisible(True)
			self.drtBH.setVisible(True)
		else:
			self.BremseHAIcon.setVisible(False)
			self.drtBH.setVisible(False)
			
		if (controlID == 119):
			self.BremsfluessigkeitIcon.setVisible(True)
			self.drtBF.setVisible(True)
		else:
			self.BremsfluessigkeitIcon.setVisible(False)
			self.drtBF.setVisible(False)
			
		if (controlID == 120):
			self.HUIcon.setVisible(True)
			self.drtHU.setVisible(True)
		else:
			self.HUIcon.setVisible(False)
			self.drtHU.setVisible(False)
			
		if (controlID == 121):
			self.AUIcon.setVisible(True)
			self.drtAU.setVisible(True)
		else:
			self.AUIcon.setVisible(False)
			self.drtAU.setVisible(False)
			
	#def onAction(self, action): #hat keinen nutzen fuer mich			

if __name__ == '__main__':
	main() #ok
	w = FensterXML("skin.xml", ADDON_PATH, 'Default', '720p') #ok
	w.doModal() #ok
	del w #ok