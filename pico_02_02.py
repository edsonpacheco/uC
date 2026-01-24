from machine import Pin, ADC
import utime
# Sensor no GP26 (ADC 0)
sensor = ADC(26)
led_v = Pin(12, Pin.OUT)
led_r = Pin(13, Pin.OUT)

while True:
    # MicroPython usa 16 bits (0-65535)
    raw = sensor.read_u16()
    temp = (raw / 65535.0) * 100.0
    
    quente = temp > 40.0
    led_v.value(not quente)
    led_r.value( quente)
    
    print("Temp: {:.1f} C".format(temp))
    utime.sleep_ms(500)
