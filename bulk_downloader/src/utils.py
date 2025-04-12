#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爱如生中国基本古籍库批量导出工具辅助函数
"""

import os
import sys
import time
import logging
import platform
import requests
import uuid
import re
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 导入配置
from config.settings import LOG_CONFIG, DOWNLOAD_CONFIG

def setup_logging(log_file=None, log_level=None, log_format=None):
    """
    设置日志
    
    Args:
        log_file (str, optional): 日志文件路径
        log_level (str, optional): 日志级别
        log_format (str, optional): 日志格式
        
    Returns:
        logging.Logger: 日志对象
    """
    # 使用配置中的参数或默认值
    log_file = log_file or LOG_CONFIG.get("FILE")
    log_level = log_level or LOG_CONFIG.get("LEVEL", "INFO")
    log_format = log_format or LOG_CONFIG.get("FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
    
    # 创建日志目录
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # 配置日志
    logger = logging.getLogger("airusheng_downloader")
    logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    logger.info("日志系统初始化完成")
    return logger

def get_image_save_path(title=None, page_num=None, image_url=None, extension=".jpg"):
    """
    获取图片保存路径
    
    Args:
        title (str, optional): 书名或标题
        page_num (int, optional): 页码
        image_url (str, optional): 图片URL
        extension (str, optional): 文件扩展名，默认为.jpg
        
    Returns:
        str: 完整的文件保存路径
    """
    # 使用配置中的图片保存目录
    image_dir = DOWNLOAD_CONFIG.get("IMAGE_DIR")
    
    # 创建下载目录
    os.makedirs(image_dir, exist_ok=True)
    
    # 如果有标题，创建以标题命名的子目录
    if title:
        # 清理标题，去除非法字符
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        title = title.strip()
        sub_dir = os.path.join(image_dir, title)
        os.makedirs(sub_dir, exist_ok=True)
        image_dir = sub_dir
    
    # 构建文件名
    if page_num is not None and title:
        # 使用标题和页码
        filename = f"{title}_第{page_num}页"
    elif image_url:
        # 使用URL的哈希值作为文件名
        filename = hashlib.md5(image_url.encode()).hexdigest()
    else:
        # 使用UUID作为文件名
        filename = str(uuid.uuid4())
    
    # 确保文件名有正确的扩展名
    if not filename.lower().endswith(extension.lower()):
        filename = f"{filename}{extension}"
    
    return os.path.join(image_dir, filename)

def get_text_save_path(title=None, page_num=None, extension=".txt"):
    """
    获取文本保存路径
    
    Args:
        title (str, optional): 书名或标题
        page_num (int, optional): 页码
        extension (str, optional): 文件扩展名，默认为.txt
        
    Returns:
        str: 完整的文件保存路径
    """
    # 使用配置中的文本保存目录
    text_dir = DOWNLOAD_CONFIG.get("TEXT_DIR")
    
    # 创建下载目录
    os.makedirs(text_dir, exist_ok=True)
    
    # 如果有标题，创建以标题命名的子目录
    if title:
        # 清理标题，去除非法字符
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        title = title.strip()
        sub_dir = os.path.join(text_dir, title)
        os.makedirs(sub_dir, exist_ok=True)
        text_dir = sub_dir
    
    # 构建文件名
    if page_num is not None and title:
        # 使用标题和页码
        filename = f"{title}_第{page_num}页"
    else:
        # 使用时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"text_{timestamp}"
    
    # 确保文件名有正确的扩展名
    if not filename.lower().endswith(extension.lower()):
        filename = f"{filename}{extension}"
    
    return os.path.join(text_dir, filename)

def download_image(image_url, save_path, base_url=None, headers=None, max_attempts=4, retry_delay=2):
    """
    下载图片，支持重试机制
    
    Args:
        image_url (str): 图片URL
        save_path (str): 保存路径
        base_url (str, optional): 基础URL，用于处理相对路径
        headers (dict, optional): 请求头
        max_attempts (int, optional): 最大尝试次数，默认为4
        retry_delay (int, optional): 重试延迟秒数，默认为2
        
    Returns:
        bool: 下载是否成功
    """
    # 处理相对URL
    if base_url and not urlparse(image_url).netloc:
        image_url = urljoin(base_url, image_url)
    
    # 设置默认请求头
    if not headers:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Referer": base_url or image_url  # 添加Referer头，有助于绕过一些防盗链
        }
    
    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # 重试下载逻辑
    for attempt in range(max_attempts):
        try:
            # 发送请求
            response = requests.get(image_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # 判断响应内容类型是否为图片
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith(('image/', 'application/octet-stream')):
                # 检查请求是否被重定向到登录页或错误页
                if '请重新进入' in response.text or 'login' in response.text.lower():
                    logger.warning(f"请求被重定向到登录页，cookie可能已过期: {image_url}")
                    if attempt == max_attempts - 1:
                        return False
                    time.sleep(retry_delay)
                    continue
            
            # 保存图片
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            # 检查文件大小，如果太小可能是错误图片
            file_size = os.path.getsize(save_path)
            if file_size < 1000:  # 小于1KB的文件可能是错误图片
                logger.warning(f"下载的图片大小异常 ({file_size} 字节)，可能需要重试: {image_url}")
                if attempt == max_attempts - 1:
                    return True  # 尽管文件小，但我们仍然保留它
                time.sleep(retry_delay)
                continue
            
            logger.debug(f"图片已成功保存 (尝试 {attempt+1}/{max_attempts}): {save_path}")
            return True
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"连接错误，尝试 {attempt+1}/{max_attempts}: {image_url}")
        except requests.exceptions.Timeout:
            logger.warning(f"请求超时，尝试 {attempt+1}/{max_attempts}: {image_url}")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
            logger.warning(f"HTTP错误 {status_code}，尝试 {attempt+1}/{max_attempts}: {image_url}")
        except Exception as e:
            logger.warning(f"下载图片失败，尝试 {attempt+1}/{max_attempts}: {str(e)}")
        
        # 如果不是最后一次尝试，等待后重试
        if attempt < max_attempts - 1:
            time.sleep(retry_delay)
    
    logger.error(f"下载图片失败，已达到最大尝试次数 ({max_attempts}): {image_url}")
    return False

def save_text(text, save_path, mode="w", encoding="utf-8"):
    """
    保存文本内容到文件
    
    Args:
        text (str): 要保存的文本
        save_path (str): 保存路径
        mode (str, optional): 文件打开模式，默认为w
        encoding (str, optional): 文件编码，默认为utf-8
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存文本
        with open(save_path, mode, encoding=encoding) as file:
            file.write(text)
        
        logger.debug(f"文本已保存: {save_path}")
        return True
    except Exception as e:
        logger.error(f"保存文本失败: {str(e)}")
        return False

