# 多媒体内容分析与处理 API

一个基于 FastAPI 的综合性多媒体内容分析与处理 API 服务，支持社交媒体内容解析、证件照处理、图像修复、YouTube视频下载等功能。

基于FastAPI的社交媒体数据分析API服务，支持从小红书、抖音、快手、微博等平台提取和分析数据。

## 📑 功能特点

- ✅ **多平台支持**：同时支持小红书、抖音、快手、微博等主流社交媒体平台
- ✅ **数据提取**：自动解析分享链接，提取包括文字、图片、视频、用户信息等多维度数据
- ✅ **灵活输出**：支持JSON和HTML两种输出格式，适应不同应用场景
- ✅ **高性能**：采用FastAPI异步框架，支持高并发请求处理
- ✅ **安全可靠**：完善的日志记录和异常处理机制
- ✅ **易于扩展**：模块化设计，便于添加新平台支持

## 🧰 技术栈

- **Web框架**：FastAPI
- **服务器**：Uvicorn
- **数据解析**：BeautifulSoup4、lxml、Selenium
- **HTTP客户端**：Requests、httpx
- **数据处理**：Pandas

## 🏗️ 项目结构

```
.
├── main.py              # 主应用入口
├── start_server.py      # 服务启动脚本
├── deploy.sh            # 生产环境部署脚本
├── run_dev.sh           # 开发环境启动脚本
├── requirements.txt     # 依赖列表
├── logs/               # 日志目录
├── hivision/           # 证件照处理模块
├── model/              # AI模型存储目录
├── storage/            # 文件存储目录
└── src/                # 源代码目录
    ├── app/            # 各平台解析模块
    │   ├── xiaohongshu/    # 小红书解析
    │   ├── douyin/         # 抖音解析
    │   ├── kuaishou/       # 快手解析
    │   └── weibo/          # 微博解析
    ├── controllers/    # 控制器
    ├── models/         # 数据模型
    ├── routes/         # API路由
    ├── services/       # 业务逻辑
    └── utils/          # 工具函数
```

## 📝 API文档

### 主要接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/analyze` | POST | 通用数据分析接口，自动识别平台类型 |
| `/analyze/xiaohongshu` | POST | 小红书数据分析接口 |
| `/analyze/douyin` | POST | 抖音数据分析接口 |
| `/analyze/kuaishou` | POST | 快手数据分析接口 |
| `/analyze/weibo` | POST | 微博数据分析接口 |
| `/health` | GET | 健康检查接口 |

### 请求参数

```json
{
  "url": "社交媒体分享链接",
  "type": "png",  // 可选，图片类型，支持 "png" 或 "webp"
  "format": "json" // 可选，返回格式，支持 "json" 或 "html"
}
```

### 示例请求

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://www.xiaohongshu.com/explore/example",
  "type": "png",
  "format": "json"
}'
```

## 🛠️ 环境配置

项目支持两种运行环境：

- **development**: 开发环境（默认）
- **production**: 生产环境

## 📦 安装和部署

### 开发环境

1. 克隆项目：
```bash
git clone https://github.com/yourusername/social-media-analysis-api.git
cd social-media-analysis-api
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

5. 启动开发服务器：
```bash
# 使用默认配置启动
python start_server.py

# 或指定环境和端口
python start_server.py --env development --port 8000 --host 127.0.0.1

# 直接运行主文件（开发模式）
python main.py
```

### 生产环境

1. 运行部署脚本：
```bash
chmod +x deploy.sh
./deploy.sh [port] [host]  # 端口和主机地址可选，默认为 8000 和 0.0.0.0
```

部署脚本会自动：
- 创建/激活虚拟环境
- 更新代码（git pull）
- 安装/更新依赖
- 重启服务

### 作为守护进程运行

项目提供了在后台作为守护进程运行的脚本:

```bash
./run_as_daemon.sh
```

## 📝 日志管理

- 应用日志：`logs/deploy_*.log`
- 进程 ID：`logs/server.pid`

## 主要功能

### 1. 社交媒体内容解析
支持解析以下平台的内容：
- **小红书**: 提取笔记内容、图片、视频等信息
- **抖音**: 解析视频内容、描述、作者信息等
- **快手**: 获取视频数据和相关信息
- **微博**: 解析微博内容和媒体资源

