# 爱如生中国基本古籍库批量下载工具

这个项目提供了一个自动化工具，用于批量下载爱如生中国基本古籍库的图片和文本内容。该工具能够自动浏览搜索结果列表，进入每个详情页，同时下载图片和提取文本。

## 功能特点

- 自动搜索和浏览搜索结果列表
- 自动进入每个搜索结果的详情页
- 下载详情页中的图片
- 提取并保存详情页中的文本内容
- 支持批量处理多个搜索结果
- 支持使用 cookie 直接访问已登录的页面
- 支持自定义保存路径和处理数量
- 支持直接处理搜索页面或详情页面 URL
- 智能识别 URL 类型并执行相应操作
- **基于网站源码优化，更精确地定位和获取内容**
- **支持图片下载重试机制，更高的成功率**
- **能从 JavaScript 变量中提取文本内容**
- **智能处理多种图片 URL 格式和插图**

## A 项目结构

```
bulk_downloader/
├── config/
│   └── settings.py       # 配置文件，包含目标网址、下载路径等
├── src/
│   ├── downloader.py     # 主要下载逻辑
│   └── utils.py          # 辅助工具函数（如文件保存、复制文字等）
├── output/
│   ├── images/           # 存储下载的图片
│   └── text/             # 存储提取的文字
├── requirements.txt      # 项目依赖的Python库
└── run.py                # 启动脚本，运行爬虫
```

## 使用前提

