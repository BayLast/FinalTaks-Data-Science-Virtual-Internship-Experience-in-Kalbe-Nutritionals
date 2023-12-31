# -*- coding: utf-8 -*-
"""VIX_Data-Science_Kalbe-Nutritionals_Bayu-Triadi-Putra.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R2KTKLtsbSDH2YVXqpY6skvCsQ4YpkPi

**Bayu Triadi Putra** **-** **Universitas Indraprasta PGRI**
"""

from google.colab import drive
drive.mount('/content/drive')

# importing library
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import product

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
from yellowbrick.cluster import KElbowVisualizer


import statsmodels.api as sm

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import autocorrelation_plot

from statsmodels.tsa.stattools import adfuller

import warnings
warnings.filterwarnings('ignore')

# Membaca dataset
df_customer = pd.read_csv(r'/content/drive/MyDrive/PBI Kalbe Data Science/Customer.csv', delimiter=';')
df_product = pd.read_csv(r'/content/drive/MyDrive/PBI Kalbe Data Science/Product.csv', delimiter=';')
df_store = pd.read_csv(r'/content/drive/MyDrive/PBI Kalbe Data Science/Store.csv', delimiter=';')
df_transaction = pd.read_csv(r'/content/drive/MyDrive/PBI Kalbe Data Science/Transaction.csv', delimiter=';')

def check_and_clean_data(df):
    # Initial counts of duplicates and missing data
    initial_duplicates = df.duplicated().sum()
    initial_missing = df.isnull().sum().sum()

    # Print initial counts
    print("Initial Count of Duplicates:", initial_duplicates)
    print("Initial Count of Missing Data:", initial_missing)

    # Dropping duplicates and missing values
    df_cleaned = df.drop_duplicates()
    df_cleaned = df_cleaned.dropna()

    # Final counts of duplicates and missing data
    final_duplicates = df_cleaned.duplicated().sum()
    final_missing = df_cleaned.isnull().sum().sum()

    # Print final counts
    print("Final Count of Duplicates:", final_duplicates)
    print("Final Count of Missing Data:", final_missing)

    return df_cleaned

#Data cleaning for customer csv file
df_customer.head()

# Data cleansing for df_customer by replacing ',' with '.' for the 'Income' column
df_customer['Income'] = df_customer['Income'].replace('[,]', '.', regex=True).astype('float')

df_customer = check_and_clean_data(df_customer)

#Data cleaning for product csv file

df_product.head()

df_product = check_and_clean_data(df_product)

#Data cleaning for store csv file

df_store.head()

# Data cleansing for df_store by replacing ',' with '.'
df_store['Latitude'] = df_store['Latitude'].replace('[,]', '.', regex=True).astype('float')
df_store['Longitude'] = df_store['Longitude'].replace('[,]', '.', regex=True).astype('float')

df_store = check_and_clean_data(df_store)

#Data cleaning for transaction csv file

df_transaction.head()

df_transaction = check_and_clean_data(df_transaction)

# Data cleansing for df_transaction by changing the Date format to datetime
df_transaction['Date'] = pd.to_datetime(df_transaction['Date'])

df_transaction.head()

print(df_transaction['TransactionID'].value_counts())

print(df_transaction[df_transaction['TransactionID'] == 'TR71313'])
print(df_transaction[df_transaction['TransactionID'] == 'TR42197'])

"""Dari hasil di atas terlihat bahwa beberapa ID Transaksi digunakan untuk ID Pelanggan yang berbeda pada tanggal yang berbeda. Ini mungkin menunjukkan kesalahan atau ketidakkonsistenan input data"""

# Group by 'TransactionID' and select the row with the maximum 'Date'
df_transaction = df_transaction.sort_values(by='Date', ascending=False) \
    .groupby('TransactionID', as_index=False).first()

print(df_transaction[df_transaction['TransactionID'] == 'TR71313'])
print(df_transaction[df_transaction['TransactionID'] == 'TR42197'])

#merge all data

# Merge the DataFrames
df_merge = pd.merge(df_transaction, df_customer, on='CustomerID', how='inner')
df_merge = pd.merge(df_merge, df_product.drop(columns=('Price')), on='ProductID', how='inner')
df_merge = pd.merge(df_merge, df_store, on='StoreID', how='inner')

df_merge.head()

#machine learning: regression

df_regresi = df_merge.groupby(['Date']).agg({
    'Qty' : 'sum'
}).reset_index()

df_regresi

decomposed = seasonal_decompose(df_regresi.set_index('Date'))

plt.figure(figsize=(8, 8))
plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')
plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Seasonality')
plt.subplot(313)
decomposed.resid.plot(ax=plt.gca())
plt.title('Residuals')
plt.tight_layout()

"""**Check Stationary Data**"""

