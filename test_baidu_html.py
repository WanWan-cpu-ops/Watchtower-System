import requests
from bs4 import BeautifulSoup

# 发送请求
def get_baidu_html():
    url = "https://www.baidu.com/s?tn=75144485_dg&ie=utf-8&word=Python&pn=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    return response.text

# 查看HTML结构
def analyze_html(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # 查看页面标题
    print(f"页面标题: {soup.title.text}")
    
    # 查找所有可能的搜索结果容器
    print("\n查找搜索结果容器...")
    
    # 尝试多种可能的类名
    possible_classes = [
        "result",
        "c-container", 
        "result-op",
        "t-container"
    ]
    
    for class_name in possible_classes:
        results = soup.find_all("div", class_=class_name)
        print(f"找到类名 '{class_name}' 的元素数量: {len(results)}")
    
    # 查看内容区域
    content_left = soup.find("div", id="content_left")
    if content_left:
        print(f"\ncontent_left 包含的子元素数量: {len(content_left.find_all('div'))}")
        # 打印前几个子元素的类名
        for i, div in enumerate(content_left.find_all('div')[:5]):
            print(f"第{i+1}个子元素的类名: {div.get('class')}")
            
            # 如果找到结果，打印详细信息
            if div.get('class'):
                print(f"  子元素HTML: {div.prettify()[:500]}...")
                break

if __name__ == "__main__":
    html = get_baidu_html()
    analyze_html(html)