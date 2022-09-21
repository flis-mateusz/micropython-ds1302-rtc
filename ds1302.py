from machine import Pin

DS1302_REG_SECOND = (0x80)
DS1302_REG_MINUTE = (0x82)
DS1302_REG_HOUR = (0x84)
DS1302_REG_DAY = (0x86)
DS1302_REG_MONTH = (0x88)
DS1302_REG_WEEKDAY = (0x8A)
DS1302_REG_YEAR = (0x8C)
DS1302_REG_WP = (0x8E)
DS1302_REG_CTRL = (0x90)
DS1302_REG_RAM = (0xC0)


def format_output(value):
    return '0{}'.format(value) if len(str(value)) == 1 else value


class DS1302:
    def __init__(self, clk, dio, cs):
        self.clk = clk
        self.dio = dio
        self.cs = cs
        self.clk.init(Pin.OUT)
        self.cs.init(Pin.OUT)

    def _dec2hex(self, dat):
        return (dat // 10) * 16 + (dat % 10)

    def _hex2dec(self, dat):
        return (dat // 16) * 10 + (dat % 16)

    def _write_byte(self, dat):
        self.dio.init(Pin.OUT)
        for i in range(8):
            self.dio.value((dat >> i) & 1)
            self.clk.value(1)
            self.clk.value(0)

    def _read_byte(self):
        d = 0
        self.dio.init(Pin.IN)
        for i in range(8):
            d = d | (self.dio.value() << i)
            self.clk.value(1)
            self.clk.value(0)
        return d

    def _get_reg(self, reg):
        self.cs.value(1)
        self._write_byte(reg)
        t = self._read_byte()
        self.cs.value(0)
        return t

    def _set_reg(self, reg, dat):
        self.cs.value(1)
        self._write_byte(reg)
        self._write_byte(dat)
        self.cs.value(0)

    def _wr(self, reg, dat):
        self._set_reg(DS1302_REG_WP, 0)
        self._set_reg(reg, dat)
        self._set_reg(DS1302_REG_WP, 0x80)

    def start(self):
        t = self._get_reg(DS1302_REG_SECOND + 1)
        self._wr(DS1302_REG_SECOND, t & 0x7f)

    def stop(self):
        t = self._get_reg(DS1302_REG_SECOND + 1)
        self._wr(DS1302_REG_SECOND, t | 0x80)

    def get_second(self, second=None):
        if second is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_SECOND + 1)) % 60)
        else:
            self._wr(DS1302_REG_SECOND, self._dec2hex(second % 60))

    def get_minute(self, minute=None):
        if minute is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_MINUTE + 1)))
        else:
            self._wr(DS1302_REG_MINUTE, self._dec2hex(minute % 60))

    def get_hour(self, hour=None):
        if hour is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_HOUR + 1)))
        else:
            self._wr(DS1302_REG_HOUR, self._dec2hex(hour % 24))

    def get_weekday(self, weekday=None):
        if weekday is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_WEEKDAY + 1)))
        else:
            self._wr(DS1302_REG_WEEKDAY, self._dec2hex(weekday % 8))

    def get_day(self, day=None):
        if day is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_DAY + 1)))
        else:
            self._wr(DS1302_REG_DAY, self._dec2hex(day % 32))

    def get_month(self, month=None):
        if month is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_MONTH + 1)))
        else:
            self._wr(DS1302_REG_MONTH, self._dec2hex(month % 13))

    def get_year(self, year=None):
        if year is None:
            return format_output(self._hex2dec(self._get_reg(DS1302_REG_YEAR + 1)) + 2000)
        else:
            self._wr(DS1302_REG_YEAR, self._dec2hex(year % 100))

    def get_date_time(self, dat=None):
        if not dat:
            return [self.get_year(), self.get_month(), self.get_day(), self.get_weekday(), self.get_hour(),
                    self.get_minute(), self.get_second()]
        else:
            self.get_year(dat[0])
            self.get_month(dat[1])
            self.get_day(dat[2])
            self.get_weekday(dat[3])
            self.get_hour(dat[4])
            self.get_minute(dat[5])
            self.get_second(dat[6])

    def ram(self, reg, dat=None):
        if dat is None:
            return self._get_reg(DS1302_REG_RAM + 1 + (reg % 31) * 2)
        else:
            self._wr(DS1302_REG_RAM + (reg % 31) * 2, dat)
