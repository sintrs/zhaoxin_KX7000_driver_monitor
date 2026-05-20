# 兆芯驱动版本监控

监控兆芯官网驱动更新，发现新版本时通过微信（Server 酱）推送通知。

## 监控目标

- **页面**: https://www.zhaoxin.com/qdxz.aspx?nid=31&typeid=600
- **驱动**: KX-7000-Linux OS_x64
- **当前基准版本**: `26.00.48`

## 运行频率

每 12 小时自动检查一次（GitHub Actions 定时任务）

## 配置步骤

### 1. Fork 或创建仓库

建议设置为 **Public** 仓库，GitHub Actions 免费额度无限。

### 2. 配置 Server 酱

1. 访问 https://sct.ftqq.com/
2. 微信扫码登录
3. 复制 **SendKey**（格式如 `SCT1234567890abcdef...`）

### 3. 设置 GitHub Secrets

1. 打开仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name: `SERVERCHAN_KEY`
4. Value: 你的 SendKey

### 4. 手动测试

进入 **Actions** → **兆芯驱动监控** → **Run workflow**，查看运行日志。

### 5. 更新基准版本

当收到更新通知后，修改 `zhaoxin_monitor.py` 中的 `BASELINE_VERSION` 为新版本号，提交到仓库。

## 文件结构

```
.
├── .github/workflows/monitor.yml   # GitHub Actions 配置
├── zhaoxin_monitor.py              # 监控脚本
├── requirements.txt                # Python 依赖
└── README.md                       # 本文件
```

## 注意事项

- `SERVERCHAN_KEY` 存储在 GitHub Secrets 中，不会泄露
- 免费版 Server 酱每日限 5 条推送，驱动更新频率低，足够使用
- 如需更及时通知，可修改 `.github/workflows/monitor.yml` 中的 cron 表达式
