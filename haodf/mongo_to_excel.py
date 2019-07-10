"""
提取mongo数据保存到excel中
"""

import pymongo
import xlwt

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.kidney
collection = db.haodf_test


def get_values():
    values = []
    for i, item in enumerate(collection.find()):
        values.append([item['name'], item['title'], item['department'], item['experience'],
                       item['special'], str(item['outpatient_info']), item['intro_url']])
    return values


def write_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿
    print("xls格式表格写入数据成功！")


if __name__ == '__main__':
    values = get_values()
    write_excel_xls('/home/shengnei/haodf_hzh.xls', 'haodf_hzh', values)
    # write_excel_xls('/Users/mac/PycharmProjects/shengnei/haodf_bj.xls', '北京', values)
