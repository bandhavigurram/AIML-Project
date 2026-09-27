# Titanic Survival Analysis and Classification

## Project Overview

This project performs Exploratory Data Analysis (EDA), data preprocessing, visualization, and machine learning classification on the classic Titanic dataset.

The project contains two main parts:

1. Exploratory Data Analysis
2. Machine Learning Modeling

The Titanic dataset is loaded using Seaborn's built-in dataset.

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn

## Project Structure

```text
AIML-Project/
│
├── EDA.py
├── modeling.py
├── titanic.csv
├── cleaned_titanic.csv
├── README.md
└── requirements.txt
```

## 1. Exploratory Data Analysis

The EDA script loads the Titanic dataset using:

```python
sns.load_dataset('titanic')
```

The original dataset is saved as `titanic.csv`.

The script then reads the CSV file and performs dataset inspection, cleaning, visualization, statistical analysis, correlation analysis, multivariate analysis, and standardization.

## 2. Data Cleaning

The `clean_data()` function handles missing values.

### Missing Value Percentage

The percentage of missing values in every column is calculated using:

```python
missing_percentages = (df.isnull().sum() / len(df)) * 100
```

### Age

Missing values in the `age` column are replaced with the median age:

```python
df.fillna({'age': df['age'].median()}, inplace=True)
```

### Embarked and Embark Town

Rows containing missing values in `embarked` or `embark_town` are dropped:

```python
df.dropna(subset=['embarked', 'embark_town'], inplace=True)
```

### Deck

The `deck` column is removed because it contains a high percentage of missing values:

```python
df.drop(columns=['deck'], inplace=True)
```

The cleaned dataset is saved as:

```text
cleaned_titanic.csv
```

## 3. Univariate Analysis

Univariate analysis is performed on `age` and `fare`.

### Histograms

Histograms with KDE are created for:

- Age
- Fare

### Box Plots

Box plots are created for:

- Age
- Fare

### Outlier Detection Using IQR

Outliers are identified using:

```text
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

The number of detected outliers in `age` and `fare` is printed.

## 4. Distribution Analysis

The project checks the distribution of the `fare` column using:

- Mean
- Median
- Mode

The code interprets the distribution as:

```text
Mean > Median > Mode
    → Right-skewed

Mean < Median < Mode
    → Left-skewed

Otherwise
    → Symmetric
