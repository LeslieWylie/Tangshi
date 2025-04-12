#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爱如生中国基本古籍库批量导出工具
"""

import sys
import time
import re
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 导入自定义模块
from config.settings import DOWNLOAD_CONFIG, BROWSER_CONFIG, SELECTORS, AUTH, COOKIES, COOKIE_STRING
from src.utils import (
    logger, 
    is_xpath, 
    wait_with_progress, 
    get_image_save_path, 
    get_text_save_path, 
    download_image, 
    save_text, 
    clean_text, 
    extract_title_from_url
)

class AirushengDownloader:
    """爱如生中国基本古籍库批量导出工具"""
    
    def __init__(self):
        """初始化下载器"""
        self.driver = None
        self.wait = None
        self.base_url = DOWNLOAD_CONFIG.get("BASE_URL")
        self.search_query = DOWNLOAD_CONFIG.get("SEARCH_QUERY")
        self.image_dir = DOWNLOAD_CONFIG.get("IMAGE_DIR")
        self.text_dir = DOWNLOAD_CONFIG.get("TEXT_DIR")
        self.max_pages = DOWNLOAD_CONFIG.get("MAX_PAGES")
        self.max_items = DOWNLOAD_CONFIG.get("MAX_ITEMS")
        self.page_delay = DOWNLOAD_CONFIG.get("PAGE_DELAY")
        self.click_delay = DOWNLOAD_CONFIG.get("CLICK_DELAY")
        self.username = AUTH.get("USERNAME")
        self.password = AUTH.get("PASSWORD")
        
        # 初始化目录
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        
        # 初始化WebDriver
        self.setup_driver()
    
    def setup_driver(self):
        """设置WebDriver"""
        try:
            # 创建Chrome选项
            chrome_options = Options()
            
            # 设置无头模式
            if BROWSER_CONFIG.get("HEADLESS"):
                chrome_options.add_argument("--headless")
            
            # 设置窗口大小
            width, height = BROWSER_CONFIG.get("WINDOW_SIZE", (1920, 1080))
            chrome_options.add_argument(f"--window-size={width},{height}")
            
            # 设置下载路径
            prefs = {
                "download.default_directory": self.image_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 创建WebDriver
            chrome_driver_path = BROWSER_CONFIG.get("CHROME_DRIVER_PATH")
            if chrome_driver_path:
                service = Service(executable_path=chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # 设置等待时间
            wait_timeout = BROWSER_CONFIG.get("WAIT_TIMEOUT", 10)
            self.wait = WebDriverWait(self.driver, wait_timeout)
            
            logger.info("WebDriver初始化成功")
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {str(e)}")
            raise
    
    def add_cookies(self):
        """
        添加cookie到浏览器
        
        Returns:
            bool: 添加cookie是否成功
        """
        try:
            # 解析域名
            domain = urlparse(self.driver.current_url).netloc
            
            # 从配置中获取cookie
            cookies_dict = COOKIES
            cookie_string = COOKIE_STRING
            
            # 如果有cookie字符串，解析为字典
            if cookie_string and not cookies_dict:
                cookies_dict = {}
                for item in cookie_string.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        cookies_dict[name] = value
            
            # 添加cookie
            if cookies_dict:
                for name, value in cookies_dict.items():
                    try:
                        cookie = {
                            "name": name,
                            "value": value,
                            "domain": domain
                        }
                        self.driver.add_cookie(cookie)
                        logger.debug(f"添加cookie: {name}")
                    except Exception as e:
                        logger.warning(f"添加单个cookie失败 '{name}': {str(e)}")
                
                logger.info("已添加cookie，共 {} 个", len(cookies_dict))
                return True
            else:
                logger.warning("没有提供cookie")
                return False
        except Exception as e:
            logger.error(f"添加cookie失败: {str(e)}")
            return False
    
    def find_element(self, selector, wait=True, parent=None):
        """
        查找元素
        
        Args:
            selector (str): 元素选择器
            wait (bool, optional): 是否等待元素出现
            parent (WebElement, optional): 父元素，默认为None
            
        Returns:
            WebElement: 找到的元素
        """
        try:
            # 确定选择器类型
            by_type = By.XPATH if is_xpath(selector) else By.CSS_SELECTOR
            
            # 搜索范围
            context = parent or self.driver
            
            # 查找元素
            if wait:
                return self.wait.until(EC.presence_of_element_located((by_type, selector)))
            else:
                return context.find_element(by_type, selector)
        except Exception as e:
            logger.error(f"查找元素失败 '{selector}': {str(e)}")
            return None
    
    def find_elements(self, selector, parent=None):
        """
        查找多个元素
        
        Args:
            selector (str): 元素选择器
            parent (WebElement, optional): 父元素，默认为None
            
        Returns:
            list: 找到的元素列表
        """
        try:
            # 确定选择器类型
            by_type = By.XPATH if is_xpath(selector) else By.CSS_SELECTOR
            
            # 搜索范围
            context = parent or self.driver
            
            # 查找元素
            return context.find_elements(by_type, selector)
        except Exception as e:
            logger.error(f"查找多个元素失败 '{selector}': {str(e)}")
            return []
    
    def click_element(self, selector, wait=True, parent=None):
        """
        点击元素
        
        Args:
            selector (str): 元素选择器
            wait (bool, optional): 是否等待元素可点击
            parent (WebElement, optional): 父元素，默认为None
            
        Returns:
            bool: 点击是否成功
        """
        try:
            # 确定选择器类型
            by_type = By.XPATH if is_xpath(selector) else By.CSS_SELECTOR
            
            # 搜索范围
            context = parent or self.driver
            
            # 查找并点击元素
            if wait:
                element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            else:
                element = context.find_element(by_type, selector)
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # 尝试点击
            try:
                element.click()
            except Exception:
                # 如果常规点击失败，使用JavaScript点击
                logger.debug(f"尝试使用JavaScript点击元素 '{selector}'")
                self.driver.execute_script("arguments[0].click();", element)
            
            time.sleep(self.click_delay)
            return True
        except Exception as e:
            logger.error(f"点击元素失败 '{selector}': {str(e)}")
            return False
    
    def login(self):
        """
        登录到爱如生
        
        Returns:
            bool: 登录是否成功
        """
        try:
            # 检查是否需要登录
            if not (self.username and self.password):
                logger.info("未提供登录信息，跳过登录步骤")
                return True
            
            # 获取登录元素选择器
            selectors = SELECTORS.get("LOGIN", {})
            username_selector = selectors.get("USERNAME_INPUT")
            password_selector = selectors.get("PASSWORD_INPUT")
            submit_selector = selectors.get("SUBMIT_BUTTON")
            
            # 输入用户名
            username_input = self.find_element(username_selector)
            if not username_input:
                return False
            username_input.clear()
            username_input.send_keys(self.username)
            
            # 输入密码
            password_input = self.find_element(password_selector)
            if not password_input:
                return False
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 点击提交按钮
            if not self.click_element(submit_selector):
                return False
            
            # 等待登录成功
            time.sleep(3)
            
            logger.info("登录成功")
            return True
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return False
    
    def search(self):
        """在爱如生中国基本古籍库中搜索内容"""
        try:
            # 构建搜索URL
            search_url = urljoin(self.base_url, DOWNLOAD_CONFIG.get("SEARCH_URL", "/spring/front/search"))
            
            # 如果当前已经在搜索页面，不需要再次导航
            if search_url not in self.driver.current_url:
                logger.info(f"导航到搜索页面: {search_url}")
                self.driver.get(search_url)
                
                # 增加页面加载等待时间
                wait_with_progress(5, "等待搜索页面加载")
            
            # 检查页面上是否有"请重新进入1！"的提示
            try:
                if "请重新进入" in self.driver.page_source:
                    logger.warning("检测到'请重新进入'提示，Cookie可能已过期")
                    # 尝试刷新页面
                    self.driver.refresh()
                    wait_with_progress(3, "刷新页面后等待")
            except:
                pass
            
            # 尝试多种方式找到搜索元素
            if self.search_query:
                # 查找搜索输入框
                search_input_selector = SELECTORS.get("SEARCH", {}).get("SEARCH_INPUT")
                search_input = None
                
                # 尝试使用JavaScript检测页面中的输入框
                try:
                    logger.info("尝试使用JavaScript查找搜索输入框")
                    inputs = self.driver.execute_script("""
                        return Array.from(document.querySelectorAll('input[type="text"]')).filter(el => 
                            el.id.toLowerCase().includes('key') || 
                            el.name.toLowerCase().includes('key') || 
                            el.placeholder.toLowerCase().includes('搜') ||
                            el.placeholder.toLowerCase().includes('检索')
                        );
                    """)
                    if inputs and len(inputs) > 0:
                        search_input = inputs[0]
                        logger.info(f"通过JavaScript找到搜索输入框: {search_input.get_attribute('id') or search_input.get_attribute('name')}")
                except Exception as e:
                    logger.warning(f"JavaScript查找失败: {str(e)}")
                
                # 如果JavaScript方法失败，使用常规方法
                if not search_input:
                    # 尝试等待页面完全加载
                    time.sleep(2)
                    
                    # 尝试从选择器列表中找到第一个可用的
                    for selector in search_input_selector.split(','):
                        try:
                            selector = selector.strip()
                            logger.debug(f"尝试选择器: {selector}")
                            
                            # 尝试查找元素，不使用等待，快速测试
                            search_input = self.find_element(selector, wait=False)
                            if search_input:
                                logger.info(f"找到搜索输入框，使用选择器: {selector}")
                                break
                        except Exception:
                            continue
                
                # 如果仍然找不到输入框，尝试通过XPath查找任何可能的输入框
                if not search_input:
                    try:
                        logger.info("尝试通过XPath查找任何文本输入框")
                        search_input = self.find_element("//input[@type='text']", wait=False)
                        if search_input:
                            logger.info("找到通用文本输入框")
                    except Exception:
                        pass
                
                # 如果找到了搜索输入框
                if search_input:
                    # 清除并输入搜索关键词
                    try:
                        search_input.clear()
                        search_input.send_keys(self.search_query)
                        logger.info(f"输入搜索关键词: {self.search_query}")
                        
                        # 查找搜索按钮
                        search_button_selector = SELECTORS.get("SEARCH", {}).get("SEARCH_BUTTON")
                        search_button = None
                        
                        # 尝试所有可能的按钮选择器
                        for selector in search_button_selector.split(','):
                            try:
                                selector = selector.strip()
                                search_button = self.find_element(selector, wait=False)
                                if search_button:
                                    logger.info(f"找到搜索按钮，使用选择器: {selector}")
                                    break
                            except Exception:
                                continue
                        
                        # 如果找不到按钮，尝试使用通用方法
                        if not search_button:
                            try:
                                # 尝试查找任何可能的搜索按钮
                                logger.info("尝试查找任何可能的搜索按钮")
                                search_button = self.find_element("//button[contains(text(), '搜') or contains(text(), '查') or contains(text(), '检索')]", wait=False)
                                if not search_button:
                                    # 尝试通过JavaScript查找按钮
                                    buttons = self.driver.execute_script("""
                                        return Array.from(document.querySelectorAll('button')).filter(el => 
                                            el.textContent.includes('搜') || 
                                            el.textContent.includes('查') || 
                                            el.textContent.includes('检索')
                                        );
                                    """)
                                    if buttons and len(buttons) > 0:
                                        search_button = buttons[0]
                            except Exception as e:
                                logger.warning(f"查找搜索按钮失败: {str(e)}")
                        
                        # 如果找到按钮，点击它
                        if search_button:
                            try:
                                search_button.click()
                                logger.info("点击搜索按钮")
                                wait_with_progress(3, "等待搜索结果加载")
                                return True
                            except Exception as e:
                                logger.warning(f"点击搜索按钮失败: {str(e)}")
                                # 尝试使用JavaScript点击
                                try:
                                    self.driver.execute_script("arguments[0].click();", search_button)
                                    logger.info("使用JavaScript点击搜索按钮")
                                    wait_with_progress(3, "等待搜索结果加载")
                                    return True
                                except Exception as js_e:
                                    logger.error(f"JavaScript点击失败: {str(js_e)}")
                        # 如果找不到按钮，尝试直接提交表单
                        else:
                            try:
                                logger.info("尝试直接提交表单")
                                # 尝试查找包含搜索输入框的表单
                                form = self.driver.execute_script("return arguments[0].form", search_input)
                                if form:
                                    form.submit()
                                    logger.info("表单提交成功")
                                    wait_with_progress(3, "等待搜索结果加载")
                                    return True
                                else:
                                    # 尝试按回车键提交
                                    search_input.send_keys(Keys.ENTER)
                                    logger.info("使用回车键提交搜索")
                                    wait_with_progress(3, "等待搜索结果加载")
                                    return True
                            except Exception as e:
                                logger.error(f"提交表单失败: {str(e)}")
                    except Exception as e:
                        logger.error(f"操作搜索输入框失败: {str(e)}")
                else:
                    logger.error("无法找到搜索输入框")
            else:
                # 如果没有搜索关键词，假设当前页面已经是搜索结果页面
                logger.info("没有提供搜索关键词，假设当前页面已经是搜索结果页面")
                return True
            
            # 如果所有尝试都失败，返回失败
            return False
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return False
    
    def get_search_results(self):
        """
        获取搜索结果列表
        
        Returns:
            list: 搜索结果列表，包含链接和标题
        """
        try:
            # 获取结果链接选择器
            item_links_selector = SELECTORS.get("RESULTS", {}).get("ITEM_LINKS")
            
            # 等待元素加载
            time.sleep(2)
            
            # 查找所有结果链接
            link_elements = self.find_elements(item_links_selector)
            
            results = []
            for link in link_elements:
                try:
                    href = link.get_attribute("href")
                    title = link.text.strip()
                    
                    # 如果标题为空，尝试获取其他属性
                    if not title:
                        title = link.get_attribute("title") or link.get_attribute("aria-label") or "未知标题"
                    
                    results.append({
                        "url": href,
                        "title": title
                    })
                except StaleElementReferenceException:
                    logger.warning("元素已过期，跳过")
                    continue
                except Exception as e:
                    logger.warning(f"处理搜索结果链接时出错: {str(e)}")
                    continue
            
            logger.info(f"找到 {len(results)} 个搜索结果")
            return results
        except Exception as e:
            logger.error(f"获取搜索结果失败: {str(e)}")
            return []
    
    def has_next_page(self):
        """
        检查是否有下一页
        
        Returns:
            bool: 是否有下一页
        """
        try:
            # 获取下一页按钮选择器
            next_page_selector = SELECTORS.get("RESULTS", {}).get("NEXT_PAGE")
            
            # 尝试找到下一页按钮
            next_page_button = self.find_element(next_page_selector, wait=False)
            if not next_page_button:
                logger.info("没有找到下一页按钮")
                return False
            
            # 检查按钮是否被禁用
            disabled = next_page_button.get_attribute("disabled") or "disabled" in next_page_button.get_attribute("class") or ""
            if disabled:
                logger.info("下一页按钮已禁用，已到达最后一页")
                return False
            
            return True
        except NoSuchElementException:
            logger.info("没有找到下一页按钮，可能已到达最后一页")
            return False
        except Exception as e:
            logger.error(f"检查下一页失败: {str(e)}")
            return False
    
    def go_to_next_page(self):
        """
        前往下一页
        
        Returns:
            bool: 是否成功前往下一页
        """
        try:
            # 先检查是否有下一页
            if not self.has_next_page():
                return False
            
            # 获取下一页按钮选择器
            next_page_selector = SELECTORS.get("RESULTS", {}).get("NEXT_PAGE")
            
            # 点击下一页按钮
            if not self.click_element(next_page_selector):
                return False
            
            # 等待页面加载
            time.sleep(2)
            
            logger.info("已前往下一页")
            return True
        except Exception as e:
            logger.error(f"前往下一页失败: {str(e)}")
            return False
    
    def process_detail_page(self, item):
        """
        处理详情页面
        
        Args:
            item (dict): 包含URL和标题的搜索结果条目
            
        Returns:
            bool: 处理是否成功
        """
        try:
            url = item["url"]
            title = item["title"]
            
            logger.info(f"正在处理: {title}")
            
            # 访问详情页
            self.driver.get(url)
            time.sleep(3)  # 等待页面加载
            
            # 下载图片
            self.download_images(title)
            
            # 提取文本
            self.extract_text(title)
            
            logger.info(f"完成处理: {title}")
            return True
        except Exception as e:
            logger.error(f"处理详情页失败: {str(e)}")
            return False
    
    def download_images(self, title):
        """
        下载详情页中的图片
        
        Args:
            title (str): 详情页标题
            
        Returns:
            int: 下载的图片数量
        """
        try:
            # 从详情页URL获取参数
            current_url = self.driver.current_url
            parsed_url = urlparse(current_url)
            query_params = {}
            
            if parsed_url.query:
                query_parts = parsed_url.query.split('&')
                for part in query_parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        query_params[key] = value
            
            # 从页面中提取重要参数
            lib_id = ''
            book_id = query_params.get('bookId', '')
            page_id = query_params.get('sheetId', '')
            
            # 如果URL中没有参数，尝试从页面JavaScript中提取
            if not book_id or not page_id:
                try:
                    lib_id = self.driver.execute_script("return T_libId || '';")
                    book_id = self.driver.execute_script("return T_bookId || '';")
                    page_id = self.driver.execute_script("return T_pageId || '';")
                except:
                    logger.warning("无法从JavaScript中提取图片参数")
            
            if not book_id:
                logger.warning("未找到bookId参数，无法构建图片URL")
            
            # 使用网站的图片URL格式
            img_url_base = urljoin(self.base_url, "/spring/front/dximg?cv=")
            chatu_url_base = urljoin(self.base_url, "/spring/front/ctimg?cv=")
            
            # 尝试直接找图片元素
            images_selector = SELECTORS.get("DETAIL", {}).get("IMAGES")
            image_elements = self.find_elements(images_selector)
            
            if not image_elements and (lib_id or book_id):
                # 如果没有直接找到图片元素但有ID参数，构建图片URL
                count = 0
                # 尝试构建主图URL
                if book_id and page_id:
                    cmd_str = f"{lib_id};{book_id};{page_id}" if lib_id else f"{book_id};{page_id}"
                    img_url = f"{img_url_base}{cmd_str}"
                    save_path = get_image_save_path(title, 1, "main_image.jpg")
                    
                    # 添加重试机制
                    max_attempts = 4  # 根据网站源码中的重试次数
                    for attempt in range(max_attempts):
                        try:
                            if download_image(img_url, save_path, self.base_url):
                                count += 1
                                logger.info(f"成功下载主图: {img_url}")
                                break
                        except Exception as e:
                            logger.warning(f"下载主图尝试 {attempt+1}/{max_attempts} 失败: {str(e)}")
                            time.sleep(2)  # 短暂等待后重试
                
                # 检查是否有插图
                try:
                    chatu_count = self.driver.execute_script("return chatuCount || 0;")
                    if chatu_count > 0:
                        for i in range(chatu_count):
                            chatu_cmd = f"{lib_id};{book_id};{page_id};{i}" if lib_id else f"{book_id};{page_id};{i}"
                            chatu_img_url = f"{chatu_url_base}{chatu_cmd}"
                            save_path = get_image_save_path(title, i + 2, f"chatu_{i}.jpg")
                            
                            # 添加重试机制
                            for attempt in range(max_attempts):
                                try:
                                    if download_image(chatu_img_url, save_path, self.base_url):
                                        count += 1
                                        logger.info(f"成功下载插图 {i+1}: {chatu_img_url}")
                                        break
                                except Exception as e:
                                    logger.warning(f"下载插图 {i+1} 尝试 {attempt+1}/{max_attempts} 失败: {str(e)}")
                                    time.sleep(2)
                except:
                    logger.debug("无法获取插图数量")
                
                logger.info(f"根据参数构建共下载 {count} 张图片")
                return count
            
            # 如果找到图片元素，直接下载
            count = 0
            for i, img in enumerate(image_elements):
                try:
                    # 获取图片URL
                    src = img.get_attribute("src")
                    if not src:
                        # 尝试获取data-src属性
                        src = img.get_attribute("data-src")
                        if not src:
                            continue
                    
                    # 确保URL是绝对路径
                    if not src.startswith(("http://", "https://")):
                        src = urljoin(self.driver.current_url, src)
                    
                    # 构建保存路径
                    save_path = get_image_save_path(title, i + 1, src)
                    
                    # 下载图片，添加重试机制
                    max_attempts = 4
                    for attempt in range(max_attempts):
                        try:
                            if download_image(src, save_path, self.driver.current_url):
                                count += 1
                                logger.debug(f"成功下载图片 {i+1}: {src}")
                                break
                        except Exception as e:
                            logger.warning(f"下载图片 {i+1} 尝试 {attempt+1}/{max_attempts} 失败: {str(e)}")
                            time.sleep(2)
                except Exception as e:
                    logger.warning(f"处理图片元素 {i+1} 时出错: {str(e)}")
                    continue
            
            logger.info(f"从页面元素共下载 {count} 张图片")
            return count
        except Exception as e:
            logger.error(f"下载图片失败: {str(e)}")
            return 0
    
    def extract_text(self, title):
        """
        提取并保存详情页中的文本
        
        Args:
            title (str): 详情页标题
            
        Returns:
            bool: 提取是否成功
        """
        try:
            # 尝试从不同的元素获取文本内容
            text_content_selector = SELECTORS.get("DETAIL", {}).get("TEXT_CONTENT")
            text = ""
            
            # 首先尝试通过选择器直接查找文本内容元素
            text_element = self.find_element(text_content_selector, wait=False)
            
            if not text_element:
                logger.warning("未找到文本内容元素，尝试从JavaScript变量获取")
                
                # 尝试从JavaScript变量获取文本
                try:
                    # 尝试获取T_htmlContent变量
                    js_text = self.driver.execute_script("return T_htmlContent || '';")
                    if js_text:
                        logger.info("成功从JavaScript变量T_htmlContent获取文本内容")
                        text = js_text
                    else:
                        # 尝试获取ocrContent变量
                        ocr_text = self.driver.execute_script("return ocrContent || '';")
                        if ocr_text:
                            logger.info("成功从JavaScript变量ocrContent获取文本")
                            text = ocr_text
                        else:
                            # 检查是否需要点击"下载"按钮
                            show_text_button = self.find_element("//button[contains(text(), '下载') or contains(@title, '下载')] | //a[contains(text(), '下载')]", wait=False)
                            if show_text_button:
                                logger.info('找到"下载"按钮，尝试点击')
                                show_text_button.click()
                                time.sleep(2)  # 等待文本加载
                                
                                # 重新尝试获取文本元素
                                new_text_element = self.find_element(text_content_selector, wait=False)
                                if new_text_element:
                                    new_text = new_text_element.text
                                    if new_text:
                                        text = new_text
                                    else:
                                        inner_html = self.driver.execute_script("return arguments[0].innerHTML;", new_text_element)
                                        text = re.sub(r'<[^>]+>', ' ', inner_html)
                except Exception as e:
                    logger.warning(f"从JavaScript变量获取文本失败: {str(e)}")
            else:
                # 如果找到了文本元素，获取其文本内容
                element_text = text_element.text
                if element_text:
                    text = element_text
                else:
                    # 如果text属性为空，尝试获取innerHTML
                    inner_html = self.driver.execute_script("return arguments[0].innerHTML;", text_element)
                    text = re.sub(r'<[^>]+>', ' ', inner_html)
            
            # 如果仍然没有文本，尝试通过OCR方式处理图片
            if not text:
                logger.warning("无法直接获取文本内容，尝试分析图片...")
                # 这里可以添加调用OCR服务的代码
                # 为了简单起见，先跳过这一步
                text = "【无法直接获取文本，需要OCR处理】"
            
            # 清理文本
            text = clean_text(text)
            
            if not text:
                logger.warning("提取的文本为空")
                return False
            
            # 保存文本
            save_path = get_text_save_path(title)
            save_text(text, save_path)
            
            logger.info(f"已提取并保存文本: {save_path}")
            return True
        except Exception as e:
            logger.error(f"提取文本失败: {str(e)}")
            return False
    
    def process_search_results(self):
        """处理搜索结果页面的各个条目"""
        try:
            # 收集搜索结果
            all_results = []
            page_count = 0
            has_next_page = True
            
            # 收集所有搜索结果
            while has_next_page and (self.max_pages is None or page_count < self.max_pages):
                page_count += 1
                logger.info(f"正在处理第 {page_count} 页搜索结果")
                
                # 获取当前页的搜索结果
                results = self.get_search_results()
                all_results.extend(results)
                
                # 如果已达到最大条目数，停止收集
                if self.max_items is not None and len(all_results) >= self.max_items:
                    all_results = all_results[:self.max_items]
                    break
                
                # 前往下一页
                has_next_page = self.go_to_next_page()
            
            # 处理每个搜索结果
            logger.info(f"共找到 {len(all_results)} 个搜索结果，开始处理详情页")
            
            for i, item in enumerate(all_results):
                logger.info(f"正在处理第 {i+1}/{len(all_results)} 个结果: {item.get('title', '未知标题')}")
                self.process_detail_page(item)
                
                # 短暂休息，避免频繁请求
                if i < len(all_results) - 1:
                    wait_with_progress(self.page_delay, "等待处理下一个结果")
            
            logger.info(f"批量下载完成，共处理 {len(all_results)} 个搜索结果")
        except Exception as e:
            logger.error(f"处理搜索结果失败: {str(e)}")
    
    def start(self, url=None):
        """
        启动下载过程
        
        Args:
            url (str, optional): 指定的URL，优先于配置的BASE_URL
        """
        try:
            # 确定起始URL
            start_url = url or self.base_url
            
            # 如果URL是搜索结果页面或详情页面，直接使用该URL
            is_search_page = DOWNLOAD_CONFIG.get("SEARCH_URL", "/spring/front/search") in start_url
            is_detail_page = DOWNLOAD_CONFIG.get("DETAIL_URL", "/spring/front/jumpread") in start_url
            
            # 打开起始页面
            logger.info(f"打开网页: {start_url}")
            self.driver.get(start_url)
            
            # 等待页面加载
            wait_with_progress(5, "等待页面初始加载")
            
            # 添加cookie
            self.add_cookies()
            
            # 刷新页面使cookie生效
            self.driver.refresh()
            wait_with_progress(3, "等待刷新完成")
            
            # 检查是否遇到"请重新进入1！"的提示
            if "请重新进入" in self.driver.page_source:
                logger.warning("检测到'请重新进入'提示，Cookie可能已过期")
                
                # 尝试重新加载或使用备用方法
                if self.username and self.password:
                    logger.info("尝试使用登录凭据")
                    if not self.login():
                        logger.error("登录失败，将尝试直接处理")
                else:
                    logger.warning("未提供登录信息，将尝试另一种方式访问")
            
            # 如果是详情页面，直接处理
            if is_detail_page:
                # 从URL中提取标题
                title = extract_title_from_url(start_url)
                self.process_detail_page({"title": title, "url": start_url})
                logger.info("处理详情页面完成")
                return
            
            # 如果不是搜索结果页面，尝试进行搜索
            if not is_search_page and self.search_query:
                search_success = self.search()
                if not search_success:
                    logger.warning("常规搜索方式失败，尝试备用方法")
                    
                    # 尝试备用方法 - 直接构建搜索URL
                    try:
                        # 尝试构建带有查询参数的URL
                        search_url_with_params = f"{self.base_url}{DOWNLOAD_CONFIG.get('SEARCH_URL', '/spring/front/search')}?keyword={self.search_query}"
                        logger.info(f"尝试直接访问搜索URL: {search_url_with_params}")
                        self.driver.get(search_url_with_params)
                        wait_with_progress(3, "等待页面加载")
                        
                        # 检查是否成功找到搜索结果
                        if "没有找到" in self.driver.page_source or "无结果" in self.driver.page_source:
                            logger.warning("搜索可能没有结果")
                        else:
                            logger.info("通过URL参数方式进行搜索可能成功")
                    except Exception as e:
                        logger.error(f"备用搜索方法失败: {str(e)}")
                        # 如果备用方法也失败，输出错误但继续尝试处理
                        logger.warning("备用搜索方法也失败，将尝试直接处理当前页面")
            
            # 尝试处理当前页面的搜索结果，无论之前的搜索是否成功
            try:
                # 检查当前页面是否包含可能的搜索结果
                possible_results = self.find_elements("//div[contains(@class, 'st')]/a | //div[contains(@class, 'g')]/a | //div[contains(@id, 'item_')]/a | //a[contains(@href, 'jumpread')]")
                
                if possible_results and len(possible_results) > 0:
                    logger.info(f"在当前页面找到 {len(possible_results)} 个可能的结果链接")
                    self.process_search_results()
                else:
                    logger.warning("当前页面未找到明显的搜索结果，尝试分析页面")
                    
                    # 获取所有链接，尝试找到可能的详情页链接
                    all_links = self.find_elements("//a[contains(@href, 'jumpread') or contains(@href, 'book') or contains(@href, 'detail')]")
                    if all_links and len(all_links) > 0:
                        logger.info(f"找到 {len(all_links)} 个可能的详情页链接")
                        
                        # 处理找到的链接
                        results = []
                        for link in all_links[:min(10, len(all_links))]:  # 限制最多处理10个
                            try:
                                href = link.get_attribute("href")
                                title = link.text.strip() or link.get_attribute("title") or extract_title_from_url(href)
                                if href and "jumpread" in href:
                                    results.append({"url": href, "title": title})
                            except Exception:
                                continue
                        
                        # 处理找到的结果
                        if results:
                            logger.info(f"将处理 {len(results)} 个找到的链接")
                            for i, item in enumerate(results):
                                try:
                                    logger.info(f"处理第 {i+1}/{len(results)} 个结果: {item.get('title', '未知标题')}")
                                    self.process_detail_page(item)
                                    wait_with_progress(self.page_delay, "等待处理下一个结果")
                                except Exception as e:
                                    logger.error(f"处理详情页失败: {str(e)}")
                                    continue
                        else:
                            logger.warning("未找到可处理的链接")
                    else:
                        logger.warning("未找到任何可处理的链接")
            except Exception as e:
                logger.error(f"处理搜索结果失败: {str(e)}")
            
        except Exception as e:
            logger.error(f"下载过程发生错误: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        finally:
            logger.info("下载过程结束")
            # 确保关闭浏览器
            self.close()
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")


if __name__ == "__main__":
    # 测试
    downloader = AirushengDownloader()
    downloader.start() 