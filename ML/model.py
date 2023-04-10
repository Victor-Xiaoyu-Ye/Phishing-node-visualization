import pandas as pd
import numpy as np
from sklearn import metrics
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
#该部分代码有一小部分参考借鉴了陈博士的代码资料，参考的部分已用*标出
class Model:
	def __init__(self,train_data,train_label):
		self.train_data=train_data
		self.train_label=train_label
		self.lgb_params = {
	    'boosting_type': 'goss',
	    'objective': 'binary',
	    'learning_rate': 0.2,
	    'num_leaves': 40,
	    'verbosity': -1,
	    'max_depth': 8,
	    'metric': {'l2', 'auc'}
	    }
		self.slice=1/3
	def init_train_data(self):
		reverse_train_data = self.train_data.copy(deep=True)
		reverse_train_data.columns = ['blockNumber','to','from','value']
		reverse_train_data['value']*= -1
		self.train_data = pd.concat([self.train_data, reverse_train_data],axis = 0)
		self.train_data.sort_index(inplace=True)
		feature = self.get_feature(self.train_data)
		feature.columns=list(map(self.deal_feature_name,feature.columns))
		train_list,train_list_y=self.concat_feature(feature, train_label)
		train_list_fd,train_list_y_fd=self.concat_feature(feature, train_label,fd=1)
		return train_list,train_list_y,train_list_fd,train_list_y_fd
	def model_train(self,train_list,train_list_y,train_list_fd,train_list_y_fd):
		for i in range(0,5):
			x_train=train_list[i]
			y_train=train_list_y[i]
			split=1-self.slice
			split= int(split * len(x_train))
			train = x_train[0:split]
			train_y = y_train[0:split]
			test = x_train[split:]
			test_y = y_train[split:]
			train_set = lgb.Dataset(train, label = train_y, free_raw_data=False)
			test_set = lgb.Dataset(test, label = test_y, free_raw_data=False)

			x_train_fd=train_list_fd[i]
			y_train_fd=train_list_y_fd[i]
			split=1-self.slice
			split_fd = int(split * len(x_train))
			train_fd = x_train_fd[0:split_fd]
			train_y_fd = y_train_fd[0:split_fd]
			test_fd = x_train_fd[split_fd:]
			test_y_fd = y_train_fd[split_fd:]
			train_set_fd = lgb.Dataset(train_fd, label = train_y_fd, free_raw_data=False)
			test_set_fd = lgb.Dataset(test_fd, label = test_y_fd, free_raw_data=False)
			if i==0:
				lgb_model = lgb.train(self.lgb_params, train_set,keep_training_booster=True,
				num_boost_round=200,verbose_eval = 5,valid_sets=test_set,early_stopping_rounds= 100)
				lgb_model_fd = lgb.train(self.lgb_params, train_set_fd,keep_training_booster=True,
				num_boost_round=200,verbose_eval = 5,valid_sets=test_set_fd,early_stopping_rounds= 100)
			else:
				lgb_model = lgb.train(self.lgb_params, train_set,keep_training_booster=True,init_model=lgb_model,
				num_boost_round=200,verbose_eval = 5,valid_sets=test_set,early_stopping_rounds= 100)
				lgb_model_fd = lgb.train(self.lgb_params, train_set_fd,keep_training_booster=True,init_model=lgb_model_fd,
				num_boost_round=200,verbose_eval = 5,valid_sets=test_set_fd,early_stopping_rounds= 100)
			print("done!!!!!!!")
		lgb_model.save_model('model.txt')
		lgb_model_fd.save_model('model_fd.txt')

	def concat_feature(self,feature, train_label,fd=0):
	    train_data= pd.merge(left=feature, right=train_label, left_on='address', right_on='address', how='inner')
	    fishing_node = train_data[train_data['label'] == 1].sample(n=200)
	    common_node = train_data[train_data['label'] == 0].sample(n=1000)
	    common_node_list=[]
	    for i in range(0,5):
	    	common_node_list.append(common_node[200*i:199+200*i])
	    train_list=[]
	    train_list_y=[]
	    for i in range(0,5):
	    	train_list.append(pd.concat([fishing_node, common_node_list[i]]))
	    	train_list[i]=train_list[i].sample(frac=1)
	    	train_list_y.append(train_list[i]['label'])
	    	train_list[i]= train_list[i].drop(['address', 'label'], axis=1)
	    	if fd==1:
	    		train_list[i].drop(['from_in_sum_sum',
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
		       'in_nunique', 'in_count_nunique_ratio', 'in_count_nunique_equal'],axis=1,inplace=True)
	    return train_list, train_list_y
	def get_node_feature(self,train_data):
		#*
	    from_block_feature = train_data.groupby(['from'])['blockNumber'].agg([np.ptp, 'std'])
	    from_block_feature=from_block_feature.add_prefix('from_block_')
	    from_value_feature = train_data.groupby(['from'])['value'].agg(['sum', 'mean', 'std', 'max', 'min'])
	    from_value_feature=from_value_feature.add_prefix('from_value_')
	    from_feature = pd.concat([from_block_feature, from_value_feature], axis = 1)  

	    to_block_feature = train_data.groupby(['to'])['blockNumber'].agg([np.ptp, 'std'])
	    to_block_feature=to_block_feature.add_prefix('to_block_')
	    to_value_feature = train_data.groupby(['to'])['value'].agg(['sum', 'mean', 'std', 'max', 'min'])
	    to_value_feature=to_value_feature.add_prefix('to_value_')
	    to_feature = pd.concat([to_block_feature, to_value_feature], axis = 1)

	    from_feature.reset_index(inplace=True)
	    to_feature.reset_index(inplace=True)
	    temp_feature = pd.merge(left=from_feature, right=to_feature, left_on='from', right_on='to', how='inner')
	    temp_feature['address'] = temp_feature['from']
	    temp_feature.drop(['from', 'to'], axis = 1, inplace=True)
	    return temp_feature
	def get_net_feature(self,train_data):
		#*
		from_to_one_degree_feature = train_data.groupby(['from'])['to'].agg(['count', 'nunique'])
		from_to_one_degree_feature=from_to_one_degree_feature.add_prefix('from_to_').reset_index()
		from_to_one_degree_feature['from_to_count_nunique_ratio'] = from_to_one_degree_feature['from_to_count'] / from_to_one_degree_feature['from_to_nunique']
		from_to_one_degree_feature['from_to_count_nunique_equal'] = (from_to_one_degree_feature['from_to_count'] == from_to_one_degree_feature['from_to_nunique']).astype(int)
		from_to_two_degree_feature = train_data.groupby(['from', 'to'])['value'].agg(['sum', 'mean', 'max', 'min']).groupby(['from']).agg(
		['sum', 'std', 'median', 'max', 'min']).add_prefix('from_to_')
		from_to_two_degree_feature = pd.DataFrame(from_to_two_degree_feature.to_records(), index=None)
		from_to_net_feature =  from_to_two_degree_feature.merge(right=from_to_one_degree_feature, left_on='from', right_on='from', how='inner')                                             
	       
		to_from_one_degree_feature = train_data.groupby(['to'])['from'].agg(['count', 'nunique'])
		to_from_one_degree_feature=to_from_one_degree_feature.add_prefix('to_from_').reset_index()
		to_from_one_degree_feature['to_from_count_nunique_ratio'] = to_from_one_degree_feature['to_from_count'] / to_from_one_degree_feature['to_from_nunique']
		to_from_one_degree_feature['to_from_count_nunique_equal'] = (to_from_one_degree_feature['to_from_count'] == to_from_one_degree_feature['to_from_nunique']).astype(int)  
		to_from_two_degree_feature = train_data.groupby(['to', 'from'])['value'].agg(['sum', 'mean', 'max', 'min']).groupby(['to']).agg(
		['sum', 'std', 'median', 'max', 'min']).add_prefix('to_from_')
		to_from_two_degree_feature = pd.DataFrame(to_from_two_degree_feature.to_records(), index=None)
		to_from_net_feature =  to_from_two_degree_feature.merge(right=to_from_one_degree_feature, left_on='to', right_on='to', how='inner')
		return from_to_net_feature, to_from_net_feature
	def get_feature(self,train_data):
	    node_feature = self.get_node_feature(train_data)
	    from_to_net_feature, to_from_net_feature = self.get_net_feature(train_data)
	    feature = node_feature.merge(right=from_to_net_feature, left_on='address', right_on='from', how='left')
	    feature = feature.merge(right=to_from_net_feature, left_on='address', right_on='to',how='left')
	    feature.drop(['from','to'], inplace=True, axis = 1)
	    return feature
	def deal_feature_name(self,x):
		#*
	    if x.count('from_to_') == 2:
	        return 'from_in_' + x[1:-1].replace('from_to_', '').replace(',', '').replace('\'', '').replace(' ', '_')
	    if x.count('to_from_') == 2:
	        return 'to_out_' + x[1:-1].replace('to_from_', '').replace(',', '').replace('\'', '').replace(' ', '_')
	    if x.count('from_to_') == 1:
	        return x.replace('from_to', 'out')
	    if x.count('to_from_') == 1:
	        return x.replace('to_from', 'in')
	    if (x.count('block') == 1 or x.count('value') == 1):
	        return x.replace('from_block', 'out_block').replace('from_value', 'out_value').replace('to_block', 'in_block').replace('to_value', 'in_value')
	    return x
if __name__ == '__main__':
	#train_data = pd.read_csv('./train_data.csv')
	#train_label = pd.read_csv('./train_label.csv')
	#model=Model(train_data,train_label)
	#train_list,train_list_y,train_list_fd,train_list_y_fd=model.init_train_data()
	#model.model_train(train_list,train_list_y,train_list_fd,train_list_y_fd)