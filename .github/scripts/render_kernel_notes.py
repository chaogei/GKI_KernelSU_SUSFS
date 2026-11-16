import json, os
def env(n,d=""): return os.environ.get(n,d).strip() or d
def parse_managers(raw):
    try: return json.loads(raw) if raw.strip() else []
    except: return []
root = env("ROOT_FLAVOR","All")
if root.startswith("All"): root = "All"
feats=[]
if env("USE_SUSFS","true")=="true": feats.append("SUSFS")
if env("USE_NOMOUNT","true")=="true": feats.append("NoMount")
if env("USE_BBG","true")=="true": feats.append("Baseband Guard")
if env("USE_DS","true")=="true": feats.append("DroidSpaces-OSS")
if env("USE_NET","true")=="true": feats.append("Networking")
if env("USE_NTSYNC","true")=="true": feats.append("NTSync")
if env("USE_PTRACE","true")=="true": feats.append("Ptrace Leak Fix")
if env("USE_UNICODE","true")=="true": feats.append("Unicode Fix")
if env("USE_BPF","true")=="true": feats.append("BTF / eBPF / FUSE-BPF")
if env("USE_PERF","false")=="true": feats.append("Performance Tuning")
if env("PAGE_SIZE","4k")=="16k": feats.append("16 KB page size (ARM64)")
lines=[]
lines.append("# Wild Kernels for GKI2 Devices")
lines.append("")
if env("KERNEL_BUILD_VERSION")=="5.15.x-android13" and env("OS_PATCH_LEVEL")=="41":
    lines.append("## 版本更新说明：5.15.41-android13")
    lines.append("")
    lines.append("- 恢复 2022-06、2022-07、2022-08、2022-09、2022-10、2022-11 六个月份，每个月份提供 boot.img 与 AnyKernel3 双格式产物。")
    lines.append("- 针对小米 13 Android 13 FCM 7，确保 CONFIG_L2TP、CONFIG_PPP、CONFIG_PPPOL2TP、CONFIG_PPP_BSDCOMP、CONFIG_PPP_DEFLATE、CONFIG_PPP_MPPE、CONFIG_PPTP 七项内建（=y），并由真实编译配置生成 /proc/config.gz，不再嵌入另一份 stock config。")
    lines.append("- 禁用 DroidSpaces（use_ds=false）；构建入口拒绝 DS 冲突组合，最终配置必须通过七项内建及 IKCONFIG 检查，SYSVIPC、IPv6 NAT/MASQUERADE 不得为 y/m；Image 嵌入配置提取失败或与最终 .config 不一致即失败。")
    lines.append("- 目前仅 2022-11 有用户成功反馈，2022-06 至 2022-10 仍需真机验证；构建配置检查不等于完整 VINTF 或设备兼容性验证。")
    lines.append("- 本版不是最终维护版，也不代表终止维护；Latest 仅表示最新正式发布状态。")
    lines.append("")
lines.append("## Root")
lines.append("")
ksun_branch=env("KSUN_BRANCH","dev-susfs")
ksun_commit=env("KSUN_COMMIT","")
ksu_commit=env("KSU_COMMIT","")
bakasu_commit=env("BAKASU_COMMIT","")
sukisu_ultra_commit=env("SUKISU_ULTRA_COMMIT","")
finasu_commit=env("FINASU_COMMIT","")
kowsu_commit=env("KOWSU_COMMIT","")
kernelsu_commit=env("KERNELSU_COMMIT","")
nm=env("NOMOUNT_COMMIT","")
kp=env("KERNEL_PATCHES_COMMIT","")
ak=env("ANYKERNEL3_COMMIT","")
ds=env("DROIDSPACES_COMMIT","")
_rmatrix={}
try: _rmatrix={m.get("root_flavor",""):m.get("root_commit","") for m in json.loads(env("ROOT_MATRIX","[]")) if isinstance(m,dict)}
except: pass
if env("USE_SUSFS","true")=="true":
    _next_url="https://github.com/pershoot/KernelSU-Next/commit/"
else:
    _next_url="https://github.com/KernelSU-Next/KernelSU-Next/commit/"
_root_urls={"next":_next_url,"kernelsu":"https://github.com/tiann/KernelSU/commit/","bakasu":"https://github.com/Baka-SU/BakaSU/commit/","sukisu-ultra":"https://github.com/SukiSU-Ultra/SukiSU-Ultra/commit/","finasu":"https://github.com/LyraVoid/FinaSU/commit/","kowsu":"https://github.com/KOWX712/KernelSU/commit/"}
_root_commits={"next":_rmatrix.get("next","") or kernelsu_commit,"kernelsu":_rmatrix.get("kernelsu","") or ksu_commit,"bakasu":_rmatrix.get("bakasu","") or bakasu_commit,"sukisu-ultra":_rmatrix.get("sukisu-ultra","") or sukisu_ultra_commit,"finasu":_rmatrix.get("finasu","") or finasu_commit,"kowsu":_rmatrix.get("kowsu","") or kowsu_commit}
_flavors0=[m.get("flavor","") for m in parse_managers(env("MANAGER_LIST","")) if m.get("flavor","")]
if not _flavors0:
    _flavors0={"KernelSU-Next":["next"],"KernelSU":["kernelsu"],"BakaSU":["bakasu"],"SukiSU-Ultra":["sukisu-ultra"],"FinaSU":["finasu"],"KowSU":["kowsu"],"No Root":[],"All":["next","kernelsu","bakasu"]}.get(root,["next","kernelsu","bakasu"])
