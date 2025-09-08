# Fingerprint Pattern Classification using Transfer Learning
# Complete Google Colab Implementation

# =============================================================================
# PHASE 1: FOUNDATION & SETUP
# =============================================================================

# Check if we're running in Colab and mount Google Drive
import os
try:
    from google.colab import drive
    IN_COLAB = True
    print("Running in Google Colab")
except ImportError:
    IN_COLAB = False
    print("Not running in Google Colab")

if IN_COLAB:
    drive.mount('/content/drive')
    # Create project directory in Google Drive
    project_path = '/content/drive/MyDrive/fingerprint-classification'
    os.makedirs(project_path, exist_ok=True)
    os.makedirs(f'{project_path}/data/raw', exist_ok=True)
    os.makedirs(f'{project_path}/data/processed', exist_ok=True)
    os.makedirs(f'{project_path}/models', exist_ok=True)
    os.chdir(project_path)
    print(f"Project directory created at: {project_path}")

# Install required packages
!pip install -q tensorflow opencv-python matplotlib seaborn scikit-learn pillow

# Import libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
from PIL import Image
import os
import shutil
import requests
import zipfile
from pathlib import Path
import pandas as pd

# Check GPU availability
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("TensorFlow version:", tf.__version__)

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

# =============================================================================
# PHASE 2: DATA ACQUISITION & PREPROCESSING
# =============================================================================

