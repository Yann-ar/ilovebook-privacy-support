# ilovebook 隐私政策与使用条款

开发者／运营者：Yann
联系邮箱：yesiyang@outlook.com
生效日期：2026年10月4日

- [隐私政策](https://yann-ar.github.io/ilovebook-privacy-support/privacy/)
- [使用条款](https://yann-ar.github.io/ilovebook-privacy-support/terms/)
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
