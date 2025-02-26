# to_beancount

## 环境

- **Python 版本**：3.13.1
- **操作系统**：Windows 11

## 起源

春节过后，我发现自己在假期的消费有些失控。于是，我在查看微信支付账单，试图找出问题时。发现微信账单的精度让我感到失望——它只是简单地罗列了每一笔交易，却没有提供更深入的财务分析。也就意味着如果想要更好地管理自己的财务，仅靠微信账单是远远不够的。就在这时，我偶然接触到了复式记账法和 Beancount。Beancount 是一个强大的复式记账工具，它能够帮助我更系统地记录和分析每一笔收支，从而更好地掌握自己的财务状况。我立刻被它吸引住了，但很快又遇到了新的问题：手动记录账目实在是太繁琐了，我根本无法坚持下去。于是，我决定开发一个程序，将微信支付账单自动转化为 Beancount 格式。这样，我既可以利用 Beancount 的强大功能，又不需要手动记录账目。经过一番努力，to_beancount 诞生了！🎉

## 使用方式

### 1. 应用初始化

在项目根目录下运行以下命令以初始化应用：

```cmd
py.exe .\beancount_helper\main.py -i
```

### 2. 设置规则

为微信支付设置规则文件，会使用默认应用打开，同时输出路径位置，运行以下命令：

```cmd
py.exe .\beancount_helper\main.py -gr wechat
规则文件路径:C:\Users\xxx\AppData\Local\beancount_helper\data\rule\wechat_rule.xlsx
```

### 3. 账户映射

将微信支付账单文件映射到 Beancount 格式。运行以下命令：

```cmd
py.exe .\beancount_helper\main.py -t "微信支付账单(20250101-20250221).csv" -a wechat
映射后文件路径：C:\Users\xxx\AppData\Local\beancount_helper\data\temp\2025-02-26_14-48-01_4355.csv
```

### 4. 映射到 Beancount

将映射后的文件转换为 Beancount 格式。运行以下命令：

```cmd
py.exe .\beancount_helper\main.py -t  "2025-02-26_14-48-01_4355.csv" -b
2025-02-26 14:48:32 - beancount_helper - INFO - 格式检查成功！
2025-02-26 14:48:32 - beancount_helper - DEBUG - Beancount 目录: C:\Users\xxx\AppData\Local\beancount_helper\data\bean
2025-02-26 14:48:32 - beancount_helper - DEBUG - 临时文件路径: C:\Users\xxx\AppData\Local\beancount_helper\data\bean\tmp9em7irz1.bean
2025-02-26 14:48:32 - beancount_helper - DEBUG - 新文件路径: C:\Users\xxx\AppData\Local\beancount_helper\data\bean\2025-02-26_14-48-31_7671.bean
2025-02-26 14:48:32 - beancount_helper - INFO - 交易记录写入成功！
```

### 5. 启动 Beancount GUI

启动 Beancount 的图形界面。运行以下命令：

```cmd
py.exe .\beancount_helper\main.py -r
Starting Fava on <http://127.0.0.1:5001>
Fava started successfully!
Press Ctrl+C to exit...
```
