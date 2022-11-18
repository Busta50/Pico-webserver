import network
import socket
from machine import Pin
from time import sleep
import utime
import time
from dht import DHT11

import json

from machine import Pin
import machine

led = machine.Pin("LED", machine.Pin.OUT)

sensorFoto = machine.ADC(26)
sensorTemp = DHT11(Pin(0))

red = Pin(4, Pin.OUT)
green = Pin(3, Pin.OUT)
blue = Pin(2, Pin.OUT)

ssid = 'redmi'
password = 'redmi2022!'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

file = open("index2.html", "r")
html = str(file.read())
response = {}
headers = ""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        sleep(.1)
        color = "Ninguno";
        #Valor numerico de la luz
        luz = sensorFoto.read_u16()
        
        #DHT mide la temperatura/humedad
        #sensorTemp.measure()
    
        #Valor de la temperatura en centigrados
        temperatura =25#sensorTemp.temperature()
        
        #Valor de la humedad
        hum = 14#sensorTemp.humidity()
        
        #print('Temperatura: %3.1f C' %temperatura)
        #print('Humedad: %3.1f %%' %hum)
        print('Luminosidad %3.1f\n' %luz)
        if luz < 12000: #and temp < 70:++++++
            blue.value(0)
            red.value(1)
            green.value(0)
            color = "Rojo"
            luz = "Es de noche ("+str(luz)+ " lux)"
        elif luz > 30700:
            blue.value(1)
            red.value(0)
            green.value(0)
            color = "Azul"
            luz = "Es de día ("+str(luz)+ " lux)"
        else:
            blue.value(0)
            red.value(0)
            green.value(1)
            color = "Verde"
            luz = "Es de día ("+str(luz)+ " lux)"
        print('client connected from', addr)
        request = cl.recv(1024)
        #print(request)

        request = str(request)
        sensors = request.find('/get/sensors')
        page = request.find('/home')
        lightOn = request.find('/light/off')
        lightOff = request.find('/light/on')
        stateis = "LED is AA"

        if sensors == 6:
            print("Sensors request recieved. ")
         
            response ={
                "temperatura":str(temperatura),
                "luz":str(luz),
                "color":str(color)
                }
            response = json.dumps(response)
            headers = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n'
        if page == 6:
            print("Page request recieved. ")
           
            response =html
            headers =  'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
        if(lightOn ==6):
            led.on()
            response ={
                "response":"OK"
                
                }
            response = json.dumps(response)
            headers = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n'
        if(lightOff ==6):
            led.off()
            response ={
                "response":"OK"
                
                }
            response = json.dumps(response)
            headers = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n'

            
        
        cl.send(response)
        cl.close()
        time.sleep(1)
     
    except OSError as e:
        cl.close()
        print('connection closed')