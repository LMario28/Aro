# NOTAS:

# 1) Las posiciones de los LEDs son:
#    Circunferencia: 1-180 (0-179)
#    Linea izquierda: 184-237 (183-236)
#    Linea izquierda: 238-291 (237-290)

# 2) Pasos para actualizar el sketch en el ESP32

#    Requisitos: 1) Debe estar en donde está la aplicación el sketch ota.py;
#                2) En GitHub, repositorio Aro debe existir  un arhivo con nombre version.json con las lineas:
#                   {
#                     "version":2
#                   }
#                   el número de la versión debe ser mayor que el mismo archivo en el ESP32

#    a) Abrir www.github.com
#    b) lmmsegura@hotmail.com / le...24
#    c) Copiar la nueva versión del sketch a GitHub, repositorio Aro

import machine
from machine import Pin
import neopixel
import time

import network
from ota_lmms import OTAUpdater

from machine import WDT

#///////////////////////////////////////////////////////////////////////////////
#/                               CONSTANTES                                   //
#///////////////////////////////////////////////////////////////////////////////
WIFI_SSID = ['INFINITUM2426_2.4','Electronica Hotspot PC','TP-Link_lmmsegura']
WIFI_PASS = ['CNnC917MDE','electronica23','lmario28']
SSID=''
PASSWD=''
BLYNK_AUTH = 'apvVB1KTve_HC0uEb8ltb7tME6GhWIBs'

NUMERO_LEDs_RELOJ=284
NUMERO_LEDS_SOLO_ARO=180                                                       # 6. Navidad 1, 7. Navidad 2
NUMERO_LEDs_PANTALLA=576                                                       # Filas: 24, Columnas: 24
PERIODO_FLASH_LED=1000

# 16,15,15,15,15,15,15,15,15,15,15,17 LEDs
#define NUMERO_INTENTOS 5

#define MAXIMUN_RETRIES_TO_CONNECT_BLYNK 20                                    //
#define MAXIMUN_ATTEMPTS_TO_RECONNECT_WIFI 18                                  // Intentos maximos para conectarse a la red WiFi
#define TIEMPO_ESPERA_RECONECTAR_BLYNK 30000L                                  // Tiempo de espera par intentar reconectare a Blynk (milliseconds)

ZONA_MEXICO=-6                                                                 # 6. Navidad 1, 7. Navidad 2
WATCHDOG=False

#///////////////////////////////////////////////////////////////////////////////
#/                               OBJETOS                                    //
#///////////////////////////////////////////////////////////////////////////////
pixels = neopixel.NeoPixel(Pin(16, Pin.OUT), NUMERO_LEDs_RELOJ)
pixelPantalla = neopixel.NeoPixel(Pin(17, Pin.OUT), NUMERO_LEDs_PANTALLA)
if (WATCHDOG):
  wdt = WDT(timeout = 30000)

#///////////////////////////////////////////////////////////////////////////////
#/                               VARIABLES                                    //
#///////////////////////////////////////////////////////////////////////////////
tiempoLocal=''
banderaSalida=False
redActiva=0
fechaHoraInicio=''
ahorita=''
diaInicial=''
#timerReloj=''
banderaHoraRecuperadaBlynk=False
opcionSeleccionadaAzar=0
i=1
j=1
k=0
incrementoDecremento=1
contadorAnimaciones=0

#///////////////////////////////////////////////////////////////////////////////
#/                               FUNCIONES                                    //
#///////////////////////////////////////////////////////////////////////////////
#-------------------------------------------------------------------------------
def seleccionarMejorRedWiFiDisponible():
#-------------------------------------------------------------------------------

  global SSID
  global PASSWD
  global redActiva

  wiFi = network.WLAN(network.STA_IF)
  wiFi.active(True)

  authmodes = ['Open', 'WEP', 'WPA-PSK' 'WPA2-PSK4', 'WPA/WPA2-PSK']
  redesWiFiDisponibles = wiFi.scan()
#   for (ssid, bssid, channel, RSSI, authmode, hidden) in redesWiFiDisponibles:
#     print("* {:s}".format(ssid))
#     print("   - Auth: {} {}".format(authmodes[authmode], '(hidden)' if hidden else ''))
#     print("   - Channel: {}".format(channel))
#     print("   - RSSI: {}".format(RSSI))
#     print("   - BSSID: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid))
#     print()

  rssiMasFuerte = 999
  for redWiFi in redesWiFiDisponibles:
    #print ("> " + str(redWiFi[0],"utf-8"))
    #print ("> " + str(redWiFi[3]))
    ssid = str(redWiFi[0],"utf-8")
    try:
      indiceRed = WIFI_SSID.index(ssid)
    except ValueError:
      continue

    SSID = ssid
    PASSWD = WIFI_PASS[indiceRed]
    redActiva = indiceRed + 1
      
    if rssiMasFuerte!=999:
      rssi = str(redWiFi[3])
      if rssi<rssiMasFuerte:
        rssiMasFuerte = rssi
    print("Mejor red disponible:",redActiva,"|",SSID,"|",PASSWD)

#-------------------------------------------------------------------------------
def actualizarSketch():
#-------------------------------------------------------------------------------
  global SSID
  global PASSWD

  firmware_url = "https://raw.githubusercontent.com/LMario28/AroITSTA/"

  print("*************************")
  print("ACTUALIZANDO SKETCH...")
  try:
    ota_updater = OTAUpdater(SSID, PASSWD, firmware_url, "ProbarConexiones_OTA.py")
    ota_updater.download_and_install_update_if_available()
  except:
    print("NO SE PUDO ACTUALIZAR EL SKETCH")
  print("*************************")

#///////////////////////////////////////////////////////////////////////////////
#/ PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO        //
#///////////////////////////////////////////////////////////////////////////////
#seleccionarMejorRedWiFiDisponible()

#HOLA
for i in range(2):
  pixels.fill((0,10,0))
  pixels.write()
  time.sleep_ms(250)
  pixels.fill((0,0,0))
  pixels.write()
  time.sleep_ms(250)

seleccionarMejorRedWiFiDisponible()
print("Connecting to WiFi network '{}'".format(SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID,PASSWD)
while not wifi.isconnected():
  time.sleep(5)
  if (WATCHDOG):
    wdt.feed()
  print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])
actualizarSketch()

pixels.fill((255,0,0))
pixels.write()

wifi.disconnect()

#ADIOS
for i in range(2):
  pixels.fill((0,10,0))
  pixels.write()
  time.sleep_ms(250)
  pixels.fill((0,0,0))
  pixels.write()
  time.sleep_ms(250)

print("Programa terminado")
