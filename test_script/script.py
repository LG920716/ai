import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_PATH = "data/input.csv"
OUTPUT_PATH = "data/output.csv"

API_URL = "http://36.50.249.51:8080/score"

# 對照表
type_code_dict = {
    '威而柔': '1600500008', '活力保養': '1600500009', '基本型': '1600500010', '備孕潤滑液': '1600500011',
    '仿真娃娃': '1600700001', '吸吮器': '1600700002', '情趣按摩棒': '1600700004', '飛機杯': '1600700005',
    '跳蛋': '1600700006', '聰明球': '1600700008', '後庭清潔': '1600700009', '後庭棒': '1600700010',
    'SM精品': '1600700011', '加熱棒': '1600700012', '乳夾': '1600700013', '乳房按摩器': '1600700014',
    '指套': '1600700015', '真空吸引器': '1600700016', '馬眼棒': '1600700017', '陽具加長套': '1600700018',
    '陽具環': '1600700019', '震動環': '1600700020', '情趣內衣': '1900300006', '男情趣內著': '1900400006',
    '性感睡衣': '1900600003'
}

def call_api(title, img_url, retry=1):
    for attempt in range(retry + 1):
        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                json={"title": title, "img_url": img_url},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json().get("answer", {})
                category = result.get("category", "").strip()
                category_code = type_code_dict.get(category, "UNK")
                return {
                    "category": category,
                    "category_code": category_code,
                    "image_result": result.get("image_result", ""),
                    "title_result": result.get("title_result", "")
                }
            else:
                print(f"[ERROR] Status code {response.status_code} for title: {title}")
        except Exception as e:
            print(f"[EXCEPTION] {e} for title: {title}")
            time.sleep(0.5)  # 緩一緩主機壓力

    return {
        "category": "ERROR",
        "category_code": "ERR",
        "image_result": "",
        "title_result": ""
    }

def main():
    df = pd.read_csv(INPUT_PATH)
    results = [None] * len(df)
    MAX_WORKERS = 3  # 更保守，避免 timeout（可依情況調回 4~5）

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_idx = {
            executor.submit(call_api, row["GOODS_NAME"], row["img_url"]): idx
            for idx, row in df.iterrows()
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
                print(f"✅ Processed {idx + 1}/{len(df)}: {df.iloc[idx]['GOODS_NAME'][:30]}")
            except Exception as e:
                print(f"❌ Failed {idx + 1}: {e}")
                results[idx] = {
                    "category": "ERROR",
                    "category_code": "ERR",
                    "image_result": "",
                    "title_result": ""
                }
            time.sleep(0.15)  # 加入微延遲避免壓垮 Docker

    result_df = pd.DataFrame(results)
    output_df = pd.concat([df.iloc[:, :2], result_df, df.iloc[:, 2:]], axis=1)
    output_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n✅ Output saved to: {OUTPUT_PATH}")

    # === 計算分類準確率（只看是否分類正確）===
    if "L4_CAT_NAME" in df.columns:
        correct = 0
        total = len(df)
        for i in range(total):
            if result_df.iloc[i]["category"] == df.iloc[i]["L4_CAT_NAME"]:
                correct += 1
        accuracy = correct / total * 100
        print(f"\n🎯 準確率：{accuracy:.2f}%（{correct}/{total}）")

if __name__ == "__main__":
    main()
