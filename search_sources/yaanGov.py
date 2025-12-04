import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_webpage(keyword, page_num):
    """根据关键词和页码获取网页内容"""
    url = f"https://www.yaan.gov.cn/search.html?q={keyword}&page={page_num}&cbz=1"
    
    # 设置请求头，模拟浏览器访问
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "host": "www.yaan.gov.cn",
        "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"获取网页失败: {e}")
        return None

def extract_information(html_content):
    """从HTML内容中提取标题、概要、源URL"""
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # 根据实际网页结构找到搜索结果项
    search_items = soup.find_all('li')
    
    for item in search_items:
        # 提取标题
        h1_element = item.find('h1')
        title_element = h1_element.find('a') if h1_element else None
        title = title_element.get_text(strip=True) if title_element else ''
        
        # 提取源URL
        source_url = title_element['href'] if title_element and 'href' in title_element.attrs else ''
        
        # 提取概要
        p_element = item.find('p')
        summary_element = p_element.find('span') if p_element else None
        summary = summary_element.get_text(strip=True) if summary_element else ''
        
        # 图片URL固定返回空字符串
        image_url = ''
        
        # 只有当标题和源URL都存在时，才将结果添加到列表中
        if title and source_url:
            results.append({
                'title': title,
                'summary': summary,
                'image_url': image_url,
                'source_url': source_url
            })
    
    return results

def save_to_json(data, keyword, page_num):
    """将提取的信息保存为JSON文件"""
    if not data:
        print("没有数据可保存")
        return
    
    # 创建数据保存目录（如果不存在）
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"{keyword}_page_{page_num}.json"
    file_path = os.path.join(data_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def main(keyword, max_pages):
    
    # 验证输入
    if not keyword:
        print("关键词不能为空")
        return (False, [])
    
    try:
        max_pages = int(max_pages)
    except ValueError:
        print("页码必须是数字")
        return (False, [])
    
    result = []

    for page_num in range(1, max_pages + 1):
        # 爬取网页
        print(f"正在爬取关键词: {keyword}, 页码: {page_num}")
        html_content = fetch_webpage(keyword, page_num)
        
        if not html_content:
            print("爬取失败，无法继续")
            break
        
        # 提取信息
        print("正在提取信息...")
        extracted_data = extract_information(html_content)
        
        if not extracted_data:
            print("没有提取到任何信息")
            break
        
        print(f"成功提取到 {len(extracted_data)} 条信息")
        result.extend(extracted_data)  # 将提取的数据合并到结果列表中
    
    return (len(result) > 0, result)

if __name__ == "__main__":
    main()
