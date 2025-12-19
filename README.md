# Conformalized Explainable Malaria Detection

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## Overview

A dual-approach AI system for malaria diagnosis implementing two independent pipelines:

1. **Pipeline 1 (Binary Classification)**: Individual cell classification with conformal prediction and Grad-CAM explainability
2. **Pipeline 2 (Object Detection)**: Multi-class detection in clinical blood smears using YOLOv8

For this version, those pipelines are standalone as a proof of concept objective. In the near future, a new version will come out where we have a single, unified pipeline that handles all scenarios studied here.

---

## Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/beylouni/conformalized-xplainable-malaria.git
cd conformalized-xplainable-malaria

poetry install
poetry shell
```

### 2. Pipeline 1: Binary Classification (Mateus)

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

### 3. Pipeline 2: Clinical Smear Detection (Luciano)

**Task**: Detect multiple cells (7 classes) in complete blood smear images

#### 3.1. Download and Prepare Data

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

#### 3.2. Train Models

```bash
# YOLOv8
jupyter notebook notebooks/yolo-v8-multiclass-model.ipynb
# Run all cells
# Model saved to: models/YOLOv8_best.pt
# Results in: runs_yolo/detect/train2/
# Runtime: ~4-6 hours (200 epochs)

# Detectron2 (optional)
jupyter notebook notebooks/detectron2-multiclass-model.ipynb
# Model saved to: models/DETECTRON2_final_part_*
```

### 4. Demo App (Optional)

```bash
streamlit run app_demo.py
# Open: http://localhost:8501
```

---

## Project Structure

```
├── notebooks/
│   ├── benchmark.ipynb                      # Pipeline 1: Classification + Conformal Prediction
│   ├── yolo-v8-multiclass-model.ipynb       # Pipeline 2: YOLOv8 detection
│   └── detectron2-multiclass-model.ipynb    # Pipeline 2: Detectron2 (optional)
│
├── utils/
│   ├── coco2yolo.ipynb        # Convert annotations to COCO format
│   └── split-folders.ipynb    # Convert COCO to YOLO format
│
├── data/
│   ├── raw/                   # Original BBBC041 dataset (Pipeline 2)
│   └── processed/             # Converted annotations
│
├── models/                    # Trained models (.keras, .pt files)
├── runs_yolo/                 # YOLOv8 training outputs
├── output_detectron2/         # Detectron2 training outputs
├── references/                # EDA and examples
└── app_demo.py               # Streamlit demo
```

---

## Technical Details

### Pipeline 1: Binary Classification
- **Dataset**: NIH (27,558 segmented cells, automatically downloaded)
- **Models**: SimpleCNN, MobileNetV2, ResNet50V2
- **Techniques**: 
  - Conformal Prediction (Crepes library) for uncertainty quantification
  - Grad-CAM for visual explainability
  - 95% coverage guarantee

### Pipeline 2: Object Detection
- **Dataset**: BBBC041 (1,364 clinical blood smears, manual download)
- **Classes**: 7 categories (red blood cell, trophozoite, ring, schizont, gametocyte, leukocyte, difficult)
- **Models**: YOLOv8 Small (~11M parameters), Detectron2

### Key Dependencies

| Library | Pipeline 1 | Pipeline 2 | Purpose |
|---------|------------|------------|---------|
| tensorflow | ✅ | ❌ | Train CNNs |
| torch | ❌ | ✅ | YOLOv8/Detectron2 |
| crepes | ✅ | ❌ | Conformal Prediction |
| tf-keras-vis | ✅ | ❌ | Grad-CAM |
| ultralytics | ❌ | ✅ | YOLOv8 |

---

## Citation

**NIH Dataset** (Pipeline 1):
```
Rajaraman S, Antani SK, Poostchi M, et al. PeerJ. 2018;6:e4568.
```

**BBBC041 Dataset** (Pipeline 2):
```
Ljosa V, Sokolnicki KL, Carpenter AE. Nature Methods. 2012;9(7):637.
```

---

## Authors

- **Mateus Balda** - [mateusbalda89@gmail.com](mailto:mateusbalda89@gmail.com)
- **Luciano L. B. Farias** - [beylouniluciano@gmail.com](mailto:beylouniluciano@gmail.com)

---

## License

See [LICENSE](LICENSE) file for details.
