# 行政区划代码映射表
# 格式：{省份: {城市: {区县: 区县代码}}}

area_code_map = {
    "北京市": {
        "北京市": {
            "东城区": "110101000000",
            "西城区": "110102000000",
            "朝阳区": "110105000000",
            "丰台区": "110106000000",
            "石景山区": "110107000000",
            "海淀区": "110108000000",
            "门头沟区": "110109000000",
            "房山区": "110111000000",
            "通州区": "110112000000",
            "顺义区": "110113000000",
            "昌平区": "110114000000",
            "大兴区": "110115000000",
            "怀柔区": "110116000000",
            "平谷区": "110117000000",
            "密云区": "110118000000",
            "延庆区": "110119000000",
        }
    },
    "天津市": {
        "天津市": {
            "和平区": "120101000000",
            "河东区": "120102000000",
            "河西区": "120103000000",
            "南开区": "120104000000",
            "河北区": "120105000000",
            "红桥区": "120106000000",
            "东丽区": "120110000000",
            "西青区": "120111000000",
            "津南区": "120112000000",
            "北辰区": "120113000000",
            "武清区": "120114000000",
            "宝坻区": "120115000000",
            "滨海新区": "120116000000",
            "宁河区": "120117000000",
            "静海区": "120118000000",
            "蓟州区": "120119000000",
        }
    },
    # 此处省略了大量区域代码数据，实际使用时应包含完整数据
    # 完整数据请参考原始area_code_map.py文件
}

# 车牌字母映射
city_license_map = {
    # 此处应包含完整的车牌字母映射数据
    # 由于数据量大，此处省略
}