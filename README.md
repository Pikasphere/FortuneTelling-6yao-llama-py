# 六爻占卜 · Flet 桌面应用

一个基于 **Flet** 的六爻占卜小工具，支持数字起卦、显示本卦/变卦/卦辞/爻辞，并集成本地大语言模型进行 AI 解读。
**Qwen大语言模型需自行下载**

---

## 功能特性

- 🎴 **数字起卦**：输入三个正整数（上卦数、下卦数、动爻数），或一键随机生成
- 📜 **完整卦象展示**：本卦、变卦、六爻图形、动爻标记
- 📖 **原文与白话**：卦辞、爻辞原文 + 白话翻译 + 断易
- 🤖 **AI 解读**：本地 Qwen 模型，根据卦象和所问之事生成解读建议
- 📚 **历史记录**：自动保存最近 10 次占卜结果
- 🌙 **深色主题**：沉浸式暗色界面

---

## 技术栈

- Python 3.10+
- Flet（UI 框架）
- llama-cpp-python（本地 LLM 推理）
- 数据来源：`data/yijing.json`（64 卦原文、白话、爻辞等）

---

## 目录结构

```
FortuneTelling/
├── main.py                 # 主程序，负责拼装视图与回调
├── views/                  # UI 层
│   ├── __init__.py
│   ├── theme.py            # 颜色、尺寸常量
│   ├── components.py       # 可复用组件：ResultCard、HistoryItem、SummaryCard、AIView
│   └── views.py            # 大区域视图：HeaderView、InputView、ResultView、HistoryView
├── core/                   # 逻辑层
│   ├── __init__.py
│   ├── core.py             # 算卦逻辑、数据加载、AI prompt 构建
│   ├── models.py           # 数据类：Hexagram、CastResult
│   └── gua64.py            # 64 卦二进制检索表
├── llama/                  # AI 模块
│   ├── __init__.py
│   ├── qwen.py             # 模型加载与推理
│   └── gguf/
│       └── Qwen3.8-2B-Q4_K_M.gguf   # 本地模型文件（需自行下载）
├── data/
│   └── yijing.json         # 64 卦结构化数据（原文、白话、爻辞、解读）
└── requirements.txt
```

---

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/Pikasphere/FortuneTelling-6yao-llama-py.git
cd FortuneTelling-6yao-llama-py
```

### 2. 创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

`requirements.txt` 内容：

```txt
flet>=0.24.0
llama-cpp-python>=0.2.0
```

> 如果安装 `llama-cpp-python` 需要编译，请根据系统安装 C++ 编译工具链。  
> 有 NVIDIA 显卡可安装 CUDA 版本以加速推理。

### 4. 下载模型文件

将 GGUF 模型放入 `llama/gguf/` 目录，命名为：

你可以从 Hugging Face 或 ModelScope 下载任意兼容的 Qwen GGUF 模型。  

### 5. 准备数据文件

确保 `data/yijing.json` 存在。该文件包含 64 卦的完整数据，格式为：

```json
{
  "hexagrams": [
    {
      "image": "乾为天",
      "canon": {
        "guaci": ["乾：元，亨，利，贞。"],
        "lines": [
          {"index": 0, "text": "初九：潜龙勿用。"},
          ...
        ]
      },
      "overview": {
        "translation": {"text": ["乾卦：大吉大利，吉利的贞卜。"]},
        "duanyi": ["..."],
        ...
      },
      "lines": [
        {
          "index": 0,
          "original": {"text": ["初九。潜龙勿用。"]},
          "translation": {"text": ["初九：潜藏的龙，无法施展。"]},
          ...
        }
      ]
    }
  ]
}
```

---

## 运行

```bash
python main.py
```

---

## 使用说明

1. **输入所问之事**：在文本框中填写你想占问的问题，例如“近期事业运势如何？”
2. **输入三个数字**：
   - 上卦数：决定上卦（先天八卦数：乾1、兑2、离3、震4、巽5、坎6、艮7、坤8）
   - 下卦数：决定下卦
   - 动爻数：决定动爻（除以6取余，余0为上爻）
   - 也可以点击「随机三数」自动填充
3. **点击「起卦」**：
   - 页面立即显示本卦、变卦、六爻图形、动爻标记
   - 下方展示卦辞、爻辞原文及白话翻译
   - AI 解读区会显示「正在加载模型…」或「正在解读…」，稍后展示 AI 生成的解读
4. **查看历史记录**：页面底部保留最近 10 次占卜记录
5. **清空**：点击「清空」按钮清除当前卦象，历史记录不受影响

---

## 配置说明

### 模型参数

在 `llama/qwen.py` 中可以调整：

```python
_LLM = Llama(
    model_path="llama/gguf/Qwen3.8-2B-Q4_K_M.gguf",
    n_ctx=2048,          # 上下文长度，越小越快
    n_threads=8,         # CPU 线程数，建议设为物理核心数
    n_gpu_layers=0,      # 有 NVIDIA 显卡可设为 -1 使用 GPU
    chat_format="qwen",
    verbose=False,
)
```

### 系统提示词

同样在 `llama/qwen.py` 中，`SYSTEM_PROMPT` 定义了 AI 的角色和回答要求，可根据需要修改。

---

## 注意事项

- **首次运行较慢**：需要加载模型到内存，视硬件不同可能需要 5~30 秒，之后再次起卦会很快。
- **模型文件**：请确保模型文件路径正确，否则 AI 解读会报错。
- **内存占用**：2B Q4 模型约占用 1.5GB 内存，请确保系统有足够空闲内存。
- **数据文件**：`data/yijing.json` 必须存在且格式正确，否则卦辞、爻辞无法显示。
- **AI 解读仅供参考**：解读内容由本地模型生成，不构成任何决策建议。

---

## 许可证

MIT License

---

## 致谢

- 卦辞、爻辞数据来源于公开的易经资料
- UI 框架 [Flet](https://flet.dev/)
- 本地推理 [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- 模型 [Qwen](https://github.com/QwenLM/Qwen)
