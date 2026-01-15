# SKILL.md — GUDID Chronicles Agentic Skills (配銷分析代理技能手冊)

**系統名稱:** GUDID Chronicles — Supply Chain Analytics Platform  
**文件類型:** SKILL 技術說明文件  
**目標讀者:** 系統架構師、AI 工程師、前端開發者、法規與合規專家  

---

## 1. 文件目的與範圍

本文件定義「GUDID 智能代理系統」中所有代理（agents）的技能範圍、預期輸入與輸出格式、以及在 Hugging Face Space（Streamlit）環境下的執行與串接方式。

此 SKILL.md 為 `agents.yaml` 的「語義說明層」，用於：

- 協助工程師了解每個代理的用途與邊界  
- 指導前端（含 WOW UI 與 Agent Headquarters）如何設計互動與提示  
- 為合規與稽核人員提供可追溯的功能說明  

> 所有代理皆預設使用 **繁體中文** 回應，但可在提示中要求產出英文或雙語內容。

---

## 2. 執行環境與整體架構

### 2.1 執行環境

- 執行平台：Hugging Face Space  
- 前端框架：Streamlit  
- 主要檔案：
  - `app.py`：主應用程式（WOW UI + Agent Headquarters + 視覺化儀表板）
  - `agents.yaml`：31 個 AI 代理定義（本 SKILL.md 對應）
  - `SKILL.md`：本文件
- 主要 API 提供者：
  - OpenAI（含 `gpt-4o-mini`, `gpt-4.1-mini`）
  - Google Gemini（`gemini-2.5-flash`, `gemini-2.5-flash-lite`）
  - Anthropic（在部分代理可擴展）
  - Grok (xAI)（在 UI 可選擇，但目前 31 代理預設多為 OpenAI / Gemini）

### 2.2 WOW UI 與 Agent Headquarters

- **WOW UI**
  - 支援亮色 / 暗色主題
  - 支援繁體中文 / 英文介面
  - 20 種以名畫為主題的視覺樣式（透過 Jackslot / Lucky Wheel 切換）
  - 顯示系統狀態與 API 健康指標

- **Agent Headquarters**
  - 使用者可：
    - 指定要執行的代理
    - 調整系統提示（System Prompt override）
    - 選擇模型（OpenAI / Gemini / Anthropic / Grok 多模型）
    - 設定 `max_tokens`（預設 12000，上限依各家模型而定）
  - 支援 **代理鏈（chaining）**：
    - 使用者可將前一個代理的輸出，編輯後再作為下一個代理的輸入

### 2.3 資料上下文

預設配銷資料使用結構：

