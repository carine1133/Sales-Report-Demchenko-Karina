#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "Данные для тестового задания.csv"
DST = sys.argv[2] if len(sys.argv) > 2 else "daily_by_sku.csv"

STATUS_ALIASES = {"canceled": "cancelled"}


def norm_status(raw):
    s = raw.strip().lower()
    return STATUS_ALIASES.get(s, s)


def main():
    seen = {}  
    stats = defaultdict(lambda: {"orders": 0, "revenue": 0})
    dup_exact = dup_conflict = 0

    with open(SRC, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            oid = row["order_id"].strip()
            sku = row["sku"].strip()
            day = row["order_date"].strip()
            status = norm_status(row["status"])
            qty_raw = row["quantity"].strip()
            price_raw = row["price"].strip()
            key = (sku, day, status, qty_raw, price_raw)

            if oid in seen:
                if seen[oid] == key:
                    dup_exact += 1
                else:
                    dup_conflict += 1 
                continue
            seen[oid] = key

            s = stats[(sku, day)]
            s["orders"] += 1
            if status == "delivered":
                s["revenue"] += int(qty_raw) * int(price_raw)

    with open(DST, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["sku", "order_date", "orders", "revenue"])
        for (sku, day) in sorted(stats):
            w.writerow([sku, day, stats[(sku, day)]["orders"], stats[(sku, day)]["revenue"]])

    print(f"уникальных заказов: {len(seen)}, строк: {len(stats)}", file=sys.stderr)
    print(f"дублей пропущено: {dup_exact}, конфликтных: {dup_conflict}", file=sys.stderr)
    print(f"результат: {DST}", file=sys.stderr)


if __name__ == "__main__":
    main()


