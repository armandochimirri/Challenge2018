import sys
import queue
import spesa
from locale import *

import gbl
import lightHandler
import re
from aiy.leds import Leds, Color


# Ho due code: una di lettura, stringhe di testo da google home a utente e una di scrittura, stringhe di testo da utente a google home

def process_text(qRead):
    qWrite = gbl.q_speak
    while True:
        lightHandler.setcolor(Color.RED)
        text = qRead.get(True)
        if text is None:
            continue
        lightHandler.setcolor(Color.BLUE)
        print(text)
        if (
        re.match("(^dimmi le mie notifiche($| ).*)|(.* dimmi le mie notifiche .*)|(.* dimmi le mie notifiche$)", text)):
            # print("Hai detto: %s" % text)
            print("ottimo")

        # Mi gestisco gli oggetti comprati
        elif (re.match("(^ho comprato($| ).*)|(.* ho comprato .*)|(.* ho comprato$)", text)):
            print("Hai detto: %s" % text)

            groups = re.match("(ho comprato(?: (?:([a-zA-Z]+)|(\d+))(?: ([a-zA-Z]+)(?: (?:(?:a)|(?:per)) €(\d+))?)?)?)",
                              text)
            print("group1 %s" % groups.group(2))
            print("group2 %s" % groups.group(3))
            print("group3 %s" % groups.group(4))
            print("group4 %s" % groups.group(5))
            group1=groups.group(2)
            group2=groups.group(3)
            group3=groups.group(4)
            group4=groups.group(5)


            # se group1 è vuoto e anche il group2 è vuoto vuol dire
            # che ho soltanto (ho comprato)
            # chiedo l'oggetto, la quantità e il prezzo

            if(group1 is None and group2 is None):
                #chiedo l'oggetto, la quantità e il prezzo
                item=getItem(qRead,qWrite)
                if item is None:
                    continue
                qnt=getQnt(qRead,qWrite)
                price=getPrice(qRead,qWrite)
                getUser(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price))
                spesa.add_product(item,qnt,price,gbl.username)
                continue


            # group2 è la quantità group3 è l'oggetto, chiedo il prezzo
            # (ho comprato 5 mele)
            if(group1 is None and group4 is None):
                qnt=atoi(group2)
                item=group3
                price=getPrice(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price) )
                continue


            # controllo che group1 appartenga al vettore dei numeri
            # posso avere due cose(ho comprato cinque mele) chiedo solo il prezzo
            # (ho comprato cinque mele a €5)
            if(group1 in numeri):
                qnt=numeri.get(group1)
                item=group3
                # Non ho il prezzo
                price=group4
                if group4 is None:
                    price=getPrice(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price) )
                continue



            # group2 è la quantità, group3 è l'oggetto, group4 è il prezzo
            # (ho comprato 5 mele a/per €3)

            if(not(group1 is None or group2 is None or group3 is None or group4 is None)):
                qnt=atoi(group2)
                item=group3
                price=group4
                price=atof(price.replace(",","."))
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price))
                continue


            # se group1 non è un articolo allora è un oggetto singolo
            # di cui devo chiedere soltanto il prezzo (ho comprato mela)
            # chiedo solo il prezzo

            if(not(group1 in articoli_singolari or group1 in articoli_plurali)):
                qnt=1
                item=group1
                price=getPrice(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price) )
                continue


            # group1 indica un articolo singolare o plurale, group3 indica l'oggetto
            # chiedo la quantità e il prezzo
            # (ho comprato delle mele)
            if(group1 in articoli_singolari):
                qnt=1
                item=group3
                price=getPrice(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price) )
                continue

            elif(group1 in articoli_plurali):
                qnt=atoi(getQnt(qRead,qWrite))
                item=group3
                price=getPrice(qRead,qWrite)
                print("item -> %s qnt -> %d price -> %f" %(item, qnt, price) )
                continue

        elif (re.match("(^togli dalla lista($| ).*)|(.* togli dalla lista .*)|(.* togli dalla lista$)", text)):
            print("Hai detto: %s" % text)
            oggetto = text.replace("togli dalla lista", "").strip()

            # Se non dico nulla richiedo e prendo cosa mi viene detto
            if oggetto is "":
                qWrite.put("Non ho capito, cosa devo cancellare?")
                puliscicoda(qRead)
                oggetto = qRead.get(True)
                if oggetto is None:
                    continue

            # Se dico annulla esco e richiedo
            if (re.match("(^annulla($| ).*)|(.* annulla .*)|(.* annulla$)", oggetto)):
                qWrite.put("Daccordo, riprova.")
                continue

            # Chiedo conferma su cosa e' stato comprato
            qWrite.put("Ochei, quindi devo cancellare %s?" % oggetto)
            puliscicoda(qRead)

            choose = chooses(qRead)

            if (choose == False):
                qWrite.put("Daccordo, riprova.")
                continue

            qWrite.put("Ho cancellato %s dalla lista." % oggetto)

        elif (re.match("(^fai i conti($| ).*)|(.* fai i conti .*)|(.* fai i conti$)", text)):
            print("Hai detto: %s" % text)

        elif (re.match("(^mostra lista($| ).*)|(.* mostra lista .*)|(.* mostra lista$)", text)):
            print("Hai detto: %s" % text)

        elif (re.match("(^ciao($| ).*)|(.* ciao .*)|(.* ciao$)", text)):
            print("Hai detto: %s" % text)


