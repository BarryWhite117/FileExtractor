import os
import json
import requests
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class BaseAIAnalyzer(ABC):
    """AI分析器基类"""
    
    @abstractmethod
    def analyze_file_content(self, file_path: str, file_info: Dict) -> Dict:
        """分析文件内容"""
        pass
    
    @abstractmethod
    def categorize_file(self, file_path: str, file_info: Dict) -> str:
        """AI分类文件"""
        pass

class OpenAIAnalyzer(BaseAIAnalyzer):
    """OpenAI GPT分析器"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def analyze_file_content(self, file_path: str, file_info: Dict) -> Dict:
        """分析文件内容"""
        try:
            # 这里可以根据文件类型进行不同的分析
            # 对于文本文件，可以直接读取内容
            # 对于图片，可以使用GPT-4V等视觉模型
            # 这里先返回基础信息
            return {
                'ai_analysis': True,
                'content_summary': f"文件类型: {file_info['file_type']}, 大小: {file_info['size']} bytes",
                'suggested_tags': self._generate_tags(file_info),
                'category': self.categorize_file(file_path, file_info)
            }
        except Exception as e:
            return {
                'ai_analysis': False,
                'error': str(e)
            }
    
    def categorize_file(self, file_path: str, file_info: Dict) -> str:
        """AI分类文件"""
        try:
            # 根据文件类型和大小进行智能分类
            if file_info['file_type'] == 'image':
                return self._categorize_image(file_info)
            elif file_info['file_type'] == 'document':
                return self._categorize_document(file_info)
            elif file_info['file_type'] == 'video':
                return self._categorize_video(file_info)
            else:
                return 'other'
        except Exception as e:
            return 'other'
    
    def _generate_tags(self, file_info: Dict) -> List[str]:
        """生成标签"""
        tags = []
        tags.append(file_info['file_type'])
        tags.append(file_info['extension'])
        
        # 根据文件大小添加标签
        if file_info['size'] > 100 * 1024 * 1024:  # 100MB
            tags.append('large_file')
        elif file_info['size'] < 1024:  # 1KB
            tags.append('small_file')
        
        return tags
    
    def _categorize_image(self, file_info: Dict) -> str:
        """分类图片"""
        # 这里可以集成更复杂的图片分析
        return 'image'
    
    def _categorize_document(self, file_info: Dict) -> str:
        """分类文档"""
        return 'document'
    
    def _categorize_video(self, file_info: Dict) -> str:
        """分类视频"""
        return 'video'

class TongyiAnalyzer(BaseAIAnalyzer):
    """通义千问分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def analyze_file_content(self, file_path: str, file_info: Dict) -> Dict:
        """分析文件内容"""
        try:
            return {
                'ai_analysis': True,
                'content_summary': f"通义千问分析: {file_info['name']}",
                'suggested_tags': self._generate_tags(file_info),
                'category': self.categorize_file(file_path, file_info)
            }
        except Exception as e:
            return {
                'ai_analysis': False,
                'error': str(e)
            }
    
    def categorize_file(self, file_path: str, file_info: Dict) -> str:
        """AI分类文件"""
        return file_info['file_type']

class AIAnalyzerFactory:
    """AI分析器工厂"""
    
    @staticmethod
    def create_analyzer(ai_type: str, api_key: str) -> Optional[BaseAIAnalyzer]:
        """创建AI分析器"""
        if ai_type == 'openai':
            return OpenAIAnalyzer(api_key)
        elif ai_type == 'tongyi':
            return TongyiAnalyzer(api_key)
        else:
            return None

class AIConfig:
    """AI配置管理"""
    
    def __init__(self, config_file: str = "ai_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'enabled': False,
            'default_ai': 'openai',
            'api_keys': {},
            'models': {},
            'last_paths': { 'source': '', 'target': '' }
        }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存AI配置失败: {e}")
    
    def get_api_key(self, ai_type: str) -> Optional[str]:
        """获取API密钥"""
        return self.config.get('api_keys', {}).get(ai_type)
    
    def set_api_key(self, ai_type: str, api_key: str):
        """设置API密钥"""
        if 'api_keys' not in self.config:
            self.config['api_keys'] = {}
        self.config['api_keys'][ai_type] = api_key
        self.save_config()
    
    def is_enabled(self) -> bool:
        """是否启用AI功能"""
        return self.config.get('enabled', False)
    
    def set_enabled(self, enabled: bool):
        """设置是否启用AI功能"""
        self.config['enabled'] = enabled
        self.save_config()

    # ========= 通用应用配置：最近使用的目录 =========
    def get_last_path(self, key: str) -> Optional[str]:
        """读取上次保存的路径，key 可为 'source' 或 'target'"""
        return self.config.get('last_paths', {}).get(key)

    def set_last_path(self, key: str, path: str):
        """保存路径（独立保存源或目标路径）"""
        if 'last_paths' not in self.config:
            self.config['last_paths'] = {}
        self.config['last_paths'][key] = path
        self.save_config()
