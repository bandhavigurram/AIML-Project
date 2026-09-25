import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

def load_titanic_dataset():
    #Load the classic Titanic dataset 
    titanic = sns.load_dataset('titanic')
    return titanic

def clean_data(df):
    # Perform data cleaning operations here
    #find the percentage of missing values in each column
    missing_percentages = (df.isnull().sum() / len(df)) * 100
    print(f"Percentage of missing values in each column:\n{missing_percentages}")

    '''age has 19.9% missing values, we can fill it with the median value of the age column
    embarked has 0.2% missing values, as it's < 5 %, we can drop the rows with missing values in this column
    deck has 77.5% missing values, we can drop this column as it has too many missing values
    emabarked_town has 0.2% missing values, we can drop the rows with missing values in this column'''
    df.fillna({'age':df['age'].median()},inplace =True)
    df.dropna(subset=['embarked', 'embark_town'], inplace=True)
    df.drop(columns=['deck'], inplace=True)
    return df

def histogram_plot(df):
    #histogram plot for age 
    plt.figure(figsize=(12, 5))
    plt.title('Age Distribution',fontsize=14,color='blue')
    plt.xlabel('Age',fontsize = 12)
    plt.ylabel('Count',fontsize = 12)
    sns.histplot(df['age'],bins = 40,color='lavender',edgecolor='magenta',kde=True)
    plt.show()
    #histogram plot for fare
    plt.figure(figsize=(12, 5))
    plt.title('Fare Distribution',fontsize=14,color='blue')
    plt.xlabel('Fare',fontsize = 12)
    plt.ylabel('Count',fontsize = 12)
    sns.histplot(df['fare'],bins = 40,color='lavender',edgecolor='magenta',kde=True)
    plt.show()

def box_plot(df):
    #box plot for age
    plt.figure(figsize=(12, 5))
    plt.title('Age Box Plot',fontsize=14,color='blue')
    plt.xlabel('Age',fontsize = 12)
    plt.ylabel('Count',fontsize = 12)
    sns.boxplot(x=df['age'],color='pink')
    plt.show()
    #box plot for fare
    plt.figure(figsize=(12, 5))
    plt.title('Fare Box Plot',fontsize=14,color='blue')
    plt.xlabel('Fare',fontsize = 12)
    plt.ylabel('Count',fontsize = 12)
    sns.boxplot(x=df['fare'],color='pink')
    plt.show()

    #find the outliers in age and fare columns using IQR method
    Q1_age = df['age'].quantile(0.25)
    Q3_age = df['age'].quantile(0.75)
    IQR_age = Q3_age - Q1_age
    lower_bound_age = Q1_age - (1.5 * IQR_age)
    upper_bound_age = Q3_age + (1.5 * IQR_age)
    age_outliers = df[(df['age'] < lower_bound_age) | (df['age'] > upper_bound_age)]

    Q1_fare = df['fare'].quantile(0.25)
    Q3_fare = df['fare'].quantile(0.75)
    IQR_fare = Q3_fare - Q1_fare
    lower_bound_fare = Q1_fare - (1.5 * IQR_fare)
    upper_bound_fare = Q3_fare + (1.5 * IQR_fare)
    fare_outliers = df[(df['fare'] < lower_bound_fare) | (df['fare'] > upper_bound_fare)]
    return age_outliers, fare_outliers

def distribution_of_data(df, column):
    '''check the distribution of the data using skewness by mean, median and mode
        Check distribution using skewness.
            Positive skewness  -> right-skewed
            Negative skewness  -> left-skewed
            Near zero          -> approximately symmetric
    '''
    mean = df[column].mean()
    median = df[column].median()
    mode = df[column].mode()[0]
    '''If the mean is greater than the median and the median is greater than the mode, 
    then the distribution is positively skewed.
    If the mean is less than the median and the median is less than the mode,
    then the distribution is negatively skewed.
    If the mean, median, and mode are approximately equal, 
    then the distribution is approximately symmetric.'''
    if (mean > median) and (median > mode):
        return f"The distribution of {column} is right-skewed."
    elif (mean < median) and (median < mode):
        return f"The distribution of {column} is left-skewed."
    else:
        return f"The distribution of {column} is symmetric."

def survival_rate(df):
    #survival rate for sex
    survival_rate_sex = df.groupby('sex')['survived'].mean().reset_index()
    #survival rate for pclass
    survival_rate_pclass = df.groupby('pclass')['survived'].mean().reset_index()
    #survival rate for sex and pclass
    survival_rate_sex_pclass = df.groupby(['sex', 'pclass'])['survived'].mean().reset_index()
    return survival_rate_sex, survival_rate_pclass, survival_rate_sex_pclass

def correlation_matrix(df, columns):
    #correlation matrix for numerical columns
    corr_matrix = df[columns].corr()
    plt.figure(figsize=(10, 8))
    plt.title('Correlation Matrix', fontsize=14, color='blue')
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.show()
    #get the upper triangle exluding the diagonal values of the correlation matrix
    '''the matrix is symmetric, so we only need to look at one half of the matrix.
    We can use the np.triu() function to get the upper triangle of the matrix'''
    upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape),k=1).astype(bool))
    #get the pairs of columns with the highest correlation values
    correlation_pairs = (upper_triangle.stack().sort_values(key=abs,ascending=False)).head(2)
    return correlation_pairs

