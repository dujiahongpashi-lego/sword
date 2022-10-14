// http://robotjs.io/docs/
// 乐高HUB事件 转换为鼠标事件
const robot = require("robotjs")

const eventParser = (event, data) => {
    if (event == 'SHAKE' || event == 'TAP') {
        // robot.mouseClick()
        robot.mouseToggle('down')
        robot.mouseToggle('up')
    }
    else if (event == 'BUTTON_CLICK') {
        // 默认倒持乐高，（乐高按键和映射的鼠标按键）左右互换
        button = data[0] == 'left' ? 'right' : 'left' 
        if (data[1] == 0) {
            robot.mouseToggle('down', button)
        }
        else {
            robot.mouseToggle('up', button)
        }
    }
    else if (event == 'MOVE') {
        mouse = robot.getMousePos()
        const [x, y] = data
        // console.log(x, y)
        // 灵敏度(Motino to Dots Per Inch)(类似DPI)调节
        robot.moveMouse(mouse.x + x, mouse.y + y)
    }
}

exports.fakeHID = eventParser