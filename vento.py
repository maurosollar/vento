import esp32, network, json, ssd1306, utils
from machine import Pin, SoftI2C, ADC, Timer
from micropyserver import MicroPyServer
from time import sleep

WIND_DIR_PIN = 4
WIND_SPD_PIN = 6

wind_dir_pin = ADC(Pin(WIND_DIR_PIN))
wind_speed_pin = Pin(WIND_SPD_PIN, Pin.IN)

data_check_timer = Timer(2)

i2c = SoftI2C(scl=Pin(32), sda=Pin(33), freq=400000) # IO33=485_EN / IO32=CFG

display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Visto no site do MicroPython - Wireless-Tag's WT32-ETH01 v1.4
lan = network.LAN(mdc=machine.Pin(23), mdio=machine.Pin(18),
                  phy_type=network.PHY_LAN8720, phy_addr=1,
                  power=machine.Pin(16))

if not lan.active():
    lan.active(True)

while not lan.isconnected():
    pass

global contador = 0

sleep(3)
endip = lan.ifconfig()[0]
display.fill(0)
display.text('End. IP:', 0, 0, 1)
display.text(endip, 0, 16, 1)
display.show()


def calcula()
    global contador
    rpm = contador
    contador = 0
    var_adc = adc.read_u16() # Faixa 0-65535
    if val_adc <= 0.27:
        dir_grau = 315
        dir_nome = "Noroeste"
    elif val_adc <= 0.32:
        dir_grau = 270
        dir_nome = "Oeste"
    elif val_adc <= 0.38:
        dir_grau = 225
        dir_nome = "Sudoeste"
    elif val_adc <= 0.45:
        dir_grau = 180
        dir_nome = "Sul"
    elif val_adc <= 0.57: 
        dir_grau = 135
        dir_nome = "Sudeste"
    elif val_adc <= 0.75:
        dir_grau = 90
        dir_nome = "Leste"
    elif val_adc <= 1.25:  
        dir_grau = 45
        dir_nome = "Nordeste"
    else:
        dir_grau = 0
        dir_grau = "Norte"
    speed = "Velocidade KM/h: " + str(speed)
    winddir = "Direcao: " + str(winddir)
    display.fill(0)
    display.text('End. IP:', 0, 0, 1)
    display.text(endip, 0, 16, 1)
    display.text(speed, 0, 32, 1)
    display.text(winddir, 0, 48, 1)        
    display.show()

def wind_speed_int(irq):
    global wind_speed_last_int  # anti repique por software do reed switch mecânico
    global contador
    if ticks_diff(ticks_ms(), wind_speed_last_int) > 5:  # Não menos que 5ms entre pulsos
        wind_speed_last_intrpt = ticks_ms()
        contador += 1

def winddir_speed(request):
    ''' rota principal '''
    json_str = json.dumps({"speed": speed, "winddir": winddir})
    server.send("HTTP/1.0 200 OK\n")
    server.send("Content-Type: application/json\n")
    server.send("Connection: close\n\n")      
    server.send(json_str)

wind_speed_last_int = ticks_ms()
wind_speed_pin.irq(trigger=Pin.IRQ_RISING, handler=wind_speed_int)
data_check_timer.init(period=1000, mode=Timer.PERIODIC, callback=calcula)

server = MicroPyServer()
server.add_route("/", winddir_speed)
server.start()
