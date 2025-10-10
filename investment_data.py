investment_examples = {
    "كوسا": {
        "type": "short",  # موسم قصير (3-4 أشهر)
        "area_cost": 350,        # بالدولار للدونم الواحد (بذار + سماد + ري + عمالة)
        "expected_yield": 2500,  # إنتاج بالكيلو من الدونم
        "harvest_months": [5, 6, 7, 8],
        "price_per_kg": 0.6      # سعر تقريبي بالدولار للكيلو
    },
    "ورق العنب": {
        "type": "long",  # محصول دائم (كرمة)
        "area_cost": 700,        # تكلفة صيانة ورعاية سنوية
        "expected_yield": 1200,  # إنتاج بالكيلو من ورق صالح للتسويق
        "harvest_months": [5, 6],
        "price_per_kg": 2.5      # سعر تقريبي بالدولار للكيلو (موسمي)
    },
    "زيتون": {
        "type": "long",  # محصول شجري دائم
        "area_cost": 500,        # تكلفة صيانة وري وحراثة وسقاية سنوية
        "expected_yield": 800,   # إنتاج بالكيلو من الزيتون
        "harvest_months": [10, 11, 12],
        "price_per_kg": 1.2      # سعر تقريبي بالدولار للكيلو (زيتون خام)
    },
    "قمح": {
        "type": "short",
        "area_cost": 400,
        "expected_yield": 400,   # إنتاج بالكيلو من الدونم
        "harvest_months": [6, 7],
        "price_per_kg": 0.45
    },
    "بطاطا": {
        "type": "short",
        "area_cost": 600,
        "expected_yield": 3000,
        "harvest_months": [5, 6],
        "price_per_kg": 0.5
    },
    "تفاح": {
        "type": "long",
        "area_cost": 800,
        "expected_yield": 1500,
        "harvest_months": [9, 10],
        "price_per_kg": 0.8
    }
}