def clean_text(text):
    """
    清理文本
    
    Args:
        text (str): 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[\r\n\t]+', '\n', text)
    # 移除连续的换行符
    text = re.sub(r'\n+', '\n', text)
    # 去除首尾空白
    text = text.strip()
    
    return text

def is_xpath(selector):
    """
    判断选择器是否为XPath
    
    Args:
        selector (str): 元素选择器
        
    Returns:
        bool: 如果是XPath返回True，否则返回False
    """
    # 简单判断是否为XPath选择器
    return selector.startswith("/") or selector.startswith("./") or selector.startswith("(")

def extract_title_from_url(url):
    """
    从URL中提取标题信息
    
    Args:
        url (str): URL字符串
        
    Returns:
        str: 提取的标题或默认标题
    """
    try:
        # 解析URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        
        # 尝试从URL路径中提取标题
        if '/jumpread' in path:
            # 针对爱如生详情页面的URL格式进行提取
            # 例如: /spring/front/jumpread?bookId=xxxx&sheetId=yyyy
            
            # 从查询参数中提取bookId或sheetId
            book_id = None
            sheet_id = None
            
            # 解析查询参数
            if query:
                params = query.split('&')
                for param in params:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        if key == 'bookId':
                            book_id = value
                        elif key == 'sheetId':
                            sheet_id = value
            
            # 生成标题
            if book_id and sheet_id:
                return f"书籍_{book_id}_页面_{sheet_id}"
            elif book_id:
                return f"书籍_{book_id}"
            elif sheet_id:
                return f"页面_{sheet_id}"
        
        # 如果无法提取，创建基于时间戳的默认标题
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"页面_{timestamp}"
    
    except Exception as e:
        logger.error(f"从URL提取标题失败: {str(e)}")
        # 返回默认标题
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"页面_{timestamp}"

def check_environment():
    """
    检查运行环境
    
    Returns:
        dict: 环境信息
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "node": platform.node(),
        "processor": platform.processor()
    }

def wait_with_progress(seconds, message="等待中"):
    """
    带进度提示的等待
    
    Args:
        seconds (int): 等待秒数
        message (str, optional): 等待消息
    """
    for i in range(seconds):
        remaining = seconds - i
        sys.stdout.write(f"\r{message}... {remaining}秒 ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

# 初始化日志
logger = setup_logging()

if __name__ == "__main__":
    # 测试
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    
    print(f"图片保存路径示例: {get_image_save_path('测试书名', 1)}")
    print(f"文本保存路径示例: {get_text_save_path('测试书名', 1)}")
    print(f"环境信息: {check_environment()}")
    
    wait_with_progress(3, "测试等待") 