# PDF Signature Page Processing

PDF 签章页处理工具：命中签章字段的页面栅格化；无签章但带权限锁的文件无损解保护。`v1.1.0`

## 功能
- 扫描 PDF 中的数字签章字段（Signature widget），将签章页渲染为图片后重建 PDF，非签章页原样保留
- 无签章字段但存在权限保护（禁止修改 / 禁止复制）的文件，仅解除保护，页面内容零改动（文字层、水印、表格线全部原样）
- 输出为 `文件名_处理后.pdf`

## 判定与动作
| 优先级 | 判定条件 | 动作 |
|---|---|---|
| 1 | 页内存在 Signature 字段 | 该页渲染为图片（200 DPI） |
| 2 | 无签章字段，但权限位缺 Modify / Copy（正常文件为 -4） | 解除加密与权限限制，重新保存，内容不动 |
| 3 | 都不满足 | 跳过，提示无需处理 |

有签章的文件若同时带权限锁，栅格化重建后输出天然为无加密文档。

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

## 注意事项
- 代码风格：面向过程脚本风格，函数精简（find_sig_pages / is_restricted → process_pdf → run_one），使用 `%` 格式化字符串（与其他工具一致）。
- 解保护不动内容：实测原文与输出在 300 DPI 下逐像素一致（差异 0），文本 span、字体对象、绘制矢量、元数据均不变，仅 `encryption` 标记消失。
- 验证基准文件：`附件3.苏州"慧选址"系统检测报告.pdf`（iText 5.5 导出，权限 -1852，仅允许打印）。
- 文件带打开密码（needs_pass）时报错退出，不做处理。

## 更新日志
- **v1.1.0** 新增权限锁识别与无损解保护；输出统一为 `_处理后`；栅格化改用 `pix.save()`，去掉 Pillow 依赖。
- **v1.0.0** 初版：签章页栅格化重建。
