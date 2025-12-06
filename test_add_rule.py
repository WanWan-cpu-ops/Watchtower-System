from server.database import Database

# 创建数据库对象
db = Database()

# 测试添加爬虫规则
print("测试添加爬虫规则...")
try:
    rule_id = db.add_crawler_rule(
        source_id="test_source",
        source_name="测试源",
        title_xpath="//title[1]",
        content_xpath="//div",
        image_xpath="",
        url_xpath="",
        request_headers="{}",
        status=1,
        remarks="测试规则"
    )
    print(f"添加成功，规则ID: {rule_id}")
except Exception as e:
    print(f"添加失败，错误: {str(e)}")
    import traceback
    traceback.print_exc()