def chooses(qRead):
    choose = None
    while (choose == None):
        obj = qRead.get(True)
        if (re.match("(^sì($| ).*)|(.* sì .*)|(.* sì$)", obj)):
            print("Hai detto: %s" % obj)
            choose = True
        elif (re.match("(^esatto($| ).*)|(.* esatto .*)|(.* esatto$)", obj)):
            print("Hai detto: %s" % obj)
            choose = True
        elif (re.match("(^certo($| ).*)|(.* certo .*)|(.* certo$)", obj)):
            print("Hai detto: %s" % obj)
            choose = True
        elif (re.match("(^no($| ).*)|(.* no .*)|(.* no$)", obj)):
            print("Hai detto: %s" % obj)
            choose = False

    return choose

def getQnt(qRead, qWrite):
    numero=None
    while numero is None:
        qWrite.put("Ochei, qual è la quantità?")
        puliscicoda(qRead)
        qnt = qRead.get(True)
        numero = numeri.get(qnt)
        if numero is None:
            numero=atoi(qnt)
    qWrite.put("Ochei hai inserito la quantità %d" % numero)
    return numero


def getPrice(qRead, qWrite):
    numero = None
    while numero is None:
        qWrite.put("Ochei, qual è il prezzo?")
        puliscicoda(qRead)
        prz = qRead.get(True)
        prz= prz.replace("€", "").replace(",",".")
        numero = numeri.get(prz)
        if numero is None:
            numero = atof(prz)
    qWrite.put("Ochei il prezzo è €%d" % numero)
    return numero

def getItem(qRead, qWrite):
    qWrite.put("Non ho capito, cosa hai comprato?")
    puliscicoda(qRead)
    oggetto = qRead.get(True)

    # Se dico annulla esco e richiedo
    if (re.match("(^annulla($| ).*)|(.* annulla .*)|(.* annulla$)", oggetto)):
        qWrite.put("Daccordo, riprova.")
        return None

    # Chiedo conferma su cosa e' stato comprato
    qWrite.put("Ochei, quindi hai comprato %s?" % oggetto)
    puliscicoda(qRead)

    choose = chooses(qRead)

    if (choose == False):
        qWrite.put("Daccordo, riprova.")
        oggetto = None

    return oggetto

def getUser(qRead, qWrite):
    if gbl.username is "":
        qWrite.put("Chi sei?")
        puliscicoda(qRead)
        name = qRead.get(True)
        gbl.username=name
        qWrite.put("Grazie %s" % name)
        lightHandler.setcolor(Color.GREEN)
    else:
        qWrite.put("Grazie %s" % gbl.username)
        lightHandler.setcolor(Color.GREEN)


numeri = {
    'un': 1,
    'uno': 1,
    'una': 1,
    'due': 2,
    'tre': 3,
    'quattro': 4,
    'cinque': 5,
    'sei': 6,
    'sette': 7,
    'otto': 8,
    'nove': 9,
    'dieci': 10,
    'undici': 11,
    'dodici': 12,
    'tredici': 13
}

articoli_singolari = {
    'il', 'la'
}

articoli_plurali = {
    'delle', 'degli', 'dei', 'le'
}


def puliscicoda(qRead):
    while (not qRead.empty()):
        qRead.get(False)
