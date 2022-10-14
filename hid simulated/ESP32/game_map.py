# 逻辑优先级遵循：1 外部传感器（颜色、距离、压力、电机）优先于HUB内置；2 事件优先于状态
# 事件
# TAP  tap拍动
# SK  shaken摇晃
# LB   left button左按钮
# RB   right button右按钮
# C+L 颜色传感器+左按钮
# C+R 颜色传感器+右按钮
# M1S motor_1 speed电机1运动速度
# M2S motor_2 speed电机2运动速度
# FS   force sensor压力传感器
# (无单独事件或状态，仅用于组合)CS color sensor颜色传感器
# (无单独事件或状态，仅用于组合)DS distence sensor距离传感器
# FSR force sensor release压力传感器释放
# CSR color sensor release颜色传感器释放
# DSR distence sensor release距离传感器释放
#
# 状态
# AN  angle(运动传感器的)角度
# C+A 颜色传感器+角度
# D+A 距离传感器+角度
# CFA 颜色传感器+压力传感器+角度
# DFA 距离传感器+压力传感器+角度
# CLA 颜色传感器+左按钮+角度
# CRA 颜色传感器+右按钮+角度
# DLA 距离传感器+左按钮+角度
# DRA 距离传感器+右按钮+角度
#
# 一般来说，除了命令C+A和D+A映射为左右摇杆，并需要处理命令数据参数。
# 其余只映射为对应按钮的点按，按下或松开。虽然接收到了具体数据值参数，但无需处理数据

class GameConf():
    def __init__(self):
        pass

    def cmd_to_action(self, cmd):
        return (None, None, None)


class TestGame(GameConf):
    def __init__(self):
        # (PS: 方 叉 圈 三角 L1 R1 L2 R2)(值: 0x01 0x02 0x04 0x08 0x10 0x20 0x40 0x80)
        self._KEYBOND = {
            'SKILL_BTN': ('BTN', b'\x01'),
            'JUMP_BTN': ('BTN', b'\x02'),
            'ATTACK_BTN': ('BTN', b'\x04'),
            'L_ROCKER': ('L_ROCKER', None),
        }
        self._ACTION = {
            'TAP': self._KEYBOND['ATTACK_BTN'] + ('CLICK',),
            'SK': self._KEYBOND['ATTACK_BTN']+('CLICK',),
            'LB': self._KEYBOND['JUMP_BTN']+('CLICK',),
            'RB': self._KEYBOND['SKILL_BTN']+('CLICK',),
            'AN': self._KEYBOND['L_ROCKER']+('PRESS',),  # 左摇杆
        }

    def cmd_to_action(self, cmd):
        return self._ACTION[cmd]


class Genshin(GameConf):
    def __init__(self):
        self._cross_index = 0
        # (PS: 方 叉 圈 三角 L1 R1 L2 R2)(值: 0x01 0x02 0x04 0x08 0x10 0x20 0x40 0x80)
        self._GENSHIN_KEYBOND = {
            'ALL_BTN': ('BTN', b'\x00'),
            'ATTACK_BTN': ('BTN', b'\x04'),
            'JUMP_BTN': ('BTN', b'\x02'),
            'HOLY_BTN': ('BTN', b'\x08'),
            'SKILL_TRIGGER': ('BTN', b'\x80'),
            'CROSS_UP_BTN': ('CROSS', b'\x00'),
            'CROSS_RIGHT_BTN': ('CROSS', b'\x02'),
            'CROSS_DOWN_BTN': ('CROSS', b'\x04'),
            'CROSS_LEFT_BTN': ('CROSS', b'\x06'),
            'L_ROCKER': ('L_ROCKER', None),
            'R_ROCKER': ('R_ROCKER', None),
        }
        
        '''
        左右按钮：换人
        来回甩剑：普通攻击
        挡住颜色传感器：走位
        压力传感器：E技能/元素战技（点按、长按）
        挡住距离传感器按压力传感器：Q技能/元素爆发
        其他：
        -重击：遮挡颜色传感器长按压力传感器
        -跳跃：遮挡颜色传感器按左按钮（以便于跑同时跳）
        -调整视角：遮挡距离传感器
        补充：
        遮挡颜色传感器按右按钮：E技能/元素战技
        '''
        self.GENSHIN_ACTION = {
            'TAP': self._GENSHIN_KEYBOND['ATTACK_BTN'] + ('CLICK',),  # 普通攻击
            'SK': self._GENSHIN_KEYBOND['ATTACK_BTN']+('CLICK',),  # 普通攻击
            'CLA': self._GENSHIN_KEYBOND['JUMP_BTN']+('CLICK',),  # 跳
            'CRA': self._GENSHIN_KEYBOND['SKILL_TRIGGER']+('CLICK',),  # 技能短按
            'FS': self._GENSHIN_KEYBOND['SKILL_TRIGGER']+('PRESS',),  # 技能，扳机，可长按
            'DFA': self._GENSHIN_KEYBOND['HOLY_BTN']+('PRESS',),  # 必杀技
            'CFA': self._GENSHIN_KEYBOND['ATTACK_BTN']+('PRESS',),  # 攻击，可长按（重击）
            'C+A': self._GENSHIN_KEYBOND['L_ROCKER']+('PRESS',),  # 左摇杆，角色移动
            'D+A': self._GENSHIN_KEYBOND['R_ROCKER']+('PRESS',),  # 右摇杆，视角移动
            'CSR': self._GENSHIN_KEYBOND['L_ROCKER']+('RETURN',),  # 左摇杆回正
            'DSR': self._GENSHIN_KEYBOND['R_ROCKER']+('RETURN',),  # 右摇杆回正
            'FSR': self._GENSHIN_KEYBOND['ALL_BTN']+('RELEASE',),  # 松开所有按键(取消长按)
            # 'CLA': self._GENSHIN_KEYBOND['CROSS_X_BTN']+('CLICK',),  # 换人（正顺序）
            # 'CRA': self._GENSHIN_KEYBOND['CROSS_X_BTN']+('CLICK',),  # 换人（反顺序）
            'CROSS_UP': self._GENSHIN_KEYBOND['CROSS_UP_BTN']+('CLICK',),  # 换人
            'CROSS_DOWN': self._GENSHIN_KEYBOND['CROSS_DOWN_BTN']+('CLICK',),
            'CROSS_LEFT': self._GENSHIN_KEYBOND['CROSS_LEFT_BTN']+('CLICK',),
            'CROSS_RIGHT': self._GENSHIN_KEYBOND['CROSS_RIGHT_BTN']+('CLICK',),
        }

    def cmd_to_action(self, cmd):
        if cmd == 'LB':
            self._cross_index += 1
        if cmd == 'RB':
            self._cross_index -= 1
        if self._cross_index >= 4:
            self._cross_index = 0
        if self._cross_index <= -1:
            self._cross_index = 3
        if cmd == 'LB' or cmd == 'RB':
            cmd = ['CROSS_UP', 'CROSS_RIGHT', 'CROSS_LEFT',
                   'CROSS_DOWN'][self._cross_index]
            print(cmd)
        return self.GENSHIN_ACTION[cmd]


