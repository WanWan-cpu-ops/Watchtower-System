#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试SpiderTool类的request header嗅探功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.spider_tool import SpiderTool

def test_sniff_rules():
    """测试sniff_rules方法是否能正确嗅探request header"""
    spider_tool = SpiderTool()
    
    # 测试网址
    source_url = "https://example.com"
    target_title = "Example Domain"
    
    print(f"开始测试嗅探规则，URL: {source_url}")
    
    try:
        # 调用sniff_rules方法
        rules = spider_tool.sniff_rules(source_url, target_title)
        
        if rules:
            print("\n嗅探结果成功！")
            print(f"源URL: {rules.get('source_url')}")
            print(f"域名: {rules.get('domain')}")
            print(f"标题XPath: {rules.get('title_xpath')}")
            print(f"内容XPath: {rules.get('content_xpath')}")
            print(f"图片XPath: {rules.get('image_xpath')}")
            print(f"请求头: {rules.get('request_headers')}")
            
            # 检查请求头是否存在
            if 'request_headers' in rules and rules['request_headers']:
                print("\n✓ request header 嗅探功能正常工作！")
                return True
            else:
                print("\n✗ request header 嗅探功能不正常，未获取到请求头信息")
                return False
        else:
            print("\n✗ 嗅探失败，未能获取到规则")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sniff_rules()
    sys.exit(0 if success else 1)