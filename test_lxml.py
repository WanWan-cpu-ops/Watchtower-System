import sys
import lxml
print(f"Python版本: {sys.version}")
print(f"lxml版本: {lxml.__version__}")

# 尝试不同的导入方式
try:
    from lxml import etree
    print("成功导入: from lxml import etree")
except ImportError as e:
    print(f"导入失败: from lxml import etree - {e}")

try:
    import lxml.etree
    print("成功导入: import lxml.etree")
except ImportError as e:
    print(f"导入失败: import lxml.etree - {e}")

# 查看lxml模块的内容
print("\nlxml模块的内容:")
print(dir(lxml))
