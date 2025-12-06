import json

class C2SPackageHelper:
    @staticmethod
    def create_package(package_type, data=None):
        """
        创建服务端到客户端的数据包
        
        Args:
            package_type (str): 数据包类型
            data (dict, optional): 数据包内容
            
        Returns:
            str: 序列化后的JSON数据包
        """
        package = {
            'type': package_type,
            'data': data or {}
        }
        return json.dumps(package)
    
    # 登录相关数据包
    @staticmethod
    def login_success(username, permission_level):
        return C2SPackageHelper.create_package('login_response', {
            'status': 'success',
            'user': {
                'username': username,
                'permission_level': permission_level
            }
        })
    
    @staticmethod
    def login_failure(message='用户名或密码错误'):
        return C2SPackageHelper.create_package('login_response', {
            'status': 'failure',
            'message': message
        })
    
    # 数据搜索相关数据包
    @staticmethod
    def searching(): 
        return C2SPackageHelper.create_package('searching')
    
    @staticmethod
    def search_completed(data_list):
        return C2SPackageHelper.create_package('search_completed', {
            'data_list': data_list
        })
    
    # 数据筛选相关数据包
    @staticmethod
    def filter_received(): 
        return C2SPackageHelper.create_package('filter_received')
    
    @staticmethod
    def filter_completed(): 
        return C2SPackageHelper.create_package('filter_completed')
    
    # 数据管理相关数据包
    @staticmethod
    def reading_data(): 
        return C2SPackageHelper.create_package('data_management_response', {
            'status': 'reading'
        })
    
    @staticmethod
    def data_read_completed(data_list):
        return C2SPackageHelper.create_package('data_management_response', {
            'status': 'completed',
            'records': data_list
        })
    
    @staticmethod
    def deleting_data(): 
        return C2SPackageHelper.create_package('deleting_data')
    
    @staticmethod
    def data_deleted(): 
        return C2SPackageHelper.create_package('data_deleted')
    
    # 搜索源管理相关数据包
    @staticmethod
    def finding_search_sources(): 
        return C2SPackageHelper.create_package('finding_search_sources')
    
    @staticmethod
    def search_sources_found(source_list):
        return C2SPackageHelper.create_package('search_sources_found', {
            'source_list': source_list
        })
    
    @staticmethod
    def disabling_search_source(): 
        return C2SPackageHelper.create_package('disabling_search_source')
    
    @staticmethod
    def search_source_status_updated(source_list):
        return C2SPackageHelper.create_package('search_source_status_updated', {
            'source_list': source_list
        })
    
    # 成功相关数据包
    @staticmethod
    def success(package_type, data=None):
        return C2SPackageHelper.create_package(package_type, {
            'success': True,
            'data': data or {}
        })
    
    # 错误相关数据包
    @staticmethod
    def error(message='服务器错误'):
        return C2SPackageHelper.create_package('error', {
            'message': message
        })
    
