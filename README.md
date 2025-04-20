
# 🎥 CourseProject-VR-Interpolation

本项目实现了高帧率 VR 视频的多种插帧方法，包括：

- 帧平均法（Mean Interpolation）
- 深度插帧网络 RIFE（Real-Time Intermediate Flow Estimation）
- **基于 SSIM 的自适应插帧（Adaptive Interpolation）**
  - 秒级（video-level）
  - 帧级（frame-level）

并支持批量处理、延时评估、PSNR 比较、可视化结果及多块视频拼接。

---

## 📁 项目结构

```
multimedia_class/
├── data/                            # 原始 30FPS 视频块
├── ECCV2022-RIFE/                   # RIFE 插帧模型与脚本（从RIFE官方仓库中下载）
├── results/                         # 输出目录
│   ├── mean_interp/                 # 帧平均法插帧结果
│   ├── rife_interp/                 # RIFE 插帧结果
│   ├── adaptive_interp_*/           # 秒级自适应结果（按不同阈值）
│   ├── adaptive_interp_by_frame_*/  # 帧级自适应结果
│   ├── merged_video/                # 合并后的视频段和完整视频
│   ├── psnr/                        # PSNR 日志输出
│   ├── latency_psnr_summary.txt     # 综合评估日志
│   ├── psnr.png / latency.png       # 图表可视化输出
├── utils/                           # 工具模块
│   ├── video_utils.py               # 视频帧提取、保存、均值插帧等
│   ├── metric_utils.py              # PSNR, SSIM 计算工具
│   ├── merge_blocks.py              # 多块视频拼接脚本
│   ├── compare.py                   # PSNR 比较脚本
│   ├── evaluate.py                  # 单个视频质量评估
│   ├── figure.py                    # 画图脚本（PSNR/Latency）
├── mean.py                          # 帧平均法批量插帧
├── rife.py                          # RIFE 插帧批处理
├── adaptive.py                      # 秒级自适应插帧
├── adaptive_by_frame.py             # 帧级自适应插帧
└── README.md                        # 项目说明文档（本文件）
```

---

## 📦 环境依赖
- Python 3.10 
- ffmpeg 4.2
- 以及运行RIFE所需要的环境依赖
```bash
pip install numpy opencv-python moviepy==1.0.3 scikit-image
```
---

## 🚀 快速开始

### 1. 执行帧平均插帧

```bash
python mean.py
```

### 2. 执行 RIFE 插帧（需预下载 RIFE 模型）

```bash
python rife.py
```

### 3. 执行秒级自适应插帧（基于每块平均 SSIM）

```bash
python adaptive.py --threshold 0.98
```
其中 threshold 表示以RIFE为基准的相邻每块平均 SSIM

### 4. 执行帧级自适应插帧（逐对帧 SSIM）

```bash
python adaptive_by_frame.py --threshold 0.98
```
其中 threshold 表示以RIFE为基准的相邻每帧 SSIM

### 5. 合并每秒 6×4 块 → 每秒段视频 → 最终完整视频

```bash
python merge_blocks.py --method adaptive --threshold 0.98
```

---

## 📊 评估结果

### 评估延时与 PSNR，并生成图表：

```bash
python compare.py --method adaptive --threshold 0.98
python figure.py
```

输出位于：

- `results/latency_psnr_summary.txt`
- `results/psnr.png`
- `results/latency.png`

---

## 📌 命名规范说明
![K-M-RHAT-DR-NGA-731-JC.png](https://i.postimg.cc/266XBRp5/K-M-RHAT-DR-NGA-731-JC.png)

- 原始视频块命名：`{t}_{x}_{y}_out.mp4`
- 插帧输出命名：
  - `mean`: `{t}_{x}_{y}_mean.mp4`
  - `rife`: `{t}_{x}_{y}_rife.mp4`
  - `adaptive`: `{t}_{x}_{y}_adaptive.mp4`
- 支持帧级的 `adaptive_interp_by_frame_{阈值}` 输出目录

---

## 📽️ 示例输出视频结构

```bash
results/merged_video/
├── merged_second_1.mp4
├── merged_second_2.mp4
├── ...
└── final_merged_adaptive.mp4
```

## Reference

本项目中使用的深度插帧方法基于 [RIFE (Real-Time Intermediate Flow Estimation)](https://github.com/megvii-research/ECCV2022-RIFE)，于 ECCV 2022 收录。

- RIFE官方仓库地址：https://github.com/megvii-research/ECCV2022-RIFE
- RIFE论文地址：[RIFE: Real-Time Intermediate Flow Estimation for Video Frame Interpolation (ECCV 2022)](https://arxiv.org/abs/2011.06294)

本项目已对其接口进行了适配，用于本项目中的自动化插帧流程。


---