### 2. 证件照处理
基于 HivisionIDPhotos 提供专业的证件照处理功能：
- **智能制作**: 自动抠图、人脸检测、尺寸调整
- **人像抠图**: 高质量人像分离
- **背景替换**: 支持纯色、渐变背景
- **六寸排版**: 自动生成标准排版照片
- **水印添加**: 自定义文字水印
- **尺寸调整**: 按需调整图片大小和DPI

### 3. 图像修复
基于 IOPaint 提供 AI 驱动的图像修复功能：
- **智能修复**: 使用 LAMA 等先进模型进行图像修复
- **蒙版修复**: 支持自定义蒙版区域修复
- **高清增强**: 集成 RealESRGAN 超分辨率技术
- **面部增强**: 支持 GFPGAN 面部修复
- **批量处理**: 支持多种修复模型切换

### 4. YouTube 视频下载
- **多格式支持**: 支持不同质量的视频下载
- **流式传输**: 大文件流式下载，节省内存
- **质量选择**: 支持 best、worst 或指定分辨率

### 5. 系统工具
- **文件代理**: 提供文件流代理服务
- **图片代理**: 解决跨域图片访问问题
- **健康检查**: 系统状态监控

## API 接口文档

### 基础接口
- `GET /` - 根端点，返回 API 信息
- `GET /health` - 健康检查

### 社交媒体解析接口 (`/analyze`)
- `POST /analyze` - 智能识别并解析社交媒体链接
- `POST /analyze/xiaohongshu` - 解析小红书链接
- `POST /analyze/douyin` - 解析抖音链接  
- `POST /analyze/kuaishou` - 解析快手链接
- `POST /analyze/weibo` - 解析微博链接

### 证件照处理接口 (`/idphoto`)
- `POST /idphoto/create` - 证件照智能制作
- `POST /idphoto/human_matting` - 人像抠图
- `POST /idphoto/add_background` - 添加背景
- `POST /idphoto/layout` - 六寸排版照生成
- `POST /idphoto/watermark` - 添加水印
- `POST /idphoto/resize` - 调整图片大小
- `POST /idphoto/crop` - 证件照裁剪

### 图像修复接口 (`/api/v1/inpaint`)
- `POST /api/v1/inpaint/inpaint` - AI 图像修复

### YouTube 下载接口 (`/analyze/youtube`)
- `GET /analyze/youtube` - YouTube 视频下载

### 系统工具接口 (`/system`)
- `POST /system/get_file_stream` - 文件流代理
- `GET /system/image_proxy` - 图片代理
- `GET /system/proxy` - 通用代理

## API 文档

服务启动后，可以通过以下URL访问API文档：

- **Swagger UI文档**: http://[host]:[port]/docs
- **ReDoc文档**: http://[host]:[port]/redoc

## 使用示例

### 社交媒体内容解析
```bash
# 智能解析（自动识别平台）
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.xiaohongshu.com/explore/xxx"}'

# 指定平台解析
curl -X POST "http://localhost:8000/analyze/xiaohongshu" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.xiaohongshu.com/explore/xxx", "type": "png", "format": "json"}'
```

### 证件照处理
```bash
# 证件照制作
curl -X POST "http://localhost:8000/idphoto/create" \
  -H "Content-Type: application/json" \
  -d '{
    "input_image_base64": "base64_encoded_image",
    "height": 413,
    "width": 295,
    "human_matting_model": "modnet_photographic_portrait_matting",
    "hd": true
  }'
```

### 图像修复
```bash
# AI 图像修复
curl -X POST "http://localhost:8000/api/v1/inpaint/inpaint" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_encoded_image",
    "mask_base64": "base64_encoded_mask",
    "model_name": "lama"
  }'
```

### YouTube 视频下载
```bash
# 下载视频
curl "http://localhost:8000/analyze/youtube?url=https://www.youtube.com/watch?v=xxx&quality=720"
```

## 技术特性

### 高性能架构
- **异步处理**: 基于 FastAPI 的异步架构
- **流式传输**: 大文件流式处理
- **缓存优化**: 模型缓存和资源复用

