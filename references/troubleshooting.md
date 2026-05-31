# Troubleshooting

## File Does Not Appear On Mac

Check in this order:

1. The Mac and Sony camera are on the same Wi-Fi/LAN.
2. The camera uses the current `Mac 局域网地址` from the setup script.
3. `安全协议` is `关`.
4. `端口` matches the script output, usually `2121`.
5. `FTP功能` is `开`.
6. `自动FTP传输` is `开`.
7. The Mac is awake.

Run the setup script again to repeat the local FTP upload test and print the current settings.

## Yellow Exclamation Mark On Sony Camera

If files transfer successfully, this is usually an FTP status or previous error indicator, not a hardware problem.

Check:

`MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 显示FTP结果`

Also check:

`MENU -> 网络 -> FTP传输 -> FTP传输功能 -> 显示FTP错误信息`

Clear old failed transfer records if the camera offers that option.

## Mac IP Changed

The camera connects to a numeric LAN IP. If the router later assigns a different IP, transfer fails.

Fix options:

- rerun the setup script and update the camera `主机名`;
- reserve the Mac's IP in the router DHCP settings.

## Do Not Use SFTP First

macOS Remote Login provides SFTP over port 22, but many Sony camera FTP setup flows are FTP/FTPES-centric. For a creator tutorial, the repeatable route is a local FTP receiver with a fixed non-system password.

## Security Boundary

This setup is for trusted home LAN use. Do not port-forward it to the Internet.
