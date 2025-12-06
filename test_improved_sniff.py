#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试改进后的标题和内容提取逻辑
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from spider_tool import SpiderTool

def test_improved_sniff_rules():
    """
    测试改进后的标题和内容提取逻辑
    """
    print("开始测试改进后的标题和内容提取逻辑...")
    
    # 测试网站列表
    test_sites = [
        {
            "url": "https://www.runoob.com/python3/python3-tutorial.html",
            "expected_title_keyword": "Python 3 教程"
        },
        {
            "url": "https://zh.wikipedia.org/wiki/Python",
            "expected_title_keyword": "Python"
        },
        {
            "url": "https://www.baidu.com/s?wd=Python教程",
            "expected_title_keyword": "Python教程"
        }
    ]
    
    spider_tool = SpiderTool()
    
    for site in test_sites:
        print(f"\n=== 测试网站: {site['url']} ===")
        try:
            # 获取页面内容
            page_data = spider_tool.fetch_page(site['url'])
            
            if not page_data:
                print("  ❌ 获取页面内容失败")
                continue
            
            html_content = page_data['content']
            headers = page_data['headers']
            
            # 提取标题XPath
            title_xpath = spider_tool.extract_title_xpath(html_content, site['expected_title_keyword'])
            print(f"  标题XPath: {'✅' if title_xpath else '❌'} {title_xpath}")
            
            # 提取内容XPath
            content_xpath = spider_tool.extract_content_xpath(html_content, title_xpath)
            print(f"  内容XPath: {'✅' if content_xpath else '❌'} {content_xpath}")
            
            # 如果都成功，验证提取的内容
            if title_xpath and content_xpath:
                tree = spider_tool.get_html_tree(html_content)
                
                # 验证标题提取
                title_elements = tree.xpath(title_xpath)
                if title_elements:
                    extracted_title = title_elements[0].text_content().strip()
                    print(f"  提取的标题: {extracted_title[:50]}...")
                    if site['expected_title_keyword'] in extracted_title:
                        print("  标题验证: ✅ 匹配成功")
                    else:
                        print("  标题验证: ❌ 匹配失败")
                
                # 验证内容提取
                content_elements = tree.xpath(content_xpath)
                if content_elements:
                    extracted_content = content_elements[0].text_content().strip()
                    print(f"  提取的内容长度: {len(extracted_content)} 字符")
                    print(f"  内容预览: {extracted_content[:100]}...")
                    
                    # 内容质量评估
                    if len(extracted_content) > 1000:
                        print("  内容质量: ✅ 内容丰富")
                    elif len(extracted_content) > 500:
                        print("  内容质量: ⚠️ 内容适中")
                    else:
                        print("  内容质量: ❌ 内容较少")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_improved_sniff_rules()
