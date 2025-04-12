/**
 * 爱如生中国基本古籍库批量导出脚本
 * 
 * 使用方法:
 * 1. 在浏览器中打开爱如生中国基本古籍库搜索结果页面
 * 2. 按F12打开开发者工具
 * 3. 切换到"控制台"(Console)选项卡
 * 4. 复制粘贴此脚本，然后按回车执行
 * 5. 脚本会自动选择当前页面所有复选框，点击导出按钮，然后自动翻页继续
 */

// 配置参数
const config = {
    // 总共要处理的页数，设置为null表示处理所有页面
    maxPages: null,
    // 每页处理完后的等待时间(毫秒)
    pageDelay: 5000,
    // 点击元素后的等待时间(毫秒)
    clickDelay: 1000,
    // 复选框的XPath或CSS选择器(根据实际网页调整)
    checkboxSelector: 'input[type="checkbox"]',
    // 导出按钮的XPath或CSS选择器(根据实际网页调整)
    exportButtonSelector: 'button.export-btn, button[title*="导出"], button:contains("导出")',
    // 下一页按钮的XPath或CSS选择器(根据实际网页调整)
    nextPageSelector: 'a.next-page, a[title*="下一页"], a:contains("下一页"), li.ant-pagination-next:not(.ant-pagination-disabled) a'
};

// 日志函数
const log = (message, type = 'info') => {
    const styles = {
        info: 'color: #0066cc; font-weight: bold;',
        success: 'color: #00cc66; font-weight: bold;',
        error: 'color: #cc0000; font-weight: bold;',
        warning: 'color: #cccc00; font-weight: bold;'
    };
    console.log(`%c[爱如生导出工具] ${message}`, styles[type]);
};

// 等待函数
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 检查元素是否存在
const elementExists = (selector, isXPath = false) => {
    try {
        if (isXPath) {
            return document.evaluate(
                selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
            ).singleNodeValue !== null;
        } else {
            return document.querySelector(selector) !== null;
        }
    } catch (e) {
        log(`检查元素失败: ${e.message}`, 'error');
        return false;
    }
};

// 获取元素
const getElements = (selector, isXPath = false) => {
    try {
        if (isXPath) {
            const elements = [];
            const xpathResult = document.evaluate(
                selector, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
            );
            for (let i = 0; i < xpathResult.snapshotLength; i++) {
                elements.push(xpathResult.snapshotItem(i));
            }
            return elements;
        } else {
            return Array.from(document.querySelectorAll(selector));
        }
    } catch (e) {
        log(`获取元素失败: ${e.message}`, 'error');
        return [];
    }
};

// 点击元素
const clickElement = async (selector, isXPath = false) => {
    try {
        const element = isXPath 
            ? document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
            : document.querySelector(selector);
        
        if (!element) {
            log(`未找到元素: ${selector}`, 'warning');
            return false;
        }
        
        // 滚动到元素位置
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await sleep(500);
        
        // 尝试使用click()方法
        try {
            element.click();
        } catch (e) {
            // 如果常规点击失败，使用JavaScript点击
            log(`常规点击失败，尝试JS点击`, 'warning');
            const event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            element.dispatchEvent(event);
        }
        
        await sleep(config.clickDelay);
        return true;
    } catch (e) {
        log(`点击元素失败: ${e.message}`, 'error');
        return false;
    }
};

// 选择所有复选框
const selectAllCheckboxes = async () => {
    try {
        const checkboxes = getElements(config.checkboxSelector);
        if (checkboxes.length === 0) {
            log('未找到任何复选框', 'warning');
            return false;
        }
        
        let checkedCount = 0;
        for (const checkbox of checkboxes) {
            if (!checkbox.checked) {
                // 滚动到元素位置
                checkbox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                await sleep(200);
                
                try {
                    checkbox.click();
                } catch (e) {
                    // 如果常规点击失败，使用JavaScript点击
                    const event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    checkbox.dispatchEvent(event);
                }
                
                checkedCount++;
                await sleep(300); // 短暂延迟，避免点击过快
            }
        }
        
        log(`已选择 ${checkedCount} 个结果`, 'success');
        return true;
    } catch (e) {
        log(`选择复选框失败: ${e.message}`, 'error');
        return false;
    }
};

// 导出当前页面
const exportCurrentPage = async () => {
    try {
        const success = await clickElement(config.exportButtonSelector);
        if (success) {
            log('已点击导出按钮', 'success');
            await sleep(config.pageDelay); // 等待导出完成
            return true;
        } else {
            log('未找到导出按钮', 'warning');
            return false;
        }
    } catch (e) {
        log(`导出失败: ${e.message}`, 'error');
        return false;
    }
};

// 前往下一页
const goToNextPage = async () => {
    try {
        const success = await clickElement(config.nextPageSelector);
        if (success) {
            log('已前往下一页', 'success');
            await sleep(config.pageDelay); // 等待页面加载
            return true;
        } else {
            log('未找到下一页按钮或已到达最后一页', 'warning');
            return false;
        }
    } catch (e) {
        log(`翻页失败: ${e.message}`, 'error');
        return false;
    }
};

// 主函数
const batchExport = async () => {
    log('开始批量导出', 'info');
    
    let pageCount = 0;
    let hasNextPage = true;
    
    while (hasNextPage && (config.maxPages === null || pageCount < config.maxPages)) {
        pageCount++;
        log(`处理第 ${pageCount} 页`, 'info');
        
        // 选择所有复选框
        await selectAllCheckboxes();
        
        // 导出当前页
        await exportCurrentPage();
        
        // 前往下一页
        hasNextPage = await goToNextPage();
    }
    
    log(`批量导出完成，共处理 ${pageCount} 页`, 'success');
};

// 启动脚本
(async () => {
    try {
        await batchExport();
    } catch (e) {
        log(`脚本执行出错: ${e.message}`, 'error');
    }
})(); 