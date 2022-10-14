import bluetooth #导入BLE功能模块
from bluetooth import UUID
import random, json, struct, time, micropython, binascii
from micropython import const

MOUSE_REPORT = bytes([    # Report Description: describes what we communicate
            0x05, 0x01,   # USAGE_PAGE (Generic Desktop)
            0x09, 0x02,   # USAGE (Mouse)
            0xa1, 0x01,   # COLLECTION (Application)
            0x85, 0x01,   #   REPORT_ID (1)
            0x09, 0x01,   #   USAGE (Pointer)
            0xa1, 0x00,   #   COLLECTION (Physical)
            0x05, 0x09,   #         Usage Page (Buttons)
            0x19, 0x01,   #         Usage Minimum (1)
            0x29, 0x03,   #         Usage Maximum (3)
            0x15, 0x00,   #         Logical Minimum (0)
            0x25, 0x01,   #         Logical Maximum (1)
            0x95, 0x03,   #         Report Count (3)
            0x75, 0x01,   #         Report Size (1)
            0x81, 0x02,   #         Input(Data, Variable, Absolute); 3 button bits
            0x95, 0x01,   #         Report Count(1)
            0x75, 0x05,   #         Report Size(5)
            0x81, 0x03,   #         Input(Constant);                 5 bit padding
            0x05, 0x01,   #         Usage Page (Generic Desktop)
            0x09, 0x30,   #         Usage (X)
            0x09, 0x31,   #         Usage (Y)
            0x09, 0x38,   #         Usage (Wheel)
            0x15, 0x81,   #         Logical Minimum (-127)
            0x25, 0x7F,   #         Logical Maximum (127)
            0x75, 0x08,   #         Report Size (8)
            0x95, 0x03,   #         Report Count (3)
            0x81, 0x06,   #         Input(Data, Variable, Relative); 3 position bytes (X,Y,Wheel)
            0xc0,         #   END_COLLECTION
            0xc0          # END_COLLECTION
        ])

adv_data = b'\x02\x01\x05' + b'\x03\x03\x12\x18' + b'\x03\x19\xC2\x03' + b'\x0D\x09' + "天空之傲".encode("UTF-8")# "ESP Mouse".encode("UTF-8")
                                
HIDS = (                              # Service description: describes the service and how we communicate
    UUID(0x1812),                     # Human Interface Device
    (
        (UUID(0x2A4A), bluetooth.FLAG_READ),       # HID information
        (UUID(0x2A4B), bluetooth.FLAG_READ),       # HID report map
        (UUID(0x2A4C), bluetooth.FLAG_WRITE),      # HID control point
        (UUID(0x2A4D), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY, ((UUID(0x2908), 1),)),  # HID report / reference
        (UUID(0x2A4D), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE,  ((UUID(0x2908), 1),)),  # HID report / reference
        (UUID(0x2A4E), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE), # HID protocol mode
    ),
)
services = (HIDS,)

LEGO_ARRD='38:0B:3C:AB:34:B5' # 乐高蓝牙MAC地址
LEGO_SERVICE_UUID = UUID(0x9527)
LEGO_CHARACTERISTIC_UUID = UUID(0x000A) # 乐高侧的只读CAHR

_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_CONNECTION_UPDATE = const(27)
_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6
_IRQ_PERIPHERAL_CONNECT = 7
_IRQ_PERIPHERAL_DISCONNECT = 8
_IRQ_GATTC_SERVICE_RESULT = 9
_IRQ_GATTC_CHARACTERISTIC_RESULT = 11
_IRQ_GATTC_READ_RESULT = 15
_IRQ_GATTC_READ_DONE = 16
_IRQ_GATTC_NOTIFY = 18
_IRQ_GATTC_CHARACTERISTIC_DONE = 12

