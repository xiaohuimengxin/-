from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox,
                           QTextEdit, QRadioButton, QHBoxLayout, QGridLayout,
                           QFrame, QSizePolicy, QProgressBar, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor
import os
from fcpxml_parser import FCPXMLParser
from frame_extractor import FrameExtractor, Resolution
import subprocess
from PyQt5.QtCore import QStandardPaths
import time

class DropArea(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setFrameShape(QFrame.NoFrame)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签
        self.label = QLabel('\n将 FCPXML 文件拖放到这里\n或点击选择文件\n')
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(13)
        self.label.setFont(font)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet('''
                DropArea {
                    border: 2px dashed #3daee9;
                    border-radius: 10px;
                    background-color: #f0f0f0;
                    margin: 10px;
                }
            ''')
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet('''
            DropArea {
                border: 2px dashed #aaaaaa;
                border-radius: 10px;
                background-color: #f8f8f8;
                margin: 10px;
            }
            DropArea:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }
        ''')

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.fileDropped.emit(files[0])
            # 保持深色模式下的绿色样式
            if isinstance(self.window(), MainWindow) and self.window().current_theme:
                self.setStyleSheet('''
                    DropArea {
                        border: 2px dashed #2A8252;
                        border-radius: 10px;
                        background-color: rgba(42, 130, 82, 0.6);
                        margin: 10px;
                    }
                ''')
            else:
                self.setStyleSheet('''
                    DropArea {
                        border: 2px dashed #BDBDBD;
                        border-radius: 10px;
                        background-color: rgba(33, 150, 243, 0.1);
                        margin: 10px;
                    }
                ''')

    def mousePressEvent(self, event):
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            main_window.select_fcpxml_file()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fcpxml_path = None
        self.output_dir = os.path.expanduser("~/Desktop")
        self.is_file_dialog_open = False  # 添加标志位
        self.init_ui()
        
        # 添加系统主题检测和自动切换
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_system_theme)
        self.theme_timer.start(1000)  # 每秒检查一次系统主题
        self.current_theme = None
        self.check_system_theme()

    def check_system_theme(self):
        """检查系统主题并在需要时切换"""
        try:
            # macOS 检测深色模式的命令
            result = subprocess.run([
                'defaults', 'read', '-g', 'AppleInterfaceStyle'
            ], capture_output=True, text=True)
            is_dark = result.returncode == 0  # 如果命令成功执行，说明是深色模式
            
            if is_dark != self.current_theme:
                self.current_theme = is_dark
                self.apply_theme(is_dark)
        except Exception as e:
            print(f"检查系统主题失败: {e}")

    def apply_theme(self, is_dark):
        """应用深色或浅色主题"""
        if is_dark:
            # 深色主题样式保持不变
            self.setStyleSheet('''
                /* 全局深色背景 */
                QMainWindow, QWidget {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                
                /* 所有框架使用深色背景 */
                QFrame {
                    background-color: #1E1E1E;
                    border: 1px solid #3D3D3D;
                    border-radius: 5px;
                    padding: 5px;
                }
                
                /* 特定框架使用稍浅的背景色 */
                QFrame#darkFrame {
                    background-color: #2D2D2D;
                }
                
                /* 输入框和文本框使用深色背景 */
                QLineEdit {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #3D3D3D;
                    border-radius: 3px;
                    padding: 5px;
                    selection-background-color: #007AFF;
                    selection-color: #FFFFFF;
                }
                
                /* 文本编辑器样式 */
                QTextEdit {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #3D3D3D;
                    border-radius: 3px;
                    selection-background-color: #007AFF;
                    selection-color: #FFFFFF;
                }
                
                /* 按钮样式 */
                QPushButton {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                    border: 1px solid #3D3D3D;
                    border-radius: 3px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                
                QPushButton:hover {
                    background-color: #3D3D3D;
                }
                
                QPushButton:disabled {
                    background-color: #252525;
                    color: #666666;
                }
                
                /* 标签样式 */
                QLabel {
                    color: #E0E0E0;
                    background-color: transparent;
                }
                
                /* 单选按钮样式 */
                QRadioButton {
                    color: #E0E0E0;
                    background-color: transparent;
                    padding: 5px;
                }
                
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    background-color: #2D2D2D;
                    border: 2px solid #3D3D3D;
                }
                
                QRadioButton::indicator:checked {
                    background-color: #007AFF;
                    border: 2px solid #007AFF;
                }
                
                /* 进度条样式 */
                QProgressBar {
                    background-color: #2D2D2D;
                    border: 1px solid #3D3D3D;
                    border-radius: 3px;
                    color: #E0E0E0;
                    text-align: center;
                }
                
                QProgressBar::chunk {
                    background-color: #007AFF;
                    border-radius: 2px;
                }

                /* 文件对话框样式 */
                QFileDialog {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                
                QFileDialog QWidget {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                
                /* 占位符文本颜色 */
                QLineEdit:placeholder-shown {
                    color: #808080;
                }
                
                /* 滚动条样式 */
                QScrollBar:vertical {
                    background-color: #1E1E1E;
                    width: 12px;
                    margin: 0px;
                }

                QScrollBar::handle:vertical {
                    background-color: #3D3D3D;
                    min-height: 20px;
                    border-radius: 6px;
                }

                QScrollBar::handle:vertical:hover {
                    background-color: #4D4D4D;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background-color: #1E1E1E;
                }
            ''')
            
            # 拖放区域深色样式 - 调整透明度
            self.drop_area.setStyleSheet('''
                DropArea {
                    border: 2px dashed #3D3D3D;
                    border-radius: 10px;
                    background-color: rgba(42, 130, 82, 0.6);  /* 提高透明度到 0.6 */
                    margin: 10px;
                }
                DropArea:hover {
                    background-color: rgba(42, 130, 82, 0.9);  /* 悬停时提高到 0.9 */
                    border-color: #2A8252;  /* 边框颜色保持不变 */
                }
                QLabel {
                    color: #E0E0E0;
                    background-color: transparent;
                }
            ''')

            # 提取按钮特殊样式
            self.extract_btn.setStyleSheet('''
                QPushButton {
                    padding: 8px 30px;
                    background-color: #007AFF;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0066CC;
                }
                QPushButton:disabled {
                    background-color: #252525;
                    color: #666666;
                }
            ''')
            
        else:
            # 更新浅色主题样式，添加更多细节
            self.setStyleSheet('''
                /* 全局浅色背景 */
                QMainWindow, QWidget {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                
                /* 所有框架使用浅色背景 */
                QFrame {
                    background-color: #F5F5F5;
                    border: 1px solid #E0E0E0;
                    border-radius: 5px;
                    padding: 5px;
                }
                
                /* 特定框架使用白色背景 */
                QFrame#darkFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                
                /* 输入框样式 */
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #E0E0E0;
                    border-radius: 3px;
                    padding: 5px;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                }
                
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
                
                /* 文本编辑器样式 */
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #E0E0E0;
                    border-radius: 3px;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                }
                
                QTextEdit:focus {
                    border: 1px solid #2196F3;
                }
                
                /* 按钮样式 */
                QPushButton {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #E0E0E0;
                    border-radius: 3px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                
                QPushButton:hover {
                    background-color: #F5F5F5;
                    border: 1px solid #2196F3;
                }
                
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
                
                QPushButton:disabled {
                    background-color: #F5F5F5;
                    color: #BDBDBD;
                    border: 1px solid #E0E0E0;
                }
                
                /* 标签样式 */
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
                
                /* 单选按钮样式 */
                QRadioButton {
                    color: #333333;
                    background-color: transparent;
                    padding: 5px;
                }
                
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    background-color: #FFFFFF;
                    border: 2px solid #E0E0E0;
                }
                
                QRadioButton::indicator:hover {
                    border: 2px solid #2196F3;
                }
                
                QRadioButton::indicator:checked {
                    background-color: #2196F3;
                    border: 2px solid #2196F3;
                }
                
                /* 进度条样式 */
                QProgressBar {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 3px;
                    color: #333333;
                    text-align: center;
                }
                
                QProgressBar::chunk {
                    background-color: #2196F3;
                    border-radius: 2px;
                }
                
                /* 滚动条样式 */
                QScrollBar:vertical {
                    background-color: #F5F5F5;
                    width: 12px;
                    margin: 0px;
                }

                QScrollBar::handle:vertical {
                    background-color: #E0E0E0;
                    min-height: 20px;
                    border-radius: 6px;
                }

                QScrollBar::handle:vertical:hover {
                    background-color: #BDBDBD;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background-color: #F5F5F5;
                }
                
                /* 占位符文本颜色 */
                QLineEdit:placeholder-shown {
                    color: #BDBDBD;
                }
            ''')
            
            # 拖放区���浅色样式 - 添加淡蓝色
            self.drop_area.setStyleSheet('''
                DropArea {
                    border: 2px dashed #BDBDBD;
                    border-radius: 10px;
                    background-color: rgba(33, 150, 243, 0.1);  /* 淡蓝色带透明度 */
                    margin: 10px;
                }
                DropArea:hover {
                    background-color: rgba(33, 150, 243, 0.2);  /* 悬停时加深 */
                    border-color: #2196F3;  /* 蓝色边框 */
                }
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
            ''')

            # 提取按钮特殊样式保持不变
            self.extract_btn.setStyleSheet('''
                QPushButton {
                    padding: 8px 30px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #FFFFFF;
                }
            ''')

    def update_extract_button_style(self, is_dark):
        """更新提取按钮的样式"""
        if is_dark:
            self.extract_btn.setStyleSheet('''
                QPushButton {
                    padding: 8px 30px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #404040;
                    color: #808080;
                }
            ''')
        else:
            self.extract_btn.setStyleSheet('''
                QPushButton {
                    padding: 8px 30px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #FFFFFF;
                }
            ''')

    def init_ui(self):
        self.setWindowTitle('FCPX 记点提取器')
        self.setMinimumSize(533, 400)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)

        # 拖放区域
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        self.drop_area.fileDropped.connect(self.handle_file_selected)

        # 文件信息显示
        file_info = QFrame()
        file_info.setObjectName('darkFrame')  # 添加对象名以便样式表识别
        file_layout = QHBoxLayout(file_info)
        file_layout.setContentsMargins(8, 4, 8, 4)
        
        self.file_path_label = QLabel('未选择文件')
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.select_fcpxml_file)
        
        file_layout.addWidget(QLabel('当前文件:'))
        file_layout.addWidget(self.file_path_label, 1)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_info)

        # 输出目录选择
        output_frame = QFrame()
        output_frame.setObjectName('darkFrame')  # 添加对象名以便样式表识别
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(8, 4, 8, 4)
        
        output_label = QLabel('输出目录:')
        self.output_path_label = QLabel(self.output_dir)
        output_btn = QPushButton('选择目录')
        output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_label, 1)
        output_layout.addWidget(output_btn)
        layout.addWidget(output_frame)

        # 添加文件夹命名输入框
        folder_name_frame = QFrame()
        folder_name_frame.setObjectName('darkFrame')  # 添加对象名以便样式表识别
        folder_name_layout = QHBoxLayout(folder_name_frame)
        folder_name_layout.setContentsMargins(8, 4, 8, 4)
        
        folder_name_label = QLabel('导出文件夹名称:')
        self.folder_name_input = QLineEdit()
        self.folder_name_input.setPlaceholderText('留空将自动使用时间戳命名')
        self.folder_name_input.setStyleSheet('')  # 删除原有的样式设置
        
        folder_name_layout.addWidget(folder_name_label)
        folder_name_layout.addWidget(self.folder_name_input, 1)
        layout.addWidget(folder_name_frame)

        # 分辨率选择
        resolution_frame = QFrame()
        resolution_frame.setObjectName('darkFrame')  # 使用全局深色样式
        resolution_layout = QHBoxLayout(resolution_frame)
        resolution_layout.setContentsMargins(8, 4, 8, 4)
        
        resolution_label = QLabel('输出分辨率:')
        self.ultra_radio = QRadioButton('超清 (3840×2160)')
        self.high_radio = QRadioButton('高清 (1920×1080)')
        self.low_radio = QRadioButton('标清 (1280×720)')
        self.high_radio.setChecked(True)
        
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.ultra_radio)
        resolution_layout.addWidget(self.high_radio)
        resolution_layout.addWidget(self.low_radio)
        resolution_layout.addStretch()
        layout.addWidget(resolution_frame)

        # 添加图片质量选项
        quality_frame = QFrame()
        quality_frame.setObjectName('darkFrame')  # 使用全局深色样式
        quality_layout = QHBoxLayout(quality_frame)
        quality_layout.setContentsMargins(8, 4, 8, 4)
        
        quality_label = QLabel('图片质量:')
        self.high_quality_radio = QRadioButton('高质量 (处理较慢)')
        self.normal_quality_radio = QRadioButton('标准质量 (处理较快)')
        self.high_quality_radio.setChecked(True)  # 默认选择高质量
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.high_quality_radio)
        quality_layout.addWidget(self.normal_quality_radio)
        quality_layout.addStretch()
        layout.addWidget(quality_frame)

        # 标记点列表
        markers_frame = QFrame()
        markers_frame.setObjectName('darkFrame')  # 使用全局深色样式
        markers_layout = QVBoxLayout(markers_frame)
        markers_layout.setContentsMargins(8, 4, 8, 4)
        
        markers_layout.addWidget(QLabel('标记点列表:'))
        self.markers_text = QTextEdit()
        self.markers_text.setReadOnly(True)
        self.markers_text.setStyleSheet('')  # 删除原有的样式设置
        markers_layout.addWidget(self.markers_text)
        layout.addWidget(markers_frame)

        # 添加进度条区域（移到提取按钮之前）
        progress_frame = QFrame()
        progress_frame.setObjectName('darkFrame')  # 使用全局深色样式
        progress_layout = QVBoxLayout(progress_frame)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                border: 1px solid #dddddd;
                border-radius: 3px;
                text-align: center;
                background-color: #f0f0f0;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        ''')
        self.progress_bar.hide()  # 默认隐藏
        
        # 进度标签
        self.progress_label = QLabel('准备开始导出...')
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.hide()  # 默认隐藏
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_frame)

        # 底部按钮区域
        bottom_frame = QFrame()
        bottom_layout = QVBoxLayout(bottom_frame)
        
        # 提取按钮
        self.extract_btn = QPushButton('提取记帧')
        self.extract_btn.setStyleSheet('''
            QPushButton {
                padding: 5px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        ''')
        self.extract_btn.clicked.connect(self.extract_frames)
        self.extract_btn.setEnabled(False)
        bottom_layout.addWidget(self.extract_btn, alignment=Qt.AlignCenter)
        
        # 态标签
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.status_label)
        
        layout.addWidget(bottom_frame)

    def select_fcpxml_file(self):
        """选择 FCPXML 文件，使用 AppleScript 调用系统访达"""
        if self.is_file_dialog_open:  # 检查是否已有对话框打开
            return
            
        try:
            self.is_file_dialog_open = True  # 设置标志位
            
            script = '''
            tell application "System Events"
                tell process "Finder"
                    activate
                    delay 0.1
                    set theFile to choose file ¬
                        with prompt "选择 FCPXML 文件" ¬
                        of type {"fcpxml", "xml"}
                    return POSIX path of theFile
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, 
                                  text=True,
                                  encoding='utf-8')
            
            if result.returncode == 0:
                file_path = result.stdout.strip()
                if file_path and os.path.exists(file_path):
                    self.handle_file_selected(file_path)
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"文件选择失败：{str(e)}")
        finally:
            self.is_file_dialog_open = False  # 重置标志位

    def select_output_dir(self):
        """选择输出目录，使用 AppleScript 调用系统访达"""
        if self.is_file_dialog_open:  # 检查是否已有对话框打开
            return
            
        try:
            self.is_file_dialog_open = True  # 设置标志位
            
            script = '''
            tell application "System Events"
                tell process "Finder"
                    activate
                    delay 0.1
                    set theFolder to choose folder ¬
                        with prompt "选择输出目录"
                    return POSIX path of theFolder
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, 
                                  text=True,
                                  encoding='utf-8')
            
            if result.returncode == 0:
                dir_path = result.stdout.strip()
                if dir_path and os.path.exists(dir_path):
                    self.output_dir = dir_path
                    self.output_path_label.setText(dir_path)
                    self.update_extract_button()
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"目录选择失败：{str(e)}")
        finally:
            self.is_file_dialog_open = False  # 重置标志位

    def handle_file_selected(self, file_path):
        if file_path.lower().endswith('.fcpxml'):
            self.fcpxml_path = file_path
            self.drop_area.label.setText(f'已选择文件：\n{os.path.basename(file_path)}')
            self.file_path_label.setText(os.path.basename(file_path))
            self.update_extract_button()
        else:
            QMessageBox.warning(self, "错误", "请选择有效的FCPXML文件")

    def update_extract_button(self):
        self.extract_btn.setEnabled(bool(self.fcpxml_path and self.output_dir))

    def update_progress(self, current, total, success_count):
        """更新进度条和标签"""
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"正在导出: {current}/{total} (成功: {success_count})")
        QApplication.processEvents()  # 确保UI更新

    def extract_frames(self):
        try:
            # 在开始提取之前显示进度条
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.progress_label.show()
            self.extract_btn.setEnabled(False)
            QApplication.processEvents()  # 确保UI更新

            # 解析FCPXML
            parser = FCPXMLParser(self.fcpxml_path)
            markers = parser.parse()

            if not markers:
                self.progress_bar.hide()
                self.progress_label.hide()
                self.extract_btn.setEnabled(True)
                self.markers_text.setText("未找到标记点")
                QMessageBox.warning(self, "警告", "未找到任何标记点，请检查FCPXML文件是否正确")
                return

            # 显示标记点信息
            self.markers_text.clear()
            for marker in markers:
                self.markers_text.append(
                    f"名称: {marker.name}\n"
                    f"时间: {marker.timestamp:.3f}秒\n"
                    f"帧号: {marker.frame_id}\n"
                    f"视频: {os.path.basename(marker.video_path)}\n"
                    f"------------------------"
                )

            # 设置分辨率
            if self.ultra_radio.isChecked():
                resolution = Resolution.ULTRA_LANDSCAPE
            elif self.high_radio.isChecked():
                resolution = Resolution.HIGH_LANDSCAPE
            else:
                resolution = Resolution.LOW_LANDSCAPE

            # 获取用户自定义的文件夹名称
            custom_folder_name = self.folder_name_input.text().strip()
            
            # 创建输出目录（使用自定义名称或时间戳）
            if custom_folder_name:
                output_dir = os.path.join(self.output_dir, custom_folder_name)
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_dir = os.path.join(self.output_dir, timestamp)

            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)

            # 取帧
            extractor = FrameExtractor(
                output_dir,  # 使用新的输出目录
                resolution=resolution,
                high_quality=self.high_quality_radio.isChecked()
            )
            success_count = extractor.extract_frames(
                markers, 
                progress_callback=self.update_progress
            )

            # 隐藏进度条和标签
            self.progress_bar.hide()
            self.progress_label.hide()
            self.extract_btn.setEnabled(True)

            # 使用访达打开输出目录
            try:
                script = f'''
                tell application "System Events"
                    tell application "Finder"
                        open POSIX file "{output_dir}"
                        activate
                    end tell
                end tell
                '''
                subprocess.run(['osascript', '-e', script])
            except Exception as e:
                print(f"打开输出目录失败: {str(e)}")

            # 显示结果
            QMessageBox.information(self, "完成", 
                f"处理完成！\n"
                f"- 标记点: {len(markers)} 个\n"
                f"- 已保存图像: {success_count} 个\n"
                f"- 输出目录: {output_dir}")

        except Exception as e:
            self.progress_bar.hide()
            self.progress_label.hide()
            self.extract_btn.setEnabled(True)
            QMessageBox.critical(self, "错误", f"处理过程中出现错误：{str(e)}")

def main():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()