cut_off = round(df_regresi.shape[0]*0.8)
df_train = df_regresi[:cut_off]
df_test = df_regresi[cut_off:].reset_index(drop=True)
df_train.shape, df_train.shape

df_train

df_test

plt.figure(figsize=(12,5))
sns.lineplot(data=train, x=train.index, y=train['Qty'])
sns.lineplot(data=test, x=test.index, y=test['Qty'])
plt.show()

from statsmodels.tsa.stattools import adfuller
result = adfuller(df_regresi['Qty'])
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
  print('\t%s: %.3f' % (key, value))

"""Berdasarkan uji *Dickey-Fuller* data stasioner karena p-value < 0,05

**Choosing p, d, and q value**
"""

autocorrelation_plot(df_regresi['Qty']);

"""**Choosing p, d, and q values**"""

import itertools

p=range(0,20)
q=range(0,10)
d=range(0,2)

pdq_combinations=list(itertools.product(p,d,q))
print(len(pdq_combinations))
print(pdq_combinations)

cut_off = round(df_regresi.shape[0]*0.8)
train = df_regresi[:cut_off]
test = df_regresi[cut_off:].reset_index(drop=True)
train.shape, train.shape

rmse=[]
order1=[]

train = train.set_index('Date')
test = test.set_index('Date')
y = train['Qty']

for pdq in pdq_combinations:
  try:
    model=ARIMA(train, order=pdq).fit()
    pred=model.predict(start=len(train), end=(len(df_regresi)-1))
    error=np.sqrt(mean_squared_error(test,pred))
    order1.append(pdq)
    rmse.append(error)

  except:
    continue

results=pd.DataFrame(index=order1, data=rmse, columns=['RMSE'])

results.head()

sorted_results = results.sort_values(by='RMSE', ascending=True)
sorted_results

file_path = '/content/drive/MyDrive/PBI Kalbe Data Science/pdq_values2.csv'
sorted_results.to_csv(file_path, index=False)

"""**ARIMA**"""

def calculate_rmse(y_actual, y_pred):
    '''
    Function to calculate RMSE
    '''
    return mean_squared_error(y_actual, y_pred) ** 0.5

def evaluate_model(y_actual, y_pred):
    '''
    Function to evaluate machine learning model
    '''
    rmse = calculate_rmse(y_actual, y_pred)
    mae = mean_absolute_error(y_actual, y_pred)
    return rmse, mae

# Your existing code
df_train = df_train.set_index('Date')
df_test = df_test.set_index('Date')
y = df_train['Qty']

ARIMAmodel = ARIMA(y, order=(9, 1, 6)).fit()

y_pred = ARIMAmodel.get_forecast(len(df_test))

y_pred_df = y_pred.conf_int()
y_pred_df['predictions'] = ARIMAmodel.predict(start=y_pred_df.index[0], end=y_pred_df.index[-1])
y_pred_df.index = df_test.index
y_pred_out = y_pred_df['predictions']

rmse_value, mae_value = evaluate_model(df_test['Qty'], y_pred_out)

plt.figure(figsize=(20, 5))
plt.plot(df_train['Qty'])
plt.plot(df_test['Qty'], color='red')
plt.plot(y_pred_out, color='black', label='ARIMA Predictions')
plt.legend()

print(f'RMSE value: {rmse_value}')
print(f'MAE value: {mae_value}')

y_pred_out

"""**Predict Future Data**"""

#Build model on full dataset
y_reg = df_regresi.set_index('Date')
y_reg = y_reg['Qty']
final_model = ARIMA(y_reg, order=(9, 1, 6)).fit()
#Forecast for the next 30 days
prediction = final_model.predict(len(y_reg), len(y_reg)+30)

prediction

plt.figure(figsize=(12, 5))
plt.plot(y_reg, label='Train')
plt.plot(prediction, color='green', label='30 Days Predictions')
plt.legend()

prediction.describe()

"""Dari perkiraan rata-rata kuantitas penjualan pada bulan Januari 2023 adalah 48.261500 atau dibulatkan menjadi sekitar 48 pcs/hari.

**Clustering**
"""

df_merge.head()

# Calculate the correlation matrix
correlation_matrix = df_merge.corr()
correlation_matrix

"""Berdasarkan matriks korelasi dan mempertimbangkan tujuan mengelompokkan pelanggan serupa, kita dapat menggunakan Qty atau TotalAmount sebagai parameter karena nilai korelasinya serupa. Untuk model ini, saya menggunakan TotalAmount sebagai parameternya."""

df_cluster = df_merge.groupby(['CustomerID']).agg({
    'TransactionID': 'count',
    'Qty':'sum',
    'TotalAmount': 'sum'
}).reset_index()
df_cluster

df_cluster.info()

df_cluster = df_cluster.drop(columns = ['CustomerID'])
df_cluster.head()

df_cluster.info()

df_cluster.isna().sum()

