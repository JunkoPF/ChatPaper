# Paper searching & summarizing tool

使用 semantic scholar api 进行论文查询并下载 pdf，然后借助 [ChatPaper](https://github.com/kaixindelele/ChatPaper) 对论文 pdf 进行批量总结。

## 使用指南

### Step 1 脚本配置

配置 `apikey.ini` 和下载依赖，请参考[这里](https://github.com/kaixindelele/ChatPaper/tree/main#%E4%BD%BF%E7%94%A8%E6%AD%A5%E9%AA%A4)。

注意，本项目额外添加了 PROXY 字段，可以设置 PROXY 为代理开启的端口（例如 http://127.0.0.1:7890 ），这样就不需要设置全局代理了。(也可以不配置 PROXY 直接使用全局代理)

### Step 2 调用 paper_seeker.py

调用 `paper_seeker.py`，传入相关参数后，会查找并下载对应论文 pdf，并自动生成总结。

支持的参数：

- `--keywords KEYWORDS`: **必选**，论文查找关键字。（多个关键字之间用逗号分隔即可）
- `--save_pdf`: **可选**，如果添加，则将查找到的论文 pdf 文件存储到 `pdf/<timestamp>/xxx.pdf` 位置。
- `--limit LIMIT`: **可选**，输出论文数量，默认值为 5。
- `--offset OFFSET`: **可选**，查找偏移（即从第几个结果开始输出），默认值为 0。
- `--output OUTPUT_PATH`：**可选**，论文总结文本文档输出的位置，默认将输出到命令行中。

#### 示例

例如查找关键字为 web assembly, rust 相关的论文，将结果输出到相对路径为 summary.txt 的位置，可以在项目根目录下执行：

```shell
python3 paper_seeker.py --keywords "web assembly, rust" --output "summary.txt"
```

查找关键字为 garbage collection, golang 相关的论文，将结果输出到命令行，只要 3 篇论文，并保存 pdf,可以在项目根目录下执行：

```shell
python3 paper_seeker.py --keywords "garbage collection" --save_pdf --limit 3
```

这样搜索到的论文 pdf 文件将会保存到 `./pdf/<timestamp>/...` 中。

## TODO

- [ ] 支持缓存 pdf 文件
- [ ] 支持非 open access pdf 的论文根据摘要进行概述
- [ ] 优化论文总结格式
- [ ] 提供交互界面
