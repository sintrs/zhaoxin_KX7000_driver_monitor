#!/usr/bin/env python3
"""
兆芯驱动版本监控脚本（GitHub Actions 版）
内置固定版本号，检测到不同即推送 Server 酱

监控页面：https://www.zhaoxin.com/qdxz.aspx?nid=31&typeid=600
匹配模式：KX-7000-Linux OS_x64-{版本号}
"""

import os
import sys
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


# ============ 配置 ============
URL = "https://www.zhaoxin.com/qdxz.aspx?nid=31&typeid=600"
PREFIX = "KX-7000-Linux OS_x64"

# 内置固定版本号（当前已知的版本）
# 当推送通知后，手动更新此版本号并提交到仓库
BASELINE_VERSION = "26.00.48"

# Server 酱配置（从环境变量读取，GitHub Secrets 注入）
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "")


def now():
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_page():
    """抓取网页内容"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        resp = requests.get(URL, headers=headers, timeout=30)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except requests.RequestException as e:
        print(f"[{now()}] 请求失败: {e}")
        return None


def parse_version(html):
    """
    解析页面中的驱动版本号
    匹配模式：KX-7000-Linux OS_x64-{版本号}
    返回：版本号字符串（如 "26.00.48"），未找到返回 None
    """
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # 策略1：在链接文本中查找
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        pattern = re.escape(PREFIX) + r"[-_\s]*(\d+\.\d+\.\d+)"
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    # 策略2：在全文中搜索
    full_text = soup.get_text()
    pattern = re.escape(PREFIX) + r"[-_\s]*(\d+\.\d+\.\d+)"
    match = re.search(pattern, full_text)
    if match:
        return match.group(1)

    # 策略3：在前缀附近查找版本号
    if PREFIX in full_text:
        idx = full_text.find(PREFIX)
        nearby = full_text[idx:idx + 150]
        match = re.search(r"(\d{2}\.\d{2}\.\d{2})", nearby)
        if match:
            return match.group(1)

    return None


def send_serverchan(title, content):
    """通过 Server 酱推送到微信"""
    if not SERVERCHAN_KEY or not SERVERCHAN_KEY.startswith("SCT"):
        print(f"[{now()}] Server 酱未配置，跳过推送")
        return False

    try:
        url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
        payload = {"title": title, "desp": content}
        resp = requests.post(url, data=payload, timeout=10)
        result = resp.json()

        if result.get("code") == 0:
            print(f"[{now()}] ✅ Server 酱推送成功")
            return True
        else:
            print(f"[{now()}] ❌ Server 酱推送失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"[{now()}] ❌ Server 酱请求异常: {e}")
        return False


def check():
    """执行检查"""
    print(f"[{now()}] 开始检查...")
    print(f"[{now()}] 基准版本: {BASELINE_VERSION}")

    html = fetch_page()
    if not html:
        print(f"[{now()}] 获取页面失败，退出")
        return 1

    current_version = parse_version(html)
    print(f"[{now()}] 网页检测到版本: {current_version or '未找到'}")

    if not current_version:
        print(f"[{now()}] ⚠️ 未找到版本号，请检查网页结构")
        return 1

    if current_version == BASELINE_VERSION:
        print(f"[{now()}] ✅ 版本未变化 ({current_version})，无需推送")
        return 0

    # 版本不同，推送通知
    print(f"[{now()}] 🔔 发现新版本！{BASELINE_VERSION} → {current_version}")

    title = f"🔔 兆芯驱动更新提醒：{current_version}"
    content = f"""兆芯驱动检测到新版本！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
驱动型号：{PREFIX}
基准版本：{BASELINE_VERSION}
新版本：{current_version}
检测时间：{now()}
下载页面：{URL}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请及时下载更新。
"""

    # 控制台输出
    print(f"
{'='*55}")
    print(content)
    print(f"{'='*55}
")

    # 推送到微信
    send_serverchan(title, content)

    return 0


if __name__ == "__main__":
    sys.exit(check())
