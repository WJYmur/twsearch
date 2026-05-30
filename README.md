# twsearch - 國旅特約商店查詢 API

本專案為「國旅特約商店查詢系統」的後端資料查詢 API。採用 Microsoft Azure Functions (Python HTTP Trigger) 建置，並使用 In-Memory Cache 技術讀取靜態 JSON 資料庫，提供快速的商店檢索服務。

## ✨ 核心功能
* **快速檢索**：接收前端傳來的 API 指令 (HTTP GET)，回傳對應的商店資料。
* **多條件過濾**：支援依照縣市、分類、關鍵字進行特約商店查詢。
* **資料分頁**：支援資料分頁回傳格式 (JSON)。

## 📁 檔案結構
* `function_app.py`：核心程式邏輯，定義 API 路由。
* `host.json`：Azure Functions 全域設定檔。
* `local.settings.json`：本地開發環境設定檔。
* `requirements.txt`：Python 依賴套件清單。
* `nccc_retailers_all.json`：**重要！** 靜態資料庫，包含特約商店的所屬縣市、名稱、分類、地址與聯絡電話。
* `nccc_retailers_all.json下載點`：https://drive.google.com/file/d/1qJwNOx11g0D5H3xYjmxPYCWk32fs7nB9/view?usp=sharing

## 🚀 安裝與執行流程
1. **環境準備**：安裝 VS Code 及 Azure Functions 擴充套件，並準備 Python 虛擬環境。
2. **安裝套件**：執行 `pip install -r requirements.txt`。
3. **本地測試**：在 VS Code 中按下 `F5` 啟動本地模擬器，預設端點為 `http://localhost:7071/api/tw_search`。
4. **部署至 Azure**：
   * 於 Azure 建立 Function App (選擇 Python 執行階段)。
   * 透過 VS Code 的 Azure 擴充套件將專案 Deploy 至雲端。
   * 紀錄部署後的函式 URL，供前端專案使用。
