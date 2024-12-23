from setuptools import setup
import os
import subprocess
import sys
import shutil

# 获取 FFmpeg 路径
def get_ffmpeg_path():
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return '/opt/homebrew/bin/ffmpeg'  # 默认 Homebrew 安装路径

# 获取 FFprobe 路径
def get_ffprobe_path():
    try:
        result = subprocess.run(['which', 'ffprobe'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return '/opt/homebrew/bin/ffprobe'  # 默认 Homebrew 安装路径

FFMPEG_PATH = get_ffmpeg_path()
FFPROBE_PATH = get_ffprobe_path()

# 确保 FFmpeg 和 FFprobe 存在
if not os.path.exists(FFMPEG_PATH):
    raise Exception(f"FFmpeg not found at {FFMPEG_PATH}")
if not os.path.exists(FFPROBE_PATH):
    raise Exception(f"FFprobe not found at {FFPROBE_PATH}")

APP = ['main.py']
DATA_FILES = [
    ('MacOS', [FFMPEG_PATH, FFPROBE_PATH])  # 将 FFmpeg 和 FFprobe 放在 MacOS 目录下
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter'],
    'includes': [
        'PIL',
        'xml.etree',
        'xml.etree.ElementTree',
        'urllib.parse',
        'subprocess',
        'json',
        'datetime',
        'os',
        'typing',
        'dataclasses',
        'enum'
    ],
    'excludes': ['setuptools'],
    'resources': [FFMPEG_PATH, FFPROBE_PATH],  # 将 FFmpeg 和 FFprobe 添加为资源
    'plist': {
        'CFBundleName': 'FCPX Marker Extractor',
        'CFBundleDisplayName': 'FCPX Marker Extractor',
        'CFBundleIdentifier': 'com.fcpx.markerextractor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSAppleEventsUsageDescription': 'This app needs access to run FFmpeg commands.',
        'NSAppleMusicUsageDescription': 'This app needs access to process video files.',
    }
}

def post_process():
    """打包后的后处理"""
    app_path = os.path.join('dist', 'FCPX Marker Extractor.app')
    if os.path.exists(app_path):
        # 复制 ffmpeg 和 ffprobe 到应用程序包
        macos_path = os.path.join(app_path, 'Contents', 'MacOS')
        
        # 复制并设置 ffmpeg
        ffmpeg_dest = os.path.join(macos_path, 'ffmpeg')
        shutil.copy2(FFMPEG_PATH, ffmpeg_dest)
        os.chmod(ffmpeg_dest, 0o755)
        
        # 复制并设置 ffprobe
        ffprobe_dest = os.path.join(macos_path, 'ffprobe')
        shutil.copy2(FFPROBE_PATH, ffprobe_dest)
        os.chmod(ffprobe_dest, 0o755)

setup(
    name='FCPX Marker Extractor',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# 执行后处理
if 'py2app' in sys.argv:
    post_process() 