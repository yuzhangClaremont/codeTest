# codeTest

一个简单的图片压缩服务，还有几道编程题的答案。

## 怎么运行

```bash
cd webapp
pip install -r requirements.txt
uvicorn main:app --reload
```

然后打开 http://localhost:8000/docs 就能看到 API 文档了。

## API

就几个接口：

- POST /api/compress - 上传图片压缩
- GET /api/compress/{id} - 下载压缩后的图片
- GET /api/history - 查看历史记录
- DELETE /api/history/{id} - 删除记录

## 测试

```bash
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/compress
curl http://localhost:8000/api/history
```

## 其他文件

- quiz.py - 反转列表和解数独
- review.py - 5个代码审查的修复
- algo.py - 链表的 reduceRight 实现

## 注意

- 图片最大 10MB
- 支持 jpg/png/gif/bmp/webp/tiff
- 历史记录存在内存里，重启就没了