```ts
interface PackingListItem {
  Suppliername: string;
  deliverdate: string;      // Excel serial 或 ISO 字串（前端會轉成 deliverdate_dt）
  customer: string;
  licenseID: string;
  DeviceCategory: string;
  UDI: string;
  DeviceName: string;
  LotNumber: string;
  SN: string;
  ModelNum: string;
  Numbers: string;          // 前端會轉成 int
  Unit: string;
}
在 Streamlit 中：

CSV 會轉為 pandas.DataFrame，並新增：
deliverdate_dt: 真實日期
Numbers: 整數數量
使用者可透過篩選（客戶、日期區間）建立「當前可視範圍」，並將此資料摘要給代理作分析。
3. 代理執行模式與設計慣例
3.1 Input / Output 一般原則
輸入（Input）

一般為自然語言 +（可選）資料摘要（例如：DataFrame 的統計摘要 / JSON / 表格）
建議使用者在 Agent Headquarters：
使用 Markdown / 條列描述分析目標
附上欄位說明或匯總表，而非整個原始 CSV
輸出（Output）

預設使用繁體中文
鼓勵以下格式：
清楚分段（標題、子標、條列）
必要時使用 Markdown 表格
避免捏造精確數值；如需數字，說明為「示意」或「建議欄位」
3.2 串接與角色分工
常見串接流程範例：

nlp_analyzer：解析使用者需求，產生分析計畫
data_standardizer + label_matcher：統一欄位與資料格式
某個分析代理（例如 temporal_trend_analyst 或 customer_segmentation_analyst）
summary_analyst：整合多個結果
根據目的：
管理簡報 → executive_overview / story_telling_analyst
法規報告 → regulatory_report_writer
回收/不良事件 → adverse_event_linker + recall_manager + lot_trace_agent
代理之間沒有硬性依賴，但本 SKILL.md 提供建議串接順序。

4. 技能總覽（Skill Catalog Overview）
類別	代理 ID	角色名稱（中文）	核心用途
基礎解讀	nlp_analyzer	自然語言解析核心代理	將使用者問題轉成結構化分析計畫
基礎治理	data_standardizer	資料標準化代理	欄位/格式/度量統一
基礎治理	label_matcher	標籤與欄位語意比對代理	對齊欄位語意與圖表軸名稱
品質治理	duplicate_checker	重複紀錄偵測代理	找出疑似重複資料邏輯
品質治理	data_quality_steward	資料品質管理代理	定義資料品質 KPI 與治理策略
品質治理	udi_quality_checker	UDI 資料品質檢核代理	UDI 完整性與一致性
品質治理	serialization_auditor	SN 追蹤審核代理	植入式裝置序號治理
配銷分析	temporal_trend_analyst	時間序列趨勢分析代理	日期/時間維度趨勢
配銷分析	customer_segmentation_analyst	客戶分群與貢獻分析代理	客戶分群與 Pareto 結構
配銷分析	model_velocity_analyst	型號銷售速度分析代理	ModelNum 生命週期
配銷分析	inventory_risk_scout	庫存風險探索代理	高/低出貨風險判斷
配銷分析	capacity_planner	產能與補貨規劃代理	需求預估與補貨建議
視覺化/拓樸	supply_chain_explorer	供應鏈拓樸探索代理	Supplier-Device-Customer 流向設計
視覺化/拓樸	graph_topology_analyst	圖譜拓樸分析代理	圖論與社群結構解讀
視覺化/拓樸	network_centrality_analyst	網路中心度分析代理	關鍵節點量化
視覺化/拓樸	bottleneck_detector	瓶頸節點偵測代理	Single point of failure 風險
視覺化/拓樸	route_optimization_expert	配銷路徑最佳化構想代理	節點配置與分散策略
視覺化/拓樸	kpi_dashboard_designer	KPI 儀表板設計代理	一頁式供應鏈/合規儀表板
風險 & 合規	anomaly_detector	分佈異常偵測代理	出貨異常與風險模式
風險 & 合規	adverse_event_linker	不良事件關聯分析代理	不良事件 vs 配銷覆蓋
風險 & 合規	recall_manager	回收管理與追蹤代理	批號回收計畫設計
風險 & 合規	lot_trace_agent	批號追蹤代理	批號流向與追溯報表
風險 & 合規	license_consistency_checker	License 一致性檢核代理	LicenseID vs 產品/客戶合理性
風險 & 合規	customs_verifier	海關與進出口查驗代理	LicenseID/數量/客戶合規性
風險 & 合規	eifu_manager	eIFU 關聯管理代理	型號與電子說明書映射
風險 & 合規	international_connector	國際資料庫對照代理	跨國配銷與 GUDID 對應
敘事 & 報告	summary_analyst	分析總結代理	多代理結果整合
敘事 & 報告	executive_overview	高階主管總覽代理	3–5 KPI 高層敘事
敘事 & 報告	story_telling_analyst	資料故事敘事代理	非技術利害關係人溝通
敘事 & 報告	regulatory_report_writer	法規申報報告撰寫代理	正式法規與稽核文件
情境模擬	scenario_planner	情境與假設模擬代理	需求激增 / 回收等情境規劃
5. 個別代理技能說明
以下每個代理皆對應 agents.yaml 中的定義。此處重點在「使用情境 / I/O / 串接建議」，不重複貼出完整 system_prompt。

5.1 nlp_analyzer — 自然語言解析核心代理
類型： 基礎解讀 / 任務規劃
典型使用場景：
使用者在聊天介面輸入：
「請幫我看 2024 Q1 各客戶的配銷分佈，並找出出貨量最高的前 5 家」

輸入：
自然語言問題（可含部分欄位名稱、中文/英文混雜）
輸出：
分析計畫（Markdown）：
目標欄位（如：customer, Numbers, deliverdate_dt）
要生成的統計和圖表建議（Top-N 長條圖、折線圖等）
推薦串接：
給下一個分析代理（如 customer_segmentation_analyst 或 temporal_trend_analyst）
注意事項：
不應捏造數字，只描述「要做什麼分析」與「為什麼這樣做」。
5.2 data_standardizer — 資料標準化代理
類型： 資料治理
輸入：
欄位列表 + 若干範例紀錄（建議以文字或精簡表格形式輸入）
輸出：
清洗與標準化步驟
建議的欄位型別與命名（可含中英雙語說明）
串接建議：
可在導入新資料源時，先由此代理給出「ETL 規格草案」，再由工程師實作。
5.3 label_matcher — 標籤與欄位語意比對代理
類型： 詞彙 / 統一命名
輸入：
欄位名稱列表（如 HospName, customer, 客戶代碼 等）
輸出：
Markdown 表格：原始欄位 / 建議標準欄位 / 類型 / 建議圖表用途
串接建議：
結果可直接用來配置前端圖表元件（X 軸、分組欄、顏色分類）。
5.4 duplicate_checker — 重複紀錄偵測代理
類型： 資料品質
輸入：
欄位清單 + 文字描述（如「可能有重複訂單」）
可選：某些具代表性的重複樣本
輸出：
建議的「複合鍵組合」（如 Suppliername+customer+deliverdate+ModelNum+LotNumber）
視覺化建議（同鍵計數長條圖、熱圖）
串接建議：
搭配 data_quality_steward 形成完整品質治理方案。
5.5 data_quality_steward — 資料品質管理代理
類型： 資料治理 / KPI 設計
輸入：
欄位清單 + 常見髒資料問題描述
輸出：
品質 KPI 建議（完整率、一致率、延遲等）
定期檢查圖表建議
串接建議：
輸出可直接寫入內部資料治理政策或 SOP 文件。
5.6 udi_quality_checker — UDI 資料品質檢核代理
類型： UDI 專屬品質治理
輸入：
UDI 欄位格式說明 + 常見錯誤樣本
輸出：
檢查規則（長度、校驗、格式）
視覺化建議（UDI 長度分佈、UDI vs DeviceName 關係圖）
串接建議：
可搭配 label_matcher / data_standardizer 制定 UDI 專案清洗規格。
5.7 serialization_auditor — 序號 SN 追蹤審核代理
類型： 法規 & 追蹤
輸入：
SN 欄位狀態描述（完整度、缺失比例）
裝置類型與法規適用情境
輸出：
風險說明（對植入式裝置特別重要）
審核與補件優先順序建議
串接建議：
與 lot_trace_agent、adverse_event_linker 一起使用，在回溯調查中提供 SN 層級精度。
5.8 temporal_trend_analyst — 時間序列趨勢分析代理
類型： 配銷分析 / 時間序列
輸入：
日期欄位（deliverdate_dt）+ 數量彙總方式描述
輸出：
趨勢/季節性/尖峰與斷點的分析建議
圖表建議：原始折線、移動平均、同比/環比
串接建議：
結果可餵給 executive_overview 或 capacity_planner 作進一步決策敘事。
5.9 customer_segmentation_analyst — 客戶分群與貢獻分析代理
類型： 配銷分析 / 客戶策略
輸入：
每客戶出貨量 / 單位數 / 裝置組合等彙總資訊
輸出：
客戶分群框架（A/B/C 客戶、科別等）
長尾結構與 Pareto 80/20圖表建議
串接建議：
搭配 story_telling_analyst → 市場與銷售簡報內容。
5.10 model_velocity_analyst — 裝置型號銷售速度分析代理
類型： 產品組合 / 型號生命週期
輸入：
ModelNum × 時間 × 數量之彙總描述
輸出：
將型號分為「成長/成熟/衰退」階段的判斷邏輯
圖表建議：Top-N 長條圖、ModelNum vs 時間熱圖
串接建議：
給產品經理與供應鏈團隊作型號淘汰/上新決策參考。
5.11 inventory_risk_scout — 庫存風險探索代理
類型： 風險 & 庫存推論
輸入：
出貨節奏描述 + 客戶/型號集中度資訊
輸出：
庫存壓力或缺貨風險的概念判斷
圖表建議：波動係數、集中度指標等
串接建議：
搭配 capacity_planner，形成「風險感知 + 行動建議」組合。
5.12 capacity_planner — 產能與補貨規劃代理
類型： 規劃 / 預測
輸入：
歷史配銷分佈摘要 + 未來政策/市場假設（文字）
輸出：
粗略需求區間預估與情境
視覺化建議：區域圖、箱型圖顯示不確定性
串接建議：
之後由 executive_overview / scenario_planner 轉成決策語言。
5.13 supply_chain_explorer — 供應鏈拓樸探索代理
類型： 視覺化 / 圖譜設計
輸入：
節點定義（Suppliername, DeviceName, customer）+ 欄位說明
輸出：
如何建構 nodes/edges 結構的詳細說明
顏色/形狀/大小等視覺編碼建議
串接建議：
指導前端如何用 D3/networkx/pyvis 實作供應鏈圖（App 已有初版）。
5.14 graph_topology_analyst — 圖譜拓樸分析代理
類型： Graph / 社群結構
輸入：
圖譜結構摘要（節點/邊種類與關係描述）
輸出：
社群偵測、連通分支、拓樸特徵的解讀方式
串接建議：
與 network_centrality_analyst / bottleneck_detector 組合使用。
5.15 network_centrality_analyst — 網路中心度分析代理
類型： Graph / 指標解讀
輸入：
節點類型 + 中心度計算方式/結果摘要
輸出：
各類中心度在供應鏈中的意義（營運/風險）
視覺化標註建議（節點大小、顏色）
串接建議：
輸出提供給風險或營運團隊簡報使用。
5.16 bottleneck_detector — 瓶頸節點偵測代理
類型： 風險 / Graph
輸入：
關鍵節點或高度集中的邊資訊（文字或摘要表）
輸出：
單點失效風險說明
備援與分散策略構想
串接建議：
與 scenario_planner 合併，用於 BCP/DR（營運持續計畫）。
5.17 route_optimization_expert — 配銷路徑最佳化構想代理
類型： 策略 / 高階規劃
輸入：
供應商 / 客戶分佈摘要（可能缺乏地理細節）
輸出：
中轉站 / 區域倉等高層設計建議
視覺化構想（網路圖 + 區域分群）
串接建議：
與 supply_chain_explorer / graph_topology_analyst 一起使用。
5.18 kpi_dashboard_designer — KPI 儀表板設計代理
類型： 視覺化 / UX for Data
輸入：
使用者目標（例如：管理層 vs 合規 vs 運營）
目前可用欄位與已存在圖表說明
輸出：
儀表板版面配置、KPI 清單與互動設計
串接建議：
適合與所有分析代理結果結合後，建立「最終一頁式儀表板」設計。
5.19 anomaly_detector — 分佈異常偵測代理
類型： 風險 / 異常分析
輸入：
各種分佈彙總（按客戶/日期/型號等）
輸出：
異常模式類型與可能原因（業務/系統/通關等）
異常視覺化建議：箱型圖、控制圖、熱圖等
串接建議：
與 inventory_risk_scout / adverse_event_linker 作風險整合。
5.20 adverse_event_linker — 不良事件關聯分析代理
類型： 風險 / 合規
輸入：
不良事件摘要（UDI / LotNumber / ModelNum）+ 配銷分佈概況
輸出：
受影響客戶/地點推估邏輯
視覺化建議（受影響熱圖、分佈長條圖）
串接建議：
與 recall_manager / lot_trace_agent 串接，形成功能完整的回收/調查流程。
5.21 recall_manager — 回收管理與追蹤代理
類型： 回收 / 行動計畫
輸入：
受影響批號/UDI + 客戶/日期分佈
輸出：
回收對象優先順序與清單欄位建議
回收進度圖表（累積回收率、甘特圖概念）
串接建議：
後續交由 regulatory_report_writer 生成正式回收報告部分內容。
5.22 lot_trace_agent — 批號追蹤代理
類型： 追溯 / 回溯分析
輸入：
指定 LotNumber 或清單 + 出貨資料結構說明
輸出：
查詢與追溯報表設計（批號 vs 客戶 vs 日期）
適合前端 UI / 報表的欄位與流程
串接建議：
與 serialization_auditor（若 SN 有用）與 adverse_event_linker 一起使用。
5.23 license_consistency_checker — License 一致性檢核代理
類型： 法規 / 合規檢核
輸入：
LicenseID × ModelNum × DeviceCategory × 客戶 分佈描述
輸出：
潛在錯配風險（例如：不合理組合或集中度過高）
檢核報表與圖表設計建議
串接建議：
與 customs_verifier / regulatory_report_writer 合作完成合規檢核報告。
5.24 customs_verifier — 海關與進出口查驗代理
類型： 關務 / 合規
輸入：
LicenseID、客戶/地區分佈、數量與時間彙總
輸出：
異常通關風險描述
關務監控圖表建議（LicenseID vs 地區 / 時間）
串接建議：
作為合規報告的一部分，由 regulatory_report_writer 整理。
5.25 eifu_manager — eIFU 關聯管理代理
類型： 文件 / 合規
輸入：
ModelNum / UDI / LicenseID 與 eIFU 版本關係描述
輸出：
eIFU 對應表與狀態檢查設計
視覺化建議（未對應最新 eIFU 的客戶比例等）
串接建議：
法規與品質團隊可據此設計 eIFU 管理儀表板。
5.26 international_connector — 國際資料庫對照代理
類型： 國際化 / 資料對接
輸入：
客戶/國家分佈 + 相關國家/區域資訊
輸出：
如何對照 GUDID 或其他國家器材註冊資料的步驟建議
跨國分佈圖表（地圖/矩陣）
串接建議：
與 executive_overview 用於全球視角簡報。
5.27 summary_analyst — 分析總結代理
類型： 統合 / 總結
輸入：
其他代理的多份輸出文本
輸出：
技術總結 + 後續建議
串接建議：
先由分析代理完成工作，再集中餵給此代理，最後交給 executive_overview 或 regulatory_report_writer。
5.28 executive_overview — 高階主管總覽代理
類型： 管理簡報 / 高層視角
輸入：
分析摘要（可以是 summary_analyst 的輸出）
輸出：
3–5 個最重要的 KPI 與圖表建議
簡報大綱與標題
串接建議：
直接提供給 PM / 管理團隊製作簡報。
5.29 story_telling_analyst — 資料故事敘事代理
類型： 敘述 / 溝通
輸入：
圖表結果與技術分析摘要
輸出：
面向：病患安全 / 合規 / 營運效率 的故事版本
串接建議：
適合內外部溝通（醫院、主管機關、內部簡報）。
5.30 regulatory_report_writer — 法規申報報告撰寫代理
類型： 報告 / 合規
輸入：
完整分析結果與已決策的行動方案
輸出：
正式報告章節草案（標題+段落），語氣嚴謹
串接建議：
與法規團隊共同檢視後，可直接納入正式提交文件。
5.31 scenario_planner — 情境與假設模擬代理
類型： 風險 / 情境分析
輸入：
目前配銷結構概況 + 想要模擬的情境敘述（需求激增、回收擴大、供應中斷）
輸出：
不同情境下的監控重點與圖表設計建議
串接建議：
與 inventory_risk_scout / capacity_planner / bottleneck_detector 一起形成整體風險管理方案。
6. 典型使用 Playbook 範例
6.1 回收與不良事件調查 Playbook
nlp_analyzer：解析需求（特定批號 + 不良事件）
lot_trace_agent：設計批號追溯報表
adverse_event_linker：評估不良事件 vs 配銷覆蓋
recall_manager：設計回收對象優先順序與進度指標
regulatory_report_writer：產出法規/稽核用報告草案
6.2 高階主管月度配銷簡報 Playbook
data_standardizer + label_matcher：統一欄位與指標
temporal_trend_analyst：時間序列與季節性
customer_segmentation_analyst：客戶分群與 Top 客戶
model_velocity_analyst：產品組合與型號生命週期
summary_analyst → executive_overview → story_telling_analyst
6.3 資料品質與法規稽核準備 Playbook
data_quality_steward：建立品質 KPI 與檢查表
duplicate_checker / udi_quality_checker / serialization_auditor：針對關鍵欄位進行說明
license_consistency_checker：LicenseID 合規檢核
customs_verifier / eifu_manager / international_connector：補足海關 / 文件 / 國際對照面向
regulatory_report_writer：彙整成可提交報告草稿
7. 與 UI / 程式碼的對應關係
app.py：
根據 agents.yaml 載入所有代理定義，並建構 AgentOrchestrator
Agent Headquarters：
讓使用者在 UI 中選擇代理 ID（本文件中之 ID）
可覆寫 system prompt / 模型 / max_tokens
可編輯代理輸出並串接下一個代理
本 SKILL.md：
給工程師/PM/合規專家作為「人類可讀」的代理說明
不參與執行邏輯，但需與 agents.yaml 維持一對一對應
8. 維護原則
同步性：
若在 agents.yaml 新增/刪除/改名代理，必須同步更新 SKILL.md。
版本管理：
建議在 Git 版本控制中，將 agents.yaml 與 SKILL.md 綁定審查。
合規審查：
任何涉及法規 / 對外報告的代理（例如 regulatory_report_writer、customs_verifier）之 system prompt 修改，應經合規團隊覆核。
安全邊界：
代理只提供分析與建議，不自動執行回收或申報行為，所有決策由人類最終裁量。
