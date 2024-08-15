# NOTAS:

# 1) Las posiciones de los LEDs son:
#    Circunferencia: 1-183 (0-182)
#    Linea izquierda: 184-237 (183-236)
#    Linea izquierda: 238-291 (237-290)

# 2) El orden en los datos del tiempo (tupla) es:
#    Año, mes (1-12), día del mes (1-31), hora (0-23), minuto (0-59), segundo (0-59), día de
#    la semana (0-6 de lunes a domingo), día de año (1-366)

# 3) Pasos para actualizarel sketch en el ESP32

#    Requisitos: 1) Debe estar en donde está la aplicación el sketch ota.py;
#                   2) En GitHub, repositorio Aro debe existir  un arhivo con nombre version.json con las lineas:
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

import BlynkLib     # https://github.com/vshymanskyy/blynk-library-python/blob/master/examples/03_sync_virtual.py
from BlynkTimer_lmms import BlynkTimer
import network
from ota_lmms import OTAUpdater
import random

#///////////////////////////////////////////////////////////////////////////////
#/                               CONSTANTES                                   //
#///////////////////////////////////////////////////////////////////////////////
NUMERO_LEDs_TIRA=291
WIFI_SSID = ['INFINITUM2426_2.4','Electronica Hotspot PC','TP-Link_lmmsegura']
WIFI_PASS = ['CNnC917MDE','electronica23','lmario28']
SSID=''
PASSWD=''
BLYNK_AUTH = 'apvVB1KTve_HC0uEb8ltb7tME6GhWIBs'

NUMERO_LEDs_TIRA=291
NUMERO_LEDS_SOLO_ARO=182                                                       # 6. Navidad 1, 7. Navidad 2
PERIODO_FLASH_LED=1000
# 16,15,15,15,15,15,15,15,15,15,15,17 LEDs
POSICION_HORA=[0,   \
               16,  \
               31,  \
               46,  \
               61,  \
               76,  \
               91,  \
               106, \
               121, \
               136, \
               151, \
               166
              ]
POSICION_MINUTO=[0, 4, 7, 10, 13, 16,       \
                 19, 22, 25, 28, 31,        \
                 34, 37, 40, 43, 46,        \
                 49, 52, 55, 58, 61,        \
                 64, 67, 70, 73, 76,        \
                 79, 82, 85, 88, 91,        \
                 94, 97, 100, 103, 106,     \
                 109, 112, 115, 118, 121,   \
                 124, 127, 130, 133, 136,   \
                 139, 142, 145, 148, 151,   \
                 154, 157, 160, 163, 166,   \
                 170, 173, 176, 179         \
                 ]
#define NUMERO_INTENTOS 5

#define MAXIMUN_RETRIES_TO_CONNECT_BLYNK 20                                   //
#define MAXIMUN_ATTEMPTS_TO_RECONNECT_WIFI 18                                 // Intentos maximos para conectarse a la red WiFi
#define TIEMPO_ESPERA_RECONECTAR_BLYNK 30000L                                 // Tiempo de espera par intentar reconectare a Blynk (milliseconds)

ANIMACION=5                                                                    # 1: Flash LED, 2: Todo blanco, 3: Reloj, 4: Bandera, 5. Fiestas patrias,
ZONA_MEXICO=-6                                                                 # 6. Navidad 1, 7. Navidad 2
#///////////////////////////////////////////////////////////////////////////////
#/                               OBJETOS                                    //
#///////////////////////////////////////////////////////////////////////////////
pixels = neopixel.NeoPixel(Pin(16, Pin.OUT), NUMERO_LEDs_TIRA)
from machine import RTC
(year, month, mday, weekday, hour, minute, second, milisecond)=RTC().datetime()                

#///////////////////////////////////////////////////////////////////////////////
#/                               VARIABLES                                    //
#///////////////////////////////////////////////////////////////////////////////
tiempoLocal=''
banderaSalida=False
redActiva=0
fechaHoraInicio=''
ahorita=''
diaInicial=''

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

  firmware_url = "https://raw.githubusercontent.com/LMario28/Aro/"

  ota_updater = OTAUpdater(SSID, PASSWD, firmware_url, "boot.py")
  ota_updater.download_and_install_update_if_available()

