import math
from tabulate import tabulate

def compute_static_short(aave_eth, usdc_borrowed, p_min, p_max, entry_price, cover_aave=True):
    sqrt_p_min = math.sqrt(p_min)
    sqrt_p_max = math.sqrt(p_max)

    L = usdc_borrowed / (sqrt_p_max - sqrt_p_min)

    eth_lp = L * (sqrt_p_max - sqrt_p_min) / (sqrt_p_min * sqrt_p_max)
    lp_value = eth_lp * p_min
    il = usdc_borrowed - lp_value

    aave_loss = aave_eth * (p_max - p_min) if cover_aave else 0
    total_loss = il + aave_loss

    short_eth = total_loss / (entry_price - p_min)
    short_usd = short_eth * entry_price

    return short_eth, short_usd, il, aave_loss, L


def compute_snapshot(p, L, p_min, p_max, usdc_borrowed, aave_eth, short_eth, entry_price, cover_aave=True):
    sqrt_p = math.sqrt(p)
    sqrt_p_min = math.sqrt(p_min)
    sqrt_p_max = math.sqrt(p_max)

    if p < p_min:
        eth_lp = L * (sqrt_p_max - sqrt_p_min) / (sqrt_p_min * sqrt_p_max)
        usdc_lp = 0
        lp_value = eth_lp * p
        fixed_il = usdc_borrowed - eth_lp * p_min
        lp_drawdown_due_to_price = eth_lp * (p_min - p)
    elif p > p_max:
        eth_lp = 0
        usdc_lp = L * (sqrt_p_max - sqrt_p_min)
        lp_value = usdc_lp
        fixed_il = 0
        lp_drawdown_due_to_price = 0
    else:
        eth_lp = L * (sqrt_p_max - sqrt_p) / (sqrt_p * sqrt_p_max)
        usdc_lp = L * (sqrt_p - sqrt_p_min)
        lp_value = eth_lp * p + usdc_lp
        fixed_il = usdc_borrowed - lp_value
        lp_drawdown_due_to_price = 0

    if p < p_min:
        usdc_lp = 0

    real_loss = usdc_borrowed - lp_value
    aave_loss = aave_eth * (entry_price - p) if cover_aave else 0
    short_profit = (entry_price - p) * short_eth
    net_pnl = short_profit - aave_loss - real_loss

    return {
        "price": p,
        "eth_in_lp": eth_lp,
        "usdc_in_lp": usdc_lp,
        "lp_value": lp_value,
        "fixed_il": fixed_il,
        "real_loss": real_loss,
        "lp_drawdown_due_to_price": lp_drawdown_due_to_price,
        "aave_loss": aave_loss,
        "short_profit": short_profit,
        "net_pnl": net_pnl
    }


def main():
    print("\n🧮 Uniswap v3 Hedge Calculator\n")

    try:
        aave_eth = float(input("Введите количество ETH, предоставленных в Aave: "))
        usdc_borrowed = float(input("Введите количество USDC, которые заняли и положили в пул на Uniswap: "))
        p_max = float(input("Введите верхний диапазон пула (напр. 2600): "))
        p_min = float(input("Введите нижний диапазон пула (напр. 2000): "))

        print("\nВыберите тип хеджа:")
        print("1 — Хеджировать только LP")
        print("2 — Хеджировать LP + AAVE")
        hedge_choice = input("Ваш выбор (1 или 2): ").strip()
        cover_aave = hedge_choice == "2"

        strategy_note = "LP + Aave" if cover_aave else "LP only"

        print("\nРекомендуется открывать шорт, когда цена находится внутри диапазона, чтобы LP уже работал и генерировал комиссии")
        entry_price = float(input("По какой цене ETH открываете шорт: "))

        short_eth, short_usd, il, aave_loss, L = compute_static_short(
            aave_eth, usdc_borrowed, p_min, p_max, entry_price, cover_aave
        )

        print("\n📊 Итог хеджа:")
        print(f"  - Необходимый сайз шорта: {short_eth:.4f} ETH")
        print(f"  - Размер шорта в $: ${short_usd:,.2f}")
        print(f"  - Непостоянные потери при ETH = ${p_min}: ${il:.2f}")
        if cover_aave:
            print(f"  - Потери на ETH (с {p_max} до {p_min}): ${aave_loss:.2f}")
        print(f"  - Общий риск, который хеджируется: ${il + aave_loss:.2f}\n")

        check_now = input("Цена уже находится в диапазоне? (y/n): ").strip().lower()
        if check_now == "y":
            current_price = float(input("По какой цене ETH проверить PnL (напр. 2300): "))
            snapshot = compute_snapshot(
                current_price, L, p_min, p_max,
                usdc_borrowed, aave_eth,
                short_eth, entry_price, cover_aave
            )

            print(f"\n📉 Результат по цене ETH = ${snapshot['price']:.2f}")
            print(f"  - ETH в LP: {snapshot['eth_in_lp']:.4f}")
            print(f"  - USDC в LP: {snapshot['usdc_in_lp']:.2f}")
            print(f"  - Стоимость LP: ${snapshot['lp_value']:.2f}")
            print(f"  - Текущий IL: ${snapshot['fixed_il']:.2f}")
            if snapshot['lp_drawdown_due_to_price'] > 0:
                print(f"  - Потери от падения ETH ниже диапазона: ${snapshot['lp_drawdown_due_to_price']:.2f}")
            if cover_aave:
                print(f"  - Убыток на ETH (в Aave): ${snapshot['aave_loss']:.2f}")
            print(f"  - PnL по шорту: ${snapshot['short_profit']:.2f}")
            print(f"  - Net PnL: ${snapshot['net_pnl']:.2f}")

            # Таблица итогов
            table = [
                ["Входные параметры", ""],
                ["", ""],
                ["ETH в Aave", f"{aave_eth:.4f}"],
                ["USDC в пуле", f"{usdc_borrowed:.2f}"],
                ["Диапазон пула", f"{p_min:.2f} – {p_max:.2f}"],
                ["Цена открытия шорта", f"{entry_price:.2f}"],
                ["Тип хеджа", strategy_note],
                ["", ""],
                ["Расчёт по цене ETH", f"{snapshot['price']:.2f}"],
                ["", ""],
                ["ETH в LP", f"{snapshot['eth_in_lp']:.4f}"],
                ["USDC в LP", f"{snapshot['usdc_in_lp']:.2f}"],
                ["Стоимость LP", f"${snapshot['lp_value']:.2f}"],
                ["Текущий IL", f"${snapshot['fixed_il']:.2f}"],
            ]
            if snapshot['lp_drawdown_due_to_price'] > 0:
                table.append(["Падение LP от ETH ниже диапазона", f"${snapshot['lp_drawdown_due_to_price']:.2f}"])
            if cover_aave:
                table.append(["Убыток на ETH (в Aave)", f"${snapshot['aave_loss']:.2f}"])
            table += [
                ["PnL по шорту", f"${snapshot['short_profit']:.2f}"],
                ["", ""],
                ["Net PnL", f"${snapshot['net_pnl']:.2f}"]
            ]

            print("\n📋 Таблица результатов:\n")
            print(tabulate(table, headers=["Показатель", "Значение"], tablefmt="github"))

    except Exception as e:
        print(f"\n🚨 Ошибка: {e}")


if __name__ == "__main__":
    main()
