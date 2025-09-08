# Fingerprint Pattern Classification using Transfer Learning
# Complete implementation following the detailed project workflow

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import cv2
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class FingerprintClassifier:
    def __init__(self, data_dir, img_size=(224, 224), batch_size=32):
        self.data_dir = Path(data_dir)
        self.img_size = img_size
        self.batch_size = batch_size
        self.model = None
        self.history = None
        self.classes = ['arch', 'loop', 'whorl']
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create project directory structure"""
        dirs = [
            'data/raw', 'data/processed/arch', 'data/processed/loop', 
            'data/processed/whorl', 'models', 'notebooks', 'src'
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        print("Directory structure created successfully!")
    
    def load_and_preprocess_data(self, raw_data_path):
        """
        Load and preprocess fingerprint images
        Convert grayscale to RGB, resize, and normalize
        """
        processed_dir = Path('data/processed')
        
        for class_name in self.classes:
            class_raw_path = Path(raw_data_path) / class_name
            class_processed_path = processed_dir / class_name
            
            if not class_raw_path.exists():
                print(f"Warning: {class_raw_path} does not exist")
                continue
            
            print(f"Processing {class_name} images...")
            
            for img_file in class_raw_path.glob('*'):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # Read image
                    img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                    
                    if img is not None:
                        # Resize image
                        img = cv2.resize(img, self.img_size)
                        
                        # Convert grayscale to RGB (duplicate channels)
                        img_rgb = cv2.merge([img, img, img])
                        
                        # Normalize to [0, 1]
                        img_rgb = img_rgb.astype(np.float32) / 255.0
                        
                        # Save processed image
                        output_path = class_processed_path / img_file.name
                        # Convert back to 0-255 range for saving
                        cv2.imwrite(str(output_path), (img_rgb * 255).astype(np.uint8))
            
            print(f"Completed processing {class_name}")
    
    def explore_data(self, data_path='data/processed'):
        """Perform Exploratory Data Analysis"""
        data_path = Path(data_path)
        
        # Count images per class
        class_counts = {}
        for class_name in self.classes:
            class_path = data_path / class_name
            if class_path.exists():
                count = len(list(class_path.glob('*')))
                class_counts[class_name] = count
        
        # Visualize class distribution
        plt.figure(figsize=(10, 6))
        plt.bar(class_counts.keys(), class_counts.values())
        plt.title('Distribution of Fingerprint Classes')
        plt.xlabel('Class')
        plt.ylabel('Number of Images')
        plt.xticks(rotation=45)
        
        for i, (class_name, count) in enumerate(class_counts.items()):
            plt.text(i, count + max(class_counts.values()) * 0.01, 
                    str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        # Display sample images
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for i, class_name in enumerate(self.classes):
            class_path = data_path / class_name
            if class_path.exists():
                sample_images = list(class_path.glob('*'))[:1]
                if sample_images:
                    img = cv2.imread(str(sample_images[0]))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    axes[i].imshow(img)
                    axes[i].set_title(f'{class_name.capitalize()} Sample')
                    axes[i].axis('off')
        
        plt.tight_layout()
        plt.show()
        
        return class_counts
    
    def create_data_generators(self, data_path='data/processed', validation_split=0.2):
        """Create data generators with augmentation"""
        
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
        train_generator = train_datagen.flow_from_directory(
            data_path,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        validation_generator = val_datagen.flow_from_directory(
            data_path,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        return train_generator, validation_generator
    
    def build_model(self):
        """Build transfer learning model using ResNet50"""
        
        # Load pre-trained ResNet50 without top layers
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom classification head
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.classes), activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train_model(self, train_gen, val_gen, epochs=20):
        """Train the model with callbacks"""
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=1e-7
            )
        ]
        
        print("Starting initial training (frozen base layers)...")
        
        # Train the model
        self.history = self.model.fit(
            train_gen,
            epochs=epochs,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def fine_tune_model(self, train_gen, val_gen, epochs=10):
        """Fine-tune the model by unfreezing top layers"""
        
        print("\nStarting fine-tuning (unfreezing top layers)...")
        
        # Unfreeze the base model
        self.model.layers[0].trainable = True
        
        # Use a lower learning rate for fine-tuning
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.00001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Callbacks for fine-tuning
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=3,
                restore_best_weights=True
            )
        ]
        
        # Continue training
        fine_tune_history = self.model.fit(
            train_gen,
            epochs=epochs,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )
        
        # Combine histories
        if self.history is not None:
            for key in self.history.history.keys():
                self.history.history[key].extend(fine_tune_history.history[key])
        
        return fine_tune_history
    
    def plot_training_history(self):
        """Plot training and validation metrics"""
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Training Loss')
        axes[1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def evaluate_model(self, test_generator):
        """Evaluate model performance"""
        
        # Get predictions
        test_generator.reset()
        predictions = self.model.predict(test_generator, verbose=1)
        y_pred = np.argmax(predictions, axis=1)
        y_true = test_generator.classes
        
        # Classification report
        class_names = list(test_generator.class_indices.keys())
        print("Classification Report:")
        print(classification_report(y_true, y_pred, target_names=class_names))
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()
        
        # Calculate accuracy
        accuracy = np.sum(y_pred == y_true) / len(y_true)
        print(f"Test Accuracy: {accuracy:.4f}")
        
        return accuracy, cm
    
    def predict_single_image(self, image_path):
        """Predict class for a single image"""
        # Load and preprocess image
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Could not load image: {image_path}")
            return None
        
        # Resize and convert to RGB
        img = cv2.resize(img, self.img_size)
        img_rgb = cv2.merge([img, img, img])
        img_rgb = img_rgb.astype(np.float32) / 255.0
        
        # Add batch dimension
        img_batch = np.expand_dims(img_rgb, axis=0)
        
        # Predict
        prediction = self.model.predict(img_batch)
        predicted_class = self.classes[np.argmax(prediction)]
        confidence = np.max(prediction)
        
        return predicted_class, confidence
    
    def save_model(self, filepath='models/fingerprint_classifier.h5'):
        """Save the trained model"""
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='models/fingerprint_classifier.h5'):
        """Load a saved model"""
        self.model = keras.models.load_model(filepath)
        print(f"Model loaded from {filepath}")

# Example usage and main execution
def main():
    """Main execution function"""
    
    print("=== Fingerprint Pattern Classification Project ===")
    
    # Initialize classifier
    classifier = FingerprintClassifier(data_dir='data')
    
    # Step 1: Data preprocessing (uncomment when you have raw data)
    # classifier.load_and_preprocess_data('data/raw')
    
    # Step 2: Explore data
    print("\n1. Exploring data...")
    # class_counts = classifier.explore_data()
    
    # Step 3: Create data generators
    print("\n2. Creating data generators...")
    try:
        train_gen, val_gen = classifier.create_data_generators()
        print(f"Training samples: {train_gen.samples}")
        print(f"Validation samples: {val_gen.samples}")
        print(f"Class indices: {train_gen.class_indices}")
    except FileNotFoundError:
        print("Processed data not found. Please ensure data is preprocessed first.")
        return
    
    # Step 4: Build model
    print("\n3. Building model...")
    model = classifier.build_model()
    print(model.summary())
    
    # Step 5: Train model
    print("\n4. Training model...")
    history = classifier.train_model(train_gen, val_gen, epochs=20)
    
    # Step 6: Fine-tune model
    print("\n5. Fine-tuning model...")
    classifier.fine_tune_model(train_gen, val_gen, epochs=10)
    
    # Step 7: Plot training history
    print("\n6. Plotting training history...")
    classifier.plot_training_history()
    
    # Step 8: Evaluate model
    print("\n7. Evaluating model...")
    accuracy, cm = classifier.evaluate_model(val_gen)
    
    # Step 9: Save model
    print("\n8. Saving model...")
    classifier.save_model()
    
    print("\nProject completed successfully!")

# Additional utility functions
def create_sample_data_structure():
    """Create sample data structure for testing"""
    import shutil
    
    # Create sample directory structure
    base_dir = Path('sample_data/raw')
    for class_name in ['arch', 'loop', 'whorl']:
        (base_dir / class_name).mkdir(parents=True, exist_ok=True)
    
    print("Sample data structure created in 'sample_data/raw'")
    print("Place your fingerprint images in the respective class folders:")
    print("- sample_data/raw/arch/")
    print("- sample_data/raw/loop/")
    print("- sample_data/raw/whorl/")

def demo_prediction():
    """Demo function to show prediction on a single image"""
    classifier = FingerprintClassifier(data_dir='data')
    
    # Load trained model
    try:
        classifier.load_model()
        
        # Predict on a sample image (replace with actual path)
        image_path = "path/to/your/test/image.jpg"
        if Path(image_path).exists():
            predicted_class, confidence = classifier.predict_single_image(image_path)
            print(f"Predicted class: {predicted_class}")
            print(f"Confidence: {confidence:.4f}")
        else:
            print("Sample image not found. Please provide a valid image path.")
            
    except FileNotFoundError:
        print("Trained model not found. Please train the model first.")

if __name__ == "__main__":
    # Uncomment the function you want to run
    main()
    # create_sample_data_structure()
    # demo_prediction()