#Standarisasi dataset
X = df_cluster.values
X_std = StandardScaler().fit_transform(X)
df_std = pd.DataFrame(data=X_std,columns=df_cluster.columns)
df_std.isna().sum()

#Normalisasi dataset dengan minmaxscaler
X_norm = MinMaxScaler().fit_transform(X)
X_norm

# Normalisasi dataset dengan preprocessing sklearn
X_norm2 = preprocessing.normalize(df_cluster)
X_norm2

X_std

df_std

plt.figure(figsize=(18,3))

plt.subplot(1,3,1)
sns.histplot(df_cluster['Qty'], color='royalblue', kde= True)
plt.title('Distribusi Quantity', fontsize=16)
plt.xlabel('Quantity', fontsize=14)
plt.ylabel('Sum', fontsize=14)

plt.subplot(1,3,2)
sns.histplot(df_cluster['TransactionID'], color='deeppink', kde= True)
plt.title('distribusi transaksi pelanggan', fontsize=16)
plt.xlabel('transaksi pelanggan', fontsize=14)


plt.subplot(1,3,3)
sns.histplot(df_cluster['TotalAmount'], color='seagreen', kde= True)
plt.title('distribusi Jumlah total', fontsize=16)
plt.xlabel('Total Amount', fontsize=14)
plt.ylabel('Sum', fontsize=14)

#plt.tight_layout()

plt.show()

wcss= []
for n in range (1,11):
    model1 = KMeans(n_clusters=n, init='k-means++', n_init = 10, max_iter=100, tol =0.0001, random_state = 100)
    model1.fit(X_std)
    wcss.append(model1.inertia_)
print(wcss)

plt.figure(figsize=(10,8))
plt.plot(list(range(1,11)), wcss, color = 'blue', marker = 'o', linewidth=2, markersize=12, markerfacecolor= 'm',
         markeredgecolor= 'm')
plt.title('WCSS vs Number of Cluster', fontsize = 15)
plt.xlabel('Number of Cluster')
plt.ylabel('WCSS')
plt.xticks(list(range(1,11)))
plt.show()

#Elbow Method with yellowbrick library
visualizer = KElbowVisualizer(model1, k=(2,10))
visualizer.fit(X_std)
visualizer.show()

K = range(2, 8)
fits = []
score = []

for k in K:
    model = KMeans(n_clusters=k, random_state=0, n_init='auto').fit(data_cluster_normalize)
    fits.append(model)
    score.append(silhouette_score(data_cluster_normalize, model.labels_, metric='euclidean'))

sns.lineplot(x = K, y = score)

# Kmeans n_cluster = 4
#Clustering Kmeans
kmeans_4 = KMeans(n_clusters=4,init='k-means++',max_iter=300,n_init=10,random_state=100)
kmeans_4.fit(X_std)

# Masukin cluster ke dataset
df_cluster['cluster'] = kmeans_4.labels_
df_cluster.head()

plt.figure(figsize=(6,6))
sns.pairplot(data=df_cluster,hue='cluster',palette='Set1')
plt.show()

df_cluster['CustomerID'] = df_cluster['CustomerID']
df_cluster_mean = df_cluster.groupby('cluster').agg({'CustomerID':'count','TransactionID':'mean','Qty':'mean','TotalAmount':'mean'})
df_cluster_mean.sort_values('CustomerID', ascending = False)

"""### Summary
* Cluster 2 <br>
    - Cluster dengan jumlah pelanggan paling banyak.
    - Karakteristik pelanggan menempati posisi ketiga dari setiap metriks (transaction, quantity, total amount).
<br> **Rekomendasi**:
        - Membangun hubungan baik dengan pelanggan.
        - Memberikan survey untuk mengembangkan minat pelanggan terbanyak.
* Cluster 3 <br>
    - Karakteristik pelanggan yang menempati posisi ke dua tertinggi pada setiap metriks.
<br> **Rekomendasi**:
        - Memberikan promo secara rutin untuk meningkatkan transaksi.
        - Melakukan upselling produk-produk dengan harga tinggi.
* Cluster 1 <br>
    - Karakteristik pelanggan dengan nilai terendah pada setiap metriksnya.
<br> **Rekomendasi**:
        - Memberikan discount price yang cukup besar untuk meningkatkan Transaksi pelanggan.
        - Memberikan promo pada transaksi dengan Quantity lebih tinggi.
        - Memberikan survey untuk mengetahui potensi pengembangan produk.
* Cluster 0 <br>
    - Cluster dengan jumlah pelanggan paling sedikit
    - Karakteristik pelanggan dengan nilai tertinggi pada setiap metriksnya.
<br> **Rekomendasi**:
        - Memberikan promo loyalti untuk mempertahankan transaksi
        - Memberikan survey kepuasan pelanggan.
        - Melakukan upselling produk dengan harga lebih tinggi

"""