class TheWitcher(GameConf):
    def __init__(self):
        # (PS: 方 叉 圈 三角 L1 R1 L2 R2)(值: 0x01 0x02 0x04 0x08 0x10 0x20 0x40 0x80)
        self._THEWITCHER_KEYBOND = {
            'ALL_BTN': ('BTN', b'\x00'),
            'ATTACK_BTN': ('BTN', b'\x01'),
            'JUMP_BTN': ('BTN', b'\x04'),
            'HEAVY_ATTACK_BTN': ('BTN', b'\x08'),
            'SKILL_TRIGGER': ('BTN', b'\x80'),
            'CROSS_RIGHT_BTN': ('CROSS', b'\x02'),
            'CROSS_LEFT_BTN': ('CROSS', b'\x06'),
            'L_ROCKER': ('L_ROCKER', None),
            'R_ROCKER': ('R_ROCKER', None),
        }
        self.THEWITCHER_ACTION = {
            'TAP': self._THEWITCHER_KEYBOND['ATTACK_BTN'] + ('CLICK',),  # 普通攻击
            'SK': self._THEWITCHER_KEYBOND['ATTACK_BTN']+('CLICK',),  # 普通攻击
            'LB': self._THEWITCHER_KEYBOND['JUMP_BTN']+('CLICK',),  # 跳
            'RB': self._THEWITCHER_KEYBOND['JUMP_BTN']+('CLICK',),  # 跳
            # 技能，扳机
            'FS': self._THEWITCHER_KEYBOND['SKILL_TRIGGER']+('PRESS',),
            # 重击
            'CFA': self._THEWITCHER_KEYBOND['HEAVY_ATTACK_BTN']+('PRESS',),
            'FSR': self._THEWITCHER_KEYBOND['ALL_BTN']+('RELEASE',),  # 松开所有按键
            # 换刀1
            'CLA': self._THEWITCHER_KEYBOND['CROSS_LEFT_BTN']+('CLICK',),
            # 换刀2
            'CRA': self._THEWITCHER_KEYBOND['CROSS_RIGHT_BTN']+('CLICK',),
            'C+A': self._THEWITCHER_KEYBOND['L_ROCKER']+('PRESS',),  # 左摇杆，角色移动
            'D+A': self._THEWITCHER_KEYBOND['R_ROCKER']+('PRESS',),  # 右摇杆，视角移动
            'CSR': self._THEWITCHER_KEYBOND['L_ROCKER']+('RETURN',),  # 左摇杆回正
            'DSR': self._THEWITCHER_KEYBOND['R_ROCKER']+('RETURN',),  # 右摇杆回正
        }

    def cmd_to_action(self, cmd):
        return self.THEWITCHER_ACTION[cmd]

