"""Score a student submission against the hidden labels (teacher only).

Usage:
    python -I scripts/score_submission.py HIDDEN_LABELS_PRIVATE.csv SUBMISSION.csv

SUBMISSION.csv columns: image, prob_dr   (probability that the image is DR),
produced by running the student's predict.py on the hidden images.
Reports overall and per-source accuracy, F1 and AUC at threshold 0.5.
"""
import csv, sys
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


def main(truth_path, sub_path):
    truth = {r["image"]: r for r in csv.DictReader(open(truth_path))}
    sub = {r["image"]: float(r["prob_dr"]) for r in csv.DictReader(open(sub_path))}
    missing = set(truth) - set(sub)
    if missing:
        sys.exit(f"submission is missing {len(missing)} hidden images")
    for name, keep in [("all", None), ("odir", "odir"), ("mendeley", "mendeley")]:
        ids = [i for i in truth if keep is None or truth[i]["source"] == keep]
        y = [truth[i]["label"] == "dr" for i in ids]
        p = [sub[i] for i in ids]
        pred = [v >= 0.5 for v in p]
        print(f"{name:9s} n={len(ids):5d} acc={accuracy_score(y, pred):.3f} "
              f"f1={f1_score(y, pred):.3f} auc={roc_auc_score(y, p):.3f}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
