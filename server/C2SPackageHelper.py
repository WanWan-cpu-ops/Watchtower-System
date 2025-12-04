import json

class C2SPackageHelper:
    """客户端到服务器和服务器到客户端的数据包封装助手"""
    
    # 消息类型定义
    MSG_TYPE_LOGIN = "login"
    MSG_TYPE_REGISTER = "register"
    MSG_TYPE_SEARCH = "search"
    MSG_TYPE_FILTER = "filter"
    MSG_TYPE_REFRESH_DATA = "refresh_data"
    MSG_TYPE_DELETE_DATA = "delete_data"
    MSG_TYPE_REFRESH_SOURCES = "refresh_sources"
    MSG_TYPE_TOGGLE_SOURCE = "toggle_source"
    MSG_TYPE_REFRESH_PROFILE = "refresh_profile"
    MSG_TYPE_SEND_VERIFICATION_CODE = "send_verification_code"
    MSG_TYPE_SUBMIT_VERIFICATION = "submit_verification"
    
    # 状态类型定义
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_PROCESSING = "processing"
    STATUS_RECEIVED = "received"
    STATUS_COMPLETED = "completed"
    
    @staticmethod
    def create_package(msg_type, status, data=None):
        """创建数据包
        
        Args:
            msg_type: 消息类型
            status: 状态
            data: 附加数据
            
        Returns:
            str: JSON格式化的数据包
        """
        package = {
            "msg_type": msg_type,
            "status": status
        }
        
        if data is not None:
            package["data"] = data
        
        return json.dumps(package)
    
    @staticmethod
    def parse_package(package_str):
        """解析数据包
        
        Args:
            package_str: JSON格式化的数据包字符串
            
        Returns:
            dict: 解析后的数据包
        """
        return json.loads(package_str)
    
    @staticmethod
    def create_login_response(status, user_info=None):
        """创建登录响应包
        
        Args:
            status: 登录状态
            user_info: 用户信息（成功时返回）
            
        Returns:
            str: JSON格式化的登录响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_LOGIN,
            status,
            user_info
        )
    
    @staticmethod
    def create_register_response(status, data=None):
        """创建注册响应包
        
        Args:
            status: 注册状态
            data: 附加数据（如错误信息或用户信息）
            
        Returns:
            str: JSON格式化的注册响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_REGISTER,
            status,
            data
        )
    
    @staticmethod
    def create_search_response(status, search_results=None):
        """创建搜索响应包
        
        Args:
            status: 搜索状态
            search_results: 搜索结果（成功时返回）
            
        Returns:
            str: JSON格式化的搜索响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_SEARCH,
            status,
            search_results
        )
    
    @staticmethod
    def create_filter_response(status):
        """创建筛选响应包
        
        Args:
            status: 筛选状态
            
        Returns:
            str: JSON格式化的筛选响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_FILTER,
            status
        )
    
    @staticmethod
    def create_data_response(status, data_records=None):
        """创建数据响应包
        
        Args:
            status: 数据操作状态
            data_records: 数据记录（成功时返回）
            
        Returns:
            str: JSON格式化的数据响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_REFRESH_DATA,
            status,
            data_records
        )
    
    @staticmethod
    def create_source_response(status, sources=None):
        """创建搜索源响应包
        
        Args:
            status: 搜索源操作状态
            sources: 搜索源列表（成功时返回）
            
        Returns:
            str: JSON格式化的搜索源响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_REFRESH_SOURCES,
            status,
            sources
        )
    
    @staticmethod
    def create_profile_response(status, profile=None):
        """创建个人资料响应包
        
        Args:
            status: 操作状态
            profile: 用户个人资料（成功时返回）
            
        Returns:
            str: JSON格式化的个人资料响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_REFRESH_PROFILE,
            status,
            profile
        )
    
    @staticmethod
    def create_sms_response(status, data=None):
        """创建验证码发送响应包
        
        Args:
            status: 操作状态
            data: 附加数据（如错误信息）
            
        Returns:
            str: JSON格式化的验证码发送响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_SEND_VERIFICATION_CODE,
            status,
            data
        )
    
    @staticmethod
    def create_verification_response(status, data=None):
        """创建实名认证提交响应包
        
        Args:
            status: 操作状态
            data: 附加数据（如错误信息）
            
        Returns:
            str: JSON格式化的实名认证提交响应包
        """
        return C2SPackageHelper.create_package(
            C2SPackageHelper.MSG_TYPE_SUBMIT_VERIFICATION,
            status,
            data
        )