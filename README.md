# 物业业主信息管理（CRUD）

用于记录物业公司业主信息的小型 CRUD 项目，包含房号、业主姓名、联系电话、年龄、物业费与欠款等字段，支持新增、编辑与删除，并提供数据分析摘要。

## 功能

- 新增业主信息
- 查看业主列表
- 编辑业主信息
- 删除业主信息
- 数据分析（年龄占比、欠款统计）

## 技术栈

- Python 3
- Flask
- SQLite

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:5000`。

## 数据说明

- 数据默认存放在项目根目录下的 `owners.db`。
- 需要重置数据时可删除该文件。
