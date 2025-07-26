import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import export_text

history = pd.read_csv('data.csv', sep=';', encoding='utf-8-sig') 

le = LabelEncoder()
history['chosen_deposit_encoded'] = le.fit_transform(history['chosen'])

X = history[['min_sum', 'term', 'replenish', 'withdrawal']]
y = history['chosen_deposit_encoded']

model = DecisionTreeClassifier(max_depth=6, random_state=42)
model.fit(X, y)

def get_user_input():

    amount = int(input("\n1. Сумма для вклада (руб): "))
    term = int(input("\n2. Срок (1-36 мес., 0 - бессрочно): "))
    replenish = input("\n3. Нужно пополнение? (да/нет): ").lower() == 'да'
    withdrawal = input("4. Нужно снятие? (да/нет): ").lower() == 'да'
    print("\n5. Выплата процентов: ")
    print("   1 - Ежемесячно")
    print("   2 - В конце срока")
    print("   3 - Без разницы")
    payout_pref = int(input("Ваш выбор (1-3): "))

    return {
        'min_sum': amount,
        'term': term,
        'replenish': replenish,
        'withdrawal': withdrawal,
    }

def recommend_deposit(user_data):
    input_df = pd.DataFrame([user_data])

    print("\nДерево решений, использованное для рекомендации:")
    print(" ")
    tree_rules = export_text(model,
                             feature_names=['min_sum', 'term', 'replenish', 'withdrawal'],
                             class_names=le.classes_)
    print(tree_rules)
    print(" ")

       prediction = model.predict(input_df)
    return le.inverse_transform(prediction)[0]

user_data = get_user_input()
recommended_deposit = recommend_deposit(user_data)

print(f"Рекомендуемый вклад: {recommended_deposit}")

deposits_info = {
    "Лучший %": "Высокий процент (18%), без пополнения, снятие разрешено",
    "СберВклад": "Гибкие условия (18%), с пополнением и снятием",
    "Накопительный счёт": "Бессрочный вклад (16%), пополнение и снятие"
}
