"""
定时任务调度系统
支持定时收集百度指数和微信指数数据
"""

import time
import schedule
import logging
from datetime import datetime
from threading import Thread
import os
import sys

from config import get_collection_dates, COLLECTION_HOUR, LOG_CONFIG
from baidu_collector import BaiduIndexCollector
from wechat_collector import WechatIndexCollector
from data_processor import DataProcessor

class IndexScheduler:
    """指数数据收集调度器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.scheduler_thread = None
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        log_dir = os.path.dirname(LOG_CONFIG['file'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, LOG_CONFIG['level']),
            format=LOG_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def should_collect_today(self):
        """判断今天是否应该收集数据"""
        today = datetime.now()
        weekday = today.weekday()  # 0=周一, 6=周日
        
        # 只在周五或周一收集数据
        if weekday in [0, 4]:  # 周一或周五
            return True
        
        return False
    
    def collect_data_task(self):
        """数据收集任务"""
        try:
            self.logger.info("开始执行数据收集任务")
            
            # 检查是否应该今天收集
            if not self.should_collect_today():
                self.logger.info("今天不是数据收集日，跳过")
                return
            
            # 获取收集日期范围
            start_date, end_date = get_collection_dates()
            self.logger.info(f"收集数据范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
            # 收集百度指数数据
            self.logger.info("开始收集百度指数数据")
            baidu_collector = BaiduIndexCollector(headless=True)
            baidu_data = baidu_collector.collect_baidu_index_data(start_date, end_date)
            self.logger.info("百度指数数据收集完成")
            
            # 收集微信指数数据
            self.logger.info("开始收集微信指数数据")
            wechat_collector = WechatIndexCollector(headless=True)
            wechat_data = wechat_collector.collect_wechat_index_data(start_date, end_date)
            self.logger.info("微信指数数据收集完成")
            
            # 处理数据
            self.logger.info("开始处理数据")
            processor = DataProcessor()
            processor.process_baidu_data(baidu_data)
            processor.process_wechat_data(wechat_data)
            
            # 生成Excel报告
            output_path = f"/mnt/okcomputer/output/index_collector/data/运营商指数报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            if processor.generate_excel_report(output_path):
                self.logger.info(f"Excel报告生成成功: {output_path}")
                
                # 发送通知（可以扩展邮件、微信等通知方式）
                self._send_notification(output_path, baidu_data, wechat_data)
            else:
                self.logger.error("Excel报告生成失败")
            
            self.logger.info("数据收集任务执行完成")
            
        except Exception as e:
            self.logger.error(f"数据收集任务执行失败: {str(e)}")
    
    def _send_notification(self, report_path, baidu_data, wechat_data):
        """发送通知"""
        try:
            # 这里可以扩展邮件、微信、钉钉等通知方式
            # 目前只记录日志
            self.logger.info(f"数据收集完成报告:")
            self.logger.info(f"报告文件: {report_path}")
            self.logger.info(f"百度指数截图: {baidu_data.get('screenshots', {})}")
            self.logger.info(f"微信指数收集方式: {wechat_data.get('method', 'unknown')}")
            
            # 可以在这里添加邮件发送逻辑
            # self._send_email_notification(report_path)
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {str(e)}")
    
    def manual_run(self):
        """手动运行一次"""
        self.logger.info("手动运行数据收集任务")
        self.collect_data_task()
    
    def start_scheduler(self):
        """启动定时调度器"""
        try:
            self.logger.info("启动定时调度器")
            
            # 设置定时任务
            # 每天检查一次是否应该收集数据
            schedule.every().day.at(f"{COLLECTION_HOUR:02d}:00").do(self.collect_data_task)
            
            # 启动调度器线程
            self.is_running = True
            self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.info(f"定时调度器已启动，每天 {COLLECTION_HOUR}:00 检查并执行数据收集任务")
            
        except Exception as e:
            self.logger.error(f"启动定时调度器失败: {str(e)}")
    
    def stop_scheduler(self):
        """停止定时调度器"""
        try:
            self.logger.info("停止定时调度器")
            self.is_running = False
            schedule.clear()
            
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            
            self.logger.info("定时调度器已停止")
            
        except Exception as e:
            self.logger.error(f"停止定时调度器失败: {str(e)}")
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                self.logger.error(f"调度器运行出错: {str(e)}")
                time.sleep(60)
    
    def get_status(self):
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'next_run': str(schedule.next_run()) if schedule.next_run() else None,
            'jobs': len(schedule.jobs),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='运营商指数数据自动收集工具')
    parser.add_argument('--mode', choices=['manual', 'schedule'], default='manual',
                       help='运行模式: manual(手动运行一次) 或 schedule(启动定时调度)')
    parser.add_argument('--headless', action='store_true',
                       help='是否使用无浏览器模式')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = IndexScheduler()
    
    if args.mode == 'manual':
        # 手动运行一次
        scheduler.manual_run()
    else:
        # 启动定时调度
        scheduler.start_scheduler()
        
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n接收到退出信号，正在停止调度器...")
            scheduler.stop_scheduler()
            print("调度器已停止")

if __name__ == '__main__':
    main()