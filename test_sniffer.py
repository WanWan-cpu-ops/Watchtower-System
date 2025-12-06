#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能瞭望系统 - 嗅探器测试脚本
用于测试网页嗅探功能和爬虫规则保存功能
"""

import sys
import os
import json

# 检查是否在虚拟环境中运行
if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
    print("错误: 该应用程序必须在虚拟环境中运行!")
    print("请先激活虚拟环境，然后再运行此脚本:")
    print("Windows: venv\\Scripts\\activate.bat")
    print("Linux/Mac: source venv/bin/activate")
    sys.exit(1)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入所需模块
from server.sniffer import WebSniffer

def test_sniffer():
    """测试嗅探功能和规则保存"""
    print("=== 测试嗅探功能和规则保存 ===")
    
    # 创建嗅探器实例
    sniffer = WebSniffer()
    
    # 测试URL（使用一个简单的测试网站）
    test_url = "https://www.example.com"
    source_id = "test_source"
    source_name = "测试网站"
    
    print(f"\n1. 开始嗅探URL: {test_url}")
    print(f"源ID: {source_id}")
    print(f"源名称: {source_name}")
    
    # 执行嗅探
    result = sniffer.sniff(test_url, source_id, source_name)
    
    if result:
        print("\n2. 嗅探成功！")
        print(f"URL: {result['url']}")
        print(f"标题XPath: {result['title_xpath']}")
        print(f"内容XPath: {result['content_xpath']}")
        print(f"图片XPath: {result['image_xpath']}")
        print(f"请求头: {result['request_headers']}")
        
        if 'rule_id' in result:
            print(f"\n3. 规则已保存到数据库！")
            print(f"规则ID: {result['rule_id']}")
        else:
            print("\n3. 规则保存失败！")
        
        # 测试获取规则
        print("\n4. 测试获取规则...")
        rules_result = sniffer.get_crawler_rules()
        if rules_result['success']:
            print(f"成功获取到 {len(rules_result['rules'])} 条规则")
            for rule in rules_result['rules']:
                print(f"- 规则ID: {rule['id']}, 源名称: {rule['source_name']}, 启用状态: {rule['enabled']}")
        else:
            print(f"获取规则失败: {rules_result['error']}")
            
    else:
        print("\n2. 嗅探失败！")

if __name__ == "__main__":
    test_sniffer()