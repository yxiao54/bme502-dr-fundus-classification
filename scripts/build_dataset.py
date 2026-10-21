"""Build the Normal-vs-DR classroom dataset from the extracted source folders.

Usage:
    python -I scripts/build_dataset.py WORK_DIR RELEASE_DIR PRIVATE_DIR

WORK_DIR must contain: ocular_N, ocular_D_odir, mend_healthy, mend_DR
RELEASE_DIR gets the student-facing files (images, train.csv, val.csv, zips).
PRIVATE_DIR gets the teacher-only files (test labels, source mapping).
"""
import csv, hashlib, os, random, re, shutil, sys, zipfile
from collections import defaultdict
from pathlib import Path
from PIL import Image

SEED = 2026
SIZE = 256
FRAC = {"train": 0.70, "val": 0.10, "test": 0.20}
SOURCES = [  # (folder, source, label)
    ("ocular_N", "odir", "normal"),
    ("ocular_D_odir", "odir", "dr"),
    ("mend_healthy", "mendeley", "normal"),
    ("mend_DR", "mendeley", "dr"),
]


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def collect(work):
    items, seen, dropped = [], set(), 0
    for folder, source, label in SOURCES:
        for p in sorted((work / folder).iterdir()):
            h = md5(p)
            if h in seen:
                dropped += 1
                continue
            seen.add(h)
            m = re.match(r"(\d+)_(left|right)\.", p.name)
            group = f"odir{m.group(1)}" if m else f"{source}:{p.stem}"
            items.append(dict(path=p, source=source, label=label, group=group, orig=f"{folder}/{p.name}"))
    print(f"collected {len(items)} images, dropped {dropped} exact duplicates")
    return items


def cut(groups, rng):
    """Shuffle groups and cut them into splits by group count."""
    groups = sorted(groups)
    rng.shuffle(groups)
    n = len(groups)
    a, b = round(n * FRAC["train"]), round(n * (FRAC["train"] + FRAC["val"]))
    return {"train": groups[:a], "val": groups[a:b], "test": groups[b:]}


def assign(items, rng):
    by_group = defaultdict(list)
    for it in items:
        by_group[it["group"]].append(it)
    # stratify groups by (source, label-set) so mixed N/DR patients stay together
    strata = defaultdict(list)
    for g, its in by_group.items():
        key = (its[0]["source"], "+".join(sorted({i["label"] for i in its})))
        strata[key].append(g)
    split_of = {}
    for key in sorted(strata):
        for split, gs in cut(strata[key], rng).items():
            for g in gs:
                split_of[g] = split
    for it in items:
        it["split"] = split_of[it["group"]]


def preprocess(src, dst):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    s = max(w, h)
    canvas = Image.new("RGB", (s, s), (0, 0, 0))  # pad, never crop or stretch
    canvas.paste(im, ((s - w) // 2, (s - h) // 2))
    canvas.resize((SIZE, SIZE), Image.LANCZOS).save(dst, "JPEG", quality=95)


def main(work, release, private):
    work, release, private = Path(work), Path(release), Path(private)
    for d in (release, private):
        d.mkdir(parents=True, exist_ok=True)
        if any(d.iterdir()):
            sys.exit(f"{d} is not empty")
    rng = random.Random(SEED)
    items = collect(work)
    assign(items, rng)
    rng.shuffle(items)
    for split in FRAC:
        (release / "images" / split).mkdir(parents=True)
    rows = []
    for i, it in enumerate(items):
        name = f"img_{i:05d}.jpg"
        preprocess(it["path"], release / "images" / it["split"] / name)
        rows.append(dict(image=name, label=it["label"], split=it["split"], source=it["source"], orig=it["orig"]))
    for split in ("train", "val"):
        with open(release / f"{split}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["image", "label"])
            w.writerows((r["image"], r["label"]) for r in rows if r["split"] == split)
    with open(release / "test_images.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["image"])
        w.writerows([r["image"]] for r in rows if r["split"] == "test")
    with open(private / "all_images_private.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(private / "test_labels_private.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["image", "label", "source"])
        w.writerows((r["image"], r["label"], r["source"]) for r in rows if r["split"] == "test")
    # archives: train+val (with labels) and test (images only)
    def pack(zpath, splits, extra):
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
            for s in splits:
                for p in sorted((release / "images" / s).iterdir()):
                    z.write(p, f"{s}/{p.name}")
            for e in extra:
                z.write(release / e, e)
    pack(release / "train_val.zip", ["train", "val"], ["train.csv", "val.csv"])
    pack(release / "test_images.zip", ["test"], ["test_images.csv"])
    tally = defaultdict(int)
    for r in rows:
        tally[(r["split"], r["source"], r["label"])] += 1
    for k in sorted(tally):
        print(*k, tally[k])


if __name__ == "__main__":
    main(*sys.argv[1:4])
