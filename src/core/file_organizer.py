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
        
        # 中文目录名称映射
        self.chinese_names = {
            # 文件类型分类
            'jpg': '图片文件',
            'png': '图片文件', 
            'gif': '图片文件',
            'bmp': '图片文件',
            'tiff': '图片文件',
            'heic': '图片文件',
            'webp': '图片文件',
            'mp4': '视频文件',
            'avi': '视频文件',
            'mov': '视频文件',
            'wmv': '视频文件',
            'flv': '视频文件',
            'mkv': '视频文件',
            'webm': '视频文件',
            'm4v': '视频文件',
            'mp3': '音频文件',
            'wav': '音频文件',
            'aac': '音频文件',
            'm4a': '音频文件',
            'flac': '音频文件',
            'ogg': '音频文件',
            'wma': '音频文件',
            'pdf': 'PDF文档',
            'doc': 'Word文档',
            'docx': 'Word文档',
            'txt': '文本文件',
            'rtf': '富文本文件',
            'ppt': 'PPT演示',
            'pptx': 'PPT演示',
            'xls': 'Excel表格',
            'xlsx': 'Excel表格',
            'zip': '压缩文件',
            'rar': '压缩文件',
            '7z': '压缩文件',
            'tar': '压缩文件',
            'gz': '压缩文件',
            'bz2': '压缩文件',
            'no_ext': '无扩展名文件',
            
            # 内容分类
            'reports_research': '报告研究',
            'plans_strategies': '计划策略',
            'work_projects': '工作项目',
            'audio_recordings': '录音文件',
            'images_photos': '图片照片',
            'videos': '视频文件',
            'documents': '文档资料',
            'data_spreadsheets': '数据表格',
            'contracts_agreements': '合同协议',
            'personal_documents': '个人资料',
            'financial_documents': '财务文档',
            'learning_materials': '学习资料',
            'marketing_materials': '营销材料',
            'periodic_reports': '定期报告',
            'market_insights': '市场洞察',
            'technology_ai': '技术AI',
            'health_fitness': '健康健身',
            'travel_accommodation': '旅游住宿',
            'shopping_orders': '购物订单',
            'social_chat': '社交聊天',
            'entertainment_games': '娱乐游戏',
            'daily_life': '日常生活',
            'archives': '归档文件',
            'other_files': '其他文件',
            
            # 大小分类
            'tiny': '极小文件',
            'small': '小文件',
            'medium': '中等文件',
            'large': '大文件',
            'huge': '超大文件',
            
            # 聊天对象分类
            'unknown': '未知聊天',
            
            # 时间分类保持原样（年月格式）
        }
    
    def _get_chinese_name(self, key: str) -> str:
        """获取中文目录名称"""
        return self.chinese_names.get(key, key)
    
    def organize_files(self, source_dir: str, target_dir: str, methods: List[str], 
                      ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """整理文件"""
        try:
            print(f"🔧 FileOrganizer.organize_files 开始...")
            print(f"📍 源目录: {source_dir}")
            print(f"🎯 目标目录: {target_dir}")
            print(f"🔧 整理方式: {methods}")
            print(f"🤖 AI 分析器: {ai_analyzer}")
            print(f"📋 保留原文件: {keep_originals}")
            
            # 确保目标目录存在
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            print(f"✅ 目标目录已创建/确认: {target_dir}")
            
            # 扫描源目录
            try:
                from ..utils.file_utils import FileAnalyzer
            except ImportError:
                # 如果相对导入失败，尝试绝对导入
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from utils.file_utils import FileAnalyzer
            
            analyzer = FileAnalyzer()
            files = analyzer.scan_directory(source_dir)
            print(f"📁 扫描到 {len(files)} 个文件")
            
            if not files:
                print("❌ 没有找到文件")
                return {'success': False, 'message': '没有找到文件'}
            
            # 应用整理方法
            organized_files = {}
            for method in methods:
                print(f"🔧 正在应用整理方法: {method}")
                if method in self.organization_methods:
                    result = self.organization_methods[method](files, target_dir, ai_analyzer, custom_rules, keep_originals)
                    organized_files[method] = result
                    print(f"✅ 方法 {method} 完成，结果: {result}")
                else:
                    print(f"❌ 未知的整理方法: {method}")
            
            # 生成整理报告
            report = self._generate_report(organized_files, files)
            print(f"📊 生成报告: {report}")
            
            final_result = {
                'success': True,
                'organized_files': organized_files,
                'report': report,
                'total_files': len(files)
            }
            print(f"🎉 整理完成，最终结果: {final_result}")
            return final_result
            
        except Exception as e:
            print(f"❌ 整理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': str(e)}
    
    def _organize_by_type(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按文件后缀类型整理（按扩展名）"""
        type_dirs: Dict[str, List[str]] = {}
        moved_files: List[Dict] = []
        
        for file_info in files:
            ext = (file_info.get('extension') or '').lower()
            ext_key = ext[1:] if ext.startswith('.') and len(ext) > 1 else (ext if ext else 'no_ext')
            # 归一化常见同类后缀（如 jpeg->jpg, htm->html 等）
            ext_key = self._normalize_extension(ext_key)
            # 使用中文目录名称
            chinese_dir_name = self._get_chinese_name(ext_key)
            type_dir = os.path.join(target_dir, '按类型分类', chinese_dir_name)
            
            if type_dir not in type_dirs:
                type_dirs[type_dir] = []
                Path(type_dir).mkdir(parents=True, exist_ok=True)
            
            # 移动/复制文件
            new_path = os.path.join(type_dir, file_info['name'])
            if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                moved_files.append({
                    'original': file_info['path'],
                    'new': new_path,
                    'type': ext_key
                })
                type_dirs[type_dir].append(file_info['name'])
        
        return {
            'method': 'by_type',
            'directories': type_dirs,
            'moved_files': moved_files
        }

    def _normalize_extension(self, ext_key: str) -> str:
        """规范化后缀名，合并同类后缀，返回不带点的后缀"""
        if not ext_key:
            return 'no_ext'
        mapping = {
            # images
            'jpeg': 'jpg', 'jpe': 'jpg',
            'tif': 'tiff',
            # web/text
            'htm': 'html',
        }
        return mapping.get(ext_key, ext_key)
    
    def _organize_by_time(self, files: List[Dict], target_dir: str, 
                          ai_analyzer=None, custom_rules: Dict = None, keep_originals: bool = False) -> Dict:
        """按时间整理"""
        time_dirs = {}
        moved_files = []
        
        for file_info in files:
            modified_time = file_info['modified_time']
            year_month = f"{modified_time.year}年{modified_time.month:02d}月"
            time_dir = os.path.join(target_dir, '按时间分类', year_month)
            
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
                # 使用中文目录名称
                chinese_dir_name = self._get_chinese_name(content_category)
                content_dir = os.path.join(target_dir, '按内容分类', chinese_dir_name)
                
                if content_dir not in content_dirs:
                    content_dirs[content_dir] = []
                    Path(content_dir).mkdir(parents=True, exist_ok=True)
                
                # 移动/复制文件
                new_path = os.path.join(content_dir, file_info['name'])
                if self._move_or_copy_file(file_info['path'], new_path, keep_originals):
                    moved_files.append({
                        'original': file_info['path'],
                        'new': new_path,
                        'content_category': content_category
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
            if size < 1024:  # 1KB
                size_category = 'tiny'
            elif size < 1024 * 1024:  # 1MB
                size_category = 'small'
            elif size < 10 * 1024 * 1024:  # 10MB
                size_category = 'medium'
            elif size < 100 * 1024 * 1024:  # 100MB
                size_category = 'large'
            else:
                size_category = 'huge'
            
            # 使用中文目录名称
            chinese_dir_name = self._get_chinese_name(size_category)
            size_dir = os.path.join(target_dir, '按大小分类', chinese_dir_name)
            
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
            
            # 使用中文目录名称
            chinese_dir_name = self._get_chinese_name(chat_object)
            chat_dir = os.path.join(target_dir, '按聊天分类', chinese_dir_name)
            
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
        """获取整理方法的中文描述"""
        descriptions = {
            'by_type': '按文件类型分类（图片、视频、音频、文档等）',
            'by_time': '按修改时间分类（年月分组）',
            'by_content': '按内容智能分类（需要AI分析）',
            'by_size': '按文件大小分类（极小、小、中等、大、超大）',
            'by_chat': '按聊天对象分类（基于文件路径分析）'
        }
        return descriptions.get(method, method)
