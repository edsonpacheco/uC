from machine import Pin, ADC, I2C
import time

# ========== BIBLIOTECA LCD I2C ==========
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = True
        time.sleep_ms(50)
        
        # Sequência de inicialização do HD44780
        self.write_nibble(0x03)
        time.sleep_ms(5)
        self.write_nibble(0x03)
        time.sleep_ms(5)
        self.write_nibble(0x03)
        time.sleep_ms(1)
        self.write_nibble(0x02)  # Modo 4 bits
        
        self.write_cmd(0x28)  # 4-bit, 2 linhas, 5x8
        self.write_cmd(0x0C)  # Display ON, cursor OFF
        self.write_cmd(0x06)  # Increment cursor
        self.write_cmd(0x01)  # Clear display
        time.sleep_ms(2)

    def write_nibble(self, nibble):
        byte = (nibble & 0x0F) << 4
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x0C]))  # EN=1, backlight=1
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x08]))  # EN=0, backlight=1
        time.sleep_us(50)

    def write_cmd(self, cmd):
        self.write_nibble(cmd >> 4)
        self.write_nibble(cmd & 0x0F)
        time.sleep_us(50)

    def write_data(self, data):
        nibble_h = (data >> 4) << 4
        nibble_l = (data & 0x0F) << 4
        
        self.i2c.writeto(self.i2c_addr, bytes([nibble_h | 0x0D]))  # RS=1, EN=1
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([nibble_h | 0x09]))  # RS=1, EN=0
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


# Configuração de Hardware
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
pot = ADC(Pin(26))

# Definição de Estados
ST_IDLE, ST_READ, ST_DISP = 0, 1, 2
estado = ST_IDLE
last_update = time.ticks_ms()

while True:
    now = time.ticks_ms()
    
    if estado == ST_IDLE:
        if time.ticks_diff(now, last_update) >= 300:
            estado = ST_READ
            last_update = now
            
    elif estado == ST_READ:
        valor = pot.read_u16()
        tensao = (valor * 3.3) / 65535
        estado = ST_DISP
        
    elif estado == ST_DISP:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("UFPR Eng. Elet.")
        
        lcd.move_to(0, 1) # Move para a 2a linha
        lcd.putstr(f"Tensao: {tensao:.2f}V")
        
        print(f"Debug: {tensao:.2f}V")
        estado = ST_IDLE