def multivariate_analysis(df):
    #chart 1: survived rate by sex
    '''The chart shows that female passengers had a substantially higher survival rate than male passengers.
      This indicates that sex was strongly associated with survival outcomes in the Titanic dataset.
    '''
    survival_by_sex,survival_by_pclass,survival_by_sex_pclass = survival_rate(df)
    plt.figure(figsize=(10, 6))
    plt.title('Survival Rate by Sex',fontsize=14,color='blue')
    plt.xlabel('Sex',fontsize = 12)
    plt.ylabel('Survival Rate',fontsize = 12)
    sns.barplot(x=df['sex'],y=df['survived'],data=survival_by_sex,color='brown')
    plt.show()
    
    #chart 2: survived rate by pclass
    '''The chart shows that first-class passengers had a higher survival rate than second
        and third-class passengers. This suggests that passenger class was associated with survival,
        with passengers in higher classes experiencing higher survival rates.
    '''
    plt.figure(figsize=(10, 6))
    plt.title('Survival Rate by Pclass',fontsize=14,color='blue')
    plt.xlabel('Passenger Class',fontsize = 12)
    plt.ylabel('Survival Rate',fontsize = 12)
    sns.barplot(x='pclass',y='survived',data=survival_by_pclass,color='brown')
    plt.show()

    #chart 3: survived rate by sex and pclass
    '''The chart shows survival differences when sex and passenger class are considered together.
       Female passengers generally had higher survival rates than male passengers within
       the same passenger class, while first-class passengers generally had higher survival rates 
       than passengers in lower classes.
    '''
    plt.figure(figsize=(10, 6))
    plt.title('Survival Rate by Sex and Pclass',fontsize=14,color='blue')
    plt.xlabel('Passenger Class',fontsize = 12)
    plt.ylabel('Survival Rate',fontsize = 12)
    sns.barplot(x='pclass',y='survived',hue='sex',data=survival_by_sex_pclass)
    plt.show()

    #chart 4: survived rate by age and fare
    '''The scatter plot shows the relationship between passenger age, fare, and survival status.
        Surviving passengers are distributed across different ages and fares, but the plot also 
        shows that fare and age alone do not completely explain survival,
        supporting the need to consider multiple passenger characteristics together.
    '''
    plt.figure(figsize=(10, 6))
    plt.title('Survival Rate by Age and Fare',fontsize=14,color='blue')
    plt.xlabel('Age',fontsize = 12)
    plt.ylabel('Fare',fontsize = 12)
    sns.scatterplot(x='age',y='fare',hue='survived',data=df)
    plt.show()

def standardize_columns(df, columns):
    before_standardization = df[columns].agg(['mean', 'std'])
    #Apply StandardScaler to standardize the specified columns
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    after_standardization = df[columns].agg(['mean', 'std'])
    return before_standardization, after_standardization

if __name__ == "__main__":
    titanic = load_titanic_dataset()
    #save the dataset to a CSV file
    titanic.to_csv('titanic.csv', index=False)
    df = pd.read_csv('titanic.csv')
    #check the data information
    titanic.info()
    print(titanic.describe())
    print(titanic.shape)
    #data exploration
    cleaned_dataset = clean_data(df)
    cleaned_dataset.to_csv('cleaned_titanic.csv', index=False)
    #univariate analysis : ploat histogram and box plot for age and fare columns
    histogram_plot(cleaned_dataset)
    age_outliers, fare_outliers = box_plot(cleaned_dataset)
    print(f"Number of outliers in age column: {len(age_outliers)}")
    print(f"Number of outliers in fare column: {len(fare_outliers)}")
    #check the distribution of the data using skewness by mean, median and mode
    type_of_distribution = distribution_of_data(cleaned_dataset, 'fare')
    print(type_of_distribution)
    #Bivariate analysis: using boolean masking to find the correlation between sex and pclass columns
    survival_rate_sex, survival_rate_pclass, survival_rate_sex_pclass = survival_rate(cleaned_dataset)
    print(f'''Survival rate by sex: {survival_rate_sex}\n
          Survival rate by pclass: {survival_rate_pclass}\n
          Survival rate of sex and pclass: {survival_rate_sex_pclass}
    ''')
    #correlation matrix for numerical columns
    corr_columns = ['survived', 'pclass', 'age', 'sibsp', 'parch', 'fare']
    correlation_pairs = correlation_matrix(cleaned_dataset, corr_columns)
    '''Correlation interpretation:
            The strongest correlation pairs are identified based on the absolute
            value of their off-diagonal correlation coefficients. A positive
            correlation indicates that the two variables tend to increase together,
            while a negative correlation indicates that one tends to decrease as
            the other increases. Correlation shows association, not causation.
    '''
    print(f"Two strongest correlations:\n{correlation_pairs}")
    '''Multivariate analysis: ": produce at least 4 distinct charts that together build 
    a coherent argument about who was more likely to survive and why'''
    multivariate_analysis(cleaned_dataset)

    #standardize age and fare columns using z-score normalization/StandardScaler
    columns_to_standardize = ['age', 'fare']
    before_standardization, after_standardization = standardize_columns(cleaned_dataset, columns_to_standardize)
    print(f"Before standardization:\n{before_standardization}\nAfter standardization:\n{after_standardization}")



