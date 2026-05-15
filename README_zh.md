# 🐾 桌面宠物

[English](./README.md) | [中文](./README_zh.md)

我的自定义桌面宠物，适用于 [Codex](https://openai.com/codex) 和 [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk)。

## 宠物列表

| 名称 | 描述 |
|------|------|
| **baby-potato** | 香槟色泰迪熊风格的比熊贵宾混血（幼年版） |
| **child-potato** | 香槟色泰迪熊风格的比熊贵宾混血（成年版） |
| **cheese** | 矮脚胖脸的蓝白英短猫 |
| **Yuanbao** | 蓬松奶油金色长毛猫 |

## 仓库结构

```
<宠物名>/
├── codex/
│   ├── pet.json            # Codex 宠物配置文件
│   └── spritesheet.webp    # 1536×1872 精灵图集（8×9 网格，每帧 192×208）
├── clawd-on-desk/
│   ├── theme.json           # Clawd on Desk 主题配置
│   ├── assets/              # 各状态的 APNG 动画
│   ├── *-contact-sheet.png  # 参考总览图
│   └── codex-spritesheet-source.webp
└── source/
    └── <hatch-run-name>/    # 原始 hatch-pet 生成素材
        ├── pet_request.json     # 生成请求配置
        ├── imagegen-jobs.json   # 图片生成任务记录
        ├── prompts/             # 生成用的提示词
        ├── references/          # 参考图片
        ├── decoded/             # 解码后的单行图片
        ├── frames/              # 帧提取数据
        ├── qa/                  # QA 总览图和审核数据
        └── final/               # 最终精灵图输出
```

## 一键安装（macOS）

```bash
./install.sh
```

该脚本会将宠物复制到：
- **Codex:** `~/.codex/pets/<宠物名>/`
- **Clawd on Desk:** `~/Library/Application Support/clawd-on-desk/themes/<宠物名>/`

安装后重启对应 App 即可看到宠物。

## 手动安装

### Codex App

将 `codex/` 目录内容复制到 `~/.codex/pets/<宠物名>/`：

```bash
cp -r baby-potato/codex/ ~/.codex/pets/baby-potato/
```

重启 Codex 后，通过 **Settings > Appearance > Pets** 激活，或在编辑器中输入 `/pet`。

**所需文件：**

| 文件 | 说明 |
|------|------|
| `pet.json` | 配置清单，包含 id、displayName、description、spritesheetPath |
| `spritesheet.webp` | 1536×1872 px，8 列 × 9 行（每格 192×208），透明背景 |

<details>
<summary><b>精灵图行布局</b></summary>

| 行 | 状态 | 帧数 |
|----|------|------|
| 0 | idle（待机） | 6 |
| 1 | running-right（向右跑） | 8 |
| 2 | running-left（向左跑） | 8 |
| 3 | waving（挥手） | 4 |
| 4 | jumping（跳跃） | 5 |
| 5 | failed（失败） | 8 |
| 6 | waiting（等待） | 6 |
| 7 | running/busy（忙碌） | 6 |
| 8 | review（审查） | 6 |

</details>

### Clawd on Desk

将 `clawd-on-desk/` 目录内容复制到 `~/Library/Application Support/clawd-on-desk/themes/<宠物名>/`：

```bash
cp -r baby-potato/clawd-on-desk/ ~/Library/Application\ Support/clawd-on-desk/themes/baby-potato/
```

重启 Clawd on Desk 后，在 App 内 **Settings > Theme** 激活。

**所需文件：**

| 文件 | 说明 |
|------|------|
| `theme.json` | 主题配置（schemaVersion、name、viewBox、states 等） |
| `assets/` | 各状态动画文件（APNG/GIF/WebP/SVG） |

<details>
<summary><b>动画状态列表</b></summary>

| 状态 | 说明 |
|------|------|
| idle | 默认待机呼吸/眨眼循环 |
| thinking | 思考/等待响应 |
| working | 工作中（打字、搭建、抛球、指挥、打扫、搬运） |
| error | 出错/难过 |
| attention | 开心/打招呼 |
| notification | 通知提醒 |
| sleeping | 深度睡眠 |
| waking | 醒来过渡 |
| yawning | 打哈欠（入睡前） |
| dozing | 浅睡 |
| collapsing | 倒下入睡过渡 |

**支持格式：** SVG（最佳眼球追踪）、APNG（最佳动画质量）、GIF、WebP、PNG、JPG

</details>

## 创建新宠物

### Codex

1. 制作 1536×1872 精灵图，9 行动画，透明背景
2. 编写 `pet.json`，填入 id、displayName、description
3. 将两个文件放入 `~/.codex/pets/<宠物名>/`

也可以使用内置的 hatch-pet 功能：输入 `/pet` 然后描述你想要的宠物。

**完整教程：** 参见 [examples/generate-pet-with-codex_zh.md](examples/generate-pet-with-codex_zh.md)，以 Cheese 为例展示从真实宠物照片生成桌面宠物的全流程（含评审门控）。

### Clawd on Desk

1. 在 clawd-on-desk 仓库中运行 `node scripts/create-theme.js <名称>`，或手动创建目录
2. 添加各动画状态的 APNG/GIF 素材
3. 配置 `theme.json`，设置 viewBox、状态映射和时间参数
4. 使用 `node scripts/validate-theme.js path/to/theme` 验证

最简主题只需 4 张图片（idle、thinking、working、sleeping），其他状态可用 `fallbackTo` 回退。

## 平台对比

| | Codex | Clawd on Desk |
|---|---|---|
| 安装路径 | `~/.codex/pets/<名称>/` | `~/Library/Application Support/clawd-on-desk/themes/<名称>/` |
| 配置文件 | `pet.json` | `theme.json`（schemaVersion 1） |
| 素材格式 | 单张精灵图（1536×1872，8×9 网格） | 每个状态独立的 APNG/GIF/SVG 文件 |
| 激活方式 | Settings > Pets 或 `/pet` | Settings > Theme |
| 最少素材 | 1 张精灵图 | 4 张图片（idle、thinking、working、sleeping） |

## License

个人使用。宠物美术素材为原创。
