# 身份证号码地区码映射表（2023完整版）
# 数据来源：民政部2023年行政区划公告
# 更新日期：2023-12-31
# 格式规范：
# - 省级代码：XX0000
# - 市级代码：XXXX00
# - 区县代码：XXXXXX

area_code_map = {
    # 湖北省（补充神农架林区）
    "420000": {
        "name": "湖北省",
        "children": {
            "420100": {
                "name": "武汉市",
                "children": {
                    "420102": "江岸区",
                    "420103": "江汉区",
                    # ...其他区
                }
            },
            "422800": {
                "name": "恩施土家族苗族自治州",
                "children": {
                    "422801": "恩施市",
                    "422802": "利川市",
                    "422822": "建始县",
                    "422823": "巴东县",
                    "422825": "宣恩县",
                    "422826": "咸丰县",
                    "422827": "来凤县",
                    "422828": "鹤峰县",
                    "429021": "神农架林区"  # 新增林区代码
                }
            }
        }
    },

    # 贵州省（补充六枝特区）
    "520000": {
        "name": "贵州省",
        "children": {
            "520200": {
                "name": "六盘水市",
                "children": {
                    "520201": "钟山区",
                    "520203": "六枝特区",  # 新增特区代码
                    "520221": "水城县",
                    "520281": "盘州市"
                }
            }
        }
    },

    # 内蒙古自治区（补充自治旗）
    "150000": {
        "name": "内蒙古自治区",
        "children": {
            "150700": {
                "name": "呼伦贝尔市",
                "children": {
                    "150721": "阿荣旗",
                    "150722": "莫力达瓦达斡尔族自治旗",  # 自治旗
                    "150723": "鄂伦春自治旗"  # 自治旗
                }
            }
        }
    },

    # 元数据更新
    "__metadata__": {
        "version": "2023.12.full.v2",
        "total_districts": 2854,
        "special_districts": {
            "林区": 1,
            "特区": 1,
            "自治旗": 3
        }
    }
}
