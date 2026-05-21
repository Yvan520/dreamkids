# 一键部署指南

## 选项 A：Render（推荐，国内访问快）

1. 打开 https://render.com 点 "Get Started"
2. 登录（用 GitHub 账号）
3. 点 "New +" → "Web Service"
4. 选择你的 GitHub 仓库 `Yvan520/dreamkids`
5. 设置：
   - **Name**: `dreamkids-storycraft`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0`
   - **Plan**: Free
6. 点 "Create Web Service"
7. 部署完成后，设置环境变量（Environment Variables）：
   - `API_KEY` = 你的通义千问 API Key
   - `IMAGE_SERVICE` = `doubao` 或 `tongyi`
   - `TEXT_MODEL` = `qwen-plus`

## 选项 B：Hugging Face Spaces（永久免费）

1. 打开 https://huggingface.co/spaces 点 "Create new Space"
2. 设置：
   - **Space Name**: `dreamkids-storycraft`
   - **SDK**: `Streamlit`
   - **License**: `MIT`
3. 点 "Create Space"
4. 把 `src/` `assets/` `scripts/` `tests/` `.streamlit/` 文件夹
   以及 `requirements.txt` `.env.example` `pyproject.toml` 文件
   拖到上传区域
5. 在 Settings → Repository Secrets 添加环境变量：
   - `API_KEY`
   - `IMAGE_SERVICE`
   - `TEXT_MODEL`

## 选项 C：Docker 部署

```bash
docker build -t storycraft .
docker run -p 8501:8501 \
  -e API_KEY=your-key \
  -e IMAGE_SERVICE=doubao \
  storycraft
```

## 获取 API Key

### 通义千问（推荐新手）
1. 打开 https://bailian.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通"通义千问"服务（新用户免费额度）
4. 创建 API Key

### 豆包（速度更快，支持组图）
1. 打开 https://console.volcengine.com/ark
2. 注册/登录火山引擎
3. 创建推理接入点，获取 API Key
