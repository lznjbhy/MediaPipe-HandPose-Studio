import tabula
import pandas as pd

# 1. 定义文件路径
pdf_path = "main.pdf"   # 替换为你的PDF文件路径
excel_path = "output.xlsx" # 输出的Excel文件路径

# 2. 指定需要提取的页码
# 注意：页码可以是一个整数（单页），也可以是一个列表（多页），如 [2, 5, 6, 7]
# 也可以使用页码范围字符串 ‘2-4‘, ’2,5-7‘
pages = [10, 11]  # 提取第2，5，6，7页
# 另一种写法： pages = “2,5-7”

# 3. 使用tabula读取指定页面的所有表格
# multiple_tables=True 表示一页上可能有多个表格
df_list = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, lattice=True)

# 4. 创建一个ExcelWriter对象，用于写入多个Sheet
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # 遍历提取到的所有表格列表
    for i, df in enumerate(df_list):
        # 为每个表格创建一个Sheet，Sheet名按顺序编号
        sheet_name = f"Page_{i+1}"
        # 将DataFrame写入Excel的Sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"表格 {i+1} 已写入Sheet: {sheet_name}")

print(f"\n转换完成！所有表格已保存至: {excel_path}")