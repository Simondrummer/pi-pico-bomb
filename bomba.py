import utime
from machine import I2C, Pin, PWM
from pico_i2c_lcd import I2cLcd

# --- Konfiguracja LCD ---
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 39, 2, 16)

# --- Konfiguracja buzzera ---
buzzer = PWM(Pin(16))
buzzer.duty_u16(0)

# --- Konfiguracja przycisków (GPIO ↔ 3.3V + PULL_DOWN) ---
btn_start = Pin(10,  Pin.IN, Pin.PULL_DOWN)
btn_abort = Pin(11,  Pin.IN, Pin.PULL_DOWN)
btn_up    = Pin(12,  Pin.IN, Pin.PULL_DOWN)
btn_down  = Pin(13,  Pin.IN, Pin.PULL_DOWN)

def tone(freq, ms):
    if freq <= 0:
        buzzer.duty_u16(0)
        utime.sleep_ms(ms)
    else:
        buzzer.freq(freq)
        buzzer.duty_u16(32768)
        utime.sleep_ms(ms)
        buzzer.duty_u16(0)


def custom_char():
    lcd.custom_char(0, bytearray([
        0x00,
        0x04,
        0x0E,
        0x1F,
        0x04,
        0x04,
        0x04,
        0x00
    ]))
    lcd.custom_char(1, bytearray([
        0x00,
        0x04,
        0x04,
        0x04,
        0x1F,
        0x0E,
        0x04,
        0x00
    ]))
    

def wait_for_start(count):
    
    lcd.clear()
    lcd.move_to(1, 0)
    lcd.putstr("NACISNIJ START")
    lcd.move_to(0, 1)
    lcd.putstr(f"Czas: {count:2d}s")
    lcd.move_to(11, 1)
    lcd.putstr("G  B: ")
    custom_char()
    lcd.move_to(12,1)
    lcd.putchar(chr(0))
    lcd.move_to(15,1)
    lcd.putchar(chr(1))
    

    while True:
        if btn_start.value():           # wciśnięty = 1
            utime.sleep_ms(200)         # anti-bounce
            return count
        if btn_up.value():
            count = min(99, count + 1)
            lcd.move_to(0, 1)
            lcd.putstr(f"Czas: {count:2d}s")
            utime.sleep_ms(200)
        if btn_down.value():
            count = max(1, count - 1)
            lcd.move_to(0, 1)
            lcd.putstr(f"Czas: {count:2d}s")
            utime.sleep_ms(200)
        utime.sleep_ms(50)

def countdown(sec):
    for i in range(sec, 0, -1):
        if btn_abort.value():
            lcd.clear()
            lcd.putstr("   PRZERWANO")
            tone(400, 300)
            return

        lcd.clear()
        lcd.putstr("  UWAGA! BOMBA")
        lcd.move_to(0,1)
        lcd.putstr(f"     {i:2d} sek")

        if i <= 5:
            freq = 1200 + (5 - i)*100
            dur  = 80
        else:
            freq = 800
            dur  = 100
        tone(freq, dur)
        utime.sleep_ms(1000 - dur)

    # Finał
    lcd.clear()
    lcd.putstr("     BOOM!")
    for _ in range(15):
        tone(2000, 100)
        utime.sleep_ms(50)
    lcd.move_to(0,1)
    

# --- Pętla główna ---
count = 10
while True:
    # 1) wybór czasu i czekaj na START
    count = wait_for_start(count)
    # 2) odliczaj
    countdown(count)
    # 3) pauza przed kolejnym cyklem
    utime.sleep_ms(1500)
