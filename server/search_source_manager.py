import os
import importlib.util
import hashlib
import json

class SearchSourceManager:
    def __init__(self, blacklist=None):
        self.search_sources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'search_sources')
        os.makedirs(self.search_sources_dir, exist_ok=True)
        self.blacklist = blacklist or []
        self.search_source_config = self.load_search_source_config()
        self.search_sources = self.load_search_sources()
    
    def load_search_source_config(self):
        """
        加载搜索源配置文件
        
        Returns:
            dict: 搜索源配置字典，每个元素包含name和description
        """
        config_file_path = os.path.join(self.search_sources_dir, 'search_source_config.json')
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_source_id(self, file_path):
        """
        根据文件路径生成唯一的搜索源ID
        
        Args:
            file_path (str): 搜索源文件路径
            
        Returns:
            str: 唯一的搜索源ID
        """
        # 使用文件路径的MD5哈希作为唯一ID
        return hashlib.md5(file_path.encode('utf-8')).hexdigest()
    
    def load_search_sources(self):
        """
        加载所有搜索源
        
        Returns:
            list: 搜索源列表，每个元素包含id、name和module
        """
        search_sources = []
        
        # 遍历搜索源目录中的所有.py文件
        for filename in os.listdir(self.search_sources_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(self.search_sources_dir, filename)
                source_id = self.get_source_id(file_path)
                
                # 导入模块
                spec = importlib.util.spec_from_file_location(filename[:-3], file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 检查模块是否包含main函数
                    if hasattr(module, 'main') and callable(module.main):
                        # 从配置文件中获取数据源说明
                        source_config = self.search_source_config.get(filename[:-3], {})
                        search_sources.append({
                            'id': source_id,
                            'name': filename[:-3],
                            'display_name': source_config.get('name', filename[:-3]),
                            'description': source_config.get('description', ''),
                            'module': module,
                            'enabled': source_id not in self.blacklist
                        })
        
        return search_sources
    
    def get_enabled_sources(self):
        """
        获取所有启用的搜索源
        
        Returns:
            list: 启用的搜索源列表
        """
        return [source for source in self.search_sources if source['enabled']]
    
    def get_all_sources(self):
        """
        获取所有搜索源（包括禁用的）
        
        Returns:
            list: 所有搜索源列表
        """
        return self.search_sources
    
    def enable_source(self, source_id):
        """
        启用搜索源
        
        Args:
            source_id (str): 搜索源ID
            
        Returns:
            bool: 操作是否成功
        """
        for source in self.search_sources:
            if source['id'] == source_id:
                source['enabled'] = True
                return True
        return False
    
    def disable_source(self, source_id):
        """
        禁用搜索源
        
        Args:
            source_id (str): 搜索源ID
            
        Returns:
            bool: 操作是否成功
        """
        for source in self.search_sources:
            if source['id'] == source_id:
                source['enabled'] = False
                return True
        return False
    
    def reload_sources(self):
        """
        重新加载所有搜索源
        """
        self.search_sources = self.load_search_sources()