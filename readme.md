## 说明
所有功能在使用前要先加载对应的模块：在使用 `ff` 命令前要先加载 `ffmpeg` 模块</br>
手动加载：`lm ffmpeg`，自动加载在`config.txt`内设置，模块只需要加载一次</br>

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
`i l` 打印所有模块名及加载情况</br>
`i` 加载所有模块</br>
`i n` 加载软件启动后新复制到module文件夹内的模块</br>
`i name` 按名称加载模块</br>
`i -name` 在模块列表里搜索name并加载</br>
`i a/b/c` 加载a/b/c标记的模块</br>
`i index` 加载第index个模块</br>
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

### dav.bat
以dav方式上传文件会调用这个脚本</br>

### ftp.bat
以ftp方式上传文件会调用这个脚本</br>

### sync.bat
镜像同步时调用这个脚本</br>

### config.txt
保存一些设置</br>

### downloadPreset.txt
预设的命令行下载命令</br>

### ffmpegPreset.txt
预设的ffmpeg命令</br>

### sshPreset.txt
预设的ssh命令</br>

### pathDict.txt
保存的路径</br>

### search.txt
用短名称搜索的网址</br>

### web.txt
用短名称打开的网址</br>

### history.txt
保存命令记录</br>

### 模块名及命令
所有功能模块位于`module`文件夹内</br>

### ffmpeg
调用ffmpeg</br>

#### 命令
`sc` 场景切割</br>
`mv` 合并视频</br>
`ff` 按`ffmpegPerset.txt`里预设的命令批量处理视频，有两种命令格式</br>
1. `ff id src dst`</br>
2. `ff id src @loop dst` 第四个参数表输入的文件要循环使用，以`@`开头，如水印文件</br>
   
选中的源文件会按文件类型分类后依次填充进命令，一条命令所需要的源文件填充完后，剩下的源文件会循环填充同一条命令，最后依次执行所有命令，将`ffmpegPerset.txt`第一行parallel后面的`false`改为`true` 会并行运行所有命令</br>
`InputImage`填充一张图片路径</br>
`InputImage*0`填充所有图片路径</br>
`InputImage*2`填充两图片路径</br>
`InputImage*-1`循环填充一张源图片路径</br>



### download
调用命令行下载器或aria2c的远程下载</br>

#### 命令
`dl` 调用`downloadPerset.txt`里预设的命令</br>
`aa` 以`rpc`方式调用`aria2c`进行下载</br>

`aa` 从剪贴板读取链接或种子文件并发送到`aria2c`，默认会下载到`aria2c`配置的下载路径</br>
`aa dstpath` 从剪贴板读取链接或种子文件并发送到`aria2c`，下载到`dstpath`</br>
`aa on` 开启一个udp端口，接收来自浏览器的批量下载，下载路径是用`dp`命令设置的路径</br>
`aa off` 关闭udp端口</br>

### ssh
SSH客户端，包含文件上传下载</br>

#### 命令
`ssh` 进入ssh模式</br>
`con` 连接主机</br>
`dis` 断开连接</br>
`put` 上传文件</br>
`get` 下载文件</br>
`cm` 切换到其它模式</br>
`ex` 执行剪贴板里的命令，不能替换命令里的参数</br>
`ex r` 重新加载`sshPreset.txt`</br>
`ex l` 打印`sshPreset.txt`的命令</br>
`ex l key` 打印`key`下面的命令</br>
`ex *` 从剪贴板读取命令，同时可以替换命令里的参数</br>
`ex key` 执行`key`下面的命令</br>
`ex key@index` 执行`key`下面的第`index`条命令</br>
`bex iplist key` 批量执行命令</br>
其它的输入会被当成命令发送的远程主机</br>

### alarmClock
闹钟</br>

#### 命令
`ac` 查看闹钟状态</br>
`ac l` 打印所有闹钟</br>
`ac r` 重新加载闹钟列表</br>
`ac on` 启动闹钟</br>
`ac off` 停止闹钟</br>


