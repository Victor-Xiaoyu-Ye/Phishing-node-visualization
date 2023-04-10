from model3 import Model
import pandas as pd
import numpy as np
from sklearn import metrics
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
lgb_model=lgb.Booster(model_file='./model.txt')
data=pd.read_csv('./predict_data.csv')
model=Model(data,"")
feature=model.get_feature(data)
data_adress=feature['address']
feature=feature.drop(['address'],axis=1)
feature.columns=list(map(model.deal_feature_name,feature.columns))
result_f=lgb_model.predict(feature)
result=[]
for item in result_f:
	if item>0.8:
		result.append(1)
	elif item<0.2:
		result.append(0)
	else:
		result.append(99)
result=pd.DataFrame(result,columns=['label'])
result=pd.concat([data_adress,result],axis=1)

result_exc=result[result['label']!=99]

result_fd=result[result['label']==99]
result_fd_address=result_fd['address']
feature_fd=model.get_feature(data)
feature_fd.columns=list(map(model.deal_feature_name,feature_fd.columns))
print(feature_fd.columns)
feature_fd.drop(['from_in_sum_sum',
		       'from_in_sum_std', 'from_in_sum_median', 'from_in_sum_max',
		       'from_in_sum_min', 'from_in_mean_sum', 'from_in_mean_std',
		       'from_in_mean_median', 'from_in_mean_max', 'from_in_mean_min',
		       'from_in_max_sum', 'from_in_max_std', 'from_in_max_median',
		       'from_in_max_max', 'from_in_max_min', 'from_in_min_sum',
		       'from_in_min_std', 'from_in_min_median', 'from_in_min_max',
		       'from_in_min_min', 'out_count', 'out_nunique',
		       'out_count_nunique_ratio', 'out_count_nunique_equal', 'to_out_sum_sum',
		       'to_out_sum_std', 'to_out_sum_median', 'to_out_sum_max',
		       'to_out_sum_min', 'to_out_mean_sum', 'to_out_mean_std',
		       'to_out_mean_median', 'to_out_mean_max', 'to_out_mean_min',
		       'to_out_max_sum', 'to_out_max_std', 'to_out_max_median',
		       'to_out_max_max', 'to_out_max_min', 'to_out_min_sum', 'to_out_min_std',
		       'to_out_min_median', 'to_out_min_max', 'to_out_min_min', 'in_count',
		       'in_nunique', 'in_count_nunique_ratio', 'in_count_nunique_equal'],inplace=True,axis=1)
feature_fd=pd.merge(left=result_fd_address,right=feature_fd,left_on='address', right_on='address',how='inner')
data_fd_adress=feature_fd['address']
feature_fd=feature_fd.drop(['address'],axis=1)
print(feature_fd.columns)
lgb_model_fd=lgb.Booster(model_file='./model_fd.txt')
result_f_fd=lgb_model_fd.predict(feature_fd)
print(len(result_f_fd))
result_fd=[]
for item in result_f_fd:
	if item>0.5:
		result_fd.append(1)
	else:
		result_fd.append(0)
print(len(result_fd))
result_fd=pd.DataFrame(result_fd,columns=['label'])
print(len(result_fd))
result_fd=pd.concat([data_fd_adress,result_fd],axis=1)
print(result_fd)
result_all=pd.concat([result_exc,result_fd])
print(len(result_exc))
print(len(result_all[result_all['label']==1]))
result_all.to_csv('./predict_label.csv')


