from controller.rag.loader.excel_loader import ExcelLoader

loader = ExcelLoader(file_path='./data/upload/人员信息.xlsx')
loader.load()