### qtAlarmClock
pyqt5界面的闹钟，功能同上</br>

#### 命令
`qac`

### timeCount
计时器、倒计时、时钟</br>

#### 命令
`tc` 启动一个新的计时器</br>
`cd time` 启动一个新的倒计时</br>
`ck` 显示时钟</br>

#### 可选参数
`m` 毫秒计时</br>
`fs` 窗口全屏</br>
`st` 倒计时归零后停止计时，默认会反向计时</br>
`tp` 窗口置顶</br>


#### 快捷键
`左键双击` 重置计时或倒计时</br>
`esc` 功能同上</br>
`右键` 停止或启动计时\倒计时\时钟</br>
`空格` 功能同上</br>
`回车` 全屏或退出全屏</br>
`+` 复制当前时间到一个列表，重置会清空列表</br>



### bar
从剪贴板、文本批量生成条码</br>
编码类型：code128, code39, ean, ean13, ean14, ean8, gs1, gs1_128, gtin, isbn, isbn10, isbn13, issn, itf, jan, pzn, upc, upca</br>
#### 命令
`bar code` 从剪贴板读取内容生成`code`编码的条码并显示在输入框下面，右键保存条码，保存时需要选择目标路径，左键双击关闭</br>
`bar code dstpath` 功能同上，在保存条码时保存到`dstpath`，不用选择保存路径</br>
`bar code * dstpath` 从剪贴板读取内容批量生成条码并保存到`dstpath`，不会显示条码</br>
`bar code f dstpath` 从剪贴板读取文件路径，读取文件内容批量生成条码并保存到`dstpath`，不会显示条码，文件只能是`txt`</br>

### barXLSX
从文本、表格批量生成条码</br>

#### 命令
`bar code f dstpath` 默认条码内容和保存的文件名都是第一列，按所有行生成条码</br>
`bar code f dstpath strColumn` 指定条码的内容列</br>
`bar code f dstpath strColumn nameColumn` 指定条码的内容列和保存的文件名所用的列</br>
`bar code f dstpath strColumn nameColumn startRow` 从`startRow`到最后一行生成条码</br>
`bar code f dstpath strColumn nameColumn startRow endRow` 从`startRow`到`endRow`生成条码</br>

### dbar
从桌面、图片、摄像头扫描条码,二维码</br>

#### 命令
`dbar` 从桌面扫描条码/二维码</br>
`dbar f` 从剪贴板读取图片路径并从图片扫描条码/二维码</br>
`dbar c` 打开摄像头扫描条码/二维码</br>

### qr
从剪贴板、文本批量生成二维码</br>

#### 命令
`qr` 从剪贴板读取内容生成二维码并显示在输入框下面，右键保存二维码，保存时需要选择目标路径，左键双击关闭</br>
`qr dstpath` 功能同上，在保存条码时保存到dstpath，不用选择保存路径</br>
`qr * dstpath` 从剪贴板读取内容生成一个二维码并保存到`dstpath`，不会显示二维码</br>
`qr ** dstpath` 从剪贴板读取内容按行批量生成二维码并保存到`dstpath`，不会显示二维码</br>
`qr f dstpath` 从剪贴板读取文件路径，读取文件内容批量生成二维码并保存到`dstpath`，不会显示二维码，文件只能是`txt`</br>

### qrXLSX
从文本、表格批量生成二维码</br>

#### 命令
`qr f dstpath` 默认二维码内容和保存的文件名都是第一列，按所有行生成二维码</br>
`qr f dstpath strColumn` 指定二维码的内容列</br>
`qr f dstpath strColumn nameColumn` 指定二维码的内容列和保存的文件名所用的列</br>
`qr f dstpath strColumn nameColumn startRow` 生成从`startRow`到最后一行的二维码</br>
`qr f dstpath strColumn nameColumn startRow endRow` 生成从`startRow`到`endRow`的二维码</br>

### dqr
从桌面、图片、摄像头扫描二维码</br>

