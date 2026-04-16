# 🚀 TikTok Creator Scraper -- Extract Emails, Followers & Bio Links

## 📌 Description

A concurrent TikTok creator scraper that extracts account validity,
profile URLs, followers, emails, and emails from bio links.

------------------------------------------------------------------------

## 🧠 中文简介

一个基于并发浏览器自动化的 TikTok
达人数据抓取工具，支持批量提取账号有效性、主页链接、粉丝数、邮箱，以及
Bio 外链中的邮箱信息。

------------------------------------------------------------------------

## ✨ Features

-   Batch scrape TikTok creator data\
-   Extract followers, emails, and bio links\
-   Parse emails from Link-in-bio tools\
-   Concurrent browser automation (faster scraping)\
-   Export results to CSV

------------------------------------------------------------------------
## 📖 Tutorial / 教程指南

👉 Full guide available here:
https://www.notion.so/TK-by-Eth-344e7d9efd848061a892d4503cb1ff86

------------------------------------------------------------------------

## 🛠️ Installation

### 1. Install Python

Download: https://www.python.org/
Version: Python 3.9+

------------------------------------------------------------------------

### 2. Install Dependencies

``` bash
pip install selenium requests
```

------------------------------------------------------------------------

### 3. Install Chrome & ChromeDriver

-   Install Google Chrome\
-   Check version: chrome://version/\
-   Download matching ChromeDriver\
-   Place it in the same folder as script

------------------------------------------------------------------------

## 🚀 Usage

### 1. Edit IDs

``` python
ids = [
    "username1",
    "username2"，
    "username3"，
    "username4"
]
```

------------------------------------------------------------------------

### 2. Set Output Path

``` python
output_dir = r"D:\TikTokData\Output"
```

------------------------------------------------------------------------

### 3. Run Script

``` bash
python tiktok-creator-scraper.py
```

------------------------------------------------------------------------

## 📊 Output

-   result_batch_xxx.csv\
-   result_final_xxx.csv

------------------------------------------------------------------------

## ⚠️ Disclaimer

This project is for educational purposes only. Do not use it in
violation of TikTok's terms of service.
