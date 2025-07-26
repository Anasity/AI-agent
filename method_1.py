import pandas as pd
import numpy as np
import multiprocessing as mp
import time

deposits = pd.read_csv('deposits.csv', sep=';')

GOAL_CHOICES = {
    1: {'name': 'max_income', 'desc': "Максимальный доход (прибыль в краткие сроки)"},
    2: {'name': 'savings', 'desc': "Накопление на цель, крупную покупку"},
    3: {'name': 'passive_income', 'desc': "Пассивный доход (частые выплаты процентов)"},
    4: {'name': 'flexible', 'desc': "Гибкое управление (возможность снятия и пополнения без штрафов)"},
    5: {'name': 'long_term', 'desc': "Долгосрочные сбережения (подушка безопасности)"}
}

def get_user_input():
    print("\u001b[1m\nВыберите финансовую цель:\u001b[0m")
    for num, goal in GOAL_CHOICES.items():
        print(f"{num}. {goal['desc']}")

    goal_num = int(input("\nНомер цели (1-5): "))
    print("\u001b[1m\nПАРАМЕТРЫ ВКЛАДА\u001b[0m")
    amount = int(input("Сумма для вклада (руб): "))
    term = int(input("Срок (1-36 мес., 0 - бессрочно): "))
    replenish = input("Нужно пополнение? (да/нет): ").lower() == 'да'
    withdrawal = input("Нужно снятие? (да/нет): ").lower() == 'да'
    print("Выплата процентов:")
    print("1 - Ежемесячно")
    print("2 - В конце срока")
    print("3 - Без разницы")
    payout = input("Ваш выбор (1-3): ")

    return {
        'goal': GOAL_CHOICES[goal_num]['name'],
        'goal_desc': GOAL_CHOICES[goal_num]['desc'],
        'amount': amount,
        'term': term,
        'replenish': replenish,
        'withdrawal': withdrawal,
        'payout': payout
    }

def calculate_score(deposit, user, max_rate):
    score = 0

    # 1. Совпадение цели (30 баллов, если совпадает)
    if deposit['goal'] == user['goal']:
        score += 30

    # 2. Ставка (30% веса)
    score += (deposit['rate'] / max_rate) * 30

    # 3. Срок (20% веса)
    if deposit['term_max'] == 0 or user['term'] <= deposit['term_max']:
        score += 20

    # 4. Пополнение (10% веса)
    if deposit['replenishable'] == user['replenish']:
        score += 10

    # 5. Снятие (10% веса)
    if deposit['withdrawal'] == user['withdrawal']:
        score += 10

    return round(score, 1)

def process_deposits(args):
    deposits_subset, user_data, max_rate = args
    results = []
    for _, deposit in deposits_subset.iterrows():
        if user_data['amount'] >= deposit['min_sum'] * 0.8:
            score = calculate_score(deposit, user_data, max_rate)
            results.append({
                'name': deposit['name'],
                'rate': deposit['rate'],
                'min_sum': deposit['min_sum'],
                'score': score,
                'goal': deposit['goal'],
                'needs_extra': user_data['amount'] < deposit['min_sum']
            })
    return results

def recommend_deposit_parallel(user_data, num_processes=4):
    max_rate = deposits['rate'].max()

    total_deposits = len(deposits)
    chunk_size = total_deposits // num_processes
    chunks = []

    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < num_processes - 1 else total_deposits
        chunks.append((deposits.iloc[start_idx:end_idx], user_data, max_rate))

    with mp.Pool(num_processes) as pool:
        results = pool.map(process_deposits, chunks)

    all_recommendations = []
    for chunk_result in results:
        all_recommendations.extend(chunk_result)

    all_recommendations.sort(key=lambda x: x['score'], reverse=True)
    return all_recommendations


def print_recommendations(rated_deposits, user_data):
    if not rated_deposits:
        print("\nНет подходящих вкладов")
        return

    print(f"\u001b[1m\nРЕКОМЕНДАЦИИ\u001b[0m")

    best = rated_deposits[0]
    if best['needs_extra']:
        missing = best['min_sum'] - user_data['amount']
        print(f"1. Совет: Доплатите {missing} ₽, чтобы выбрать вклад: \u001b[1m{best['name']}\u001b[0m")
        print(f"   Ставка: {best['rate']}% | Подходит Вам на: {best['score']}/100")

        for deposit in rated_deposits:
            if not deposit['needs_extra']:
                print(f"2. Без доплат: \u001b[1m{deposit['name']}\u001b[0m")
                print(f"   Ставка: {deposit['rate']}% | Подходит Вам на: {deposit['score']}/100")
                break
    else:
        print(f"1. {best['name']}")
        print(f"   Ставка: {best['rate']}% | Подходит Вам на: {best['score']}/100")

def main():
    user_data = get_user_input()

    start_time = time.time()

    recommendations = recommend_deposit_parallel(user_data, num_processes=4)

    end_time = time.time()
    execution_time = end_time - start_time

    print_recommendations(recommendations, user_data)
    print(f"\n\u001b[1mВремя выполнения программы: {execution_time:.4f} секунд\u001b[0m")

if __name__ == "__main__":
    mp.freeze_support()
    main()
