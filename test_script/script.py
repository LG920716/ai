import pandas as pd
import requests
import time

INPUT_PATH = "data/input.csv"
OUTPUT_PATH = "data/output.csv"
API_URL = "http://51.249.50.36:8080/score"

def call_api(title, img_url):
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"title": title, "img_url": img_url},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json().get("answer", {})
            # 解碼 category 中文（通常不需轉，但保險處理）
            category = result.get("category", "").encode().decode("unicode_escape")
            return {
                "category": category,
                "image_result": result.get("image_result", ""),
                "title_result": result.get("title_result", "")
            }
        else:
            print(f"[ERROR] Status code {response.status_code} for title: {title}")
    except Exception as e:
        print(f"[EXCEPTION] {e} for title: {title}")
    return {
        "category": "ERROR",
        "image_result": "",
        "title_result": ""
    }

def main():
    df = pd.read_csv(INPUT_PATH)

    results = []
    for idx, row in df.iterrows():
        print(f"Processing row {idx+1}/{len(df)}: {row['GOODS_NAME'][:30]}...")
        api_result = call_api(row["GOODS_NAME"], row["img_url"])
        results.append(api_result)
        time.sleep(0.5)  # 為了避免過快請求，可調整

    # 將結果轉成 DataFrame 並合併
    result_df = pd.DataFrame(results)
    output_df = pd.concat([df.iloc[:, :2], result_df, df.iloc[:, 2:]], axis=1)
    output_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n✅ Finished. Output saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
