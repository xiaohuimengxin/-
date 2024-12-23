import subprocess
import os
import sys
from typing import List
from fcpxml_parser import Marker
from enum import Enum
import json
from datetime import datetime

class Resolution(Enum):
    # 横版视频分辨率
    LOW_LANDSCAPE = (1280, 720)
    HIGH_LANDSCAPE = (1920, 1080)
    ULTRA_LANDSCAPE = (3840, 2160)
    
    # 竖版视频分辨率
    LOW_PORTRAIT = (720, 1280)
    HIGH_PORTRAIT = (1080, 1920)
    ULTRA_PORTRAIT = (2160, 3840)
    
    @classmethod
    def get_resolution_name(cls, resolution):
        names = {
            cls.LOW_LANDSCAPE: "标清 (1280×720)",
            cls.HIGH_LANDSCAPE: "高清 (1920×1080)",
            cls.ULTRA_LANDSCAPE: "超清 (3840×2160)",
        }
        return names.get(resolution, "未知分辨率")

class FrameExtractor:
    def __init__(self, output_dir: str, resolution: Resolution = Resolution.HIGH_LANDSCAPE, high_quality: bool = True):
        self.output_dir = output_dir
        self.resolution = resolution
        self.high_quality = high_quality
        
        # 获取 ffmpeg 和 ffprobe 的路径
        if getattr(sys, 'frozen', False):
            # ���果是打包后的应用
            base_path = os.path.dirname(sys.executable)
            self.ffmpeg_path = os.path.join(base_path, 'ffmpeg')
            self.ffprobe_path = os.path.join(base_path, 'ffprobe')
        else:
            # 如果是开发环境
            self.ffmpeg_path = 'ffmpeg'
            self.ffprobe_path = 'ffprobe'

    def get_video_info(self, video_path: str) -> dict:
        """获取视频信息，包括宽高比"""
        try:
            command = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            video_info = json.loads(result.stdout)
            
            video_stream = next(
                (stream for stream in video_info['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if video_stream:
                width = int(video_stream['width'])
                height = int(video_stream['height'])
                return {'width': width, 'height': height}
            
            return None
        except Exception as e:
            print(f"获取视频信息失败: {str(e)}")
            return None

    def get_output_resolution(self, video_info: dict) -> tuple[int, int]:
        """根据原视频比例确定输出分辨率"""
        if not video_info:
            return self.resolution.value
            
        original_width = video_info['width']
        original_height = video_info['height']
        is_portrait = original_height > original_width
        
        # 计算原始视频的宽高比
        aspect_ratio = original_height / original_width
        
        # 根据视频方向和设置的分辨率选择输出尺寸
        if is_portrait:
            # 竖版视频：以高度为基准，按比例计算宽度
            if self.resolution == Resolution.ULTRA_LANDSCAPE:
                base_height = 3840  # 4K
                base_width = int(base_height / aspect_ratio)
            elif self.resolution == Resolution.HIGH_LANDSCAPE:
                base_height = 1920  # 1080p
                base_width = int(base_height / aspect_ratio)
            else:
                base_height = 1280  # 720p
                base_width = int(base_height / aspect_ratio)
            return (base_width, base_height)
        else:
            # 横版视频：以宽度为基准，按比例计算高度
            if self.resolution == Resolution.ULTRA_LANDSCAPE:
                base_width = 3840  # 4K
                base_height = int(base_width * aspect_ratio)
            elif self.resolution == Resolution.HIGH_LANDSCAPE:
                base_width = 1920  # 1080p
                base_height = int(base_width * aspect_ratio)
            else:
                base_width = 1280  # 720p
                base_height = int(base_width * aspect_ratio)
            return (base_width, base_height)

    def extract_frame(self, video_path: str, timestamp: float, output_filename: str) -> bool:
        """从视频中提取指定时间点的帧"""
        try:
            output_path = os.path.join(self.output_subdir, f"{output_filename}.jpg")
            
            video_info = self.get_video_info(video_path)
            width, height = self.get_output_resolution(video_info)
            
            if self.high_quality:
                # 高质量设置
                command = [
                    self.ffmpeg_path,
                    '-ss', str(timestamp),
                    '-i', video_path,
                    '-vframes', '1',
                    '-q:v', '1',
                    '-compression_level', '0',
                    '-vf', (f'scale={width}:{height}:flags=lanczos,'
                           'unsharp=3:3:1.5:3:3:0.5'),
                    '-preset', 'veryslow',
                    '-qmin', '1',
                    '-qmax', '1',
                    '-y',
                    output_path
                ]
            else:
                # 标准质量设置
                command = [
                    self.ffmpeg_path,
                    '-ss', str(timestamp),
                    '-i', video_path,
                    '-vframes', '1',
                    '-q:v', '3',
                    '-vf', f'scale={width}:{height}',
                    '-y',
                    output_path
                ]
            
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"提取帧失败: {str(e)}")
            return False

    def extract_frames(self, markers: List[Marker], progress_callback=None) -> int:
        """提取所有标记点对应的帧"""
        success_count = 0
        total_markers = len(markers)
        
        # 直接使用传入的输出目录，不再创建子文件夹
        self.output_subdir = self.output_dir
        
        for i, marker in enumerate(markers, 1):
            # 清理文件名
            safe_name = "".join(c for c in marker.name if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = f"marker_{marker.frame_id}"
                
            if self.extract_frame(marker.video_path, marker.timestamp, safe_name):
                success_count += 1
            
            # 更新进度
            if progress_callback:
                progress_callback(i, total_markers, success_count)
        
        # 在 macOS 中打开输出文件夹
        try:
            subprocess.run(['open', self.output_dir])
        except Exception as e:
            print(f"打开输出文件夹失败: {str(e)}")
                
        # 只返回成功计数
        return success_count