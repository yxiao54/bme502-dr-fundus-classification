"""Check a submission file before it is scored. Needs no labels and takes about a second.

Usage:
    python -I scripts/check_submission.py hidden_images.csv submission.csv

hidden_images.csv is the file released with the hidden images (column: image).
submission.csv must have exactly the columns  image,prob_dr  and one row per hidden image.

Errors (exit code 1): wrong columns, missing images, extra images, duplicate rows, empty or
non-numeric values, NaN or infinite values, values outside [0, 1] (with a hint when they look
like logits).
Warnings (exit code 0): values that look like class labels, or a constant column.
"""
import csv, math, sys


def read_rows(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def main(hidden_path, sub_path):
    errors, warnings = [], []

    _, hidden_rows = read_rows(hidden_path)
    hidden = [r["image"] for r in hidden_rows]
    fields, rows = read_rows(sub_path)

    if fields != ["image", "prob_dr"]:
        sys.exit(f"ERROR: columns must be exactly image,prob_dr; found {fields}")

    names = [r["image"] for r in rows]
    seen, dup = set(), set()
    for n in names:
        (dup if n in seen else seen).add(n)
    missing = set(hidden) - seen
    extra = seen - set(hidden)
    if dup:
        errors.append(f"{len(dup)} duplicated image names, e.g. {sorted(dup)[:3]}")
    if missing:
        errors.append(f"{len(missing)} hidden images are missing, e.g. {sorted(missing)[:3]}")
    if extra:
        errors.append(f"{len(extra)} images are not in the hidden set, e.g. {sorted(extra)[:3]}")
    if len(rows) != len(hidden):
        errors.append(f"{len(rows)} rows, but the hidden set has {len(hidden)} images")

    values, bad_text, bad_number = [], 0, 0
    for r in rows:
        s = (r["prob_dr"] or "").strip()
        if s == "":
            bad_text += 1
            continue
        try:
            v = float(s)
        except ValueError:
            bad_text += 1
            continue
        if math.isnan(v) or math.isinf(v):
            bad_number += 1
            continue
        values.append(v)
    if bad_text:
        errors.append(f"{bad_text} prob_dr values are empty or not numbers")
    if bad_number:
        errors.append(f"{bad_number} prob_dr values are NaN or infinite")

    if values:
        lo, hi = min(values), max(values)
        out = sum(1 for v in values if v < 0 or v > 1)
        if out:
            hint = " These look like logits: apply a sigmoid, 1 / (1 + exp(-x))." if lo < 0 or hi > 1 else ""
            errors.append(f"{out} prob_dr values are outside [0, 1] (min {lo:.4g}, max {hi:.4g}).{hint}")
        if set(values) <= {0.0, 1.0}:
            warnings.append("every prob_dr is exactly 0 or 1: this looks like class labels, not probabilities. "
                            "AUROC needs a graded probability; save the model's probability output instead.")
        elif hi - lo < 1e-9:
            warnings.append(f"prob_dr is the same value ({lo:.4g}) for every row.")

    for w in warnings:
        print("WARNING:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        sys.exit(1)
    print(f"OK: {len(rows)} unique rows, all hidden images present, probabilities in [0, 1], no NaN.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:3])
