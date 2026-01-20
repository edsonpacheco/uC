from machine import Pin, ADC
import machine
# GPIO e ADC Initialização
led = Pin(15, Pin.OUT)
btn = Pin(14, Pin.IN, Pin.PULL_UP)
sensor = ADC(Pin(26))
def gpio_callback(pin):
    # ADC read (0-65535) e conversão
    raw = sensor.read_u16()
    voltage = raw * 3.3 / 65535
    temp = voltage * 100.0
    print(f"Leitura ADC: {raw} | Temp: {temp:.1f} C")
    led.value(temp > 30.0)

# Configurando IRQ em Falling Edge
btn.irq(trigger=Pin.IRQ_FALLING, 
        handler=gpio_callback)

while True:
    machine.idle() # Low Power Mode
