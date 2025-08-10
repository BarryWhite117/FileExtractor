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
        return self._smart_categorize(file_info)
    
    def _smart_categorize(self, file_info: Dict) -> str:
        """智能分类文件"""
        name = file_info['name'].lower()
        file_type = file_info['file_type']
        extension = file_info.get('extension', '').lower()
        
        # 基于文件名的关键词分类
        if any(keyword in name for keyword in ['报告', 'report', '分析', 'analysis', '研究', 'research']):
            return 'reports_research'
        elif any(keyword in name for keyword in ['计划', 'plan', '规划', 'strategy', '方案', 'proposal']):
            return 'plans_strategies'
        elif any(keyword in name for keyword in ['工作', 'work', '项目', 'project', 'okr', 'pmo']):
            return 'work_projects'
        elif any(keyword in name for keyword in ['录音', 'audio', 'voice', '语音']):
            return 'audio_recordings'
        elif any(keyword in name for keyword in ['图片', 'image', 'photo', '截图', 'screenshot']):
            return 'images_photos'
        elif any(keyword in name for keyword in ['视频', 'video', '录像']):
            return 'videos'
        elif any(keyword in name for keyword in ['文档', 'document', 'doc', 'pdf']):
            return 'documents'
        elif any(keyword in name for keyword in ['数据', 'data', '表格', 'excel', 'xlsx']):
            return 'data_spreadsheets'
        elif any(keyword in name for keyword in ['合同', 'contract', '协议', 'agreement']):
            return 'contracts_agreements'
        elif any(keyword in name for keyword in ['简历', 'resume', 'cv', '个人资料']):
            return 'personal_documents'
        elif any(keyword in name for keyword in ['财务', 'finance', '账单', 'bill', '发票', 'invoice']):
            return 'financial_documents'
        elif any(keyword in name for keyword in ['学习', 'study', '培训', 'training', '教育', 'education']:
            return 'learning_materials'
        elif any(keyword in name for keyword in ['营销', 'marketing', '广告', 'advertisement', '宣传']):
            return 'marketing_materials'
        elif any(keyword in name for keyword in ['年报', 'annual', '季度', 'quarterly', '月度', 'monthly']):
            return 'periodic_reports'
        elif any(keyword in name for keyword in ['市场', 'market', '行业', 'industry', '洞察', 'insight']):
            return 'market_insights'
        elif any(keyword in name for keyword in ['技术', 'tech', 'ai', '人工智能', '数字化']):
            return 'technology_ai'
        elif any(keyword in name for keyword in ['健康', 'health', '医疗', 'medical', '健身', 'fitness']):
            return 'health_fitness'
        elif any(keyword in name for keyword in ['旅游', 'travel', '酒店', 'hotel', '机票', 'flight']):
            return 'travel_accommodation'
        elif any(keyword in name for keyword in ['购物', 'shopping', '订单', 'order', '商品', 'product']):
            return 'shopping_orders'
        elif any(keyword in name for keyword in ['社交', 'social', '聊天', 'chat', '微信', 'wechat']):
            return 'social_chat'
        elif any(keyword in name for keyword in ['娱乐', 'entertainment', '游戏', 'game', '音乐', 'music']):
            return 'entertainment_games'
        elif any(keyword in name for keyword in ['生活', 'life', '日常', 'daily', '家庭', 'family']):
            return 'daily_life'
        else:
            # 基于文件类型和扩展名的默认分类
            if file_type == 'image':
                return 'images_photos'
            elif file_type == 'video':
                return 'videos'
            elif file_type == 'audio':
                return 'audio_recordings'
            elif file_type == 'document':
                if extension in ['.pdf', '.doc', '.docx']:
                    return 'documents'
                elif extension in ['.xls', '.xlsx', '.csv']:
                    return 'data_spreadsheets'
                else:
                    return 'documents'
            elif file_type == 'archive':
                return 'archives'
            else:
                return 'other_files'
    
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
            # 基于文件名和扩展名进行智能分类
            category = self._smart_categorize(file_info)
            tags = self._generate_tags(file_info)
            
            return {
                'ai_analysis': True,
                'content_summary': f"智能分析: {file_info['name']} - {category}",
                'suggested_tags': tags,
                'category': category
            }
        except Exception as e:
            return {
                'ai_analysis': False,
                'error': str(e)
            }
    
    def categorize_file(self, file_path: str, file_info: Dict) -> str:
        """AI分类文件"""
        return self._smart_categorize(file_info)
    
    def _smart_categorize(self, file_info: Dict) -> str:
        """智能分类文件"""
        name = file_info['name'].lower()
        file_type = file_info['file_type']
        extension = file_info.get('extension', '').lower()
        
        # 基于文件名的关键词分类
        if any(keyword in name for keyword in ['报告', 'report', '分析', 'analysis', '研究', 'research']):
            return 'reports_research'
        elif any(keyword in name for keyword in ['计划', 'plan', '规划', 'strategy', '方案', 'proposal']):
            return 'plans_strategies'
        elif any(keyword in name for keyword in ['工作', 'work', '项目', 'project', 'okr', 'pmo']):
            return 'work_projects'
        elif any(keyword in name for keyword in ['录音', 'audio', 'voice', '语音']):
            return 'audio_recordings'
        elif any(keyword in name for keyword in ['图片', 'image', 'photo', '截图', 'screenshot']):
            return 'images_photos'
        elif any(keyword in name for keyword in ['视频', 'video', '录像']):
            return 'videos'
        elif any(keyword in name for keyword in ['文档', 'document', 'doc', 'pdf']):
            return 'documents'
        elif any(keyword in name for keyword in ['数据', 'data', '表格', 'excel', 'xlsx']):
            return 'data_spreadsheets'
        elif any(keyword in name for keyword in ['合同', 'contract', '协议', 'agreement']):
            return 'contracts_agreements'
        elif any(keyword in name for keyword in ['简历', 'resume', 'cv', '个人资料']):
            return 'personal_documents'
        elif any(keyword in name for keyword in ['财务', 'finance', '账单', 'bill', '发票', 'invoice']):
            return 'financial_documents'
        elif any(keyword in name for keyword in ['学习', 'study', '培训', 'training', '教育', 'education']):
            return 'learning_materials'
        elif any(keyword in name for keyword in ['营销', 'marketing', '广告', 'advertisement', '宣传']):
            return 'marketing_materials'
        elif any(keyword in name for keyword in ['年报', 'annual', '季度', 'quarterly', '月度', 'monthly']):
            return 'periodic_reports'
        elif any(keyword in name for keyword in ['市场', 'market', '行业', 'industry', '洞察', 'insight']):
            return 'market_insights'
        elif any(keyword in name for keyword in ['技术', 'tech', 'ai', '人工智能', '数字化']):
            return 'technology_ai'
        elif any(keyword in name for keyword in ['健康', 'health', '医疗', 'medical', '健身', 'fitness']):
            return 'health_fitness'
        elif any(keyword in name for keyword in ['旅游', 'travel', '酒店', 'hotel', '机票', 'flight']):
            return 'travel_accommodation'
        elif any(keyword in name for keyword in ['购物', 'shopping', '订单', 'order', '商品', 'product']):
            return 'shopping_orders'
        elif any(keyword in name for keyword in ['社交', 'social', '聊天', 'chat', '微信', 'wechat']):
            return 'social_chat'
        elif any(keyword in name for keyword in ['娱乐', 'entertainment', '游戏', 'game', '音乐', 'music']):
            return 'entertainment_games'
        elif any(keyword in name for keyword in ['生活', 'life', '日常', 'daily', '家庭', 'family']):
            return 'daily_life'
        else:
            # 基于文件类型和扩展名的默认分类
            if file_type == 'image':
                return 'images_photos'
            elif file_type == 'video':
                return 'videos'
            elif file_type == 'audio':
                return 'audio_recordings'
            elif file_type == 'document':
                if extension in ['.pdf', '.doc', '.docx']:
                    return 'documents'
                elif extension in ['.xls', '.xlsx', '.csv']:
                    return 'data_spreadsheets'
                else:
                    return 'documents'
            elif file_type == 'archive':
                return 'archives'
            else:
                return 'other_files'

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
