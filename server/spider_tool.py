import requests
from bs4 import BeautifulSoup
import lxml.etree as ET
import re
from urllib.parse import urlparse

class SpiderTool:
    """
    爬虫工具类，用于网页内容爬取和XPath提取
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_domain(self, url):
        """
        从URL中提取域名
        """
        parsed_url = urlparse(url)
        return parsed_url.netloc
    
    def fetch_page(self, url):
        """
        获取网页内容和响应信息
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return {
                'content': response.text,
                'headers': dict(response.headers)
            }
        except Exception as e:
            print(f"爬取网页失败: {url} - 错误: {str(e)}")
            return None
    
    def extract_title_xpath(self, html_content, target_title):
        """
        提取标题的XPath
        使用改进的标题分析逻辑，基于标签优先级、位置和内容特征
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tree = ET.HTML(html_content)
            
            # 1. 基于target_title的精确匹配
            title_elements = []
            for element in soup.find_all(text=re.compile(re.escape(target_title))):
                if target_title in element:
                    title_elements.append(element.parent)
            
            if not title_elements:
                # 2. 尝试部分匹配（如果精确匹配失败）
                for element in soup.find_all(text=True):
                    if target_title[:20] in element and len(element.strip()) < 200:
                        title_elements.append(element.parent)
            
            if not title_elements:
                return None
            
            # 标签优先级顺序
            title_tag_priority = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'div', 'span', 'p']
            
            # 3. 按照标签优先级排序元素
            prioritized_elements = []
            for tag in title_tag_priority:
                for element in title_elements:
                    if element.name == tag:
                        # 计算元素在页面中的位置（越靠前越优先）
                        position = len(str(element.previous))
                        prioritized_elements.append((element, position))
            
            if prioritized_elements:
                # 选择同标签中位置最靠前的
                prioritized_elements.sort(key=lambda x: x[1])
                best_element = prioritized_elements[0][0]
            else:
                # 如果没有优先级标签，选择文本长度最接近标题的
                title_len = len(target_title)
                best_element = min(title_elements, 
                                  key=lambda x: abs(len(x.get_text().strip()) - title_len))
            
            # 转换为lxml元素
            element_text = best_element.get_text().strip()
            if len(element_text) > 0:
                # 使用contains进行匹配，避免特殊字符问题
                lxml_elements = tree.xpath(f"//{best_element.name}[contains(text(), '{element_text[:30]}')]")
                if lxml_elements:
                    return self.get_element_xpath(lxml_elements[0])
            
            return None
            
        except Exception as e:
            print(f"提取标题XPath失败 - 错误: {str(e)}")
            return None
    
    def get_element_xpath(self, element):
        """
        获取元素的XPath
        """
        path = []
        current = element
        
        while current is not None:
            if current.tag == 'html':
                path.append('html')
                break
            
            siblings = current.getparent().findall(current.tag)
            if len(siblings) == 1:
                path.append(current.tag)
            else:
                index = siblings.index(current) + 1
                path.append(f"{current.tag}[{index}]")
            
            current = current.getparent()
        
        return '/' + '/'.join(reversed(path))
    
    def sniff_rules(self, url, target_title):
        """
        嗅探网页规则
        """
        page_data = self.fetch_page(url)
        if not page_data:
            return None
        
        html_content = page_data['content']
        response_headers = page_data['headers']
        
        domain = self.get_domain(url)
        title_xpath = self.extract_title_xpath(html_content, target_title)
        
        # 这里可以添加更多XPath提取逻辑，如内容、图片等
        content_xpath = self.extract_content_xpath(html_content, title_xpath)
        image_xpath = self.extract_image_xpath(html_content)
        
        # 准备要返回的数据
        result = {
            'source_url': url,
            'domain': domain,
            'title_xpath': title_xpath,
            'content_xpath': content_xpath,
            'image_xpath': image_xpath
        }
        
        # 添加request headers信息
        if response_headers:
            result['request_headers'] = self.headers
        
        return result
    
    def extract_content_xpath(self, html_content, title_xpath=None):
        """
        提取内容的XPath
        使用改进的内容分析逻辑，基于文本密度、标签结构和页面布局
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tree = ET.HTML(html_content)
            
            # 1. 排除非内容区域的标签和类名
            exclude_tags = ['header', 'nav', 'aside', 'footer', 'script', 'style', 'iframe']
            exclude_classes = ['header', 'nav', 'aside', 'footer', 'sidebar', 'advertisement', 'ad', 'comment', 'related', 'share', 'social']
            
            # 移除排除的标签
            for tag in exclude_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # 移除带有排除类的元素
            for element in soup.find_all(class_=lambda x: x and any(cls in x.lower() for cls in exclude_classes)):
                element.decompose()
            
            # 2. 识别潜在的内容容器
            content_candidates = []
            content_tags = ['article', 'main', 'section', 'div', 'p']
            
            for tag in content_tags:
                for element in soup.find_all(tag):
                    # 获取元素文本
                    text = element.get_text().strip()
                    text_length = len(text)
                    
                    if text_length < 300:  # 内容太短，可能不是主要内容
                        continue
                    
                    # 计算文本密度（文本长度 / 总HTML长度）
                    html_length = len(str(element))
                    text_density = text_length / html_length if html_length > 0 else 0
                    
                    # 计算段落数量
                    p_count = len(element.find_all('p'))
                    
                    # 计算链接密度（链接文本长度 / 总文本长度）
                    link_text = ''.join([a.get_text() for a in element.find_all('a')])
                    link_density = len(link_text) / text_length if text_length > 0 else 0
                    
                    # 内容评分：综合考虑文本长度、文本密度、段落数量和链接密度
                    # 链接密度越低越好（避免导航菜单）
                    score = (text_length * 0.4) + (text_density * 1000 * 0.3) + (p_count * 10 * 0.2) - (link_density * 1000 * 0.1)
                    
                    content_candidates.append((element, score, text_length, p_count, text_density, link_density))
            
            if not content_candidates:
                return None
            
            # 3. 排序候选内容，选择分数最高的
            content_candidates.sort(key=lambda x: x[1], reverse=True)
            best_candidate = content_candidates[0][0]
            
            # 4. 如果找到标题XPath，尝试找到标题附近的内容
            if title_xpath and len(content_candidates) > 1:
                # 将XPath转换为BeautifulSoup元素
                title_tag = None
                try:
                    title_elements = tree.xpath(title_xpath)
                    if title_elements:
                        # 尝试找到对应的BeautifulSoup元素
                        title_text = title_elements[0].xpath('string()').strip()
                        title_tag = soup.find(text=title_text)
                        if title_tag:
                            title_tag = title_tag.parent
                except:
                    pass
                
                if title_tag:
                    try:
                        # 查找标题后面的内容容器
                        all_descendants = list(soup.descendants)
                        if title_tag in all_descendants:
                            title_index = all_descendants.index(title_tag)
                            
                            # 查找标题附近的候选内容
                            nearby_candidates = []
                            for candidate, score, text_len, p_count, text_density, link_density in content_candidates:
                                if candidate in all_descendants:
                                    candidate_index = all_descendants.index(candidate)
                                    # 只考虑标题后面且距离不太远的内容
                                    if candidate_index > title_index:
                                        distance = candidate_index - title_index
                                        if distance < 100:
                                            nearby_candidates.append((candidate, score, text_len, p_count, distance))
                            
                            if nearby_candidates:
                                # 选择附近分数最高的，但只有当它的分数与最高分相差不超过20%时才使用
                                highest_score = content_candidates[0][1]
                                nearby_candidates.sort(key=lambda x: x[1], reverse=True)
                                
                                # 只有当附近元素的分数接近最高分（不低于80%）时才替换
                                if nearby_candidates[0][1] >= highest_score * 0.8:
                                    best_candidate = nearby_candidates[0][0]
                    except:
                        pass
            
            # 转换为lxml元素
            element_text = best_candidate.get_text().strip()
            
            if len(element_text) > 0:
                # 使用标签和部分文本内容进行匹配
                tag = best_candidate.name
                
                # 清理样本文本，移除换行符和特殊字符，只保留普通文本
                sample_text = element_text[:50]
                sample_text = sample_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                # 移除多余的空格
                sample_text = ' '.join(sample_text.split())
                
                # 使用更可靠的XPath匹配方法
                # 1. 首先尝试使用完整的文本内容匹配
                try:
                    # 使用normalize-space来处理空白字符
                    xpath_query = f"//{tag}[normalize-space() = normalize-space('{sample_text}')]"
                    lxml_elements = tree.xpath(xpath_query)
                    
                    if lxml_elements:
                        # 如果有多个匹配，选择文本长度最接近的
                        best_lxml_element = min(lxml_elements,
                                               key=lambda x: abs(len(x.xpath('string()').strip()) - len(element_text)))
                        return self.get_element_xpath(best_lxml_element)
                except:
                    pass
                
                # 2. 如果完整匹配失败，尝试使用contains匹配
                try:
                    xpath_query = f"//{tag}[contains(normalize-space(), normalize-space('{sample_text}'))]"
                    lxml_elements = tree.xpath(xpath_query)
                    
                    if lxml_elements:
                        # 如果有多个匹配，选择文本长度最接近的
                        best_lxml_element = min(lxml_elements,
                                               key=lambda x: abs(len(x.xpath('string()').strip()) - len(element_text)))
                        return self.get_element_xpath(best_lxml_element)
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"提取内容XPath失败 - 错误: {str(e)}")
            return None
    
    def extract_image_xpath(self, html_content):
        """
        提取图片的XPath模式
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 找到所有图片元素
            images = soup.find_all('img')
            if not images:
                return None
            
            # 分析图片的父容器模式
            parent_patterns = {}
            for img in images:
                if img.parent:
                    parent_tag = img.parent.name
                    parent_patterns[parent_tag] = parent_patterns.get(parent_tag, 0) + 1
            
            # 找到最常见的父容器
            if parent_patterns:
                most_common_parent = max(parent_patterns.items(), key=lambda x: x[1])[0]
                return f"//{most_common_parent}/img"
            
            return "//img"
        except Exception as e:
            print(f"提取图片XPath失败 - 错误: {str(e)}")
            return None