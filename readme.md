## 各模块可用命令及功能

`alarmClock:`</br>
ac</br>
闹钟</br>

`autoWrite:`</br>
w</br>
自动输出预设的文本</br>

`bar:`</br>
bar</br>
从剪贴板、文本批量生成条码</br>

`barXLSX:`</br>
bar</br>
从文本、表格批量生成条码</br>

`calculator:`</br>
cal</br>
计算器</br>

`core:`</br>
t, printClip, clr, sleep, tt, index, ls, dd, dp, ss, d, ap, gd, /, e, sp, s, del, ad</br>
操作常用路径及临时路径</br>


`dbar:`</br>
dbar</br>
从桌面、图片、摄像头扫描条码</br>

`download:`</br>
aa, du, dl</br>
批量下载</br>


`dqr:`</br>
dqr
从桌面、图片、摄像头扫描二维码</br>

`extract:`</br>
rem, ret, ext</br>
提取html元素</br>

`ffmpeg:`</br>
mv, ff, fft, sc, fu</br>
调用ffmpeg批量操作视频</br>

`log:`</br>
log</br>
写文件</br>

`ocr:`</br>
ocr</br>
从剪贴板、图片、桌面、摄像头识别文字</br>

`opencv:`</br>
den, sa, cmap</br>
图片转伪彩、降噪,读取摄像头保存到文件</br>

`pdf:`</br>
mpdf</br>
合并pdf</br>

`pillow:`</br>
merge, blur, ro, g2s, s2g, crop, gray, wm, cut, unis, rs</br>
图片批量缩放、旋转、转灰度、模糊、裁剪、加水印、裁切、统一尺寸、合并、gif转图片序列、图片序列转gif</br>

`preview:`</br>
ve, view, vap</br>
预览图片</br>

`printScreen:`</br>
ps, pc, gs</br>
屏幕截图，拾色，获取屏幕区域尺寸</br>

`processFile:`</br>
cp, s2, s3, s5, ms, nd, enc, r1, rn, uzip, dec, s1, nf, m5, zip</br>
复制文件，镜像同步文件夹，新建文件或文件夹，加密解密文件，压缩解压缩文件，计算文件Hash，批量重命名</br>

`processHistory:`</br>
saveh, clearh, loadh</br>
保存、加载、清空命令历史</br>

`qr:`</br>
qr</br>
从剪贴板、文本批量生成二维码</br>

`qrXLSX:`</br>
qr</br>
从文本、表格批量生成二维码</br>

`recvFile:`</br>
rf</br>
局域网接收文件</br>

`removeWatermark:`</br>
rwm</br>
Opencv去水印</br>

`saveAs:`</br>
sa</br>
保存剪贴板、桌面到文件</br>

`saveAsXLSX:`</br>
sa</br>
从剪贴板读取数据保存到XLSX文件</br>

`search:`</br>
f, df</br>
搜索桌面及指定文件夹内的文件</br>

`sendFile:`</br>
sf</br>
局域网发送文件</br>

`showKey:`</br>
mh, kh, hk</br>
显示键盘按键或鼠标按键</br>

`ssh:`</br>
ssh</br>
SSH客户端</br>

`timeCount:`</br>
tc, ck, cd</br>
计时、倒计时、时钟</br>

`todo:`</br>
td</br>
待办</br>


`tool:`</br>
self, <, 16, col, lower, ., upper, $, header, e64, d64, num, 10, 2, str, 8, >, ￥, substr, @, inner, exec</br>
运行cmd、powershell命令，进制转换，base64编码解码，快捷打开网址，快捷搜索，快捷打开系统设置，生成随机字符串，截取字符串，提取字符串的某一列，加行号，生成请求头，提取html文本，转大小写，执行python代码片段，关机，重启</br>

`vlc:`</br>
vlc</br>
控制VLC播放器</br>

`webOcr:`</br>
wocr</br>
网络ocr客户端</br>

## 依赖包
`Asteriod:`</br>
pywin32</br>
keyboard</br>

`bar:`</br>
python-barcode</br>

`baxXLSX:`</br>
python-barcode</br>
openpyxl</br>

`dbar:`</br>
opencv-python</br>
numpy</br>
pyzbar</br>

`download:`</br>
requests</br>

`dqr:`</br>
opencv-python</br>
opencv-contrib-python</br>

`ocr:`</br>
opencv-python</br>
pytesseract</br>
numpy</br>

`opencv:`</br>
opencv-python</br>
numpy</br>


`pdf:`</br>
PyPDF2</br>

`printScreen:`</br>
pywin32</br>

`qr:`</br>
qrcode</br>

`qrXLSX:`</br>
qrcode</br>
openpyxl</br>

`removeWaterMark:`</br>
opencv-python</br>
numpy</br>

`saveAsXLSX:`</br>
openpyxl</br>

`showKey:`</br>
keyboard</br>
mouse</br>

`ssh:`</br>
paramiko</br>

`webOcr:`</br>
zerorpc</br>


### 局部快捷键
`↑` 显示上一条命令</br>
`↓` 显示下一条命令</br>
`esc` 如果当前不在普通模式，退出当前所在模式，回到普通模式</br>
`ctrl+n` 切换到普通模式</br>
`ctrl+m` 在当前模式和前一个模式间来回切换</br>
`ctrl+backspace` 清空输入框</br>

### 全局快捷键

`alt+c` 复制所选内容并召出输入框</br>
`alt+v` 截屏</br>
`alt+b` 复制当前文件夹路径（等于 `alt+d`和`ctrl+c`的组合）</br>
`alt+n` 复制所选文件路径（等于 `alt+3`，`alt+3` 这个快捷键需要将`复制路径`添加到`快速访问工具栏`,win11可以使用ctrl+shift+c ）</br>
`alt+space` 召出输入框</br>

#### 命令
`run` 执行多条命令</br>
`i l` 打印所有模块名及加载情况</br>
`i` 加载所有模块</br>
`i n` 加载软件启动后新复制到module文件夹内的模块</br>
`i name` 按名称加载模块</br>
`i -name` 在模块列表里搜索name并加载</br>
`i a/b/c` 加载a/b/c标记的模块</br>
`i index` 加载第index个模块</br>
`cmd` 打印可用命令</br>
`cmd command` 查找命令所在模块</br>
`h` 隐藏输入框</br>
`q` 退出程序</br>


`*` 表示从剪贴板读取内容，可以作为源也可以作为目标</br>
`s` 标记所选路径为源路径，可以是文件、文件夹或字符串</br>
`ss` 追加所选路径到源路径</br>
`d` 标记所选路径为目标路径，只能是文件夹</br>
`dd` 追加所选路径到目标路径</br>
`t` 标记路径，可以作为源也可以作为目标，可以是文件、文件夹或字符串</br>
`tt` 追加所选路径到t标记的路径</br>

`self` 打开脚本所在文件夹</br>
`ad` 添加进字典，同名时会覆盖原路径</br>
`ap` 追加进字典</br>
`clr` 清空字典</br>
`del` 按名称删除一条记录或所有记录</br>
`ls` 打印字典</br>
`sp` 保存字典到硬盘</br>

`index` 设置全局序号</br>
`dp` 设置下载路径</br>
`gd` 从字典复制路径到剪贴板</br>

