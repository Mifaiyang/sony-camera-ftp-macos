#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import textwrap
import time
from pathlib import Path


APP_DIR = Path.home() / "Library" / "Application Support" / "SonyCameraFtp"
CONFIG_PATH = APP_DIR / "config.json"
SERVER_PATH = APP_DIR / "sony_camera_ftp_server.py"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.codex.sony-camera-ftp.plist"
INBOX = Path.home() / "Public" / "Sony-Camera-Inbox"
PICTURES_LINK = Path.home() / "Pictures" / "Sony-Camera-Inbox"
USER = "sonyftp"
PASSWORD = "20261111"
PASSIVE_START = 50000
PASSIVE_END = 50050


def run(cmd, check=True, capture=False):
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def load_or_create_config(port):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
    else:
        data = {}
    data.update({
        "user": USER,
        "password": PASSWORD,
        "port": port,
        "inbox": str(INBOX),
        "passive_start": PASSIVE_START,
        "passive_end": PASSIVE_END,
    })
    CONFIG_PATH.write_text(json.dumps(data, indent=2) + "\n")
    CONFIG_PATH.chmod(0o600)
    return data


def ensure_venv():
    venv_python = APP_DIR / ".venv" / "bin" / "python"
    if not venv_python.exists():
        run([sys.executable, "-m", "venv", str(APP_DIR / ".venv")])
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "pyftpdlib"])
    return venv_python


def write_server():
    server_code = f"""#!/usr/bin/env python3
import json
import socket
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

CONFIG = json.loads(Path({str(CONFIG_PATH)!r}).read_text())


def local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


inbox = Path(CONFIG["inbox"]).expanduser()
inbox.mkdir(parents=True, exist_ok=True)

authorizer = DummyAuthorizer()
authorizer.add_user(CONFIG["user"], CONFIG["password"], str(inbox), perm="elradfmwMT")

handler = FTPHandler
handler.authorizer = authorizer
handler.passive_ports = range(int(CONFIG["passive_start"]), int(CONFIG["passive_end"]) + 1)
handler.banner = "Sony Camera Mac FTP receiver ready"

server = FTPServer(("0.0.0.0", int(CONFIG["port"])), handler)
print(f"Sony Camera FTP server listening on {{local_ip()}}:{{CONFIG['port']}}", flush=True)
print(f"Saving uploads to {{inbox}}", flush=True)
server.serve_forever()
"""
    SERVER_PATH.write_text(server_code)
    SERVER_PATH.chmod(0o700)


def write_plist(venv_python):
    (Path.home() / "Library" / "LaunchAgents").mkdir(parents=True, exist_ok=True)
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.codex.sony-camera-ftp</string>
  <key>ProgramArguments</key>
  <array>
    <string>{venv_python}</string>
    <string>{SERVER_PATH}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>WorkingDirectory</key>
  <string>{APP_DIR}</string>
  <key>StandardOutPath</key>
  <string>{APP_DIR / "sony-camera-ftp.out.log"}</string>
  <key>StandardErrorPath</key>
  <string>{APP_DIR / "sony-camera-ftp.err.log"}</string>
</dict>
</plist>
"""
    PLIST_PATH.write_text(plist)


def install_launch_agent():
    uid = os.getuid()
    run(["launchctl", "bootout", f"gui/{uid}", str(PLIST_PATH)], check=False)
    run(["launchctl", "bootstrap", f"gui/{uid}", str(PLIST_PATH)])
    run(["launchctl", "enable", f"gui/{uid}/com.codex.sony-camera-ftp"], check=False)
    run(["launchctl", "kickstart", "-k", f"gui/{uid}/com.codex.sony-camera-ftp"])


def make_inbox_link():
    INBOX.mkdir(parents=True, exist_ok=True)
    if PICTURES_LINK.exists() or PICTURES_LINK.is_symlink():
        if PICTURES_LINK.is_symlink() and PICTURES_LINK.resolve() == INBOX:
            return
        return
    PICTURES_LINK.symlink_to(INBOX)


def verify_once(config):
    from ftplib import FTP
    from io import BytesIO

    host = lan_ip()
    ftp = FTP()
    ftp.connect(host, int(config["port"]), timeout=8)
    ftp.login(config["user"], config["password"])
    ftp.storbinary("STOR SONY_CAMERA_AGENT_VERIFY.txt", BytesIO(b"sony camera ftp verify ok\n"))
    ftp.quit()
    verify_file = INBOX / "SONY_CAMERA_AGENT_VERIFY.txt"
    ok = verify_file.exists()
    if ok:
        verify_file.unlink()
    return ok


def verify(config, attempts=15, delay_seconds=1):
    last_error = None
    for _ in range(attempts):
        try:
            if verify_once(config):
                return True
        except Exception as exc:
            last_error = exc
        time.sleep(delay_seconds)
    if last_error:
        print(f"Verification error: {last_error}", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description="Set up Sony camera FTP auto transfer receiver on macOS.")
    parser.add_argument("--port", type=int, default=2121)
    args = parser.parse_args()

    if sys.platform != "darwin":
        raise SystemExit("This setup script is for macOS.")
    if not shutil.which("launchctl"):
        raise SystemExit("launchctl not found; this must run on macOS.")

    config = load_or_create_config(args.port)
    venv_python = ensure_venv()
    write_server()
    write_plist(venv_python)
    make_inbox_link()
    install_launch_agent()
    ok = verify(config)
    host = lan_ip()

    print()
    print("Sony Camera Mac FTP receiver is ready." if ok else "FTP receiver installed, but verification failed.")
    print()
    print("Mac 端：")
    print(f"- Mac 局域网地址：{host}")
    print(f"- FTP 端口：{config['port']}")
    print(f"- 接收目录：{INBOX}")
    print(f"- Finder 快捷入口：{PICTURES_LINK}")
    print(f"- FTP 用户名：{config['user']}")
    print(f"- FTP 密码：{config['password']}")
    print()
    print("Sony 相机中文菜单填写：")
    print(textwrap.dedent(f"""\
    MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 服务器设置 -> 服务器1

    显示名称：MAC
    主机名：{host}
    安全协议：关
    端口：{config['port']}
    指定目录：留空 或 /
    目录层级：与相机相同
    同名文件：不覆盖
    用户名：{config['user']}
    密码：{config['password']}

    然后打开：
    FTP功能：开
    自动FTP传输：开
    """))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
