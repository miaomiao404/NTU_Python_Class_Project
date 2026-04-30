"""
自動下載開源中文字體到 fonts/ 資料夾
執行方式: python download_fonts.py
"""

import os
import zipfile
import requests

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)


def _download_file(url, dest_path):
    try:
        r = requests.get(url, timeout=120, stream=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"    ✗ 下載失敗: {e}")
        return False


def download_direct(url, filename, name):
    """直接下載單一字體檔"""
    print(f"  → {name}")
    dest = os.path.join(FONTS_DIR, filename)
    if os.path.exists(dest):
        print(f"    ✓ 已存在，略過: {filename}")
        return True
    if _download_file(url, dest):
        print(f"    ✓ {filename}")
        return True
    return False


def download_github_release(repo, keywords, name, extract_filter=None):
    """從 GitHub 最新 Release 下載字體"""
    print(f"  → GitHub: {repo}")
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        r = requests.get(api_url, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        assets = r.json().get("assets", [])
    except Exception as e:
        print(f"    ✗ 無法取得 release 資訊: {e}")
        return False

    for asset in assets:
        aname = asset["name"]
        if not any(k.lower() in aname.lower() for k in keywords):
            continue
        url = asset["browser_download_url"]
        dest = os.path.join(FONTS_DIR, aname)

        if not _download_file(url, dest):
            continue

        if aname.lower().endswith(".zip"):
            extracted = []
            try:
                with zipfile.ZipFile(dest, "r") as z:
                    for member in z.namelist():
                        if not member.lower().endswith((".ttf", ".otf")):
                            continue
                        if extract_filter and not any(
                            k.lower() in member.lower() for k in extract_filter
                        ):
                            continue
                        bname = os.path.basename(member)
                        if not bname:
                            continue
                        out = os.path.join(FONTS_DIR, bname)
                        with open(out, "wb") as f:
                            f.write(z.read(member))
                        extracted.append(bname)
            except Exception as e:
                print(f"    ✗ 解壓失敗: {e}")
                os.remove(dest)
                return False
            os.remove(dest)
            for f in extracted:
                print(f"    ✓ {f}")
            return len(extracted) > 0
        else:
            print(f"    ✓ {aname}")
            return True

    print(f"    ✗ 找不到符合的檔案（關鍵字: {keywords}）")
    return False


# ── 字體清單 ────────────────────────────────────────────────────────
#
# 來源一：Google Fonts → 改從 github.com/google/fonts 直接抓 raw 檔
# 來源二：各 GitHub repo 的 Release
# ────────────────────────────────────────────────────────────────────

GOOGLE_FONTS_BASE = "https://github.com/google/fonts/raw/main/ofl"

FONT_LIST = [
    # ── 毛筆 / 行書 / 楷書（Google Fonts via GitHub raw）────────────
    {"type": "direct",
     "name": "馬尚正楷 Ma Shan Zheng",
     "url": f"{GOOGLE_FONTS_BASE}/mashanzheng/MaShanZheng-Regular.ttf",
     "filename": "MaShanZheng-Regular.ttf"},

    {"type": "direct",
     "name": "之芒行書 Zhi Mang Xing",
     "url": f"{GOOGLE_FONTS_BASE}/zhimangxing/ZhiMangXing-Regular.ttf",
     "filename": "ZhiMangXing-Regular.ttf"},

    {"type": "direct",
     "name": "龍藏草書 Long Cang",
     "url": f"{GOOGLE_FONTS_BASE}/longcang/LongCang-Regular.ttf",
     "filename": "LongCang-Regular.ttf"},

    {"type": "direct",
     "name": "ZCOOL QingKe HuangYou",
     "url": f"{GOOGLE_FONTS_BASE}/zcoolqingkehuangyou/ZCOOLQingKeHuangYou-Regular.ttf",
     "filename": "ZCOOLQingKeHuangYou-Regular.ttf"},

    {"type": "direct",
     "name": "ZCOOL KuaiLe 圓體",
     "url": f"{GOOGLE_FONTS_BASE}/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf",
     "filename": "ZCOOLKuaiLe-Regular.ttf"},

    {"type": "direct",
     "name": "流間毛草 Liu Jian Mao Cao",
     "url": f"{GOOGLE_FONTS_BASE}/liujianmaocao/LiuJianMaoCao-Regular.ttf",
     "filename": "LiuJianMaoCao-Regular.ttf"},

    {"type": "direct",
     "name": "ZCOOL XiaoWei 小薇",
     "url": f"{GOOGLE_FONTS_BASE}/zcoolxiaowei/ZCOOLXiaoWei-Regular.ttf",
     "filename": "ZCOOLXiaoWei-Regular.ttf"},

    # Noto Sans/Serif TC：variable font，從 google/fonts repo 抓
    {"type": "direct",
     "name": "Noto Sans TC 思源黑體（繁中）",
     "url": f"{GOOGLE_FONTS_BASE}/notosanstc/NotoSansTC%5Bwght%5D.ttf",
     "filename": "NotoSansTC-VF.ttf"},

    {"type": "direct",
     "name": "Noto Serif TC 思源宋體（繁中）",
     "url": f"{GOOGLE_FONTS_BASE}/notoseriftc/NotoSerifTC%5Bwght%5D.ttf",
     "filename": "NotoSerifTC-VF.ttf"},

    # Noto Sans SC（簡體黑體，字形涵蓋廣）
    {"type": "direct",
     "name": "Noto Sans SC 思源黑體（簡中）",
     "url": f"{GOOGLE_FONTS_BASE}/notosanssc/NotoSansSC%5Bwght%5D.ttf",
     "filename": "NotoSansSC-VF.ttf"},

    # ── 半手寫楷書（GitHub Release）──────────────────────────────────
    {"type": "github",
     "name": "霞鶩文楷 LXGW WenKai",
     "repo": "lxgw/LxgwWenKai",
     "keywords": ["LXGWWenKai-Regular.ttf"],
     "extract_filter": None},

    {"type": "github",
     "name": "霞鶩文楷 TC 繁中版",
     "repo": "lxgw/LxgwWenkaiTC",
     "keywords": ["Regular.ttf"],
     "extract_filter": None},

    # ── 圓體（GitHub Release）────────────────────────────────────────
    {"type": "github",
     "name": "jf open 粉圓",
     "repo": "justfont/open-huninn-font",
     "keywords": [".ttf"],
     "extract_filter": None},


    # Noto Serif SC（簡中宋體，風格與繁中近似）
    {"type": "direct",
     "name": "Noto Serif SC 宋體（簡中）",
     "url": f"{GOOGLE_FONTS_BASE}/notoserifsc/NotoSerifSC%5Bwght%5D.ttf",
     "filename": "NotoSerifSC-VF.ttf"},

    # ── 思源系列（Adobe，GitHub Release）────────────────────────────
    {"type": "github",
     "name": "思源黑體 Source Han Sans TC",
     "repo": "adobe-fonts/source-han-sans",
     "keywords": ["10_SourceHanSansTC.zip"],
     "extract_filter": ["Regular"]},

    {"type": "github",
     "name": "思源宋體 Source Han Serif TC",
     "repo": "adobe-fonts/source-han-serif",
     "keywords": ["10_SourceHanSerifTC.zip"],
     "extract_filter": ["Regular"]},

    # ── 古典 / 手寫 / 特殊風格（GitHub Release）─────────────────────
    {"type": "github",
     "name": "齊伋體 QiJi（明代木刻風）",
     "repo": "LingDong-/qiji-font",
     "keywords": [".ttf", ".otf"],
     "extract_filter": None},

    {"type": "github",
     "name": "芫荽 Iansui 手寫楷書",
     "repo": "ButTaiwan/iansui",
     "keywords": [".zip", ".ttf"],
     "extract_filter": None},

    {"type": "github",
     "name": "研習明體 StudyMing",
     "repo": "project-ccs/StudyMing",
     "keywords": [".ttf", ".otf"],
     "extract_filter": None},

    # ── 像素體（GitHub Release）─────────────────────────────────────
    {"type": "github",
     "name": "Zpix 像素字體",
     "repo": "SolidZORO/zpix-pixel-font",
     "keywords": [".ttf"],
     "extract_filter": None},

    # ── 手動下載 ─────────────────────────────────────────────────────
    {"type": "manual",
     "name": "全字庫正宋體 TW-Sung",
     "url": "https://data.gov.tw/dataset/5961"},

    {"type": "manual",
     "name": "全字庫正楷體 TW-Kai",
     "url": "https://data.gov.tw/dataset/5961"},
]


def main():
    print(f"目標資料夾: {FONTS_DIR}\n{'='*50}")
    success, failed, manual = [], [], []

    for font in FONT_LIST:
        print(f"\n【{font['name']}】")

        if font["type"] == "direct":
            ok = download_direct(font["url"], font["filename"], font["name"])
        elif font["type"] == "github":
            ok = download_github_release(
                font["repo"], font["keywords"], font["name"],
                font.get("extract_filter"),
            )
        else:
            print(f"  ⚠  請手動下載: {font.get('url', '')}")
            manual.append(font["name"])
            continue

        (success if ok else failed).append(font["name"])

    print(f"\n{'='*50}")
    print(f"✓ 自動下載成功: {len(success)} 套")
    if failed:
        print(f"✗ 自動下載失敗（{len(failed)} 套）:")
        for f in failed:
            print(f"  - {f}")
    if manual:
        print(f"⚠  需手動下載（{len(manual)} 套）:")
        for f in manual:
            print(f"  - {f}")
    print(f"\n字體檔案位置: {FONTS_DIR}")


if __name__ == "__main__":
    main()