def get_move_data(data):
    if type(data) == type(1) or data == []: # 数组类型才可以继续往下
        return b'\x00\x00\x00\x00'
    pitch = data[0]
    roll = data[1]
    SPEED_LIMIT = 30 # 限速绝对值，否则鼠标移动过快
    x_speed = [SPEED_LIMIT, roll][roll < SPEED_LIMIT] 
    y_speed = [SPEED_LIMIT, pitch][pitch < SPEED_LIMIT]
    x_speed = [0-SPEED_LIMIT, x_speed][x_speed > 0-SPEED_LIMIT]
    y_speed = [0-SPEED_LIMIT, y_speed][y_speed > 0-SPEED_LIMIT]
    #x_move = b'\x00'
    #y_move = b'\x00'
    # 默认倒持，正数表示左、上
    y_move = (0xff - y_speed).to_bytes(1, 'big')
    x_move = (0xff - x_speed).to_bytes(1, 'big')
    print(y_move, x_move)
    #if y_speed == 0:
    #    pass
    #elif y_speed > 0: # 上
    #    y_move = (0xff - y_speed).to_bytes(1, 'big')
    #else: # 下
    #    y_move = y_speed.to_bytes(1, 'big')
    #if x_speed == 0:
    #    pass
    #elif x_speed > 0: # 左
    #    x_move = (0xff - x_speed).to_bytes(1, 'big')
    #else: # 右
    #    x_move = x_speed.to_bytes(1, 'big')
    return b'\x00' + x_move + y_move + b'\x00'

def get_roll_data(data):
    if type(data) == type([]) or data == 0: # 数值类型才可以继续往下
        return b'\x00\x00\x00\x00'
    return [b'\x00\x00\x00\x01', b'\x00\x00\x00\xff'][data<0]

