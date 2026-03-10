# Conformalized Explainable Malaria Detection

## Overview
A hierarchical approach for malaria diagnosis that implements two independent stages:

1. **Stage 1 (Object Detection)**: Multi-class detection in clinical blood smears using YOLOv8
2. **Stage 2 (Binary Classification)**: Individual cell classification with conformal prediction and Grad-CAM explainability

## Methodological design
<p align="center">
  <img src="https://github.com/user-attachments/assets/9e295620-9828-4aa2-bfd8-765bc38fa923" width="700">
</p>

---

## Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone "this SSH repo link"
cd conformalized-xplainable-malaria

poetry install
poetry shell
```

### 2. Stage 1: Clinical Smear Detection

**Task**: Detect multiple cells (7 classes) in complete blood smear images

#### 2.1. Download and Prepare Data

```bash
# Download BBBC041 dataset
cd data/raw/
wget https://data.broadinstitute.org/bbbc/BBBC041/malaria.zip
unzip malaria.zip
# Extract: images/ training.json test.json
cd ../..

# Convert annotations
jupyter notebook utils/coco2yolo.ipynb  # Run all cells
jupyter notebook utils/split-folders.ipynb  # Run all cells
```

**Expected structure after preparation:**
```
data/
├── raw/
│   ├── images/          # 1,364 images
│   ├── training.json
│   └── test.json
└── processed/
    ├── training_coco.json
    ├── test_coco.json
    └── dataset/labels/
        ├── train/       # 1,208 .txt files
        └── test/        # 120 .txt files
```

#### 2.2. Train Models

```bash
# YOLOv8
jupyter notebook notebooks/yolo-v8-multiclass-model.ipynb
# Run all cells
# Model saved to: models/YOLOv8_best.pt
# Results in: runs_yolo/detect/train2/
# Runtime: ~4-6 hours (200 epochs)
```

### 3. Stage 2: Binary Classification

**Task**: Classify individual cells (Infected/Non-Infected) with uncertainty quantification

```bash
# Open notebook
jupyter notebook notebooks/benchmark.ipynb

# Run all cells - the notebook automatically:
# - Downloads NIH dataset via TensorFlow Datasets (27,558 images)
# - Trains SimpleCNN, MobileNetV2, ResNet50V2
# - Applies Conformal Prediction
# - Generates Grad-CAM visualizations

# Models saved to: models/*.keras
# Runtime: ~2-3 hours (GPU)
```

**No manual data download needed** - TensorFlow Datasets handles it automatically!

---

## Project Structure

```
├── notebooks/
│   ├── benchmark.ipynb                      # Stage 2: Classification + Conformal Prediction
│   └── yolo-v8-multiclass-model.ipynb       # Stage 1: YOLOv8 detection
│
├── utils/
│   ├── coco2yolo.ipynb        # Convert annotations to COCO format
│   └── split-folders.ipynb    # Convert COCO to YOLO format
│
├── data/
│   ├── raw/                   # Original BBBC041 dataset (Stage 1)
│   └── processed/             # Converted annotations
│
├── models/                    # Trained models (.keras, .pt files)
├── runs_yolo/                 # YOLOv8 training outputs
├── references/                # EDA and examples
└── app_demo.py               # Streamlit demo
```

---

## Technical Details

### Stage 1: Object Detection
- **Dataset**: BBBC041 (1,364 clinical blood smears, manual download)
- **Classes**: 7 categories (red blood cell, trophozoite, ring, schizont, gametocyte, leukocyte, difficult)
- **Model**: YOLOv8 Small (~11M parameters)

### Stage 2: Binary Classification
- **Dataset**: NIH (27,558 segmented cells, automatically downloaded)
- **Models**: SimpleCNN, MobileNetV2, ResNet50V2
- **Techniques**: 
  - Conformal Prediction (Crepes library) for uncertainty quantification
  - Grad-CAM for visual explainability
  - 95% coverage guarantee

### Key Dependencies

| Library | Stage 2 | Stage 1 | Purpose |
|---------|------------|------------|---------|
| tensorflow | ✅ | ❌ | Train CNNs |
| torch | ❌ | ✅ | YOLOv8 |
| crepes | ✅ | ❌ | Conformal Prediction |
| tf-keras-vis | ✅ | ❌ | Grad-CAM |
| ultralytics | ❌ | ✅ | YOLOv8 |

---

## Citation

**BBBC041 Dataset** (Stage 1):
```
Ljosa V, Sokolnicki KL, Carpenter AE. Nature Methods. 2012;9(7):637.
```

**NIH Dataset** (Stage 2):
```
Rajaraman S, Antani SK, Poostchi M, et al. PeerJ. 2018;6:e4568.
```

---

## License

See [LICENSE](LICENSE) file for details.
