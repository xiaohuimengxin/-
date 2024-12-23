from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QRadioButton, 
                           QButtonGroup, QFileDialog, QMessageBox)
import os
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCPX 标记点提取器")
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        # ... 文件选择和输出目录选择的代码保持不变 ...
        
        # 在输出目录选择之后添加文件夹命名选项
        self.folder_name_group = QHBoxLayout()
        self.folder_name_label = QLabel("导出文件夹名称：")
        self.folder_name_input = QLineEdit()
        self.folder_name_input.setPlaceholderText("留空将自动使用时间戳命名")
        self.folder_name_group.addWidget(self.folder_name_label)
        self.folder_name_group.addWidget(self.folder_name_input)
        
        # 将文件夹命名选项添加到主布局中
        self.main_layout.addLayout(self.folder_name_group)
        
        # ... 分辨率选择和其他选项的代码保持不变 ...

    def handle_export(self):
        try:
            if not hasattr(self, 'output_dir') or not self.output_dir:
                QMessageBox.warning(self, "警告", "请先选择输出目录！")
                return
                
            # 获取用户输入的文件夹名称
            custom_folder_name = self.folder_name_input.text().strip()
            
            if custom_folder_name:
                # 使用用户输入的名称
                output_folder = os.path.join(self.output_dir, custom_folder_name)
            else:
                # 使用时间戳命名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_folder = os.path.join(self.output_dir, timestamp)
            
            # 创建输出文件夹
            os.makedirs(output_folder, exist_ok=True)
            
            # ... 继续处理帧提取的逻辑 ...
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出过程中发生错误：{str(e)}")