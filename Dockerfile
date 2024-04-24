#设置python环境镜像
FROM python:3.6
 
# 设置src文件夹是工作目录
WORKDIR /src
 
# 安装相应的python库
RUN pip install -r requirements.txt
 
COPY . .
 
# 执行Python程序（网页程序主程序）
CMD ["python3", "server.py"]