### AI 模型集成
- **LAMA**: 先进的图像修复模型
- **MTCNN**: 人脸检测技术
- **ModNet**: 高质量人像抠图
- **RealESRGAN**: 图像超分辨率
- **GFPGAN**: 面部增强技术

### 安全与稳定
- **错误处理**: 完善的异常处理机制
- **日志系统**: 分模块的详细日志记录
- **健康检查**: 系统状态监控
- **环境隔离**: 开发/生产环境配置分离

## 🔍 问题排查

### 常见问题及解决方案

#### 1. 服务启动问题
- 检查端口是否被占用：`lsof -i :8000`
- 查看日志文件：`logs/app_*.log`、`logs/system_*.log`
- 确保所有依赖都已正确安装：`pip install -r requirements.txt`
- 检查 Python 版本兼容性

#### 2. AI 模型相关问题
- **图像修复模型加载失败**：
  - 检查 `model/lama/big-lama.pt` 是否存在
  - 确保有足够的磁盘空间和内存
  - 查看 `logs/inpainting_*.log` 获取详细错误信息
  
- **证件照处理失败**：
  - 确保输入图像格式正确（支持 PNG、JPG）
  - 检查图像中是否包含清晰的人脸
  - 验证 base64 编码是否正确

#### 3. 社交媒体解析问题
- **链接解析失败**：
  - 确认链接格式正确且可访问
  - 检查网络连接是否正常
  - 查看 `logs/analyze_*.log` 获取详细信息
  
- **内容获取不完整**：
  - 可能是目标网站反爬虫机制
  - 尝试更新 User-Agent 配置
  - 检查是否需要代理访问

#### 4. YouTube 下载问题
- 确保安装了 `yt-dlp`：`pip install yt-dlp`
- 检查 YouTube 链接是否有效
- 验证网络连接和代理设置 
##
 环境变量

项目支持以下环境变量配置：

- `APP_ENV`: 运行环境 (`development`、`production`、`testing`)
- `PORT`: 服务端口 (默认: 8000)
- `HOST`: 绑定主机 (默认: 127.0.0.1 开发环境, 0.0.0.0 生产环境)

## 模型文件

### 图像修复模型
项目使用 LAMA 模型进行图像修复，模型文件会自动下载到：
- 系统缓存目录: `~/.cache/iopaint/lama/big-lama.pt`
- 项目本地目录: `model/lama/big-lama.pt`

### 证件照处理模型
HivisionIDPhotos 相关模型会根据需要自动下载：
- 人像抠图模型: ModNet、HivisionModNet 等
- 人脸检测模型: MTCNN 等

## 性能优化建议

### 硬件要求
- **CPU**: 推荐 4 核心以上
- **内存**: 推荐 8GB 以上（AI 模型需要较多内存）
- **存储**: 推荐 SSD，至少 10GB 可用空间
- **GPU**: 可选，支持 CUDA 加速图像处理

### 生产环境优化
1. **使用 GPU 加速**：
   ```bash
   # 安装 CUDA 版本的 PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **调整工作进程数**：
   ```bash
   # 在 start_server.py 中修改 workers 参数
   uvicorn.run("main:app", workers=4)
   ```

3. **配置反向代理**：
   ```nginx
   # Nginx 配置示例
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 开发指南

### 项目结构说明
```
src/
├── app/                 # 各平台解析模块
│   ├── xiaohongshu/    # 小红书解析
│   ├── douyin/         # 抖音解析
│   ├── kuaishou/       # 快手解析
│   └── weibo/          # 微博解析
├── controllers/        # 控制器层
├── models/            # 数据模型
├── routes/            # API 路由
├── services/          # 业务逻辑层
└── utils/             # 工具函数
    ├── config.py      # 配置管理
    ├── logger.py      # 日志配置
    └── response.py    # 响应格式
```

### 添加新的解析平台
1. 在 `src/app/` 下创建新平台目录
2. 实现解析逻辑类
3. 在 `src/routes/analyze.py` 中添加路由
4. 更新 `config.py` 中的关键词映射

### 自定义日志
```python
from src.utils import get_app_logger

logger = get_app_logger()
logger.info("自定义日志信息")
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本项目仅供学习和研究使用，请遵守相关平台的使用条款和法律法规。
