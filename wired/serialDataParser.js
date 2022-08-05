const { fakeHID } = require('./fakeHID')

const parseMotors = (motors) => {
    let m = motors.map((motor, index) => {
        const cmd = ['MOTOR_1_ROLL', 'MOTOR_2_ROLL', 'MOTOR_3_ROLL', 'MOTOR_4_ROLL'][index] // 最多支持4个电机（因为我只有4个电机,后面的就不写了）按ABCDEF排号
        const speed = motor[1][0]
        return { cmd, speed }
    })
    m = m.filter(motor => motor.speed > 5 || motor.speed < -5)
    if (m.length == 0) {
        return { cmd: '', payload: 0 }
    }
    return { cmd: m[0].cmd, payload: m[0].speed }
}

const parseEvent = (eventNo, data) => {
    eventsMap = {
        0: 'DEFAULT',// 'MOTOR_1_ROLL', 'MOTOR_2_ROLL', 'MOTOR_3_ROLL', 'MOTOR_4_ROLL'
        2: 'BATTARY_STATE',
        3: 'BUTTON_CLICK', // 左右按键
        4: 'TAP', // 拍击、小摇晃 
        14: 'SHAKE' // 大摇晃
    }

    currentEvent = eventsMap[eventNo]
    let cmd = currentEvent
    let payload = data
    if (currentEvent == 'DEFAULT') {
        const [portA, portB, portC, portD, portE, portF, motionAngle] = data

        // 判断是否是电机事件
        const ports = [portA, portB, portC, portD, portE, portF]
        motors = ports.filter(port => port[0] == 75)// 75代表电机插入了对应的PORT（其他数字应该代表其他传感器，我没试）
        const { cmd: motorCmd, payload: motorSpeed } = parseMotors(motors)
        if (motorSpeed != 0) {
            return { cmd: motorCmd, payload: motorSpeed }
        }

        // 判断是否是角度倾斜事件


    }
    return {
        cmd,
        payload
    }
}

const dataParser = (line) => {

    const { m, p } = JSON.parse(line)

    // if (m == 0) console.log(line)
    const { cmd, payload } = parseEvent(m, p)
    if (cmd != 'DEFAULT' && cmd != 'BATTARY_STATE') {
        fakeHID(cmd, payload)
    }
}

exports.dataParser = dataParser
