// 运行前需要关闭其他工具（如MINDSTORMS APP）对乐高USB串口连接的占用
// 启动命令 node .\index.js
// https://serialport.io/docs/guide-usage
const LEGO_SERIAL_PORT = 'COM3'
const { SerialPort, ReadlineParser } = require('serialport')
const { dataParser } = require('./serialDataParser')

SerialPort.list().then((ports) => {
    console.log(ports);
}).catch((err) => {
    console.log(err);
});

const port = new SerialPort({ path: LEGO_SERIAL_PORT, baudRate: 38400 }, function (err) {
    if (err) {
        return console.log('Error: ', err.message)
    }
});

const parser = port.pipe(new ReadlineParser({ delimiter: '\r' }))
//parser.on('data', console.log)
parser.on('data', dataParser)