_labels0={"next":"KernelSU-Next","kernelsu":"KernelSU","bakasu":"BakaSU","sukisu-ultra":"SukiSU-Ultra","finasu":"FinaSU","kowsu":"KowSU"}
_rc=[]
for _fl0 in _flavors0:
    _c=_root_commits.get(_fl0,"")
    if _c and len(_c)==40: _rc.append(f"{_labels0.get(_fl0,_fl0)} [`{_c[:7]}`]({_root_urls[_fl0]}{_c})")
    elif _c: _rc.append(f"{_labels0.get(_fl0,_fl0)} `{_c}`")
for _r in _rc: lines.append(f"- {_r}")
lines.append("")
lines.append("## Features")
lines.append("")
_kp_url="https://github.com/WildKernels/kernel_patches/commit/"
_feat_commit={"NoMount":("https://github.com/maxsteeel/nomount/commit/",nm),"Baseband Guard":(_kp_url,kp),"DroidSpaces-OSS":("https://github.com/ravindu644/Droidspaces-OSS/commit/",ds)}
for f in feats:
    _u,_c=_feat_commit.get(f,("",""))
    if _c and len(_c)==40: lines.append(f"- {f} [`{_c[:7]}`]({_u}{_c})")
    elif _c: lines.append(f"- {f} `{_c}`")
    else: lines.append(f"- {f}")
if not feats: lines.append("- (none)")
kp=env("KERNEL_PATCHES_COMMIT","")
ak=env("ANYKERNEL3_COMMIT","")
ds=env("DROIDSPACES_COMMIT","")
lines.append("")
lines.append("## SUSFS commits")
lines.append("")
all_variants=["android12-5.10","android13-5.10","android13-5.15","android14-5.15","android14-6.1","android15-6.6","android16-6.12"]
def kbv_to_variant(kbv):
    if ".x-android" in kbv:
        kv, av = kbv.split(".x-android", 1)
        v = f"android{av}-{kv}"
        return v if v in all_variants else ""
    return ""
kbv=env("KERNEL_BUILD_VERSION","All")
_sel=kbv_to_variant(kbv)
variants=[_sel] if _sel else list(all_variants)
sus_map={"android12-5.10":env("SUSFS_ANDROID12_5_10",""),"android13-5.10":env("SUSFS_ANDROID13_5_10",""),"android13-5.15":env("SUSFS_ANDROID13_5_15",""),"android14-5.15":env("SUSFS_ANDROID14_5_15",""),"android14-6.1":env("SUSFS_ANDROID14_6_1",""),"android15-6.6":env("SUSFS_ANDROID15_6_6",""),"android16-6.12":env("SUSFS_ANDROID16_6_12","")}
sus_map_bakasu={"android12-5.10":env("SUSFS_ANDROID12_5_10_BAKASU",""),"android13-5.10":env("SUSFS_ANDROID13_5_10_BAKASU",""),"android13-5.15":env("SUSFS_ANDROID13_5_15_BAKASU",""),"android14-5.15":env("SUSFS_ANDROID14_5_15_BAKASU",""),"android14-6.1":env("SUSFS_ANDROID14_6_1_BAKASU",""),"android15-6.6":env("SUSFS_ANDROID15_6_6_BAKASU",""),"android16-6.12":env("SUSFS_ANDROID16_6_12_BAKASU","")}
sus_map_sukisu_ultra={"android12-5.10":env("SUSFS_ANDROID12_5_10_SUKISU_ULTRA",""),"android13-5.10":env("SUSFS_ANDROID13_5_10_SUKISU_ULTRA",""),"android13-5.15":env("SUSFS_ANDROID13_5_15_SUKISU_ULTRA",""),"android14-5.15":env("SUSFS_ANDROID14_5_15_SUKISU_ULTRA",""),"android14-6.1":env("SUSFS_ANDROID14_6_1_SUKISU_ULTRA",""),"android15-6.6":env("SUSFS_ANDROID15_6_6_SUKISU_ULTRA",""),"android16-6.12":env("SUSFS_ANDROID16_6_12_SUKISU_ULTRA","")}
_flavors=[m.get("flavor","") for m in parse_managers(env("MANAGER_LIST","")) if m.get("flavor","")]
if not _flavors:
    _flavors={"KernelSU-Next":["next"],"KernelSU":["kernelsu"],"BakaSU":["bakasu"],"SukiSU-Ultra":["sukisu-ultra"],"KowSU":["kowsu"],"No Root":[],"All":["next","kernelsu","bakasu"]}.get(root,["next","kernelsu","bakasu"])
_labels={"next":"KernelSU-Next","kernelsu":"KernelSU","bakasu":"BakaSU","sukisu-ultra":"SukiSU-Ultra","kowsu":"KowSU"}
_susfs_url="https://gitlab.com/simonpunk/susfs4ksu"
lines.append("| SUSFS branch |" + "".join(f" {_labels.get(_fl,_fl)} |" for _fl in _flavors))
lines.append("|---" * (len(_flavors) + 1) + "|")
for v in variants:
    _row=f"| gki-{v} |"
    for _fl in _flavors:
        # KowSU never ships SUSFS: render n/a rather than shared pins.
        _sm={} if _fl=="kowsu" else (sus_map_sukisu_ultra if _fl=="sukisu-ultra" else (sus_map_bakasu if _fl=="bakasu" else sus_map))
        sha=_sm.get(v,"")
        sha_s=f"[`{sha[:7]}`]({_susfs_url}/-/commit/{sha})" if sha else "_n/a_"
        _row+=f" {sha_s} |"
    lines.append(_row)
lines.append("")
lines.append("")
output="\n".join(lines)+"\n"
print(output,end="")
s=os.environ.get("GITHUB_STEP_SUMMARY")
if s: open(s,"a").write(output)
