import os
import shutil
import magic
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import mimetypes

class FileAnalyzer:
    """文件分析器"""
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
        self.file_types = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg', '.wma'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.ppt', '.pptx', '.xls', '.xlsx'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'other': []
        }
    
    def get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            mime_type = self.mime.from_file(str(path))
            
            # 获取文件类型
            file_type = self._categorize_file(path.suffix.lower(), mime_type)
            
            return {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'file_type': file_type,
                'mime_type': mime_type,
                'extension': path.suffix.lower()
            }
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return {}
    
    def _categorize_file(self, extension: str, mime_type: str) -> str:
        """分类文件类型"""
        for category, exts in self.file_types.items():
            if extension in exts:
                return category
        
        # 根据 MIME 类型分类
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('text/') or mime_type in ['application/pdf', 'application/msword']:
            return 'document'
        elif mime_type.startswith('application/zip') or mime_type.startswith('application/x-rar'):
            return 'archive'
        
        return 'other'
    
    def scan_directory(self, directory: str) -> List[Dict]:
        """扫描目录获取所有文件信息"""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        files.append(file_info)
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return files
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_file_icon(self, file_type: str) -> str:
        """获取文件类型图标"""
        icons = {
            'image': '🖼️',
            'video': '🎥',
            'audio': '🎵',
            'document': '📄',
            'archive': '📦',
            'other': '📁'
        }
        return icons.get(file_type, '📁')
