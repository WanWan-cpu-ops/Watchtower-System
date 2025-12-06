#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试本地HTML文件的标题和内容提取逻辑
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from spider_tool import SpiderTool

def test_local_html_sniff():
    """
    测试本地HTML文件的标题和内容提取逻辑
    """
    print("开始测试本地HTML文件的标题和内容提取逻辑...")
    
    # 读取本地HTML文件
    html_file_path = "test_local_html.html"
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 读取本地HTML文件失败: {str(e)}")
        return
    
    print(f"✅ 成功读取本地HTML文件: {html_file_path}")
    
    spider_tool = SpiderTool()
    target_title = "Python教程：从入门到精通"
    
    print(f"\n=== 测试标题提取 (目标标题: '{target_title}') ===")
    try:
        # 提取标题XPath
        title_xpath = spider_tool.extract_title_xpath(html_content, target_title)
        print(f"标题XPath: {'✅' if title_xpath else '❌'} {title_xpath}")
        
        if title_xpath:
            # 验证标题提取
            import lxml.etree as ET
            tree = ET.HTML(html_content)
            title_elements = tree.xpath(title_xpath)
            if title_elements:
                # 使用lxml的text_content方法
                extracted_title = title_elements[0].xpath('string()').strip()
                print(f"提取的标题: {extracted_title}")
                if target_title in extracted_title:
                    print("标题验证: ✅ 匹配成功")
                else:
                    print("标题验证: ❌ 匹配失败")
    except Exception as e:
        print(f"❌ 标题提取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== 测试内容提取 ===")
    try:
        # 提取内容XPath
        content_xpath = spider_tool.extract_content_xpath(html_content, title_xpath)
        print(f"内容XPath: {'✅' if content_xpath else '❌'} {content_xpath}")
        
        if content_xpath:
            # 验证内容提取
            import lxml.etree as ET
            tree = ET.HTML(html_content)
            content_elements = tree.xpath(content_xpath)
            if content_elements:
                # 使用lxml的text_content方法
                extracted_content = content_elements[0].xpath('string()').strip()
                print(f"提取的内容长度: {len(extracted_content)} 字符")
                print(f"内容预览: {extracted_content[:200]}...")
                
                # 内容质量评估
                if len(extracted_content) > 1000:
                    print("内容质量: ✅ 内容丰富")
                elif len(extracted_content) > 500:
                    print("内容质量: ⚠️ 内容适中")
                else:
                    print("内容质量: ❌ 内容较少")
                
                # 检查是否包含关键内容
                key_sections = ["Python简介", "Python的历史", "Python的特点"]
                found_sections = 0
                for section in key_sections:
                    if section in extracted_content:
                        found_sections += 1
                
                print(f"关键章节识别率: {found_sections}/{len(key_sections)}")
                if found_sections >= len(key_sections) * 0.7:
                    print("章节完整性: ✅ 良好")
                else:
                    print("章节完整性: ⚠️ 可能缺失重要内容")
    except Exception as e:
        print(f"❌ 内容提取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== 测试综合功能 ===")
    try:
        # 使用sniff_rules方法测试完整流程
        result = spider_tool.sniff_rules("http://example.com/test", target_title)
        print(f"sniff_rules方法结果: {'✅' if result else '❌'}")
        if result:
            print(f"源URL: {result['source_url']}")
            print(f"域名: {result['domain']}")
            print(f"标题XPath: {result['title_xpath']}")
            print(f"内容XPath: {result['content_xpath']}")
            print(f"图片XPath: {result['image_xpath']}")
            if 'request_headers' in result:
                print(f"请求头: 包含 {len(result['request_headers'])} 个字段")
                for key, value in list(result['request_headers'].items())[:5]:  # 只显示前5个
                    print(f"  {key}: {value[:50]}...")
    except Exception as e:
        print(f"❌ 综合功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_local_html_sniff()