#-------------------------------------------------------------------------------
def desplegarMensajeVisual(tipLla):
#-------------------------------------------------------------------------------
  # Conexión a red WLAN fallida (un parpadeo en rojo)
  if(tipLla==1):
    for i in range(1):
      pixels.fill((255,0,0))
      pixels.write()
      time.sleep(0.5)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.5)
  # Conexión a red WLAN exitosa (un parpadeo en verde opaco)
  elif(tipLla==2):
    for i in range(1):
      pixels.fill((0,100,0))
      pixels.write()
      time.sleep(0.5)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.5)
  # Conexión a Blink WLAN exitosa (un parpadeo en verde brillante)
  elif(tipLla==3):
    for i in range(1):
      pixels.fill((0,255,0))
      pixels.write()
      time.sleep(0.5)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.5)
      
#-------------------------------------------------------------------------------
def actualizarHora():
#-------------------------------------------------------------------------------
  global tiempoLocal

  pixels.fill((0,0,0))
  desplegarEsqueleto()
  desplegarHoraHora()
  desplegarHoraMinuto()
  desplegarHoraSegundo()
  pixels.write()

#-------------------------------------------------------------------------------
def desplegarEsqueleto():
#-------------------------------------------------------------------------------
  # MINUTO MINUTO MINUTO
  for i in range(60):
    pixels[POSICION_MINUTO[i]] = (0,2,0)

  # HORA HORA HORA
  pixels[182] = (5,0,5)                                                         # LED 183
  pixels[0] = (5,0,5)
  pixels[1] = (5,0,5)
  for i in range(1,12):
    pixels[POSICION_HORA[i]-1] = (5,0,5)
    pixels[POSICION_HORA[i]] = (5,0,5)
    pixels[POSICION_HORA[i]+1] = (5,0,5)

#-------------------------------------------------------------------------------
def desplegarHoraHora():
#-------------------------------------------------------------------------------
  hora = RTC().datetime()[4]
  if(hora>=12):
    hora -= 12
  ledHoraActual = map(3600 * hora + 60 * RTC().datetime()[5] + RTC().datetime()[6], 0, 43200, 0, NUMERO_LEDS_SOLO_ARO) + 1;
  pixels[ledHoraActual-1] = (255,0,0)
  pixels[ledHoraActual] = (255,0,0)
  pixels[ledHoraActual+1] = (255,0,0)

  pixels[POSICION_HORA[redActiva] + 2] = (1,1,1)

#-------------------------------------------------------------------------------
def map(x, in_min, in_max, out_min, out_max):
#-------------------------------------------------------------------------------
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min;

#-------------------------------------------------------------------------------
def desplegarHoraMinuto():
#-------------------------------------------------------------------------------
  ledMinutoActual = POSICION_MINUTO[RTC().datetime()[5]]
  pixels[ledMinutoActual-1] = (0,255,0)
  pixels[ledMinutoActual] = (0,255,0)

#-------------------------------------------------------------------------------
def desplegarHoraSegundo():
#-------------------------------------------------------------------------------
  ledSegundoActual = POSICION_MINUTO[RTC().datetime()[6]]
  pixels[ledSegundoActual] = (255,255,0)

#-------------------------------------------------------------------------------
def bandera():
#-------------------------------------------------------------------------------
  pixels.fill((0,0,0))

# Semicírculo  izquierdo (VERDE)
  for i in range (104,173):     # [104,172]
    pixels[i] = (0,70,0)

  # Línea vertical izquierda
  for i in range (183,237):     # [183,236]
    pixels[i] = (0,70,0)

  # Semisemicírculo superior izquierdo (BLANCO)
  for i in range (172,183):     # [172,182]
    pixels[i] = (128,128,128)

  # Semisemicírculo superior derecho (BLANCO)
  for i in range (0,11):        # [0,10]
    pixels[i] = (128,128,128)

  # Semicírculo inferior (BLANCO)
  for i in range (79,104):      # [79,103]
    pixels[i] = (128,128,128)

  # Línea vertical Derecha (ROJO)
  for i in range (237,291):     # [237,290]
    pixels[i] = (200,0,0)

  # Semicírculo derecho (ROJO)
  for i in range (11,80):       # [11,79]
    pixels[i] = (200,0,0)

  pixels.write()

#///////////////////////////////////////////////////////////////////////////////
#/ PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO        //
#///////////////////////////////////////////////////////////////////////////////
#seleccionarMejorRedWiFiDisponible()

seleccionarMejorRedWiFiDisponible()
print("Connecting to WiFi network '{}'".format(SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID,PASSWD)
while not wifi.isconnected():
  time.sleep(5)
  print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])
actualizarSketch()

