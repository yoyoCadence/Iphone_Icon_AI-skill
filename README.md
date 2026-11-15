# iphone-icon — a Claude skill that designs real home-screen icons for web apps

[English](#english) · [繁體中文](#繁體中文)

![examples](assets/examples/gallery.png)

---

## English

Give Claude a web page (or just a description of the app) and get back an iPhone home-screen icon
that was **designed** — metaphor, material, light, palette — rather than a shape dropped on a
gradient. The skill also renders every size iOS/Android need, shows the icon on a simulated home
screen before calling it done, and wires the `<head>` tags and `manifest.webmanifest`.

### What you get
```
icon.svg                      editable 1024 master
icons/apple-touch-icon.png    180×180 — the file iOS actually uses
icons/icon-512.png · icon-192.png · icon-1024.png
icons/preview.png             the icon on dark + light home screens, at 60/40/29/20pt
manifest.webmanifest          + a managed block in your HTML <head>
```

### Install (Claude Code)
```bash
# personal skill — available in every project
git clone https://github.com/yoyoCadence/Iphone_Icon_AI-skill.git ~/.claude/skills/iphone-icon
```
```bash
# or project skill — committed with one repo
git clone https://github.com/yoyoCadence/Iphone_Icon_AI-skill.git .claude/skills/iphone-icon
```
Rendering needs Node ≥ 18 with Playwright's Chromium (one-time):
```bash
npm i -g playwright && npx playwright install chromium
```
```bash
pip install pillow
```
Without Playwright the renderer falls back to `rsvg-convert` / ImageMagick (filters degrade) and
the preview sheet is skipped. For claude.ai, zip this folder (SKILL.md at the zip root) and upload
it under *Settings → Capabilities → Skills*.

### Use
Just ask, in any language:
- "Make an icon for this page so people can add it to their iPhone home screen."
- "My PWA is called Swell, surf forecasts, brand colour #0E7490 — I need the apple-touch-icon and manifest icons."
- "幫我這個記帳網頁做一個加到主畫面用的 icon，不要幾何圖形那種。"

Claude will write a six-line concept note, build the SVG, render it, **look at the preview**,
revise, then inject the tags. Expect one or two revision rounds — that is the process working,
not failing.

### How it works
1. **Brief** — name (≤ 11 chars), purpose, tone, brand colours; `extract_brand.py` pulls them from your HTML/CSS.
2. **Concept** — metaphor ladder (object → action → feeling → letter), three tests: readable at 29pt, ownable, no collision with famous icons.
3. **Style** — one of seven recipes (lit glyph, rendered object, liquid glass, layered paper, luminous, monogram, horizon scene), each with SVG lighting rigs.
4. **Render → critique** — `render.js` produces the PNG set and a home-screen preview; `validate.py` checks transparency, glyph extent, corner intrusion, contrast and tonal depth; Claude reads the preview and fixes what it sees.
5. **Deliver** — `inject.py` writes the head block (cache-busted) and the manifest; explains the standalone-mode trade-off.

### Scripts (usable on their own)
| | |
|---|---|
| `node scripts/render.js icon.svg --out icons --label "Name" --grid` | SVG → PNG set + preview sheet (+ grid overlay) |
| `python3 scripts/validate.py icons/icon-1024.png` | mechanical checks, advisory |
| `python3 scripts/inject.py index.html --name "Name" --theme "#0a2838"` | head tags + manifest, idempotent |
| `python3 scripts/extract_brand.py index.html styles.css` | title, colours, fonts, copy |

### FAQ
**The icon on my phone didn't change.** iOS caches web-clip icons by URL and never refreshes an
existing shortcut. `inject.py` adds `?v=<hash>`; remove the shortcut and add it again.

**Black corners / a black square.** The PNG had transparency. iOS composites over black. The tile
must be full-bleed; `validate.py` flags this.

**Double rounded corners.** Rounding was baked into the PNG. Keep it square — iOS applies the mask.

**Can it match my existing logo?** Yes — put the logo SVG/PNG in the project and say so; the skill
will treat it as the glyph and build the material and tile around it.

---

## 繁體中文

把網頁（或只是一句話描述你的 app）交給 Claude，拿回一個**真正被設計過**的 iPhone 主畫面圖示——
有隱喻、有材質、有光線、有配色，而不是「一個幾何圖形放在漸層上」。這個 skill 同時會輸出 iOS /
Android 需要的所有尺寸、先把圖示放到模擬的主畫面上檢查，再把 `<head>` 標籤與
`manifest.webmanifest` 接到你的網頁。

### 你會拿到
```
icon.svg                      可編輯的 1024 母檔
icons/apple-touch-icon.png    180×180 —— iOS 真正讀取的檔案
icons/icon-512.png · icon-192.png · icon-1024.png
icons/preview.png             圖示在深色／淺色主畫面、60/40/29/20pt 的預覽
manifest.webmanifest          + HTML <head> 內一段受管理的標籤區塊
```

### 安裝（Claude Code）
```bash
# 個人 skill——所有專案都能用
git clone https://github.com/yoyoCadence/Iphone_Icon_AI-skill.git ~/.claude/skills/iphone-icon
```
```bash
# 或專案 skill——跟著單一 repo 走
git clone https://github.com/yoyoCadence/Iphone_Icon_AI-skill.git .claude/skills/iphone-icon
```
出圖需要 Node ≥ 18 與 Playwright 的 Chromium（只需一次）：
```bash
npm i -g playwright && npx playwright install chromium
```
```bash
pip install pillow
```
沒有 Playwright 時會退回 `rsvg-convert` / ImageMagick（濾鏡效果會打折，且不產生預覽圖）。
在 claude.ai 使用：把這個資料夾壓成 zip（SKILL.md 在 zip 根目錄），到
*Settings → Capabilities → Skills* 上傳。

### 使用
直接用自然語言說：
- 「幫我這個網頁做一個加到主畫面用的 icon。」
- 「我的 PWA 叫 Swell，衝浪預報，品牌色 #0E7490，需要 apple-touch-icon 和 manifest 的圖。」
- 「幫我這個記帳網頁做 icon，不要幾何圖形那種。」

Claude 會先寫一段六行的概念筆記 → 寫 SVG → 出圖 → **看預覽** → 修一輪 → 注入標籤。
通常會有一到兩輪修改，這是流程在運作，不是出錯。

### 運作方式
1. **需求**：名稱（≤ 11 字）、用途、調性、品牌色；`extract_brand.py` 會從 HTML/CSS 抓出來。
2. **概念**：隱喻階梯（物件 → 動作 → 感受 → 字母），三個檢驗：29pt 看得懂、換成競品會被發現、不撞知名 icon。
3. **風格**：七種配方（受光字形、實體物件、液態玻璃、層疊紙張、發光線條、單字母、地平線場景），每種附 SVG 打光骨架。
4. **出圖 → 審視**：`render.js` 產生 PNG 與主畫面預覽；`validate.py` 檢查透明、字形比例、角落侵入、對比、層次；Claude 看圖修圖。
5. **交付**：`inject.py` 寫入 head 區塊（含快取破壞參數）與 manifest，並說明 standalone 模式的取捨。

### 常見問題
**手機上的圖示沒更新。** iOS 以 URL 快取 web clip 圖示，且既有捷徑永遠不會自己刷新。
`inject.py` 會加上 `?v=<hash>`；請移除捷徑再重新加入。

**角落是黑的／整個變黑方塊。** PNG 有透明區域，iOS 會把它疊在黑色上。底圖必須滿版；`validate.py` 會警告。

**圓角變成兩層。** PNG 裡已經烤進圓角。保持方形——遮罩由 iOS 套用。

**能用我現有的 logo 嗎？** 可以——把 logo 的 SVG/PNG 放進專案並說明，skill 會把它當作主字形，再圍繞它建立材質與底圖。

---

MIT License · built with the Claude skill-creator workflow; evals live in `evals/`.