1. 安装 Python 3.6+：[https://www.python.org/downloads/](https://www.python.org/downloads/)
2. 安装 Chrome 浏览器：[https://www.google.com/chrome/](https://www.google.com/chrome/)

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装依赖：
   ```bash
   cd bulk_downloader
   pip install -r requirements.txt
   ```

## 使用方法

### 1. 配置设置

有三种方式配置工具：

**方法一：修改配置文件**

编辑 `config/settings.py` 文件，修改以下主要配置：

```python
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
```

如果需要使用 cookie，请设置：

```python
# Cookie设置
COOKIES = {
    "ddhgguuy_session": "uk496de3r6fv8luiptmut86vuj",
    "JSESSIONID": "64DF3F552061EBA1576A66990470948C"
}

# 或者使用Cookie字符串
COOKIE_STRING = "ddhgguuy_session=uk496de3r6fv8luiptmut86vuj; JSESSIONID=64DF3F552061EBA1576A66990470948C"
```

如果需要登录，请设置：

```python
# 登录信息
"USERNAME": "your_username",
"PASSWORD": "your_password",
```

**方法二：使用命令行参数**

直接在命令行中传递参数：

```bash
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --query "唐诗" --image-dir "./images" --text-dir "./text" --pages 5 --max-items 10
```

**方法三：使用 cookie（推荐）**

使用浏览器中的 cookie 直接访问已登录页面：

1. 在浏览器中登录爱如生，打开搜索结果页面
2. 使用开发者工具(F12)获取 cookie
3. 使用 cookie 参数启动工具：

```bash
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --cookie "ddhgguuy_session=uk496de3r6fv8luiptmut86vuj; JSESSIONID=64DF3F552061EBA1576A66990470948C"
```

### 2. 运行工具

基本用法：

```bash
python run.py
```

直接处理详情页面：

```bash
python run.py --url "http://dh.g.sjuku.top/spring/front/jumpread?bookId=XXX&sheetId=YYY" --cookie "ddhgguuy_session=value; JSESSIONID=value"
```

## 详细获取 Cookie 步骤

### Chrome 浏览器

1. 先登录爱如生网站，并完成搜索，确保你在搜索结果页面
2. 按 `F12` 或右键点击页面选择"检查"打开开发者工具
3. 选择上方的 `Network`（网络）选项卡
4. 刷新页面（按 F5）
5. 在请求列表中点击第一个请求（通常是页面本身）
6. 在右侧面板中，选择 `Headers`（标头）标签
7. 向下滚动找到 `Request Headers`（请求标头）部分
8. 找到 `Cookie:` 一行，其后面的内容就是完整的 cookie 字符串

![获取Cookie示意图](https://i.imgur.com/YXcnR57.png)

9. 右键点击 cookie 值，选择"复制值"
10. 将复制的 cookie 字符串用于命令行参数：

```bash
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --cookie "你复制的cookie字符串"
```

### Firefox 浏览器

1. 登录爱如生网站并完成搜索
2. 按 `F12` 打开开发者工具
3. 选择 `Network`（网络）选项卡
4. 刷新页面
5. 在请求列表中点击第一个请求
6. 右侧面板中选择 `Headers`（标头）
7. 找到 `Cookie` 部分
8. 右键点击并复制值

### Edge 浏览器

1. 登录爱如生网站并完成搜索
2. 按 `F12` 打开开发者工具
3. 选择 `Network`（网络）选项卡
4. 刷新页面
5. 在请求列表中点击第一个请求
6. 在右侧面板中，找到 `Request headers`（请求标头）部分
7. 找到并复制 `Cookie` 的值

### 重要提示

- Cookie 通常包含敏感信息，请不要公开分享
- Cookie 是有时效性的，一段时间后可能会过期，需要重新获取
- 如果使用 Cookie 方式仍无法访问，请检查 Cookie 是否完整复制，或是否已过期
- 如遇到"请重新进入 1！"的提示，很可能是 Cookie 已过期，需要重新获取

## 命令行参数

| 参数              | 描述                                            |
| ----------------- | ----------------------------------------------- |
| `-u, --url`       | 爱如生中国基本古籍库 URL（搜索页面或详情页面）  |
| `-q, --query`     | 搜索关键词                                      |
| `--image-dir`     | 图片保存路径                                    |
| `--text-dir`      | 文本保存路径                                    |
| `-p, --pages`     | 最大页数，默认为所有页面                        |
| `-m, --max-items` | 处理的最大条目数，默认为所有条目                |
| `--cookie`        | Cookie 字符串，例如'name1=value1; name2=value2' |
| `--username`      | 登录用户名                                      |
| `--password`      | 登录密码                                        |
| `--headless`      | 启用无头模式（不显示浏览器窗口）                |
| `--driver`        | ChromeDriver 路径                               |
| `--page-delay`    | 每页处理完后的等待时间(秒)                      |
| `--click-delay`   | 点击元素后的等待时间(秒)                        |

## 示例

```bash
# 基本使用（搜索页面）
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --query "唐诗"

# 使用cookie访问搜索页面（推荐方式）
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --cookie "ddhgguuy_session=value; JSESSIONID=value"

# 直接处理详情页面
python run.py --url "http://dh.g.sjuku.top/spring/front/jumpread?bookId=12345&sheetId=67890" --cookie "ddhgguuy_session=value; JSESSIONID=value"

# 设置登录信息和保存目录
python run.py --url "http://dh.g.sjuku.top/spring/front/search" --query "唐诗" --username "user" --password "pass" --image-dir "./下载图片" --text-dir "./提取文本"

# 限制处理数量和调整延迟
python run.py --query "唐诗" --pages 3 --max-items 20 --page-delay 10 --click-delay 2

# 使用无头模式（无浏览器界面）
python run.py --query "唐诗" --headless
```

## 智能 URL 处理特性

工具现在能够根据 URL 类型自动执行不同操作：

1. 如果提供搜索页面 URL (`/spring/front/search`)：

   - 工具会自动处理搜索结果列表
   - 依次访问每个结果的详情页并下载内容

2. 如果提供详情页面 URL (`/spring/front/jumpread`)：
   - 工具会直接处理该页面
   - 下载该页面的图片和文本内容
   - 不会浏览搜索结果列表

这种设计使得工具更加灵活，可以根据需要处理单个页面或批量处理多个页面。

## 自定义元素选择器

如果爱如生网站结构发生变化，您可能需要调整元素选择器。编辑 `config/settings.py` 文件中的 `SELECTORS` 部分：

```python
# 爱如生网站元素选择器
SELECTORS = {
    # 登录相关
    "LOGIN": {
        "USERNAME_INPUT": "#username",
        "PASSWORD_INPUT": "#password",
        "SUBMIT_BUTTON": "//button[@type='submit']",
    },

    # 搜索相关
    "SEARCH": {
        "SEARCH_INPUT": "#search_input",
        "SEARCH_BUTTON": "//button[@type='submit']",
    },

    # 搜索结果列表相关
    "RESULTS": {
        "ITEM_LINKS": "//div[contains(@class, 'result-item')]//a[contains(@class, 'item-title')] | //ul[contains(@class, 'search-results')]//a[contains(@class, 'result-title')]",
        "NEXT_PAGE": "//a[contains(text(), '下一页') or contains(@aria-label, 'Next') or contains(@title, '下一页')]",
    },

    # 详情页相关
    "DETAIL": {
        "IMAGES": "//div[contains(@class, 'book-content')]//img | //div[contains(@class, 'page-content')]//img",
        "DOWNLOAD_BUTTON": "//button[contains(text(), '下载') or contains(@title, '下载')] | //a[contains(text(), '下载') or contains(@title, '下载')]",
        "TEXT_CONTENT": "//div[contains(@class, 'text-content')] | //div[contains(@class, 'book-text')]",
        "BACK_BUTTON": "//button[contains(text(), '返回') or contains(@title, '返回')] | //a[contains(text(), '返回') or contains(@title, '返回')]",
    },
}
```

## 注意事项

1. 网站可能会有反爬虫机制，请适当调整脚本中的延迟时间，避免操作过快被封 IP
2. 网站界面可能会更新，导致选择器失效，此时需要根据新界面调整选择器
3. Cookie 通常有过期时间，如果遇到"请重新进入 1！"的提示，可能需要更新 Cookie
4. 大量自动化操作可能违反网站服务条款，请合理使用，避免对服务器造成过大负担
5. 下载的内容可能受版权保护，请遵守相关法律法规，仅用于个人学习研究
6. 在爱如生服务器负载较高时，建议设置较长的页面延迟以减轻服务器压力

## 故障排除

1. **"请重新进入 1！"提示**

   - 这通常表示 Cookie 已过期或会话失效
   - 重新在浏览器中登录并获取新的 Cookie
   - 确保使用完整的 Cookie 字符串

2. **无法找到元素**

   - 网站结构可能已更改，需要更新 SELECTORS 配置
   - 检查是否需要增加等待时间让页面完全加载

3. **图片下载失败**

   - 确认您有网络访问权限
   - 检查存储路径是否有写入权限
   - 检查图片 URL 是否正确

4. **脚本运行缓慢**
   - 适当增加页面延迟和点击延迟
   - 减少最大页数或最大条目数
   - 确保计算机资源足够

## 许可证

本项目仅供学习研究使用，请勿用于商业用途。

## 网站源码优化说明

本工具的最新版本基于爱如生网站的实际源代码进行了优化，确保能更精确地获取内容：

### 图片获取优化

1. **图片 URL 构造**：使用正确的 URL 格式 `/spring/front/dximg?cv=` 和 `/spring/front/ctimg?cv=`
2. **参数提取**：能从 URL 和 JavaScript 变量中提取 bookId、sheetId 等参数
3. **重试机制**：每张图片下载支持多达 4 次的重试，与网站原始代码一致
4. **多种图片处理**：支持处理主图和插图，实现全面采集

### 文本提取优化

1. **多源提取**：可从多种 DOM 元素和 JavaScript 变量中提取文本
2. **OCR 识别**：当网站使用 OCR 技术提供文本时，能正确获取
3. **HTML 清理**：智能清理 HTML 标签，提供纯文本内容
4. **交互支持**：能够自动点击"显示文字"按钮来获取更多内容

### 元素定位优化

更新了所有 CSS 和 XPath 选择器，包括：

- 搜索输入框：`#ikeyword`
- 搜索按钮：`#search_btn`
- 搜索结果项：`//div[contains(@class, 'st')]/a` 等
- 图片元素：`#imgI_1 | #imgI_2 | #imgCtrl img`
- 文本内容：`#htmlContent | #div_htmlContent`

这些优化使得工具能更可靠地工作，大大提高了下载成功率和内容完整性。
