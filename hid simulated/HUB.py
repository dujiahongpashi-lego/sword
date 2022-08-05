import bluetooth, json
from mindstorms.control import Timer
from time import sleep_ms
from hub import button, port, display, Image
from micropython import const

_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

if 'FLAG_INDICATE' in dir(bluetooth):
    # We're on MINDSTORMS Robot Inventor
    # New version of bluetooth
    _IRQ_GATTS_WRITE = 3
else:
    # We're probably on SPIKE Prime
    _IRQ_GATTS_WRITE = 1 << 2

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# 随意而为的UUID
_UART_UUID = bluetooth.UUID(0x9527)
_UART_TX = (
    bluetooth.UUID(0x000A),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID(0x000B),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

class TianKongZhiAo():
    def __init__(self):
        # 建立蓝牙连接
        self.is_bluetooth_connected = False
        self.changed = False
        self.timer = Timer()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle, data)
            self._conn_handle = conn_handle
            self.is_bluetooth_connected = True
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle, data)
            self._conn_handle = None
            self.is_bluetooth_connected = False
            self._advertise()

    # 拔剑！(初始化)
    def draw(self):
        self._ble = bluetooth.BLE()
        #self._ble.config(gap_name='LEGO SWORD', rxbuf=256)
        self._ble.config(rxbuf=256)
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),
        ) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._ble.gatts_set_buffer(self._handle_tx, 256)
        self._ble.gatts_set_buffer(self._handle_rx, 256)
        self._advertise()

    def disconnect(self):
        try:
            if not self._conn_handle:
                return
        except AttributeError:
            return
        self._ble.gap_disconnect(self._conn_handle)
        sleep_ms(500)

    def is_connected(self):
        return self.is_bluetooth_connected

    def send(self, cmd, data=0): 
        # 默认Notify BUFFER上限是20字节。未能找到扩大BUFFER的方法，因此需要控制协议格式（body大小不可超过20byte）
        #print('Send msg:', cmd)
        body = json.dumps([cmd, data])
        #print('Set msg body:', body)
        self._ble.gatts_notify(self._conn_handle, self._handle_tx, body)

    def _advertise(self, interval_us=100000):
        print("Starting bluetooth advertising")
        self._ble.gap_advertise(interval_us)
 

class ConnectionMode():
    CONNECT = 1
    DISCONNECT = 2

def set_display(mode):
    if mode == ConnectionMode.DISCONNECT:
        _images = [
            Image('00009:00030:00000:00000:00000'),
            # Image('00000:00009:00000:00000:00000'),
            Image('00000:00000:00039:00000:00000'),
            # Image('00000:00000:00000:00009:00000'),
            Image('00000:00000:00000:00030:00009'),
            # Image('00000:00000:00000:00000:00090'),
            Image('00000:00000:00000:00300:00900'),
            # Image('00000:00000:00000:00000:09000'),
            Image('00000:00000:00000:03000:90000'),
            # Image('00000:00000:00000:90000:00000'),
            Image('00000:00000:93000:00000:00000'),
            # Image('00000:90000:00000:00000:00000'),
            Image('90000:03000:00000:00000:00000'),
            # Image('09000:00000:00000:00000:00000'),
            Image('00900:00300:00000:00000:00000'),
            # Image('00090:00000:00000:00000:00000'),
        ]
        _center_img = Image("00000:05550:05850:05550:00000")
        CLOCK_ANIMATION = [img + _center_img for img in _images]
        display.show(CLOCK_ANIMATION, delay=150, wait=False, loop=True)
    elif mode ==  ConnectionMode.CONNECT:
        display.show(Image('99999:90009:90909:90009:99999'))

try:
    lego_sword = TianKongZhiAo()
    lego_sword.draw()
    current_mode = ConnectionMode.DISCONNECT
    mode = current_mode
    set_display(mode)

    from mindstorms import MSHub, Motor
    mshub = MSHub()


    while True:
        # 按下中间按钮，退出程序
        if button.center.is_pressed():
            break
        current_mode = [ConnectionMode.DISCONNECT, ConnectionMode.CONNECT][lego_sword.is_connected()]
        if current_mode != mode:
            mode = current_mode
            set_display(mode)
        if not lego_sword.is_connected():
            continue
        # 左右按钮
        if button.left.was_pressed():
            lego_sword.send('LB') # Left Button 左按钮
            continue
        if button.right.was_pressed():
            lego_sword.send('RB')# Right Button 右按钮
            continue
        # 滚轮
        wheel = None
        try:
            wheel = Motor('A')
        except Exception as e:
            wheel = None
        if wheel:
            wr_speed = wheel.get_speed() 
            if wr_speed > 10 or wr_speed < -10:
                #print('WRS', wr_speed)
                sleep_ms(50)
                lego_sword.send('WRS', wr_speed) # Wheel Roll Speed 滚轮滚动速度
                continue
        # 俯仰
        pitch = mshub.motion_sensor.get_pitch_angle()
        # 横滚
        roll = mshub.motion_sensor.get_roll_angle()
        if pitch >= 5 or pitch <= -5 or roll >= 5 or roll <= -5:
            lego_sword.send('AN', [pitch, roll]) # Angle 角度
            sleep_ms(45)
            continue

except Exception as e:
    print('Got Exception :::', e)

# 断开蓝牙
lego_sword.disconnect()
del(lego_sword)

# 抛异常以强制结束程序
raise SystemExit
