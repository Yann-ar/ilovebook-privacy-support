#!/usr/bin/env python3
"""Generate the app's public legal pages, or check that every mirror is current."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Booka" / "LegalDocuments.json"
OUTPUT = ROOT / "PublicSite"
if not SOURCE.exists():
    SOURCE = ROOT / "content" / "legal-documents.json"
    OUTPUT = ROOT

STYLES = """
:root{color-scheme:light dark;--canvas:#f2f2f7;--surface:#fff;--ink:#17171a;--muted:#5c5c65;--line:#d8d8df;--accent:#1762c4;--soft:#eaf1fc}
*{box-sizing:border-box}body{margin:0;background:var(--canvas);color:var(--ink);font:17px/1.85 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow-wrap:anywhere}
a{color:var(--accent);text-underline-offset:.2em}a:focus-visible{outline:3px solid var(--accent);outline-offset:4px;border-radius:4px}
.skip{position:absolute;left:12px;top:-100px;padding:10px;background:var(--surface)}.skip:focus{top:12px}
.topbar{max-width:920px;margin:auto;padding:24px 24px 12px;display:flex;gap:20px;justify-content:space-between;align-items:center;flex-wrap:wrap}
.brand{font-size:20px;font-weight:700;text-decoration:none;color:var(--ink)}nav{display:flex;gap:20px;flex-wrap:wrap}nav a{padding:8px 0;text-decoration:none;font-size:15px}nav [aria-current=page]{font-weight:700}
main{max-width:768px;margin:auto;padding:20px 24px 60px}.terms{--accent:#6752b3;--soft:#f0edfa}
.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,var(--soft),var(--surface));border:1px solid var(--line);border-radius:26px;padding:30px}
.hero-mark,.highlight-mark{color:var(--accent);background:var(--soft);border-radius:13px;display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px}
.hero-mark svg{width:25px;height:25px}.eyebrow{color:var(--accent);font-size:12px;font-weight:700;letter-spacing:.1em;margin:15px 0 7px}
h1{font-size:clamp(30px,5vw,38px);line-height:1.3;margin:0 0 12px}h2{font-size:21px;line-height:1.5;margin:0}p{margin:0 0 16px}p:last-child{margin-bottom:0}.subtitle{color:var(--muted);max-width:620px}.date{display:inline-block;background:var(--surface);border-radius:99px;padding:6px 12px;font-size:13px;color:var(--muted);margin-top:18px}
.glance{margin:26px 0}.glance>h2{font-size:18px;margin-bottom:12px}.highlights{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.highlight{background:var(--surface);border-radius:18px;padding:16px}.highlight-mark{width:32px;height:32px;border-radius:9px;font-size:13px;font-weight:700}.highlight h3{font-size:16px;line-height:1.5;margin:10px 0 6px}.highlight p{font-size:14px;line-height:1.7;color:var(--muted)}
.section,.contact{padding:24px;background:var(--surface);border-radius:22px;margin:24px 0}.section h2{display:flex;gap:11px;align-items:baseline;margin-bottom:18px}.number{background:var(--soft);color:var(--accent);display:inline-flex;justify-content:center;align-items:center;font-size:12px;min-width:28px;height:28px;border-radius:50%}.section-body{padding-left:39px}.section ul{padding:18px 18px 18px 38px;background:var(--soft);border-radius:16px;margin:18px 0 0}.section li+li{margin-top:10px}
.contact h2{margin-bottom:12px}.contact p{font-size:14px;color:var(--muted)}.action{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--soft);color:var(--accent);padding:12px 16px;border-radius:13px;min-height:44px;margin:12px 0;text-decoration:none;font-size:15px;font-weight:600}.references{border-top:1px solid var(--line);margin-top:22px;padding-top:16px}.references a{display:block;padding:9px 0;font-size:14px;min-height:44px}
footer{max-width:768px;margin:0 auto;padding:0 24px 40px;font-size:13px;color:var(--muted)}footer p+p{margin-top:8px}.home-links{margin-top:24px;display:grid;gap:14px}.home-links a{display:block;padding:24px;background:var(--surface);border-radius:20px;text-decoration:none}.home-links strong{display:block;font-size:21px}.home-links span{display:block;color:var(--muted);font-size:15px;margin-top:5px}
@media(max-width:560px){.topbar{padding:16px 18px 8px}main{padding:16px 18px 40px}.hero{padding:24px}.highlights{grid-template-columns:1fr}.section,.contact{padding:20px}.section-body{padding-left:0}.section h2{font-size:20px}}
@media(prefers-color-scheme:dark){:root{--canvas:#000;--surface:#1c1c1e;--ink:#f5f5f7;--muted:#b4b4bf;--line:#38383d;--accent:#83b2ff;--soft:#1c2c47}.terms{--accent:#c0b2ff;--soft:#2b2545}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

def esc(value):
    return html.escape(str(value), quote=True)

def icon(kind):
    path = (
        '<path d="M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6l-8-3Z"/><path d="m8 12 3 3 5-6"/>'
        if kind == "privacy" else
        '<path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v5h4M9 12h6M9 16h6"/>'
    )
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">' + path + '</svg>'

def public_url(data, kind=""):
    return data["publicSiteURL"].rstrip("/") + "/" + (kind + "/" if kind else "")

def shell(data, title, body, current=""):
    base = urlsplit(data["publicSiteURL"]).path.rstrip("/")
    nav = "".join(
        f'<a href="{esc(base)}/{kind}/"' + (' aria-current="page"' if current == kind else "") +
        f'>{esc(label)}</a>' for kind, label in [("privacy", "隐私政策"), ("terms", "使用条款")]
    )
    return f"""<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>{esc(title)} · {esc(data["appName"])}</title>
<meta name="description" content="ilovebook 的隐私政策、使用条款和联系方式。">
<link rel="canonical" href="{esc(public_url(data, current))}"><link rel="stylesheet" href="{esc(base)}/assets/styles.css"></head>
<body><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="{esc(base)}/">{esc(data["appName"])}</a><nav aria-label="法律文件">{nav}</nav></header>
<main id="main" class="{esc(current)}">{body}</main><footer><p>开发者／运营者：{esc(data["operatorName"])} · <a href="mailto:{esc(data["supportEmail"])}">{esc(data["supportEmail"])}</a></p>
<p>本网站没有我们添加的广告、统计脚本或 Cookie。GitHub Pages 托管方的数据处理适用 <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub 隐私声明</a>。</p></footer></body></html>
"""

def document_page(data, document):
    kind = document["id"]
    hero = f'<header class="hero"><span class="hero-mark">{icon(kind)}</span><p class="eyebrow">{esc(document["eyebrow"])}</p><h1>{esc(document["title"])}</h1><p class="subtitle">{esc(document["subtitle"])}</p><span class="date">生效日期：{esc(data["effectiveDate"])}</span></header>'
    cards = "".join(
        f'<div class="highlight"><span class="highlight-mark" aria-hidden="true">{i:02}</span><h3>{esc(item["title"])}</h3><p>{esc(item["detail"])}</p></div>'
        for i, item in enumerate(document["highlights"], 1)
    )
    body = hero + f'<section class="glance" aria-labelledby="glance-title"><h2 id="glance-title">一览</h2><div class="highlights">{cards}</div></section>'
    for i, section in enumerate(document["sections"], 1):
        paragraphs = "".join(f'<p>{esc(p)}</p>' for p in section["paragraphs"])
        bullets = "<ul>" + "".join(f'<li>{esc(b)}</li>' for b in section["bullets"]) + "</ul>" if section["bullets"] else ""
        body += f'<section class="section" aria-labelledby="section-{i}"><h2 id="section-{i}"><span class="number" aria-hidden="true">{i:02}</span>{esc(section["title"])}</h2><div class="section-body">{paragraphs}{bullets}</div></section>'
    references = "".join(f'<a href="{esc(ref["url"])}" rel="noopener noreferrer">{esc(ref["title"])} ↗</a>' for ref in data["references"])
    body += f'<section class="contact" aria-labelledby="contact-title"><h2 id="contact-title">联系与公开版本</h2><p>开发者／运营者：{esc(data["operatorName"])}</p><a class="action" href="mailto:{esc(data["supportEmail"])}">{esc(data["supportEmail"])} <span aria-hidden="true">↗</span></a><a class="action" href="{esc(public_url(data, kind))}">查看公开{esc(document["title"])} <span aria-hidden="true">↗</span></a><p>应用内文档随当前版本提供；公开网站公布最新版本。</p><div class="references">{references}</div></section>'
    return shell(data, document["title"], body, kind)

def markdown(data, document):
    lines = [f'# {data["appName"]} {document["title"]}', "", f'生效日期：{data["effectiveDate"]}', "", document["subtitle"], "", "## 一览", ""]
    lines += [f'- **{item["title"]}**：{item["detail"]}' for item in document["highlights"]]
    for i, section in enumerate(document["sections"], 1):
        lines += ["", f'## {i:02} {section["title"]}', ""]
        for paragraph in section["paragraphs"]:
            lines += [paragraph, ""]
        lines += [f'- {bullet}' for bullet in section["bullets"]]
    lines += ["", "## 联系与参考", "", f'开发者／运营者：{data["operatorName"]}', "", f'联系邮箱：{data["supportEmail"]}', "", f'[公开版本]({public_url(data, document["id"])})', ""]
    lines += [f'- [{ref["title"]}]({ref["url"]})' for ref in data["references"]]
    return "\n".join(lines) + "\n"

def generated_files():
    source_bytes = SOURCE.read_bytes()
    data = json.loads(source_bytes)
    if {doc["id"] for doc in data["documents"]} != {"privacy", "terms"}:
        raise ValueError("Both privacy and terms are required.")
    files = {
        "content/legal-documents.json": source_bytes,
        "assets/styles.css": STYLES.encode("utf-8"),
        ".nojekyll": b"",
        ".gitignore": b".DS_Store\n__pycache__/\n",
        "scripts/generate-legal-site.py": Path(__file__).read_bytes(),
    }
    links = "".join(
        f'<a href="{esc(public_url(data, doc["id"]))}"><strong>{esc(doc["title"])} →</strong><span>{esc(doc["subtitle"])}</span></a>' for doc in data["documents"]
    )
    home = f'<header class="hero"><p class="eyebrow">ILOVEBOOK · LEGAL</p><h1>整理藏书，安心阅读。</h1><p class="subtitle">了解 ilovebook 如何保存资料、何时联网，以及应用的使用规则。</p><span class="date">生效日期：{esc(data["effectiveDate"])}</span></header><div class="home-links">{links}</div>'
    files["index.html"] = shell(data, "隐私与使用说明", home).encode("utf-8")
    for document in data["documents"]:
        files[f'{document["id"]}/index.html'] = document_page(data, document).encode("utf-8")
        files[f'{document["id"]}/index.md'] = markdown(data, document).encode("utf-8")
    files["README.md"] = f"""# ilovebook 隐私政策与使用条款

开发者／运营者：{data["operatorName"]}
联系邮箱：{data["supportEmail"]}
生效日期：{data["effectiveDate"]}

- [隐私政策]({public_url(data, "privacy")})
- [使用条款]({public_url(data, "terms")})
- [隐私政策 Markdown](privacy/index.md)
- [使用条款 Markdown](terms/index.md)

这是独立的公开法律资料仓库，只保存正文、静态网页和生成脚本。

## 内容同步

正文来源为 [content/legal-documents.json](content/legal-documents.json)。App 使用同一份 JSON 的本机副本，支持离线阅读。两端的正文、生效日期和联系方式应同时更新。

在 App 工程中，编辑 Booka/LegalDocuments.json 后运行 scripts/generate-legal-site.py，会更新 PublicSite 中的网页、Markdown 与正文副本。再把 PublicSite 的改动提交到本仓库。

在此仓库单独工作时：

```sh
python3 scripts/generate-legal-site.py
python3 scripts/generate-legal-site.py --check
```

如果在此仓库修改正文，需要把 content/legal-documents.json 同步回 App 工程的 Booka/LegalDocuments.json 后重新构建应用。

## GitHub Pages

从 main 分支的根目录发布。网页采用仓库路径前缀，支持窄屏、深色模式和键盘导航，无外部字体、JavaScript、广告或分析代码。

## 维护依据

正文按应用实际的本机存储、自动在线查书、封面补全与阅读计时行为编写。改变联网服务、权限、收费、同步或数据删除方式时，应重新核对和更新正文。

参考 [Apple 审核指南 5.1](https://developer.apple.com/app-store/review/guidelines/#privacy) 与 [Apple 标准许可协议](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/)。文档的发布与界面验证不代表完整的应用发布或全球法律适用性审查。
""".encode("utf-8")
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale files without writing.")
    args = parser.parse_args()
    files = generated_files()
    stale = []
    for name, data in files.items():
        path = OUTPUT / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if stale:
        raise SystemExit("Out of date: " + ", ".join(stale))
    print(("Verified" if args.check else "Generated") + f" {len(files)} legal site files.")

if __name__ == "__main__":
    main()
