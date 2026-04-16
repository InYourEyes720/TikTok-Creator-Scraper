import time
import csv
import re
import html
import os
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# -------------------- 配置 --------------------
ids = [
"jillybean271",
"kimkim.1223",
"lisdamarysalvarez",
"ameehyerimi"
]

# 自动生成完整 URL
urls = [f"https://www.tiktok.com/@{id_.strip()}" for id_ in ids]
urls = list(enumerate(urls))  # [(0, url0), (1, url1), ...]

bio_domains = ["linktr.ee", "beacons.ai", "beacons.page", "carrd.co",
               "linkin.bio", "tap.bio", "bio.link", "withkoji.com",
               "flow.page", "stan.store", "direct.me"]

output_dir = r"D:\TikTokData\Output"
os.makedirs(output_dir, exist_ok=True)

batch_size = 1000

invalid_keywords = [
    "couldn't find this account",
    "video currently unavailable",
    "找不到此账号",
]

# -------------------- ChromeDriver 创建 --------------------
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)
    return driver

# -------------------- 工具函数 --------------------
def extract_followers_from_desc(desc_text):
    m = re.search(r'([\d,.]+[kKmM]?)\s+Followers', desc_text)
    return m.group(1).upper() if m else "N/A"

def extract_email(text):
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else "N/A"

def extract_external_email(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return extract_email(r.text)
    except:
        return "N/A"

def export_csv(data, suffix):
    file_path = os.path.join(output_dir, f"result_{suffix}.csv")
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "URL", "Status", "Followers", "Email", "External_Link", "External_Email"])
        writer.writerows(data)
    print(f"✅ 已导出：{file_path}")

# -------------------- worker 函数 --------------------
def worker(sub_urls):
    driver = create_driver()
    sub_results = []
    local_batch = []

    for count, (idx, url) in enumerate(sub_urls, start=1):
        status = 0
        followers = "N/A"
        email = "N/A"
        external_link = "N/A"
        external_email = "N/A"

        # 自动从 URL 提取 ID
        id_part = url.split("@")[-1]

        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(random.uniform(1.5, 2.5))

            page_source = driver.page_source
            body_text = driver.find_element(By.TAG_NAME, "body").text

            if any(kw.lower() in body_text.lower() for kw in invalid_keywords):
                status = 0
            else:
                status = 1
                m_desc = re.search(r'"shareMeta"\s*:\s*\{[^}]*?"desc"\s*:\s*"([^"]+)"', page_source)
                if m_desc:
                    followers = extract_followers_from_desc(m_desc.group(1))

                email = extract_email(page_source)

                decoded_source = html.unescape(page_source)
                patterns = [
                    r'"bioLink"\s*:\s*\{"link"\s*:\s*"([^"]+)"',
                    r'"externalUrl"\s*:\s*"([^"]+)"',
                    r'"externalLink"\s*:\s*"([^"]+)"',
                    r'"shareMeta"\s*:\s*\{"link"\s*:\s*"([^"]+)"'
                ]
                for pat in patterns:
                    match = re.search(pat, decoded_source)
                    if match:
                        raw_link = match.group(1)
                        external_link = raw_link.encode("utf-8").decode("unicode_escape").replace("\\/", "/")
                        break
                if external_link == "N/A":
                    all_urls = re.findall(r'https?://[^\s"\'<>]+', decoded_source)
                    for u in all_urls:
                        if any(domain in u.lower() for domain in bio_domains):
                            external_link = u.replace("\\/", "/")
                            break
                if external_link != "N/A":
                    external_email = extract_external_email(external_link)

        except Exception as e:
            print(f"❌ 出错: {url} -> {e}")
            status = 0

        print(idx, url, status, followers, email, external_link, external_email)

        row = [id_part, url, status, followers, email, external_link, external_email]
        sub_results.append(row)
        local_batch.append(row)

        # 每 batch_size 条导出一次
        if len(local_batch) >= batch_size:
            export_csv(local_batch, f"batch_{idx}")
            local_batch = []

    # 导出剩余不足 batch_size 的数据
    if local_batch:
        export_csv(local_batch, f"batch_{idx}_last")

    driver.quit()
    return sub_results

# -------------------- 分块函数 --------------------
def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

# -------------------- 并发执行 --------------------
chunks = split_list(urls, 2)  # 可根据 CPU/带宽调整
results = []
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(worker, chunk) for chunk in chunks]
    for future in as_completed(futures):
        results.extend(future.result())

# -------------------- 最终汇总（按提供 id 顺序排序） --------------------
# 保留 ID 列
clean_results = [r for r in results]

# 按你提供的 ids 顺序排序
id_order = [id_.strip() for id_ in ids]
clean_results.sort(key=lambda x: id_order.index(x[0]))

now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
export_csv(clean_results, f"final_{now}")

print("🎉 全部完成，已生成最终汇总表（按原始 ID 顺序）")