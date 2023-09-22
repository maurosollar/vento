global contador = 0

WIND_DIR_SENSOR_IN_PIN = 4

WIND_SPD_SENSOR_IN_PIN = 6

wind_dir_pin = ADC(Pin(WIND_DIR_SENSOR_IN_PIN))

wind_speed_pin = Pin(WIND_SPD_SENSOR_IN_PIN, Pin.IN)

data_check_timer = Timer(2)


def wind_speed_isr(irq):
    global wind_speed_last_intrpt  # anti repique por software do reed switch mecânico
    global contador
    if ticks_diff(ticks_ms(), wind_speed_last_intrpt) > 5:  # Não menos que 5ms entre pulsos
        wind_speed_last_intrpt = ticks_ms()
        contador += 1

wind_speed_last_intrpt = ticks_ms()

wind_speed_pin.irq(trigger=Pin.IRQ_RISING, handler=wind_speed_isr)

data_check_timer.init(period=1000, mode=Timer.PERIODIC, callback=record_weather_data_points)
