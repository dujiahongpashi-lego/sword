MOUSE_APPR = b'\x03\x19\xC2\x03'  # 鼠标外观
GAMEPAD_APPR = b'\x03\x19\xC3\x03'  # 手柄外观

MOUSE_REPORT = bytes([    # Report Description: describes what we communicate
    0x05, 0x01,   # USAGE_PAGE (Generic Desktop)
    0x09, 0x02,   # USAGE (Mouse)
    0xa1, 0x01,   # COLLECTION (Application)
    0x85, 0x01,  # REPORT_ID (1)
    0x09, 0x01,  # USAGE (Pointer)
    0xa1, 0x00,  # COLLECTION (Physical)
    0x05, 0x09,  # Usage Page (Buttons)
    0x19, 0x01,  # Usage Minimum (1)
    0x29, 0x03,  # Usage Maximum (3)
    0x15, 0x00,  # Logical Minimum (0)
    0x25, 0x01,  # Logical Maximum (1)
    0x95, 0x03,  # Report Count (3)
    0x75, 0x01,  # Report Size (1)
    0x81, 0x02,  # Input(Data, Variable, Absolute); 3 button bits
    0x95, 0x01,  # Report Count(1)
    0x75, 0x05,  # Report Size(5)
    0x81, 0x03,  # Input(Constant);                 5 bit padding
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x30,  # Usage (X)
    0x09, 0x31,  # Usage (Y)
    0x09, 0x38,  # Usage (Wheel)
    0x15, 0x81,  # Logical Minimum (-127)
    0x25, 0x7F,  # Logical Maximum (127)
    0x75, 0x08,  # Report Size (8)
    0x95, 0x03,  # Report Count (3)
    # Input(Data, Variable, Relative); 3 position bytes (X,Y,Wheel)
    0x81, 0x06,
    0xc0,  # END_COLLECTION
    0xc0          # END_COLLECTION
])

GAMEPAD_REPORT = bytes([
    # Gamepad
    0x05, 0x01,  # USAGE_PAGE (Generic Desktop)
    0x09, 0x05,  # USAGE (Gamepad)
    0xa1, 0x01,  # COLLECTION (Application)
    0x85, 0x01,  # REPORT_ID (3)--3改1
    # 14按键
    0x05, 0x09,  # USAGE_PAGE (Button)
    0x19, 0x01,  # USAGE_MINIMUM (最小值：1)
    0x29, 0x0E,  # USAGE_MAXIMUM (最大值：14)
    0x15, 0x00,  # LOGICAL_MINIMUM (0)
    0x25, 0x01,  # LOGICAL_MAXIMUM (1)
    0x75, 0x01,  # REPORT_SIZE (1)
    0x95, 0x0E,  # REPORT_COUNT (14个按键)
    0x81, 0x02,  # INPUT (Data,Var,Abs)
    # 补上两个空白按键
    0x95, 0x01,  # REPORT_COUNT (1)
    0x75, 0x02,  # REPORT_SIZE (2位)
    0x81, 0x01,  # INPUT (保留)

    # 8方向十字键（HAT）
    0x05, 0x01,  # USAGE_PAGE (General Desktop)
    0x09, 0x39,  # USAGE (Hat Switch)，（Switch十字鍵）
    0x15, 0x00,  # LOGICAL_MINIMUM (0)，实际最小值
    0x25, 0x07,  # LOGICAL_MAXIMUM (7)，实际最大值
    # 0x35, 0x00,       #   PHYSICAL_MINIMUM (0)，实际最小值
    # 0x46, 0x3B, 0x01, #   PHYSICAL_MAXIMUM (315) ，实际最大值
    # 0x65, 0x14,       #   UNIT (Eng Rot:Angular Pos)，单位：角度
    0x75, 0x04,  # REPORT_SIZE (4)，占4位
    0x95, 0x01,  # REPORT_COUNT (1)
    0x81, 0x02,  # INPUT (Data,Var,Abs)
    # 补4个空位
    0x95, 0x01,       # REPORT_COUNT (1)
    0x75, 0x04,       # REPORT_SIZE (4)，共4位
    0x81, 0x01,       # INPUT

    # X, Y和Z轴
    0x15, 0x00,  # LOGICAL_MINIMUM (0)
    0x26, 0xff, 0x00,  # LOGICAL_MAXIMUM (255)
    0x75, 0x08,  # REPORT_SIZE (8)
    0x09, 0x01,  # USAGE (Pointer)，游标
    0xA1, 0x00,  # COLLECTION (Physical)，游标坐标资料集合
    0x09, 0x30,  # USAGE (x)
    0x09, 0x31,  # USAGE (y)
    0x09, 0x32,  # USAGE (z)
    0x09, 0x35,  # USAGE (rz)
    0x95, 0x04,  # REPORT_COUNT (4)
    0x81, 0x02,  # INPUT (Data,Var,Abs)
    0xc0,  # END_COLLECTION
    0xc0  # END_COLLECTION
])
# 第1字节
# 每一位：按钮01234567 (SWITCH: X B A Y L R LT RT)(PS: 方 叉 圈 三角 L1 R1 L2 R2)(值: 0x01 0x02 0x04 0x08 0x10 0x20 0x40 0x80)
# 第2字节
# 每一位：按钮8 9 10 11 12 13 空 空(- + L3 R3 Home 截图)
# 第3字节
# 前4位方向(值0~7十字方向键8个方向) 后4位空
# 第4567字节
# 摇杆lj rj的x y x(z) y(rz)


