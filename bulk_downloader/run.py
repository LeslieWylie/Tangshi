#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爱如生中国基本古籍库批量下载工具
主入口文件
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到系统路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 导入自定义模块
from src.downloader import AirushengDownloader
from src.utils import logger, check_environment
from config.settings import DOWNLOAD_CONFIG, BROWSER_CONFIG, AUTH, COOKIES, COOKIE_STRING

def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="爱如生中国基本古籍库批量下载工具")
    
    # 基本参数
    parser.add_argument("-u", "--url", type=str, help="爱如生中国基本古籍库URL")
    parser.add_argument("-q", "--query", type=str, help="搜索关键词")
    parser.add_argument("--image-dir", type=str, help="图片保存路径")
    parser.add_argument("--text-dir", type=str, help="文本保存路径")
    parser.add_argument("-p", "--pages", type=int, help="最大页数，默认为所有页面")
    parser.add_argument("-m", "--max-items", type=int, help="处理的最大条目数，默认为所有条目")
    
    # Cookie参数
    parser.add_argument("--cookie", type=str, help="Cookie字符串，例如'name1=value1; name2=value2'")
    
    # 登录参数
    parser.add_argument("--username", type=str, help="登录用户名")
    parser.add_argument("--password", type=str, help="登录密码")
    
    # 浏览器参数
    parser.add_argument("--headless", action="store_true", help="启用无头模式（不显示浏览器窗口）")
    parser.add_argument("--driver", type=str, help="ChromeDriver路径")
    
    # 高级参数
    parser.add_argument("--page-delay", type=int, help="每页处理完后的等待时间(秒)")
    parser.add_argument("--click-delay", type=int, help="点击元素后的等待时间(秒)")
    
    return parser.parse_args()

def update_settings(args):
    """
    根据命令行参数更新配置
    
    Args:
        args (argparse.Namespace): 命令行参数
    """
    global COOKIE_STRING
    
    # 更新下载设置
    if args.url:
        DOWNLOAD_CONFIG["BASE_URL"] = args.url
    
    if args.query:
        DOWNLOAD_CONFIG["SEARCH_QUERY"] = args.query
    
    if args.image_dir:
        DOWNLOAD_CONFIG["IMAGE_DIR"] = os.path.abspath(args.image_dir)
    
    if args.text_dir:
        DOWNLOAD_CONFIG["TEXT_DIR"] = os.path.abspath(args.text_dir)
    
    if args.pages is not None:
        DOWNLOAD_CONFIG["MAX_PAGES"] = args.pages
    
    if args.max_items is not None:
        DOWNLOAD_CONFIG["MAX_ITEMS"] = args.max_items
    
    if args.page_delay is not None:
        DOWNLOAD_CONFIG["PAGE_DELAY"] = args.page_delay
    
    if args.click_delay is not None:
        DOWNLOAD_CONFIG["CLICK_DELAY"] = args.click_delay
    
    # 更新Cookie
    if args.cookie:
        COOKIE_STRING = args.cookie
        # 解析Cookie字符串为字典
        cookies_dict = {}
        for item in args.cookie.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies_dict[name] = value
        
        # 更新COOKIES字典
        COOKIES.clear()
        COOKIES.update(cookies_dict)
    
    # 更新浏览器设置
    if args.headless:
        BROWSER_CONFIG["HEADLESS"] = True
    
    if args.driver:
        BROWSER_CONFIG["CHROME_DRIVER_PATH"] = os.path.abspath(args.driver)
    
    # 更新登录信息
    if args.username:
        AUTH["USERNAME"] = args.username
    
    if args.password:
        AUTH["PASSWORD"] = args.password

def print_banner():
    """打印启动横幅"""
    banner = """
    ╭──────────────────────────────────────────────╮
    │                                              │
    │     爱如生中国基本古籍库批量下载工具         │
    │                                              │
    ╰──────────────────────────────────────────────╯
    """
    print(banner)

def print_settings():
    """打印当前设置"""
    print("\n当前设置:")
    print(f"- 目标URL: {DOWNLOAD_CONFIG['BASE_URL']}")
    print(f"- 搜索关键词: {DOWNLOAD_CONFIG['SEARCH_QUERY']}")
    print(f"- 图片保存路径: {DOWNLOAD_CONFIG['IMAGE_DIR']}")
    print(f"- 文本保存路径: {DOWNLOAD_CONFIG['TEXT_DIR']}")
    print(f"- 最大页数: {DOWNLOAD_CONFIG['MAX_PAGES'] or '所有页面'}")
    print(f"- 最大条目数: {DOWNLOAD_CONFIG['MAX_ITEMS'] or '所有条目'}")
    print(f"- 每页延迟: {DOWNLOAD_CONFIG['PAGE_DELAY']}秒")
    print(f"- 无头模式: {'启用' if BROWSER_CONFIG['HEADLESS'] else '禁用'}")
    print(f"- Cookie状态: {'已配置' if COOKIES or COOKIE_STRING else '未配置'}")
    print(f"- 登录状态: {'已配置' if AUTH['USERNAME'] and AUTH['PASSWORD'] else '未配置'}")
    print()

def check_config():
    """
    检查配置是否有效
    
    Returns:
        bool: 配置是否有效
    """
    # 检查URL
    if not DOWNLOAD_CONFIG.get("BASE_URL") or DOWNLOAD_CONFIG.get("BASE_URL") == "https://www.example.com/airusheng":
        logger.error("错误: 未设置有效的目标URL，请在settings.py中设置BASE_URL或使用命令行参数--url")
        return False
    
    # 检查搜索关键词（如果没有使用Cookie）
    if not DOWNLOAD_CONFIG.get("SEARCH_QUERY") and not (COOKIES or COOKIE_STRING):
        logger.warning("警告: 未设置搜索关键词，如果不是直接访问搜索结果页面，可能无法正常工作")
    
    # 确保输出目录存在
    os.makedirs(DOWNLOAD_CONFIG.get("IMAGE_DIR"), exist_ok=True)
    os.makedirs(DOWNLOAD_CONFIG.get("TEXT_DIR"), exist_ok=True)
    
    return True

def main():
    """主函数"""
    # 打印启动横幅
    print_banner()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 更新配置
    update_settings(args)
    
    # 打印当前设置
    print_settings()
    
    # 检查配置是否有效
    if not check_config():
        return
    
    # 检查运行环境
    env_info = check_environment()
    logger.debug(f"运行环境: {env_info}")
    
    try:
        # 创建下载器
        downloader = AirushengDownloader()
        
        # 启动下载器，传递URL参数
        url = args.url if args.url else DOWNLOAD_CONFIG["BASE_URL"]
        downloader.start(url)
        
        logger.info("爬虫任务完成")
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
        # 尝试关闭downloader
        if 'downloader' in locals():
            downloader.close()
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        logger.exception("详细错误信息:")
        # 尝试关闭downloader
        if 'downloader' in locals():
            downloader.close()

if __name__ == "__main__":
    main() 