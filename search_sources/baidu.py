from weakref import ref
import requests
from urllib.parse import quote, unquote
import logging
import time
import json
from bs4 import BeautifulSoup

# 配置日志 - 添加文件输出
logging.basicConfig(
    level=logging.INFO,  # 设置为INFO级别，但在代码中关键位置使用INFO日志
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("baidu_spider.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BaiduSpider:
    def __init__(self):
        # 初始化基本配置
        self.base_url = 'https://www.baidu.com/s'
        # 使用用户提供的请求头 - 移除accept-encoding避免编码问题
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
            'cache-control': 'max-age=0',
            'connection': 'keep-alive',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
        }
        # 创建会话对象
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search(self, keyword, page=1):
        """
        执行百度搜索，支持动态参数
        
        Args:
            keyword (str): 搜索关键词（动态参数）
            page (int): 页码
            
        Returns:
            dict: 包含响应状态、URL和响应内容的字典
        """
        # 参数验证
        if not keyword or not isinstance(keyword, str):
            logging.error('搜索关键词必须是非空字符串')
            return {'status': 'error', 'message': '搜索关键词必须是非空字符串'}
            
        if page < 1 or not isinstance(page, int):
            logging.error('页码必须是大于等于1的整数')
            return {'status': 'error', 'message': '页码必须是大于等于1的整数'}
            
        # 对关键词进行URL编码（动态参数处理）
        encoded_keyword = quote(keyword)
        logging.info(f'原始关键词: {keyword}, 编码后: {encoded_keyword}')
        
        # 计算起始位置
        start = (page - 1) * 10
        
        # 直接将原始关键词接在URL参数位置
        full_url = f"{self.base_url}?wd={encoded_keyword}&pn={start}"
        logging.info(f'准备访问URL: {full_url}')
        
        try:
            # 发送请求，直接使用构造好的URL
            response = self.session.get(
                url=full_url,
                timeout=15
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 智能处理编码问题
            # 让requests自动检测编码
            response.encoding = response.apparent_encoding
            # 如果检测失败，尝试使用UTF-8
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            logging.info(f'请求成功，状态码: {response.status_code}')
            logging.info(f'实际访问的URL: {response.url}')
            
            # 构建参数信息用于返回
            params_info = {
                'wd': encoded_keyword,  # wd是百度搜索的关键词参数
                'pn': start            # pn是页码偏移量
            }
            
            return {
                'status': 'success',
                'status_code': response.status_code,
                'url': response.url,
                'content': response.text,
                'params': params_info
            }
            
        except Exception as e:
            logging.error(f'请求失败: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
                'url': full_url
            }
    
    def extract_search_results(self, html_content):
        """
        使用BeautifulSoup从HTML中提取搜索结果信息
        
        Args:
            html_content (str): HTML响应内容
            
        Returns:
            list: 包含提取信息的字典列表，每个字典包含标题、概要、URL和封面URL
        """
        try:
            # 解析HTML内容
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # 查找搜索结果项（百度搜索结果的主要容器类名可能会变化）
            # 尝试多种可能的选择器
            search_items = soup.select('.result.c-container')
            if not search_items:
                search_items = soup.select('.result-op')
            if not search_items:
                search_items = soup.select('[class*="result"]')
            
            logging.info(f'找到 {len(search_items)} 个搜索结果项')
            
            for item in search_items:
                try:
                    # 提取标题和URL
                    title_elem = item.select_one('h3 a') or item.select_one('a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True) or ''
                    url = title_elem.get('href') or ''
                    
                    # 提取概要内容
                    summary = ''
                    # 尝试多种可能的概要元素
                    summary_elem = None
                    
                    # 尝试多种可能的概要选择器
                    possible_selectors = [
                        '.c-abstract',  # 主要的概要类
                        '.c-abstract-size',  # 可能的变体
                        '.content-right',  # 内容右侧区域
                        '.c-span-text',  # 可能包含文本的span
                        'p',  # 直接查找段落标签
                        'div[data-content]',  # 带数据内容属性的div
                        '.result-op div',  # 操作结果内的div
                        '.result-molecule div',  # 分子结果内的div
                        'div[class*="content"]',  # 包含content的类
                        'div[class*="text"]'  # 包含text的类
                    ]
                    
                    # 尝试每个选择器，直到找到内容
                    for selector in possible_selectors:
                        candidates = item.select(selector)
                        for candidate in candidates:
                            text = candidate.get_text(strip=True)
                            # 确保内容不为空且长度合理（大于10个字符）
                            if text and len(text) > 10:
                                summary_elem = candidate
                                summary = text
                                break
                        if summary_elem:
                            break
                    
                    logging.info(f'提取概要: {summary[:50]}...' if summary else '未提取到概要')
                    
                    # 提取封面URL（如果有图片）
                    cover_url = ''
                    img_elem = item.select_one('img')
                    if img_elem:
                        img_src = img_elem.get('src') or img_elem.get('data-src') or ''
                        # 确保URL是完整的
                        if img_src and not img_src.startswith(('http://', 'https://')):
                            if img_src.startswith('//'):
                                cover_url = f'https:{img_src}'
                            else:
                                cover_url = f'https://www.baidu.com{img_src}'
                        else:
                            cover_url = img_src
                    
                    # 只添加有效结果
                    if title and url:
                        results.append({
                            'title': title,
                            'summary': summary,
                            'url': url,
                            'cover_url': cover_url
                        })
                        logging.debug(f'提取到结果: 标题={title[:30]}...')
                    
                except Exception as e:
                    logging.error(f'处理单个搜索结果时出错: {str(e)}')
                    continue
            
            # 去重处理，避免重复结果
            unique_results = []
            seen_urls = set()
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            
            logging.info(f'成功提取并去重 {len(unique_results)} 条搜索结果')
            return unique_results
            
        except Exception as e:
            logging.error(f'解析HTML并提取搜索结果时出错: {str(e)}')
            return []
    
    def save_extracted_results(self, extracted_results, keyword):
        """
        将提取的搜索结果保存为JSON文件
        
        Args:
            extracted_results (list): 提取的搜索结果列表
            keyword (str): 搜索关键词
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 构建保存数据的结构
            save_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'keyword': keyword,
                'total_results': len(extracted_results),
                'results': extracted_results
            }
            
            # 保存到JSON文件
            filename = rf'proceeded_pages\search_scan_{keyword}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f'提取的搜索结果已保存到 {filename}')
            print(f"\n提取的搜索结果已保存到: {filename}")
            print(f"共提取到 {len(extracted_results)} 条有效搜索结果")
            
            return True
        except Exception as e:
            logging.error(f'保存提取的搜索结果失败: {str(e)}')
            print(f"\n❌ 保存提取的搜索结果失败: {str(e)}")
            return False
    
    def save_response_info(self, result, keyword, page):
        """
        保存响应信息到文件
        
        Args:
            result (dict): 搜索结果字典
            keyword (str): 搜索关键词
            page (int): 页码
        """
        try:
            # 保存详细响应信息到JSON文件
            info_filename = rf'search_cache\search_info_{keyword}_{page}.json'
            info_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'keyword': keyword,
                'page': page,
                'status': result.get('status'),
                'status_code': result.get('status_code'),
                'url': result.get('url'),
                'params': result.get('params'),
                'message': result.get('message')
            }
            
            with open(info_filename, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f'响应信息已保存到 {info_filename}')
            
            # 如果成功，保存完整的HTML内容
            if result.get('status') == 'success':
                html_filename = rf'html_cache\baidu_search_response_{keyword}_{page}.html'
                # 保存完整的HTML内容
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                logging.info(f'完整HTML响应已保存到 {html_filename}')
                
            return True
        except Exception as e:
            logging.error(f'保存响应信息失败: {str(e)}')
            return False

def run_spider(keyword, page=1):
    """
    运行爬虫的主函数 - 专注于动态参数处理和数据提取
    
    Args:
        keyword (str): 搜索关键词（动态参数）
        page (int): 页码（默认1，不再由用户输入）
        
    Returns:
        dict: 搜索结果信息
    """
    spider = BaiduSpider()
    
    print(f"\n[动态参数爬虫] 开始执行")
    print(f"关键词: '{keyword}'")
    print("-" * 50)
    
    try:
        # 执行搜索 - 核心动态参数功能
        result = spider.search(keyword, page)
        
        # 保存响应信息
        spider.save_response_info(result, keyword, page)
        
        # 输出执行结果
        if result['status'] == 'success':
            print(f"\n✅ 请求成功!")
            print(f"状态码: {result['status_code']}")
            print(f"访问URL: {result['url']}")
            print(f"\n动态参数处理:")
            print(f"原始关键词: {keyword}")
            print(f"编码后关键词: {result['params']['wd']}")
            print(f"页码偏移量: {result['params']['pn']}")
            
            # 显示响应大小信息
            content_size = len(result['content'])
            print(f"\n响应内容大小: {content_size} 字符")
            print(f"响应信息已保存到: search_info_{keyword}_{page}.json")
            print(f"完整HTML内容已保存到: search_response_{keyword}_{page}.html")
            
            # 提取搜索结果信息
            print(f"\n🔍 正在提取搜索结果信息...")
            extracted_results = spider.extract_search_results(result['content'])
            
            # 保存提取的搜索结果
            if extracted_results:
                spider.save_extracted_results(extracted_results, keyword)
                return {"status":"success","result":result,"data":extracted_results}
            else:
                print("\n⚠️  未提取到任何有效搜索结果")
                return {"status":"failed","result":result,"data":[]}
                
        else:
            print(f"\n❌ 请求失败!")
            print(f"错误信息: {result['message']}")
            print(f"尝试访问的URL: {result['url']}")
            return {"status":"failed","result":result,"data":[]}
        
    except Exception as e:
        error_msg = f"爬虫执行过程中发生错误: {str(e)}"
        print(f"\n❌ {error_msg}")
        logging.error(error_msg)
        return {'status': 'error', 'message': str(e)}

def main(keyword, max_pages=1):
    try:  
        # 验证关键词
        if not keyword.strip():
            print("错误: 关键词不能为空")
            return (False, [])
        
        all_results = []
        for page in range(1, max_pages + 1):
            # 执行爬虫
            print("\n正在发送请求，请稍候...")
            response = run_spider(keyword, page)
            if response["status"] == "success":
                print("\n✅ 搜索成功!")
                print(f"共提取到 {len(response['data'])} 条有效搜索结果")
                
                # 构建返回数据结构
                search_result = {
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "keyword": keyword,
                    "total_results": len(response['data']),
                    "results": response['data']
                }
                
                all_results.append(search_result)
            else:
                print("\n⚠️  搜索失败或未提取到有效结果")
                return (False, [])
        
        return (True, all_results)

    except Exception as e:
        print(f"\n发生意外错误: {str(e)}")
        return (False, [])

if __name__ == '__main__':
    main()