# API 接口文档使用说明

本目录包含 Hot AI Backend 项目的 API 接口文档，提供多种格式以满足不同需求。

## 📁 文件说明

### 1. `index.html` - 交互式 Web 文档（推荐）
**类似于 Swagger UI 的可测试文档界面**

- **打开方式**: 直接在浏览器中打开
  ```bash
  # Windows PowerShell
  Start-Process docs\index.html
  
  # 或使用默认浏览器
  start docs\index.html
  ```

- **功能特点**:
  - ✅ 美观的现代化 UI 界面
  - ✅ 可展开/收起的接口详情
  - ✅ 完整的请求参数说明
  - ✅ 请求和响应示例
  - ✅ 认证说明
  - ✅ 错误码表格
  - ✅ 响应式布局，支持移动端

### 2. `openapi.yaml` - OpenAPI 3.0 规范文件
**标准的 OpenAPI (Swagger) 规范文件**

- **用途**: 
  - 导入到 Swagger UI、Redoc、Postman 等工具
  - 自动生成客户端代码
  - API 网关配置
  - 自动化测试

- **在线查看工具**:
  - [Swagger Editor](https://editor.swagger.io/) - 上传 YAML 文件即可查看
  - [Stoplight Studio](https://stoplight.io/studio) - 可视化编辑和预览

- **本地使用**:
  ```bash
  # 使用 Docker 运行 Swagger UI
  docker run -d -p 8081:80 -v $(pwd)/docs/openapi.yaml:/usr/share/nginx/html/openapi.yaml swaggerapi/swagger-ui
  ```

### 3. `user-api.md` - Markdown 格式文档
**传统的文本格式文档**

- **用途**:
  - 打印或导出为 PDF
  - 在 GitHub/GitLab 等代码托管平台查看
  - 快速查阅
  - 集成到其他文档系统

- **查看方式**:
  - 任意 Markdown 阅读器
  - VS Code / IntelliJ IDEA 等 IDE
  - GitHub/GitLab 直接渲染

## 🚀 快速开始

### 方式一：Web 界面（推荐）
```powershell
# 在浏览器中打开交互式文档
start docs\index.html
```

### 方式二：使用 Swagger UI
1. 访问 [Swagger Editor](https://editor.swagger.io/)
2. 点击 "File" → "Import URL" 或粘贴 `openapi.yaml` 内容
3. 即可看到类似 Swagger UI 的界面

### 方式三：使用 Postman
1. 打开 Postman
2. 点击 "Import"
3. 选择 `openapi.yaml` 文件
4. 所有接口将自动导入到 Collection 中，可直接测试

## 📊 接口概览

| 接口 | 方法 | 路径 | 认证 |
|------|------|------|------|
| 用户注册 | POST | `/api/v1/auth/register` | ❌ |
| 用户登录 | POST | `/api/v1/auth/login` | ❌ |
| 刷新 Token | POST | `/api/v1/auth/refresh` | ❌ |
| 用户登出 | POST | `/api/v1/auth/logout` | ✅ |

## 🔐 认证说明

除了注册和登录接口外，其他接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <your_access_token>
```

**Token 信息**:
- **有效期**: 24 小时
- **刷新方式**: 使用 Refresh Token 通过 `/auth/refresh` 接口获取新的 Access Token
- **Token 类型**: JWT (JSON Web Token)

## 🛠️ 开发工具集成

### VS Code 插件推荐
- **OpenAPI (Swagger) Editor** - 编辑和预览 OpenAPI 规范
- **REST Client** - 直接发送 HTTP 请求测试接口
- **Thunder Client** - 轻量级 API 测试工具

### IntelliJ IDEA / WebStorm
- 内置支持 OpenAPI 规范
- 安装 "OpenAPI Specification" 插件
- 右键 `openapi.yaml` → "Show OpenAPI Specification"

### Postman
1. Import `openapi.yaml`
2. 自动生成 Collection
3. 在 Authorization 标签页设置 Bearer Token
4. 一键发送请求测试

## 📝 更新日志

- **v1.0.0** (2026-03-31)
  - ✨ 初始版本发布
  - 📄 添加用户认证相关接口文档
  - 🎨 创建交互式 Web 文档
  - 📋 生成 OpenAPI 3.0 规范文件

## 📞 技术支持

如有问题，请联系开发团队或提交 Issue。

---

**最后更新**: 2026-03-31  
**文档版本**: v1.0.0  
**API 版本**: v1
