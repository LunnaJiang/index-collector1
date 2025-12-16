"""
百度指数数据收集器
"""

import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from config import BROWSER_CONFIG, BAIDU_INDEX_URL, KEYWORDS, SCREENSHOT_CONFIG, SCREENSHOTS_DIR

class BaiduIndexCollector:
    """百度指数数据收集器"""
    
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        self.data = {
            'search_index': [],  # 搜索指数
            'info_index': []     # 资讯指数
        }
        
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
    
    def navigate_to_baidu_index(self):
        """导航到百度指数页面"""
        try:
            self.driver.get(BAIDU_INDEX_URL)
            self.logger.info(f"已访问百度指数页面: {BAIDU_INDEX_URL}")
            time.sleep(3)
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "home-header"))
            )
            self.logger.info("百度指数页面加载完成")
            
        except TimeoutException:
            self.logger.error("百度指数页面加载超时")
            raise
        except Exception as e:
            self.logger.error(f"导航到百度指数页面失败: {str(e)}")
            raise
    
    def search_keywords(self, keywords):
        """搜索关键词"""
        try:
            # 找到搜索框
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-input"))
            )
            
            # 清空搜索框
            search_box.clear()
            
            # 输入关键词（用逗号分隔多个关键词）
            keyword_str = ','.join(keywords)
            search_box.send_keys(keyword_str)
            self.logger.info(f"输入关键词: {keyword_str}")
            
            # 点击搜索按钮
            search_button = self.driver.find_element(By.CLASS_NAME, "search-btn")
            search_button.click()
            self.logger.info("已点击搜索按钮")
            
            # 等待搜索结果加载
            time.sleep(5)
            
        except TimeoutException:
            self.logger.error("搜索框加载超时")
            raise
        except Exception as e:
            self.logger.error(f"搜索关键词失败: {str(e)}")
            raise
    
    def switch_to_info_index(self):
        """切换到资讯指数"""
        try:
            # 查找资讯指数标签
            info_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '资讯指数') or contains(@class, 'info-index')]"))
            )
            info_tab.click()
            self.logger.info("已切换到资讯指数")
            time.sleep(3)
            
        except TimeoutException:
            self.logger.error("资讯指数标签加载超时")
            raise
        except Exception as e:
            self.logger.error(f"切换到资讯指数失败: {str(e)}")
            raise
    
    def get_index_data(self, index_type='search'):
        """获取指数数据"""
        try:
            data = {}
            
            # 等待图表加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "index-trend-chart"))
            )
            
            # 获取图表数据（这里需要根据实际情况调整选择器）
            chart_data = self.driver.execute_script(
                "return window.chartData || window.indexData || null"
            )
            
            if chart_data:
                self.logger.info(f"成功获取{index_type}数据")
                data = chart_data
            else:
                # 如果无法通过JS获取数据，尝试解析页面元素
                self.logger.warning("无法通过JS获取数据，尝试解析页面元素")
                data = self._parse_chart_elements()
            
            return data
            
        except Exception as e:
            self.logger.error(f"获取{index_type}数据失败: {str(e)}")
            return {}
    
    def _parse_chart_elements(self):
        """解析图表元素获取数据（备用方案）"""
        try:
            # 这里需要根据实际页面结构编写解析逻辑
            # 查找包含数据的元素
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, ".index-data-item, .data-point, .trend-value")
            
            data = {}
            for element in data_elements:
                try:
                    keyword = element.get_attribute("data-keyword")
                    value = element.text
                    if keyword and value:
                        data[keyword] = value
                except:
                    continue
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析图表元素失败: {str(e)}")
            return {}
    
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
            
            # 确认日期选择
            confirm_btn = self.driver.find_element(By.CLASS_NAME, "date-confirm")
            confirm_btn.click()
            time.sleep(3)
            
            self.logger.info(f"已设置日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
        except TimeoutException:
            self.logger.error("日期选择器加载超时")
        except Exception as e:
            self.logger.error(f"设置日期范围失败: {str(e)}")
    
    def take_screenshot(self, filename_prefix):
        """截图"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            
            # 等待页面完全加载
            time.sleep(SCREENSHOT_CONFIG['baidu']['wait_time'])
            
            # 截图
            if SCREENSHOT_CONFIG['baidu']['full_page']:
                # 全屏截图
                self.driver.save_screenshot(filepath)
            else:
                # 当前视口截图
                self.driver.get_screenshot_as_file(filepath)
            
            self.logger.info(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return None
    
    def collect_baidu_index_data(self, start_date, end_date):
        """收集百度指数数据"""
        try:
            self.logger.info("开始收集百度指数数据")
            
            # 1. 设置浏览器
            self.setup_driver()
            
            # 2. 导航到百度指数
            self.navigate_to_baidu_index()
            
            # 3. 搜索关键词
            self.search_keywords(KEYWORDS['baidu'])
            
            # 4. 设置日期范围
            self.set_date_range(start_date, end_date)
            
            # 5. 截图
            screenshot_path = self.take_screenshot('baidu_index_search')
            
            # 6. 获取搜索指数数据
            search_data = self.get_index_data('search')
            
            # 7. 切换到资讯指数
            self.switch_to_info_index()
            time.sleep(2)
            
            # 8. 截图
            info_screenshot_path = self.take_screenshot('baidu_index_info')
            
            # 9. 获取资讯指数数据
            info_data = self.get_index_data('info')
            
            # 10. 整理数据
            result = {
                'search_data': search_data,
                'info_data': info_data,
                'screenshots': {
                    'search': screenshot_path,
                    'info': info_screenshot_path
                },
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            }
            
            self.logger.info("百度指数数据收集完成")
            return result
            
        except Exception as e:
            self.logger.error(f"收集百度指数数据失败: {str(e)}")
            raise
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
    collector = BaiduIndexCollector(headless=False)
    
    try:
        # 收集数据
        data = collector.collect_baidu_index_data(start_date, end_date)
        print("百度指数数据收集成功")
        print(f"数据范围: {data['date_range']['start']} 到 {data['date_range']['end']}")
        print(f"截图保存位置: {data['screenshots']}")
        
    except Exception as e:
        print(f"数据收集失败: {str(e)}")

if __name__ == '__main__':
    main()