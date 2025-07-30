import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.metrics import confusion_matrix

INPUT_PATH = "data/input.csv"
OUTPUT_PATH = "data/output.csv"

API_URL = "http://36.50.249.51:8080/score"

# 分類對照表
type_code_dict = {
    '威而柔': '1600500008', '活力保養': '1600500009', '基本型': '1600500010', '備孕潤滑液': '1600500011',
    '仿真娃娃': '1600700001', '吸吮器': '1600700002', '情趣按摩棒': '1600700004', '飛機杯': '1600700005',
    '跳蛋': '1600700006', '聰明球': '1600700008', '後庭清潔': '1600700009', '後庭棒': '1600700010',
    'SM精品': '1600700011', '加熱棒': '1600700012', '乳夾': '1600700013', '乳房按摩器': '1600700014',
    '指套': '1600700015', '真空吸引器': '1600700016', '馬眼棒': '1600700017', '陽具加長套': '1600700018',
    '陽具環': '1600700019', '震動環': '1600700020', '情趣內衣': '1900300006', '男情趣內著': '1900400006',
    '性感睡衣': '1900600003'
}

# 定義 18 禁分類清單
ADULT_CATEGORIES = set(type_code_dict.keys())

def call_api(title, img_url, retry=1):
    for attempt in range(retry + 1):
        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                json={"title": title, "img_url": img_url},
                timeout=60
            )
            if response.status_code == 200:
                result = response.json().get("answer", {})
                category = result.get("category", "").strip()
                category_code = type_code_dict.get(category, "-")
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
            time.sleep(0.5)
    return {
        "category": "ERROR",
        "category_code": "ERR",
        "image_result": "",
        "title_result": ""
    }

def main():
    df = pd.read_csv(INPUT_PATH)
    results = [None] * len(df)
    MAX_WORKERS = 4

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
            time.sleep(0.15)

    result_df = pd.DataFrame(results)
    output_df = pd.concat([df.iloc[:, :2], result_df, df.iloc[:, 2:]], axis=1)

    # 標記是否為 18 禁商品
    output_df["is_adult_pred"] = output_df["category"].isin(ADULT_CATEGORIES)
    output_df["is_adult_true"] = output_df["L4_CAT_NAME"].isin(ADULT_CATEGORIES)

    # === 改進版 is_correct 判斷邏輯 ===
    def check_is_correct(row):
        if row["category"] == "ERROR":
            return False

        pred_is_adult = row["category"] in ADULT_CATEGORIES
        true_is_adult = row["L4_CAT_NAME"] in ADULT_CATEGORIES

        if pred_is_adult and true_is_adult:
            return row["category"] == row["L4_CAT_NAME"]  # 成人 → 成人，還要分類正確
        elif not pred_is_adult and not true_is_adult:
            return True  # 非成人 → 非成人，只要預測非成人就算對
        else:
            return False  # 一個成人一個非成人 → 錯誤

    output_df["is_correct"] = output_df.apply(check_is_correct, axis=1)

    output_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n✅ Output saved to: {OUTPUT_PATH}")

    # === 準確率計算（只針對可比對的列）===
    valid_rows = output_df[~output_df["category_code"].isin(["UNK", "ERR"])]
    correct = valid_rows["is_correct"].sum()
    total = len(valid_rows)
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n🎯 分類準確率：{accuracy:.2f}%（{correct}/{total}）")

    # === 混淆矩陣（18禁 vs. 分類正確性）===
    print("\n📊 混淆矩陣（rows = is_adult_pred, cols = is_correct）")
    matrix = confusion_matrix(
        output_df["is_adult_true"], 
        output_df["is_correct"], 
        labels=[True, False]
    )
    print(f"""
          分類正確   分類錯誤
18禁商品     {matrix[0,0]:>5}       {matrix[0,1]:>5}
非18禁商品   {matrix[1,0]:>5}       {matrix[1,1]:>5}
    """)

    # === 18 禁判斷準確率（所有樣本都能算）===
    output_df["is_adult_match"] = output_df["is_adult_pred"] == output_df["is_adult_true"]
    adult_match_rate = output_df["is_adult_match"].mean() * 100
    adult_match_count = output_df["is_adult_match"].sum()
    print(f"\n🔞 18禁辨識準確率：{adult_match_rate:.2f}%（{adult_match_count}/{len(output_df)}）")

    # === 混淆矩陣（預測的是否是成人 vs 真實是否是成人）===
    print("\n📊 混淆矩陣（rows = 預測是否為成人, cols = 真實是否為成人）")
    matrix = confusion_matrix(
        df["is_adult_pred"],
        df["is_adult_true"],
        labels=[True, False]
    )
    print(f"""
                 真實是18禁   真實非18禁
預測是18禁       {matrix[0,0]:>5}         {matrix[0,1]:>5}
預測非18禁       {matrix[1,0]:>5}         {matrix[1,1]:>5}
    """)

if __name__ == "__main__":
    main()