class FingerprintDataProcessor:
    def __init__(self, raw_data_path, processed_data_path, target_size=(224, 224)):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.target_size = target_size
        self.classes = ['arch', 'loop', 'whorl']
        
    def download_sample_data(self):
        """
        Download and setup sample fingerprint dataset
        Note: Replace this with actual dataset download in real implementation
        """
        print("Setting up sample data structure...")
        for class_name in self.classes:
            os.makedirs(f'{self.raw_data_path}/{class_name}', exist_ok=True)
            os.makedirs(f'{self.processed_data_path}/{class_name}', exist_ok=True)
        
        print("Sample data structure created. Please upload your fingerprint images to:")
        for class_name in self.classes:
            print(f"  - {self.raw_data_path}/{class_name}/")
    
    def preprocess_image(self, image_path, output_path):
        """
        Preprocess a single fingerprint image for transfer learning
        """
        try:
            # Read image in grayscale
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return False
            
            # Resize to target size
            img_resized = cv2.resize(img, self.target_size)
            
            # Convert grayscale to RGB (duplicate channels for pre-trained models)
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)
            
            # Normalize pixel values to [0, 1]
            img_normalized = img_rgb.astype(np.float32) / 255.0
            
            # Convert back to 0-255 range for saving
            img_final = (img_normalized * 255).astype(np.uint8)
            
            # Save preprocessed image
            cv2.imwrite(output_path, img_final)
            return True
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return False
    
    def preprocess_all_images(self):
        """
        Preprocess all images in the raw data directory
        """
        total_processed = 0
        class_counts = {}
        
        for class_name in self.classes:
            input_dir = f'{self.raw_data_path}/{class_name}'
            output_dir = f'{self.processed_data_path}/{class_name}'
            
            if not os.path.exists(input_dir):
                print(f"Warning: {input_dir} does not exist")
                continue
            
            image_files = [f for f in os.listdir(input_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            
            processed_count = 0
            for img_file in image_files:
                input_path = os.path.join(input_dir, img_file)
                output_path = os.path.join(output_dir, img_file)
                
                if self.preprocess_image(input_path, output_path):
                    processed_count += 1
            
            class_counts[class_name] = processed_count
            total_processed += processed_count
            print(f"Processed {processed_count} images for class '{class_name}'")
        
        print(f"\nTotal images processed: {total_processed}")
        return class_counts
    
    def visualize_data_distribution(self, class_counts):
        """
        Visualize the distribution of classes
        """
        plt.figure(figsize=(10, 6))
        classes = list(class_counts.keys())
        counts = list(class_counts.values())
        
        plt.bar(classes, counts)
        plt.title('Distribution of Fingerprint Classes')
        plt.xlabel('Fingerprint Pattern')
        plt.ylabel('Number of Images')
        plt.xticks(rotation=45)
        
        for i, count in enumerate(counts):
            plt.text(i, count + max(counts) * 0.01, str(count), 
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        # Check for class imbalance
        if len(set(counts)) > 1:
            max_count = max(counts)
            min_count = min(counts)
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            
            if imbalance_ratio > 2:
                print(f"Warning: Class imbalance detected (ratio: {imbalance_ratio:.2f})")
                print("Consider using class weights or data augmentation")

    def display_sample_images(self):
        """
        Display sample images from each class
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, class_name in enumerate(self.classes):
            class_dir = f'{self.processed_data_path}/{class_name}'
            if os.path.exists(class_dir):
                image_files = [f for f in os.listdir(class_dir) 
                              if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                if image_files:
                    # Display first image
                    img_path = os.path.join(class_dir, image_files[0])
                    img = cv2.imread(img_path)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    axes[i].imshow(img)
                    axes[i].set_title(f'{class_name.title()} - Sample 1')
                    axes[i].axis('off')
                    
                    # Display second image if available
                    if len(image_files) > 1:
                        img_path = os.path.join(class_dir, image_files[1])
                        img = cv2.imread(img_path)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        axes[i+3].imshow(img)
                        axes[i+3].set_title(f'{class_name.title()} - Sample 2')
                        axes[i+3].axis('off')
        
        plt.tight_layout()
        plt.show()

# Initialize data processor
processor = FingerprintDataProcessor('data/raw', 'data/processed')

# Setup sample data structure (you'll need to upload actual data)
processor.download_sample_data()

# =============================================================================
# DEMO DATA GENERATION (Remove this section when using real data)
# =============================================================================

def create_demo_fingerprint_images():
    """
    Create synthetic fingerprint-like images for demonstration
    Remove this function when using real fingerprint data
    """
    print("Creating demo fingerprint images...")
    
    for class_name in processor.classes:
        class_dir = f'data/raw/{class_name}'
        
        for i in range(20):  # Create 20 demo images per class
            # Create a synthetic fingerprint-like pattern
            img = np.random.randint(50, 200, (200, 200), dtype=np.uint8)
            
            # Add some pattern-specific characteristics
            if class_name == 'arch':
                # Arch-like pattern
                for y in range(200):
                    for x in range(200):
                        if abs(x - 100) < 50 and y > 100 + abs(x - 100) * 0.5:
                            img[y, x] = min(255, img[y, x] + 50)
            elif class_name == 'loop':
                # Loop-like pattern
                center_x, center_y = 100, 100
                for y in range(200):
                    for x in range(200):
                        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                        if 40 < dist < 80:
                            img[y, x] = min(255, img[y, x] + 60)
            else:  # whorl
                # Whorl-like pattern
                center_x, center_y = 100, 100
                for y in range(200):
                    for x in range(200):
                        angle = np.arctan2(y - center_y, x - center_x)
                        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                        if dist < 80 and int(angle * 5) % 2 == 0:
                            img[y, x] = min(255, img[y, x] + 70)
            
            # Save demo image
            filename = f'{class_dir}/demo_{class_name}_{i:03d}.png'
            cv2.imwrite(filename, img)
    
    print("Demo images created!")

# Create demo data (remove this when using real data)
create_demo_fingerprint_images()

# Process all images
print("Processing images...")
class_counts = processor.preprocess_all_images()

# Visualize data distribution
processor.visualize_data_distribution(class_counts)

# Display sample images
processor.display_sample_images()

# =============================================================================
# PHASE 3: MODEL DEVELOPMENT & TRAINING
# =============================================================================

class FingerprintClassifier:
    def __init__(self, input_shape=(224, 224, 3), num_classes=3):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def build_transfer_learning_model(self, base_model_name='ResNet50'):
        """
        Build transfer learning model with pre-trained base
        """
        print(f"Building transfer learning model with {base_model_name}...")
        
        # Load pre-trained base model
        if base_model_name == 'ResNet50':
            base_model = ResNet50(weights='imagenet', 
                                include_top=False, 
                                input_shape=self.input_shape)
        else:
            raise ValueError(f"Base model {base_model_name} not supported")
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build the complete model
        self.model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile the model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("Model built successfully!")
        print(f"Total parameters: {self.model.count_params():,}")
        print(f"Trainable parameters: {sum([tf.size(w).numpy() for w in self.model.trainable_weights]):,}")
        
        return self.model
    
    def setup_data_generators(self, data_dir, validation_split=0.2, batch_size=32):
        """
        Setup data generators with augmentation
        """
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            validation_split=validation_split
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # Create generators
        self.train_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        self.val_generator = val_datagen.flow_from_directory(
            data_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        print(f"Training samples: {self.train_generator.samples}")
        print(f"Validation samples: {self.val_generator.samples}")
        print(f"Classes: {list(self.train_generator.class_indices.keys())}")
        
        return self.train_generator, self.val_generator
    
    def train_stage1(self, epochs=15):
        """
        Stage 1: Train only the classification head
        """
        print("Starting Stage 1 training (frozen base model)...")
        
        callbacks = [
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=3),
            keras.callbacks.ModelCheckpoint('models/fingerprint_stage1.h5', 
                                          save_best_only=True)
        ]
        
        self.history = self.model.fit(
            self.train_generator,
            epochs=epochs,
            validation_data=self.val_generator,
            callbacks=callbacks
        )
        
        print("Stage 1 training completed!")
        return self.history
    
    def fine_tune_stage2(self, epochs=10, fine_tune_layers=50):
        """
        Stage 2: Fine-tune top layers of base model
        """
        print(f"Starting Stage 2 fine-tuning (last {fine_tune_layers} layers)...")
        
        # Unfreeze the base model
        self.model.layers[0].trainable = True
        
        # Freeze all layers except the last few
        for layer in self.model.layers[0].layers[:-fine_tune_layers]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=Adam(learning_rate=0.00001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        callbacks = [
            keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            keras.callbacks.ModelCheckpoint('models/fingerprint_final.h5', 
                                          save_best_only=True)
        ]
        
        # Continue training
        history2 = self.model.fit(
            self.train_generator,
            epochs=epochs,
            validation_data=self.val_generator,
            callbacks=callbacks
        )
        
        # Combine histories
        if self.history:
            for key in self.history.history:
                self.history.history[key].extend(history2.history[key])
        
        print("Stage 2 fine-tuning completed!")
        return history2

# Initialize classifier
classifier = FingerprintClassifier()

# Build model
model = classifier.build_transfer_learning_model('ResNet50')
model.summary()

# Setup data generators
train_gen, val_gen = classifier.setup_data_generators('data/processed')

# Train Stage 1
print("\n" + "="*50)
print("TRAINING STAGE 1")
print("="*50)
history1 = classifier.train_stage1(epochs=15)

# Train Stage 2 (Fine-tuning)
print("\n" + "="*50)
print("TRAINING STAGE 2 - FINE TUNING")
print("="*50)
history2 = classifier.fine_tune_stage2(epochs=10)

# =============================================================================
# PHASE 4: EVALUATION & VISUALIZATION
# =============================================================================

class ModelEvaluator:
    def __init__(self, model, val_generator, class_names):
        self.model = model
        self.val_generator = val_generator
        self.class_names = class_names
    
    def plot_training_history(self, history):
        """
        Plot training and validation accuracy/loss
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot accuracy
        ax1.plot(history.history['accuracy'], label='Training Accuracy')
        ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
        ax1.set_title('Model Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        ax1.grid(True)
        
        # Plot loss
        ax2.plot(history.history['loss'], label='Training Loss')
        ax2.plot(history.history['val_loss'], label='Validation Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def evaluate_model(self):
        """
        Comprehensive model evaluation
        """
        print("Evaluating model on validation set...")
        
        # Get predictions
        self.val_generator.reset()
        predictions = self.model.predict(self.val_generator)
        y_pred = np.argmax(predictions, axis=1)
        y_true = self.val_generator.classes
        
        # Calculate accuracy
        accuracy = np.mean(y_pred == y_true)
        print(f"Validation Accuracy: {accuracy:.4f}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred, target_names=self.class_names))
        
        # Confusion matrix
        self.plot_confusion_matrix(y_true, y_pred)
        
        return accuracy, y_true, y_pred, predictions
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """
        Plot confusion matrix
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.show()
        
        # Calculate per-class accuracy
        for i, class_name in enumerate(self.class_names):
            class_acc = cm[i, i] / cm[i, :].sum() if cm[i, :].sum() > 0 else 0
            print(f"{class_name} accuracy: {class_acc:.3f}")
    
    def show_prediction_samples(self, num_samples=9):
        """
        Show sample predictions with confidence scores
        """
        self.val_generator.reset()
        
        # Get a batch of images and predictions
        batch_images, batch_labels = next(self.val_generator)
        predictions = self.model.predict(batch_images)
        
        # Select random samples
        indices = np.random.choice(len(batch_images), 
                                 min(num_samples, len(batch_images)), 
                                 replace=False)
        
        fig, axes = plt.subplots(3, 3, figsize=(15, 15))
        axes = axes.flatten()
        
        for i, idx in enumerate(indices):
            if i >= len(axes):
                break
                
            # Get image and predictions
            img = batch_images[idx]
            true_label = np.argmax(batch_labels[idx])
            pred_probs = predictions[idx]
            pred_label = np.argmax(pred_probs)
            confidence = pred_probs[pred_label]
            
            # Display image
            axes[i].imshow(img)
            axes[i].axis('off')
            
            # Create title with prediction info
            true_class = self.class_names[true_label]
            pred_class = self.class_names[pred_label]
            color = 'green' if pred_label == true_label else 'red'
            
            title = f"True: {true_class}\nPred: {pred_class}\nConf: {confidence:.3f}"
            axes[i].set_title(title, color=color, fontsize=10)
        
        plt.tight_layout()
        plt.show()

# Initialize evaluator
class_names = list(train_gen.class_indices.keys())
evaluator = ModelEvaluator(model, val_gen, class_names)

# Plot training history
evaluator.plot_training_history(classifier.history)

# Evaluate model
accuracy, y_true, y_pred, predictions = evaluator.evaluate_model()

# Show prediction samples
evaluator.show_prediction_samples()

# =============================================================================
# PHASE 5: MODEL SAVING & DEPLOYMENT PREPARATION
# =============================================================================

# Save the final model
model.save('models/fingerprint_classifier_final.h5')
print("Model saved successfully!")

# Save model in TensorFlow Lite format for mobile deployment
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('models/fingerprint_classifier.tflite', 'wb') as f:
    f.write(tflite_model)
print("TensorFlow Lite model saved!")

# Create a prediction function for deployment
def predict_fingerprint_pattern(image_path, model_path='models/fingerprint_classifier_final.h5'):
    """
    Predict fingerprint pattern from image path
    """
    # Load model
    model = keras.models.load_model(model_path)
    
    # Load and preprocess image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, "Could not load image"
    
    # Preprocess
    img_resized = cv2.resize(img, (224, 224))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)
    img_normalized = img_rgb.astype(np.float32) / 255.0
    img_batch = np.expand_dims(img_normalized, axis=0)
    
    # Predict
    predictions = model.predict(img_batch)
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class]
    
    class_names = ['arch', 'loop', 'whorl']
    predicted_pattern = class_names[predicted_class]
    
    return predicted_pattern, confidence

# Test the prediction function
print("\nTesting prediction function...")
# You can test with any image in your processed data
sample_image_path = None
for class_name in ['arch', 'loop', 'whorl']:
    class_dir = f'data/processed/{class_name}'
    if os.path.exists(class_dir):
        images = os.listdir(class_dir)
        if images:
            sample_image_path = os.path.join(class_dir, images[0])
            break

if sample_image_path:
    pattern, confidence = predict_fingerprint_pattern(sample_image_path)
    print(f"Sample prediction: {pattern} (confidence: {confidence:.3f})")
else:
    print("No sample images found for testing")

# Print final summary
print("\n" + "="*60)
print("FINGERPRINT CLASSIFICATION PROJECT COMPLETED!")
print("="*60)
print(f"Final validation accuracy: {accuracy:.4f}")
print(f"Model saved at: models/fingerprint_classifier_final.h5")
print(f"TensorFlow Lite model saved at: models/fingerprint_classifier.tflite")
print("\nModel is ready for deployment!")
print("="*60)