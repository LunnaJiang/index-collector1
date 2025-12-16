"""
微信指数数据收集器
注意：由于微信指数主要通过小程序提供，本工具提供多种收集方式
"""

import time
import logging
import json
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from config import BROWSER_CONFIG, KEYWORDS, SCREENSHOT_CONFIG, SCREENSHOTS_DIR

class WechatIndexCollector:
    """微信指数数据收集器"""
    
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        self.data = []
        
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={BROWSER_CONFIG["window_size"]}')
            chrome_options.add_argument(f'--user-agent={BROWSER_CONFIG["user_agent"]}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(BROWSER_CONFIG['timeout'])
            self.logger.info("浏览器驱动初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器驱动初始化失败: {str(e)}")
            raise
    
    def close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            self.logger.info("浏览器驱动已关闭")
    
    def try_web_version(self):
        """尝试访问微信指数的网页版本"""
        try:
            # 尝试访问微信指数的网页版本
            web_url = "https://index.weixin.qq.com"
            self.driver.get(web_url)
            self.logger.info(f"已访问微信指数网页版: {web_url}")
            time.sleep(5)
            
            # 检查是否需要登录
            if "login" in self.driver.current_url or "auth" in self.driver.current_url:
                self.logger.warning("需要登录微信指数网页版")
                return False
            
            # 等待页面加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "index-container"))
            )
            
            return True
            
        except TimeoutException:
            self.logger.error("微信指数网页版加载超时")
            return False
        except Exception as e:
            self.logger.error(f"访问微信指数网页版失败: {str(e)}")
            return False
    
    def search_keywords_in_web(self, keywords):
        """在网页版中搜索关键词"""
        try:
            # 找到搜索框
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-input"))
            )
            
            for keyword in keywords:
                # 清空搜索框
                search_box.clear()
                
                # 输入关键词
                search_box.send_keys(keyword)
                self.logger.info(f"输入关键词: {keyword}")
                
                # 点击搜索按钮
                search_button = self.driver.find_element(By.CLASS_NAME, "search-btn")
                search_button.click()
                time.sleep(3)
                
                # 获取数据
                keyword_data = self.get_wechat_index_data(keyword)
                if keyword_data:
                    self.data.append(keyword_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"搜索关键词失败: {str(e)}")
            return False
    
    def get_wechat_index_data(self, keyword):
        """获取微信指数数据"""
        try:
            # 等待数据加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "index-chart"))
            )
            
            # 尝试通过JavaScript获取数据
            chart_data = self.driver.execute_script(
                "return window.chartData || window.indexData || null"
            )
            
            if chart_data:
                self.logger.info(f"成功获取 {keyword} 的微信指数数据")
                return {
                    'keyword': keyword,
                    'data': chart_data,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # 备用方案：解析页面元素
                return self._parse_wechat_index_elements(keyword)
            
        except Exception as e:
            self.logger.error(f"获取 {keyword} 微信指数数据失败: {str(e)}")
            return None
    
    def _parse_wechat_index_elements(self, keyword):
        """解析微信指数页面元素"""
        try:
            # 查找数据元素
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".index-value, .data-point, .trend-number")
            
            values = []
            for element in data_elements:
                try:
                    value = element.text.strip()
                    if value and value.replace(',', '').replace('.', '').isdigit():
                        values.append(value)
                except:
                    continue
            
            return {
                'keyword': keyword,
                'data': values,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'element_parsing'
            }
            
        except Exception as e:
            self.logger.error(f"解析微信指数页面元素失败: {str(e)}")
            return None
    
    def set_date_range(self, start_date, end_date):
        """设置日期范围"""
        try:
            # 查找日期选择器
            date_picker = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "date-picker"))
            )
            date_picker.click()
            time.sleep(2)
            
            # 设置开始日期
            start_input = self.driver.find_element(By.CLASS_NAME, "start-date")
            start_input.clear()
            start_input.send_keys(start_date.strftime('%Y-%m-%d'))
            
            # 设置结束日期
            end_input = self.driver.find_element(By.CLASS_NAME, "end-date")
            end_input.clear()
            end_input.send_keys(end_date.strftime('%Y-%m-%d'))
            
            # 确认
            confirm_btn = self.driver.find_element(By.CLASS_NAME, "date-confirm")
            confirm_btn.click()
            time.sleep(3)
            
            self.logger.info(f"已设置日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            self.logger.error(f"设置日期范围失败: {str(e)}")
    
    def take_screenshot(self, filename_prefix):
        """截图"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            
            # 等待页面加载
            time.sleep(SCREENSHOT_CONFIG['wechat']['wait_time'])
            
            # 截图
            if SCREENSHOT_CONFIG['wechat']['full_page']:
                self.driver.save_screenshot(filepath)
            else:
                self.driver.get_screenshot_as_file(filepath)
            
            self.logger.info(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return None
    
    def simulate_manual_collection(self, start_date, end_date):
        """
        模拟手动收集方式
        由于微信指数小程序的限制，提供手动收集的辅助工具
        """
        try:
            self.logger.info("启动手动收集辅助模式")
            
            # 打开一个空白页面用于截图记录
            self.driver.get("about:blank")
            
            # 创建提示信息
            js_script = """
            document.body.innerHTML = `
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #07c160;">微信指数数据收集提示</h2>
                    <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3>收集时间范围：%s 至 %s</h3>
                        <h3>需要收集的关键词：</h3>
                        <ul style="font-size: 16px; line-height: 1.8;">
            """ % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            
            for keyword in KEYWORDS['wechat']:
                js_script += f"<li>{keyword}</li>"
            
            js_script += """
                        </ul>
                        <h3>操作步骤：</h3>
                        <ol style="font-size: 14px; line-height: 1.8;">
                            <li>打开微信，搜索"微信指数"小程序</li>
                            <li>分别搜索以上关键词</li>
                            <li>记录每日指数数据</li>
                            <li>截图保存</li>
                            <li>将数据填入Excel模板</li>
                        </ol>
                        <p style="color: #666; font-size: 12px;">
                            注：由于微信指数小程序的技术限制，无法直接自动化获取数据
                        </p>
                    </div>
                </div>
            `;
            """
            
            self.driver.execute_script(js_script)
            
            # 截图作为记录
            screenshot_path = self.take_screenshot('wechat_manual_guide')
            
            # 等待用户操作
            input("请在微信中完成数据收集后，按回车键继续...")
            
            return {
                'method': 'manual',
                'screenshot': screenshot_path,
                'guide': 'manual_collection_guide',
                'keywords': KEYWORDS['wechat'],
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            self.logger.error(f"手动收集模式失败: {str(e)}")
            return None
    
    def collect_wechat_index_data(self, start_date, end_date):
        """收集微信指数数据"""
        try:
            self.logger.info("开始收集微信指数数据")
            
            # 1. 设置浏览器
            self.setup_driver()
            
            # 2. 尝试访问网页版
            web_success = self.try_web_version()
            
            if web_success:
                # 3. 搜索关键词
                self.search_keywords_in_web(KEYWORDS['wechat'])
                
                # 4. 设置日期范围
                self.set_date_range(start_date, end_date)
                
                # 5. 截图
                screenshot_path = self.take_screenshot('wechat_index_web')
                
                result = {
                    'method': 'web',
                    'data': self.data,
                    'screenshot': screenshot_path,
                    'date_range': {
                        'start': start_date.strftime('%Y-%m-%d'),
                        'end': end_date.strftime('%Y-%m-%d')
                    }
                }
            else:
                # 如果网页版不可用，启动手动收集辅助模式
                self.logger.warning("微信指数网页版不可用，启动手动收集辅助模式")
                result = self.simulate_manual_collection(start_date, end_date)
            
            self.logger.info("微信指数数据收集完成")
            return result
            
        except Exception as e:
            self.logger.error(f"收集微信指数数据失败: {str(e)}")
            # 失败后启动手动收集模式
            return self.simulate_manual_collection(start_date, end_date)
        finally:
            self.close_driver()

def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from config import get_collection_dates
    
    # 获取收集日期
    start_date, end_date = get_collection_dates()
    
    # 创建收集器
    collector = WechatIndexCollector(headless=False)
    
    try:
        # 收集数据
        data = collector.collect_wechat_index_data(start_date, end_date)
        print("微信指数数据收集完成")
        print(f"收集方式: {data.get('method', 'unknown')}")
        print(f"数据范围: {data['date_range']['start']} 到 {data['date_range']['end']}")
        
    except Exception as e:
        print(f"数据收集失败: {str(e)}")

if __name__ == '__main__':
    main()