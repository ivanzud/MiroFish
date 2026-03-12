# 贡献指南

感谢你对 MiroFish 项目的兴趣！我们欢迎任何形式的贡献。

## 如何贡献

### 1. Fork 仓库
点击 GitHub 仓库页面的 "Fork" 按钮，将仓库复制到你的账户。

### 2. 克隆你的 Fork
```bash
git clone https://github.com/你的用户名/MiroFish.git
cd MiroFish
```

### 3. 创建分支
```bash
git checkout -b feature/你的功能名称
# 或
git checkout -b fix/问题描述
```

### 4. 进行修改
- 确保代码符合项目规范
- 添加必要的测试
- 更新相关文档

### 4.1 运行校验
提交前建议至少运行一次仓库级校验：

```bash
npm run validate
```

如果你只想先跑较快的一轮检查，可以使用：

```bash
npm run validate:fast
```

`validate:fast` 会运行轻量级后端测试集和前端测试；`validate` 会额外执行前端生产构建。

### 4.2 安装可选 Git Hooks
这个仓库提供了轻量、仓库内置的 Git hooks，不依赖 Husky，也不强制所有贡献者启用：

```bash
npm run hooks:install
```

安装后：

- `pre-commit` 会运行后端轻量测试和前端测试
- `pre-push` 会运行完整校验（含前端 build）

如需取消，只需执行：

```bash
git config --unset core.hooksPath
```

### 5. 提交更改
```bash
git add .
git commit -m "描述你的修改"
```

### 6. 推送到你的 Fork
```bash
git push -u origin docs/add-pr-guide
```

### 7. 创建 Pull Request
1. 访问你的 GitHub Fork 仓库
2. 点击 "Compare & pull request" 按钮
3. 填写 PR 描述
4. 点击 "Create pull request"

## 分支命名规范

- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构

## 代码规范

- 前端: 遵循 Vue.js 风格指南
- 后端: 遵循 PEP 8 Python 代码规范

## 许可证

参与本项目即表示你同意遵守 MIT 许可证。
