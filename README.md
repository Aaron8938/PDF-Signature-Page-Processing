# PDF Signature Page Processing

PDF 数字签章页处理工具：将签章页栅格化，解决签章显示异常问题。

## 功能
- 扫描 PDF 中的数字签章字段（Signature widget）
- 将签章页渲染为图片后重建 PDF
- 非签章页保持原样插入
- 输出为 `文件名_签章页处理后.pdf`
- 支持交互模式、命令行参数、stdin 管道

## 环境配置
依赖安装于独立 venv：
```
C:\Users\Administrator\.workbuddy\binaries\python\envs\pdfsig
```
pip 安装时如遇代理超时，设置 `NO_PROXY=*` 并使用 `--trusted-host` 绕过。

## 使用方法
### BAT 模式
双击 `run_signature_process.bat`，拖入 PDF 文件或粘贴路径。
处理完成后提示：`[Y]` 重新运行 / `[Enter]` 退出。

### 命令行模式
```
python main_signature_process.py "file.pdf"
```

## 依赖
- Python 3.x
- PyMuPDF (fitz)
- Pillow

## 注意事项
- 代码风格：面向过程脚本风格，函数精简（find_sig_pages → process_pdf → run_one），使用 `%` 格式化字符串（与其他工具一致）。
