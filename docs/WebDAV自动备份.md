# WebDAV 自动备份（Windows 桌面版）

本 fork 为 ActivityWatch 桌面版（aw-qt 经典托盘版）增加了与
[aw-android-plus](https://github.com/guyu-guyu/aw-android-plus) 相同的功能：
**通过 WebDAV 自动备份数据**，且与手机端共用同一套备份目录结构，
多台设备可以把数据备份到同一个 WebDAV 文件夹。

## 工作原理

1. aw-qt 托盘程序按设定的间隔（默认 15 分钟）运行随包的 `aw-sync` 一次性推送：
   `aw-sync --sync-dir <本地缓存目录> --port <端口> sync --mode push`，
   把本地数据同步到本地缓存目录（位于数据目录下的 `aw-qt/webdav-sync`）。
2. 随后将缓存目录整棵树上传到 WebDAV 服务器，远程路径为
   `<远程目录>/<设备名>/<device_id>/sync.db`，与手机端完全一致。
3. 未变化的文件会根据本地清单（大小 + 修改时间 + 远程大小）自动跳过，
   每次只上传有变化的 `sync.db`。

备份是**单向上传**：只备份、不下载、不做恢复合并。`sync.db` 本身是 aw-sync 的
同步快照，之后可以用官方同步机制从中恢复/合并数据。

## 使用方法

1. 右键托盘图标 → **WebDAV 自动备份** → **备份设置…**
2. 填写：
   - **服务器地址**：WebDAV 可写目录的地址，如 `https://nas.example:5008/data`
     或局域网 `http://192.168.1.8:5005/backup`
   - **用户名 / 密码**：可同时留空（匿名访问）
   - **远程目录**：默认 `activitywatch`，手机端和电脑端填同一个即可共用
   - **备份间隔**：默认 15 分钟
3. 保存后勾选 **自动备份**，或点 **立即备份** 手动触发一次。
   子菜单第一行会显示上次备份的时间和结果。

## 配置与隐私

- 配置保存在 `aw-qt.toml` 的 `[webdav-backup]` 段（与 aw-qt 其他配置同文件）。
- 密码在 Windows 上用 DPAPI 加密后存储（字段 `password_dpapi`），
  只有当前 Windows 用户能解密；配置文件拷到别的机器/用户下密码将不可用，
  需要重新填写。
- 本地缓存目录：数据目录下 `aw-qt/webdav-sync`；
  备份状态与清单：同目录旁的 `webdav-backup-status.json` /
  `webdav-backup-manifest.json`。

## 注意事项

- 服务器地址应指向一个**可写目录**；程序会自动创建远程目录层级。
- 局域网 NAS 可使用 `http://` 地址；公网建议使用 `https://`。
- 备份依赖随包的 `aw-sync` 与正在运行的 aw-server，服务器未启动时该轮备份会失败，
  状态行会显示失败原因，下一周期自动重试。
- 与 aw-sync 守护进程互不影响：备份用独立的本地缓存目录一次性推送，
  不会改动守护进程的同步目录。

## 代码位置（aw-qt 子模块）

- `aw_qt/webdav_backup.py`：无 Qt 依赖的核心逻辑（配置、DPAPI、WebDAV 客户端、上传、备份周期）
- `aw_qt/webdav_dialog.py`：设置对话框
- `aw_qt/trayicon.py`：托盘菜单与定时调度
- `tests/test_webdav_backup.py`：单元/集成测试
