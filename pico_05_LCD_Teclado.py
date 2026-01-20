"""
{
  "version": 1,
  "editor": "wokwi",
  "parts": [
    { "type": "wokwi-pi-pico", "id": "pico", "top": 0, "left": 0, "attrs": {} },
    { "type": "wokwi-potentiometer", "id": "pot", "top": 300, "left": -100, "attrs": {} },
    { "type": "wokwi-lcd1602", "id": "lcd", "top": -50, "left": 250, "attrs": { "pins": "i2c" } },
    { "type": "wokwi-membrane-keypad", "id": "keypad", "top": 142, "left": 255.2, "attrs": {} }
  ],
  "connections": [
    [ "pot:SIG", "pico:GP26", "blue", [ "v0" ] ],
    [ "pot:VCC", "pico:3V3", "red", [ "v0" ] ],
    [ "pot:GND", "pico:GND.8", "black", [ "v0" ] ],
    [ "lcd:SDA", "pico:GP4", "green", [ "v0" ] ],
    [ "lcd:SCL", "pico:GP5", "yellow", [ "v0" ] ],
    [ "lcd:VCC", "pico:3V3", "red", [ "v0" ] ],
    [ "lcd:GND", "pico:GND.1", "black", [ "v0" ] ],
    [ "keypad:C1", "pico:GP6", "green", [ "v0" ] ],
    [ "keypad:C2", "pico:GP7", "blue", [ "v0" ] ],
    [ "keypad:C3", "pico:GP8", "yellow", [ "v0" ] ],
    [ "keypad:C4", "pico:GP9", "orange", [ "v0" ] ],
    [ "keypad:R1", "pico:GP10", "purple", [ "v0" ] ],
    [ "keypad:R2", "pico:GP11", "gray", [ "v0" ] ],
    [ "keypad:R3", "pico:GP12", "white", [ "v0" ] ],
    [ "keypad:R4", "pico:GP13", "brown", [ "v0" ] ]
  ],
  "dependencies": {}
}
"""

from machine import Pin, ADC, I2C
import time

# ========== CLASSE LCD I2C ==========
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = True
        time.sleep_ms(50)
        
        self.write_nibble(0x03)
        time.sleep_ms(5)
        self.write_nibble(0x03)
        time.sleep_ms(5)
        self.write_nibble(0x03)
        time.sleep_ms(1)
        self.write_nibble(0x02)
        
        self.write_cmd(0x28)
        self.write_cmd(0x0C)
        self.write_cmd(0x06)
        self.write_cmd(0x01)
        time.sleep_ms(2)

    def write_nibble(self, nibble):
        byte = (nibble & 0x0F) << 4
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x0C]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x08]))
        time.sleep_us(50)

    def write_cmd(self, cmd):
        self.write_nibble(cmd >> 4)
        self.write_nibble(cmd & 0x0F)
        time.sleep_us(50)

    def write_data(self, data):
        nibble_h = (data >> 4) << 4
        nibble_l = (data & 0x0F) << 4
        
        self.i2c.writeto(self.i2c_addr, bytes([nibble_h | 0x0D]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([nibble_h | 0x09]))
        time.sleep_us(50)
        
        self.i2c.writeto(self.i2c_addr, bytes([nibble_l | 0x0D]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([nibble_l | 0x09]))
        time.sleep_us(50)

    def clear(self):
        self.write_cmd(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        row_offsets = [0x00, 0x40]
        self.write_cmd(0x80 | (col + row_offsets[row]))

    def putstr(self, string):
        for char in string:
            self.write_data(ord(char))

# ========== CONFIGURAÇÃO DE HARDWARE ==========
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
pot = ADC(Pin(26))

# Teclado matricial 4x4
rows = [Pin(i, Pin.OUT) for i in [10, 11, 12, 13]]
cols = [Pin(i, Pin.IN, Pin.PULL_UP) for i in [6, 7, 8, 9]]

# Mapa do teclado
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def read_keypad():
    """Lê o teclado matricial"""
    for row_idx, row_pin in enumerate(rows):
        row_pin.value(0)  # Ativa a linha
        for col_idx, col_pin in enumerate(cols):
            if col_pin.value() == 0:  # Tecla pressionada
                row_pin.value(1)
                time.sleep_ms(200)  # Debounce
                return keys[row_idx][col_idx]
        row_pin.value(1)  # Desativa a linha
    return None

# Estados
ST_IDLE = 0
ST_READ = 1
ST_DISP = 2

estado = ST_IDLE
last_update = 0
v = 0.0
modo = "ADC"  # Modo inicial: mostra ADC

print("Sistema inicializado!")
print("Teclas: A=ADC, B=Tensao, C=%, D=Raw")

# ========== LOOP PRINCIPAL ==========
while True:
    now = time.ticks_ms()
    
    # Lê teclado
    key = read_keypad()
    if key:
        print(f"Tecla pressionada: {key}")
        if key == 'A':
            modo = "ADC"
        elif key == 'B':
            modo = "Tensao"
        elif key == 'C':
            modo = "Percentual"
        elif key == 'D':
            modo = "Raw"
    
    if estado == ST_IDLE:
        if time.ticks_diff(now, last_update) >= 300:
            estado = ST_READ
            last_update = now
    
    elif estado == ST_READ:
        raw = pot.read_u16()
        v = (raw * 3.3) / 65535
        perc = (raw / 65535) * 100
        estado = ST_DISP
    
    elif estado == ST_DISP:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("UFPR Eng. Elet.")
        lcd.move_to(0, 1)
        
        if modo == "ADC":
            lcd.putstr(f"ADC: {int(raw)}")
        elif modo == "Tensao":
            lcd.putstr(f"V: {v:.2f}V")
        elif modo == "Percentual":
            lcd.putstr(f"Pot: {perc:.1f}%")
        elif modo == "Raw":
            lcd.putstr(f"Raw: {raw}")
        
        estado = ST_IDLE
    
    time.sleep_ms(10)
