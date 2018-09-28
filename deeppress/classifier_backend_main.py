from models import get_model, compile_model
from dataset import request_categories, prepare_dataset
from train import create_gens, start_training, create_labels
from predict import model_load, get_image, get_labels, predict_class


def train(model_id):
    filename, architecture = get_model(model_id)
    cat_dict, categories_id = request_categories()
    path = prepare_dataset(categories_id, filename)
    model, gen = compile_model(architecture, categories_id)
    train_generator, test_generator, image_files, class_indices = create_gens(path, gen)
    model_file, train_accuracy, train_loss, val_accuracy, val_loss = start_training(model, train_generator, test_generator, image_files, filename)
    create_labels(cat_dict, filename, class_indices)
    return train_accuracy, train_loss, val_accuracy, val_loss

def predictor(img_url, filename):
    model = model_load(filename)
    img = get_image(img_url)
    labels, names = get_labels(filename)
    predicted_id, predicted_class, confidence = predict_class(img, model, labels, names)
    return predicted_id, predicted_class, confidence
