# FCPX Marker Frame Extractor

这是一个用于从 Final Cut Pro X 项目中提取标记点对应帧图片的工具。

## 功能特点
- 解析 FCPXML 文件中的标记点信息
- 支持所有轨道中的标记点提取
- 支持多个视频文件的标记点提取
- 支持4k高清(3840×2160)和1080p高清(1920×1080)两种输出分辨率
- 支持自定义导出文件夹名称（可选）
- 导出的图片以标记点名称命名
- 简单易用的图形界面
## 使用要求
- Python 3.x
- FFmpeg
- PyQt5

## 安装步骤

1. 安装 FFmpeg (如果尚未安装):
   ```bash
   brew install ffmpeg
   ```

2. 创建并激活虚拟环境:
   ```bash
   # 创建虚拟环境
   python3 -m venv fcpx_venv
   
   # 激活虚拟环境
   source fcpx_venv/bin/activate
   ```

3. 安装 Python 依赖:
   ```bash
   # 确保在虚拟环境中
   pip install -r requirements.txt
   ```

4. 运行程序:
   ```bash
   python3 main.py
   ```

5. 使用完毕后，可以退出虚拟环境:
   ```bash
   deactivate
   ```

## 打包说明

如果你想将程序打包成macOS应用程序，请按照以下步骤操作：

1. 确保已安装所有依赖：
   ```bash
   # 激活虚拟环境
   source fcpx_venv/bin/activate
   
   # 安装依赖
   pip3 install -r requirements.txt
   ```

2. 清理旧的构建文件：
   ```bash
   rm -rf build dist
   ```

3. 执行打包命令：
   ```bash
   python3 setup.py py2app
   ```

4. 打包完成后，可以在 `dist` 目录下找到可执行文件。

# 5. 执行签名命令
codesign --force --deep --sign - "dist/FCPX Marker Extractor.app"

# 6. 验证签名
codesign --verify --deep --strict "dist/FCPX Marker Extractor.app"
注意事项：
- 确���系统已安装 FFmpeg
- 打包过程可能需要几分钟时间
- 打包完成后的应用程序会自动包含所需的 FFmpeg

## 使用说明
1. 点击"选择FCPXML文件"按钮选择项目文件
2. 点击"选择输出目录"按钮选择图片保存位置
3. 可选：输入自定义导出文件夹名称（留空将使用时间戳命名）
4. 点击"提取标记帧"开始处理

## 注意事项
- 请确保在运行程序前已激活虚拟环境
- 如果遇到权限问题，可能需要使用 sudo 安装 FFmpeg

# 签名应用
codesign --force --deep --sign - "dist/FCPX Marker Extractor.app"