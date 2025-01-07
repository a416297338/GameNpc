import xml.etree.ElementTree as ET

from deep_translator import GoogleTranslator

def translate_to_chinese(text):
    translator = GoogleTranslator(source='en', target='zh-CN')
    translation = translator.translate(text)
    return translation


# 解析上传的XML文件
file_path = './desert.tmx'
tree = ET.parse(file_path)
root = tree.getroot()

# 遍历文档中的所有[property]标签
for property_elem in root.findall(".//property"):
    # 获取name属性
    name = property_elem.get("name")
    # 如果name是'name'并且value不是None,进行翻译
    if name == "name" and property_elem.get("value") is not None:
        # 获取value属性
        value = property_elem.get("value")
        # 翻译value
        if value == "None":
            continue
        translated_value = translate_to_chinese(value)
        # 更新[property]标签的value属性为翻译后的文本
        property_elem.set("value", translated_value)

# 将修改后的XML保存到新的文件
output_file_path = './translated_tmx_file.tmx'
tree.write(output_file_path, encoding='utf-8', xml_declaration=True)