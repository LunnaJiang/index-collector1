"""
运营商指数数据自动收集工具 - 主程序入口
"""

import os
import sys
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

from config import create_directories
from scheduler import IndexScheduler
from baidu_collector import BaiduIndexCollector
from wechat_collector import WechatIndexCollector
from data_processor import DataProcessor

class IndexCollectorGUI:
    """图形用户界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("运营商指数数据自动收集工具")
        self.root.geometry("800x600")
        
        # 初始化组件
        self.scheduler = IndexScheduler()
        self.is_running = False
        
        # 创建界面
        self._create_widgets()
        
        # 初始化
        create_directories()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = tk.Label(self.root, text="运营商指数数据自动收集工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧面板 - 控制按钮
        control_frame = tk.LabelFrame(main_frame, text="控制面板", width=200)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        control_frame.pack_propagate(False)
        
        # 手动收集按钮
        self.manual_btn = tk.Button(control_frame, text="手动收集数据", 
                                   command=self.manual_collect,
                                   width=20, height=2, bg="#4CAF50", fg="white")
        self.manual_btn.pack(pady=10)
        
        # 启动定时任务按钮
        self.schedule_btn = tk.Button(control_frame, text="启动定时任务", 
                                     command=self.toggle_scheduler,
                                     width=20, height=2, bg="#2196F3", fg="white")
        self.schedule_btn.pack(pady=10)
        
        # 生成报告按钮
        self.report_btn = tk.Button(control_frame, text="生成Excel报告", 
                                   command=self.generate_report,
                                   width=20, height=2, bg="#FF9800", fg="white")
        self.report_btn.pack(pady=10)
        
        # 查看截图按钮
        self.screenshot_btn = tk.Button(control_frame, text="查看截图", 
                                       command=self.view_screenshots,
                                       width=20, height=2, bg="#9C27B0", fg="white")
        self.screenshot_btn.pack(pady=10)
        
        # 退出按钮
        self.exit_btn = tk.Button(control_frame, text="退出", 
                                 command=self.exit_application,
                                 width=20, height=2, bg="#F44336", fg="white")
        self.exit_btn.pack(pady=10)
        
        # 右侧面板 - 日志和状态
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 状态框架
        status_frame = tk.LabelFrame(right_frame, text="系统状态", height=100)
        status_frame.pack(fill=tk.X, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="就绪", font=("Arial", 12))
        self.status_label.pack(pady=20)
        
        # 日志框架
        log_frame = tk.LabelFrame(right_frame, text="运行日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=20, width=60)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        # 创建TextHandler用于在界面显示日志
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        # 设置日志
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 添加TextHandler
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(text_handler)
    
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def manual_collect(self):
        """手动收集数据"""
        def collect():
            try:
                self.update_status("正在收集数据...", "blue")
                self.manual_btn.config(state=tk.DISABLED)
                
                # 获取收集日期
                from config import get_collection_dates
                start_date, end_date = get_collection_dates()
                logging.info(f"收集数据范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
                
                # 收集百度指数
                logging.info("开始收集百度指数数据...")
                baidu_collector = BaiduIndexCollector(headless=True)
                baidu_data = baidu_collector.collect_baidu_index_data(start_date, end_date)
                logging.info("百度指数数据收集完成")
                
                # 收集微信指数
                logging.info("开始收集微信指数数据...")
                wechat_collector = WechatIndexCollector(headless=True)
                wechat_data = wechat_collector.collect_wechat_index_data(start_date, end_date)
                logging.info("微信指数数据收集完成")
                
                # 处理数据
                logging.info("开始处理数据...")
                processor = DataProcessor()
                processor.process_baidu_data(baidu_data)
                processor.process_wechat_data(wechat_data)
                
                # 生成报告
                output_path = f"/mnt/okcomputer/output/index_collector/data/运营商指数报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                if processor.generate_excel_report(output_path):
                    logging.info(f"Excel报告生成成功: {output_path}")
                    messagebox.showinfo("成功", f"数据收集完成！\n报告已保存到:\n{output_path}")
                else:
                    logging.error("Excel报告生成失败")
                    messagebox.showerror("错误", "Excel报告生成失败")
                
                self.update_status("数据收集完成", "green")
                
            except Exception as e:
                logging.error(f"数据收集失败: {str(e)}")
                self.update_status("数据收集失败", "red")
                messagebox.showerror("错误", f"数据收集失败:\n{str(e)}")
            finally:
                self.manual_btn.config(state=tk.NORMAL)
        
        # 在新线程中运行收集任务
        thread = threading.Thread(target=collect)
        thread.start()
    
    def toggle_scheduler(self):
        """切换定时任务状态"""
        if not self.is_running:
            self.scheduler.start_scheduler()
            self.is_running = True
            self.schedule_btn.config(text="停止定时任务", bg="#F44336")
            self.update_status("定时任务已启动", "green")
            logging.info("定时任务已启动")
        else:
            self.scheduler.stop_scheduler()
            self.is_running = False
            self.schedule_btn.config(text="启动定时任务", bg="#2196F3")
            self.update_status("定时任务已停止", "red")
            logging.info("定时任务已停止")
    
    def generate_report(self):
        """生成Excel报告"""
        try:
            self.update_status("正在生成报告...", "blue")
            
            processor = DataProcessor()
            
            # 这里可以从数据库或缓存中读取已有的数据
            # 目前生成空模板
            
            output_path = f"/mnt/okcomputer/output/index_collector/data/运营商指数报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            if processor.generate_excel_report(output_path):
                logging.info(f"Excel报告生成成功: {output_path}")
                messagebox.showinfo("成功", f"Excel报告生成成功！\n保存位置:\n{output_path}")
                self.update_status("报告生成完成", "green")
            else:
                logging.error("Excel报告生成失败")
                messagebox.showerror("错误", "Excel报告生成失败")
                self.update_status("报告生成失败", "red")
                
        except Exception as e:
            logging.error(f"生成报告失败: {str(e)}")
            messagebox.showerror("错误", f"生成报告失败:\n{str(e)}")
            self.update_status("报告生成失败", "red")
    
    def view_screenshots(self):
        """查看截图"""
        try:
            screenshots_dir = "/mnt/okcomputer/output/index_collector/screenshots"
            if os.path.exists(screenshots_dir):
                os.system(f"open '{screenshots_dir}'" if os.name == 'posix' else f"start '{screenshots_dir}'")
            else:
                messagebox.showinfo("提示", "截图目录不存在，请先运行数据收集")
        except Exception as e:
            messagebox.showerror("错误", f"打开截图目录失败:\n{str(e)}")
    
    def exit_application(self):
        """退出应用"""
        if self.is_running:
            if messagebox.askyesno("确认", "定时任务正在运行，确定要退出吗？"):
                self.scheduler.stop_scheduler()
            else:
                return
        
        self.root.quit()

def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    app = IndexCollectorGUI(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == '__main__':
    main()