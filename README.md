## 第一步：设置 .env
把项目中的 .env 里面的 OPENAI_API_KEY 配置为自己的

```
OPENAI_API_KEY=sk-xxxx
```

## 第二步设置：

控制某些软件包在编译和运行时是否使用本地（原生）库

执行下面命令：
```
export HNSWLIB_NO_NATIVE=1
```

## 第三步：安装包

执行下面命令：
```
pip install -r requirements.txt
```

## 第四步：运行

#### 运行 main.py 文件

#### 然后在界面里面输入问题：
🤖：有什么可以帮您？
👨：9月份的销售额是多少（需要自己输入）
>>>>Round: 0<<<<

#### 问题参考：
* 9月份的销售额是多少
* 销售总额最大的产品是什么
* 帮我找出销售额不达标的供应商
* 给这两家供应商发一封邮件通知此事
* 对比8月和9月销售情况，写一份报告


```sql
    select * from road_centerline where id = 1
```
