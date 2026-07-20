# 地质行业动态 · 每日速览

> 广东省地质测绘院 技术部 · 陈敏 汇编  
> 自动更新 | GitHub Pages | 移动端适配

---

## 一键部署

1. 将本项目推送到 GitHub 仓库
2. 进入仓库 **Settings → Pages**
3. Source 选择 **GitHub Actions**
4. 访问 `https://你的用户名.github.io/仓库名/`

---

## 自动更新

- **频率**：每日 UTC 00:00（北京时间 08:00）自动运行
- **原理**：GitHub Actions 定时执行 `update.py`，自动抓取信息源新增文章
- **手动触发**：进入 Actions 页面 → Daily Update → Run workflow

---

## 信息源覆盖

| 分类 | 渠道 |
|------|------|
| 部委官方 | 自然资源部、中国地质调查局 |
| 专业媒体 | i自然全媒体、泰伯网 |
| 科研院所 | 莫干山地信实验室 |
| 学术期刊 | 测绘学报 |

---

## 项目结构

```
geo-daily/
├── index.html    # 前端页面（移动端适配）
├── data.json     # 数据存储（文章列表、渠道配置）
├── update.py     # 自动采集脚本
├── .github/
│   └── workflows/
│       └── update.yml   # GitHub Actions 配置
└── README.md
```

---

## 本地预览

```bash
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```
