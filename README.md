вот отформатированный и чисто оформленный `README.md`, готовый для GitHub:

---

````markdown
# Uniswap v3 Hedge Calculator

A simple terminal-based calculator for simulating Uniswap v3 LP positions hedged with short ETH.

Supports two strategies:
- Hedge only impermanent loss (LP)
- Hedge LP + Aave-style ETH exposure (fully neutral)

---

### 🔧 Requirements

```bash
pip install -r requirements.txt
````

---

### 🚀 Run

```bash
python lpshort.py
```

---

### ✍️ Inputs

* Amount of ETH deposited in Aave
* Amount of USDC borrowed and used in Uniswap LP
* Price range of Uniswap position
* Price of ETH at short entry
* Current ETH price (optional, for PnL check)

---

### 📊 Outputs

* Required short size to hedge LP or LP+Aave
* IL, real drawdown, and net PnL at given ETH price
* Clean summary table in the console

---

> Built for research and educational purposes.
> Use with care. Feedback welcome.

```

---

если файл называется не `lpshort.py`, просто замени название в секции `Run`.  
хочешь — добавим скриншот с примером таблицы прямо в README.
```
