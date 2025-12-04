import requests
from bs4 import BeautifulSoup


def main(search_content, page_count):
    """百度搜索源主函数
    
    Args:
        search_content: 搜索内容
        page_count: 爬取页数
        
    Returns:
        tuple: (status, data)
            status: 爬取状态（"success"或"failed"）
            data: 爬取的数据列表
    """
    try:
        data = []
        
        # 百度搜索URL模板
        base_url = "https://www.baidu.com/s"
        
        # 爬取指定页数
        for page in range(page_count):
            # 计算起始位置
            start = page * 10
            
            # 构建请求参数
            params = {
                "tn": "75144485_dg",
                "ie": "utf-8",
                "word": search_content,
                "pn": start
            }
            
            # 设置请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # 发送请求
            response = requests.get(base_url, params=params, headers=headers)
            response.encoding = "utf-8"
            
            # 解析HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找搜索结果（优先使用c-container类）
            results = soup.find_all("div", class_="c-container")
            
            if not results:
                # 尝试使用旧的result类名
                results = soup.find_all("div", class_="result")
                if not results:
                    # 没有更多结果了
                    break
            
            # 提取结果信息
            for result in results:
                # 提取标题（尝试多种可能的标题标签和类名）
                title_tag = None
                
                # 尝试h3标签
                title_tag = result.find("h3")
                if not title_tag:
                    # 尝试h3标签与特定类名
                    possible_title_classes = ["t", "c-title"]
                    for cls in possible_title_classes:
                        title_tag = result.find("h3", class_=cls)
                        if title_tag:
                            break
                
                if not title_tag:
                    continue
                
                title = title_tag.text.strip()
                
                # 提取URL
                a_tag = title_tag.find("a")
                if not a_tag:
                    continue
                
                url = a_tag.get("href")
                if not url:
                    continue
                
                # 提取摘要（尝试多种可能的摘要标签和类名）
                summary = ""
                possible_abstract_selectors = [
                    "div.c-abstract",
                    "div.abstract",
                    "div.c-span18.c-gap-left1",
                    "div.content-right"
                ]
                
                for selector in possible_abstract_selectors:
                    abstract_tag = result.select_one(selector)
                    if abstract_tag:
                        summary = abstract_tag.text.strip()
                        break
                
                # 提取图片URL（百度搜索结果可能没有图片）
                image_url = ""
                possible_image_selectors = [
                    "img.c-img",
                    "img.tile-img",
                    "div.imgbox img"
                ]
                
                for selector in possible_image_selectors:
                    thumbnail_tag = result.select_one(selector)
                    if thumbnail_tag and thumbnail_tag.get("src"):
                        image_url = thumbnail_tag.get("src")
                        if image_url and image_url.startswith("//"):
                            image_url = "http:" + image_url
                        break
                
                # 添加到结果列表
                data.append({
                    "title": title,
                    "summary": summary,
                    "image_url": image_url,
                    "url": url
                })
        
        return "success", data
        
    except Exception as e:
        print(f"百度搜索源爬取失败: {e}")
        return "failed", []


if __name__ == "__main__":
    # 测试代码
    status, data = main("Python", 1)
    print(f"爬取状态: {status}")
    print(f"爬取数据数: {len(data)}")
    if data:
        print(f"第一条数据: {data[0]}")
