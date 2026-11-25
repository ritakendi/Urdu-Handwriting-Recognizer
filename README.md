# Urdu Handwriting Recognizer

A mobile-first project for turning handwritten Urdu into editable digital Urdu text. The intended app lets a user draw a character or word on a canvas, review the three best suggestions, and copy, save, or share the result. A practice mode will help learners recognize Urdu letters.

## What we are building

Urdu is written from right to left. Many letters join, and their shapes can change depending on their position in a word. Small dots distinguish several otherwise similar letters. That makes whole-word recognition a different task from classifying a picture of one isolated character.

We are developing the model in two levels:

1. **Character recognition:** train and evaluate a CNN on labeled isolated characters. This powers the letter practice feature and establishes the image preprocessing and app inference path.
2. **Word recognition:** support writing full words as required by the project description. This needs word/line examples and sequence recognition or another word-level approach; the isolated-character model alone cannot do this.

The target app features are a drawing canvas with undo and clear, three ranked suggestions, editable recognized text, copy/save/share, and letter practice. We will state clearly which input types the delivered model supports.

## Languages and tools

| Part | Language / tool | What it does |
|---|---|---|
| Model training | Python 3.11, TensorFlow/Keras | Builds and trains the character-recognition CNN |
| Image preparation | OpenCV (`cv2`) | Cleans, centers, thresholds, and resizes handwriting images |
| Model evaluation | scikit-learn, Matplotlib | Produces evaluation metrics, the confusion matrix, and training graphs |
| Mobile app | Kotlin, Android Studio, Gradle | Builds the Android app and its native phone features |
| Drawing interface | Android Canvas (custom view) | Captures finger-written characters or words and supports undo/clear |
| On-device recognition | TensorFlow Lite (planned) | Runs the trained model in the Android app without sending handwriting to a server |
| Version control | Git and GitHub | Tracks and shares the source code; datasets and trained model files stay out of Git |
| Character data | UHaT via Zenodo (selected, not downloaded yet) | Provides labeled isolated-character examples for the first model |

Python model preparation/training is in place. A minimal Kotlin Android launch screen now builds; the drawing canvas and TensorFlow Lite integration remain to be implemented. The word-level dataset and model approach also remain to be selected.

## Current implementation

- `src/urdu_recognizer/preprocess.py` — OpenCV preprocessing for grayscale, thresholding, centering, and resizing.
- `src/urdu_recognizer/train.py` — Keras CNN training and evaluation with accuracy/loss plots and a confusion matrix.
- `android/app/src/main/java/com/example/urduhandwritingrecognizer/MainActivity.kt` — minimal Android welcome screen and app entry point.
- The dataset and model are not included in Git.

## Dataset

The selected starting candidate is [UHaT on Zenodo](https://zenodo.org/records/3670611), a 28×28 isolated Urdu character and digit dataset. Its record describes separate train/test folders and samples from 900+ writers. The accompanying [paper](https://doi.org/10.1007/s42452-019-1914-1) states that the dataset is for non-commercial research use. Cite the paper in project reports and do not redistribute the data. The record does not show a specific license.

Download and extract the archive locally under `data/raw/`. Expected relevant folders are:

```text
data/raw/Data/characters train set/<class-name>/*
data/raw/Data/characters test set/<class-name>/*
```

The folder names are used as class labels until they are checked and mapped to the corresponding Urdu characters. Digit folders are not used for the character model. Word-level data still needs to be selected before implementing word recognition.

## Setup

Use Python 3.11 in a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Prepare the images

After extracting UHaT, run:

```bash
PYTHONPATH=src python -m urdu_recognizer.preprocess \
  --input "data/raw/Data/characters train set" \
  --output data/processed/train

PYTHONPATH=src python -m urdu_recognizer.preprocess \
  --input "data/raw/Data/characters test set" \
  --output data/processed/test
```

The preprocessing script preserves the class-folder layout and writes standardized 28×28 grayscale PNGs. The test folders remain separate for final evaluation.

## Train and evaluate

From the repository root:

```bash
PYTHONPATH=src python -m urdu_recognizer.train \
  --train-dir data/processed/train \
  --test-dir data/processed/test \
  --output-dir artifacts/character_cnn
```

The run saves the Keras model, class names, held-out predictions, an accuracy/loss graph, and a confusion matrix in the output directory. The training script keeps a validation split inside the training folders and uses the separate test folders only for final evaluation.

## Project status

The repository contains the character-model training pipeline and a minimal Android screen. The drawing canvas, model integration, and word-level recognition are next implementation areas. Do not interpret a character-only accuracy score as word recognition accuracy.
