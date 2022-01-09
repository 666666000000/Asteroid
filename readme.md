## 说明
所有功能在使用前要先加载对应的模块</br>

## 快捷键
快捷键在`shortcut.txt`内设置</br>

### 局部快捷键
`↑` 显示上一条命令</br>
`↓` 显示下一条命令</br>
`esc` 如果当前不在普通模式，退出当前所在模式，回到普通模式</br>
`ctrl+n` 切换到普通模式</br>
`ctrl+space` 在当前模式和前一个模式间来回切换</br>
`ctrl+backspace` 清空输入框</br>

### 全局快捷键

`alt+c` 复制所选内容并召出输入框</br>
`alt+v` 截屏</br>
`alt+b` 复制当前文件夹路径（等于 `alt+d`和`ctrl+c`的组合）</br>
`alt+n` 复制所选文件路径（等于 `alt+3`，`alt+3` 这个快捷键需要将`复制路径`添加到`快速访问工具栏` ）</br>
`alt+space` 召出输入框</br>

#### 命令
`run` 执行多条命令</br>
`lm l` 打印所有模块名及加载情况</br>
`lm` 加载所有模块</br>
`lm n` 加载软件启动后新复制到module文件夹内的模块</br>
`lm name` 按名称加载模块</br>
`lm -name` 在模块列表里搜索name并加载</br>
`lm a/b/c` 加载a/b/c标记的模块</br>
`lm index` 加载第index个模块</br>
`kw` 打印可用命令</br>
`kw command` 查找命令所在模块</br>
`h` 隐藏输入框</br>
`q` 退出程序</br>


`*` *表示从剪贴板读取内容，可以作为源也可以作为目标</br>
`s` 标记所选路径为源路径，可以是文件、文件夹或字符串</br>
`ss` 追加所选路径到源路径</br>
`d` 标记所选路径为目标路径，只能是文件夹</br>
`dd` 追加所选路径到目标路径</br>
`t` 标记路径，可以作为源也可以作为目标，可以是文件、文件夹或字符串</br>
`tt` 追加所选路径到t标记的路径</br>


`ad` 添加进字典，同名时会覆盖原路径</br>
`ap` 追加进字典</br>
`clr` 清空字典</br>
`del` 按名称删除一条记录或所有记录</br>
`list` 打印字典</br>
`sp` 保存字典到硬盘</br>

`index` 设置全局序号</br>
`dp` 设置下载路径</br>
`gd` 从字典复制路径到剪贴板</br>

### 模块及功能


`alarmClock`</br>
{'ac'}</br>
闹钟</br>

`bar`</br>
{'bar'}</br>
从剪贴板、文本批量生成条码</br>

`barXLSX`</br>
{'bar'}</br>
从文本、表格批量生成条码</br>

`dbar`</br>
{'dbar'}</br>
从桌面、图片、摄像头扫描条码</br>

`download`</br>
{'dl', 'aa'}</br>
调用命令行下载器，RPC添加Aria2c下载任务，接收浏览器批量下载</br>

`dqr`</br>
{'dqr'}</br>
从桌面、图片、摄像头扫描二维码</br>

`ffmpeg`</br>
{'mv', 'ff', 'sc'}</br>
调用ffmpeg拼接视频、场景切割、批量转换视频</br>

`manageFile`</br>
{'cp', 'ms', 'nf', 'nd', 'enc', 'dec', 'zip', 'uzip', 'ftp', 'dav', 'm5', 's1', 's2', 's3', 's5', 'r1', 'rn'}</br>
复制文件，镜像同步文件夹，新建文件或文件夹，加密解密文件，压缩解压缩文件，ftp/dav上传文件，Hash文件，批量重命名</br>

`manageHistory`</br>
{ 'saveh', 'loadh', 'clearh'}</br>
保存、加载、清空命令历史</br>

`ocr`</br>
{'ocr'}</br>
从剪贴板、图片、桌面、摄像头识别文字</br>

`wocr`</br>
{'wocr'}</br>
从剪贴板、图片、桌面识别文字（网络版）</br>

`opencvImage`</br>
{'cmap', 'den', 'sa'}</br>
图片转伪彩、降噪,读取摄像头保存到文件</br>

`pdf`</br>
{'mpdf'}</br>
合并pdf</br>

`pillowImage`
{'rs', 'ro', 'crop', 'gray', 'wm', 'cut'}</br>
图片批量缩放、旋转、裁剪、转灰度、加水印、裁切</br>

`printScreen`</br>
{'ps', 'pc', 'gs'}</br>
屏幕截图，拾色，获取屏幕区域尺寸</br>

`qr`</br>
{'qr'}</br>
从剪贴板、文本批量生成二维码</br>

`qrXLSX`</br>
{'qr'}</br>
从文本、表格批量生成二维码</br>

`qtAlarmClock`</br>
{'qac'}</br>
qt界面的闹钟</br>

`recvFile`</br>
{'rf'}</br>
局域网接收文件</br>

`removeWaterMark`</br>
{'rwm'}</br>
Opencv去水印</br>

`saveAs`</br>
{'sa'}</br>
保存剪贴板、桌面到文件</br>

`saveAsXLSX`</br>
{'sa'}</br>
从剪贴板读取数据保存到XLSX文件</br>

`sendFile`</br>
{'sf'}</br>
局域网发送文件</br>

`showKey`</br>
{'hk', 'kh', 'mh'}</br>
显示键盘按键或鼠标按键</br>

`ssh ssh #000000 Control-s`</br>
{'ex', 'bex', 'ssh'}</br>
SSH客户端</br>

`timeCount`</br>
{'tc', 'cd', 'ck'}</br>
计时、倒计时、时钟</br>

`tool`</br>
{'ca', 'pa', '<', '>', '2', '8', '10', '16', 'cal', 'e64', 'd64', '@', '￥', '$', 'gj', 'cq'}</br>
在所选文件夹打开cmd或powershell，运行cmd命令，进制转换，计算器，base64编码解码，打开常用网站或搜索关键字，定时关机或重启</br>

`txt txt #d2fc69 Control-t`</br>
{'wt'}</br>
写txt</br>

`vlc vlc #f57d00 Control-m`</br>
{'vlc'}</br>
控制VLC播放器</br>


