# 童梦工坊 — 部署与设置指南

## 快速部署（5分钟上线）

### 方案1：Vercel（推荐，免费）
1. 安装 Vercel CLI：`npm i -g vercel`
2. 在项目目录运行：`vercel`
3. 或者直接把项目文件夹拖到 [vercel.com/new](https://vercel.com/new)

### 方案2：Netlify（免费）
1. 打开 [netlify.com/drop](https://app.netlify.com/drop)
2. 把 `index.html` 拖进去

### 方案3：直接本地打开
双击 `index.html` 即可在浏览器中预览

---

## 设置表单（重要！不然数据收不到）

### 方案A：Formspree（推荐，免费50次/月）
1. 打开 [formspree.io](https://formspree.io) 注册
2. 创建新表单，获得表单 ID（类似 `xyzabc`）
3. 修改 `index.html` 第 358 行附近这段代码：

```html
// 替换 WEBHOOK_URL 为空字符串
const WEBHOOK_URL = '';
// 改为：
const WEBHOOK_URL = 'https://formspree.io/f/你的表单ID';
```

4. 每次有人提交，Formspree 会发邮件通知你

### 方案B：Google Sheets（免费，无限次）
1. 打开 [sheets.new](https://sheets.new) 创建新表格
2. 第一行填入：`家长姓名`, `邮箱`, `孩子姓名`, `孩子年龄`, `主题`, `留言`, `时间`
3. 打开 扩展程序 → Apps Script
4. 粘贴以下代码：

```javascript
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = JSON.parse(e.postData.contents);
  sheet.appendRow([
    data.parentName,
    data.email,
    data.childName,
    data.childAge,
    data.theme,
    data.message,
    data.timestamp
  ]);
  return ContentService.createTextOutput(JSON.stringify({success: true}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

5. 部署 → 新建部署 → 选择"网页应用" → 执行身份选"任何人" → 部署
6. 复制生成的 URL，填入 `index.html` 的 `WEBHOOK_URL`

### 方案C：直接收邮件（最简单）
不改代码。数据会自动保存在浏览器 localStorage 里。你打开页面后按 F12 → 控制台输入：

```javascript
console.log(JSON.parse(localStorage.getItem('dreamkids_waitlist')));
```

就能看到所有提交记录。缺点是换电脑就看不到。

---

## 个性化修改

### 改公司名
搜索 `童梦工坊`，全部替换为你想要的名字

### 改定价
搜索 `¥399`、`¥699`、`¥1,299` 修改

### 改联系方式
页面目前没有留联系方式，如需添加，在 footer 区域加：

```html
<p style="margin-top:8px;font-size:0.85rem;color:var(--text-light);">
  微信：你的微信号 | 邮箱：your@email.com
</p>
```

---

## 第一周行动清单

1. **今天**：部署上线，设置 Formspree
2. **Day 1-2**：给自己或朋友孩子做一本免费 demo
3. **Day 3**：注册小红书账号，发第一条笔记
4. **Day 4-7**：每天发 1 条，观察反馈，收集前 3 个候补
5. **第一单目标**：¥399，手工交付，记录全流程耗时

---

## 成本预估

| 项目 | 月费 |
|------|------|
| ChatGPT Pro | ¥145 |
| Midjourney | ¥620 |
| Vercel/Netlify 托管 | 免费 |
| Formspree | 免费（50次/月） |
| **总计** | **¥765/月** |

接 2 单 ¥699 精装版即可回本并盈利。
