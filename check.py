#!/usr/bin/env python3

import sys
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "Данные для тестового задания.csv"
res = sys.argv[2] if len(sys.argv) > 2 else "daily_by_sku.csv"

raw = pd.read_csv(src, dtype=str, keep_default_na=False)
d = raw.drop_duplicates("order_id").copy()
d["status"] = d["status"].str.strip().str.lower().replace({"canceled": "cancelled"})
assert set(d["status"]) == {"delivered", "cancelled"}, set(d["status"])
d["amount"] = (pd.to_numeric(d["quantity"], errors="coerce").fillna(0)
               * pd.to_numeric(d["price"])).where(d["status"] == "delivered", 0)

exp = (d.groupby(["sku", "order_date"])
         .agg(orders=("order_id", "size"), revenue=("amount", "sum"))
         .reset_index().sort_values(["sku", "order_date"]).reset_index(drop=True))
got = pd.read_csv(res)

assert got.equals(exp.astype(got.dtypes)), "результат не совпал с пандасным расчётом"
assert got["orders"].sum() == raw["order_id"].nunique(), "сумма orders != уникальных заказов"
assert not got.duplicated(["sku", "order_date"]).any()
print("OK")
print("уникальных заказов:", got["orders"].sum(), "| выручка:", got["revenue"].sum())
print("строк в файле:", len(got), "| сырых строк:", len(raw))
