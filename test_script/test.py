import pandas as pd
from sklearn.metrics import confusion_matrix

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
ADULT_CATEGORIES = set(type_code_dict.keys())

def check_is_correct(row):
    if row["category"] == "ERROR":
        return False

    pred_is_adult = row["category"] in ADULT_CATEGORIES
    true_is_adult = row["L4_CAT_NAME"] in ADULT_CATEGORIES

    if pred_is_adult and true_is_adult:
        return row["category"] == row["L4_CAT_NAME"]
    elif not pred_is_adult and not true_is_adult:
        return True
    else:
        return False

def analyze_output(path="data/output.csv"):
    df = pd.read_csv(path)

    df["is_adult_pred"] = df["category"].isin(ADULT_CATEGORIES)
    df["is_adult_true"] = df["L4_CAT_NAME"].isin(ADULT_CATEGORIES)
    df["is_correct"] = df.apply(check_is_correct, axis=1)

    # === 分類準確率 ===
    correct = df["is_correct"].sum()
    total = len(df)
    accuracy = correct / total * 100
    print(f"\n🎯 分類準確率：{accuracy:.2f}%（{correct}/{total}）")

    # === 成人 / 非成人 區分準確率 ===
    df["is_adult_match"] = df["is_adult_pred"] == df["is_adult_true"]
    adult_match = df["is_adult_match"].sum()
    adult_match_rate = (adult_match / len(df)) * 100
    print(f"📏 成人 / 非成人 區分準確率：{adult_match_rate:.2f}%（{adult_match}/{len(df)}）")

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

# 如果你要單獨執行
if __name__ == "__main__":
    analyze_output()
