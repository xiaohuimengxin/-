import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List
import os
import urllib.parse

@dataclass
class Marker:
    name: str
    timestamp: float
    frame_id: int
    video_path: str

@dataclass
class VideoInfo:
    path: str
    fps: float
    start_time: float = 0.0
    clip_id: str = ""
    duration: float = 0.0

class FCPXMLParser:
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.markers = []
        self.fps = 30
        self.videos = []
        
    def _parse_time(self, time_str: str) -> tuple[float, int]:
        if not time_str:
            return 0.0, 0
            
        time_str = time_str.rstrip('s')
        
        if '/' in time_str:
            numerator, denominator = map(float, time_str.split('/'))
            seconds = numerator / denominator
            frame = int(numerator)
            return seconds, frame
        
        seconds = float(time_str)
        frame = int(seconds * self.fps)
        return seconds, frame
        
    def _find_video_info(self, root: ET.Element) -> List[VideoInfo]:
        """查找所有视频文件信息"""
        videos = []
        # 查找所有资源
        for asset in root.findall(".//resources/asset"):
            asset_id = asset.get('id')
            media_rep = asset.find(".//media-rep[@kind='original-media']")
            if media_rep is not None:
                src = media_rep.get('src')
                if src:
                    # 处理URL编码的路径
                    path = urllib.parse.unquote(src.replace('file://', ''))
                    
                    # 查找帧率信息
                    format_elem = root.find(f".//format[@id='{asset.get('format')}']")
                    if format_elem is not None:
                        fps_str = format_elem.get('frameDuration')
                        if fps_str and '/' in fps_str:
                            _, denominator = map(float, fps_str.rstrip('s').split('/'))
                            fps = denominator
                            
                            videos.append(VideoInfo(
                                path=path,
                                fps=fps,
                                clip_id=asset_id
                            ))
        return videos
        
    def parse(self) -> List[Marker]:
        """解析FCPXML文件中的所有标记点和视频信息"""
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        
        # 获取所有视频信息
        self.videos = self._find_video_info(root)
        if self.videos:
            self.fps = self.videos[0].fps
        
        # 解析标记点
        for asset_clip in root.findall(".//asset-clip"):
            # 获取视频引用ID
            ref_id = asset_clip.get('ref')
            
            # 找到对应的视频信息
            video_info = next((v for v in self.videos if v.clip_id == ref_id), None)
            if not video_info:
                continue
            
            # 获取片段的偏移时间
            offset = 0.0
            offset_str = asset_clip.get('offset', '0s')
            offset, _ = self._parse_time(offset_str)
            
            # 解析此片段中的所有标记点
            for marker in asset_clip.findall("marker"):
                name = marker.get('value', 'unnamed_marker')
                start = marker.get('start', '0')
                
                try:
                    timestamp, frame_id = self._parse_time(start)
                    
                    # 调整时间戳（考虑片段偏移）
                    adjusted_timestamp = timestamp
                    
                    self.markers.append(Marker(
                        name=name,
                        timestamp=adjusted_timestamp,
                        frame_id=frame_id,
                        video_path=video_info.path
                    ))
                except ValueError as e:
                    print(f"警告: 无法解析时间戳 '{start}' (标记点: {name})")
                    continue
        
        if not self.markers:
            print("未找到任何标记点。")
            self._print_xml_structure(root)
        
        return self.markers

    def _print_xml_structure(self, element, level=0):
        """打印XML结构，用于调试"""
        print("  " * level + element.tag)
        for child in element:
            self._print_xml_structure(child, level + 1)