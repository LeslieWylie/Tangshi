#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爱如生中国基本古籍库批量导出工具配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 下载设置
DOWNLOAD_CONFIG = {
    # 爱如生中国基本古籍库URL
    "BASE_URL": "http://dh.g.sjuku.top",  # 实际URL
    
    # 搜索页面路径
    "SEARCH_URL": "/spring/front/search",  # 搜索页面路径
    
    # 详情页面路径
    "DETAIL_URL": "/spring/front/jumpread",  # 详情页面路径
    
    # 搜索关键词
    "SEARCH_QUERY": "唐诗",  # 请替换为您的搜索关键词
    
    # 图片保存路径
    "IMAGE_DIR": os.path.join(BASE_DIR, "output", "images"),
    
    # 文本保存路径
    "TEXT_DIR": os.path.join(BASE_DIR, "output", "text"),
    
    # 最大页数，设置为None表示下载所有页面
    "MAX_PAGES": None,
    
    # 每页处理完后的等待时间(秒)
    "PAGE_DELAY": 5,
    
    # 点击元素后的等待时间(秒)
    "CLICK_DELAY": 1,
    
    # 从搜索结果中处理的最大条目数，设置为None表示处理所有条目
    "MAX_ITEMS": None,
}

# 浏览器设置
BROWSER_CONFIG = {
    # 是否启用无头模式（不显示浏览器窗口）
    "HEADLESS": False,
    
    # 浏览器窗口大小
    "WINDOW_SIZE": (1920, 1080),
    
    # WebDriver等待超时时间(秒)
    "WAIT_TIMEOUT": 10,
    
    # ChromeDriver路径，设置为None表示自动查找
    "CHROME_DRIVER_PATH": None,
}

# Cookie设置
COOKIES = {
    "ddhgguuy_session": "uk496de3r6fv8luiptmut86vuj",
    "JSESSIONID": "64DF3F552061EBA1576A66990470948C"
}

# Cookie字符串形式（如果您更喜欢直接粘贴整个字符串）
COOKIE_STRING = "ddhgguuy_session=uk496de3r6fv8luiptmut86vuj; JSESSIONID=64DF3F552061EBA1576A66990470948C"

# 爱如生网站元素选择器
SELECTORS = {
    # 登录相关
    "LOGIN": {
        "USERNAME_INPUT": "15379993153",
        "PASSWORD_INPUT": "wyl041016",
        "SUBMIT_BUTTON": "//button[@type='submit']",
    },
    
    # 搜索相关
    "SEARCH": {
        "SEARCH_INPUT": "input[type='text'], #ikeyword, #searchInput, input[name='keyword'], .search-input",  # 使用多个可能的选择器
        "SEARCH_BUTTON": "#search_btn, button[type='submit'], input[type='submit'], .search-button, button:contains('搜索'), button:contains('检索')",  # 使用多个可能的选择器
    },
    
    # 搜索结果列表相关
    "RESULTS": {
        "ITEM_LINKS": "//div[contains(@class, 'st')]/a | //div[contains(@class, 'g')]/a | //div[contains(@id, 'item_')]/a",
        "NEXT_PAGE": "//a[contains(text(), '下一页') or contains(@aria-label, 'Next') or contains(@title, '下一页')] | //div[@class='pagebox']/a[contains(text(), '>')]",
    },
    
    # 详情页相关
    "DETAIL": {
        "IMAGES": "#imgI_1 | #imgI_2 | #imgCtrl img",
        "DOWNLOAD_BUTTON": "//button[contains(text(), '下载') or contains(@title, '下载')] | //a[contains(text(), '下载') or contains(@title, '下载')]",
        "TEXT_CONTENT": "#htmlContent | #div_htmlContent | .book-text",
        "BACK_BUTTON": "//button[contains(text(), '返回') or contains(@title, '返回')] | //a[contains(text(), '返回') or contains(@title, '返回')]",
    },
}

# 日志设置
LOG_CONFIG = {
    "LEVEL": "INFO",  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
    "FILE": os.path.join(BASE_DIR, "output", "downloader.log"),
}

# 登录信息 (如需登录，请填写)
AUTH = {
    "USERNAME": "15379993153",  # 请替换为您的用户名
    "PASSWORD": "wyl123456",  # 请替换为您的密码
} 