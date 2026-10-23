# Normal vs. Diabetic Retinopathy: a binary classification assignment

BME 502: Fundamentals of AI Medical Apps (Fall 2026 B)

A dataset of colour fundus photographs for practising binary image classification:
**normal** (label `normal`) vs. **diabetic retinopathy** (label `dr`). Images are
merged from two public sources, de-duplicated, cropped to the fundus and resized to
256×256 (the original-resolution images are also available). They are split into
train / validation / test (all labelled) and a hidden set whose images are released
but whose labels are withheld.

## Download

The images are too large for GitHub and are hosted on Google Drive.

| File | Size | Contents | Link |
|---|---|---|---|
| `train_val_test.zip` | 117 MB | 5,012 train + 715 val + 705 test images, with `train.csv`, `val.csv`, `test.csv` (labels included) | [Google Drive](https://drive.google.com/file/d/1hgfg4Skm6gQVdOQtrjjRLXKvXWXY7PKZ/view?usp=sharing) |
| `hidden_images.zip` | 13 MB | 715 hidden images, `hidden_images.csv` (**no labels**) | [Google Drive](https://drive.google.com/file/d/11sDqpSBURHdlZy_a0M8QRbfHhLSPie1O/view?usp=sharing) |

**Access:** please open the links with your ASU account. They are not available to other accounts.

### Raw images (optional)

If you would rather choose the resolution, cropping and padding yourself, the
original-resolution images are also available. They use the same file names, splits
and CSVs as the 256×256 version.

| File | Size | Contents | Link |
|---|---|---|---|
| `raw_train_val_test.zip` | 1.6 GB | Same images as `train_val_test.zip`, at original resolution | [Google Drive](https://drive.google.com/file/d/1DOPxUj6Xb4EX5zu9BdFyfXx4mayS8Rki/view?usp=sharing) |
| `raw_hidden_images.zip` | 170 MB | Same images as `hidden_images.zip`, at original resolution | [Google Drive](https://drive.google.com/file/d/1xv7SLA83gFvqzDdrxIMGJrP1PpK6YCOz/view?usp=sharing) |

The raw images vary in size (Mendeley: 2004×1690; ODIR: many sizes, often wide with
black borders), so you must unify them yourself before training. Image size and
aspect ratio also reveal the source dataset, so think about how your preprocessing
interacts with that. The assignment can be done entirely with the 256×256 version.

## Dataset

| Split | Normal | DR | Total |
|---|---|---|---|
| train | 2,826 | 2,186 | 5,012 |
| val | 404 | 311 | 715 |
| test (labelled) | 394 | 311 | 705 |
| hidden (images only, labels withheld) | 397 | 318 | 715 |
| **all** | **4,021** | **3,126** | **7,147** |

Image format: RGB JPEG, 256×256. Each image was cropped to the fundus (black borders
removed), padded with black to a square (never stretched) and resized. File names
are neutral (`img_00000.jpg`) and carry no label or source information.

### CSV files

Every CSV has one row per image with these columns:

| Column | Meaning |
|---|---|
| `image` | file name |
| `label` | `normal` or `dr` (train, val and test CSVs only; encode as you like, e.g. `normal` = 0, `dr` = 1) |
| `source` | `odir` or `mendeley` |
| `patient_group` | anonymised patient; both eyes of a patient share it (ODIR only) |
| `eye` | `left` or `right` (ODIR only) |
| `age`, `sex` | patient age and sex (ODIR only) |

The last four columns are empty for Mendeley images, which come with no patient
information.

### Sources

| Source | Normal | DR | Notes |
|---|---|---|---|
| ODIR-5K (ODIR-2019 Grand Challenge) | 2,997 | 1,619 | Many image sizes, often wide with black borders. Left/right eye of the same patient share an ID. Age and sex come from the original ODIR annotations. |
| Mendeley *Eye Disease Image Dataset* (Rashid et al., 2024) | 1,024 | 1,507 | Images from two eye hospitals in Bangladesh; 2004×1690 px, top and bottom of the circle are cut off. |

Cleaning: exact duplicate images were removed, and images that appear in both
source collections were kept only once.

### How the split was made

- 70 / 10 / 10 / 10 split into train / val / test / hidden, stratified by (source × class).
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
- **Mendeley scores may look better than they should.** Some patients may have been
  photographed several times, and because Mendeley images are split image by image,
  photos of the same eye can end up in both train and test. Results on Mendeley
  images are therefore likely higher than on ODIR images. Compare the two (use the
  `source` column) and think about:
  - Why could a model score higher on an eye it has effectively already seen?
  - How could you check this yourself, for example by looking at the training images
    most similar to a validation image?
  - Which result would you trust more for a new patient, and what would you do
    differently if you had patient IDs?
- **Does your model work equally well for everyone?** For ODIR images you also have
  `age` and `sex`. Compare your results across sexes and across age groups (for
  example under 50, 50 to 65, over 65). Some groups contain few images, so decide for
  yourself how to define the groups and which images to pool to get reliable numbers.
  Are the differences larger than you would expect from random variation? If a group
  does worse, what could explain it, and why does it matter for a model that might be
  used in a clinic?
- Classes are mildly imbalanced (56% normal); consider F1 and AUC, not just accuracy.
- The labels come from the source datasets and were not re-checked by us.

### Cross-dataset analysis (extension)

The two sources differ in camera, resolution, framing and class balance, so a model
that works on one may not work on the other. With the `source` column you can, for
example:

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
   to recover them.

**How to submit:** TBD

**Evaluation:** TBD

## Repository layout

```
scripts/score_submission.py   scores a submission against the hidden labels (used by the instructor)
scripts/requirements.txt
```

## Attribution and licences

- Mendeley Eye Disease Image Dataset: Rashid, Sharmin, Khatun, Hasan, Uddin (2024),
  DOI 10.17632/s9bfhswzjb.1, licence **CC BY 4.0**. Described in: Sharmin et al.,
  "A dataset of color fundus images for the detection and classification of eye
  diseases", *Data in Brief* 57 (2024), 110979.
- ODIR-2019 Grand Challenge (ODIR-5K): https://odir2019.grand-challenge.org/ (please
  cite it in research use). Image selection and class labels follow the Kaggle
  *Ocular Disease Dataset* (Manan_1717, MIT), which merges several public datasets,
  so check the original licences before any commercial use.
