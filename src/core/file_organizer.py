import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class FileOrganizer:
    """文件整理器"""
    
    def __init__(self):
        self.organization_methods = {
            'by_type': self._organize_by_type,
            'by_time': self._organize_by_time,
            'by_content': self._organize_by_content,
            'by_size': self._organize_by_size,
            'by_chat': self._organize_by_chat
        }
    
    def organize_files(self, source_dir: str, target_dir: str, methods: List[str], 
                      ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """整理文件"""
        try:
            # 确保目标目录存在
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            # 扫描源目录
            from ..utils.file_utils import FileAnalyzer
            analyzer = FileAnalyzer()
            files = analyzer.scan_directory(source_dir)
            
            if not files:
                return {'success': False, 'message': '没有找到文件'}
            
            # 应用整理方法
            organized_files = {}
            for method in methods:
                if method in self.organization_methods:
                    result = self.organization_methods[method](files, target_dir, ai_analyzer, custom_rules, keep_originals)
                    organized_files[method] = result
            
            # 生成整理报告
            report = self._generate_report(organized_files, files)
            
            return {
                'success': True,
                'organized_files': organized_files,
                'report': report,
                'total_files': len(files)
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _organize_by_type(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按文件类型整理"""
        type_dirs = {}
        moved_files = []
        
        for file_info in files:
            file_type = file_info['file_type']
            type_dir = os.path.join(target_dir, 'by_type', file_type)
            
            if type_dir not in type_dirs:
                type_dirs[type_dir] = []
                Path(type_dir).mkdir(parents=True, exist_ok=True)
            
            # 移动/复制文件
            new_path = os.path.join(type_dir, file_info['name'])
            if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                moved_files.append({
                    'original': file_info['path'],
                    'new': new_path,
                    'type': file_type
                })
                type_dirs[type_dir].append(file_info['name'])
        
        return {
            'method': 'by_type',
            'directories': type_dirs,
            'moved_files': moved_files
        }
    
    def _organize_by_time(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按时间整理"""
        time_dirs = {}
        moved_files = []
        
        for file_info in files:
            modified_time = file_info['modified_time']
            year_month = f"{modified_time.year}_{modified_time.month:02d}"
            time_dir = os.path.join(target_dir, 'by_time', year_month)
            
            if time_dir not in time_dirs:
                time_dirs[time_dir] = []
                Path(time_dir).mkdir(parents=True, exist_ok=True)
            
            # 移动/复制文件
            new_path = os.path.join(time_dir, file_info['name'])
            if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                moved_files.append({
                    'original': file_info['path'],
                    'new': new_path,
                    'time': year_month
                })
                time_dirs[time_dir].append(file_info['name'])
        
        return {
            'method': 'by_time',
            'directories': time_dirs,
            'moved_files': moved_files
        }
    
    def _organize_by_content(self, files: List[Dict], target_dir: str, 
                            ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按内容类型整理（需要AI分析器）"""
        if not ai_analyzer:
            return {'method': 'by_content', 'error': '需要AI分析器'}
        
        content_dirs = {}
        moved_files = []
        
        for file_info in files:
            # 使用AI分析文件内容
            ai_result = ai_analyzer.analyze_file_content(file_info['path'], file_info)
            
            if ai_result.get('ai_analysis'):
                content_category = ai_result.get('category', 'unknown')
                content_dir = os.path.join(target_dir, 'by_content', content_category)
                
                if content_dir not in content_dirs:
                    content_dirs[content_dir] = []
                    Path(content_dir).mkdir(parents=True, exist_ok=True)
                
                # 移动/复制文件
                new_path = os.path.join(content_dir, file_info['name'])
                if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                    moved_files.append({
                        'original': file_info['path'],
                        'new': new_path,
                        'content_category': content_category,
                        'ai_tags': ai_result.get('suggested_tags', [])
                    })
                    content_dirs[content_dir].append(file_info['name'])
        
        return {
            'method': 'by_content',
            'directories': content_dirs,
            'moved_files': moved_files
        }
    
    def _organize_by_size(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按文件大小整理"""
        size_dirs = {}
        moved_files = []
        
        for file_info in files:
            size = file_info['size']
            if size > 100 * 1024 * 1024:  # 100MB
                size_category = 'large'
            elif size > 10 * 1024 * 1024:  # 10MB
                size_category = 'medium'
            else:
                size_category = 'small'
            
            size_dir = os.path.join(target_dir, 'by_size', size_category)
            
            if size_dir not in size_dirs:
                size_dirs[size_dir] = []
                Path(size_dir).mkdir(parents=True, exist_ok=True)
            
            # 移动/复制文件
            new_path = os.path.join(size_dir, file_info['name'])
            if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                moved_files.append({
                    'original': file_info['path'],
                    'new': new_path,
                    'size_category': size_category
                })
                size_dirs[size_dir].append(file_info['name'])
        
        return {
            'method': 'by_size',
            'directories': size_dirs,
            'moved_files': moved_files
        }
    
    def _organize_by_chat(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按聊天对象整理（基于文件路径分析）"""
        chat_dirs = {}
        moved_files = []
        
        for file_info in files:
            # 尝试从路径中提取聊天对象信息
            path_parts = Path(file_info['path']).parts
            chat_object = self._extract_chat_object(path_parts)
            
            chat_dir = os.path.join(target_dir, 'by_chat', chat_object)
            
            if chat_dir not in chat_dirs:
                chat_dirs[chat_dir] = []
                Path(chat_dir).mkdir(parents=True, exist_ok=True)
            
            # 移动/复制文件
            new_path = os.path.join(chat_dir, file_info['name'])
            if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                moved_files.append({
                    'original': file_info['path'],
                    'new': new_path,
                    'chat_object': chat_object
                })
                chat_dirs[chat_dir].append(file_info['name'])
        
        return {
            'method': 'by_chat',
            'directories': chat_dirs,
            'moved_files': moved_files
        }
    
    def _extract_chat_object(self, path_parts: Tuple) -> str:
        """从路径中提取聊天对象"""
        # 这里可以根据微信文件存储的路径结构来提取
        # 例如：/path/to/WeChat/Data/msg/2024/01/chat_id/
        for part in path_parts:
            if part.startswith('msg') or part.startswith('chat'):
                return part
        return 'unknown'
    
    def _move_or_copy_file(self, source: str, destination: str, keep_originals: bool) -> bool:
        """移动或复制文件（根据 keep_originals），同时处理重名"""
        try:
            # 如果目标文件已存在，添加序号
            if os.path.exists(destination):
                base, ext = os.path.splitext(destination)
                counter = 1
                while os.path.exists(destination):
                    destination = f"{base}_{counter}{ext}"
                    counter += 1
            
            if keep_originals:
                shutil.copy2(source, destination)
            else:
                shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"移动/复制文件失败 {source} -> {destination}: {e}")
            return False
    
    def _generate_report(self, organized_files: Dict, all_files: List[Dict]) -> Dict:
        """生成整理报告"""
        total_files = len(all_files)
        total_size = sum(f['size'] for f in all_files)
        
        # 统计文件类型
        type_stats = {}
        for file_info in all_files:
            file_type = file_info['file_type']
            if file_type not in type_stats:
                type_stats[file_type] = {'count': 0, 'size': 0}
            type_stats[file_type]['count'] += 1
            type_stats[file_type]['size'] += file_info['size']
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'type_statistics': type_stats,
            'organization_methods': list(organized_files.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_methods(self) -> List[str]:
        """获取可用的整理方法"""
        return list(self.organization_methods.keys())
    
    def get_method_description(self, method: str) -> str:
        """获取方法的描述"""
        descriptions = {
            'by_type': '按文件类型整理（图片、视频、文档等）',
            'by_time': '按修改时间整理（年_月）',
            'by_content': '按AI分析的内容类型整理',
            'by_size': '按文件大小整理（大、中、小）',
            'by_chat': '按聊天对象整理'
        }
        return descriptions.get(method, '未知方法')
