import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression 
from sklearn.tree import DecisionTreeClassifier, plot_tree 
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, recall_score,
    f1_score, roc_curve, roc_auc_score
)

#use the same dataset as in EDA.py i.e.cleaned_titanic.csv
cleaned_titanic_df = pd.read_csv('cleaned_titanic.csv')

# Split the dataset into features and target variable
x = cleaned_titanic_df.drop(columns=['survived'])
y = cleaned_titanic_df['survived']
# Split the dataset into training and testing sets
'''The dataset is not perfectly balanced between these two classes. 
    If you perform an ordinary random split, the proportion of survivors 
    and non-survivors in the training and test sets can differ from the 
    original dataset.So, used stratify = y
'''
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42,stratify=y)
'''I have already taken cleaned data set in which all missing values are handled'''
print(f"Shape of train and test data:{x_train.shape},{x_test.shape}")

#preprocessing on training data only
categorical_columns = x.select_dtypes(include=['object', 'category']).columns.tolist()
numerical_columns = x.select_dtypes(include=['int64', 'float64']).columns.tolist()

'''Encode categorical columns using One-Hot Encoding'''
x_train = pd.get_dummies(
    x_train,columns=categorical_columns,drop_first=True)
x_test = pd.get_dummies(
    x_test,columns=categorical_columns,drop_first=True)

#standardization
scalar = StandardScaler()

#fit scalar only on x_train data 
x_train[numerical_columns] = scalar.fit_transform(x_train[numerical_columns])

#only tranform on x_test data
x_test[numerical_columns] = scalar.transform(x_test[numerical_columns])
print(f"After encoding shape of train and test data:{x_train.shape},{x_test.shape}")

# train three classifiers
#Logistic Regression
logistic_model = LogisticRegression()
logistic_model.fit(x_train, y_train)
logistic_predictions = logistic_model.predict(x_test)

# Decision Tree
decision_tree_model = DecisionTreeClassifier(random_state=42)
decision_tree_model.fit(x_train, y_train)
decision_tree_predictions = decision_tree_model.predict(x_test)
plt.figure(figsize=(20, 10))
plot_tree(
    decision_tree_model,
    feature_names=x_train.columns,
    class_names=['Not Survived', 'Survived'],
    filled=True,
    rounded=True,
    fontsize=8
)
plt.title("Decision Tree Classifier")
plt.show()

# Random Forest
random_forest_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
random_forest_model.fit(x_train, y_train)
random_forest_predictions = random_forest_model.predict(x_test)

#model evaluation
models = {
    'Logistic Regression': (
        logistic_model,
        logistic_predictions
    ),
    'Decision Tree': (
        decision_tree_model,
        decision_tree_predictions
    ),
    'Random Forest': (
        random_forest_model,
        random_forest_predictions
    )
}

results = []

for model_name, (model, predictions) in models.items():
    # Confusion Matrix
    cm = confusion_matrix(y_test, predictions)
    # Classification metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)

    # Probability of positive class
    probabilities = model.predict_proba(x_test)[:, 1]

    # ROC and AUC
    fpr, tpr, thresholds = roc_curve(y_test, probabilities)
    auc = roc_auc_score(y_test, probabilities)

    results.append({
        'Model': model_name,
        'Confusion Matrix': cm,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'AUC': auc
    })

    # ROC Curve
    plt.plot(
        fpr,
        tpr,
        label=f'{model_name} (AUC = {auc:.3f})'
    )

# ROC Curve
#plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Model Comparison')
plt.legend()
plt.show()

# Comparison Table
comparison_table = pd.DataFrame(results)
print(comparison_table)