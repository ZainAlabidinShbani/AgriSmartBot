from investment_data import investment_examples

def calculate_profit(crop_name, area_dunum=1):
    data = investment_examples.get(crop_name)
    if not data:
        return "❌ لا توجد بيانات استثمارية لهذا المحصول."

    total_cost = data["area_cost"] * area_dunum
    total_yield = data["expected_yield"] * area_dunum
    total_revenue = total_yield * data["price_per_kg"]
    profit = total_revenue - total_cost

    return (
        f"📊 التقدير الاستثماري لمحصول {crop_name}:\n"
        f"📏 المساحة: {area_dunum} دونم\n"
        f"💰 التكلفة الإجمالية: {total_cost:.2f} دولار\n"
        f"🌾 الإنتاج المتوقع: {total_yield:,} كغ\n"
        f"💵 الإيرادات المتوقعة: {total_revenue:.2f} دولار\n"
        f"✅ الربح الصافي المتوقع: {profit:.2f} دولار\n"
        f"🗓 أشهر الحصاد: {', '.join(map(str, data['harvest_months']))}"
    )
