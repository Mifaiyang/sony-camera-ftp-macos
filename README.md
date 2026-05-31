# Sony Camera FTP macOS

用 AI Agent 一步配置 Sony 相机通过家里 Wi-Fi 自动同步素材到 Mac。

适合 Sony A7 系列、ZV 系列等支持 FTP 传输的机型。Mac 会被配置成一个本地 FTP 接收端，相机拍完后把照片或视频传到 Mac 文件夹。

## 给用户的最简单用法

把这个 GitHub 链接发给你的 AI Agent，然后说：

```text
使用这个 GitHub skill，帮我配置 Sony 相机自动同步到 Mac：
https://github.com/YOUR_NAME/sony-camera-ftp-macos
```

Agent 会自动完成 Mac 端配置，并输出相机中文菜单要填的内容。

## 固定配置

Agent 会自动设置：

```text
用户名：sonyftp
密码：20261111
端口：2121
接收目录：~/Public/Sony-Camera-Inbox
Finder 快捷入口：~/Pictures/Sony-Camera-Inbox
```

Mac 的局域网 IP 会由 Agent 自动检测，不需要用户自己查。

## 相机端填写

Agent 配好 Mac 后，会输出类似下面的相机设置：

```text
MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 服务器设置 -> 服务器1

显示名称：MAC
主机名：你的 Mac 局域网 IP
安全协议：关
端口：2121
指定目录：留空 或 /
目录层级：与相机相同
同名文件：不覆盖
用户名：sonyftp
密码：20261111

然后打开：
FTP功能：开
自动FTP传输：开
```

## 直接运行脚本

如果不用 skill，也可以直接运行：

```bash
python3 scripts/setup_sony_camera_ftp_macos.py
```

## 注意

这个方案只建议在家里局域网使用，不要把 FTP 端口暴露到公网。
