import json
from timeit import default_timer

import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, ConfusionMatrixDisplay, \
    confusion_matrix, auc, roc_curve

from src.dataset_handler import default_preprocess, load_csv_dataset
from src.trainer import train_model


def test_model(model, x_test, y_test):
    start = default_timer()
    res = score_test(model.predict(x_test), y_test)
    print(f'Tested {model.__class__.__name__} model in {round(default_timer() - start, 2)} seconds.\n')
    return res



def score_test(y_pred: np.ndarray, y_test):
    matrix = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = matrix.ravel()
    ConfusionMatrixDisplay(matrix)
    plt.show()
    fpr, tpr, _ = roc_curve(y_test, y_pred, pos_label=1)
    return {
        'confusion_matrix': {
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'tp': int(tp),
        },
        'auc': round(auc(fpr, tpr), 3),
        'accuracy': round(accuracy_score(y_test, y_pred), 3),
        'f1': round(f1_score(y_test, y_pred), 3),
        'recall': round(recall_score(y_test, y_pred, average="binary"), 3),
        'precision': round(precision_score(y_test, y_pred), 3),
    }


def base_test(
        csv_path,
        base_model,
        index_col,
        target_col,
        test_size=0.2,
        exclude_cols=None,
        preprocess: callable = default_preprocess
):
    if exclude_cols is None:
        exclude_cols = []
    feature_train, feature_test, label_train, label_test = load_csv_dataset(
        csv_path, index_col, target_col, exclude_cols, test_size=test_size, preprocess=preprocess)
    label_train = label_train[target_col].tolist()
    label_test = label_test[target_col].tolist()
    model = train_model(base_model, feature_train, label_train)
    start = default_timer()
    test_results = test_model(model, feature_test, label_test)
    report = {
        'model': base_model.__class__.__name__,
        'results': test_results
    }
    save_test_results(report)
    return test_results


def save_test_results(results):
    file_name = f"out\\test-results\\{results['model']}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
