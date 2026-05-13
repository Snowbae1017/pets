# 示例：使用 Codex App 生成桌面宠物

以 **Cheese**（蓝白英短猫）为例，展示从自家宠物照片生成 Codex 桌面宠物的完整流程。

## 前置条件

- [Codex App](https://openai.com/codex)（macOS）— 内置 `/pet` 技能和 `$imagegen`
- 宠物照片：几张脸部和身体照片放在一个文件夹（如 `~/Downloads/cheese/`）
- 图像生成模型：`gpt-image-2`（可替换为你自己的模型）

## Prompt

打开 Codex App，新建会话，输入：

```
我想要用我家宠物生成一个桌面电子宠物，我家宠物的照片已经在 ~/Downloads/cheese
这个文件夹下了，有 face look 也有 body 照片, 这是一只短腿胖乎乎的蓝白英短,
你要按照 codex APP 的宠物的要求来帮我生成哦，生成的宠物要保留真实宠物的毛流感
和神态，不要过于动画化。你生成的 base 图片要先给我评审，我认可了你再继续图像生成。
```

> **提示：** Codex CLI（`codex` 命令行）也支持同样的 prompt。

## 背后发生了什么

Codex 使用内置的 `hatch-pet` 技能，自动编排整个生成流水线：

### 阶段 1：初始化 & 照片分析

1. 读取你的照片文件夹，识别参考图片
2. 创建工作目录（如 `~/Downloads/cheese/hatch-pet-run-codex/`）
3. 将参考图复制到 `references/` 并调整尺寸适配 API
4. 分析宠物特征，生成 `pet_request.json` — 记录宠物描述、色键选择、图集规格等

### 阶段 2：Base 宠物生成（带审核门控）

5. 编写 `prompts/base-pet.md` — 权威精灵图规格：
   - 宠物描述（来自照片分析 + 你的文字说明）
   - 风格合约（像素风、Q版、粗描边、平面着色）
   - 色键背景色
6. 调用 `$imagegen`（gpt-image-2），传入参考照片 + prompt
7. **展示 base 精灵图供你审核** — 这是你要求的评审环节

此时你会看到类似这样的信息：

```
这是 Cheese 的 base 精灵图。风格是像素风 Q版：
- 灰蓝色头顶和脸颊，白色口鼻
- 圆圆的琥珀色眼睛，粉色鼻头
- 短腿、矮胖紧凑的身体
- 纯绿色 #00FF00 色键背景

你看效果可以吗？我可以调整后再继续。
```

如果不满意，可以要求修改（多轮迭代很正常）：

```
脸部花色不太像，请参考真实照片的灰色面具 + 白色鼻梁，
毛流要更明显一些，不要太光滑像橡胶玩具
```

每次修改会生成一个变体保存到 `previews/` — Cheese 经过了 5 个版本：
- `cheese-base-v1.png` — 初始版本
- `cheese-base-v2-furflow.png` — 增加毛流纹理
- `cheese-base-v3-unobstructed-furflow.png` — 解除面部遮挡
- `cheese-base-v4-balanced-fur.png` — 平衡毛发细节
- `cheese-base-v5-v1-face-softened-v2-fur.png` — 最终通过 ✓

### 阶段 3：动画行生成

Base 通过后，Codex 逐行生成动画。图集规格 1536×1872（8列 × 9行，每格 192×208）：

| 行 | 状态 | 帧数 | 说明 |
|----|------|------|------|
| 0 | idle | 6 | 呼吸/眨眼待机循环 |
| 1 | running-right | 8 | 向右跑 |
| 2 | running-left | 8 | 向左跑（镜像翻转第1行） |
| 3 | waving | 4 | 挥手打招呼 |
| 4 | jumping | 5 | 跳跃弧线 |
| 5 | failed | 8 | 失败/沮丧反应 |
| 6 | waiting | 6 | 耐心等待 |
| 7 | running | 6 | 忙碌工作中 |
| 8 | review | 6 | 审查/查看 |

每行生成时输入：
- 所有参考照片作为身份锚点
- 审核通过的 base 精灵图作为身份参考
- 帧槽位布局引导图
- 行专用动画 prompt

`running-left` 使用镜像策略 — 直接水平翻转 `running-right`（如果宠物没有左右不对称的标记，则无需额外生成）。

### 阶段 4：组装 & 验证

8. 从每行条带中提取单帧（去除色键 → 透明 PNG）
9. 将所有帧组装为最终 `spritesheet.png` / `spritesheet.webp`
10. 生成 QA 总览图和验证报告
11. 创建 `pet.json` 配置清单

## 输出目录结构

```
~/Downloads/cheese/hatch-pet-run-codex/
├── pet_request.json          # 完整生成配置
├── imagegen-jobs.json        # 任务追踪（状态、sha256 等）
├── prompts/
│   ├── base-pet.md           # Base 精灵图 prompt
│   ├── variants/             # 修改版 prompt（v2, v3, ...）
│   └── rows/                 # 每行动画 prompt
├── references/
│   ├── reference-01..05.jpg  # 你的宠物照片（已复制）
│   ├── canonical-base.png    # 审核通过的 base 精灵图
│   ├── api-sized/            # 调整尺寸后的 API 版本
│   └── layout-guides/        # 帧槽位引导图
├── previews/                 # Base 精灵图各版本迭代
├── decoded/                  # 各行条带 PNG
│   ├── base.png
│   ├── idle.png
│   ├── running-right.png
│   └── ...
├── frames/                   # 提取后的逐帧 PNG
│   ├── idle/00.png..05.png
│   ├── running-right/00.png..07.png
│   └── ...
├── qa/
│   ├── contact-sheet.png     # 全帧概览图
│   ├── review.json           # 帧验证报告
│   ├── run-summary.json
│   └── videos/               # 各状态预览动画
└── final/
    ├── spritesheet.png       # 最终图集（PNG）
    ├── spritesheet.webp      # 最终图集（WebP 无损）
    └── validation.json
```

## 安装宠物

生成完成后：

```bash
# 复制到 Codex 宠物目录
mkdir -p ~/.codex/pets/cheese
cp final/spritesheet.webp ~/.codex/pets/cheese/
cat > ~/.codex/pets/cheese/pet.json << 'EOF'
{
  "id": "cheese",
  "displayName": "Cheese",
  "description": "A short-legged, chubby blue-and-white British Shorthair cat.",
  "spritesheetPath": "spritesheet.webp"
}
EOF
```

重启 Codex → **Settings > Appearance > Pets** → 选择 Cheese。

或使用本仓库的安装脚本：

```bash
./install.sh
```

## 经验提示

- **参考照片越多，身份还原越好。** Cheese 用了 5 张照片（2张脸、3张身体）— 模型看到的角度越多，越不会臆造特征。
- **修改反馈要具体。** "不像"太模糊 — 请说清楚哪里不对："灰色面具范围不对"、"眼睛太大像动漫了"。
- **Base 精灵图是最重要的一步。** 所有动画行都从它继承身份，所以值得花时间打磨。
- **色键自动选择**以避免与宠物配色冲突。Cheese 用绿色 `#00FF00`（不是洋红）因为蓝灰色猫不含绿色调。
- **生成模型很重要。** `gpt-image-2` 对像素风 Q版风格 + 参考图锚定生成效果不错。换成你有的模型即可。
