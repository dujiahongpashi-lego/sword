// http://robotjs.io/docs/
const robot = require("robotjs")

const eventParser = (event, data) => {
    console.log(event, data)
    if (event == 'SHAKE' || event == 'TAP') {
        // robot.mouseClick()
        robot.mouseToggle('down')
        robot.mouseToggle('up')
    } 
    else if (event == 'BUTTON_CLICK') {
        button = data[0] == 'left' ? 'right' : 'left' // 默认倒持乐高，（乐高按键和映射的鼠标按键）左右互换
        if (data[1] == 0) {
            robot.mouseToggle('down', button)
        }
        else {
            robot.mouseToggle('up', button)
        }

    }
}

exports.fakeHID = eventParser