#### 命令
`dqr` 截取桌面扫描二维码</br>
`dqr f` 从剪贴板读取图片路径并从图片扫描二维码</br>
`dqr c` 打开摄像头扫描二维码</br>

### ocr
从剪贴板、图片、桌面、摄像头识别文字（调用tesseract）</br>

#### 命令
`ocr` 从剪贴板读取图片按中文简体识别</br>
`ocr ct` 从剪贴板读取图片按中文繁体识别</br>
`ocr en` 从剪贴板读取图片按英文识别</br>
`ocr f` 从剪贴板读取图片路径按中文简体识别</br>
`ocr s` 截取桌面按中文简体识别</br>
`ocr c` 打开摄像头按中文简体识别</br>
`ocr f/s/c ct/en` 从图片或桌面或摄像头按繁体或英文识别文字</br>


### saveAs
保存剪贴板、桌面到文件</br>

#### 命令
`sa d\1.jpg` 从剪贴板读取图片保存到`d`标记的路径</br>
`sa d\<i>.txt` 从剪贴板读取文本保存到`d`标记的路径，`<i>`会被全局序号替换</br>
`sa d\<i>.jpg s` 保存桌面到`d`标记的路径</br>
`sa d\<i>.jpg c` 抓取摄像头保存到`d`标记的路径，要先加载opencvImage模块，按回车保存图片</br>
`sa d\<i>.jpg c 1000` 间隔`1000毫秒`抓取摄像头保存到`d`标记的路径</br>
`sa d\<i>.jpg c 1000 10` 间隔`1000毫秒`抓取摄像头保存到`d`标记的路径,总共保存`10`张</br>

### saveAsXLSX
从剪贴板读取数据保存到XLSX文件</br>

#### 命令
`sa d\1.xlsx` 从剪贴板读取数据保存到`d`标记的路径</br>


### printScreen
屏幕截图/拾色，获取屏幕区域尺寸</br>

#### 命令
`ps` 手动截屏,图片保存到剪贴板</br>
`ps dstpath` 手动截屏，图片保存到`dstpath`</br>
`pc` 屏幕拾色，返回`十六进制`和`十进制`的rgb值，保存在剪贴板</br>
`pc c` 打开windows拾色器</br>
`pc p` 打开一个调色板拾色</br>
`gs` 获取屏幕区域的尺寸，配合ffmpeg录制屏幕区域到视频或gif时使用</br>


### recvFile
局域网接收文件</br>

#### 命令
`rf` 查看接收线程是否启动</br>
`rf dstpath` 设置保存路径</br>
`rf on` 启动接收线程</br>
`rf off` 停止接收线程</br>

### sendFile
局域网发送文件</br>

#### 命令
`sf off` 停止发送文件</br>
`sf src iplist` 依次发送文件到列表里的主机</br>

### opencvImage
调用opencv处理图片</br>

#### 命令
`cmap` 灰度图生成伪彩图片</br>
`den` 图片降噪</br>

### pillowImage
调用pillow处理图片</br>

#### 命令
`rs` 缩放图片</br>
`ro` 旋转图片</br>
`crop` 裁剪图片</br>
`gray` 转灰度图</br>
`wm` 加水印</br>
`cut` 裁切图片</br>

### removeWaterMark
图片去水印</br>

#### 命令
`rwm` 从剪贴板读取图片路径并打开opencv窗口</br>

#### 快捷键
`esc` 关闭opencv窗口</br>
`enter` 重新开始处理</br>
`右键` 保存已处理的图片</br>
`d` 下一张</br>
`a` 前一张</br>

### manageFile
操作文件</br>

#### 命令
`cp` 复制文件，适用用将文件复制到一个或多个固定的文件夹，如存放备份文件的文件夹</br>
`ms` 调用`robocopy`镜像同步文件夹</br>
`nf/nd` 新建文件/文件夹</br>
`enc/dec` 调用`openssl`加密/解密文件</br>