class HID_Device():
    def __init__(self):
        self.appr = MOUSE_APPR  # 默认鼠标外观
        self.report_map = MOUSE_REPORT  # 默认鼠标report map

    def get_notify_payload(self, cmd, data):  # 返回值可能是单个命令，也可能是列表
        return []


class Simulate_Mouse(HID_Device):
    def _get_move_payload(self, data):
        if type(data) == type(1) or data == []:  # 输入类型检查，数组类型才可以继续往下
            return b'\x00\x00\x00\x00'
        pitch = data[0]
        roll = data[1]
        SPEED_LIMIT = 30  # 限速绝对值，否则鼠标移动过快
        x_speed = [SPEED_LIMIT, roll][roll < SPEED_LIMIT]
        y_speed = [SPEED_LIMIT, pitch][pitch < SPEED_LIMIT]
        x_speed = [0-SPEED_LIMIT, x_speed][x_speed > 0-SPEED_LIMIT]
        y_speed = [0-SPEED_LIMIT, y_speed][y_speed > 0-SPEED_LIMIT]
        # 倒持，正数表示左、上
        #y_move = (0xff - y_speed).to_bytes(1, 'big')
        #x_move = (0xff - x_speed).to_bytes(1, 'big')
        # 侧持
        x_move = (0xff - y_speed).to_bytes(1, 'big')
        y_move = (0xff - x_speed).to_bytes(1, 'big')
        # print(y_move, x_move)
        return b'\x00' + x_move + y_move + b'\x00'

    def _get_roll_payload(self, data):
        if type(data) == type([]) or data == 0:  # 输入类型检查，数值类型才可以继续往下
            return b'\x00\x00\x00\x00'
        return [b'\x00\x00\x00\x01', b'\x00\x00\x00\xff'][data < 0]

    def get_notify_payload(self, cmd, data):
        cmd_map = {
            'LB': 'R_CLICK',
            'RB': 'L_CLICK',  # 默认倒持，左右键相反
            'AN': 'MOVE',
            'M1R': 'WHELL_ROLL',
            'M2R': 'WHELL_ROLL'
        }
        '''
        # 只挥动 打游戏版：
        cmd_map = {
            'LB': 'R_CLICK',
            'RB': 'L_CLICK',  # 默认倒持，左右键相反
            'TAP': 'L_CLICK',
            'SK': 'L_CLICK'
        }
        '''
        try:
            current_cmd = cmd_map[cmd]
            repeat_map = {
                'L_CLICK': lambda d: [b'\x01\x00\x00\x00', b'\x00\x00\x00\x00'],
                'R_CLICK': lambda d: [b'\x02\x00\x00\x00', b'\x00\x00\x00\x00'],
                'MOVE': self._get_move_payload,
                'WHELL_ROLL': self._get_roll_payload
            }
            return repeat_map[current_cmd](data)
        except Exception as e:
            # print("Unexpected cmd", e)
            return None


class Simulate_Gamepad(HID_Device):
    def __init__(self, game):
        self.appr = GAMEPAD_APPR
        self.report_map = GAMEPAD_REPORT 
        self._game = game

    def get_notify_payload(self, cmd, data):
        try:
            params = self._game.cmd_to_action(cmd)
            # print(params)
            return self._get_payload(*params, data)
        except Exception as e:
            # print("Unexpected cmd", e)
            return None

    def _angle_to_coordinate(self, angle):
        # 10度以内为安全区
        # 角度入参范围 -90 到 90
        # 先映射到坐标 -128 ~ -38 and 38 ~ 128
        # 再整体增加128
        coordinate = 0
        if angle < -10:
            coordinate = angle - 38
        elif angle > 10:
            coordinate = angle + 38
        coordinate += 128
        return coordinate
        
    def _data_to_xy(self, data):
        if type(data) != type([]):
            return b'\x80\x80'
        y_origin = 0 - data[1] # 横滚
        x_origin = data[0] # 俯仰
        x_move = self._angle_to_coordinate(x_origin).to_bytes(1, 'big')
        y_move = self._angle_to_coordinate(y_origin).to_bytes(1, 'big')
        return x_move + y_move

    def _get_payload(self, btn_type, btn, press_type, data):
        # btn_type: BTN, BTN_EX(TODO), CROSS, L_ROCKER,R_ROCKER
        # btn: 如b\x00
        # press_type: CLICK PRESS RELEASE RETURN
        payload = b'\x00\x00\x0F\x80\x80\x80\x80'  # default
        if btn_type == 'L_ROCKER' or btn_type == 'R_ROCKER':
            btn_data = self._data_to_xy(data)
            payload = {
                'L_ROCKER': b'\x00\x00\x0F' + btn_data + b'\x80\x80',
                'R_ROCKER': b'\x00\x00\x0F\x80\x80' + btn_data
            }[btn_type]
        if btn_type == 'BTN':
            payload = btn + b'\x00\x0F\x80\x80\x80\x80'
        if btn_type == 'CROSS':
            payload = b'\x00\x00' + btn + b'\x80\x80\x80\x80'

        if press_type == 'CLICK':
            return [payload, b'\x00\x00\x0F\x80\x80\x80\x80']
        if press_type == 'PRESS':
            return payload
        if press_type == 'RELEASE' or press_type == 'RETURN':
            return b'\x00\x00\x0F\x80\x80\x80\x80'