```

## 5. Survival Rate Analysis

Survival rates are calculated using the mean of the binary `survived` column.

The analysis is performed for:

1. Sex
2. Passenger class
3. Sex and passenger class together

Examples:

```python
df.groupby('sex')['survived'].mean()
```

```python
df.groupby('pclass')['survived'].mean()
```

```python
df.groupby(['sex', 'pclass'])['survived'].mean()
```

Since `survived` contains 0 and 1, its mean represents the survival rate.

## 6. Correlation Analysis

A correlation matrix is generated for:

```text
survived
pclass
age
sibsp
parch
fare
```

The correlation matrix is visualized using a Seaborn heatmap.

The project also extracts the two strongest off-diagonal correlation pairs based on the absolute correlation value.

Correlation indicates association between variables and does not establish causation.

## 7. Multivariate Analysis

Four charts are created:

1. Survival Rate by Sex
2. Survival Rate by Passenger Class
3. Survival Rate by Sex and Passenger Class
4. Age vs Fare by Survival Status

The fourth chart uses:

```text
X-axis → Age
Y-axis → Fare
Hue   → Survived
```

## 8. Standardization

The `age` and `fare` columns are standardized using:

```python
StandardScaler()
```

The transformation is equivalent to:

```text
z = (x - mean) / standard deviation
```

The project prints the mean and standard deviation before and after standardization.

The transformed variables should have approximately:

```text
Mean ≈ 0
Standard deviation ≈ 1
```

## 9. Machine Learning Modeling

The modeling script uses:

```text
cleaned_titanic.csv
```

The target variable is:

```text
survived
```

### Features and Target

```python
x = cleaned_titanic_df.drop(columns=['survived'])
y = cleaned_titanic_df['survived']
```

Therefore:

```text
X → All columns except survived
y → survived
```

## 10. Train-Test Split

The dataset is divided into:

```text
80% → Training data
20% → Testing data
```

using:

```python
train_test_split(
    x,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
```

`stratify=y` maintains a similar target-class distribution in the training and testing datasets.

## 11. Categorical Feature Encoding

Categorical columns are identified using:

```python
x.select_dtypes(include=['object', 'category'])
```

One-hot encoding is performed using:

```python
pd.get_dummies(
    x_train,
    columns=categorical_columns,
    drop_first=True
)
```

The same operation is performed on the test dataset.

## 12. Numerical Feature Standardization

Numerical columns are identified using:

```python
x.select_dtypes(include=['int64', 'float64'])
```

`StandardScaler` is fitted only on the training data:

```python
x_train[numerical_columns] = scalar.fit_transform(
    x_train[numerical_columns]
)
```

The fitted scaler is then used to transform the test data:

```python
x_test[numerical_columns] = scalar.transform(
    x_test[numerical_columns]
)
```

## 13. Classification Models

Three classifiers are trained.

### Logistic Regression

```python
LogisticRegression()
```

### Decision Tree Classifier

```python
DecisionTreeClassifier(random_state=42)
```

A tree visualization is generated using `plot_tree()`.

### Random Forest Classifier

```python
RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
```

The Random Forest uses 100 estimators.

## 14. Model Evaluation

All three models are evaluated on the same test dataset.

The following metrics are calculated:

### Confusion Matrix

```python
confusion_matrix(y_test, predictions)
```

The matrix contains:

- True Negative
- False Positive
- False Negative
- True Positive

### Accuracy

```python
accuracy_score(y_test, predictions)
```

### Precision

```python
precision_score(y_test, predictions)
```

### Recall

```python
recall_score(y_test, predictions)
```

### F1 Score

```python
f1_score(y_test, predictions)
```

## 15. ROC Curve and ROC-AUC

The probability of the positive class is obtained using:

```python
model.predict_proba(x_test)[:, 1]
```

The ROC curve is generated using:

```python
roc_curve(y_test, probabilities)
```

ROC-AUC is calculated using:

```python
roc_auc_score(y_test, probabilities)
```

The ROC plot compares all three models using False Positive Rate and True Positive Rate.

## 16. Model Comparison

The results are stored in a DataFrame containing:

```text
Model
Confusion Matrix
Accuracy
Precision
Recall
F1 Score
AUC
```

The final comparison table is printed using:

```python
print(comparison_table)
```

## 17. How to Run the Project

### Step 1: Install Dependencies

Open the terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### Step 2: Run EDA

```bash
python EDA.py
```

This will:

- Load the Titanic dataset
- Save `titanic.csv`
- Clean the data
- Save `cleaned_titanic.csv`
- Display dataset information
- Generate EDA visualizations
- Calculate survival rates
- Generate the correlation matrix
- Perform multivariate analysis
- Standardize age and fare

### Step 3: Run Modeling

After running `EDA.py`, execute:

```bash
python modeling.py
```

This will:

- Load `cleaned_titanic.csv`
- Split features and target
- Perform the train-test split
- Encode categorical variables
- Standardize numerical variables
- Train Logistic Regression
- Train Decision Tree
- Train Random Forest
- Display the Decision Tree
- Generate the ROC curve
- Print the model comparison table

## 18. Reproducibility

`random_state=42` is used for:

- Train-test split
- Decision Tree
- Random Forest

This helps produce reproducible results when the code is run under the same conditions.

## 19. Generated Files

The EDA script generates:

```text
titanic.csv
cleaned_titanic.csv
```

The modeling script displays the model evaluation results and does not save trained model objects.

## 20. Summary

The project demonstrates an end-to-end machine learning workflow:

```text
Load Dataset
      ↓
Inspect Dataset
      ↓
Handle Missing Values
      ↓
Exploratory Data Analysis
      ↓
Outlier Analysis
      ↓
Distribution Analysis
      ↓
Survival Rate Analysis
      ↓
Correlation Analysis
      ↓
Multivariate Analysis
      ↓
Standardization
      ↓
Train-Test Split
      ↓
Categorical Encoding
      ↓
Feature Standardization
      ↓
Model Training
      ↓
Logistic Regression
Decision Tree
Random Forest
      ↓
Model Evaluation
      ↓
Accuracy / Precision / Recall / F1 / AUC
      ↓
ROC Curve and Model Comparison
```