print("Connecting to Blynk server...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Create BlynkTimer Instance
timer = BlynkTimer()

#///////////////////////////////////////////////////////////////////////////////
#/                               FUNCIONES BLYNK
#///////////////////////////////////////////////////////////////////////////////
@blynk.on("connected")
def blynk_connected(ping):
  desplegarMensajeVisual(3)
  print('Blynk ready. Ping:', ping, 'ms')
  blynk.send_internal("utc","time")
  print('RTC sync request was sent')

@blynk.on("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')
banderaSalida=False

@blynk.on("internal:utc")
def on_utc(value):
  global tiempoLocal

  if value[0] == "time":
    ts = int(value[1])//1000
    # on embedded systems, you may need to subtract time difference between 1970 and 2000
    ts -= 946684800
    # Ajuste por zona
    ts += 3600 * ZONA_MEXICO
    tiempoLocal = time.localtime(ts)
    # Año, mes (1-12), día del mes (1-31), hora (0-23), minuto (0-59), segundo (0-59), día de
    # la semana (0-6 de lunes a domingo), día de año (1-366)
    # SINCRONIZACIÓN DEL RELOJ INTERNO E IMPRESIÓN DE FECHA Y HORA
    #RTC().init((year, month, mday, weekday, hour, minute, second, milisecond))
    RTC().init((tiempoLocal[0], tiempoLocal[1], tiempoLocal[2], tiempoLocal[6], tiempoLocal[3], \
                tiempoLocal[4], tiempoLocal[5], milisecond))
    print ("Fecha: {:02d}/{:02d}/{}".format(RTC().datetime()[2],
                                        RTC().datetime()[1],
                                        RTC().datetime()[0]))
    print ("Hora: {:02d}:{:02d}:{:02d}".format(RTC().datetime()[4],
                                           RTC().datetime()[5],
                                           RTC().datetime()[6]))

  #elif value[0] == "tz_name":
    #print("Timezone: ", value[1])

#///////////////////////////////////////////////////////////////////////////////
#/                             FIN FUNCIONES BLYNK
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
#/                                   TIMERS
#///////////////////////////////////////////////////////////////////////////////
if (RTC().datetime()[1]!=9):
  timerReloj=timer.set_interval(1,actualizarHora)
#timer.set_interval(60,actualizarSketch)
#///////////////////////////////////////////////////////////////////////////////
#/                                FIN DE TIMERS
#///////////////////////////////////////////////////////////////////////////////

diaInicial=RTC().datetime()[2]
opcionSeleccionadaAzar=0
random.seed()
banderaAnimacionEstablecida=False
banderaReloj = False

# CICLO INFINITO EN ESPERA POR EVENTOS
while banderaSalida==False:
  try:
    blynk.run()
    timer.run()

    # Posiciones en RTC(): 0. Año; 1: Mes; 2: Día; 4: Hora; 5: Minuto; 6: Segundo
    if (RTC().datetime()[2]!=diaInicial):
      banderaAnimacionEstablecida=false
      opcionSeleccionadaAzar=0
      diaInicial = RTC().datetime()[2]

    if (RTC().datetime()[1]==9):
      if (RTC().datetime()[5]%5!=0 and not banderaReloj):
        timerReloj = timer.set_interval(1,actualizarHora)
        banderaReloj = True
        banderaAnimacionEstablecida = False
      elif (RTC().datetime()[5]%5==0 and banderaReloj):
        timer._delete(timerReloj)
        banderaReloj = False
        if (opcionSeleccionadaAzar==0):
          opcionSeleccionadaAzar = random.randint(1,1)
        if (opcionSeleccionadaAzar==1):
          if (not banderaAnimacionEstablecida):
            bandera()
            banderaAnimacionEstablecida = True
#         else:
#           fuegosArtificiales()
#     elif mes==12 or mes == 1:
#       if (opcionSeleccionadaAzar==0):
#         opcionSeleccionadaAzar = random(1,3)
#     }
#     if (opcionSeleccionadaAzar == 1)
#     {
#       if (!banderaAnimacionEstablecida)
#       {
#         bandera();
#         banderaAnimacionEstablecida = true;
#       }
#     }
#     else
#       fuegosArtificiales();
#   }
#   else
#     desplegarHora();
# 
#   // Esperar que pase 1 segundo
#   while (segundo == segundoAnterior)
#     segundo = second();
#   segundoAnterior = segundo;
# }
  except KeyboardInterrupt:
    banderaSalida = True

wifi.disconnect()
time.sleep(1)
if not wifi.isconnected():
  print("WiFi disconnected")
else:
  print("WiFi connected. Can't disconnect")
print("Programa terminado")

#///////////////////////////////////////////////////////////////////////////////
#/ PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL        //
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
#/ FIN PROVISIONAL
#///////////////////////////////////////////////////////////////////////////////
