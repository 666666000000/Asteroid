## 快捷键
快捷键在`shortcut.txt`内设置

### 局部快捷键
`↑` 显示上一条命令
`↓` 显示下一条命令
`esc` 如果当前不在普通模式，退出当前所在模式，回到普通模式
`ctrl+n` 切换到普通模式
`ctrl+space` 在当前模式和前一个模式间来回切换
`ctrl+backspace` 清空输入框

### 全局快捷键

`alt+c` 复制所选内容并召出输入框
`alt+v` 截屏
`alt+b` 复制当前文件夹路径（等于 `alt+d`和`ctrl+c`的组合）
`alt+n` 复制所选文件路径（等于 `alt+3`，`alt+3` 这个快捷键需要将`复制路径`添加到`快速访问工具栏` ）
`alt+space` 召出输入框

#### 命令
`run` 执行多条命令
`lm l` 打印所有模块名及加载情况
`lm` 加载所有模块
`lm n` 加载软件启动后新复制到module文件夹内的模块
`lm name` 按名称加载模块
`lm -name` 在模块列表里搜索name并加载
`lm a/b/c` 加载a/b/c标记的模块
`lm index` 加载第index个模块
`kw` 打印可用命令
`kw command` 查找命令所在模块
`h` 隐藏输入框
`q` 退出程序


`*` *表示从剪贴板读取内容，可以作为源也可以作为目标
`s` 标记所选路径为源路径，可以是文件、文件夹或字符串
`ss` 追加所选路径到源路径
`d` 标记所选路径为目标路径，只能是文件夹
`dd` 追加所选路径到目标路径
`t` 标记路径，可以作为源也可以作为目标，可以是文件、文件夹或字符串
`tt` 追加所选路径到t标记的路径


`ad` 添加进字典，同名时会覆盖原路径
`ap` 追加进字典
`clr` 清空字典
`del` 按名称删除一条记录或所有记录
`list` 打印字典
`sp` 保存字典到硬盘

`index` 设置全局序号
`dp` 设置下载路径
`gd` 从字典复制路径到剪贴板

### 模块及功能


`alarmClock`
{'ac'}
闹钟

`bar`
{'bar'}
从剪贴板、文本批量生成条码

`barXLSX`
{'bar'}
从文本、表格批量生成条码

`dbar`
{'dbar'}
从桌面、图片、摄像头扫描条码

`download`
{'dl', 'aa'}
调用命令行下载器，RPC添加Aria2c下载任务，接收浏览器批量下载

`dqr`
{'dqr'}
从桌面、图片、摄像头扫描二维码

`ffmpeg`
{'mv', 'ff', 'sc'}
调用ffmpeg拼接视频、场景切割、批量转换视频

`manageFile`
{'cp', 'ms', 'nf', 'nd', 'enc', 'dec', 'zip', 'uzip', 'ftp', 'dav', 'm5', 's1', 's2', 's3', 's5', 'r1', 'rn'}
复制文件，镜像同步文件夹，新建文件或文件夹，加密解密文件，压缩解压缩文件，ftp/dav上传文件，Hash文件，批量重命名

`manageHistory`
{ 'saveh', 'loadh', 'clearh'}
保存、加载、清空命令历史

`ocr`
{'ocr'}
从剪贴板、图片、桌面、摄像头识别文字

`opencvImage`
{'cmap', 'den', 'sa'}
图片转伪彩、降噪,读取摄像头保存到文件

`pdf`
{'mpdf'}
合并pdf

`pillowImage`
{'rs', 'ro', 'crop', 'gray', 'wm', 'cut9'}
图片批量缩放、旋转、裁剪、转灰度、加水印、九宫格

`printScreen`
{'ps', 'pc', 'gs'}
屏幕截图，拾色，获取屏幕区域尺寸

`qr`
{'qr'}
从剪贴板、文本批量生成二维码

`qrXLSX`
{'qr'}
从文本、表格批量生成二维码

`qtAlarmClock`
{'qac'}
qt界面的闹钟

`recvFile`
{'rf'}
局域网接收文件

`removeWaterMark`
{'rwm'}
Opencv去水印

`saveAs`
{'sa'}
保存剪贴板、桌面到文件

`saveAsXLSX`
{'sa'}
从剪贴板读取数据保存到XLSX文件

`sendFile`
{'sf'}
局域网发送文件

`showKey`
{'hk', 'kh', 'mh'}
显示键盘按键或鼠标按键

`ssh ssh #000000 Control-s`
{'ex', 'bex', 'ssh'}
SSH客户端

`timeCount`
{'tc', 'cd', 'ck'}
计时、倒计时、时钟

`tool`
{'ca', 'pa', '<', '>', '2', '8', '10', '16', 'cal', 'e64', 'd64', '@', '￥', '$', 'gj', 'cq'}
在所选文件夹打开cmd或powershell，运行cmd命令，进制转换，计算器，base64编码解码，打开常用网站或搜索关键字，定时关机或重启

`txt txt #d2fc69 Control-t`
{'wt'}
写txt

`vlc vlc #f57d00 Control-m`
{'vlc'}
控制VLC播放器


