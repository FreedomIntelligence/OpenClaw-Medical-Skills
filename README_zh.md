# OpenClaw Medical Skills — 医疗 AI 技能库

<p align="center">
  <a href="https://www.atlascloud.ai/?utm_source=github&utm_medium=link&utm_campaign=openclaw-medical-skills">
    <img src="assets/atlas-cloud-logo.png" alt="Atlas Cloud" width="140" />
  </a>
  <br />
  <sub><strong>Atlas Cloud</strong> Atlas Cloud provides OpenAI-compatible LLM APIs and async image/video generation APIs for medical agent skills and multimodal report workflows.</sub>
</p>


<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github&color=gold)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github&color=blue)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/FreedomIntelligence/OpenClaw-Medical-Skills?style=for-the-badge&logo=github)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/issues)
[![技能数量](https://img.shields.io/badge/技能数量-869-brightgreen?style=for-the-badge)](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills/tree/main/skills)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/平台-OpenClaw%20%7C%20NanoClaw-orange?style=for-the-badge)](https://github.com/openclaw/openclaw)

**最大的开源医疗 AI 技能库，专为 OpenClaw 框架设计。**

*869 个精选技能 · 临床医学 · 基因组学 · 药物发现 · 生物信息学 · 医疗器械*

[English](README.md) | [中文](#)

</div>

---

## 项目简介

**OpenClaw Medical Skills** 是一个包含 **869 个 AI Agent 技能**的精选集合，覆盖生物医学与临床研究的完整领域。这些技能专为 [OpenClaw](https://github.com/openclaw/openclaw) / [NanoClaw](https://github.com/qwibitai/nanoclaw) —— 基于 Claude 的个人 AI 助手框架 —— 设计，能将通用 AI 智能体转变为强大的医学与科研研究伙伴。

每个技能都是一个独立模块（`SKILL.md` 文件），它：
- 为 Agent 注入专业领域知识与工作流
- 连接真实的数据库、API 和计算工具
- 输出结构化的临床或科研相关结果

### 为什么需要这个技能库？

| 没有技能 | 配备 OpenClaw Medical Skills 后 |
|---|---|
| 对医学的通用 AI 回答 | 真实查询 PubMed / ClinicalTrials.gov / FDA |
| 无生物信息学能力 | RNA-seq、scRNA-seq、GWAS、变异注释流程 |
| 无药物情报 | ChEMBL、DrugBank、DDI 预测、药物警戒 |
| 无临床文档 | SOAP 记录、出院小结、预先授权决策 |
| 无基因组学支持 | VCF 注释、ACMG 分类、多基因风险评分 |
| 无法规指导 | FDA、CE 认证、IEC 62304、ISO 14971 合规 |

本集合整合了来自 **12 个以上**开源技能仓库的内容，涵盖学术研究工具、临床工作流、法规框架和前沿 AI 驱动的蛋白质设计——让您的 AI 智能体具备媲美专业研究科学家团队的能力。

---

## 安装方法

### 前置要求

- 已安装并运行 [OpenClaw](https://github.com/openclaw/openclaw)，或使用替代方案 [NanoClaw](https://github.com/qwibitai/nanoclaw)
- Git（用于克隆本仓库）

---

### OpenClaw 用户

OpenClaw 从以下两个位置加载技能：

| 优先级 | 路径 | 作用域 |
|---|---|---|
| 高 | `<workspace>/skills/` | 每个工作区独立（推荐） |
| 低 | `~/.openclaw/skills/` | 全局，所有 Agent 共享 |

#### 方法一 — 克隆并复制（推荐）

```bash
# 克隆本仓库
git clone https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git

# 安装到当前工作区的 skills 目录
cp -r OpenClaw-Medical-Skills/skills/* <your-workspace>/skills/

# 或安装到全局（所有 Agent 均可使用）
cp -r OpenClaw-Medical-Skills/skills/* ~/.openclaw/skills/
```

下次会话时技能自动生效，无需重启。

#### 方法二 — OpenClaw CLI

如果您使用 [OpenClaw 插件注册表](https://clawhub.com)，您可以搜索并安装单个技能。批量安装整个集合建议使用方法一。

```bash
openclaw plugins install <skill-slug>    # 安装单个技能
openclaw plugins update                  # 更新所有已安装技能
```

#### 方法三 — 配置额外技能目录

将本仓库的克隆路径永久配置到 `~/.openclaw/openclaw.json` 中：

```json
{
  "plugins": {
    "local": ["/path/to/OpenClaw-Medical-Skills"]
  }
}
```

这样无需复制文件，即可挂载整个技能集合。

#### 方法四 — 仅安装所需技能

按需选择与您领域相关的技能：

```bash
# 示例：临床 + 药物发现技能组合
SKILLS=(
  "clinical-reports"
  "tooluniverse-drug-research"
  "tooluniverse-pharmacovigilance"
  "clinicaltrials-database"
  "biomedical-search"
  "tooluniverse-drug-drug-interaction"
)

for skill in "${SKILLS[@]}"; do
  cp -r OpenClaw-Medical-Skills/skills/$skill ~/.openclaw/skills/
done
```

---

### NanoClaw 用户

NanoClaw 在容器启动时从 `container/skills/` 加载技能。

```bash
# 克隆并复制到 NanoClaw 容器技能目录
git clone https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git
cp -r OpenClaw-Medical-Skills/skills/* /path/to/nanoclaw/container/skills/

# 重建容器使技能生效
cd /path/to/nanoclaw
./container/build.sh
```

---

### 验证安装

安装完成后，向您的 Agent 提问：

```
你现在有哪些医疗和临床方面的技能？
```

Agent 应当列出已安装的技能及其功能说明。

---

## 技能总览

| 类别 | 数量 | 代表技能 |
|---|---|---|
| 通用与核心 | 10 | 浏览器/搜索、文档处理与开发工作流工具 |
| 医疗与临床 | 119 | 临床报告、决策支持、肿瘤学、影像与医疗 AI |
| 科学数据库 | 43 | 基因组/蛋白/药物数据库与生物医学检索 |
| 生物信息学 (gptomics bio-* 套件) | 239 | 变异分析、测序质控、差异表达、通路与单细胞分析 |
| 组学与计算生物学 | 59 | 单细胞/空间组学、蛋白质组、化学信息学与蛋白设计 |
| ClawBio 管道 | 21 | 面向 scRNA、GWAS、祖先分析与结构生物学的编排流程 |
| BioOS 扩展套件 | 285 | 覆盖肿瘤、免疫、临床 AI 与研究基础设施的扩展智能体 |
| 数据科学与工具 | 93 | 统计、可视化、自动化、模拟与科研工具链 |
| **总计** | **869** | |

---

## 目录导航

### 通用与核心
- [通用工具](#通用工具)

### 医疗与临床
- [医疗专用工具](#医疗专用工具)
- [药物安全与化学生物学](#药物安全与化学生物学)
- [医学影像与病理](#医学影像与病理)
- [医疗 ML 与临床 AI](#医疗-ml-与临床-ai)
- [心理健康与危机干预](#心理健康与危机干预)
- [健康与健康管理分析](#健康与健康管理分析)
- [医疗器械与监管](#医疗器械与监管)
- [医疗器械软件 (meddev-agent-skills)](#医疗器械与监管)

### 科学数据库
- [科学数据库（基因组与变异）](#科学数据库（基因组与变异）)
- [科学数据库（蛋白质、通路与药物）](#科学数据库（蛋白质、通路与药物）)
- [癌症基因组数据库](#癌症基因组数据库)
- [基因组与分子数据库](#基因组与分子数据库)
- [结构生物学与药物发现](#结构生物学与药物发现)

### 生物信息学 (gptomics)
- [生物信息学工具与流程](#生物信息学工具与流程)
- [生物信息 — 临床数据库与变异分析](#生物信息--临床数据库与变异分析)
- [生物信息 — 测序与读长质控](#生物信息--测序与读长质控)
- [生物信息 — 差异表达与转录组学](#生物信息--差异表达与转录组学)
- [生物信息 — 通路与网络分析](#生物信息--通路与网络分析)
- [生物信息 — 单细胞与空间组学](#生物信息--单细胞与空间组学)
- [生物信息 — 表观基因组学与染色质](#生物信息--表观基因组学与染色质)
- [生物信息 — 宏基因组学与微生物组](#生物信息--宏基因组学与微生物组)
- [生物信息 — 免疫信息学与流式细胞术](#生物信息--免疫信息学与流式细胞术)
- [生物信息 — 多组学整合](#生物信息--多组学整合)
- [生物信息 — 蛋白质组学与代谢组学](#生物信息--蛋白质组学与代谢组学)
- [生物信息 — 结构生物学与化学信息学](#生物信息--结构生物学与化学信息学)
- [生物信息 — 流行病学基因组学与因果基因组学](#生物信息--流行病学基因组学与因果基因组学)

### 组学与计算生物学
- [单细胞与空间组学](#单细胞与空间组学)
- [单细胞与轨迹分析](#单细胞与轨迹分析)
- [蛋白质组学与质谱](#蛋白质组学与质谱)
- [化学信息学与药物发现](#化学信息学与药物发现)
- [蛋白质结构与设计](#蛋白质结构与设计)
- [系统发育与网络分析](#系统发育与网络分析)

### ClawBio 管道
- [生物信息学编排与管道 (ClawBio)](#生物信息学编排与管道-clawbio)
- [基因组学、祖先分析与药物基因组学 (ClawBio)](#基因组学、祖先分析与药物基因组学-clawbio)
- [结构生物学与文献综合 (ClawBio)](#结构生物学与文献综合-clawbio)

### BioOS 扩展套件
- [BioOS 扩展生物信息工具套件](#bioos-扩展生物信息工具套件)
- [肿瘤学与精准医学智能体 (BioOS)](#肿瘤学与精准医学智能体-21个)
- [血液学与血液病 (BioOS)](#血液学与血液病-7个)
- [免疫学与细胞治疗 (BioOS)](#免疫学与细胞治疗-9个)
- [单细胞与空间组学智能体 (BioOS)](#单细胞与空间组学智能体-15个)
- [药物发现与分子设计 (BioOS)](#药物发现与分子设计-35个)
- [临床AI与医疗 (BioOS)](#临床ai与医疗-20个)
- [研究基础设施与智能体框架 (BioOS)](#研究基础设施与智能体框架-20个)

### 数据科学与工具
- [统计与数据分析](#统计与数据分析)
- [数据处理与科学计算](#数据处理与科学计算)
- [科学可视化与科研传播](#科学可视化与科研传播)
- [公共卫生与时序分析](#公共卫生与时序分析)
- [计算模拟与本体论](#计算模拟与本体论-heshamfsmaterials-simulation-skills-17个)
- [分析师人格](#分析师人格)
- [实验室自动化与集成](#实验室自动化与集成)
- [科学研究与写作](#科学研究与写作)
- [科学文献与参考管理](#科学文献与参考管理)
- [补充科学工具](#补充科学工具)
- [开发工作流技能](#开发工作流技能-obrasuperpowers-14个)

---

## 技能列表

## 🧰 通用与核心

<details open>
<summary>展开/收起该大类</summary>

### 通用工具

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [agent-browser](skills/agent-browser/) | 浏览器自动化。可用于网页研究、阅读文章、与网页应用交互、填写表单、截图、提取数据、测试网页等。任何需要浏览器的场景均可使用。 |
| [find-skills](skills/find-skills/) | 帮助用户发现和安装 Agent 技能。当用户询问"如何做 X"、"有没有能做 X 的技能"、"是否有 skill 可以……"或希望扩展 Agent 能力时触发。 |
| [multi-search-engine](skills/multi-search-engine/) | 多搜索引擎集成，支持 17 个引擎（8 个国内 + 9 个国际）。涵盖百度、Bing、360、搜狗、微信、Google、DuckDuckGo、WolframAlpha 等。支持高级搜索语法、时间过滤、站内搜索，无需 API Key。 |
| [wikipedia-search](skills/wikipedia-search/) | 通过 MediaWiki API 搜索并获取 Wikipedia 结构化内容，提供可靠的百科全书式信息。支持多语言查询。 |
| [deep-research](skills/deep-research/) | 自主多步骤深度研究。搜索多个信息来源，阅读全文，综合分析后生成结构化报告。适用于综合调研、文献综述、竞品分析或对某一主题的深度挖掘。 |
| [pdf](skills/pdf/) | 全功能 PDF 工具包——提取文本和表格、创建新 PDF、合并/拆分文档、填写表单、OCR 扫描件。处理任何 .pdf 文件时使用。 |
| [docx](skills/docx/) | 创建、编辑和分析 Word 文档（.docx）。支持修订追踪、批注、格式保留和文本提取。起草、审阅或提取 Word 文件内容时使用。 |
| [xlsx](skills/xlsx/) | 电子表格创建、编辑与分析。支持公式、格式设置、数据分析和可视化。处理任何 .xlsx、.xlsm、.csv 或 .tsv 文件时使用。 |
| [pptx](skills/pptx/) | 演示文稿创建、编辑与分析。支持布局、演讲者备注、模板和设计定制。处理任何 .pptx 文件时使用。 |
| [doc-coauthoring](skills/doc-coauthoring/) | 结构化文档协作撰写工作流。撰写文档、提案、技术规格、决策文件或类似结构化内容时使用。 |

</details>

</details>

## 🏥 医疗与临床

<details open>
<summary>展开/收起该大类</summary>

### 医疗专用工具

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [pubmed-search](skills/pubmed-search/) | 搜索 PubMed 科学文献。当用户要求查找论文、搜索文献、查询研究、查找出版物或询问近期研究时触发。 |
| [medical-research-toolkit](skills/medical-research-toolkit/) | 查询 14+ 个生物医学数据库，用于药物再利用、靶点发现、临床试验和文献研究。通过统一 MCP 端点访问 ChEMBL、PubMed、ClinicalTrials.gov、OpenTargets、OpenFDA、OMIM、Reactome、KEGG、UniProt 等数据库。 |
| [medical-specialty-briefs](skills/medical-specialty-briefs/) | 按医学专科生成每日或按需的医学研究简报。检索顶级期刊（NEJM、Lancet、JAMA、BMJ、Nature Medicine）最新研究，提供一句话要点摘要和直达链接。适用于内分泌、心脏病、肿瘤、神经等专科的医学资讯查询。 |
| [usmle](skills/usmle/) | 美国医师执照考试备考助手。提供进度追踪、薄弱点分析、题库管理和住院医匹配规划。涵盖 Step 1/2 CK/Step 3 考试结构、IMG 专项指导、分数预测和身心健康支持。 |
| [medical-entity-extractor](skills/medical-entity-extractor/) | 从患者消息中提取医学实体，包括症状、药物、检验值、诊断等。 |
| [patiently-ai](skills/patiently-ai/) | 为患者简化医疗文件。将医生信件、检查报告、处方、出院小结和临床记录转化为清晰、个性化的通俗语言。 |
| [biomedical-search](skills/biomedical-search/) | 综合生物医学信息搜索，整合 PubMed、预印本、临床试验和 FDA 药物标签。由 Valyu 语义搜索驱动，一站式检索多源生物医学数据。 |
| [medical-imaging-review](skills/medical-imaging-review/) | 撰写医学影像 AI 研究的文献综述。适用于撰写综述论文、系统评价或影像相关主题的文献分析。 |
| [fhir-developer-skill](skills/fhir-developer-skill/) | FHIR API 开发指南，用于构建医疗数据端点（Patient、Observation、Encounter、Condition、MedicationRequest）。开发或集成 FHIR REST API 时使用。 |
| [clinical-trial-protocol-skill](skills/clinical-trial-protocol-skill/) | 为药物或医疗器械生成临床试验方案。适用于设计临床研究、编写 FDA 申报文件或制定试验性产品研究方案。 |
| [prior-auth-review-skill](skills/prior-auth-review-skill/) | 自动化保险预授权（PA）审核。评估医疗必要性，对照覆盖政策进行验证，并生成预授权决定。 |
| [clinical-reports](skills/clinical-reports/) | 撰写全面的临床报告——病例报告（CARE 指南）、诊断报告（放射/病理/检验）、临床试验报告（ICH-E3、CSR）及患者文档（SOAP、H&P、出院小结）。符合 HIPAA/FDA/ICH-GCP 规范。 |
| [clinicaltrials-database](skills/clinicaltrials-database/) | 通过 API v2 查询 ClinicalTrials.gov。按疾病、药物、地点、状态或分期检索试验，按 NCT ID 获取详情，导出数据用于临床研究和患者匹配。 |
| [clinical-decision-support](skills/clinical-decision-support/) | 生成临床决策支持（CDS）文档，涵盖患者队列分析、治疗建议报告（含 GRADE 证据分级）、生物标志物整合及统计输出（风险比、生存曲线）。适用于药物研发和临床研究。 |
| [tooluniverse-clinical-trial-design](skills/tooluniverse-clinical-trial-design/) | 临床试验设计可行性评估。评估患者人群规模、生物标志物流行率、终点选择、对照组分析、安全监测和监管路径。规划 I/II 期试验或评估试验可行性时使用。 |
| [tooluniverse-disease-research](skills/tooluniverse-disease-research/) | 生成全面的疾病研究报告，覆盖流行病学、发病机制、诊断、治疗和在研临床试验。询问疾病、综合征或需要系统性疾病分析时使用。 |
| [tooluniverse-literature-deep-research](skills/tooluniverse-literature-deep-research/) | 深度生物医学文献研究，含靶点消歧、证据分级和主题结构化提取。解析基因/蛋白 ID 及同义词，合成生物学模型并生成可检验假说。适用于深度文献综述或靶点画像。 |
| [tooluniverse-clinical-guidelines](skills/tooluniverse-clinical-guidelines/) | 检索 12+ 权威来源的临床实践指南（NICE、WHO、ADA、AHA/ACC、NCCN、SIGN、CPIC 等）。覆盖心脏病、肿瘤、糖尿病、药物基因组学等领域。询问治疗建议或诊疗标准时使用。 |
| [tooluniverse-drug-research](skills/tooluniverse-drug-research/) | 全面的药物研究报告，涵盖药物身份、药理、靶点、临床试验、安全性、药物基因组学和 ADMET 特性。适用于药物画像、安全性评估或临床研发研究。 |
| [tooluniverse-drug-repurposing](skills/tooluniverse-drug-repurposing/) | 基于靶点、化合物和疾病驱动策略识别药物再利用候选。通过分析靶点、生物活性和安全档案，为已批准药物寻找新适应症。 |
| [tooluniverse-drug-drug-interaction](skills/tooluniverse-drug-drug-interaction/) | 药物相互作用预测与风险评估。分析 CYP450/转运体机制、严重程度分级，提供管理策略。支持多药联用分析（3种以上）和替代用药推荐。 |
| [tooluniverse-rare-disease-diagnosis](skills/tooluniverse-rare-disease-diagnosis/) | 基于表型和遗传数据的罕见病鉴别诊断。将症状映射至 HPO 术语，从 Orphanet/OMIM 识别候选疾病，解读意义不明变异（VUS）。 |
| [tooluniverse-pharmacovigilance](skills/tooluniverse-pharmacovigilance/) | 分析来自 FDA 不良事件报告、药品说明书警告和药物基因组数据的药物安全信号。计算 PRR/ROR，识别严重不良事件，评估药物基因组风险。 |
| [tooluniverse-clinical-trial-matching](skills/tooluniverse-clinical-trial-matching/) | 精准医学和肿瘤学的患者-试验智能匹配。从 ClinicalTrials.gov 按分子入选标准、临床标准、生物标志物对齐和地理可及性对试验排序，输出量化试验匹配评分（0-100）。 |
| [literature-review](skills/literature-review/) | 跨多数据库（PubMed、arXiv、bioRxiv、Semantic Scholar）的系统性文献综述。生成格式规范的报告，支持 APA、Nature、Vancouver 等多种引用格式。 |
| [tooluniverse-precision-oncology](skills/tooluniverse-precision-oncology/) | 基于肿瘤分子图谱提供可操作的治疗建议。解读肿瘤突变，识别 FDA 批准疗法、相关临床试验和耐药机制。 |
| [tooluniverse-cancer-variant-interpretation](skills/tooluniverse-cancer-variant-interpretation/) | 肿瘤体细胞变异临床解读。给定基因+变异（如 EGFR L858R、BRAF V600E），评估致癌性、治疗意义和试验入组资格。 |
| [tooluniverse-variant-analysis](skills/tooluniverse-variant-analysis/) | VCF 文件处理与变异注释分析。解析 VCF，整合 ClinVar/gnomAD/COSMIC 注释，解读临床意义。 |
| [tooluniverse-variant-interpretation](skills/tooluniverse-variant-interpretation/) | 系统性临床变异解读——从原始变异调用到 ACMG 分级建议，整合 ClinVar、gnomAD 和人群数据库证据。 |
| [tooluniverse-structural-variant-analysis](skills/tooluniverse-structural-variant-analysis/) | 结构变异（SV/CNV）综合分析。分类 SV 类型，评估致病性，解读拷贝数变异的临床意义。 |
| [tooluniverse-polygenic-risk-score](skills/tooluniverse-polygenic-risk-score/) | 基于 GWAS 汇总统计数据构建和解读多基因风险评分（PRS），计算遗传风险档案并解读 PRS 百分位数。 |
| [tooluniverse-precision-medicine-stratification](skills/tooluniverse-precision-medicine-stratification/) | 整合基因组、临床和治疗数据进行精准医学患者分层，识别治疗相关亚组和生物标志物驱动的治疗选项。 |
| [tooluniverse-gwas-trait-to-gene](skills/tooluniverse-gwas-trait-to-gene/) | 利用 GWAS Catalog（50万+关联）和 Open Targets Genetics 的基因座-基因预测，发现与疾病/性状关联的基因。 |
| [tooluniverse-gwas-drug-discovery](skills/tooluniverse-gwas-drug-discovery/) | 将 GWAS 信号转化为药物靶点和再利用机会。执行基因座-基因映射、靶点成药性评估和已有药物识别。 |
| [tooluniverse-gwas-study-explorer](skills/tooluniverse-gwas-study-explorer/) | 跨队列比较 GWAS 研究并评估可重复性。整合 NHGRI-EBI GWAS Catalog 和 Open Targets Genetics 进行跨研究荟萃分析。 |
| [tooluniverse-gwas-finemapping](skills/tooluniverse-gwas-finemapping/) | 通过统计精细定位鉴定 GWAS 基因座的因果变异，计算后验概率和可信集。 |
| [tooluniverse-gwas-snp-interpretation](skills/tooluniverse-gwas-snp-interpretation/) | 整合 GWAS Catalog、Open Targets Genetics 和 ClinVar 解读 SNP 的性状关联和功能注释。 |
| [tooluniverse-phylogenetics](skills/tooluniverse-phylogenetics/) | 系统发育和序列分析——比对处理、进化树构建和进化度量，适用于病原体或物种进化研究。 |
| [tooluniverse-epigenomics](skills/tooluniverse-epigenomics/) | 表观基因组数据处理——甲基化芯片分析（CpG 过滤、差异甲基化）、染色质可及性和组蛋白修饰分析。 |
| [tooluniverse-rnaseq-deseq2](skills/tooluniverse-rnaseq-deseq2/) | 使用 PyDESeq2 进行 RNA-seq 差异表达分析——标准化、离散度估计、Wald 检验、LFC 收缩和通路富集。 |
| [tooluniverse-single-cell](skills/tooluniverse-single-cell/) | 使用 scanpy 进行单细胞 RNA 测序分析——QC、标准化、PCA、UMAP、Leiden 聚类、轨迹分析和细胞类型注释。 |
| [tooluniverse-spatial-transcriptomics](skills/tooluniverse-spatial-transcriptomics/) | 空间转录组学数据分析——在组织架构中映射基因表达，支持 10x Visium、MERFISH、seqFISH 和 Slide-seq 平台。 |
| [tooluniverse-spatial-omics-analysis](skills/tooluniverse-spatial-omics-analysis/) | 空间多组学数据整合分析框架——空间变异基因、空间域注释和组织分辨率多组学分析。 |
| [tooluniverse-proteomics-analysis](skills/tooluniverse-proteomics-analysis/) | 质谱蛋白质组学数据分析——蛋白定量、差异表达、翻译后修饰（PTM）和蛋白互作网络构建。 |
| [tooluniverse-metabolomics](skills/tooluniverse-metabolomics/) | 代谢组学研究——代谢物鉴定并检索数据库（HMDB 22万+代谢物、MetaboLights、Metabolomics Workbench）。 |
| [tooluniverse-metabolomics-analysis](skills/tooluniverse-metabolomics-analysis/) | 代谢组学数据分析——代谢物鉴定、定量、通路分析和代谢通量，处理 LC-MS、GC-MS 或 NMR 数据。 |
| [tooluniverse-multi-omics-integration](skills/tooluniverse-multi-omics-integration/) | 整合转录组、蛋白质组、表观基因组、基因组和代谢组数据，用于系统生物学和精准医学研究。 |
| [tooluniverse-multiomic-disease-characterization](skills/tooluniverse-multiomic-disease-characterization/) | 整合基因组、转录组、蛋白质组、通路和治疗层面进行系统级疾病多组学表征。 |
| [tooluniverse-expression-data-retrieval](skills/tooluniverse-expression-data-retrieval/) | 从 ArrayExpress 和 BioStudies 检索基因表达和组学数据集，含质量评估和结构化报告。 |
| [tooluniverse-gene-enrichment](skills/tooluniverse-gene-enrichment/) | 基因集富集和通路分析——使用 gseapy、PANTHER、STRING、Reactome，支持 GO 富集、KEGG 通路和 40+ ToolUniverse 工具。 |
| [tooluniverse-systems-biology](skills/tooluniverse-systems-biology/) | 系统生物学和通路分析——使用 Reactome、KEGG、WikiPathways、Pathway Commons 和 BioModels 进行网络建模与通路模拟。 |
| [tooluniverse-protein-interactions](skills/tooluniverse-protein-interactions/) | 使用 STRING、BioGRID 和 SASBDB 分析蛋白互作网络，含置信度评分和功能模块识别。 |
| [tooluniverse-protein-structure-retrieval](skills/tooluniverse-protein-structure-retrieval/) | 从 RCSB PDB、PDBe 和 AlphaFold 检索蛋白质结构数据，含质量评估和综合结构档案。 |
| [tooluniverse-protein-therapeutic-design](skills/tooluniverse-protein-therapeutic-design/) | AI 辅助蛋白质治疗药物从头设计（结合剂、酶、支架）——RFdiffusion 骨架生成、ProteinMPNN 序列设计和 ESM 评估。 |
| [tooluniverse-antibody-engineering](skills/tooluniverse-antibody-engineering/) | 治疗性抗体工程与优化——人源化、亲和力成熟、可开发性评估和免疫原性预测。 |
| [tooluniverse-immune-repertoire-analysis](skills/tooluniverse-immune-repertoire-analysis/) | TCR/BCR 免疫库测序数据分析——克隆性、多样性、V(D)J 基因使用、克隆扩增和抗原特异性预测。 |
| [tooluniverse-immunotherapy-response-prediction](skills/tooluniverse-immunotherapy-response-prediction/) | 整合多生物标志物预测患者对免疫检查点抑制剂（ICI）的响应——TMB、MSI、PD-L1、TIL 信号和 HLA 分型。 |
| [tooluniverse-infectious-disease](skills/tooluniverse-infectious-disease/) | 感染性疾病病原体表征与药物再利用分析——识别病原体分类、必需蛋白、结构靶点和治疗选项。 |
| [tooluniverse-crispr-screen-analysis](skills/tooluniverse-crispr-screen-analysis/) | CRISPR 功能筛选分析——汇集或阵列式筛选（敲除/激活/干扰）以鉴定必需基因和阳性 hit。 |
| [tooluniverse-target-research](skills/tooluniverse-target-research/) | 综合药物靶点情报——蛋白信息、结构、互作、通路、表达、变异图谱和药物研发管线。 |
| [tooluniverse-network-pharmacology](skills/tooluniverse-network-pharmacology/) | 化合物-靶点-疾病网络分析，用于药物再利用、多药理学发现和系统药理学研究。 |
| [tooluniverse-statistical-modeling](skills/tooluniverse-statistical-modeling/) | 生物医学数据集统计建模——线性/逻辑回归、混合效应模型、生存分析和贝叶斯方法。 |
| [tooluniverse-image-analysis](skills/tooluniverse-image-analysis/) | 生物医学显微镜图像分析——菌落形态测量、细胞计数、荧光定量和成像数据统计比较。 |
| [literature-search](skills/literature-search/) | 跨 PubMed、arXiv、bioRxiv、medRxiv 的综合科学文献搜索，由 Valyu 语义搜索驱动，支持自然语言查询。 |
| [medrxiv-search](skills/medrxiv-search/) | 使用 Valyu 语义搜索检索 medRxiv 医学预印本，支持自然语言查询。 |
| [clinical-trials-search](skills/clinical-trials-search/) | 通过 Valyu 自然语言查询 ClinicalTrials.gov——按疾病、入组状态和结局终点检索试验。 |
| [drug-discovery-search](skills/drug-discovery-search/) | 整合 ChEMBL、DrugBank、靶点和 FDA 标签的端到端药物发现平台，Valyu 自然语言驱动。 |
| [drug-labels-search](skills/drug-labels-search/) | 通过 Valyu 自然语言查询 FDA 药品说明书——适应症、用法用量和安全性数据。 |
| [chembl-search](skills/chembl-search/) | 使用 Valyu 语义搜索检索 ChEMBL 生物活性分子数据库——化合物、实验数据和生物活性。 |
| [open-targets-search](skills/open-targets-search/) | 通过 Valyu 语义搜索检索 Open Targets 药物-疾病关联和靶点验证数据。 |
| [patents-search](skills/patents-search/) | 通过 Valyu 自然语言查询全球专利——先有技术、专利图谱和创新追踪。 |
| [drugbank-search](skills/drugbank-search/) | 使用 Valyu 语义搜索检索 DrugBank 综合药物数据库——机制、相互作用和安全性数据。 |
| [arxiv-search](skills/arxiv-search/) | 使用 Valyu 语义搜索检索 arXiv 预印本（生物、医学、AI 方向），支持自然语言查询。 |
| [gwas-database](skills/gwas-database/) | 查询 NHGRI-EBI GWAS Catalog 的 SNP-性状关联——按 rs ID、疾病/性状或基因检索，获取 p 值和汇总统计数据。 |
| [scikit-survival](skills/scikit-survival/) | Python 生存分析与时间-事件建模工具——Kaplan-Meier 曲线、Cox 回归、log-rank 检验和删失数据处理（scikit-survival）。 |

</details>

### 药物安全与化学生物学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [tooluniverse-adverse-event-detection](skills/tooluniverse-adverse-event-detection/) | 使用 FDA FAERS 数据、药品说明书和不均衡分析（PRR、ROR、IC）检测和分析药物不良事件信号，生成量化安全信号评分（0-100）。 |
| [tooluniverse-binder-discovery](skills/tooluniverse-binder-discovery/) | 使用基于结构和基于配体的方法为蛋白质靶点发现新型小分子结合剂，生成候选化合物、ADMET 档案和合成可行性报告。 |
| [tooluniverse-chemical-compound-retrieval](skills/tooluniverse-chemical-compound-retrieval/) | 从 PubChem 和 ChEMBL 检索化合物信息，含消歧、交叉引用和质量评估，生成包含标识符、性质和生物活性的综合档案。 |
| [tooluniverse-chemical-safety](skills/tooluniverse-chemical-safety/) | 综合化学安全和毒理学评估，整合 ADMET-AI 预测、CTD 毒理基因组学、FDA 标签安全数据、DrugBank 安全档案和 STITCH 化学-蛋白相互作用。 |
| [tooluniverse-drug-target-validation](skills/tooluniverse-drug-target-validation/) | 跨10个维度（消歧、疾病关联、成药性、化合物存量、临床先例、安全性、表达证据）计算验证药物靶点，用于早期药物发现。 |
| [tooluniverse-sequence-retrieval](skills/tooluniverse-sequence-retrieval/) | 从 NCBI 和 ENA 检索生物序列（DNA、RNA、蛋白质），含基因消歧、登录号类型处理和综合序列档案。 |

</details>

### 医学影像与病理

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [pydicom](skills/pydicom/) | 用于处理 DICOM 医学影像文件的 Python 库。读取、写入、修改 DICOM 数据，提取像素数据，处理元数据和多帧文件。 |
| [histolab](skills/histolab/) | 全切片图像（WSI）数字病理学图像处理工具包。处理 H&E 或 IHC 染色组织图像，从吉像素切片中提取图块用于深度学习。 |
| [pathml](skills/pathml/) | 用于分析 WSI 和多参数影像数据的计算病理学工具包。支持 H&E 染色图像、多重免疫荧光和空间组学整合。 |
| [omero-integration](skills/omero-integration/) | 显微镜数据管理平台。通过 Python 访问图像，检索数据集，分析像素，管理 ROI/注释，用于高内容筛选工作流。 |
| [neurokit2](skills/neurokit2/) | 综合生理信号处理工具包：ECG、EEG、EDA、RSP、PPG、EMG、EOG 信号。心血管信号分析、神经生理学和生理数据处理。 |
| [neuropixels-analysis](skills/neuropixels-analysis/) | Neuropixels 神经记录分析。加载 SpikeGLX/OpenEphys 数据，Kilosort4 峰值排序，质量指标，Allen/IBL 管理，用于神经科学研究。 |

</details>

### 医疗 ML 与临床 AI

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [pyhealth](skills/pyhealth/) | 用于临床数据（EHR、医保理赔）开发 ML 模型的综合医疗 AI 工具包。任务定义 API、模型训练、评估，用于临床 NLP 和预测。 |
| [scikit-learn](skills/scikit-learn/) | Python 机器学习：监督学习（分类、回归）、无监督学习（聚类、降维）、模型评估、超参数调优，应用于医疗数据分析。 |
| [transformers](skills/transformers/) | 用于 NLP、计算机视觉、音频和多模态任务的预训练 Transformer 模型。文本生成、分类、问答和生物医学 NLP（BioBERT、ClinicalBERT）。 |
| [shap](skills/shap/) | 使用 SHAP（沙普利加性解释）的模型可解释性。解释 ML 模型预测，计算特征重要性，生成生物医学模型的 SHAP 图。 |
| [umap-learn](skills/umap-learn/) | UMAP 降维。快速非线性流形学习，用于 2D/3D 可视化、聚类预处理（HDBSCAN），用于高维组学数据。 |

</details>

### 健康与健康管理分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [nutrition-analyzer](skills/nutrition-analyzer/) | 全面营养分析：宏量/微量营养素追踪、膳食评估、餐食规划、食物数据查询和营养建议。 |
| [mental-health-analyzer](skills/mental-health-analyzer/) | 心理健康数据分析：情绪追踪、症状模式、PHQ/GAD评分、行为洞察和健康建议。 |
| [sleep-analyzer](skills/sleep-analyzer/) | 睡眠质量分析：睡眠阶段、时长、效率指标、昼夜节律评估和睡眠卫生建议。 |
| [rehabilitation-analyzer](skills/rehabilitation-analyzer/) | 康复进度追踪：功能评估、运动方案、康复里程碑和物理/职业治疗结局测量。 |
| [fitness-analyzer](skills/fitness-analyzer/) | 健身表现分析：运动追踪、力量/有氧指标、训练负荷、VO2max估算和周期化规划。 |
| [health-trend-analyzer](skills/health-trend-analyzer/) | 纵向健康趋势分析：生命体征追踪、生物标志物趋势、风险因素监测和预测性健康洞察。 |
| [weightloss-analyzer](skills/weightloss-analyzer/) | 体重管理分析：热量平衡、体成分追踪、进度监测和循证减重策略。 |
| [goal-analyzer](skills/goal-analyzer/) | 健康目标追踪与分析：SMART目标设定、进度指标、习惯养成和健康目标的激励洞察。 |
| [occupational-health-analyzer](skills/occupational-health-analyzer/) | 职业健康评估：工作场所人体工程学、暴露风险、工作相关疾病监测和复工规划。 |
| [travel-health-analyzer](skills/travel-health-analyzer/) | 旅行医学：目的地健康风险、疫苗接种要求、疟疾预防、高原反应和旅行者健康准备。 |
| [family-health-analyzer](skills/family-health-analyzer/) | 家庭健康管理：儿科发育里程碑、家族病史、预防性筛查时间表和多代健康追踪。 |
| [tcm-constitution-analyzer](skills/tcm-constitution-analyzer/) | 中医体质分析：中医体质评估、证型辨别、草药建议和生活方式指导。 |
| [emergency-card](skills/emergency-card/) | 生成包含关键健康数据、药物、过敏和紧急联系人的急救医疗信息卡，用于患者安全。 |
| [ai-analyzer](skills/ai-analyzer/) | AI驱动的全面健康数据解读，结合多个生物标志物和健康指标进行整体健康评估。 |
| [wellally-tech](skills/wellally-tech/) | WellAlly健康分析平台的技术框架：集成模式、数据管道和健康AI基础设施。 |

</details>

### 心理健康与危机干预

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [crisis-detection-intervention-ai](skills/crisis-detection-intervention-ai/) | 使用NLP和心理健康情感分析检测危机信号。实现自杀意念检测、自动升级和危机资源整合，用于心理健康应用和康复平台。 |
| [crisis-response-protocol](skills/crisis-response-protocol/) | 安全处理心理健康危机情况：危机检测、安全协议、紧急升级、自杀预防和热线整合，适用于AI辅导应用。 |
| [hipaa-compliance](skills/hipaa-compliance/) | 处理PHI时确保HIPAA合规。用于健康数据应用的审计日志、数据访问控制、安全事件追踪和合规验证。 |
| [clinical-diagnostic-reasoning](skills/clinical-diagnostic-reasoning/) | 通过系统性错误分析、鉴别诊断框架和临床判断改进，识别和抵制医疗决策中的认知偏见。 |
| [speech-pathology-ai](skills/speech-pathology-ai/) | AI驱动的言语语言病理学：音素分析、构音可视化、嗓音障碍评估、流利度干预、AAC和口吃治疗支持。 |
| [hrv-alexithymia-expert](skills/hrv-alexithymia-expert/) | 心率变异性生物特征和情绪意识训练。HRV分析、内感受训练、生物反馈、迷走神经张力评估和自主神经系统评价。 |
| [adhd-daily-planner](skills/adhd-daily-planner/) | ADHD优化的日常规划：时间盲友好的日程安排、执行功能支持、多巴胺感知任务设计和神经多样性友好的生产力系统。 |
| [grief-companion](skills/grief-companion/) | 富有同理心的丧亲支持、纪念创作、悲伤教育和在非线性失落旅程中提供治愈引导。 |
| [jungian-psychologist](skills/jungian-psychologist/) | 荣格分析心理学：阴影工作、原型分析、梦境解析、积极想象、通过深层心理学视角的成瘾/康复和个体化过程。 |
| [modern-drug-rehab-computer](skills/modern-drug-rehab-computer/) | 综合成瘾康复知识系统：循证治疗（CBT、DBT、MI、EMDR、MAT）、康复资源、危机干预和戒毒机构的家庭系统。 |
| [recovery-community-moderator](skills/recovery-community-moderator/) | 成瘾康复社区的创伤知情AI主持：减少伤害、12步传统、冲突检测和危机帖子识别。 |

</details>

### 医疗器械与监管

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [iso-13485-certification](skills/iso-13485-certification/) | 医疗器械ISO 13485质量管理体系文档综合工具包：差距分析、质量手册、程序、医疗器械档案。涵盖FDA QMSR、EU MDR合规要求。 |

</details>

</details>

## 🗂️ 科学数据库

<details open>
<summary>展开/收起该大类</summary>

### 科学数据库（基因组与变异）

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [clinvar-database](skills/clinvar-database/) | 查询 NCBI ClinVar 的变异临床意义。按基因/位置检索，解读致病性分类，通过 E-utilities API 或 FTP 访问，注释 VCF 文件，用于基因组医学。 |
| [clinpgx-database](skills/clinpgx-database/) | 访问 ClinPGx 药物基因组学数据（PharmGKB 的继承者）。查询基因-药物相互作用、CPIC 指南、等位基因功能，用于精准医学和基因型导向给药。 |
| [cosmic-database](skills/cosmic-database/) | 访问 COSMIC 癌症突变数据库。查询体细胞突变、癌症基因普查、突变特征、基因融合，用于癌症研究和精准肿瘤学。需要认证。 |
| [ensembl-database](skills/ensembl-database/) | 查询 Ensembl 基因组数据库 REST API（250+ 物种）。基因查询、序列检索、变异分析、比较基因组学、直系同源基因、VEP 预测。 |
| [gene-database](skills/gene-database/) | 通过 E-utilities/Datasets API 查询 NCBI Gene。按符号/ID 检索，获取基因信息（RefSeq、GO、位置、表型），批量查询，用于基因注释。 |
| [geo-database](skills/geo-database/) | 访问 NCBI GEO 基因表达/基因组数据。搜索/下载微阵列和 RNA-seq 数据集（GSE、GSM、GPL），检索 SOFT/Matrix 文件，用于转录组分析。 |
| [ena-database](skills/ena-database/) | 通过 API/FTP 访问欧洲核酸数据库。按登录号检索 DNA/RNA 序列、原始测序数据（FASTQ）、基因组组装，用于基因组学和生物信息学流程。 |
| [gget](skills/gget/) | 快速生物信息查询的 CLI/Python 工具包，访问 20+ 数据库：Ensembl、UniProt、AlphaFold、ARCHS4、Enrichr、OpenTargets、COSMIC、BLAST 等。 |
| [pysam](skills/pysam/) | 基因组文件工具包。读写 SAM/BAM/CRAM 比对、VCF/BCF 变异、FASTA/FASTQ 序列，提取区域，计算覆盖度，用于 NGS 数据处理流程。 |

</details>

### 科学数据库（蛋白质、通路与药物）

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [alphafold-database](skills/alphafold-database/) | 访问 AlphaFold 2亿+预测蛋白质结构。按 UniProt ID 检索结构，下载 PDB/mmCIF 文件，分析置信度指标（pLDDT、PAE），用于药物发现和结构生物学。 |
| [pdb-database](skills/pdb-database/) | 访问 RCSB PDB 的三维蛋白质/核酸结构。按文本/序列/结构搜索，下载坐标（PDB/mmCIF），检索元数据，用于结构生物学和药物发现。 |
| [uniprot-database](skills/uniprot-database/) | 直接 REST API 访问 UniProt。蛋白质检索、FASTA 获取、ID 映射、Swiss-Prot/TrEMBL。多数据库工作流推荐使用 bioservices（统一接口访问 40+ 服务）。 |
| [string-database](skills/string-database/) | 查询 STRING API 的蛋白质-蛋白质相互作用（5900万蛋白、200亿相互作用）。网络分析、GO/KEGG 富集、互作发现，支持 5000+ 物种，用于系统生物学。 |
| [kegg-database](skills/kegg-database/) | 直接 REST API 访问 KEGG（仅限学术用途）。通路分析、基因-通路映射、代谢通路、药物相互作用、ID 转换。 |
| [reactome-database](skills/reactome-database/) | 查询 Reactome REST API 进行通路分析、富集、基因-通路映射、疾病通路、分子相互作用，用于系统生物学研究。 |
| [brenda-database](skills/brenda-database/) | 通过 SOAP API 访问 BRENDA 酶数据库。检索动力学参数（Km、kcat）、反应方程、生物体数据和底物特异性酶信息，用于生化研究。 |
| [hmdb-database](skills/hmdb-database/) | 访问人类代谢组数据库（22万+代谢物）。按名称/ID/结构检索，获取化学性质、生物标志物数据、NMR/MS 谱图、通路，用于代谢组学。 |
| [metabolomics-workbench-database](skills/metabolomics-workbench-database/) | 通过 REST API 访问 NIH 代谢组工作台（4200+ 研究）。查询代谢物、RefMet 命名、MS/NMR 数据、m/z 搜索，用于代谢组学和生物标志物发现。 |
| [pubchem-database](skills/pubchem-database/) | 通过 PUG-REST API 查询 PubChem（1.1亿+化合物）。按名称/CID/SMILES 检索，获取性质、相似性/子结构搜索、生物活性，用于化学信息学。 |
| [chembl-database](skills/chembl-database/) | 查询 ChEMBL 生物活性分子和药物发现数据。按结构/性质检索化合物，获取生物活性数据（IC50、Ki），发现抑制剂，用于药物化学。 |
| [drugbank-database](skills/drugbank-database/) | 访问 DrugBank 的综合药物信息，包括药物性质、相互作用、靶点、通路、化学结构和药理学数据。 |
| [zinc-database](skills/zinc-database/) | 访问 ZINC（2.3亿+可购买化合物）。按 ZINC ID/SMILES 检索，相似性搜索，3D-ready 结构用于对接，类似物发现，用于虚拟筛选。 |
| [opentargets-database](skills/opentargets-database/) | 查询 Open Targets 平台的靶点-疾病关联、药物靶点发现、可成药性/安全性数据、遗传学/组学证据、已知药物，用于治疗靶点识别。 |
| [fda-database](skills/fda-database/) | 查询 openFDA API 的药品、设备、不良事件、召回、监管申报（510k、PMA）、物质识别（UNII），用于 FDA 监管数据分析。 |
| [pubmed-database](skills/pubmed-database/) | 直接 REST API 访问 PubMed。高级布尔/MeSH 查询、E-utilities API、批量处理、文献管理。 |
| [openalex-database](skills/openalex-database/) | 使用 OpenAlex 数据库查询和分析学术文献。搜索学术论文，分析研究趋势，按作者或机构查找作品。 |
| [biorxiv-database](skills/biorxiv-database/) | 按关键词、作者、日期范围或类别搜索 bioRxiv 预印本服务器，检索生命科学预印本的论文元数据。 |
| [bioservices](skills/bioservices/) | 访问 40+ 生物信息学服务的首选 Python 工具。UniProt、KEGG、ChEMBL、PubChem、Reactome、QuickGO 的统一 API——推荐用于多数据库工作流。 |
| [uspto-database](skills/uspto-database/) | 访问 USPTO API 进行专利/商标搜索、审查历史（PEDS）、转让、引用、办公室行动，用于 IP 分析和先有技术检索。 |

</details>

### 癌症基因组数据库

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [cbioportal-database](skills/cbioportal-database/) | 查询cBioPortal的癌症基因组数据：体细胞突变、拷贝数、基因表达和数百项癌症研究的生存数据。癌症靶点验证、癌基因分析和患者级基因组图谱。 |
| [depmap](skills/depmap/) | 查询癌症依赖图谱（DepMap）的癌细胞系基因依赖评分（CRISPR Chronos）、药物敏感性和基因效应图谱。识别癌症特异性脆弱性和合成致死相互作用。 |
| [imaging-data-commons](skills/imaging-data-commons/) | 查询和下载NCI成像数据共享平台的公共癌症成像数据。访问放射学（CT、MR、PET）和病理数据集用于AI训练或研究。无需身份验证。 |

</details>

### 基因组与分子数据库

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bindingdb-database](skills/bindingdb-database/) | 查询BindingDB获取药物-靶点结合亲和力数据（Ki、Kd、IC50、EC50）。药物发现、先导化合物优化、多药理学和SAR研究。 |
| [gnomad-database](skills/gnomad-database/) | 查询gnomAD获取群体等位基因频率、变异约束评分（pLI、LOEUF）和功能丧失不耐受性。变异致病性解读和罕见病遗传学。 |
| [gtex-database](skills/gtex-database/) | 查询GTEx获取组织特异性基因表达、eQTL和sQTL。将GWAS变异与基因调控联系起来并解释非编码变异效应。 |
| [interpro-database](skills/interpro-database/) | 查询InterPro获取蛋白质家族、结构域和功能位点注释。整合Pfam、PANTHER、PRINTS、SMART等11+数据库进行蛋白质功能预测。 |
| [jaspar-database](skills/jaspar-database/) | 查询JASPAR获取转录因子结合位点图谱（PWM/PFM）。调控基因组学、基序分析和GWAS调控变异解读。 |
| [monarch-database](skills/monarch-database/) | 查询Monarch Initiative知识图谱获取疾病-基因-表型关联。整合OMIM、ORPHANET、HPO、ClinVar用于罕见病基因发现。 |
| [tiledbvcf](skills/tiledbvcf/) | 使用TileDB进行可扩展的VCF/BCF摄取、存储和并行查询，用于大规模群体基因组学。 |

</details>

### 结构生物学与药物发现

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [molecular-dynamics](skills/molecular-dynamics/) | 使用OpenMM和MDAnalysis运行和分析分子动力学模拟。蛋白质/小分子系统、力场、能量最小化、RMSD/RMSF分析、自由能面计算。 |
| [glycoengineering](skills/glycoengineering/) | 分析和工程化蛋白质糖基化。预测N/O-糖基化位点，访问糖工程化工具（NetOGlyc、GlycoShield）。治疗性抗体优化和疫苗设计。 |
| [adaptyv](skills/adaptyv/) | 自动化蛋白质测试的云实验室平台：结合测定、表达测试、热稳定性、酶活性。使用NetSolP、SoluProt、ESM进行蛋白质序列优化。 |
| [ginkgo-cloud-lab](skills/ginkgo-cloud-lab/) | 在Ginkgo Bioworks云实验室提交和管理协议，实现自主实验室执行。无细胞蛋白质表达、协议工作流程和生物技术自动化。 |

</details>

</details>

## 🧬 生物信息学 (gptomics bio-* 套件)

<details open>
<summary>展开/收起该大类</summary>

### 生物信息学工具与流程

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [biopython](skills/biopython/) | 分子生物学的主要 Python 工具包：PubMed/NCBI 查询（Bio.Entrez）、序列操作、文件解析（FASTA、GenBank、FASTQ、PDB）、BLAST 工作流。 |
| [scikit-bio](skills/scikit-bio/) | 生物学数据工具包。序列分析、比对、系统发育树、多样性指数（alpha/beta、UniFrac）、坐标分析（PCoA）、PERMANOVA，用于微生物组分析。 |
| [etetoolkit](skills/etetoolkit/) | 系统发育树工具包（ETE）。树操作（Newick/NHX）、进化事件检测、直系同源/旁系同源、NCBI 分类、可视化（PDF/SVG），用于系统发育组学。 |
| [deeptools](skills/deeptools/) | NGS 分析工具包。BAM 转 bigWig、QC（相关性、PCA、指纹）、热图/分布图（TSS、峰），用于 ChIP-seq、RNA-seq、ATAC-seq 可视化。 |
| [nextflow-development](skills/nextflow-development/) | 在测序数据上运行 nf-core 生物信息学流程（rnaseq、sarek、atacseq）。处理 RNA-seq、WGS/WES 或 ATAC-seq，支持本地 FASTQ 或公共数据集（GEO/SRA）。 |
| [fastq-analysis](skills/fastq-analysis/) | SRA 下载、FASTQ 质控、STAR 比对、基因定量，以及单细胞 kallisto/bustools 流程，覆盖 bulk 和单细胞测序数据。 |
| [geniml](skills/geniml/) | 用于机器学习的基因组区间数据（BED 文件）。训练区域嵌入（Region2Vec、BEDspace），单细胞 ATAC-seq 分析。 |
| [gtars](skills/gtars/) | 基于 Rust 和 Python 绑定的高性能基因组区间分析工具。基因组区域、BED 文件、覆盖度轨道、重叠检测、ML 模型分词。 |
| [arboreto](skills/arboreto/) | 使用 GRNBoost2 和 GENIE3 算法从基因表达数据推断基因调控网络（GRN）。适用于 bulk RNA-seq 和单细胞 RNA-seq 调控网络推断。 |
| [lamindb](skills/lamindb/) | 用于生物学的开源数据框架，使 scRNA-seq、基因组学、影像等数据可查询、可追溯、可重现且符合 FAIR 原则。 |
| [dnanexus-integration](skills/dnanexus-integration/) | DNAnexus 云基因组学平台。构建应用程序/小程序，管理数据（上传/下载），dxpy Python SDK，运行工作流，处理 FASTQ/BAM/VCF。 |
| [latchbio-integration](skills/latchbio-integration/) | Latch 生物信息学工作流平台。使用 Latch SDK、@workflow/@task 装饰器构建流程，部署无服务器工作流，支持 Nextflow/Snakemake 集成。 |

</details>

### 生物信息 — 临床数据库与变异分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-clinical-databases-clinvar-lookup](skills/bio-clinical-databases-clinvar-lookup/) | 查询ClinVar的临床变异分类、致病性断言和审查状态。 |
| [bio-clinical-databases-dbsnp-queries](skills/bio-clinical-databases-dbsnp-queries/) | 查询dbSNP获取SNP频率、等位基因和功能注释数据。 |
| [bio-clinical-databases-gnomad-frequencies](skills/bio-clinical-databases-gnomad-frequencies/) | 从gnomAD获取群体等位基因频率，用于罕见变异解读。 |
| [bio-clinical-databases-hla-typing](skills/bio-clinical-databases-hla-typing/) | 从测序数据进行HLA分型。 |
| [bio-clinical-databases-myvariant-queries](skills/bio-clinical-databases-myvariant-queries/) | 批量查询MyVariant.info获取多数据库聚合变异注释。 |
| [bio-clinical-databases-pharmacogenomics](skills/bio-clinical-databases-pharmacogenomics/) | PharmGKB/CPIC药物基因组学变异查询，用于药物-基因相互作用。 |
| [bio-clinical-databases-polygenic-risk](skills/bio-clinical-databases-polygenic-risk/) | 从GWAS汇总统计和基因型数据计算多基因风险评分。 |
| [bio-clinical-databases-somatic-signatures](skills/bio-clinical-databases-somatic-signatures/) | 从体细胞变异目录中提取和分类突变特征（COSMIC）。 |
| [bio-clinical-databases-tumor-mutational-burden](skills/bio-clinical-databases-tumor-mutational-burden/) | 从体细胞变异调用计算肿瘤突变负荷（TMB）。 |
| [bio-clinical-databases-variant-prioritization](skills/bio-clinical-databases-variant-prioritization/) | 按致病性评分、遗传方式和表型匹配对候选变异进行排序和过滤。 |
| [bio-variant-calling](skills/bio-variant-calling/) | 基于GATK的胚系变异检测流程（BAM/CRAM文件输入）。 |
| [bio-variant-calling-clinical-interpretation](skills/bio-variant-calling-clinical-interpretation/) | 依据ACMG指南在临床背景下解读变异调用结果。 |
| [bio-variant-calling-deepvariant](skills/bio-variant-calling-deepvariant/) | DeepVariant深度学习变异检测器（短读长WGS/WES数据）。 |
| [bio-variant-calling-filtering-best-practices](skills/bio-variant-calling-filtering-best-practices/) | 对变异集应用VQSR和硬过滤最佳实践。 |
| [bio-variant-calling-joint-calling](skills/bio-variant-calling-joint-calling/) | 多样本联合基因分型以提升变异发现能力。 |
| [bio-variant-calling-structural-variant-calling](skills/bio-variant-calling-structural-variant-calling/) | 从长读长或配对末端测序数据调用结构变异（SV）。 |
| [bio-variant-annotation](skills/bio-variant-annotation/) | 为VCF文件添加功能性、群体和临床后果注释。 |
| [bio-variant-normalization](skills/bio-variant-normalization/) | 标准化变异表示（左对齐、分解）以实现一致比较。 |
| [bio-vcf-basics](skills/bio-vcf-basics/) | 读取、写入和解析VCF文件；按质量、区域和样本过滤。 |
| [bio-vcf-manipulation](skills/bio-vcf-manipulation/) | 高级VCF操作：合并、拆分、重新格式化、子集提取。 |
| [bio-vcf-statistics](skills/bio-vcf-statistics/) | 计算变异统计：转换/颠换比、杂合度、深度分布。 |
| [bio-gatk-variant-calling](skills/bio-gatk-variant-calling/) | 端到端GATK HaplotypeCaller变异检测（含BQSR和联合基因分型）。 |
| [bio-copy-number-cnv-annotation](skills/bio-copy-number-cnv-annotation/) | 为CNV调用添加基因内容、数据库重叠和临床意义注释。 |
| [bio-copy-number-cnv-visualization](skills/bio-copy-number-cnv-visualization/) | 可视化WGS/WES数据的拷贝数谱和分段图。 |
| [bio-copy-number-cnvkit-analysis](skills/bio-copy-number-cnvkit-analysis/) | CNVKit靶向测序和WES数据拷贝数分析。 |
| [bio-copy-number-gatk-cnv](skills/bio-copy-number-gatk-cnv/) | GATK4体细胞拷贝数改变检测流程。 |
| [bio-tumor-fraction-estimation](skills/bio-tumor-fraction-estimation/) | 从等位基因频率和拷贝数数据估计肿瘤纯度和倍性。 |
| [bio-ctdna-mutation-detection](skills/bio-ctdna-mutation-detection/) | 从液体活检超深度测序检测循环肿瘤DNA突变。 |
| [bio-cfdna-preprocessing](skills/bio-cfdna-preprocessing/) | 处理无细胞DNA测序数据：接头修剪、去重、质控。 |
| [bio-methylation-based-detection](skills/bio-methylation-based-detection/) | 从cfDNA甲基化数据检测基于甲基化的癌症信号。 |
| [bio-longitudinal-monitoring](skills/bio-longitudinal-monitoring/) | 跨序列样本追踪体细胞变异进化和克隆动态。 |

</details>

### 生物信息 — 测序与读长质控

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-fastq-quality](skills/bio-fastq-quality/) | 使用FastQC/MultiQC评估FASTQ读长质量并生成每样本QC报告。 |
| [bio-read-qc-adapter-trimming](skills/bio-read-qc-adapter-trimming/) | 使用Trimmomatic、Cutadapt或fastp修剪测序接头。 |
| [bio-read-qc-contamination-screening](skills/bio-read-qc-contamination-screening/) | 使用FastQ Screen或Kraken筛查人类/微生物污染读长。 |
| [bio-read-qc-fastp-workflow](skills/bio-read-qc-fastp-workflow/) | fastp端到端读长质控和预处理（含UMI处理）。 |
| [bio-read-qc-quality-filtering](skills/bio-read-qc-quality-filtering/) | 按质量评分和长度过滤去除低质量读长。 |
| [bio-read-qc-quality-reports](skills/bio-read-qc-quality-reports/) | 用MultiQC聚合多样本QC报告。 |
| [bio-read-qc-umi-processing](skills/bio-read-qc-umi-processing/) | 使用UMI-tools去除PCR重复以实现精确定量。 |
| [bio-paired-end-fastq](skills/bio-paired-end-fastq/) | 处理配对末端FASTQ文件：验证、交错、拆分。 |
| [bio-alignment-io](skills/bio-alignment-io/) | 使用pysam和samtools读写SAM/BAM/CRAM比对文件。 |
| [bio-alignment-msa-parsing](skills/bio-alignment-msa-parsing/) | 解析和分析多序列比对（FASTA、ClustalW、Stockholm格式）。 |
| [bio-alignment-msa-statistics](skills/bio-alignment-msa-statistics/) | 计算MSA统计：保守性、缺口含量、熵。 |
| [bio-alignment-pairwise](skills/bio-alignment-pairwise/) | 使用Smith-Waterman、Needleman-Wunsch、BLAST进行两两序列比对。 |
| [bio-longread-alignment](skills/bio-longread-alignment/) | 使用minimap2比对长读长（ONT/PacBio）；排序和索引BAM文件。 |
| [bio-longread-qc](skills/bio-longread-qc/) | 长读长测序质量控制：读长长度、N50、错误率。 |
| [bio-longread-medaka](skills/bio-longread-medaka/) | 使用Oxford Nanopore Medaka进行共识校正和变异检测。 |
| [bio-longread-structural-variants](skills/bio-longread-structural-variants/) | 使用Sniffles/PBSV从长读长数据调用大型结构变异。 |
| [bio-basecalling](skills/bio-basecalling/) | 使用Dorado/Guppy对原始ONT信号进行碱基识别；转换FAST5为FASTQ。 |
| [bio-compressed-files](skills/bio-compressed-files/) | 处理压缩生物信息文件：bgzip、tabix、zstd、htslib。 |
| [bio-format-conversion](skills/bio-format-conversion/) | 生物信息格式转换：FASTQ↔FASTA、BAM↔CRAM、BED↔GTF。 |
| [bio-sequence-statistics](skills/bio-sequence-statistics/) | 计算序列统计：GC含量、长度分布、复杂度。 |
| [bio-read-sequences](skills/bio-read-sequences/) | 从FASTA/FASTQ文件读取和遍历生物序列。 |
| [bio-write-sequences](skills/bio-write-sequences/) | 将生物序列写入FASTA/FASTQ并保留元数据。 |
| [bio-filter-sequences](skills/bio-filter-sequences/) | 按长度、质量、模式或分类标签过滤序列。 |
| [bio-batch-processing](skills/bio-batch-processing/) | 跨样本和队列批量处理大型生物信息数据集。 |
| [bio-rnaseq-qc](skills/bio-rnaseq-qc/) | RNA-seq专项质控：链特异性、rRNA污染、基因体覆盖度。 |
| [bio-long-read-sequencing-clair3-variants](skills/bio-long-read-sequencing-clair3-variants/) | 使用Clair3深度学习模型从长读长测序调用变异。 |
| [bio-long-read-sequencing-isoseq-analysis](skills/bio-long-read-sequencing-isoseq-analysis/) | Iso-Seq全长转录本分析用于亚型发现。 |
| [bio-long-read-sequencing-nanopore-methylation](skills/bio-long-read-sequencing-nanopore-methylation/) | 使用Modbam2bed从Oxford Nanopore测序识别CpG甲基化。 |
| [bio-splicing-qc](skills/bio-splicing-qc/) | RNA剪接质量评估：连接读长覆盖度、新颖剪接位点。 |
| [bio-splicing-quantification](skills/bio-splicing-quantification/) | 量化可变剪接事件：每亚型的PSI/包含率。 |
| [bio-sashimi-plots](skills/bio-sashimi-plots/) | 生成Sashimi图以可视化特定位点的RNA-seq剪接。 |
| [bio-consensus-sequences](skills/bio-consensus-sequences/) | 使用 `bcftools consensus` 将 VCF 变异应用到参考序列，生成共识 FASTA；适用于样本特异参考和单倍型重建。 |

</details>

### 生物信息 — 差异表达与转录组学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-de-deseq2-basics](skills/bio-de-deseq2-basics/) | DESeq2差异表达分析：设计矩阵、大小因子、离散度。 |
| [bio-de-edger-basics](skills/bio-de-edger-basics/) | EdgeR基于计数数据的差异表达（经验贝叶斯离散度）。 |
| [bio-de-results](skills/bio-de-results/) | 提取、过滤和注释DESeq2/EdgeR结果表。 |
| [bio-de-visualization](skills/bio-de-visualization/) | 差异表达结果的火山图、MA图和热图。 |
| [bio-differential-expression-batch-correction](skills/bio-differential-expression-batch-correction/) | 使用ComBat/limma消除多队列差异表达分析的批次效应。 |
| [bio-differential-expression-timeseries-de](skills/bio-differential-expression-timeseries-de/) | 使用样条和混合模型进行时序差异表达分析。 |
| [bio-differential-splicing](skills/bio-differential-splicing/) | 使用rMATS或MAJIQ检测差异可变剪接事件。 |
| [bio-isoform-switching](skills/bio-isoform-switching/) | 使用DRIMSeq和IsoformSwitchAnalyzeR识别亚型切换事件。 |
| [bio-ribo-seq-orf-detection](skills/bio-ribo-seq-orf-detection/) | 使用RiboTaper/Ribo-TISH从核糖体图谱数据检测翻译ORF。 |
| [bio-ribo-seq-riboseq-preprocessing](skills/bio-ribo-seq-riboseq-preprocessing/) | 核糖体图谱读长预处理：接头修剪、rRNA去除、比对。 |
| [bio-ribo-seq-ribosome-periodicity](skills/bio-ribo-seq-ribosome-periodicity/) | 评估Ribo-seq数据中的三联体周期性和核糖体足迹质量。 |
| [bio-ribo-seq-ribosome-stalling](skills/bio-ribo-seq-ribosome-stalling/) | 从Ribo-seq图谱识别核糖体停滞位点和暂停。 |
| [bio-ribo-seq-translation-efficiency](skills/bio-ribo-seq-translation-efficiency/) | 从匹配的RNA-seq和Ribo-seq计算翻译效率比。 |

</details>

### 生物信息 — 通路与网络分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-pathway-go-enrichment](skills/bio-pathway-go-enrichment/) | 使用clusterProfiler或g:Profiler进行基因本体富集分析。 |
| [bio-pathway-gsea](skills/bio-pathway-gsea/) | 使用预排序或基于计数的统计进行基因集富集分析（GSEA）。 |
| [bio-pathway-kegg-pathways](skills/bio-pathway-kegg-pathways/) | KEGG代谢/信号通路富集和可视化。 |
| [bio-pathway-reactome](skills/bio-pathway-reactome/) | Reactome通路分析（层次富集和可视化）。 |
| [bio-pathway-wikipathways](skills/bio-pathway-wikipathways/) | WikiPathways富集和网络可视化。 |
| [bio-pathway-enrichment-visualization](skills/bio-pathway-enrichment-visualization/) | 通路结果的点图、富集图和网络可视化。 |

</details>

### 生物信息 — 单细胞与空间组学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-single-cell-batch-integration](skills/bio-single-cell-batch-integration/) | 使用Harmony、BBKNN、scVI跨批次整合scRNA-seq数据集。 |
| [bio-single-cell-cell-annotation](skills/bio-single-cell-cell-annotation/) | 使用标记基因和参考图谱注释单细胞簇。 |
| [bio-single-cell-cell-communication](skills/bio-single-cell-cell-communication/) | 使用CellChat或NicheNet推断配体-受体细胞间通讯。 |
| [bio-single-cell-clustering](skills/bio-single-cell-clustering/) | 在Scanpy/Seurat中使用Leiden/Louvain算法对单细胞聚类。 |
| [bio-single-cell-data-io](skills/bio-single-cell-data-io/) | 读写AnnData、Seurat和10x Genomics h5ad/h5格式。 |
| [bio-single-cell-doublet-detection](skills/bio-single-cell-doublet-detection/) | 使用Scrublet或DoubletFinder从scRNA-seq去除双联体。 |
| [bio-single-cell-lineage-tracing](skills/bio-single-cell-lineage-tracing/) | 使用克隆条形码从scRNA-seq重建细胞谱系树。 |
| [bio-single-cell-markers-annotation](skills/bio-single-cell-markers-annotation/) | 识别簇标记基因并自动注释细胞类型。 |
| [bio-single-cell-metabolite-communication](skills/bio-single-cell-metabolite-communication/) | 从scRNA-seq推断代谢物介导的细胞间通讯。 |
| [bio-single-cell-multimodal-integration](skills/bio-single-cell-multimodal-integration/) | 使用WNN/MultiVI整合scRNA-seq与ATAC、CITE-seq或空间数据。 |
| [bio-single-cell-perturb-seq](skills/bio-single-cell-perturb-seq/) | 分析Perturb-seq / CROP-seq基因扰动筛选数据。 |
| [bio-single-cell-preprocessing](skills/bio-single-cell-preprocessing/) | 单细胞预处理：计数过滤、归一化、高变基因选择。 |
| [bio-single-cell-scatac-analysis](skills/bio-single-cell-scatac-analysis/) | scATAC-seq峰调用、TF基序富集和染色质可及性分析。 |
| [bio-single-cell-splicing](skills/bio-single-cell-splicing/) | 使用scVelo或Alevin进行RNA速度和剪接动态分析。 |
| [bio-single-cell-trajectory-inference](skills/bio-single-cell-trajectory-inference/) | 使用Monocle3、PAGA或Slingshot推断伪时间轨迹。 |
| [bio-spatial-transcriptomics-image-analysis](skills/bio-spatial-transcriptomics-image-analysis/) | 分析与空间转录组学数据共配准的组织学图像。 |
| [bio-spatial-transcriptomics-spatial-communication](skills/bio-spatial-transcriptomics-spatial-communication/) | 具有空间背景的配体-受体通讯分析（COMMOT、SpatialDE）。 |
| [bio-spatial-transcriptomics-spatial-data-io](skills/bio-spatial-transcriptomics-spatial-data-io/) | 加载和处理Visium、Slide-seq、MERFISH和STARmap数据集。 |
| [bio-spatial-transcriptomics-spatial-deconvolution](skills/bio-spatial-transcriptomics-spatial-deconvolution/) | 使用RCTD、SPOTlight对空间点中的细胞类型比例进行解卷积。 |
| [bio-spatial-transcriptomics-spatial-domains](skills/bio-spatial-transcriptomics-spatial-domains/) | 使用SpatialDE/BANKSY识别空间可变基因和组织域。 |
| [bio-spatial-transcriptomics-spatial-multiomics](skills/bio-spatial-transcriptomics-spatial-multiomics/) | 将空间转录组学与蛋白质组学、代谢组学或成像整合。 |
| [bio-spatial-transcriptomics-spatial-neighbors](skills/bio-spatial-transcriptomics-spatial-neighbors/) | 构建空间邻居图并进行邻域富集分析。 |
| [bio-spatial-transcriptomics-spatial-preprocessing](skills/bio-spatial-transcriptomics-spatial-preprocessing/) | 空间转录组学预处理：质控、归一化、点过滤。 |
| [bio-spatial-transcriptomics-spatial-proteomics](skills/bio-spatial-transcriptomics-spatial-proteomics/) | 分析CODEX、IMC或MIBI平台的空间蛋白质组学数据。 |
| [bio-spatial-transcriptomics-spatial-statistics](skills/bio-spatial-transcriptomics-spatial-statistics/) | 空间统计：Moran's I、空间自相关、共定位。 |
| [bio-spatial-transcriptomics-spatial-visualization](skills/bio-spatial-transcriptomics-spatial-visualization/) | 可视化空间基因表达图和组织切片叠加层。 |

</details>

### 生物信息 — 表观基因组学与染色质

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-atac-seq-atac-peak-calling](skills/bio-atac-seq-atac-peak-calling/) | 使用MACS2/MACS3调用ATAC-seq染色质可及性峰。 |
| [bio-atac-seq-atac-qc](skills/bio-atac-seq-atac-qc/) | ATAC-seq质量控制：TSS富集、片段大小、FRiP评分。 |
| [bio-atac-seq-differential-accessibility](skills/bio-atac-seq-differential-accessibility/) | 使用DESeq2/DiffBind进行条件间差异染色质可及性分析。 |
| [bio-atac-seq-footprinting](skills/bio-atac-seq-footprinting/) | 使用TOBIAS或HINT-ATAC从ATAC-seq数据进行TF足迹分析。 |
| [bio-atac-seq-motif-deviation](skills/bio-atac-seq-motif-deviation/) | 使用chromVAR对单细胞ATAC数据进行TF基序偏差评分。 |
| [bio-atac-seq-nucleosome-positioning](skills/bio-atac-seq-nucleosome-positioning/) | 从ATAC-seq片段长度分布推断核小体定位。 |
| [bio-chipseq-differential-binding](skills/bio-chipseq-differential-binding/) | 使用DiffBind进行差异ChIP-seq结合分析。 |
| [bio-chipseq-motif-analysis](skills/bio-chipseq-motif-analysis/) | 使用HOMER/MEME从ChIP-seq峰进行从头和已知基序发现。 |
| [bio-chipseq-peak-annotation](skills/bio-chipseq-peak-annotation/) | 为ChIP-seq峰添加基因组特征和最近基因注释。 |
| [bio-chipseq-peak-calling](skills/bio-chipseq-peak-calling/) | 使用MACS2调用TF结合和组蛋白标记的ChIP-seq峰。 |
| [bio-chipseq-qc](skills/bio-chipseq-qc/) | ChIP-seq质量指标：FRiP、SCC、phantompeakqualtools。 |
| [bio-chipseq-super-enhancers](skills/bio-chipseq-super-enhancers/) | 使用ROSE从H3K27ac ChIP-seq识别超级增强子。 |
| [bio-chipseq-visualization](skills/bio-chipseq-visualization/) | 使用deepTools在峰区域生成热图和聚合图谱。 |
| [bio-hi-c-analysis-compartment-analysis](skills/bio-hi-c-analysis-compartment-analysis/) | 从Hi-C接触矩阵调用A/B区室。 |
| [bio-hi-c-analysis-contact-pairs](skills/bio-hi-c-analysis-contact-pairs/) | 处理Hi-C接触对：过滤、去重、分箱。 |
| [bio-hi-c-analysis-hic-data-io](skills/bio-hi-c-analysis-hic-data-io/) | 使用cooler/hicstuff读写Hi-C数据格式：.hic、cool、mcool。 |
| [bio-hi-c-analysis-hic-differential](skills/bio-hi-c-analysis-hic-differential/) | 条件间差异Hi-C相互作用分析。 |
| [bio-hi-c-analysis-hic-visualization](skills/bio-hi-c-analysis-hic-visualization/) | 使用pyGenomeTracks可视化Hi-C接触图、TAD和环。 |
| [bio-hi-c-analysis-loop-calling](skills/bio-hi-c-analysis-loop-calling/) | 使用Mustache或HICCUPS从Hi-C数据检测染色质环。 |
| [bio-hi-c-analysis-matrix-operations](skills/bio-hi-c-analysis-matrix-operations/) | 归一化Hi-C矩阵：ICE、KR、VC；计算观测/期望值。 |
| [bio-hi-c-analysis-tad-detection](skills/bio-hi-c-analysis-tad-detection/) | 从Hi-C数据识别拓扑相关域（TAD）。 |
| [bio-methylation-bismark-alignment](skills/bio-methylation-bismark-alignment/) | 使用Bismark比对亚硫酸盐测序读长并提取CpG甲基化。 |
| [bio-methylation-calling](skills/bio-methylation-calling/) | 从WGBS/RRBS比对中调用CpG甲基化。 |
| [bio-methylation-dmr-detection](skills/bio-methylation-dmr-detection/) | 使用DSS或MethylKit识别差异甲基化区域（DMR）。 |
| [bio-methylation-methylkit](skills/bio-methylation-methylkit/) | MethylKit甲基化分析：CpG瓦片、DMR调用、注释。 |

</details>

### 生物信息 — 宏基因组学与微生物组

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-metagenomics-abundance](skills/bio-metagenomics-abundance/) | 从鸟枪法宏基因组学估计微生物分类丰度。 |
| [bio-metagenomics-amr-detection](skills/bio-metagenomics-amr-detection/) | 使用AMRFinder或RGI/CARD检测抗菌素耐药基因。 |
| [bio-metagenomics-functional-profiling](skills/bio-metagenomics-functional-profiling/) | 使用HUMAnN3进行宏基因组功能分析（通路/基因家族）。 |
| [bio-metagenomics-kraken](skills/bio-metagenomics-kraken/) | 使用Kraken2/Bracken进行宏基因组读长分类。 |
| [bio-metagenomics-metaphlan](skills/bio-metagenomics-metaphlan/) | 使用MetaPhlAn4进行基于进化支特异性标记的微生物群落图谱分析。 |
| [bio-metagenomics-strain-tracking](skills/bio-metagenomics-strain-tracking/) | 使用StrainPhlan或inStrain跨样本追踪微生物菌株。 |
| [bio-metagenomics-visualization](skills/bio-metagenomics-visualization/) | 使用Krona图和堆积柱状图可视化微生物组组成。 |
| [bio-microbiome-amplicon-processing](skills/bio-microbiome-amplicon-processing/) | 使用QIIME2或DADA2处理16S/ITS扩增子测序数据。 |
| [bio-microbiome-differential-abundance](skills/bio-microbiome-differential-abundance/) | 使用ANCOM-BC、MaAsLin2或ALDEx2检验差异微生物丰度。 |
| [bio-microbiome-diversity-analysis](skills/bio-microbiome-diversity-analysis/) | Alpha/beta多样性分析：Shannon、PD、UniFrac、PCoA。 |
| [bio-microbiome-functional-prediction](skills/bio-microbiome-functional-prediction/) | 使用PICRUSt2或Tax4Fun从16S数据预测功能能力。 |
| [bio-microbiome-qiime2-workflow](skills/bio-microbiome-qiime2-workflow/) | 端到端QIIME2流程：去噪、多样性、差异丰度。 |
| [bio-microbiome-taxonomy-assignment](skills/bio-microbiome-taxonomy-assignment/) | 使用SILVA、GTDB或Greengenes2为ASV/OTU分配分类。 |

</details>

### 生物信息 — 免疫信息学与流式细胞术

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-immunoinformatics-epitope-prediction](skills/bio-immunoinformatics-epitope-prediction/) | 使用NetMHCpan/MHCflurry从蛋白质序列预测MHC-I/II表位。 |
| [bio-immunoinformatics-immunogenicity-scoring](skills/bio-immunoinformatics-immunogenicity-scoring/) | 为疫苗和新抗原优先排序评分肽段免疫原性。 |
| [bio-immunoinformatics-mhc-binding-prediction](skills/bio-immunoinformatics-mhc-binding-prediction/) | 预测多个等位基因的肽-MHC结合亲和力。 |
| [bio-immunoinformatics-neoantigen-prediction](skills/bio-immunoinformatics-neoantigen-prediction/) | 从体细胞突变预测新抗原，用于个性化癌症疫苗。 |
| [bio-immunoinformatics-tcr-epitope-binding](skills/bio-immunoinformatics-tcr-epitope-binding/) | 使用ERGO、pMTnet或NetTCR预测TCR-表位结合。 |
| [bio-tcr-bcr-analysis-immcantation-analysis](skills/bio-tcr-bcr-analysis-immcantation-analysis/) | 使用Immcantation套件分析B/T细胞受体库。 |
| [bio-tcr-bcr-analysis-mixcr-analysis](skills/bio-tcr-bcr-analysis-mixcr-analysis/) | MiXCR V(D)J比对和克隆型组装用于免疫库分析。 |
| [bio-tcr-bcr-analysis-repertoire-visualization](skills/bio-tcr-bcr-analysis-repertoire-visualization/) | 可视化库多样性、克隆扩增和V基因使用情况。 |
| [bio-tcr-bcr-analysis-scirpy-analysis](skills/bio-tcr-bcr-analysis-scirpy-analysis/) | 使用Scirpy进行整合scRNA-seq的单细胞TCR/BCR分析。 |
| [bio-tcr-bcr-analysis-vdjtools-analysis](skills/bio-tcr-bcr-analysis-vdjtools-analysis/) | 使用VDJtools进行免疫库统计和重叠分析。 |
| [bio-flow-cytometry-bead-normalization](skills/bio-flow-cytometry-bead-normalization/) | 使用校准珠对流式细胞仪数据进行归一化。 |
| [bio-flow-cytometry-clustering-phenotyping](skills/bio-flow-cytometry-clustering-phenotyping/) | 使用FlowSOM、PhenoGraph或UMAP对细胞群体进行聚类和表型分析。 |
| [bio-flow-cytometry-compensation-transformation](skills/bio-flow-cytometry-compensation-transformation/) | 应用补偿矩阵和双指数/arcsinh变换。 |
| [bio-flow-cytometry-cytometry-qc](skills/bio-flow-cytometry-cytometry-qc/) | 流式/质谱细胞仪质量控制：信号漂移、溢出、异常值检测。 |
| [bio-flow-cytometry-differential-analysis](skills/bio-flow-cytometry-differential-analysis/) | 条件间细胞群体的统计比较。 |
| [bio-flow-cytometry-doublet-detection](skills/bio-flow-cytometry-doublet-detection/) | 检测和去除流式细胞仪数据中的双联体。 |
| [bio-flow-cytometry-fcs-handling](skills/bio-flow-cytometry-fcs-handling/) | 使用FlowCore/FlowKit读取、写入和操作FCS文件。 |
| [bio-flow-cytometry-gating-analysis](skills/bio-flow-cytometry-gating-analysis/) | 用于细胞群体鉴定的手动和算法门控策略。 |
| [bio-imaging-mass-cytometry-cell-segmentation](skills/bio-imaging-mass-cytometry-cell-segmentation/) | 使用Mesmer或CellProfiler对IMC图像中的细胞进行分割。 |
| [bio-imaging-mass-cytometry-data-preprocessing](skills/bio-imaging-mass-cytometry-data-preprocessing/) | 成像质谱细胞仪数据预处理：热像素去除、归一化。 |
| [bio-imaging-mass-cytometry-interactive-annotation](skills/bio-imaging-mass-cytometry-interactive-annotation/) | 在IMC空间数据集中交互式注释细胞类型。 |
| [bio-imaging-mass-cytometry-phenotyping](skills/bio-imaging-mass-cytometry-phenotyping/) | 从多标记IMC面板对免疫和肿瘤细胞进行表型分析。 |
| [bio-imaging-mass-cytometry-quality-metrics](skills/bio-imaging-mass-cytometry-quality-metrics/) | IMC采集质量指标：信噪比、组织覆盖度。 |
| [bio-imaging-mass-cytometry-spatial-analysis](skills/bio-imaging-mass-cytometry-spatial-analysis/) | 成像质谱细胞仪数据的空间细胞邻域分析。 |

</details>

### 生物信息 — 多组学整合

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-multi-omics-data-harmonization](skills/bio-multi-omics-data-harmonization/) | 协调多组学数据集：样本匹配、批次校正、特征对齐。 |
| [bio-multi-omics-mixomics-analysis](skills/bio-multi-omics-mixomics-analysis/) | 使用mixOmics进行多组学因子分析（DIABLO、MOFA、sPLS-DA）。 |
| [bio-multi-omics-mofa-integration](skills/bio-multi-omics-mofa-integration/) | 跨模态潜因子发现的多组学因子分析（MOFA+）。 |
| [bio-multi-omics-similarity-network](skills/bio-multi-omics-similarity-network/) | 相似性网络融合（SNF）用于多组学患者分层。 |

</details>

### 生物信息 — 蛋白质组学与代谢组学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-proteomics-data-import](skills/bio-proteomics-data-import/) | 从MaxQuant、Proteome Discoverer、FragPipe导入DDA/DIA蛋白质组学数据。 |
| [bio-proteomics-dia-analysis](skills/bio-proteomics-dia-analysis/) | 使用DIA-NN或Spectronaut进行DIA蛋白质组学分析。 |
| [bio-proteomics-differential-abundance](skills/bio-proteomics-differential-abundance/) | 使用limma、MSstats或DEqMS进行差异蛋白丰度分析。 |
| [bio-proteomics-peptide-identification](skills/bio-proteomics-peptide-identification/) | 肽段谱图匹配和数据库搜索结果解析。 |
| [bio-proteomics-protein-inference](skills/bio-proteomics-protein-inference/) | 蛋白质分组、简约性和蛋白质组学实验的FDR控制。 |
| [bio-proteomics-proteomics-qc](skills/bio-proteomics-proteomics-qc/) | 蛋白质组学质控：肽段计数、覆盖度、缺失值、CV。 |
| [bio-proteomics-ptm-analysis](skills/bio-proteomics-ptm-analysis/) | 翻译后修饰分析：磷酸化、泛素化、糖基化富集。 |
| [bio-proteomics-quantification](skills/bio-proteomics-quantification/) | 无标记、TMT/iTRAQ和SILAC定量工作流程。 |
| [bio-proteomics-spectral-libraries](skills/bio-proteomics-spectral-libraries/) | 构建和使用DIA数据分析的谱图库。 |
| [bio-metabolomics-lipidomics](skills/bio-metabolomics-lipidomics/) | 脂质组学数据分析：脂质类别注释、脂肪酸组成。 |
| [bio-metabolomics-metabolite-annotation](skills/bio-metabolomics-metabolite-annotation/) | 使用HMDB、MZmine、SIRIUS或MetFrag注释质谱特征。 |
| [bio-metabolomics-msdial-preprocessing](skills/bio-metabolomics-msdial-preprocessing/) | MS-DIAL的LC-MS/GC-MS数据预处理和峰检测。 |
| [bio-metabolomics-normalization-qc](skills/bio-metabolomics-normalization-qc/) | 代谢组学归一化：PQN、LOESS、中位数、批次校正。 |
| [bio-metabolomics-pathway-mapping](skills/bio-metabolomics-pathway-mapping/) | 将鉴定的代谢物映射到KEGG、MetaCyc或Reactome通路。 |
| [bio-metabolomics-statistical-analysis](skills/bio-metabolomics-statistical-analysis/) | 代谢组学的单变量/多变量统计：PCA、PLS-DA、ANOVA。 |
| [bio-metabolomics-targeted-analysis](skills/bio-metabolomics-targeted-analysis/) | 靶向代谢组学（MRM/SRM）：校准曲线、定量。 |
| [bio-metabolomics-xcms-preprocessing](skills/bio-metabolomics-xcms-preprocessing/) | XCMS的LC-MS峰检测、对齐和分组。 |

</details>

### 生物信息 — 结构生物学与化学信息学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-structural-biology-alphafold-predictions](skills/bio-structural-biology-alphafold-predictions/) | 使用AlphaFold2/3预测：模型质量评估、置信度评分。 |
| [bio-structural-biology-modern-structure-prediction](skills/bio-structural-biology-modern-structure-prediction/) | 使用ESMFold、RoseTTAFold和OpenFold进行现代结构预测。 |
| [bio-pdb-geometric-analysis](skills/bio-pdb-geometric-analysis/) | 蛋白质结构几何分析：距离、角度、接触、RMSD。 |
| [bio-pdb-structure-io](skills/bio-pdb-structure-io/) | 使用BioPython或Gemmi读写PDB/mmCIF结构文件。 |
| [bio-pdb-structure-modification](skills/bio-pdb-structure-modification/) | 修改蛋白质结构：添加氢原子、突变残基、能量最小化。 |
| [bio-pdb-structure-navigation](skills/bio-pdb-structure-navigation/) | 导航和检查PDB结构：链、残基、原子选择。 |
| [bio-molecular-descriptors](skills/bio-molecular-descriptors/) | 计算分子描述符（RDKit）：MW、LogP、TPSA、指纹。 |
| [bio-molecular-io](skills/bio-molecular-io/) | 使用RDKit读写化学结构格式：SDF、SMILES、MOL2、PDB。 |
| [bio-reaction-enumeration](skills/bio-reaction-enumeration/) | 从SMARTS反应模板枚举反应和产物。 |
| [bio-similarity-searching](skills/bio-similarity-searching/) | 分子相似性搜索：Tanimoto系数、基于指纹、骨架跳跃。 |
| [bio-substructure-search](skills/bio-substructure-search/) | 使用SMARTS模式在化学数据库中进行子结构搜索。 |
| [bio-virtual-screening](skills/bio-virtual-screening/) | 虚拟筛选流程：对接、评分、姿态过滤（AutoDock/Vina）。 |
| [bio-admet-prediction](skills/bio-admet-prediction/) | 预测ADMET性质：吸收、分布、代谢、排泄、毒性。 |

</details>

### 生物信息 — 流行病学基因组学与因果基因组学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-epidemiological-genomics-amr-surveillance](skills/bio-epidemiological-genomics-amr-surveillance/) | 来自基因组流行病学数据的抗菌素耐药性监测。 |
| [bio-epidemiological-genomics-pathogen-typing](skills/bio-epidemiological-genomics-pathogen-typing/) | 病原体分子分型：MLST、wgMLST、cgMLST（用于暴发分析）。 |
| [bio-epidemiological-genomics-phylodynamics](skills/bio-epidemiological-genomics-phylodynamics/) | 系统动力学：分子钟、种群动态、BEAST2/TreeTime。 |
| [bio-epidemiological-genomics-transmission-inference](skills/bio-epidemiological-genomics-transmission-inference/) | 使用TransPhylo/outbreaker2从病原体基因组推断传播网络。 |
| [bio-epidemiological-genomics-variant-surveillance](skills/bio-epidemiological-genomics-variant-surveillance/) | 从基因组监测追踪病原体变异出现和传播。 |
| [bio-causal-genomics-colocalization-analysis](skills/bio-causal-genomics-colocalization-analysis/) | 使用coloc或eCAVIAR进行GWAS和eQTL信号的共定位分析。 |
| [bio-causal-genomics-fine-mapping](skills/bio-causal-genomics-fine-mapping/) | 使用SuSiE或FINEMAP对GWAS位点的因果变异进行精细定位。 |
| [bio-causal-genomics-mediation-analysis](skills/bio-causal-genomics-mediation-analysis/) | 基因表达中间变量的因果中介分析。 |
| [bio-causal-genomics-mendelian-randomization](skills/bio-causal-genomics-mendelian-randomization/) | 使用MR-Base/TwoSampleMR进行两样本孟德尔随机化。 |
| [bio-causal-genomics-pleiotropy-detection](skills/bio-causal-genomics-pleiotropy-detection/) | 在MR分析中检测水平多效性和异质性。 |
| [bio-genome-engineering-base-editing-design](skills/bio-genome-engineering-base-editing-design/) | 设计碱基编辑器（CBE/ABE）用于精确单碱基纠正。 |
| [bio-genome-engineering-grna-design](skills/bio-genome-engineering-grna-design/) | 使用Cas-OFFinder和CRISPOR设计和评分CRISPR引导RNA。 |
| [bio-genome-engineering-hdr-template-design](skills/bio-genome-engineering-hdr-template-design/) | 通过同源定向修复设计精确敲入的HDR模板。 |
| [bio-genome-engineering-off-target-prediction](skills/bio-genome-engineering-off-target-prediction/) | 在全基因组范围内预测CRISPR脱靶位点用于安全性评估。 |
| [bio-genome-engineering-prime-editing-design](skills/bio-genome-engineering-prime-editing-design/) | 为引物编辑实验设计pegRNA和切口酶gRNA。 |
| [bio-crispr-screens-base-editing-analysis](skills/bio-crispr-screens-base-editing-analysis/) | 分析碱基编辑筛选：引导效率、编辑结果。 |
| [bio-crispr-screens-batch-correction](skills/bio-crispr-screens-batch-correction/) | 纠正跨重复实验CRISPR筛选数据的批次效应。 |
| [bio-crispr-screens-crispresso-editing](skills/bio-crispr-screens-crispresso-editing/) | 使用CRISPResso2从扩增子测序量化编辑结果。 |
| [bio-crispr-screens-hit-calling](skills/bio-crispr-screens-hit-calling/) | 使用MAGeCK、BAGEL2或casTLE从CRISPR筛选中调用命中基因。 |
| [bio-crispr-screens-jacks-analysis](skills/bio-crispr-screens-jacks-analysis/) | 使用JACKS层次贝叶斯模型进行CRISPR筛选分析。 |
| [bio-crispr-screens-library-design](skills/bio-crispr-screens-library-design/) | 设计CRISPR筛选文库：引导选择、对照、覆盖度。 |
| [bio-crispr-screens-mageck-analysis](skills/bio-crispr-screens-mageck-analysis/) | MAGeCK MLE/RRA分析用于CRISPR pooled筛选。 |
| [bio-crispr-screens-screen-qc](skills/bio-crispr-screens-screen-qc/) | CRISPR筛选质量控制：基尼指数、读长分布。 |

</details>

</details>

## 🔬 组学与计算生物学

<details open>
<summary>展开/收起该大类</summary>

### 单细胞与空间组学

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [anndata](skills/anndata/) | 在 Python 中处理单细胞基因组学的注释数据矩阵，管理带元数据的实验测量数据和大规模组学数据。 |
| [scanpy](skills/scanpy/) | 单细胞 RNA-seq 分析。加载 .h5ad/10X 数据，QC、标准化、PCA/UMAP/t-SNE、Leiden 聚类、标志基因、细胞类型注释、轨迹分析。 |
| [scvi-tools](skills/scvi-tools/) | 单细胞分析的深度学习框架：数据整合/批次校正（scVI/scANVI）、ATAC-seq（PeakVI）、CITE-seq（totalVI）、多组学（MultiVI）、空间转录组解卷积（DestVI）。 |
| [single-cell-rna-qc](skills/single-cell-rna-qc/) | 使用 scverse 最佳实践对单细胞 RNA-seq 数据（.h5ad 或 .h5 文件）进行 MAD-based 过滤和综合可视化质控。 |
| [cellxgene-census](skills/cellxgene-census/) | 查询 CZ CELLxGENE Census（6100万+细胞）。按细胞类型/组织/疾病过滤，检索表达数据，与 scanpy/PyTorch 集成，用于人群级单细胞分析。 |
| [pydeseq2](skills/pydeseq2/) | 使用 Python DESeq2 进行差异基因表达分析。从 bulk RNA-seq 计数识别差异表达基因，Wald 检验，FDR 校正，火山图/MA 图。 |
| [bulk-combat-correction](skills/bulk-combat-correction/) | 使用 pyComBat 去除合并 bulk RNA-seq 或微阵列队列中的批次效应，导出校正矩阵并生成校正前后对比可视化。 |
| [bulk-deg-analysis](skills/bulk-deg-analysis/) | Bulk RNA-seq DEG 流程：基因 ID 映射、DESeq2 标准化、统计检验、可视化和通路富集（OmicVerse）。 |
| [bulk-deseq2-analysis](skills/bulk-deseq2-analysis/) | 基于 PyDESeq2 的差异表达分析，含 ID 映射、差异检验、折叠变化阈值和富集可视化。 |
| [bulk-stringdb-ppi](skills/bulk-stringdb-ppi/) | 通过 STRING 查询蛋白相互作用，使用 pyPPI 构建 PPI 图谱，为 bulk 基因列表生成网络图。 |
| [bulk-to-single-deconvolution](skills/bulk-to-single-deconvolution/) | 使用 Bulk2Single 工作流将 bulk RNA-seq 队列转换为合成单细胞数据集，进行细胞比例估计和 beta-VAE 生成。 |
| [bulk-trajblend-interpolation](skills/bulk-trajblend-interpolation/) | 使用 BulkTrajBlend 通过 beta-VAE 和 GNN 模型从 bulk RNA-seq 生成中间细胞，扩展 scRNA-seq 发育轨迹。 |
| [bulk-wgcna-analysis](skills/bulk-wgcna-analysis/) | 在 OmicVerse 中运行 PyWGCNA——共表达模块构建、特征基因可视化和枢纽基因提取。 |
| [single-annotation](skills/single-annotation/) | 单细胞注释工作流：SCSA、MetaTiME、CellVote、CellMatch、GPTAnno 和加权 KNN 转移，用于跨模态细胞类型注释。 |
| [single-cellphone-db](skills/single-cellphone-db/) | 在注释的单细胞数据上运行 CellPhoneDB v5，推断配体-受体网络并生成 CellChat 风格的可视化。 |
| [single-clustering](skills/single-clustering/) | 单细胞聚类工作流：QC、多方法聚类、主题建模、cNMF 和跨批次整合（OmicVerse）。 |
| [single-downstream-analysis](skills/single-downstream-analysis/) | OmicVerse 下游分析教程参考：AUCell 评分、metacell DEG 及相关导出。 |
| [single-multiomics](skills/single-multiomics/) | OmicVerse 多组学教程：MOFA、GLUE 配对、SIMBA 整合、TOSICA 转移和 StaVIA 制图。 |
| [single-preprocessing](skills/single-preprocessing/) | OmicVerse 单细胞预处理教程：QC、标准化、HVG 检测、PCA/嵌入流程（CPU/GPU）。 |
| [single-to-spatial-mapping](skills/single-to-spatial-mapping/) | 使用 Single2Spatial 工作流将 scRNA-seq 图谱映射到空间转录组切片，进行深度森林训练和标志物可视化。 |
| [single-trajectory](skills/single-trajectory/) | OmicVerse 轨迹分析工作流：PAGA、Palantir、VIA、速度耦合和命运评分。 |
| [spatial-tutorials](skills/spatial-tutorials/) | 空间转录组学教程：跨 Visium、Visium HD、Stereo-seq 和 Slide-seq 平台的预处理、解卷积和下游建模。 |
| [tcga-preprocessing](skills/tcga-preprocessing/) | 将 TCGA 样本表、表达数据和临床数据导入 OmicVerse，初始化生存元数据并导出注释的 AnnData 文件。 |
| [gsea-enrichment](skills/gsea-enrichment/) | OmicVerse 中的基因集富集分析，含正确的基因集格式处理，用于加载通路数据库和运行 GSEA。 |

</details>

### 化学信息学与药物发现

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [rdkit](skills/rdkit/) | 精细分子控制的化学信息学工具包。SMILES/SDF 解析、描述符（MW、LogP、TPSA）、指纹、子结构搜索、2D/3D 生成、相似性计算。 |
| [datamol](skills/datamol/) | 具有简化接口的 Pythonic RDKit 封装，用于标准药物发现：SMILES 解析、标准化、描述符、指纹、聚类、3D 构象生成。 |
| [medchem](skills/medchem/) | 药物化学过滤器。应用药物样规则（Lipinski、Veber）、PAINS 过滤、结构警报、复杂度指标，用于化合物优先级排列和文库过滤。 |
| [diffdock](skills/diffdock/) | 基于扩散的分子对接。从 PDB/SMILES 预测蛋白质-配体结合构象，置信度评分，虚拟筛选，用于基于结构的药物设计。 |
| [molfeat](skills/molfeat/) | 用于 ML 的分子特征化（100+ 特征器）。ECFP、MACCS、描述符、预训练模型（ChemBERTa），将 SMILES 转换为特征，用于 QSAR 和分子 ML。 |
| [deepchem](skills/deepchem/) | 分子机器学习工具包。性质预测（ADMET、毒性）、GNN（GCN、MPNN）、MoleculeNet 基准、预训练模型，用于药物发现 ML。 |
| [torchdrug](skills/torchdrug/) | 基于图的药物发现工具包。分子性质预测（ADMET）、蛋白质建模、知识图谱推理、分子生成、逆合成、GNN（GIN、GAT、SchNet）。 |
| [torch_geometric](skills/torch_geometric/) | 图神经网络（PyG）。节点/图分类、链接预测、GCN、GAT、GraphSAGE、分子性质预测，用于药物发现中的几何深度学习。 |
| [pytdc](skills/pytdc/) | 治疗学数据公共基准（TDC）。AI-ready 药物发现数据集（ADME、毒性、DTI）、基准、支架分割、分子预言机，用于治疗学 ML。 |
| [cobrapy](skills/cobrapy/) | 约束型代谢建模（COBRA）。FBA、FVA、基因敲除、通量采样、SBML 模型，用于系统生物学和代谢工程分析。 |

</details>

### 蛋白质组学与质谱

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [matchms](skills/matchms/) | 质谱光谱分析。处理 mzML/MGF/MSP 文件，光谱相似性（余弦、改良余弦），元数据协调，化合物鉴定，用于代谢组学和 MS 数据处理。 |
| [pyopenms](skills/pyopenms/) | OpenMS 的 Python 接口，用于 LC-MS/MS 蛋白质组学和代谢组学工作流。文件处理（mzML、mzXML、mzTab、pepXML、mzIdentML）和定量分析。 |
| [flowio](skills/flowio/) | 解析 FCS（流式细胞术标准）文件 v2.0-3.1。提取事件为 NumPy 数组，读取元数据/通道，转换为 CSV/DataFrame，用于流式细胞术数据预处理。 |

</details>

### 蛋白质结构与设计

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [esm](skills/esm/) | ESM3 生成式多模态蛋白质设计（序列、结构、功能）和 ESM C 高效蛋白质嵌入。用于序列评分和嵌入的蛋白质语言模型。 |
| [alphafold](skills/alphafold/) | 使用 AlphaFold2 结构预测验证蛋白质设计。验证设计序列折叠正确性，预测结合剂-靶点复合物结构，计算 pLDDT/PAE 指标。 |
| [boltz](skills/boltz/) | 使用 Boltz-1/Boltz-2 进行结构预测，这是一个开放的生物分子结构预测器，用于蛋白质复合物和结合剂验证。 |
| [boltzgen](skills/boltzgen/) | 使用 BoltzGen 扩散模型进行全原子蛋白质设计。从一开始就具有侧链感知的设计，可围绕小分子或配体进行设计。 |
| [chai](skills/chai/) | 使用 Chai-1 基础模型进行蛋白质-蛋白质复合物结构预测、结合剂验证和蛋白质-小分子相互作用预测。 |
| [rfdiffusion](skills/rfdiffusion/) | 使用 RFdiffusion 扩散模型从头生成蛋白质骨架，用于结合剂支架设计和蛋白质从头设计。 |
| [bindcraft](skills/bindcraft/) | 使用 BindCraft 幻觉进行端到端结合剂设计，内置 AF2 验证，用于高质量结合剂设计活动。 |
| [binder-design](skills/binder-design/) | 选择合适蛋白质结合剂设计工具（BoltzGen、BindCraft 或 RFdiffusion）并规划结合剂设计活动的指导。 |
| [proteinmpnn](skills/proteinmpnn/) | 使用 ProteinMPNN 逆折叠设计蛋白质序列，用于 RFdiffusion 骨架的序列设计、序列重设计和固定位置设计。 |
| [ligandmpnn](skills/ligandmpnn/) | 使用 LigandMPNN 进行配体感知蛋白质序列设计，围绕小分子设计序列、酶活性位点设计和结合口袋优化。 |
| [solublempnn](skills/solublempnn/) | 使用 SolubleMPNN 进行溶解性优化的蛋白质序列设计，用于大肠杆菌表达优化、减少聚集和溶解性改善。 |
| [foldseek](skills/foldseek/) | 使用 Foldseek 进行结构相似性搜索，在 PDB/AFDB 数据库中查找相似结构，进行结构同源性搜索和进化关系发现。 |
| [ipsae](skills/ipsae/) | 使用 ipSAE（来自对齐误差的蛋白间评分）对结合剂设计进行排名，用于对 BindCraft 或 RFdiffusion 输出进行筛选。 |
| [pdb](skills/pdb/) | 从 RCSB PDB 按 PDB ID 获取并分析蛋白质结构，搜索相似结构，为结合剂设计准备靶点。 |
| [protein-design-workflow](skills/protein-design-workflow/) | 蛋白质设计流程的端到端指导，从项目启动到实验验证的逐步工作流指南。 |
| [protein-qc](skills/protein-qc/) | 蛋白质设计的质量控制指标和过滤阈值：pLDDT、PAE、ipTM，用于结合、表达和结构评估。 |
| [cell-free-expression](skills/cell-free-expression/) | 无细胞蛋白质合成（CFPS）优化指导、低产量/聚集故障排除和 DNA 模板设计优化。 |
| [binding-characterization](skills/binding-characterization/) | SPR 和 BLI 结合表征实验指导，动力学数据解读和结合信号不良故障排除。 |

</details>

### 单细胞与轨迹分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [scvelo](skills/scvelo/) | RNA速度分析。从未剪接/剪接mRNA动态估计细胞状态转变，推断轨迹方向，计算潜伏时间，识别scRNA-seq数据中的驱动基因。 |

</details>

### 系统发育与网络分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [phylogenetics](skills/phylogenetics/) | 使用MAFFT、IQ-TREE 2和FastTree构建和分析系统发育树。进化分析、微生物基因组学、病毒系统动力学和分子钟研究。 |
| [networkx](skills/networkx/) | Python网络和图分析。生物网络分析、蛋白质相互作用网络、通路图、社区检测和中心性度量。 |
| [torch-geometric](skills/torch-geometric/) | 用于分子属性预测、药物-靶点相互作用建模和生物图几何深度学习的图神经网络（PyG）。 |

</details>

</details>

## ⚙️ ClawBio 管道

<details open>
<summary>展开/收起该大类</summary>

### 生物信息学编排与管道 (ClawBio)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-orchestrator](skills/bio-orchestrator/) | 将生物信息学请求路由到专业子技能的元代理。处理文件类型检测（VCF、FASTQ、BAM、PDB、h5ad）、分析规划、报告生成和可重现性导出。 |
| [scrna-orchestrator](skills/scrna-orchestrator/) | 本地Scanpy单细胞RNA-seq管道：QC、聚类、标记基因发现和从原始计数.h5ad文件进行两组差异表达分析。 |
| [seq-wrangler](skills/seq-wrangler/) | 序列QC、比对和BAM处理。封装FastQC、BWA/Bowtie2、SAMtools实现自动化读长转BAM管道。 |
| [vcf-annotator](skills/vcf-annotator/) | 使用VEP、ClinVar、gnomAD频率和祖先背景注释VCF变异。生成优先级排列的变异报告。 |
| [repro-enforcer](skills/repro-enforcer/) | 将生物信息学分析导出为可重现包，包含Conda环境、Singularity容器定义和Nextflow管道。 |
| [galaxy-bridge](skills/galaxy-bridge/) | Galaxy工具发现、推荐和执行 — 来自usegalaxy.org的8,000+生物信息学工具，多信号评分和工作流程建议。 |

</details>

### 基因组学、祖先分析与药物基因组学 (ClawBio)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [gwas-lookup](skills/gwas-lookup/) | 跨9个基因组数据库的联合变异查询：GWAS Catalog、Open Targets、PheWeb（UKB、FinnGen、BBJ）、GTEx、eQTL Catalogue等。 |
| [gwas-prs](skills/gwas-prs/) | 使用PGS Catalog从DTC基因数据（23andMe/AncestryDNA）计算多基因风险评分。 |
| [pharmgx-reporter](skills/pharmgx-reporter/) | 来自DTC基因数据的药物基因组报告 — 12个基因、31个SNP、51种药物，含CPIC指南和个性化剂量卡。 |
| [clinpgx](skills/clinpgx/) | 查询ClinPGx API获取药物基因组基因-药物数据、临床注释、CPIC指南和FDA药品标签。 |
| [drug-photo](skills/drug-photo/) | 通过Claude视觉从药品包装照片识别药物，然后检索基因型知情的剂量指导。 |
| [claw-ancestry-pca](skills/claw-ancestry-pca/) | 与西蒙斯基因组多样性项目（345个样本，164个全球群体）的祖先分解PCA分析。 |
| [genome-compare](skills/genome-compare/) | 通过IBS和EM混合将基因组与参考个体比较并估计祖先组成。 |
| [equity-scorer](skills/equity-scorer/) | 从VCF或祖先数据计算HEIM多样性和公平性指标。生成杂合度、FST、PCA图和HEIM公平评分报告。 |
| [claw-metagenomics](skills/claw-metagenomics/) | 鸟枪法宏基因组分析：分类（Kraken2/Bracken）、耐药组（CARD/RGI）和功能通路（HUMAnN3）。 |
| [ukb-navigator](skills/ukb-navigator/) | UK Biobank 12,000+数据字段和出版物的语义搜索 — 为研究问题找到合适的变量。 |

</details>

### 结构生物学与文献综合 (ClawBio)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [struct-predictor](skills/struct-predictor/) | 使用AlphaFold、Boltz或Chai进行本地蛋白质结构预测。比较结构、计算RMSD、可视化3D模型。 |
| [lit-synthesizer](skills/lit-synthesizer/) | 搜索PubMed和bioRxiv，用LLM摘要论文，构建引用图，生成文献综述章节。 |
| [claw-semantic-sim](skills/claw-semantic-sim/) | 使用PubMedBERT嵌入计算疾病研究文献的语义相似性指数。计算研究公平性指标（HEIM）。 |
| [labstep](skills/labstep/) | 通过Labstep API与电子实验记录本交互。查询实验、协议、资源和库存。 |
| [profile-report](skills/profile-report/) | 生成结构化生物信息学分析概要报告。 |

</details>

</details>

## 🧠 BioOS 扩展套件

<details open>
<summary>展开/收起该大类</summary>

### BioOS 扩展生物信息工具套件

#### 序列与比对

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-alignment-sorting](skills/bio-alignment-sorting/) | 使用 samtools sort 按坐标或名称排序 SAM/BAM 文件。 |
| [bio-alignment-filtering](skills/bio-alignment-filtering/) | 按标志、质量、区域或配对状态过滤比对结果。 |
| [bio-alignment-indexing](skills/bio-alignment-indexing/) | 使用 samtools index 为 BAM/CRAM 文件建立索引以实现随机访问。 |
| [bio-alignment-validation](skills/bio-alignment-validation/) | 验证比对文件完整性，检测截断或损坏文件。 |
| [bio-alignment-files-bam-statistics](skills/bio-alignment-files-bam-statistics/) | 计算比对统计数据：flagstat、idxstats、覆盖深度。 |
| [bio-sam-bam-basics](skills/bio-sam-bam-basics/) | 使用 samtools/pysam 读取、检查和操作 SAM/BAM 文件。 |
| [bio-duplicate-handling](skills/bio-duplicate-handling/) | 使用 Picard 或 samtools markdup 标记和去除 PCR 重复。 |
| [bio-pileup-generation](skills/bio-pileup-generation/) | 从 BAM 生成碱基级 pileup 用于变异检测和覆盖分析。 |
| [bio-reference-operations](skills/bio-reference-operations/) | 下载、索引和管理参考基因组 FASTA 文件。 |
| [bio-blast-searches](skills/bio-blast-searches/) | 针对本地或远程数据库运行 BLAST 搜索以进行序列同源性分析。 |
| [bio-local-blast](skills/bio-local-blast/) | 本地搭建并运行 BLAST+，支持自定义数据库。 |
| [bio-entrez-search](skills/bio-entrez-search/) | 搜索 NCBI Entrez 数据库（PubMed、基因、核苷酸、蛋白质、SRA）。 |
| [bio-entrez-fetch](skills/bio-entrez-fetch/) | 通过登录号或 UID 从 NCBI Entrez 获取记录。 |
| [bio-entrez-link](skills/bio-entrez-link/) | 跨 NCBI Entrez 数据库检索关联记录。 |
| [bio-uniprot-access](skills/bio-uniprot-access/) | 查询 UniProt 获取蛋白质序列、注释和交叉引用。 |
| [bio-geo-data](skills/bio-geo-data/) | 下载和解析 GEO 数据集和系列矩阵。 |
| [bio-sra-data](skills/bio-sra-data/) | 使用 fasterq-dump 从 NCBI SRA 下载原始测序数据。 |
| [bio-batch-downloads](skills/bio-batch-downloads/) | 批量从 NCBI、EBI、Ensembl 下载生物信息学数据。 |

</details>

#### 序列分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-seq-objects](skills/bio-seq-objects/) | 使用 BioPython 序列对象：SeqRecord、特征、注释。 |
| [bio-sequence-properties](skills/bio-sequence-properties/) | 计算序列属性：MW、pI、疏水性、消光系数。 |
| [bio-sequence-similarity](skills/bio-sequence-similarity/) | 通过成对比对和百分比同一性计算序列相似性。 |
| [bio-sequence-slicing](skills/bio-sequence-slicing/) | 从 FASTA/FASTQ 中切片、提取和操作子序列。 |
| [bio-motif-search](skills/bio-motif-search/) | 使用 FIMO、MAST 或正则表达式搜索调控基序。 |
| [bio-codon-usage](skills/bio-codon-usage/) | 分析密码子使用偏差并优化表达序列。 |
| [bio-transcription-translation](skills/bio-transcription-translation/) | 转录和翻译 DNA 序列，处理遗传密码变体。 |
| [bio-reverse-complement](skills/bio-reverse-complement/) | 计算反向互补序列，支持链感知序列操作。 |
| [bio-primer-design-primer-basics](skills/bio-primer-design-primer-basics/) | 使用 Primer3 为标准扩增设计 PCR 引物。 |
| [bio-primer-design-primer-validation](skills/bio-primer-design-primer-validation/) | 通过 BLAST 和热力学分析验证引物特异性。 |
| [bio-primer-design-qpcr-primers](skills/bio-primer-design-qpcr-primers/) | 设计具有效率和特异性优化的 qPCR/RT-PCR 引物。 |
| [bio-restriction-sites](skills/bio-restriction-sites/) | 在 DNA 序列中查找限制酶识别位点。 |
| [bio-restriction-mapping](skills/bio-restriction-mapping/) | 创建限制图谱和体外酶切模式。 |
| [bio-restriction-fragment-analysis](skills/bio-restriction-fragment-analysis/) | 分析克隆和凝胶预测的限制片段模式。 |
| [bio-restriction-enzyme-selection](skills/bio-restriction-enzyme-selection/) | 根据切割位点和兼容性选择克隆用限制酶。 |

</details>

#### 读段比对

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-read-alignment-bwa-alignment](skills/bio-read-alignment-bwa-alignment/) | 使用 BWA-MEM 将短读段比对到参考基因组。 |
| [bio-read-alignment-bowtie2-alignment](skills/bio-read-alignment-bowtie2-alignment/) | 使用 Bowtie2 比对短读段，支持局部和端对端模式。 |
| [bio-read-alignment-hisat2-alignment](skills/bio-read-alignment-hisat2-alignment/) | 使用 HISAT2 进行剪接感知 RNA-seq 比对。 |
| [bio-read-alignment-star-alignment](skills/bio-read-alignment-star-alignment/) | 使用高速 STAR 比对器进行 RNA-seq，支持连接检测。 |

</details>

#### 基因组组装

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-genome-assembly-long-read-assembly](skills/bio-genome-assembly-long-read-assembly/) | 使用 Flye 或 Canu 从 ONT/PacBio 长读段进行从头组装。 |
| [bio-genome-assembly-hifi-assembly](skills/bio-genome-assembly-hifi-assembly/) | 使用 Hifiasm 对 HiFi (CCS) 读段进行高精度基因组组装。 |
| [bio-genome-assembly-short-read-assembly](skills/bio-genome-assembly-short-read-assembly/) | 使用 SPAdes 进行 Illumina 从头组装，支持宏基因组/细菌/转录组。 |
| [bio-genome-assembly-metagenome-assembly](skills/bio-genome-assembly-metagenome-assembly/) | 宏基因组组装：共组装、分箱、MAG 恢复。 |
| [bio-genome-assembly-assembly-qc](skills/bio-genome-assembly-assembly-qc/) | 使用 QUAST、BUSCO 和 NGA50 指标评估组装质量。 |
| [bio-genome-assembly-assembly-polishing](skills/bio-genome-assembly-assembly-polishing/) | 使用 Medaka (ONT) 或 NextPolish (Illumina) 打磨组装结果。 |
| [bio-genome-assembly-scaffolding](skills/bio-genome-assembly-scaffolding/) | 使用 Hi-C、光学图谱或长读段对 contig 进行支架化。 |
| [bio-genome-assembly-contamination-detection](skills/bio-genome-assembly-contamination-detection/) | 检测和去除组装基因组中的污染。 |

</details>

#### 基因组区间与注释

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-genome-intervals-bed-file-basics](skills/bio-genome-intervals-bed-file-basics/) | 使用 pybedtools/bedtools 读取、写入和过滤 BED 文件。 |
| [bio-genome-intervals-interval-arithmetic](skills/bio-genome-intervals-interval-arithmetic/) | 对基因组区间进行交集、相减、合并和补集操作。 |
| [bio-genome-intervals-proximity-operations](skills/bio-genome-intervals-proximity-operations/) | 查找最近特征并计算区间之间的距离。 |
| [bio-genome-intervals-coverage-analysis](skills/bio-genome-intervals-coverage-analysis/) | 计算基因组区域的读段深度覆盖率。 |
| [bio-genome-intervals-bigwig-tracks](skills/bio-genome-intervals-bigwig-tracks/) | 从 BAM/bedGraph 创建和查询 BigWig 信号轨迹。 |
| [bio-genome-intervals-gtf-gff-handling](skills/bio-genome-intervals-gtf-gff-handling/) | 解析和操作 GTF/GFF 注释文件。 |
| [bio-bedgraph-handling](skills/bio-bedgraph-handling/) | 处理 bedGraph 覆盖文件：算术运算、归一化、格式转换。 |

</details>

#### RNA 定量

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-rna-quantification-featurecounts-counting](skills/bio-rna-quantification-featurecounts-counting/) | 使用 subread 包的 featureCounts 统计每个基因的读段数。 |
| [bio-rna-quantification-alignment-free-quant](skills/bio-rna-quantification-alignment-free-quant/) | 使用 Salmon 或 Kallisto 进行伪比对定量。 |
| [bio-rna-quantification-tximport-workflow](skills/bio-rna-quantification-tximport-workflow/) | 使用 tximport 将 Salmon/Kallisto 定量结果导入 R/DESeq2。 |
| [bio-rna-quantification-count-matrix-qc](skills/bio-rna-quantification-count-matrix-qc/) | QC 计数矩阵：文库大小、零膨胀、基因检测率。 |
| [bio-expression-matrix-counts-ingest](skills/bio-expression-matrix-counts-ingest/) | 从多种定量工具加载和验证计数矩阵。 |
| [bio-expression-matrix-gene-id-mapping](skills/bio-expression-matrix-gene-id-mapping/) | 在 Ensembl、Entrez、HGNC 和基因符号标识符之间映射。 |
| [bio-expression-matrix-metadata-joins](skills/bio-expression-matrix-metadata-joins/) | 将样品元数据连接到表达矩阵用于下游分析。 |
| [bio-expression-matrix-sparse-handling](skills/bio-expression-matrix-sparse-handling/) | 使用 scipy 稀疏格式高效处理稀疏计数矩阵。 |

</details>

#### 表观转录组与 CLIP-seq

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-epitranscriptomics-merip-preprocessing](skills/bio-epitranscriptomics-merip-preprocessing/) | 预处理 MeRIP-seq 数据用于 m6A 甲基化分析。 |
| [bio-epitranscriptomics-m6a-peak-calling](skills/bio-epitranscriptomics-m6a-peak-calling/) | 使用 exomePeak2 或 MACS2 从 MeRIP-seq 中检测 m6A 峰。 |
| [bio-epitranscriptomics-m6anet-analysis](skills/bio-epitranscriptomics-m6anet-analysis/) | 使用 m6Anet 深度学习进行纳米孔直接 RNA m6A 检测。 |
| [bio-epitranscriptomics-m6a-differential](skills/bio-epitranscriptomics-m6a-differential/) | 不同条件之间的差异 m6A 甲基化分析。 |
| [bio-epitranscriptomics-modification-visualization](skills/bio-epitranscriptomics-modification-visualization/) | 可视化 RNA 修饰谱和 metagene 图。 |
| [bio-clip-seq-clip-preprocessing](skills/bio-clip-seq-clip-preprocessing/) | 预处理 CLIP-seq/eCLIP 数据：接头修剪、去多重化。 |
| [bio-clip-seq-clip-alignment](skills/bio-clip-seq-clip-alignment/) | 使用 STAR 比对 CLIP-seq 读段，处理唯一映射读段。 |
| [bio-clip-seq-clip-peak-calling](skills/bio-clip-seq-clip-peak-calling/) | 使用 PureCLIP 或 MACS2 从 CLIP-seq 中检测 RBP 结合峰。 |
| [bio-clip-seq-binding-site-annotation](skills/bio-clip-seq-binding-site-annotation/) | 用基因组特征和 RNA 区域注释 CLIP-seq 峰。 |
| [bio-clip-seq-clip-motif-analysis](skills/bio-clip-seq-clip-motif-analysis/) | 从 CLIP-seq 峰序列中发现 RBP 结合基序。 |

</details>

#### 小 RNA-seq

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-small-rna-seq-smrna-preprocessing](skills/bio-small-rna-seq-smrna-preprocessing/) | 预处理小 RNA-seq：接头修剪、大小筛选。 |
| [bio-small-rna-seq-mirdeep2-analysis](skills/bio-small-rna-seq-mirdeep2-analysis/) | 使用 miRDeep2 鉴定和定量已知/新型 miRNA。 |
| [bio-small-rna-seq-mirge3-analysis](skills/bio-small-rna-seq-mirge3-analysis/) | 使用 miRge3.0 进行 miRNA 注释和定量。 |
| [bio-small-rna-seq-target-prediction](skills/bio-small-rna-seq-target-prediction/) | 使用 TargetScan 或 miRDB 预测 miRNA 靶基因。 |
| [bio-small-rna-seq-differential-mirna](skills/bio-small-rna-seq-differential-mirna/) | 使用 DESeq2/edgeR 进行差异 miRNA 表达分析。 |

</details>

#### 群体遗传学与单体型分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-population-genetics-plink-basics](skills/bio-population-genetics-plink-basics/) | PLINK2 用于 GWAS QC、LD 修剪和基础群体遗传学。 |
| [bio-population-genetics-population-structure](skills/bio-population-genetics-population-structure/) | 使用 PCA、ADMIXTURE 和 STRUCTURE 进行群体分层分析。 |
| [bio-population-genetics-linkage-disequilibrium](skills/bio-population-genetics-linkage-disequilibrium/) | 计算 LD 指标（r²、D'）和 LD 衰减分析。 |
| [bio-population-genetics-association-testing](skills/bio-population-genetics-association-testing/) | 使用 PLINK、BOLT-LMM 或 SAIGE 进行 GWAS 关联检验。 |
| [bio-population-genetics-scikit-allel-analysis](skills/bio-population-genetics-scikit-allel-analysis/) | 使用 scikit-allel 进行群体遗传学分析：多样性、Fst、单倍型。 |
| [bio-population-genetics-selection-statistics](skills/bio-population-genetics-selection-statistics/) | 检测自然选择信号：iHS、XP-EHH、Tajima's D。 |
| [bio-phasing-imputation-haplotype-phasing](skills/bio-phasing-imputation-haplotype-phasing/) | 使用 SHAPEIT4 或 BEAGLE 进行变异位点分型。 |
| [bio-phasing-imputation-genotype-imputation](skills/bio-phasing-imputation-genotype-imputation/) | 使用 Michigan/TOPMed 填补服务器进行缺失基因型填补。 |
| [bio-phasing-imputation-reference-panels](skills/bio-phasing-imputation-reference-panels/) | 选择和准备用于填补的参考面板（1KGP、HRC、TOPMed）。 |
| [bio-phasing-imputation-imputation-qc](skills/bio-phasing-imputation-imputation-qc/) | QC 填补数据：R² 过滤、INFO 分数、等位基因一致性。 |

</details>

#### 比较基因组与系统进化

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-comparative-genomics-ortholog-inference](skills/bio-comparative-genomics-ortholog-inference/) | 使用 OrthoFinder 或 OMA 推断直系同源和旁系同源基因。 |
| [bio-comparative-genomics-synteny-analysis](skills/bio-comparative-genomics-synteny-analysis/) | 使用 MCScan 或 SyRI 检测基因组间共线性块。 |
| [bio-comparative-genomics-positive-selection](skills/bio-comparative-genomics-positive-selection/) | 使用 PAML、HyPhy 或 dN/dS 比值检验正选择。 |
| [bio-comparative-genomics-hgt-detection](skills/bio-comparative-genomics-hgt-detection/) | 检测微生物基因组中的水平基因转移事件。 |
| [bio-comparative-genomics-ancestral-reconstruction](skills/bio-comparative-genomics-ancestral-reconstruction/) | 使用 ASR 方法重建祖先序列和性状。 |
| [bio-phylo-tree-io](skills/bio-phylo-tree-io/) | 以 Newick、Nexus、PhyloXML 格式读写系统发育树。 |
| [bio-phylo-modern-tree-inference](skills/bio-phylo-modern-tree-inference/) | 使用 IQ-TREE 2 或 FastTree 进行最大似然树推断。 |
| [bio-phylo-tree-manipulation](skills/bio-phylo-tree-manipulation/) | 对系统发育树进行根定、修剪、重排序和注释。 |
| [bio-phylo-tree-visualization](skills/bio-phylo-tree-visualization/) | 使用 iTOL、ETE3 或 ggtree 可视化系统发育树。 |
| [bio-phylo-distance-calculations](skills/bio-phylo-distance-calculations/) | 计算成对系统发育距离和多样性指标。 |

</details>

#### 系统生物学与代谢建模

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-systems-biology-flux-balance-analysis](skills/bio-systems-biology-flux-balance-analysis/) | 使用 COBRApy 进行代谢网络建模的通量平衡分析（FBA）。 |
| [bio-systems-biology-metabolic-reconstruction](skills/bio-systems-biology-metabolic-reconstruction/) | 从基因组注释重建全基因组代谢模型。 |
| [bio-systems-biology-gene-essentiality](skills/bio-systems-biology-gene-essentiality/) | 通过代谢模型中的单基因敲除预测必需基因。 |
| [bio-systems-biology-context-specific-models](skills/bio-systems-biology-context-specific-models/) | 从表达数据构建情境特异性代谢模型（GIMME、iMAT）。 |
| [bio-systems-biology-model-curation](skills/bio-systems-biology-model-curation/) | 整理 SBML 代谢模型：质量/电荷平衡、缺口填充。 |

</details>

#### 实验设计、机器学习与报告

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-experimental-design-sample-size](skills/bio-experimental-design-sample-size/) | 组学实验的功效分析和样本量计算。 |
| [bio-experimental-design-power-analysis](skills/bio-experimental-design-power-analysis/) | 检测差异信号的统计功效分析。 |
| [bio-experimental-design-batch-design](skills/bio-experimental-design-batch-design/) | 使用 ComBat 设计优化样品批次以最小化混淆效应。 |
| [bio-experimental-design-multiple-testing](skills/bio-experimental-design-multiple-testing/) | 多重检验校正：Bonferroni、BH/FDR、q 值。 |
| [bio-machine-learning-omics-classifiers](skills/bio-machine-learning-omics-classifiers/) | 在组学数据上训练分类器：随机森林、SVM、XGBoost。 |
| [bio-machine-learning-biomarker-discovery](skills/bio-machine-learning-biomarker-discovery/) | 使用 LASSO、弹性网、SHAP 从组学数据中识别生物标志物。 |
| [bio-machine-learning-model-validation](skills/bio-machine-learning-model-validation/) | 交叉验证、AUC-ROC、校准和置换检验。 |
| [bio-machine-learning-survival-analysis](skills/bio-machine-learning-survival-analysis/) | 生存分析机器学习：RSF、DeepSurv、CoxBoost。 |
| [bio-machine-learning-atlas-mapping](skills/bio-machine-learning-atlas-mapping/) | 使用 scANVI 或 Symphony 将查询细胞映射到参考图谱。 |
| [bio-machine-learning-prediction-explanation](skills/bio-machine-learning-prediction-explanation/) | 使用 SHAP 和特征重要性解释组学机器学习预测。 |
| [bio-reporting-automated-qc-reports](skills/bio-reporting-automated-qc-reports/) | 为组学管道生成自动化 MultiQC 风格报告。 |
| [bio-reporting-jupyter-reports](skills/bio-reporting-jupyter-reports/) | 创建带有可重复分析代码的 Jupyter notebook 报告。 |
| [bio-reporting-rmarkdown-reports](skills/bio-reporting-rmarkdown-reports/) | 渲染带有集成图表和统计数据的 Rmarkdown 报告。 |
| [bio-reporting-quarto-reports](skills/bio-reporting-quarto-reports/) | 从分析代码构建 Quarto 多格式报告（HTML/PDF）。 |
| [bio-reporting-figure-export](skills/bio-reporting-figure-export/) | 以指定 DPI 导出 PDF/SVG/TIFF 格式的出版质量图表。 |
| [bio-research-tools-biomarker-signature-studio](skills/bio-research-tools-biomarker-signature-studio/) | 构建、验证和可视化多组学生物标志物特征。 |

</details>

#### 端到端工作流管道

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-workflows-fastq-to-variants](skills/bio-workflows-fastq-to-variants/) | 完整的 FASTQ → 比对 → 变异检测管道。 |
| [bio-workflows-rnaseq-to-de](skills/bio-workflows-rnaseq-to-de/) | RNA-seq → 比对 → 计数 → DESeq2 差异表达。 |
| [bio-workflows-scrnaseq-pipeline](skills/bio-workflows-scrnaseq-pipeline/) | 单细胞 RNA-seq 端到端：Cell Ranger → Scanpy → 聚类。 |
| [bio-workflows-atacseq-pipeline](skills/bio-workflows-atacseq-pipeline/) | ATAC-seq：修剪 → 比对 → 峰检测 → 差异分析。 |
| [bio-workflows-chipseq-pipeline](skills/bio-workflows-chipseq-pipeline/) | ChIP-seq：比对 → 峰检测 → 基序分析 → 注释。 |
| [bio-workflows-methylation-pipeline](skills/bio-workflows-methylation-pipeline/) | WGBS/RRBS：bismark 比对 → 甲基化检测 → DMR 识别。 |
| [bio-workflows-metagenomics-pipeline](skills/bio-workflows-metagenomics-pipeline/) | 宏基因组：QC → 分类 → 功能注释 → AMR。 |
| [bio-workflows-metabolomics-pipeline](skills/bio-workflows-metabolomics-pipeline/) | LC-MS/GC-MS：预处理 → 注释 → 统计分析。 |
| [bio-workflows-proteomics-pipeline](skills/bio-workflows-proteomics-pipeline/) | DDA/DIA 蛋白质组：搜索 → 定量 → 差异丰度分析。 |
| [bio-workflows-gwas-pipeline](skills/bio-workflows-gwas-pipeline/) | GWAS：QC → 填补 → 关联 → 精细定位 → 注释。 |
| [bio-workflows-somatic-variant-pipeline](skills/bio-workflows-somatic-variant-pipeline/) | 使用 GATK Mutect2/Strelka2 进行肿瘤-正常体细胞变异检测。 |
| [bio-workflows-cnv-pipeline](skills/bio-workflows-cnv-pipeline/) | 拷贝数变异检测：WGS/WES CNV 检测和注释。 |
| [bio-workflows-spatial-pipeline](skills/bio-workflows-spatial-pipeline/) | 空间转录组：比对 → 解卷积 → 结构域检测。 |
| [bio-workflows-multi-omics-pipeline](skills/bio-workflows-multi-omics-pipeline/) | 多组学整合管道：MOFA、SNF、相似性网络融合。 |
| [bio-workflows-multiome-pipeline](skills/bio-workflows-multiome-pipeline/) | 10x Multiome：联合 scRNA-seq + scATAC-seq 处理和整合。 |
| [bio-workflows-hic-pipeline](skills/bio-workflows-hic-pipeline/) | Hi-C 接触图生成、归一化、TAD/环路检测。 |
| [bio-workflows-neoantigen-pipeline](skills/bio-workflows-neoantigen-pipeline/) | 新抗原预测：体细胞变异 → MHC 结合 → 免疫原性。 |
| [bio-workflows-microbiome-pipeline](skills/bio-workflows-microbiome-pipeline/) | 微生物组：16S/ITS 扩增子或散弹枪 → 多样性 → 差异分析。 |
| [bio-workflows-crispr-screen-pipeline](skills/bio-workflows-crispr-screen-pipeline/) | CRISPR 筛选：向导计数 → MAGeCK → 命中检测 → 可视化。 |
| [bio-workflows-crispr-editing-pipeline](skills/bio-workflows-crispr-editing-pipeline/) | CRISPR 编辑：扩增子测序 → CRISPResso2 → 结果分析。 |
| [bio-workflows-tcr-pipeline](skills/bio-workflows-tcr-pipeline/) | TCR/BCR：V(D)J 比对 → 克隆型 → 文库分析。 |
| [bio-workflows-riboseq-pipeline](skills/bio-workflows-riboseq-pipeline/) | Ribo-seq：足迹比对 → 周期性 → ORF 检测。 |
| [bio-workflows-smrna-pipeline](skills/bio-workflows-smrna-pipeline/) | 小 RNA-seq：miRNA 鉴定 → 定量 → 差异表达分析。 |
| [bio-workflows-merip-pipeline](skills/bio-workflows-merip-pipeline/) | MeRIP-seq：m6A 峰检测 → 差异分析 → 基序分析。 |
| [bio-workflows-clip-pipeline](skills/bio-workflows-clip-pipeline/) | CLIP-seq：峰检测 → 结合位点注释 → 基序发现。 |
| [bio-workflows-imc-pipeline](skills/bio-workflows-imc-pipeline/) | 成像质谱细胞仪：分割 → 表型鉴定 → 空间分析。 |
| [bio-workflows-cytometry-pipeline](skills/bio-workflows-cytometry-pipeline/) | 流式/质谱细胞仪：QC → 设门 → 聚类 → 差异分析。 |
| [bio-workflows-longread-sv-pipeline](skills/bio-workflows-longread-sv-pipeline/) | 长读段结构变异检测和注释管道。 |
| [bio-workflows-genome-assembly-pipeline](skills/bio-workflows-genome-assembly-pipeline/) | 从头基因组组装：原始读段 → 组装 → QC → 注释。 |
| [bio-workflows-outbreak-pipeline](skills/bio-workflows-outbreak-pipeline/) | 病原体基因组：组装 → 分型 → 系统动力学 → 传播分析。 |
| [bio-workflows-biomarker-pipeline](skills/bio-workflows-biomarker-pipeline/) | 生物标志物发现：组学 → 特征选择 → 验证 → 报告。 |
| [bio-workflows-metabolic-modeling-pipeline](skills/bio-workflows-metabolic-modeling-pipeline/) | 代谢模型重建 → FBA → 模拟 → 可视化。 |
| [bio-splicing-pipeline](skills/bio-splicing-pipeline/) | 选择性剪接分析：rMATS → PSI → 差异分析 → sashimi 图。 |
| [bio-liquid-biopsy-pipeline](skills/bio-liquid-biopsy-pipeline/) | 液体活检：cfDNA/ctDNA QC → 突变检测 → TMB → MRD。 |
| [bio-workflow-management-snakemake-workflows](skills/bio-workflow-management-snakemake-workflows/) | 创建和管理 Snakemake 可重复生物信息工作流。 |
| [bio-workflow-management-nextflow-pipelines](skills/bio-workflow-management-nextflow-pipelines/) | 构建和运行 Nextflow (DSL2) 生物信息管道。 |
| [bio-workflow-management-cwl-workflows](skills/bio-workflow-management-cwl-workflows/) | 编写通用工作流语言（CWL）可移植工作流定义。 |
| [bio-workflow-management-wdl-workflows](skills/bio-workflow-management-wdl-workflows/) | 创建用于 Terra/Cromwell 生物信息执行的 WDL 工作流。 |
| [bio-workflows-expression-to-pathways](skills/bio-workflows-expression-to-pathways/) | 从差异表达结果到 GO/KEGG/Reactome 富集与通路可视化的端到端工作流。 |

</details>

#### 生信数据可视化

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bio-data-visualization-heatmaps-clustering](skills/bio-data-visualization-heatmaps-clustering/) | 使用 ComplexHeatmap 或 seaborn 进行层次聚类热图。 |
| [bio-data-visualization-volcano-customization](skills/bio-data-visualization-volcano-customization/) | 使用 ggplot2 或 matplotlib 为差异表达结果定制火山图。 |
| [bio-data-visualization-circos-plots](skills/bio-data-visualization-circos-plots/) | 使用 Circos 或 pycirclize 进行环形基因组可视化。 |
| [bio-data-visualization-genome-browser-tracks](skills/bio-data-visualization-genome-browser-tracks/) | 从 BAM/BigWig 生成基因组浏览器轨迹和 IGV 会话。 |
| [bio-data-visualization-genome-tracks](skills/bio-data-visualization-genome-tracks/) | 使用 pyGenomeTracks 绘制多面板基因组轨迹图。 |
| [bio-data-visualization-ggplot2-fundamentals](skills/bio-data-visualization-ggplot2-fundamentals/) | R ggplot2 用于出版质量基因组学和组学图表。 |
| [bio-data-visualization-interactive-visualization](skills/bio-data-visualization-interactive-visualization/) | 使用 Plotly、Bokeh 或 shiny 进行交互式组学可视化。 |
| [bio-data-visualization-upset-plots](skills/bio-data-visualization-upset-plots/) | UpSet 图用于多集合交集可视化。 |
| [bio-data-visualization-multipanel-figures](skills/bio-data-visualization-multipanel-figures/) | 使用 cowplot 或 patchwork 组合多面板出版图表。 |
| [bio-data-visualization-color-palettes](skills/bio-data-visualization-color-palettes/) | 科学色彩调色板：色盲友好、感知均匀、发散型。 |
| [bio-data-visualization-specialized-omics-plots](skills/bio-data-visualization-specialized-omics-plots/) | 专用图表：棒棒糖图（突变）、circomap、oncoprint。 |

</details>

### 肿瘤学与精准医学智能体 (21个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [autonomous-oncology-agent](skills/autonomous-oncology-agent/) | 自主肿瘤学研究智能体：文献挖掘、试验匹配、生物标志物分析和治疗假说生成。 |
| [precision-oncology-agent](skills/precision-oncology-agent/) | 精准肿瘤学：肿瘤分子分型 → 可操作变异 → 治疗建议。 |
| [pan-cancer-multiomics-agent](skills/pan-cancer-multiomics-agent/) | 泛癌多组学整合，用于跨癌症模式发现和驱动基因识别。 |
| [tumor-clonal-evolution-agent](skills/tumor-clonal-evolution-agent/) | 建模肿瘤克隆进化：从体细胞变异生成系统发育树和克隆动力学。 |
| [tumor-heterogeneity-agent](skills/tumor-heterogeneity-agent/) | 从大量和单细胞测序数据分析瘤内异质性。 |
| [tumor-mutational-burden-agent](skills/tumor-mutational-burden-agent/) | 计算 TMB 并评估其对免疫治疗反应的预测价值。 |
| [chromosomal-instability-agent](skills/chromosomal-instability-agent/) | 从拷贝数和 SV 数据量化染色体不稳定性（CIN）。 |
| [cancer-metabolism-agent](skills/cancer-metabolism-agent/) | 从转录组学和代谢组学数据分析肿瘤代谢重编程。 |
| [liquid-biopsy-analytics-agent](skills/liquid-biopsy-analytics-agent/) | 全面液体活检分析：ctDNA 检测、MRD 监测、治疗反应。 |
| [ctdna-dynamics-mrd-agent](skills/ctdna-dynamics-mrd-agent/) | 追踪 ctDNA 动力学用于微小残留病灶检测和治疗监测。 |
| [mrd-edge-detection-agent](skills/mrd-edge-detection-agent/) | 通过深度测序和错误抑制进行超灵敏 MRD 检测。 |
| [hrd-analysis-agent](skills/hrd-analysis-agent/) | 同源重组缺陷（HRD）分析用于 PARP 抑制剂反应预测。 |
| [computational-pathology-agent](skills/computational-pathology-agent/) | 计算病理学：WSI 分析、组织分割、组织学特征提取。 |
| [multimodal-radpath-fusion-agent](skills/multimodal-radpath-fusion-agent/) | 融合放射学和病理学影像用于综合癌症表型鉴定。 |
| [radiomics-pathomics-fusion-agent](skills/radiomics-pathomics-fusion-agent/) | 提取影像组学和病理组学特征并整合用于预测建模。 |
| [radgpt-radiology-reporter](skills/radgpt-radiology-reporter/) | AI 辅助放射学报告生成，基于影像学发现。 |
| [organoid-drug-response-agent](skills/organoid-drug-response-agent/) | 分析患者来源类器官的药物反应用于个体化治疗预测。 |
| [pdx-model-analysis-agent](skills/pdx-model-analysis-agent/) | 患者来源异种移植模型分析，用于药物疗效和生物标志物发现。 |
| [deep-visual-proteomics-agent](skills/deep-visual-proteomics-agent/) | 深度视觉蛋白质组学：激光捕获显微切割质谱数据的空间蛋白质组分析。 |
| [exosome-ev-analysis-agent](skills/exosome-ev-analysis-agent/) | 细胞外囊泡和外泌体分析：货物分析和生物标志物发现。 |
| [microbiome-cancer-agent](skills/microbiome-cancer-agent/) | 肿瘤微生物组分析及其在癌症进展和免疫治疗反应中的作用。 |
| [bio-fragment-analysis](skills/bio-fragment-analysis/) | 基于 FinaleToolkit/Griffin 分析 cfDNA 片段长度分布与 fragmentomics 特征，用于肿瘤检测与组织来源评估。 |

</details>

### 血液学与血液病 (7个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [myeloma-mrd-agent](skills/myeloma-mrd-agent/) | 从流式细胞仪和 NGS 数据评估多发性骨髓瘤 MRD。 |
| [mpn-progression-monitor-agent](skills/mpn-progression-monitor-agent/) | 从连续分子数据监测骨髓增殖性肿瘤进展。 |
| [mpn-research-assistant](skills/mpn-research-assistant/) | 骨髓增殖性肿瘤研究助手：文献、突变分析、治疗。 |
| [bone-marrow-ai-agent](skills/bone-marrow-ai-agent/) | 骨髓分析：原始细胞计数、免疫表型、疾病分类。 |
| [hemoglobinopathy-analysis-agent](skills/hemoglobinopathy-analysis-agent/) | 血红蛋白变体分析，镰状细胞和地中海贫血基因型-表型评估。 |
| [chip-clonal-hematopoiesis-agent](skills/chip-clonal-hematopoiesis-agent/) | 不确定潜力的克隆性造血（CHIP）变异检测和风险评估。 |
| [coagulation-thrombosis-agent](skills/coagulation-thrombosis-agent/) | 凝血途径分析、血栓形成倾向评估、抗凝指导。 |

</details>

### 免疫学与细胞治疗 (9个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [cart-design-optimizer-agent](skills/cart-design-optimizer-agent/) | 优化 CAR-T 细胞构建设计：scFv 选择、连接子、共刺激域。 |
| [armored-cart-design-agent](skills/armored-cart-design-agent/) | 设计装甲 CAR-T 细胞，带有细胞因子负载和耐药机制。 |
| [tcell-exhaustion-analysis-agent](skills/tcell-exhaustion-analysis-agent/) | 从 scRNA-seq 和 ATAC-seq 数据分析 T 细胞耗竭。 |
| [nk-cell-therapy-agent](skills/nk-cell-therapy-agent/) | NK 细胞治疗设计：受体工程、扩增方案、持久性。 |
| [tcr-pmhc-prediction-agent](skills/tcr-pmhc-prediction-agent/) | 预测 TCR-pMHC 结合亲和力和选择性用于 TCR 治疗设计。 |
| [tcr-repertoire-analysis-agent](skills/tcr-repertoire-analysis-agent/) | TCR 文库分析：V(D)J 使用、克隆型动力学、抗原特异性。 |
| [immune-checkpoint-combination-agent](skills/immune-checkpoint-combination-agent/) | 从肿瘤免疫微环境预测最佳免疫检查点联合策略。 |
| [tme-immune-profiling-agent](skills/tme-immune-profiling-agent/) | 肿瘤微环境免疫分型：细胞类型去卷积和空间定位。 |
| [cytokine-storm-analysis-agent](skills/cytokine-storm-analysis-agent/) | 细胞因子风暴检测、严重程度评分和干预建模。 |

</details>

### 单细胞与空间组学智能体 (15个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [cellagent-annotation](skills/cellagent-annotation/) | 使用标志基因数据库进行 AI 驱动的单细胞簇注释。 |
| [universal-single-cell-annotator](skills/universal-single-cell-annotator/) | 使用基础模型和多参考整合的通用 scRNA-seq 注释器。 |
| [scfoundation-model-agent](skills/scfoundation-model-agent/) | 单细胞基础模型推断（scFoundation/scGPT）用于零样本注释。 |
| [rna-velocity-agent](skills/rna-velocity-agent/) | 使用 scVelo 进行 RNA 速率分析，用于轨迹和命运决定推断。 |
| [spatial-transcriptomics-agent](skills/spatial-transcriptomics-agent/) | 端到端空间转录组分析：QC、去卷积、结构域检测。 |
| [spatial-transcriptomics-analysis](skills/spatial-transcriptomics-analysis/) | 使用 Squidpy 和 SpatialDE 进行空间转录组分析。 |
| [spatial-agent](skills/spatial-agent/) | 空间组学智能体：将空间数据与影像、蛋白质和基因组层整合。 |
| [nicheformer-spatial-agent](skills/nicheformer-spatial-agent/) | 使用 Nicheformer 基础模型进行空间生态位分析，研究组织微环境。 |
| [spatial-epigenomics-agent](skills/spatial-epigenomics-agent/) | 空间表观基因组分析：空间分辨的染色质可及性和基因调控。 |
| [bioinformatics-singlecell](skills/bioinformatics-singlecell/) | 通用单细胞生物信息学：聚类、轨迹、细胞通讯。 |
| [scrna-qc](skills/scrna-qc/) | 单细胞 RNA-seq 质量控制：双联体去除、环境 RNA、过滤阈值。 |
| [compbioagent-explorer](skills/compbioagent-explorer/) | 多组学数据集分析的计算生物学探索智能体。 |
| [simo-multiomics-integration-agent](skills/simo-multiomics-integration-agent/) | 使用 SIMO/MOFA+ 进行单细胞多组学整合，生成联合嵌入。 |
| [epigenomics-methylgpt-agent](skills/epigenomics-methylgpt-agent/) | 表观基因组和 DNA 甲基化分析，基于 MethylGPT 方法。 |
| [biomaster-workflows](skills/biomaster-workflows/) | BioMaster 工作流编排，用于端到端生物信息分析。 |

</details>

### 药物发现与分子设计 (35个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [agentd-drug-discovery](skills/agentd-drug-discovery/) | AgentD 自主药物发现：靶点识别、先导化合物筛选、ADMET 优化。 |
| [chematagent-drug-discovery](skills/chematagent-drug-discovery/) | CheMatAgent：化学感知药物设计，支持逆合成和性质优化。 |
| [chemcrow-drug-discovery](skills/chemcrow-drug-discovery/) | ChemCrow 药物发现工具包：网络搜索、Python、化学工具集成。 |
| [medea-therapeutic-discovery](skills/medea-therapeutic-discovery/) | MEDEA 治疗发现：多模态证据聚合用于靶点-疾病验证。 |
| [molecule-evolution-agent](skills/molecule-evolution-agent/) | 定向分子进化：用于化合物优化和文库设计的生成模型。 |
| [molecular-glue-discovery-agent](skills/molecular-glue-discovery-agent/) | 分子胶水发现：诱导邻近降解剂和三元复合物稳定剂。 |
| [protac-design-agent](skills/protac-design-agent/) | PROTAC 设计：E3 连接酶配体选择、连接子优化、三元复合物建模。 |
| [tpd-ternary-complex-agent](skills/tpd-ternary-complex-agent/) | 靶向蛋白降解三元复合物建模和协同性预测。 |
| [mage-antibody-generator](skills/mage-antibody-generator/) | MAGE 抗体生成器：序列设计、人源化、亲和力成熟。 |
| [antibody-design-agent](skills/antibody-design-agent/) | 抗体设计：表位定位、CDR 工程、双特异性构建。 |
| [aav-vector-design-agent](skills/aav-vector-design-agent/) | AAV 载体设计：衣壳选择、启动子优化、有效载荷容量。 |
| [protein-structure-prediction](skills/protein-structure-prediction/) | 使用 AlphaFold3、ESMFold 或 Boltz 进行蛋白质结构预测和比较。 |
| [crispr-guide-design](skills/crispr-guide-design/) | CRISPR 向导 RNA 设计，具有靶向评分和脱靶最小化。 |
| [crispr-offtarget-predictor](skills/crispr-offtarget-predictor/) | 使用 CRISPOR/Cas-OFFinder 全基因组预测 CRISPR Cas9/Cas12 脱靶位点。 |
| [chemical-property-lookup](skills/chemical-property-lookup/) | 通过名称/SMILES 从 PubChem、ChEMBL、DrugBank 查找化学性质。 |
| [chemistry-agent](skills/chemistry-agent/) | 通用化学智能体，用于合成规划、反应预测和性质计算。 |
| [cryoem-ai-drug-design-agent](skills/cryoem-ai-drug-design-agent/) | 从冷冻电镜结构进行 AI 引导药物设计：结合位点分析和对接。 |
| [time-resolved-cryoem-agent](skills/time-resolved-cryoem-agent/) | 动态结构生物学的时间分辨冷冻电镜分析。 |
| [cnv-caller-agent](skills/cnv-caller-agent/) | 专用 CNV 检测智能体，集成多种检测器并进行集成评分。 |
| [popeve-variant-predictor-agent](skills/popeve-variant-predictor-agent/) | 使用基于群体的 EVE 进化模型进行变异致病性预测。 |
| [varcadd-pathogenicity](skills/varcadd-pathogenicity/) | 从结构和进化角度对编码变异进行 VARCADD 致病性评分。 |
| [variant-interpretation-acmg](skills/variant-interpretation-acmg/) | 基于证据的 ACMG/AMP 变异解读与分类框架。 |
| [gene-panel-design-agent](skills/gene-panel-design-agent/) | 设计用于临床或研究测序应用的靶向基因组合。 |
| [pharmacogenomics-agent](skills/pharmacogenomics-agent/) | 药物基因组学分析：变异-药物相互作用预测和用药建议。 |
| [multi-ancestry-prs-agent](skills/multi-ancestry-prs-agent/) | 使用祖先特异性权重计算多祖先多基因风险评分。 |
| [prs-net-deep-learning-agent](skills/prs-net-deep-learning-agent/) | 使用 PRSnet 进行复杂性状的深度学习 PRS 预测。 |
| [cellfree-rna-agent](skills/cellfree-rna-agent/) | 无细胞 RNA 分析：血浆 cfRNA 分析用于液体活检诊断。 |
| [long-read-sequencing-agent](skills/long-read-sequencing-agent/) | 长读段测序分析：SV 检测、甲基化、异构体发现、组装。 |
| [bayesian-optimizer](skills/bayesian-optimizer/) | 贝叶斯优化用于生物医学研究的实验设计和超参数调优。 |

</details>

### 临床AI与医疗 (20个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [chatehr-clinician-assistant](skills/chatehr-clinician-assistant/) | EHR 临床助手：病历摘要、结构化数据提取、临床决策支持。 |
| [clinical-note-summarization](skills/clinical-note-summarization/) | 将临床病历摘要为带关键发现的结构化 SOAP 格式。 |
| [clinical-nlp-extractor](skills/clinical-nlp-extractor/) | 从非结构化文本中提取临床实体（诊断、药物、操作）。 |
| [ehr-fhir-integration](skills/ehr-fhir-integration/) | EHR-FHIR 整合：HL7 FHIR 资源创建、查询和工作流自动化。 |
| [fhir-development](skills/fhir-development/) | FHIR API 开发：构建 SMART on FHIR 应用和 FHIR 资源端点。 |
| [digital-twin-clinical-agent](skills/digital-twin-clinical-agent/) | 创建患者数字孪生用于治疗模拟和结局预测。 |
| [trial-eligibility-agent](skills/trial-eligibility-agent/) | 从 EHR 数据和试验标准评估患者临床试验入组资格。 |
| [trialgpt-matching](skills/trialgpt-matching/) | TrialGPT 患者-试验匹配，从临床病历进行资格评估。 |
| [wearable-analysis-agent](skills/wearable-analysis-agent/) | 分析可穿戴传感器数据：活动、睡眠、HRV、ECG 健康监测。 |
| [multimodal-medical-imaging](skills/multimodal-medical-imaging/) | 多模态医学影像分析：CT、MRI、PET 融合和分割。 |
| [prior-auth-coworker](skills/prior-auth-coworker/) | 保险审批流程的预授权工作流助手。 |
| [care-coordination](skills/care-coordination/) | 护理协调智能体：多学科团队沟通和护理计划管理。 |
| [claims-appeals](skills/claims-appeals/) | 保险理赔申诉：文档准备和拒绝原因分析。 |
| [lab-results](skills/lab-results/) | 实验室结果解读：参考范围、趋势分析、危急值提醒。 |
| [drug-interaction-checker](skills/drug-interaction-checker/) | 从患者用药清单检查药物相互作用并进行严重程度评分。 |
| [regulatory-drafter](skills/regulatory-drafter/) | 起草监管文件：FDA、EMA、ICH 文档准备。 |
| [regulatory-drafting](skills/regulatory-drafting/) | 医疗器械/药物申报的监管写作和文档结构化。 |
| [biomedical-data-analysis](skills/biomedical-data-analysis/) | 综合生物医学数据分析：统计、可视化和解读。 |
| [data-visualization-biomedical](skills/data-visualization-biomedical/) | 生物医学专用数据可视化：临床试验图、生存曲线、森林图。 |

</details>

### 研究基础设施与智能体框架 (20个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [biomni-general-agent](skills/biomni-general-agent/) | BioMni 通用生物医学智能体，用于灵活的多步骤研究任务。 |
| [biomni-research-agent](skills/biomni-research-agent/) | BioMni 研究智能体，集成文献、数据库和分析功能。 |
| [biokernel](skills/biokernel/) | BioKernel：用于生物信息工具编排的统一计算内核。 |
| [biomcp-server](skills/biomcp-server/) | BioMCP：用于生物信息工具访问的模型上下文协议服务器。 |
| [mcpmed-bioinformatics-server](skills/mcpmed-bioinformatics-server/) | 为智能体提供医学生物信息工具访问的 MCP 服务器。 |
| [kragen-knowledge-graph](skills/kragen-knowledge-graph/) | KRAGEN 知识图谱，用于生物医学实体关系和推理。 |
| [leads-literature-mining](skills/leads-literature-mining/) | LEADS 文献挖掘：从论文中自动提取生物学发现。 |
| [knowledge-synthesis](skills/knowledge-synthesis/) | 从多个生物医学来源综合知识，生成结构化摘要。 |
| [deep-research-swarm](skills/deep-research-swarm/) | 多智能体群体，用于深度科学研究和并行文献综合。 |
| [research-literature](skills/research-literature/) | 研究文献管理：搜索、整理和综合科学论文。 |
| [search-strategy](skills/search-strategy/) | 设计科学文献和数据库的系统检索策略。 |
| [scientific-manuscript](skills/scientific-manuscript/) | 科学手稿写作和修改，支持期刊特定格式。 |
| [cellular-senescence-agent](skills/cellular-senescence-agent/) | 细胞衰老分析：标志物评分、SASP 分析、组织老化评估。 |
| [ngs-analysis](skills/ngs-analysis/) | 下一代测序数据分析编排和 QC。 |
| [opentrons-protocol-agent](skills/opentrons-protocol-agent/) | Opentrons 液体处理器方案设计，用于自动化实验室工作流。 |
| [virtual-lab-agent](skills/virtual-lab-agent/) | 虚拟实验室智能体，用于体外实验模拟和方案优化。 |
| [data-visualization-expert](skills/data-visualization-expert/) | 复杂科学和临床数据集的专业数据可视化。 |
| [lobster-bioinformatics](skills/lobster-bioinformatics/) | 通过 Lobster AI 运行生物信息分析：scRNA-seq、bulk RNA-seq、文献挖掘、数据集发现、QC 和可视化。 |

</details>

</details>

## 📊 数据科学与工具

<details open>
<summary>展开/收起该大类</summary>

### 统计与数据分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [statistical-analysis](skills/statistical-analysis/) | 统计分析工具包。假设检验（t 检验、ANOVA、卡方）、回归、相关、贝叶斯统计、检验效能分析、假设检验、APA 报告。 |
| [statsmodels](skills/statsmodels/) | 统计建模工具包。OLS、GLM、逻辑回归、ARIMA、时间序列、假设检验、诊断、AIC/BIC，用于严格的统计推断。 |
| [pymc](skills/pymc/) | 使用 PyMC 进行贝叶斯建模。构建层次模型，MCMC（NUTS），变分推断，LOO/WAIC 比较，后验检验，用于概率编程。 |
| [simpy](skills/simpy/) | 基于过程的离散事件仿真框架，适用于临床系统建模：队列、资源、时间事件，用于医院工作流和患者流建模。 |
| [exploratory-data-analysis](skills/exploratory-data-analysis/) | 对 200+ 格式的科学数据文件进行综合探索性数据分析——结构、内容、质量评估和可视化。 |
| [data-stats-analysis](skills/data-stats-analysis/) | 统计检验、假设检验、相关分析和多重检验校正（OmicVerse，使用 scipy 和 statsmodels）。 |
| [data-transform](skills/data-transform/) | 使用 pandas 和 numpy 转换、清洗、重塑和预处理生物数据（OmicVerse）。 |
| [data-viz-plots](skills/data-viz-plots/) | 使用 matplotlib 和 seaborn 创建出版质量的图表和可视化（OmicVerse）。 |
| [scientific-visualization](skills/scientific-visualization/) | 使用 matplotlib/seaborn/plotly 创建发表级图形。多面板布局、误差棒、显著性标记、色盲友好、PDF/EPS/TIFF 导出。 |

</details>

### 实验室自动化与集成

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [opentrons-integration](skills/opentrons-integration/) | Flex/OT-2 机器人实验室自动化平台。编写 Protocol API v2 协议、液体处理、硬件模块（加热振荡器、热循环仪）、耗材管理。 |
| [pylabrobot](skills/pylabrobot/) | 实验室自动化工具包，控制移液工作站、酶标仪、泵、加热振荡器、培养箱、离心机和分析仪器。 |
| [benchling-integration](skills/benchling-integration/) | Benchling R&D 平台集成。通过 API 访问注册表（DNA、蛋白质）、库存、ELN 条目、工作流，构建 Benchling App，用于实验室数据管理自动化。 |
| [labarchive-integration](skills/labarchive-integration/) | 电子实验记录本 API 集成。访问记录本、管理条目/附件、备份记录本，与 Protocols.io/Jupyter/REDCap 集成。 |
| [protocolsio-integration](skills/protocolsio-integration/) | protocols.io API 集成，用于管理科学实验方案——搜索、创建、更新、发布方案，管理步骤和试剂。 |
| [instrument-data-to-allotrope](skills/instrument-data-to-allotrope/) | 将实验室仪器输出文件（PDF、CSV、Excel、TXT）转换为 Allotrope Simple Model（ASM）JSON 格式，用于 LIMS 系统、数据湖和下游分析。 |

</details>

### 科学研究与写作

<details>
<summary>点击展开技能列表</summary>

| 技能 | 说明 |
|------|------|
| [scientific-writing](skills/scientific-writing/) | 用完整段落撰写科学稿件，采用两阶段流程：章节提纲然后正文。覆盖研究论文所有章节。 |
| [scientific-critical-thinking](skills/scientific-critical-thinking/) | 评估研究严谨性。评估方法学、实验设计、统计有效性、偏倚、混杂因素、证据质量（GRADE、Cochrane ROB）。 |
| [scientific-brainstorming](skills/scientific-brainstorming/) | 研究构思伙伴。生成假说、探索跨学科联系、挑战假设、开发方法论、识别研究空白，用于创造性科学问题解决。 |
| [hypothesis-generation](skills/hypothesis-generation/) | 生成可检验的假说。从观察中制定假设，设计实验，探索竞争性解释，发展预测，提出机制，用于跨学科科学探究。 |
| [scientific-problem-selection](skills/scientific-problem-selection/) | 帮助科学家进行研究问题选择、项目构思、解决停滞项目和战略性科学决策。 |
| [peer-review](skills/peer-review/) | 系统性同行评审工具包。评估方法学、统计、设计、可重复性、伦理、图形完整性、报告标准，用于稿件和基金评审。 |
| [citation-management](skills/citation-management/) | 综合文献引用管理。从 Google Scholar 和 PubMed 检索论文，提取准确元数据，验证引用，生成 BibTeX 条目。 |
| [research-grants](skills/research-grants/) | 为 NSF、NIH、DOE 和 DARPA 撰写竞争性科研项目申请书。机构特定格式、评审标准、预算编制、广泛影响和意义陈述。 |
| [research-lookup](skills/research-lookup/) | 使用 Perplexity Sonar Pro Search 或 Sonar Reasoning Pro（通过 OpenRouter）查询当前研究信息，自动选择最适合查询复杂度的模型。 |
| [biomni](skills/biomni/) | 自主生物医学 AI 智能体框架，执行跨基因组学、药物发现、分子生物学和临床分析的复杂研究任务。 |
| [treatment-plans](skills/treatment-plans/) | 为所有临床专科生成简洁（3-4页）的医疗治疗方案（LaTeX/PDF 格式），支持普通医学、康复治疗、心理健康和慢性病管理。 |

</details>

### 分析师人格

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [biologist-analyst](skills/biologist-analyst/) | 生物学家分析师人格，用于解读生物实验、测序数据、细胞生物学测定和分子生物学研究。 |
| [chemist-analyst](skills/chemist-analyst/) | 化学家分析师人格，用于解读化学数据、合成路线、光谱结果、反应机制和实验室分析。 |
| [epidemiologist-analyst](skills/epidemiologist-analyst/) | 流行病学家分析师人格，用于研究设计、队列分析、风险因素评估、公共卫生监测和因果推断。 |
| [psychologist-analyst](skills/psychologist-analyst/) | 心理学家分析师人格，用于行为数据分析、心理评估解读、临床案例制定和心理健康研究。 |

</details>

### 公共卫生与时序分析

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [datacommons-client](skills/datacommons-client/) | 访问Google Data Commons的公共健康统计数据：疾病流行率、人口统计数据、全球来源的健康指标。 |
| [timesfm-forecasting](skills/timesfm-forecasting/) | 使用Google TimesFM进行零样本时序预测。适用于生命体征趋势、健康传感器数据和纵向健康监测，无需自定义模型训练。 |
| [aeon](skills/aeon/) | 时序机器学习：分类、回归、聚类、异常检测、分割，适用于时序健康数据和连续临床测量。 |

</details>

### 科学文献与参考管理

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [bgpt-paper-search](skills/bgpt-paper-search/) | 使用BGPT MCP服务器搜索科学论文。每篇论文返回25+结构化字段：方法、结果、样本量、质量评分。用于文献综述和证据综合。 |
| [pyzotero](skills/pyzotero/) | 通过Zotero Web API v3以编程方式与Zotero参考文献库交互。检索、创建、更新条目，导出引用，上传PDF，构建研究自动化工作流程。 |
| [open-notebook](skills/open-notebook/) | 自托管NotebookLM替代品。摄取PDF、视频、网页、文档；生成AI驱动的笔记；与研究材料对话；支持16+AI提供商。 |

</details>

### 数据处理与科学计算

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [dask](skills/dask/) | 用于超出RAM的基因组/组学数据集的分布式计算。扩展pandas/NumPy超过内存限制，并行文件处理，分布式ML。 |
| [polars](skills/polars/) | 快速内存DataFrame库（1-100GB）。生物医学数据ETL和分析管道的更快pandas替代品。 |
| [vaex](skills/vaex/) | 数十亿行数据的核外DataFrame操作。大型基因组和临床数据集的快速统计和可视化。 |
| [zarr-python](skills/zarr-python/) | 云存储的分块N维数组。压缩数组、并行I/O、S3/GCS集成，用于大规模组学数据。 |
| [pytorch-lightning](skills/pytorch-lightning/) | 生物医学AI的结构化PyTorch深度学习：多GPU训练、回调、日志记录、临床/基因组模型的分布式训练。 |

</details>

### 科学可视化与科研传播

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [matplotlib](skills/matplotlib/) | 全定制的低级绘图库。用于科学手稿和期刊的出版质量图形。 |
| [seaborn](skills/seaborn/) | 带pandas集成的统计可视化。用于生物医学数据探索的箱线图、小提琴图、热图、配对图。 |
| [plotly](skills/plotly/) | 交互式可视化。悬停信息、缩放、探索性生物医学分析和演示的仪表板。 |
| [infographics](skills/infographics/) | 使用迭代AI精炼创建专业科学信息图表。支持10种信息图类型和8种行业风格。 |
| [scientific-schematics](skills/scientific-schematics/) | 出版质量的科学图表：神经网络架构、生物通路、系统图、流程图。 |
| [scientific-slides](skills/scientific-slides/) | 为会议、研讨会、论文答辩构建研究演示幻灯片。支持PowerPoint和LaTeX Beamer。 |
| [latex-posters](skills/latex-posters/) | 使用LaTeX（beamerposter、tikzposter）创建专业研究海报。多栏布局的会议海报。 |
| [pptx-posters](skills/pptx-posters/) | 可导出为PDF或PPTX的HTML/CSS研究海报。现代网页式海报设计。 |
| [markdown-mermaid-writing](skills/markdown-mermaid-writing/) | 使用Markdown和24种Mermaid图表类型进行科学文档编写。9种科学报告文档模板。 |
| [paper-2-web](skills/paper-2-web/) | 将学术论文转换为交互式网站、演示视频和会议海报（Paper2Web、Paper2Video、Paper2Poster）。 |

</details>

### 补充科学工具

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [pymoo](skills/pymoo/) | 多目标优化（PYMOO）：药物设计参数优化、帕累托前沿分析、进化算法。 |
| [markitdown](skills/markitdown/) | 将文档（PDF、DOCX、PPTX、HTML、图像）转换为Markdown进行处理和分析。 |
| [perplexity-search](skills/perplexity-search/) | 通过Perplexity进行AI驱动的科学信息实时检索。 |
| [geopandas](skills/geopandas/) | 地理空间数据分析：流行病学制图、疾病分布、空间健康分析。 |
| [hypogenic](skills/hypogenic/) | 对表格数据集进行自动假设生成和检验，结合文献洞察与数据驱动验证。 |
| [pdf-processing](skills/pdf-processing/) | 高级PDF处理：文本提取、表格解析、注释、表单填写。 |
| [pdf-processing-pro](skills/pdf-processing-pro/) | 专业PDF处理：增强型OCR、多栏布局处理、批量处理。 |
| [pdf-anthropic](skills/pdf-anthropic/) | Anthropic优化的PDF分析，用于科学和医学文档理解。 |
| [xlsx-official](skills/xlsx-official/) | 官方Excel/XLSX技能：电子表格创建、分析和数据管理。 |
| [docx-official](skills/docx-official/) | 官方Word/DOCX技能：文档创建、编辑和格式化。 |
| [pptx-official](skills/pptx-official/) | 官方PowerPoint/PPTX技能：演示文稿创建和编辑。 |

</details>

### 计算模拟与本体论 (HeshamFS/materials-simulation-skills, 17个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [ontology-validator](skills/ontology-validator/) | 验证生物医学本体结构（HPO、GO、MeSH、SNOMED、OBO）的术语关系。 |
| [ontology-explorer](skills/ontology-explorer/) | 浏览和查询生物医学本体：术语层次、注释、交叉引用。 |
| [ontology-mapper](skills/ontology-mapper/) | 跨生物医学本体映射：HPO↔OMIM、GO↔UniProt、疾病↔表型交叉本体。 |
| [slurm-job-script-generator](skills/slurm-job-script-generator/) | 为HPC基因组学/生物信息管道作业生成优化的SLURM sbatch脚本。 |
| [numerical-integration](skills/numerical-integration/) | 为生物学模型模拟选择和配置ODE/PDE时间积分方法（刚性系统、IMEX）。 |
| [nonlinear-solvers](skills/nonlinear-solvers/) | 为生物网络优化、参数拟合和FBA配置非线性求解器。 |
| [parameter-optimization](skills/parameter-optimization/) | 实验设计、灵敏度分析、贝叶斯优化用于生物模型校准。 |
| [linear-solvers](skills/linear-solvers/) | 为大规模生物网络和代谢模型计算选择线性求解器。 |
| [numerical-stability](skills/numerical-stability/) | 分析时变生物模拟的数值稳定性（CFL准则、刚性检测）。 |
| [simulation-orchestrator](skills/simulation-orchestrator/) | 编排多模拟活动：参数扫描、批量作业、结果聚合。 |
| [simulation-validator](skills/simulation-validator/) | 验证模拟：预飞检查、运行时监控、收敛性、NaN/Inf检测。 |
| [convergence-study](skills/convergence-study/) | 使用Richardson外推法进行模拟验证的空间/时间收敛性分析。 |
| [post-processing](skills/post-processing/) | 提取、分析和可视化模拟输出：时间序列、场分布、统计摘要。 |
| [performance-profiling](skills/performance-profiling/) | 识别计算瓶颈，分析扩展行为，优化HPC模拟作业。 |
| [differentiation-schemes](skills/differentiation-schemes/) | 为生物模型PDE离散化选择有限差分/有限体积/谱方法。 |
| [time-stepping](skills/time-stepping/) | 生物动力学自适应时间步控制：CFL约束、检查点调度。 |
| [mesh-generation](skills/mesh-generation/) | 数值模拟的网格生成：分辨率、质量指标、自适应细化。 |

</details>

### 开发工作流技能 (obra/superpowers, 14个)

<details>
<summary>点击展开技能列表</summary>

| 技能 | 描述 |
|------|------|
| [test-driven-development](skills/test-driven-development/) | TDD 工作流：先写测试再实现，红-绿-重构循环确保代码可靠。 |
| [systematic-debugging](skills/systematic-debugging/) | 结构化调试方法：假设形成、证据收集、根因分析。 |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/) | 编排并行子智能体处理独立任务以最大化吞吐量。 |
| [writing-plans](skills/writing-plans/) | 复杂多步骤任务前编写结构化实现计划。 |
| [executing-plans](skills/executing-plans/) | 在隔离会话中按审查检查点执行书面实现计划。 |
| [brainstorming](skills/brainstorming/) | 在实现前对需求和设计进行结构化创意探索。 |
| [writing-skills](skills/writing-skills/) | 以正确格式创建和验证新的 SKILL.md 技能并完成部署验证。 |
| [verification-before-completion](skills/verification-before-completion/) | 声明工作完成前运行验证命令并确认输出。 |
| [requesting-code-review](skills/requesting-code-review/) | 带上下文、变更摘要和具体问题来结构化代码审查请求。 |
| [receiving-code-review](skills/receiving-code-review/) | 以技术严谨性而非盲目接受来处理代码审查反馈。 |
| [subagent-driven-development](skills/subagent-driven-development/) | 将开发任务分解为子任务供并行子智能体执行。 |
| [using-git-worktrees](skills/using-git-worktrees/) | 为功能开发和计划执行创建隔离的 git 工作树。 |
| [finishing-a-development-branch](skills/finishing-a-development-branch/) | 完成开发分支：合并、PR 或清理，提供结构化决策选项。 |
| [using-superpowers](skills/using-superpowers/) | 元技能：在对话开始时发现并使用可用技能完成任何任务。 |

</details>

</details>

## 致谢

我们从以下优秀的项目中受益，如果你感兴趣，请访问它们～

1. [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
2. [Anthropics Skills](https://github.com/anthropics/skills)
3. [Skillsmp](https://skillsmp.com/)
4. [awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
5. [ClawHub](https://clawhub.ai/)
6. [水产市场](https://openclawmp.cc/)
7. [Skills.Sh](https://skills.sh/)
8. [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
9. [llmbase](https://llmbase.ai/openclaw/)
10. [OpenClaw](https://docs.openclaw.ai/zh-CN)
11. [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)
12. [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)
13. [LLMs-Universal-Life-Science-and-Clinical-Skills-](https://github.com/mdbabumiamssm/LLMs-Universal-Life-Science-and-Clinical-Skills-)
14. [BioClaw](https://github.com/Runchuan-BU/BioClaw)
15. [ClawBio](https://github.com/ClawBio/ClawBio)
