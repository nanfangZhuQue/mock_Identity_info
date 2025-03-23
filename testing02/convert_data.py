# 转换脚本：将ChinaCitys.py中的数据转换为area_code_map.py格式

# 直接从文件中读取数据，避免模块导入问题
with open('d:\\my-obj\\testing02\\ChinaCitys.py', 'r', encoding='utf-8') as f:
    china_citys_content = f.read()

# 执行文件内容以获取address变量
locals_dict = {}
exec(china_citys_content, globals(), locals_dict)
address_data = locals_dict.get('address')

if not address_data:
    raise ValueError("无法从ChinaCitys.py中提取address变量")

# 创建新的area_code_map字典
new_area_code_map = {}

# 遍历address列表，转换数据格式
for province_data in address_data:
    province_name = province_data["province"]
    new_area_code_map[province_name] = {}
    
    for city_data in province_data["citys"]:
        city_name = city_data["city"]
        new_area_code_map[province_name][city_name] = {}
        
        for area_data in city_data["areas"]:
            area_name = area_data["area"]
            area_code = area_data["code"]
            new_area_code_map[province_name][city_name][area_name] = area_code

# 保留原有的车牌字母映射表
city_license_map = {
    "北京市": {"市辖区": "京"},
    "天津市": {"市辖区": "津"},
    "河北省": {
        "石家庄市": "冀A",
        "唐山市": "冀B",
        "秦皇岛市": "冀C",
        "邯郸市": "冀D",
        "邢台市": "冀E",
        "保定市": "冀F",
        "张家口市": "冀G",
        "承德市": "冀H",
        "沧州市": "冀J",
        "廊坊市": "冀R",
        "衡水市": "冀T"
    },
    "山西省": {
        "太原市": "晋A",
        "大同市": "晋B",
        "阳泉市": "晋C",
        "长治市": "晋D",
        "晋城市": "晋E",
        "朔州市": "晋F",
        "晋中市": "晋K",
        "运城市": "晋M",
        "忻州市": "晋H",
        "临汾市": "晋L",
        "吕梁市": "晋J"
    }
}

# 生成新的area_code_map.py文件
with open('d:\\my-obj\\testing02\\area_code_map.py', 'w', encoding='utf-8') as f:
    f.write('# 行政区划代码映射表\n')
    f.write('# 格式：{省份: {城市: {区县: 区县代码}}}\n\n')
    
    f.write('area_code_map = {\n')
    for province, cities in new_area_code_map.items():
        f.write(f'    "{province}": {{\n')
        for city, areas in cities.items():
            f.write(f'        "{city}": {{\n')
            for area, code in areas.items():
                f.write(f'            "{area}": "{code}",\n')
            f.write('        },\n')
        f.write('    },\n')
    f.write('}\n\n')
    
    f.write('# 车牌字母映射表\n')
    f.write('city_license_map = {\n')
    for province, cities in city_license_map.items():
        f.write(f'    "{province}": {{\n')
        if isinstance(cities, dict):
            for city, code in cities.items():
                f.write(f'        "{city}": "{code}",\n')
        else:
            f.write(f'        "{cities}",\n')
        f.write('    },\n')
    f.write('}\n')

print("转换完成！新的area_code_map.py文件已生成。")