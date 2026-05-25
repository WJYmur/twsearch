import azure.functions as func
import logging
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# 🌟 宣告全域變數做為「記憶體快取」
global_stores_data = None

def load_data():
    global global_stores_data
    if global_stores_data is None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, 'nccc_retailers_all.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                global_stores_data = json.load(f)
            logging.info(f"✅ 成功載入 {len(global_stores_data)} 筆資料至記憶體")
        except Exception as e:
            logging.error(f"❌ 讀取 JSON 檔案失敗: {e}")
            global_stores_data = []
            
    return global_stores_data

@app.route(route="tw_search")
def tw_search(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('收到前端的特約商店查詢請求。')

    # 1. 載入資料
    all_stores = load_data()

    # 2. 取得前端傳來的查詢參數
    county = req.params.get('county')
    category = req.params.get('category')
    keyword = req.params.get('keyword')
    
    # 取得分頁參數
    try:
        page = int(req.params.get('page', 1))
        limit = int(req.params.get('limit', 10))
    except ValueError:
        page = 1
        limit = 10

    # 🌟 紀錄使用者輸入
    logging.info(f"👉 使用者查詢條件 -> 縣市: {county}, 分類: {category}, 關鍵字: {keyword}, 頁數: {page}")

    # 3. 核心過濾邏輯
    results = all_stores

    if county:
        results = [s for s in results if s.get('county') == county]

    if category:
        results = [s for s in results if s.get('cat') == category]

    # ==========================================
    # 🌟 修改點：支援多關鍵字搜尋 (以空格區分，必須同時符合)
    # ==========================================
    if keyword:
        # split() 會自動把字串依照空格切成陣列，且自動忽略多餘的連續空格
        keywords_list = keyword.lower().split()
        
        # 使用 Python 的 all() 函數，確保每一個關鍵字都有出現在店名、地址或分類中
        results = [
            s for s in results 
            if all(
                kw in s.get('name', '').lower() or 
                kw in s.get('addr', '').lower() or 
                kw in s.get('cat', '').lower()
                for kw in keywords_list
            )
        ]

    # 4. 執行分頁切割
    total_count = len(results)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_results = results[start_idx:end_idx]

    # 5. 組合回傳資料格式
    response_data = {
        "total": total_count,
        "page": page,
        "limit": limit,
        "data": paginated_results
    }

    return func.HttpResponse(
        json.dumps(response_data, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )

# ==========================================
# 🌟 新增的 API 說明文件端點 (Doc)
# ==========================================
@app.route(route="tw_search/Doc", methods=["GET"])
def api_doc(req: func.HttpRequest) -> func.HttpResponse:
    # 這裡撰寫 HTML 內容，加上簡單的 CSS 排版讓畫面更好看
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>特約商店搜尋 API 說明文件</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }
            h1 { color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px; }
            h2 { color: #333; margin-top: 30px; }
            .endpoint { background-color: #e1dfdd; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 1.2em; }
            .method { background-color: #107c10; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 0.9em; margin-right: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #0078D4; color: white; }
            .example { background-color: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }
            a { color: #0078D4; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>📚 特約商店搜尋 API 說明文件</h1>
        <p>這支 API 提供快速檢索國民旅遊卡特約商店資料的功能，支援多重條件過濾與分頁功能。</p>

        <h2>📍 請求端點 (Endpoint)</h2>
        <div class="endpoint">
            <span class="method">GET</span> /api/tw_search
        </div>

        <h2>⚙️ 查詢參數 (Query Parameters)</h2>
        <table>
            <tr>
                <th>參數名稱</th>
                <th>型別</th>
                <th>必填</th>
                <th>說明與範例</th>
            </tr>
            <tr>
                <td><code>county</code></td>
                <td>String</td>
                <td>否</td>
                <td>依縣市過濾。例如：<code>台北市</code>、<code>苗栗縣</code></td>
            </tr>
            <tr>
                <td><code>category</code></td>
                <td>String</td>
                <td>否</td>
                <td>依分類過濾。例如：<code>餐飲業</code>、<code>旅宿業</code></td>
            </tr>
            <tr>
                <td><code>keyword</code></td>
                <td>String</td>
                <td>否</td>
                <td>模糊搜尋。支援多關鍵字（以空格分隔）。比對店名、地址或分類。例如：<code>飯店 台北</code></td>
            </tr>
            <tr>
                <td><code>page</code></td>
                <td>Integer</td>
                <td>否</td>
                <td>請求的頁碼。預設為 <code>1</code></td>
            </tr>
            <tr>
                <td><code>limit</code></td>
                <td>Integer</td>
                <td>否</td>
                <td>每頁回傳的資料筆數。預設為 <code>10</code></td>
            </tr>
        </table>

        <h2>🚀 測試範例 (點擊直接測試)</h2>
        <ul>
            <li><strong>搜尋特定縣市：</strong> <br><a href="/api/tw_search?county=苗栗縣" target="_blank">/api/tw_search?county=苗栗縣</a></li>
            <li><strong>複合搜尋 (縣市 + 關鍵字)：</strong> <br><a href="/api/tw_search?county=台北市&keyword=咖啡" target="_blank">/api/tw_search?county=台北市&keyword=咖啡</a></li>
            <li><strong>測試分頁 (第2頁，每頁5筆)：</strong> <br><a href="/api/tw_search?county=台中市&page=2&limit=5" target="_blank">/api/tw_search?county=台中市&page=2&limit=5</a></li>
        </ul>

        <h2>📦 回傳格式 (JSON)</h2>
        <div class="example">
{
  "total": 125,
  "page": 1,
  "limit": 10,
  "data": [
    {
      "name": "測試商店名稱",
      "county": "台北市",
      "cat": "餐飲業",
      "addr": "台北市中正區測試路1號"
    }
  ]
}
        </div>
    </body>
    </html>
    """
    
    # 回傳時將 mimetype 設為 text/html，瀏覽器就會把它渲染成網頁
    return func.HttpResponse(
        html_content,
        mimetype="text/html",
        status_code=200
    )