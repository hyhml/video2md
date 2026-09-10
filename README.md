# video2md

面向“视频 → 文稿”工作流的模块化工具仓库。当前实现第一环节：将本地视频或音频转为带粗时间轴的中文初稿。

默认模型是 **Paraformer-zh**（速度优先）；可用 `--model nano` 切换为 **Fun-ASR-Nano-2512**（质量优先）。转写在本地运行，模型权重首次使用时从其公开模型仓库下载。

## 两种下载方式

- **只使用工具**：下载 [`user` 分支](https://github.com/hyhml/video2md/tree/user)，它只包含运行所需代码和简短说明。

  ```bash
  git clone --branch user --depth 1 https://github.com/hyhml/video2md.git
  ```

- **参与开发或复现评测**：下载本分支（`main`）。其中 `developer-mode/` 保留协议、版本记录、模型选择依据和可公开的汇总测试数据；不含原视频、模型权重和完整转写，以避免体积及版权问题。

当前用户包版本为 `0.1.0`；对应的模型比较基准为 `v0.2.0`。版本语义与后续环节的规划见 [开发者说明](developer-mode/README.md)。

## 当前工作流边界

1. 本仓库当前完成：语音转文字（ASR）。
2. 后续将独立加入：口语修订、合理分段、Markdown 组织。

各环节将保持“可单独调用，也可串联”的接口边界。
