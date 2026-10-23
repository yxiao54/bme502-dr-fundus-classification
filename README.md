# Normal vs. Diabetic Retinopathy: a binary classification assignment

A classroom dataset of colour fundus photographs for practising binary image
classification: **normal** (label `normal`) vs. **diabetic retinopathy** (label `dr`).
Images are merged from two public sources, de-duplicated, resized to 256×256 and
split into train / validation / test (all labelled) and a hidden set whose images are released but whose labels only the instructor holds.

## Download

The images are too large for GitHub and are hosted on Google Drive.

| File | Size | Contents | Link |
|---|---|---|---|
| `train_val_test.zip` | 114 MB | 5,012 train + 715 val + 705 test images, with `train.csv`, `val.csv`, `test.csv` (labels included) | [Google Drive](https://drive.google.com/file/d/1qKhlWGLvTDMPcT37DpYTpyZUX8LBqUBz/view?usp=sharing) |
| `hidden_images.zip` | 13 MB | 715 hidden images, `hidden_images.csv` (**no labels**) | _TODO: add Google Drive link_ |

## Dataset

| Split | Normal | DR | Total |
|---|---|---|---|
| train | 2,826 | 2,186 | 5,012 |
| val | 404 | 311 | 715 |
| test (labelled) | 394 | 311 | 705 |
| hidden (images only, labels held by instructor) | 397 | 318 | 715 |
| **all** | **4,021** | **3,126** | **7,147** |

Image format: RGB JPEG, 256×256. Originals are padded with black to a square
(never cropped or stretched) before resizing. File names are neutral
(`img_00000.jpg`) and carry no label or source information.

### Sources

| Source | Normal | DR | Notes |
|---|---|---|---|
| ODIR-2019 (via the Kaggle *Ocular Disease Dataset* by Manan_1717) | 2,997 | 1,619 | Round fundus images, about 1570 px. Left/right eye of the same patient share an ID. |
| Mendeley *Eye Disease Image Dataset* (Rashid et al., 2024) | 1,024 | 1,509 | Images from two eye hospitals in Bangladesh; 2004×1690 px, top and bottom of the circle are cut off. |

Cleaning steps: the Kaggle dataset's 1,509 `DR*.jpg` images were dropped because
they are the same images as the Mendeley DR class; 2 byte-identical duplicates
were removed. The ODIR5K_Classification Kaggle dataset was **not** used: its
`normal` class duplicates the Ocular Disease Dataset's `N` class, and its images
are 224×224 with swapped colour channels.

### How the split was made

- 70 / 10 / 10 / 10 split into train / val / test / hidden, seed 2026, stratified by (source × class).
- **ODIR images are split by patient**: both eyes of a patient, including patients
  with one normal and one DR eye (236 of them), always land in the same split.
  No patient appears in more than one split (verified).
- Mendeley images have no patient ID and are split by file, so the same patient's
  images may appear on both sides of a split.

### Known pitfalls (good discussion material)

- **Source shortcut.** DR makes up 35% of the ODIR images but 60% of the Mendeley
  images, and the two sources look different (circle shape, colour, resolution).
  A model can score well partly by recognising the source. Compare per-source
  results before trusting a high accuracy.
- Classes are mildly imbalanced (56% normal); report F1 and AUC, not just accuracy.
- The labels come from the source datasets and were not re-checked by us.

## Assignment (student version)

1. Download `train_val_test.zip` and train a binary classifier on `train/`; tune on `val/`.
2. Evaluate **once**, at the end, on `test/` and report your test accuracy. Do not tune on it.
3. Download `hidden_images.zip` and predict `prob_dr` (probability of DR) for every image in it.
4. Submit `submission.csv` with columns `image,prob_dr`, plus your notebook.
5. Do not look for or use the original datasets' labels for the hidden images.

Grading uses the hidden set. Compare your own test accuracy with your hidden-set
result: a large gap suggests the test set was used for tuning.

## Repository layout

```
scripts/build_dataset.py      rebuilds the dataset from the extracted source folders
scripts/score_submission.py   instructor-only scoring of a submission against the hidden labels
scripts/requirements.txt
```

`teacher_private/` (hidden labels and the image-to-source mapping) is
git-ignored and must never be committed or shared with students.

## Rebuilding

Extract the source classes into one folder (`ocular_N`, `ocular_D_odir`,
`mend_healthy`, `mend_DR`; `ocular_D_odir` is the `*_left/_right` files of the
Kaggle dataset's `D` folder), then:

```bash
pip install -r scripts/requirements.txt
python -I scripts/build_dataset.py WORK_DIR RELEASE_DIR PRIVATE_DIR
```

## Attribution and licences

- Mendeley Eye Disease Image Dataset: Rashid, Sharmin, Khatun, Hasan, Uddin (2024),
  DOI 10.17632/s9bfhswzjb.1, licence **CC BY 4.0**.
- Ocular Disease Dataset (Kaggle, Manan_1717): MIT; it merges ODIR-2019 and other
  public datasets, so check the original licences before any commercial use.
- ODIR-2019 Grand Challenge: https://odir2019.grand-challenge.org/ (please cite it
  in research use).

Check that redistributing the images, even on Google Drive, is compatible with
these terms before sharing the link outside your class.