class BLEDoubleConnect:
    def __init__(self, ble=None):
        if ble == None:
            ble = bluetooth.BLE()
            ble.active(True)
            ble.config(gap_name="天空之傲-求赞求三连")
            handles = ble.gatts_register_services(services)
            ble.gap_advertise(100, adv_data)
            (h_info, h_map, _, h_repin, h_d1, h_repout, h_d2, h_model,) = handles[0]
            ble.gatts_write(h_info, b"\x01\x01\x00\x02")     # HID info: ver=1.1, country=0, flags=normal
            ble.gatts_write(h_map, MOUSE_REPORT)    # HID input report map
            ble.gatts_write(h_d1, b"\x01\x01")  # HID reference: id=1, type=input
            ble.gatts_write(h_d2, b"\x01\x02")  # HID reference: id=1, type=output
            ble.gatts_write(h_model, b"\x01")   # HID Protocol Model: 0=Boot Model, 1=Report Model
            
        self._ble = ble
        self._ble.irq(self._irq)
        self._conn_handle = None
        self._rx_handle = None
        self._pc_conn_handle = None
        self._pc_bluetooth_connected = False
        self._h_repin = h_repin
        self._ble.gatts_set_buffer(h_repin, 1024)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        print('Try to connect...', self._addr_type, self._addr)
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # Returns true if we've successfully connected and discovered uart characteristics.
    def is_connected(self):
        return (
            self._conn_handle is not None
            and self._rx_handle is not None
        )

    # Disconnect from current device.
    def disconnect(self):
        print('Try disconnect ', self._conn_handle)
        if self._conn_handle is None:
            print('error, not found conn_handle')
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._conn_handle = None
        
    def is_pc_connected(self):
        return (
            self._pc_conn_handle is not None
            and self._h_repin is not None
        )
    def pc_disconnect(self):
        print('Try disconnect pc', self._pc_conn_handle)
        if self._pc_conn_handle is None:
            print('error, not found conn_handle')
            return
        self._ble.gap_disconnect(self._pc_conn_handle)
        self._pc_conn_handle = None

    def _on_scan(self, addr_type, addr_show_addr, addr):
        if addr_type is not None:
            print("Found peripheral:", addr_show_addr)
            # time.sleep_ms(500)
            self.connect()
        else:
            self.timed_out = True
            print("No uart peripheral '{}' found.".format(self._search_name))

    # Find a device advertising the uart service.
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._addr_show_str = None
        self._scan_callback = callback
        print('Start Scan')
        self._ble.gap_scan(20000, 30000, 30000)

    def scan_connect(self):
        self.timed_out = False
        self.scan(callback=self._on_scan)
        while not self.is_connected() and not self.timed_out:
            time.sleep_ms(10)
        return not self.timed_out
    
    # 转发(LEGO to PC)
    def repeat(self, cmd, data):
        cmd_map = {
            'LB': 'R_CLICK',
            'RB': 'L_CLICK',# 默认倒持，左右键相反
            'AN': 'MOVE',
            'WRS': 'W_ROLL',
            }
        current_cmd = cmd_map[cmd]
        repeat_map = { # TODO 流程待优化
            'L_CLICK':b'\x01\x00\x00\x00',
            'R_CLICK':b'\x02\x00\x00\x00',
            'MOVE': get_move_data(data),
            'W_ROLL': get_roll_data(data)
            }
        repeat_notify_cmd = repeat_map[current_cmd]
        print('notify cmd ', repeat_notify_cmd)
        if self._pc_conn_handle:
            self._ble.gatts_notify(self._pc_conn_handle, self._h_repin, repeat_notify_cmd)
            if cmd_map[cmd] in ['L_CLICK', 'R_CLICK']:
                self._ble.gatts_notify(self._pc_conn_handle, self._h_repin, b'\x00\x00\x00\x00')

    def _irq(self, event, data):
        #print('BLE Event', event)
        if event == _IRQ_CENTRAL_CONNECT: # 主机与ESP连接
            conn_handle, _, _ = data
            print("New PC connection", conn_handle)
            self._pc_conn_handle = conn_handle
            self._pc_bluetooth_connected = True
        elif event == _IRQ_PERIPHERAL_CONNECT: # ESP与乐高连接
            time.sleep_ms(100)
            conn_handle, addr_type, addr = data
            print('Connect successful.', conn_handle)
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(conn_handle)
        elif event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            addr_str = binascii.hexlify(addr).decode('utf-8')
            if addr_str == LEGO_ARRD.lower().replace(':',''):
                print('Found one!', addr_str)
                time.sleep_ms(100)
                self._addr_type = addr_type
                self._addr_show_str = addr_str
                self._addr = bytes(addr) # Note: addr buffer is owned by caller so need to copy it.
                self._ble.gap_scan(None)
        elif event == _IRQ_SCAN_DONE:
            print('Scan Done')
            time.sleep_ms(100)
            if self._scan_callback:
                if self._addr:
                    self._scan_callback(self._addr_type, self._addr_show_str, self._addr)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)
        elif event == _IRQ_GATTC_SERVICE_RESULT: # (LEGO)SERVICE查找成功
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print('_IRQ_GATTC_SERVICE_RESULT, Found service ', uuid, 'vs',LEGO_SERVICE_UUID)
            if conn_handle == self._conn_handle and uuid == LEGO_SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle
                print("Discover the right service", uuid)
                time.sleep_ms(100)
                self._ble.gattc_discover_characteristics(self._conn_handle, start_handle, end_handle)
                print("Try to discover some characteristics...")
        elif event == _IRQ_GATTC_SERVICE_DONE:
            pass
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT: # (LEGO)CHARACTERISTIC连接成功
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle:
                if uuid == LEGO_CHARACTERISTIC_UUID:
                    print("Discover the right CHARACTERISTIC ", uuid)
                    self._rx_handle = value_handle
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            pass
        elif event == _IRQ_GATTC_NOTIFY: # 获取到了(LEGO)广播数据
            conn_handle, value_handle, notify_data = data
            json_msg = json.loads(notify_data)
            #print('Json msg', json_msg)
            msg_cmd = json_msg[0]
            msg_data = json_msg[1]
            #print('Msg', msg_cmd, msg_data)
            self.repeat(msg_cmd, msg_data)

def start():
    # Initialize
    print("starting BLE")
    ble = BLEDoubleConnect()

    try:
        found_lego = ble.scan_connect()
        if not found_lego:
            print ("Scanning timed out")
            del(ble)
            raise SystemExit
        print("LEGO Connected")
    
        time.sleep(600)
    
        ble.disconnect()
        print("LEGO Disconnected")
        time.sleep_ms(2000)
    
    except Exception as e:
        print("ERROR!!!!", e)

start()



