import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QTextEdit, QFileDialog, QCheckBox, QGroupBox,
                             QProgressBar, QTabWidget, QScrollArea, QFrame,
                             QMessageBox, QComboBox, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

from ..core.file_organizer import FileOrganizer
from ..ai.ai_analyzer import AIAnalyzerFactory, AIConfig
from ..utils.file_utils import FileAnalyzer

class FileExtractorGUI(QMainWindow):
    """文件提取器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileExtractor - 微信文件整理工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化组件
        self.file_organizer = FileOrganizer()
        self.ai_config = AIConfig()
        self.ai_analyzer = None
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.setup_ui()
        
        # 连接信号
        self.connect_signals()
        
        # 加载配置
        self.load_config()
    
    def setup_styles(self):
        """设置界面样式"""
        # 设置字体
        font = QFont("PingFang SC", 10)
        self.setFont(font)
        
        # 设置样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #28a745;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                text-align: center;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 4px;
            }
        """)
    
    def setup_ui(self):
        """创建界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("FileExtractor - 微信文件整理工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 文件整理标签页
        self.setup_file_organization_tab(tab_widget)
        
        # AI 设置标签页
        self.setup_ai_settings_tab(tab_widget)
        
        # 关于标签页
        self.setup_about_tab(tab_widget)
    
    def setup_file_organization_tab(self, tab_widget):
        """设置文件整理标签页"""
        org_widget = QWidget()
        org_layout = QVBoxLayout(org_widget)
        
        # 源目录选择
        source_group = QGroupBox("选择源目录")
        source_layout = QHBoxLayout(source_group)
        
        self.source_path_edit = QLineEdit()
        self.source_path_edit.setPlaceholderText("请选择微信文件所在目录...")
        source_layout.addWidget(self.source_path_edit)
        
        self.browse_source_btn = QPushButton("浏览...")
        source_layout.addWidget(self.browse_source_btn)
        
        org_layout.addWidget(source_group)
        
        # 目标目录选择
        target_group = QGroupBox("选择目标目录")
        target_layout = QHBoxLayout(target_group)
        
        self.target_path_edit = QLineEdit()
        self.target_path_edit.setPlaceholderText("请选择整理后的文件保存目录...")
        target_layout.addWidget(self.target_path_edit)
        
        self.browse_target_btn = QPushButton("浏览...")
        target_layout.addWidget(self.browse_target_btn)
        
        org_layout.addWidget(target_group)
        
        # 整理方式选择
        method_group = QGroupBox("选择整理方式")
        method_layout = QGridLayout(method_group)
        
        self.method_checkboxes = {}
        methods = self.file_organizer.get_available_methods()
        
        for i, method in enumerate(methods):
            checkbox = QCheckBox(self.file_organizer.get_method_description(method))
            self.method_checkboxes[method] = checkbox
            method_layout.addWidget(checkbox, i // 2, i % 2)
        
        org_layout.addWidget(method_group)
        
        # AI 功能开关
        ai_group = QGroupBox("AI 功能")
        ai_layout = QHBoxLayout(ai_group)
        
        self.ai_enabled_checkbox = QCheckBox("启用 AI 内容分析")
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["OpenAI GPT", "通义千问"])
        
        ai_layout.addWidget(self.ai_enabled_checkbox)
        ai_layout.addWidget(QLabel("选择模型:"))
        ai_layout.addWidget(self.ai_model_combo)
        ai_layout.addStretch()
        
        org_layout.addWidget(ai_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("扫描文件")
        self.scan_btn.setStyleSheet("background-color: #17a2b8;")
        button_layout.addWidget(self.scan_btn)
        
        self.organize_btn = QPushButton("开始整理")
        self.organize_btn.setEnabled(False)
        button_layout.addWidget(self.organize_btn)
        
        self.preview_btn = QPushButton("预览结果")
        self.preview_btn.setStyleSheet("background-color: #ffc107; color: #212529;")
        button_layout.addWidget(self.preview_btn)
        
        org_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        org_layout.addWidget(self.progress_bar)
        
        # 结果显示
        result_group = QGroupBox("处理结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        result_layout.addWidget(self.result_text)
        
        org_layout.addWidget(result_group)
        
        # 添加标签页
        tab_widget.addTab(org_widget, "文件整理")
    
    def setup_ai_settings_tab(self, tab_widget):
        """设置 AI 设置标签页"""
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        
        # OpenAI 设置
        openai_group = QGroupBox("OpenAI 设置")
        openai_layout = QVBoxLayout(openai_group)
        
        openai_layout.addWidget(QLabel("API Key:"))
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("请输入 OpenAI API Key...")
        openai_layout.addWidget(self.openai_key_edit)
        
        openai_layout.addWidget(QLabel("模型:"))
        self.openai_model_combo = QComboBox()
        self.openai_model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        openai_layout.addWidget(self.openai_model_combo)
        
        ai_layout.addWidget(openai_group)
        
        # 通义千问设置
        tongyi_group = QGroupBox("通义千问设置")
        tongyi_layout = QVBoxLayout(tongyi_group)
        
        tongyi_layout.addWidget(QLabel("API Key:"))
        self.tongyi_key_edit = QLineEdit()
        self.tongyi_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.tongyi_key_edit.setPlaceholderText("请输入通义千问 API Key...")
        tongyi_layout.addWidget(self.tongyi_key_edit)
        
        ai_layout.addWidget(tongyi_group)
        
        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_ai_config)
        ai_layout.addWidget(save_btn)
        
        ai_layout.addStretch()
        
        tab_widget.addTab(ai_widget, "AI 设置")
    
    def setup_about_tab(self, tab_widget):
        """设置关于标签页"""
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>FileExtractor - 微信文件整理工具</h2>
        <p>这是一个帮助整理微信聊天文件的工具，支持多种整理方式和 AI 内容分析。</p>
        
        <h3>主要功能：</h3>
        <ul>
            <li>按文件类型整理（图片、视频、文档等）</li>
            <li>按时间整理（年_月）</li>
            <li>按文件大小整理</li>
            <li>按聊天对象整理</li>
            <li>AI 内容分析（可选）</li>
        </ul>
        
        <h3>使用方法：</h3>
        <ol>
            <li>选择微信文件所在目录</li>
            <li>选择整理后的保存目录</li>
            <li>选择整理方式</li>
            <li>点击"开始整理"</li>
        </ol>
        
        <h3>注意事项：</h3>
        <ul>
            <li>请确保有足够的磁盘空间</li>
            <li>建议先备份重要文件</li>
            <li>AI 功能需要配置相应的 API Key</li>
        </ul>
        """)
        
        about_layout.addWidget(about_text)
        tab_widget.addTab(about_widget, "关于")
    
    def connect_signals(self):
        """连接信号"""
        self.browse_source_btn.clicked.connect(self.browse_source_directory)
        self.browse_target_btn.clicked.connect(self.browse_target_directory)
        self.scan_btn.clicked.connect(self.scan_files)
        self.organize_btn.clicked.connect(self.organize_files)
        self.preview_btn.clicked.connect(self.preview_organization)
        
        # 路径变化时启用扫描按钮
        self.source_path_edit.textChanged.connect(self.check_paths)
        self.target_path_edit.textChanged.connect(self.check_paths)
    
    def browse_source_directory(self):
        """浏览源目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择微信文件目录")
        if directory:
            self.source_path_edit.setText(directory)
    
    def browse_target_directory(self):
        """浏览目标目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择整理后的保存目录")
        if directory:
            self.target_path_edit.setText(directory)
    
    def check_paths(self):
        """检查路径是否有效"""
        source_valid = bool(self.source_path_edit.text().strip())
        target_valid = bool(self.target_path_edit.text().strip())
        self.scan_btn.setEnabled(source_valid and target_valid)
    
    def scan_files(self):
        """扫描文件"""
        source_dir = self.source_path_edit.text().strip()
        if not source_dir or not os.path.exists(source_dir):
            QMessageBox.warning(self, "警告", "请选择有效的源目录")
            return
        
        self.result_text.clear()
        self.result_text.append("正在扫描文件...")
        
        # 创建扫描线程
        self.scan_thread = ScanThread(source_dir)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.start()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.scan_btn.setEnabled(False)
    
    def on_scan_finished(self, files):
        """扫描完成"""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if files:
            self.result_text.append(f"扫描完成！找到 {len(files)} 个文件")
            self.organize_btn.setEnabled(True)
        else:
            self.result_text.append("没有找到文件")
            self.organize_btn.setEnabled(False)
    
    def organize_files(self):
        """整理文件"""
        source_dir = self.source_path_edit.text().strip()
        target_dir = self.target_path_edit.text().strip()
        
        if not source_dir or not target_dir:
            QMessageBox.warning(self, "警告", "请选择源目录和目标目录")
            return
        
        # 获取选中的整理方式
        selected_methods = [method for method, checkbox in self.method_checkboxes.items() 
                          if checkbox.isChecked()]
        
        if not selected_methods:
            QMessageBox.warning(self, "警告", "请至少选择一种整理方式")
            return
        
        # 创建 AI 分析器
        if self.ai_enabled_checkbox.isChecked():
            self.setup_ai_analyzer()
        
        # 开始整理
        self.result_text.append("开始整理文件...")
        self.organize_btn.setEnabled(False)
        
        # 创建整理线程
        self.organize_thread = OrganizeThread(
            self.file_organizer, source_dir, target_dir, 
            selected_methods, self.ai_analyzer
        )
        self.organize_thread.finished.connect(self.on_organize_finished)
        self.organize_thread.start()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
    
    def setup_ai_analyzer(self):
        """设置 AI 分析器"""
        if self.ai_model_combo.currentText() == "OpenAI GPT":
            api_key = self.openai_key_edit.text().strip()
            if api_key:
                self.ai_analyzer = AIAnalyzerFactory.create_analyzer('openai', api_key)
        elif self.ai_model_combo.currentText() == "通义千问":
            api_key = self.tongyi_key_edit.text().strip()
            if api_key:
                self.ai_analyzer = AIAnalyzerFactory.create_analyzer('tongyi', api_key)
    
    def on_organize_finished(self, result):
        """整理完成"""
        self.progress_bar.setVisible(False)
        self.organize_btn.setEnabled(True)
        
        if result.get('success'):
            self.result_text.append("整理完成！")
            self.result_text.append(f"总共处理了 {result.get('total_files', 0)} 个文件")
            
            # 显示详细结果
            report = result.get('report', {})
            if report:
                self.result_text.append(f"\n整理报告:")
                self.result_text.append(f"总文件数: {report.get('total_files', 0)}")
                self.result_text.append(f"总大小: {self.format_size(report.get('total_size', 0))}")
                self.result_text.append(f"使用的方法: {', '.join(report.get('organization_methods', []))}")
        else:
            self.result_text.append(f"整理失败: {result.get('message', '未知错误')}")
    
    def preview_organization(self):
        """预览整理结果"""
        QMessageBox.information(self, "预览", "预览功能开发中...")
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def load_config(self):
        """加载配置"""
        # 加载 AI 配置
        if self.ai_config.is_enabled():
            self.ai_enabled_checkbox.setChecked(True)
        
        # 加载 API Keys
        openai_key = self.ai_config.get_api_key('openai')
        if openai_key:
            self.openai_key_edit.setText(openai_key)
        
        tongyi_key = self.ai_config.get_api_key('tongyi')
        if tongyi_key:
            self.tongyi_key_edit.setText(tongyi_key)
    
    def save_ai_config(self):
        """保存 AI 配置"""
        # 保存 API Keys
        openai_key = self.openai_key_edit.text().strip()
        if openai_key:
            self.ai_config.set_api_key('openai', openai_key)
        
        tongyi_key = self.tongyi_key_edit.text().strip()
        if tongyi_key:
            self.ai_config.set_api_key('tongyi', tongyi_key)
        
        # 保存启用状态
        self.ai_config.set_enabled(self.ai_enabled_checkbox.isChecked())
        
        QMessageBox.information(self, "成功", "AI 配置已保存")


class ScanThread(QThread):
    """文件扫描线程"""
    finished = pyqtSignal(list)
    
    def __init__(self, source_dir):
        super().__init__()
        self.source_dir = source_dir
    
    def run(self):
        """运行扫描"""
        try:
            analyzer = FileAnalyzer()
            files = analyzer.scan_directory(self.source_dir)
            self.finished.emit(files)
        except Exception as e:
            print(f"扫描失败: {e}")
            self.finished.emit([])


class OrganizeThread(QThread):
    """文件整理线程"""
    finished = pyqtSignal(dict)
    
    def __init__(self, organizer, source_dir, target_dir, methods, ai_analyzer):
        super().__init__()
        self.organizer = organizer
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.methods = methods
        self.ai_analyzer = ai_analyzer
    
    def run(self):
        """运行整理"""
        try:
            result = self.organizer.organize_files(
                self.source_dir, self.target_dir, 
                self.methods, self.ai_analyzer
            )
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({'success': False, 'message': str(e)})


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("FileExtractor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Vibe Coding")
    
    # 创建主窗口
    window = FileExtractorGUI()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
