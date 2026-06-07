# B站整合包监控

每2小时自动检查 B站 上新的「整合包更新/发布」视频，推送到微信。

## 部署步骤

### 1. 注册 Server酱
- 打开 https://sct.ftqq.com
- 微信扫码登录
- 复制你的 SendKey

### 2. 上传到 GitHub
```
# 在本地执行（或手动上传）
git init
git add .
git commit -m "init"
```

### 3. 设置密钥
- 打开 GitHub 仓库 Settings → Secrets and variables → Actions
- 点 `New repository secret`
- Name: `SERVERCHAN_KEY`
- Value: 粘贴你的 Server酱 SendKey

### 4. 手动触发一次测试
- 打开 GitHub 仓库 Actions 页面
- 点 `B站整合包监控` → `Run workflow`
