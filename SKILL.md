---
name: sony-camera-ftp-macos
description: Configure Sony camera home Wi-Fi FTP auto transfer to macOS with a one-command AI Agent workflow. Use when the user gives this GitHub skill link or asks an AI agent to set up Sony camera-to-Mac automatic photo or video syncing, avoid SD-card import, avoid phone relay, create a Mac FTP receiver, generate camera menu settings, troubleshoot Sony FTP errors, or package a repeatable workflow for creators teaching AI Agent automation.
---

# Sony Camera FTP macOS

Set up a Mac as a local FTP receiver for Sony camera automatic transfer. Prefer this route over macOS SFTP/Remote Login unless the user explicitly asks for SFTP: Sony camera FTP menus are usually FTP/FTPES-oriented, and SFTP detours often waste time.

## Default Workflow

1. Confirm the user is on macOS and wants local home Wi-Fi transfer, not public Internet access.
2. Run `scripts/setup_sony_camera_ftp_macos.py` from this skill.
3. Verify the script reports:
   - FTP service running
   - LAN IP detected
   - local upload test passed
   - LaunchAgent installed
4. Give the user the generated Sony camera Chinese menu settings from the script output.
5. Ask the user to test with one real camera photo.
6. If the photo lands in the inbox folder, stop. If not, troubleshoot using `references/troubleshooting.md`.

## Setup Command

Run:

```bash
python3 /path/to/sony-camera-ftp-macos/scripts/setup_sony_camera_ftp_macos.py
```

Optional custom port:

```bash
python3 /path/to/sony-camera-ftp-macos/scripts/setup_sony_camera_ftp_macos.py --port 2121
```

The script creates:

- FTP account: `sonyftp`
- fixed camera-friendly password: `20261111`
- receiver app in `~/Library/Application Support/SonyCameraFtp`
- inbox folder at `~/Public/Sony-Camera-Inbox`
- Finder shortcut at `~/Pictures/Sony-Camera-Inbox`
- LaunchAgent at `~/Library/LaunchAgents/com.codex.sony-camera-ftp.plist`

The script detects the Mac LAN IP automatically and prints all camera values. Do not ask the user to choose IP, port, username, or password unless something fails.

## Camera Settings To Provide

After the script runs, copy the generated values into the camera:

`MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 服务器设置 -> 服务器1`

Use these field names:

- 显示名称：`MAC`
- 主机名：script output `Mac 局域网地址`
- 安全协议：`关`
- 端口：script output `FTP 端口`
- 指定目录：留空，或填 `/`
- 目录层级：`与相机相同`
- 同名文件：`不覆盖`
- 用户名：`sonyftp`
- 密码：`20261111`

Then enable:

- `FTP功能`：`开`
- `自动FTP传输`：`开`

Transfer target guidance:

- `静止影像`：`全部`
- `动态影像`：`全部` if the user wants all videos; otherwise `仅拍摄标记`
- `RAW+J/H传输目标`：choose `RAW`, `JPEG & HEIF`, or `RAW+J & RAW+H`

## Safety Defaults

- Keep the receiver on the home LAN only.
- Do not expose port `2121` on the router.
- Do not reuse the user's macOS password.
- Use the fixed password `20261111` for simpler camera input and tutorial consistency.
- If the user is making a tutorial video, tell viewers the AI Agent will detect their own Mac IP and print their own camera settings.

## Common Follow-Ups

- If the camera shows a yellow exclamation mark but files transfer, check `显示FTP结果` and clear old FTP error records.
- If the Mac IP changes, rerun the script or configure DHCP reservation in the router.
- If upload fails after reboot, run the script again; it is idempotent and rewrites the same simple configuration.
- For detailed failures, read `references/troubleshooting.md`.
