# 小米 13 (fuxi) 内核构建兼容性记录

## 设备信息

| 项目 | 值 |
|------|-----|
| 设备 | 小米 13 (fuxi) |
| 系统 | MIUI V14.0.8.0.TMCCNXM |
| Android | 13 |
| 内核 | 5.15.41 |
| GKI 分支 | android13-5.15 |
| Kernel FCM 版本 | 7 |
| 本次成功构建月份 | 2022-11 |

## 2026-11-17 成功修复记录

- 修复提交：`1c2b6ab5b892c3fce4d6c7a721bdafcef11d28e2`。
- GitHub Actions：[Build Kernels #43951926284](https://github.com/chaogei/GKI_KernelSU_SUSFS/actions/runs/43951926284)。
- 用户反馈本次修复成功；本文记录构建参数、排查证据与修复措施，未额外归档刷入后的完整日志。
- 核心经验：**同时保证真实编译配置符合设备 FCM 要求，以及 `/proc/config.gz` 如实报告该配置；只修改编译配置、继续嵌入另一份 stock config，无法解决开机校验失败。**

### 根因与证据

开机弹窗：

> 您的设备内部出现了问题。请联系您的设备制造商了解详情。

本次实际抓取的启动日志：

```text
Build: Vendor interface is incompatible, error=1
ActivityTaskManager: Build fingerprint is not consistent, warning user
```

当时手机上的两套信息不一致：

| 检查位置 | 修复前实际内容 |
|----------|----------------|
| `/proc/version` | `5.15.41-android13-Wild`，实际运行的自定义内核 |
| `/proc/config.gz` 文件头 | `Linux/arm64 5.15.110 Kernel Configuration`，另一版本的配置 |
| `/vendor/etc/vintf/manifest_kalama.xml` | `target-level="7"` |
| `/system/etc/vintf/compatibility_matrix.7.xml` | 存在适用的 `5.15.41` 内核配置要求 |

Android 13 的 libvintf 从 `/proc/config.gz` 读取内核配置。本仓库的 `.github/actions/stock-config/action.yml` 会把 `kernel/Makefile` 中 `config_data` 的输入，从 `$(KCONFIG_CONFIG)` 换成独立的 `arch/arm64/configs/stock_defconfig`。这使系统读到的配置与真实编译配置脱离。

将手机报告的配置与本机 FCM 7 矩阵中适用的 `5.15.41` 要求逐项比较，发现下列 7 项均为 `m`，但要求为 `y`。此前只围绕 `L2TP` 修改 `.config` 或 `POST_DEFCONFIG_CMDS`，既没有消除配置来源分离，也没有覆盖其他 6 项。

## Android 13 FCM 7 兼容性要求

以下是本设备、本系统和目标内核对应的要求，不应不经核对推广到其他 ROM 或内核分支。

### 必须内建（=y）的配置

| 配置项 | 要求 | 修复前 `/proc/config.gz` |
|--------|------|-------------------------|
| `CONFIG_L2TP` | `y` | `m` |
| `CONFIG_PPP` | `y` | `m` |
| `CONFIG_PPPOL2TP` | `y` | `m` |
| `CONFIG_PPP_BSDCOMP` | `y` | `m` |
| `CONFIG_PPP_DEFLATE` | `y` | `m` |
| `CONFIG_PPP_MPPE` | `y` | `m` |
| `CONFIG_PPTP` | `y` | `m` |

`.github/actions/build-kernel/action.yml` 在编译前复用 `set-kernel-config`，统一写入 `gki_defconfig`，同时确保 `CONFIG_IKCONFIG=y`、`CONFIG_IKCONFIG_PROC=y`。

目标 `2022-11` 上游 GKI 的 `gki_defconfig` 本来就将上述 7 项设为 `y`；此前看到的 `m` 来自替换后的 stock config，不能据此认定目标上游默认值为 `m`。相关 Kconfig 依赖在该目标配置中具备，无需把 `tristate` 改成 `bool`。

### 必须禁用的配置

| 配置项 | 要求 | 处理方式 |
|--------|------|----------|
| `CONFIG_IP6_NF_NAT` | 禁用 | 网络配置不再主动启用，最终配置校验拒绝 `y/m` |
| `CONFIG_IP6_NF_TARGET_MASQUERADE` | 禁用 | 网络配置不再主动启用，最终配置校验拒绝 `y/m` |
| `CONFIG_SYSVIPC` | 禁用 | 禁用 DroidSpaces，最终配置校验拒绝 `y/m` |

### 必须排除的功能

DroidSpaces (DS) 会强制启用 `CONFIG_SYSVIPC=y`、`CONFIG_POSIX_MQUEUE=y`、`CONFIG_IPC_NS=y`。其中 `SYSVIPC=y` 与此处 FCM 7 要求直接冲突。

- 触发构建时必须设置 `use_ds=false`。
- `.github/workflows/build.yml` 在构建任务入口拒绝 `android13-5.15 + DS/All`，避免编译结束后才失败。
- 不应强行关闭 DS 所需配置后，仍将产物标记为完整支持 DS。

## 构建参数

### 本次成功构建使用的参数

```yaml
release_type: CI
kernel_build_version: 5.15.x-android13
os_patch_level: 2022-11
page_size: 4k
commit_mode: verified
root_flavor: KernelSU-Next
use_cache: false
allow_version_mismatch: false
brand_name: Wild
keep_kmi: false
kernel_runner: ubuntu-24.04
use_susfs: true
use_nomount: true
use_bbg: true
use_net: true
use_ds: false
use_ntsync: false
use_ptrace: false
use_unicode: false
use_bpf: false
use_perf: false
test_release_notes: false
```

等效 feature_set：`SUSFS+NoMount+BBG+NET`。

使用精确月份 `2022-11` 将构建限制到目标 `5.15.41`；`CI` 上传构建 artifacts，不创建 Release。需要发布时再显式选择 `Pre-Release` 或 `Release`，不要将发布状态与编译成功混为一谈。

### 本轮正式发布参数与流程设计

保留上面的成功 CI 参数作为历史复现依据；本轮正式发布改用以下参数，其余功能开关沿用上述记录，尤其保持 `use_ds=false`：

```yaml
release_type: Release
kernel_build_version: 5.15.x-android13
os_patch_level: '41'
```

发布范围为 `2022-06` 至 `2022-11` 六个月份，每个月份均须提供 `boot.img` 与 AnyKernel3 刷入包。流程设计是先严格核对所选月份、版本与双格式产物完整性，再创建 draft 并完整上传、核对附件，全部成功后才转为正式 Release 并标记 Latest；缺失或上传失败不得发布不完整版本。这是本轮发布流程的设计要求，不表示已经完成正式发布。

Latest 表示最新正式发布状态，不是最终维护版或终止维护声明；后续仍可继续修复和更新。

### 代码基础

基于 WildKernels r22 tag (`8d8e0339`)，该版本此前验证可在小米 13 上正常启动；本次成功修复对应提交为 `1c2b6ab5`。

上游后续版本可能更新 SUSFS/KernelSU pins。复现时保留本次代码与 `verified` 选择，不要在排查兼容性时同时切换到最新依赖。

## 自定义修改清单

### 1. tracefs 权限修复（WebView）

**文件**：`.github/actions/kernel-fixes/action.yml`

此前针对 WebView renderer 访问 `/sys/kernel/tracing/trace_marker` 的问题，将 tracefs 默认根目录权限从 0700 调整为 0755；这与本次 FCM 弹窗是不同问题。

### 2. FCM 7 网络配置及真实配置报告修复

**文件**：`.github/actions/networking-config/action.yml`、`.github/actions/build-kernel/action.yml`、`.github/workflows/build.yml`、`.github/workflows/prepare.yml`

- 网络配置删除 `CONFIG_IP6_NF_NAT=y` 和 `CONFIG_IP6_NF_TARGET_MASQUERADE=y`，保留 `CONFIG_L2TP=y`。
- 构建前统一确保 7 项网络配置内建，并启用 IKCONFIG 及其 proc 接口；移除旧的单项 `POST_DEFCONFIG_CMDS` 环境覆盖。
- `android13-5.15` 跳过 stock config 嵌入，恢复由真实编译 `.config` 生成 `/proc/config.gz`。
- 同步跳过该分支的 stock config 预取任务、artifact 参数传递和下载，其他内核分支保持原有嵌入行为。
- 构建入口拒绝 DS 冲突组合。
- 构建后必须找到最终 `.config`，检查 7 项及 IKCONFIG 为 `y`，并拒绝 SYSVIPC、IPv6 NAT/MASQUERADE 为 `y/m`。
- 从产出的 `Image` 提取嵌入配置，与最终 `.config` 全文比对；缺失、提取失败或内容不一致即失败，不能跳过后继续发布。

### 3. disabled 过滤修复

**文件**：`.github/workflows/prepare.yml`

r22 的 jq 查询没有过滤 `"disabled": true` 的 config 条目；现有矩阵生成通过 `select($item.disabled != true)` 排除禁用条目。

### 4. NoMount 编译修复

**文件**：`.github/workflows/main.yml`

此前 NoMount dev 分支引入 libc 头文件（`unistd.h`），与 zig cc freestanding 编译不兼容；已 pin 到 `04af0552bb29c7cee1b78c3eea69d7ed98b80bf2`（2026-11-01）。

### 5. Release artifact 修复

**文件**：`.github/workflows/main.yml`

- NoMount 下载使用 `name: NoMount-Metamodule` 和 `path: release-assets/nomount-raw`。
- NoMount zip 从 `release-assets/nomount-raw` 目录打包。
- Artifact re-fetch 的 jq 路径从 `.[0].archive_download_url` 改为 `.artifacts[0].id`。

### 6. boot.img 生成

**文件**：`.github/actions/build-kernel/action.yml`、`.github/workflows/build.yml`、`.github/workflows/main.yml`

- 设置 `BUILD_GKI_ARTIFACTS=1`。
- 收集 boot.img 到 `boot-images/` 并重命名带版本前缀。
- 上传为 `*-BootIMG` artifact；Release 流程下载到 `release-assets/boot-images`。

生成通用 boot.img 本身不解决本次配置校验问题；关键仍是内核配置及其嵌入内容一致且合规。

### 7. sublevel 41 恢复六个月份

**文件**：`.github/config/android13-5.15.json`

正式发布范围恢复为同属 sublevel 41 的六个月份：`2022-06`、`2022-07`、`2022-08`、`2022-09`、`2022-10`、`2022-11`，不再只构建 `2022-11`。选择 `os_patch_level=41` 汇集这六个月份；配置文件仍包含其他 sublevel，不应以 `All` 代替该过滤条件。

目前只有 `2022-11` 有用户成功反馈，`2022-06` 至 `2022-10` 尚需真机验证；恢复构建与通过配置门禁不等于已确认所有月份在小米 13 上可用。

## 刷入后的验证命令

以下命令仅用于读取信息，不刷写分区、不修改系统。管道和筛选放在 Android shell 内，便于从 Windows PowerShell 调用。

```bash
adb shell "cat /proc/version; zcat /proc/config.gz | head -4"
adb shell "zcat /proc/config.gz | grep -E '^CONFIG_(IKCONFIG|IKCONFIG_PROC|L2TP|PPP|PPPOL2TP|PPP_BSDCOMP|PPP_DEFLATE|PPP_MPPE|PPTP)='"
adb shell "zcat /proc/config.gz | grep -E '^(# )?CONFIG_(SYSVIPC|IP6_NF_NAT|IP6_NF_TARGET_MASQUERADE)(=| )'"
adb shell "logcat -b all -d | grep -E 'VintfObject|For config|Vendor interface is incompatible|Build fingerprint is not consistent'"
adb shell "ls -ld /sys/kernel/tracing"
```

检查要点：

1. `/proc/version` 和配置文件头应对应所刷目标，不再出现运行 `5.15.41` 却报告 `5.15.110` 配置的情况。启用 SUSFS 时，`uname -a` 可能被伪装，不应单独作为刷入版本证据。
2. 上述 7 项和 IKCONFIG 两项均应为 `y`；禁用项不得出现 `=y` 或 `=m`，部分不可见符号可能完全不出现在配置中。
3. 检查本次开机是否仍有 VINTF 不兼容日志，并人工确认重启后的弹窗是否消失。日志无输出也可能是缓冲区已覆盖，不能单独作为校验成功的证据。
4. 构建配置检查不等于完整 VINTF 检查；若仍失败，继续按设备实际矩阵排查其他配置、HAL、版本等要求，不要直接屏蔽弹窗。

## 排查误区与其他注意事项

### 不要把通用 fingerprint 日志直接当成分区不匹配

曾读到 `ro.bootimage.build.fingerprint` 为 V14.0.9.0，而系统为 V14.0.8.0；但仅凭该属性不能确定它来自 `vendor_boot`，也不能认定它就是本次弹窗原因。

Android 13 的 `Build.isBuildConsistent()` 在 Treble 路径调用 `VintfObject.verifyWithoutAvb()`；本次 `Vendor interface is incompatible, error=1` 对应该失败分支，随后框架仍会打印通用的 `Build fingerprint is not consistent` 提示。

因此，此前“换通用 ramdisk 可避免此问题”或“刷回原厂 vendor_boot 可彻底修复”的结论不适用于本次已定位的问题，没有足够证据支持，不能据此要求刷分区。

### SUSFS 与版本、启动状态显示

此前设备查询曾显示 `ro.boot.verifiedbootstate=green`、`ro.boot.vbmeta.device_state=locked`，但实际 bootloader 已解锁。使用 SUSFS 等功能时，部分显示值可能经过伪装，不能仅凭这些属性判断真实启动状态；版本定位应结合 `/proc/version`、构建记录与实际产物。
