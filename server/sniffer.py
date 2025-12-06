#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网页内容嗅探器
用于解析和分析网页内容，获取详细的标题、内容的DOM对应的XPath，以及所需的request headers
"""

import requests
import re
import json
from bs4 import BeautifulSoup
from lxml import etree
from datetime import datetime

class WebSniffer:
    def __init__(self):
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def log(self, message, level='INFO'):
        """
        日志记录函数
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [SNIFFER] [{level}] {message}")
    
    def fetch_page(self, url, headers=None):
        """
        获取网页内容和响应头信息
        
        参数:
            url: 要获取的网页URL
            headers: 自定义请求头
            
        返回:
            tuple: (网页内容, 响应头, 最终使用的请求头)
        """
        self.log(f"开始获取网页内容: URL={url}", 'INFO')
        
        try:
            # 合并默认请求头和自定义请求头
            final_headers = self.default_headers.copy()
            if headers:
                final_headers.update(headers)
            
            response = self.session.get(url, headers=final_headers, timeout=10)
            response.raise_for_status()  # 抛出HTTP错误
            
            self.log(f"网页内容获取成功: URL={url}, 状态码={response.status_code}", 'INFO')
            
            # 返回网页内容、响应头和最终使用的请求头
            return response.text, dict(response.headers), final_headers
        
        except requests.RequestException as e:
            self.log(f"网页内容获取失败: URL={url}, 错误: {str(e)}", 'ERROR')
            return None, None, None
    
    def extract_xpath(self, html_content, element_type='title'):
        """
        从HTML内容中提取指定类型元素的XPath
        
        参数:
            html_content: HTML内容
            element_type: 元素类型 ('title' 或 'content')
            
        返回:
            str: 提取的XPath
        """
        self.log(f"开始提取XPath: 元素类型={element_type}", 'DEBUG')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tree = etree.HTML(html_content)
            
            if element_type == 'title':
                # 首先尝试获取<title>标签
                title_tag = soup.find('title')
                if title_tag:
                    self.log(f"找到<title>标签", 'DEBUG')
                    return self.get_element_xpath(tree, title_tag)
                
                # 如果没有<title>标签，尝试查找h1标签
                h1_tags = soup.find_all('h1')
                if h1_tags:
                    self.log(f"找到{len(h1_tags)}个<h1>标签，使用第一个", 'DEBUG')
                    return self.get_element_xpath(tree, h1_tags[0])
                
                # 尝试查找h2标签
                h2_tags = soup.find_all('h2')
                if h2_tags:
                    self.log(f"找到{len(h2_tags)}个<h2>标签，使用第一个", 'DEBUG')
                    return self.get_element_xpath(tree, h2_tags[0])
                
                self.log(f"未找到合适的标题元素", 'WARNING')
                return None
            
            elif element_type == 'content':
                # 查找可能包含正文内容的元素
                content_candidates = []
                
                # 尝试查找常见的内容容器标签
                common_content_tags = ['div', 'article', 'main', 'section']
                for tag_name in common_content_tags:
                    elements = soup.find_all(tag_name)
                    for element in elements:
                        # 计算元素的文本长度，选择最长的作为正文
                        text_length = len(element.get_text(separator='', strip=True))
                        if text_length > 100:  # 过滤掉过短的内容
                            content_candidates.append((text_length, element))
                
                # 按文本长度降序排序，选择最长的
                content_candidates.sort(reverse=True, key=lambda x: x[0])
                
                if content_candidates:
                    longest_content = content_candidates[0][1]
                    self.log(f"找到最长正文内容，长度={content_candidates[0][0]}字符", 'DEBUG')
                    return self.get_element_xpath(tree, longest_content)
                
                self.log(f"未找到合适的正文内容元素", 'WARNING')
                return None
            
            elif element_type == 'image':
                # 查找所有图片标签
                img_tags = soup.find_all('img')
                if img_tags:
                    # 尝试选择第一个有src属性且alt属性不为空的图片
                    for img_tag in img_tags:
                        if img_tag.get('src') and img_tag.get('alt'):
                            self.log(f"找到图片标签，src={img_tag.get('src')}", 'DEBUG')
                            return self.get_element_xpath(tree, img_tag)
                    
                    # 如果没有找到有alt属性的图片，选择第一个有src属性的图片
                    self.log(f"找到{len(img_tags)}个图片标签，使用第一个", 'DEBUG')
                    return self.get_element_xpath(tree, img_tags[0])
                
                self.log(f"未找到图片元素", 'WARNING')
                return None
            
        except Exception as e:
            self.log(f"提取XPath失败: 元素类型={element_type}, 错误: {str(e)}", 'ERROR')
            return None
    
    def get_element_xpath(self, tree, element):
        """
        获取元素的XPath
        
        参数:
            tree: lxml树对象
            element: BeautifulSoup元素对象
            
        返回:
            str: 元素的XPath
        """
        try:
            # 获取元素的标签名和属性
            tag_name = element.name
            attributes = element.attrs
            
            # 使用lxml查找该元素的XPath
            if attributes:
                # 如果有id属性，使用id定位
                if 'id' in attributes:
                    xpath = f"//{tag_name}[@id='{attributes['id']}']"
                    return xpath
                
                # 如果有class属性，使用class定位
                if 'class' in attributes:
                    class_name = ' '.join(attributes['class'])
                    xpath = f"//{tag_name}[@class='{class_name}']"
                    return xpath
            
            # 如果没有属性，使用标签名和位置定位
            elements = tree.xpath(f"//{tag_name}")
            index = None
            
            for i, el in enumerate(elements):
                # 比较文本内容
                if el.text == element.text:
                    index = i
                    break
            
            if index is not None:
                xpath = f"//{tag_name}[{index + 1}]"
                return xpath
            
            # 如果还是找不到，返回简单的XPath
            self.log(f"无法精确定位元素，返回简单XPath", 'WARNING')
            return f"//{tag_name}"
            
        except Exception as e:
            self.log(f"获取元素XPath失败: 错误: {str(e)}", 'ERROR')
            return f"//{element.name}"
    
    def analyze_page(self, url, headers=None):
        """
        分析网页，提取标题、内容的XPath和请求头信息
        
        参数:
            url: 要分析的网页URL
            headers: 自定义请求头
            
        返回:
            dict: 包含分析结果的字典
        """
        self.log(f"开始分析网页: URL={url}", 'INFO')
        
        try:
            # 获取网页内容
            html_content, response_headers, final_headers = self.fetch_page(url, headers)
            if not html_content:
                return None
            
            # 提取标题XPath
            title_xpath = self.extract_xpath(html_content, 'title')
            
            # 提取正文内容XPath
            content_xpath = self.extract_xpath(html_content, 'content')
            
            # 提取图片XPath
            image_xpath = self.extract_xpath(html_content, 'image')
            
            # 转换请求头为JSON字符串
            headers_json = json.dumps(final_headers, ensure_ascii=False, indent=2)
            
            # 构造分析结果
            result = {
                'url': url,
                'title_xpath': title_xpath,
                'content_xpath': content_xpath,
                'image_xpath': image_xpath,
                'request_headers': headers_json,
                'response_headers': json.dumps(response_headers, ensure_ascii=False, indent=2) if response_headers else None,
            }
            
            self.log(f"网页分析完成: URL={url}", 'INFO')
            return result
            
        except Exception as e:
            self.log(f"网页分析失败: URL={url}, 错误: {str(e)}", 'ERROR')
            return None
    
    def sniff(self, url, source_id, source_name, headers=None):
        """
        执行完整的嗅探流程
        
        参数:
            url: 要嗅探的网页URL
            source_id: 源ID
            source_name: 源名称
            headers: 自定义请求头
            
        返回:
            dict: 包含嗅探结果的字典
        """
        self.log(f"开始完整嗅探流程: URL={url}, 源ID={source_id}, 源名称={source_name}", 'INFO')
        
        try:
            # 分析网页
            analysis_result = self.analyze_page(url, headers)
            if not analysis_result:
                return None
            
            # 添加源信息
            analysis_result['source_id'] = source_id
            analysis_result['source_name'] = source_name
            
            self.log(f"嗅探流程完成: URL={url}", 'INFO')
            return analysis_result
            
        except Exception as e:
            self.log(f"嗅探流程失败: URL={url}, 错误: {str(e)}", 'ERROR')
            return None

# 测试代码
if __name__ == "__main__":
    sniffer = WebSniffer()
    
    # 测试嗅探功能
    test_url = "https://www.example.com"
    result = sniffer.sniff(test_url, "example", "示例网站")
    
    if result:
        print("\n嗅探结果:")
        print(f"URL: {result['url']}")
        print(f"标题XPath: {result['title_xpath']}")
        print(f"内容XPath: {result['content_xpath']}")
        print(f"图片XPath: {result['image_xpath']}")
        print(f"请求头: {result['request_headers']}")
    else:
        print("\n嗅探失败")