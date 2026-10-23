# Normal vs. Diabetic Retinopathy: a binary classification assignment

BME 502: Fundamentals of AI Medical Apps (Fall 2026 B)

A dataset of colour fundus photographs for practising binary image classification:
**normal** (label `normal`) vs. **diabetic retinopathy** (label `dr`). Images are
merged from two public sources, de-duplicated and resized to 256×256. They are split
into train / validation / test (all labelled) and a hidden set whose images are
released but whose labels are withheld.

## Download

The images are too large for GitHub and are hosted on Google Drive.

| File | Size | Contents | Link |
|---|---|---|---|
| `train_val_test.zip` | 119 MB | 5,012 train + 715 val + 705 test images, with `train.csv`, `val.csv`, `test.csv` (labels included) | [Google Drive](https://drive.google.com/file/d/13LAkbYtJi9Imwhvaef5v03r_TNCxpGP8/view?usp=sharing) |
| `hidden_images.zip` | 13 MB | 715 hidden images, `hidden_images.csv` (**no labels**) | [Google Drive](https://drive.google.com/file/d/1CF3Tj6vLqWVd1MNRmfZw3uxygvHrZoUS/view?usp=sharing) |

**Access:** please open the links with your ASU account. They are not available to other accounts.

**Metadata:** `metadata.csv` in this repository lists the split and the source dataset
(`odir` or `mendeley`) of every image, hidden ones included. It contains no labels.
Download it with the *Download raw file* button on its
[GitHub page](metadata.csv), or directly from
<https://raw.githubusercontent.com/yxiao54/bme502-dr-fundus-classification/main/metadata.csv>.

## Dataset

| Split | Normal | DR | Total |
|---|---|---|---|
| train | 2,826 | 2,186 | 5,012 |
| val | 404 | 311 | 715 |
| test (labelled) | 394 | 311 | 705 |
| hidden (images only, labels withheld) | 397 | 318 | 715 |
| **all** | **4,021** | **3,126** | **7,147** |

Image format: RGB JPEG, 256×256. Originals are padded with black to a square
(never cropped or stretched) before resizing. File names are neutral
(`img_00000.jpg`) and carry no label or source information; use `metadata.csv` to look up the source.

Each labelled CSV has the columns `image,label`, where `label` is `normal` or `dr`.
Encode them as you like, for example `normal` = 0 and `dr` = 1.

### Sources

| Source | Normal | DR | Notes |
|---|---|---|---|
| ODIR-2019 (via the Kaggle *Ocular Disease Dataset* by Manan_1717) | 2,997 | 1,619 | Round fundus images, about 1570 px. Left/right eye of the same patient share an ID. |
| Mendeley *Eye Disease Image Dataset* (Rashid et al., 2024) | 1,024 | 1,507 | Images from two eye hospitals in Bangladesh; 2004×1690 px, top and bottom of the circle are cut off. |

Cleaning: exact duplicate images were removed, and images that appear in both
source collections were kept only once.

### How the split was made

- 70 / 10 / 10 / 10 split into train / val / test / hidden, seed 2026, stratified by (source × class).
- **ODIR images are split by patient**: both eyes of a patient, including patients
  with one normal and one DR eye (236 of them), always land in the same split.
  No patient appears in more than one split (verified).
- **Mendeley images have no patient information**, so they are split randomly, image
  by image; images of the same eye may therefore appear in different splits.

### Things to think about

- **Source shortcut.** DR makes up 35% of the ODIR images but 60% of the Mendeley
  images, and the two sources look different (circle shape, colour, resolution).
  A model can score well partly by recognising the source. Does your model perform
  equally well on both kinds of image?
- **Mendeley scores may be too optimistic.** Because Mendeley images are split image
  by image, results on them are likely higher than on ODIR images. Compare the two
  (see `metadata.csv`): which would you trust more, and why?
- Classes are mildly imbalanced (56% normal); consider F1 and AUC, not just accuracy.
- The labels come from the source datasets and were not re-checked by us.

### Cross-dataset analysis (extension)

The two sources differ in camera, resolution, framing and class balance, so a model
that works on one may not work on the other. With `metadata.csv` you can, for example:

- report accuracy, F1 and AUC separately for ODIR and Mendeley images in `val` and `test`;
- train on one source only and test on the other, and compare with training on both;
- discuss why the per-source results differ, and what that means for using such a
  model on images from a new hospital.

## Assignment

1. Download `train_val_test.zip` and train a binary classifier on `train/`; tune on `val/`.
2. Evaluate **once**, at the end, on `test/` and report your test accuracy. Do not tune on it.
3. Download `hidden_images.zip` and predict `prob_dr` (probability of DR) for every image in it.
4. Prepare `submission.csv` with one row per hidden image and the columns
   `image,prob_dr`, for example:

   ```
   image,prob_dr
   img_00001.jpg,0.93
   img_00005.jpg,0.07
   ```

5. Work independently, and do not look for or use the original datasets' labels for
   the hidden images. Their labels are withheld on purpose, so please do not try
   to recover them by re-creating the split.

**How to submit:** TBD

**Evaluation:** TBD

## Repository layout

```
metadata.csv                  split and source (odir / mendeley) of every image, no labels
scripts/build_dataset.py      rebuilds the dataset from the extracted source folders
scripts/score_submission.py   scores a submission against the hidden labels (used by the instructor)
scripts/requirements.txt
```

## Rebuilding

The scripts are included for transparency. To see how the images were processed,
extract the source classes into one folder (`ocular_N`, `ocular_D_odir`,
`mend_healthy`, `mend_DR`; `ocular_D_odir` is the `*_left/_right` files of the
Kaggle dataset's `D` folder), then:

```bash
pip install -r scripts/requirements.txt
python -I scripts/build_dataset.py WORK_DIR RELEASE_DIR PRIVATE_DIR
```

## Attribution and licences

- Mendeley Eye Disease Image Dataset: Rashid, Sharmin, Khatun, Hasan, Uddin (2024),
  DOI 10.17632/s9bfhswzjb.1, licence **CC BY 4.0**. Described in: Sharmin et al.,
  "A dataset of color fundus images for the detection and classification of eye
  diseases", *Data in Brief* 57 (2024), 110979.
- Ocular Disease Dataset (Kaggle, Manan_1717): MIT; it merges ODIR-2019 and other
  public datasets, so check the original licences before any commercial use.
- ODIR-2019 Grand Challenge: https://odir2019.grand-challenge.org/ (please cite it
  in research use).
