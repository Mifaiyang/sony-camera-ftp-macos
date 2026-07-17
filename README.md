<div align="center">

# Sony Camera FTP macOS

让支持 FTP 的 Sony 相机把照片和视频直接传到 Mac。第一次配置完成后，不用每次拔卡，也不用先绕到手机。

[交给 AI Agent](#交给-ai-agent) · [自己运行](#自己运行脚本) · [相机设置](#相机里要填什么) · [安全边界](#安全边界)

</div>

---

我做这个项目，是因为相机到电脑的最后几米一直很割裂。拍摄在相机里完成，整理和剪辑在 Mac 上完成，中间却常常要拔卡、找读卡器，再手动复制一遍。

Sony 相机本身支持 FTP 传输，Mac 端缺少的是一个适合普通用户的接收端。这个项目会在 Mac 上搭好本地 FTP 服务，设置开机自启，创建固定收件箱，并把相机菜单需要填写的参数一次打印出来。

它目前只是一个开源脚本和 AI Agent Skill，没有图形界面。

## 实际使用流程

```mermaid
flowchart LR
    A["Sony 相机拍摄"] --> B["家里 Wi-Fi"]
    B --> C["Mac 本地 FTP 接收端"]
    C --> D["Sony-Camera-Inbox"]
    D --> E["整理 / 剪辑 / 备份"]
```

第一次需要完成两件事：在 Mac 上运行安装脚本，再把脚本输出的参数填进相机。以后只要 Mac 和相机在同一个局域网，相机就可以按自身的 FTP 规则传输素材。

这里的“自动”有明确边界。Mac 端的安装、后台服务和参数生成可以自动完成；相机菜单仍需本人操作一次。

## 交给 AI Agent

把下面这段话发给支持 GitHub Skill 的 AI Agent：

```text
使用这个 GitHub Skill，帮我配置 Sony 相机自动传输到 Mac：
https://github.com/Mifaiyang/sony-camera-ftp-macos
```

Agent 会运行配置脚本，检查本机上传是否成功，然后给出相机端要填写的 IP、端口、用户名和密码。

## 自己运行脚本

如果不使用 AI Agent，可以克隆仓库后直接运行：

```bash
git clone https://github.com/Mifaiyang/sony-camera-ftp-macos.git
cd sony-camera-ftp-macos
python3 scripts/setup_sony_camera_ftp_macos.py
```

第一次运行需要联网安装 `pyftpdlib`。脚本仅支持 macOS，并依赖系统自带的 `launchctl`。

## Mac 上会发生什么

脚本会完成这些工作：

| 项目 | 实际设置 |
|---|---|
| FTP 账号 | `sonyftp` |
| FTP 密码 | `20261111` |
| FTP 端口 | `2121` |
| 被动端口 | `50000-50050` |
| 接收目录 | `~/Public/Sony-Camera-Inbox` |
| Finder 入口 | `~/Pictures/Sony-Camera-Inbox` |
| 后台启动 | `~/Library/LaunchAgents/com.codex.sony-camera-ftp.plist` |
| 运行文件 | `~/Library/Application Support/SonyCameraFtp` |

安装完成后，脚本会从本机向 FTP 服务上传一个临时文件。测试通过才会显示 `Sony Camera Mac FTP receiver is ready.`。测试文件随后会被删除。

脚本可以重复运行。Mac 的局域网 IP 变化、服务异常或配置不确定时，重新运行会覆盖同一套配置并再次测试。

## 相机里要填什么

不同机型和固件的菜单名称可能略有区别。带 FTP 功能的 Sony 相机通常可以沿下面的路径进入服务器设置：

```text
MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 服务器设置 -> 服务器1
```

填写脚本最后打印的参数：

```text
显示名称：MAC
主机名：脚本输出的 Mac 局域网地址
安全协议：关
端口：2121
指定目录：留空 或 /
目录层级：与相机相同
同名文件：不覆盖
用户名：sonyftp
密码：20261111
```

然后打开：

```text
FTP功能：开
自动FTP传输：开
```

先拍一张测试照片。文件进入 `~/Public/Sony-Camera-Inbox` 后，再决定是否传 RAW、JPEG/HEIF 或视频。不要一开始就用整张存储卡测试，排错会变慢。

## 为什么这样设计

这个项目需要同时处理相机兼容、Mac 后台运行、局域网地址和普通用户的配置门槛。单独启动一个 FTP 服务远远不够。

### 先服从相机支持的协议

macOS 的“远程登录”提供的是 SFTP，但 Sony 相机里的 FTP 设置通常围绕 FTP/FTPES。为了少绕一层兼容问题，这个版本选择了局域网内的普通 FTP。

代价也很清楚：FTP 不加密，所以它只能放在可信的家庭局域网里使用。

### 把相机要记住的参数固定下来

账号、密码和端口保持固定，相机只需配置一次。Mac 的局域网 IP 无法可靠写死，因此由脚本在运行时检测并打印。路由器以后重新分配 IP 时，重新运行脚本并更新相机主机名即可。

### 先验证 Mac，再让用户碰相机

如果服务本身没有启动成功，先在相机菜单里来回改参数只会增加变量。脚本会先做本机 FTP 上传测试。早期版本曾在服务刚启动时过早判断失败，后来改成多次重试，给 LaunchAgent 留出启动时间。

### 让服务在重启后继续运行

接收端由 macOS LaunchAgent 管理，登录后自动启动，异常退出时也会重新拉起。用户看到的是一个固定文件夹，不需要每天打开终端守着脚本。

## 这个项目怎么做出来的

一开始的问题很朴素：能不能让相机拍完后直接把素材送到 Mac？真正做起来，工作被拆成了几层。

先确认相机端到底支持什么协议，再在 Mac 上搭最小接收端；随后处理依赖安装、后台启动、文件落点和 IP 检测。脚本能运行以后，还要把技术输出翻译成相机中文菜单，因为那才是用户真正会卡住的地方。

最后一步是把流程做成 Skill。用户只要给 Agent 一个 GitHub 地址，Agent 就能读取操作顺序、运行脚本、判断验证结果，并在失败时按固定次序排查。脚本解决重复操作，Skill 解决“下一步该做什么”。

我在这个项目里负责确定使用场景、收敛配置项、定义成功标准和安全边界，也持续处理实际使用中出现的问题。AI Agent 参与了脚本实现、排错和文档整理。几轮调整里，更多时间花在减少用户需要理解的东西上。

## 安全边界

当前实现优先考虑家庭局域网里的易用性，不适合直接暴露在公网。

- 不要在路由器上转发 `2121` 或 `50000-50050` 端口。
- 不要在咖啡店、酒店、校园公共网等不可信网络中运行。
- FTP 为明文传输，固定账号和密码不能当作互联网安全凭证。
- 服务绑定到 Mac 的网络接口，同一网络中的设备可以尝试连接。
- FTP 账号的目录被限制在 `~/Public/Sony-Camera-Inbox`，但它在该目录内具有文件管理权限。
- 不要把 macOS 登录密码改成 FTP 密码，也不要复用其他重要密码。

Mac 休眠后，相机无法继续传输。需要长时间自动接收时，要同时检查系统睡眠设置。

## 常见问题

### 相机显示黄色感叹号，但文件已经传过去

这通常是历史错误或 FTP 状态提示。检查：

```text
MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 显示FTP结果
MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 显示FTP错误信息
```

### 之前能传，后来突然失败

先重新运行脚本，查看 Mac 当前局域网 IP。地址变化后，需要同步修改相机里的“主机名”。如果经常变化，可以在路由器里为 Mac 设置 DHCP 地址保留。

### 文件没有出现在 Mac

按这个顺序检查：

1. Mac 和相机是否连接同一个局域网；
2. Mac 是否处于唤醒状态；
3. 相机主机名是否等于脚本当前输出的 IP；
4. 安全协议是否关闭，端口是否为 `2121`；
5. `FTP功能` 和 `自动FTP传输` 是否都已打开；
6. 重新运行脚本时，本机上传测试是否通过。

更多排错步骤见 [references/troubleshooting.md](references/troubleshooting.md)。

## 当前限制

- 仅支持 macOS；
- 只适用于带 FTP 传输功能的 Sony 相机；
- 没有图形界面，也没有双击卸载器；
- 相机菜单需要手动配置一次；
- Mac IP 变化后需要更新相机主机名；
- 当前版本使用明文 FTP，定位是可信家庭局域网工具。

## 仓库结构

```text
sony-camera-ftp-macos/
├── SKILL.md
├── agents/openai.yaml
├── scripts/setup_sony_camera_ftp_macos.py
└── references/troubleshooting.md
```

## 反馈

如果你的 Sony 机型菜单路径不同，或者脚本验证通过但相机仍无法传输，可以提交 [Issue](https://github.com/Mifaiyang/sony-camera-ftp-macos/issues)。请附上机型、macOS 版本、相机错误提示和脚本最后一段输出；不要公开个人网络信息或其他账号密码。

更多作品：[周灏 · Hao Zhou Portfolio](https://mifaiyang.github.io/hao-zhou-portfolio/) · [GitHub @Mifaiyang](https://github.com/Mifaiyang)
