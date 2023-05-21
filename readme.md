## 2023年之前的视频里的功能和现有功能有部分区别

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