`zip/uzip` 调用`7zip`压缩/解压缩文件</br>
`zip` 所选文件压缩到一个文件</br>
`zip *` 所选文件分别压缩到一个文件</br>
`zip pw` 所选文件加密压缩到一个文件</br>
`zip * d\name.zip` 所选文件压缩到目标路径的一个文件</br>
`zip * d\*.zip` 所选文件分别压缩到目标路径</br>
`zip * d\*.zip pw` 功能同上，加密压缩</br>
`zip * bf@0\*.zip` 所选文件分别压缩到`bf`标记的路径下每一个文件夹内</br>
`zip * bf@1\*.zip` 所选文件分别压缩到`bf`标记的路径下第一个文件夹内</br>
`zip * bf@a\*.zip` 所选文件分别压缩到`bf`标记的路径下第一个文件夹名包含`a`的文件夹内</br>
`uzip` 参数同zip</br>

`ftp/dav` 调用`winscp`以ftp或dav的方式上传文件</br>
`m5/s1/s2/s3/s5/r1` 调用powershell计算文件的`md5/sha1/sha256/sha384/sha512/ripemd160`</br>
`rn` 批量重命名</br>
##### 重命名规则:
`rn r` 用随机字符串重命名，16位长度</br>
`rn r 32` 用随机字符串重命名，32位长度</br>
`rn r:<i>` 用序列号重命名</br>
`rn r:123:abc` 将原文件名中的`123`替换为`abc`</br>
`rn i:abc` 在原文件名的末尾添加`abc`</br>
`rn i:0:abc` 在原文件名的头部添加`abc`</br>
`rn c:5` 删除原文件名头部的5个文字</br>
`rn c:-5` 删除原文件名尾部的5个文字</br>
`rn c:5:-5` 删除原文件名头部和尾部的5个文字</br>
`rn l` 原文件名转小写</br>
`rn u` 原文件名转小写</br>
`rn .jpg` 原文件的后缀修改为jpg</br>
多个规则可以连起来使用：`rn r:000:abc i:def c:-5 .jpg`



#### tool
一些未分类功能</br>

#### 命令

`ca` 在所选路径或字典路径打开cmd窗口</br>
`pa` 在所选路径或字典路径打开powershell窗口</br>
`<` 执行cmd命令并关闭cmd窗口</br>
`>` 执行cmd命令不关闭cmd窗口</br>
`2/8/10/16` 进制转换</br>
`cal` 计算器</br>
`e64/d64` base64编码/解码</br>
`@` 用短名称打开网址</br>
`￥/$` 用短名称搜索关键字</br>
`gj` 关机</br>
`cq` 重启</br>

### manageHistory
操作命令缓存</br>

#### 命令
`clearh` 清空命令缓存</br>
`loadh` 从history.txt加载命令缓存</br>
`saveh` 保存命令缓存到history.txt</br>

### pdf
合并pdf</br>

#### 命令
`mpdf src dst` 从src获取pdf路径，合并后保存到dst</br>

### txt
写txt</br>

#### 命令
`wt` 进入txt模式</br>
`cm` 在未打开文件前切换到其它模式</br>
`wt file` 打开file并进入txt模式，成功打开文件后所有的输入都会写进txt</br>

### vlc
控制vlc播放器</br>

#### 命令
`vlc` 进入vlc模式</br>
`on` 启动方便去</br>
`off` 关闭播放器</br>
`play` 开始播放</br>
`pause` 暂停播放</br>
`stop` 停止播放</br>
`n` 下一首</br>
`p` 前一首</br>
`l` 切换播放列表</br>
`pl` 打印列表</br>
`repeat` 单曲循环</br>
`loop` 列表循环</br>
`rand` 随机播放</br>
`fs` 全屏或退出全屏</br>
`sk` 跳转到指定时间，按秒算</br>
`go` 按编号切换歌曲或视频</br>
`v` 设置音量</br>
`vu` 增大音量</br>
`vd` 减小音量</br>
`t` 打印时间</br>
`cm` 切换到其它模式</br>
`sleep` 延时，用于自动执行多条命令</br>
其它的输入会被当成名称进行搜索</br>


