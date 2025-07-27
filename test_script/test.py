import pandas as pd

OUTPUT_PATH = "data/output.csv"

# 定義「18 禁商品」的分類關鍵字（可自行調整）
ADULT_CATEGORIES = {
    '情趣內衣', '飛機杯', '跳蛋', 'SM精品', '情趣按摩棒', '仿真娃娃', '後庭棒',
    '震動環', '吸吮器', '加熱棒', '陽具環', '馬眼棒', '乳夾', '乳房按摩器', '真空吸引器',
    '指套', '陽具加長套', '男情趣內著', '性感睡衣', '基本型', '威而柔', '活力保養',
    '後庭清潔', '聰明球', '備孕潤滑液'
}

def main():
    df = pd.read_csv(OUTPUT_PATH)

    total = len(df)
    detected_adult = df[df["category"].isin(ADULT_CATEGORIES)]
    count = len(detected_adult)

    print(f"📦 Output 總商品數：{total}")
    print(f"🔞 模型判斷為 18 禁 的商品數：{count}")
    print(f"📊 佔比：{count / total * 100:.2f}%")
    
    print("\n🧾 範例前幾筆 18 禁商品：")
    print(detected_adult[["GOODS_CODE", "GOODS_NAME", "category"]].head(10))

if __name__ == "__main__":
    main()
