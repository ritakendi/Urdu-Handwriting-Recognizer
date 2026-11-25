"""Train and evaluate a small Keras CNN for isolated Urdu characters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix


def build_model(num_classes: int, image_size: int = 28) -> tf.keras.Model:
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomRotation(0.04),
            tf.keras.layers.RandomTranslation(0.08, 0.08),
            tf.keras.layers.RandomZoom(0.08),
        ],
        name="augmentation",
    )
    inputs = tf.keras.Input(shape=(image_size, image_size, 1))
    x = tf.keras.layers.Rescaling(1.0 / 255)(inputs)
    x = augmentation(x)
    x = tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def plot_history(history: tf.keras.callbacks.History, output_dir: Path) -> None:
    epochs = range(1, len(history.history["accuracy"]) + 1)
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(epochs, history.history["accuracy"], label="training")
    axes[0].plot(epochs, history.history["val_accuracy"], label="validation")
    axes[0].set(title="Accuracy", xlabel="Epoch", ylabel="Accuracy")
    axes[0].legend()
    axes[1].plot(epochs, history.history["loss"], label="training")
    axes[1].plot(epochs, history.history["val_loss"], label="validation")
    axes[1].set(title="Loss", xlabel="Epoch", ylabel="Loss")
    axes[1].legend()
    figure.tight_layout()
    figure.savefig(output_dir / "training_curves.png", dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-dir", type=Path, required=True)
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/character_cnn"))
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--image-size", type=int, default=28)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        args.train_dir,
        labels="inferred",
        label_mode="int",
        color_mode="grayscale",
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
        validation_split=0.15,
        subset="training",
        seed=42,
        shuffle=True,
    )
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        args.train_dir,
        labels="inferred",
        label_mode="int",
        color_mode="grayscale",
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
        validation_split=0.15,
        subset="validation",
        seed=42,
        shuffle=True,
    )
    class_names = train_ds.class_names
    if len(class_names) < 2:
        raise ValueError("Training needs at least two class folders")

    test_ds = tf.keras.utils.image_dataset_from_directory(
        args.test_dir,
        labels="inferred",
        label_mode="int",
        class_names=class_names,
        color_mode="grayscale",
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
        shuffle=False,
    )
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    validation_ds = validation_ds.prefetch(autotune)
    test_ds = test_ds.prefetch(autotune)

    model = build_model(len(class_names), image_size=args.image_size)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(args.output_dir / "best_model.keras", save_best_only=True),
    ]
    history = model.fit(
        train_ds,
        validation_data=validation_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )
    plot_history(history, args.output_dir)

    probabilities = model.predict(test_ds)
    y_pred = np.argmax(probabilities, axis=1)
    y_true = np.concatenate([labels.numpy() for _, labels in test_ds])
    test_loss, test_accuracy = model.evaluate(test_ds, verbose=0)
    matrix = confusion_matrix(y_true, y_pred, labels=range(len(class_names)))
    display = ConfusionMatrixDisplay(matrix, display_labels=class_names)
    figure, axis = plt.subplots(figsize=(max(8, len(class_names) * 0.35), max(7, len(class_names) * 0.35)))
    display.plot(ax=axis, xticks_rotation="vertical", colorbar=False, values_format="d")
    figure.tight_layout()
    figure.savefig(args.output_dir / "confusion_matrix.png", dpi=180)
    plt.close(figure)

    model.save(args.output_dir / "character_cnn.keras")
    (args.output_dir / "class_names.json").write_text(json.dumps(class_names, ensure_ascii=False, indent=2) + "\n")
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    (args.output_dir / "metrics.json").write_text(
        json.dumps({"test_loss": float(test_loss), "test_accuracy": float(test_accuracy), "classification_report": report}, indent=2)
        + "\n"
    )
    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Artifacts written to {args.output_dir}")


if __name__ == "__main__":
    main()
