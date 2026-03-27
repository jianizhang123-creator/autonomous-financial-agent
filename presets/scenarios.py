"""
Preset financial-goal scenarios for the interactive demo.
"""

PRESETS = [
    {
        "id": "save_5000",
        "name": "三个月攒5000块",
        "name_en": "Save \u00a55000 in 3 Months",
        "goal": "我想在三个月内攒下5000块钱",
        "goal_type": "savings",
        "target_amount": 5000,
        "target_days": 90,
        "description": "Moderate savings goal with balanced lifestyle adjustments",
    },
    {
        "id": "pay_debt",
        "name": "还清信用卡8000元",
        "name_en": "Pay Off \u00a58000 Credit Card",
        "goal": "我需要在两个月内还清8000元的信用卡账单",
        "goal_type": "debt_repayment",
        "target_amount": 8000,
        "target_days": 60,
        "description": "Aggressive debt repayment requiring significant spending cuts",
    },
    {
        "id": "cut_delivery",
        "name": "每月减少外卖开支30%",
        "name_en": "Cut Delivery Spending 30%",
        "goal": "我想把每月外卖开支从900元减少到630元以下",
        "goal_type": "spending_reduction",
        "target_amount": 270,
        "target_days": 30,
        "description": "Behavioral change goal targeting a specific spending category",
    },
]
