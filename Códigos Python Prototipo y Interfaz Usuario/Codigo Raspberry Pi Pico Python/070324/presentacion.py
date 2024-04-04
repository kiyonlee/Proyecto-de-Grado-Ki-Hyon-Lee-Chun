
from utime import sleep_ms
from ssd1306 import SSD1306_I2C


def presentation(i2c):

    oled = SSD1306_I2C(128, 64, i2c)

    oled.fill(0)
    oled.text("PG - PUJ", 35, 5)
    oled.text("Ki Hyon Lee", 20, 20)
    oled.text("Sensor Temp", 25, 40)
    oled.show()
    sleep_ms(2000)
    oled.fill(0)

