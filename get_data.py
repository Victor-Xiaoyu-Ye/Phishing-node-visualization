import csv
import pandas as pd
from json import dump
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import requests as r
import networkx as nx
import matplotlib.pyplot as plt
def get_data_fromcsv(address):
	#data=pd.read_csv("./predict_data")
	label=pd.read_csv("./predict_label.csv")
	#print(label["address"])
	if(address not in list(label["address"])):
		return []
	else:
		data=pd.read_csv("./predict_data.csv")
		data_to=data[data['to']==address]
		data_from=data[data['from']==address]
		search_data=pd.concat([data_from,data_to])
		search_data.drop_duplicates()
		#return list(search_data['from']),list(search_data['to'])
		list_all=[]
		for i1,i2 in zip(list(search_data['from']),list(search_data['to'])):
			temp_list=[]
			temp_list.append(i1)
			temp_list.append(i2)
			if i1 not in list(label["address"]):
				temp_list.append(0)
			else:
				temp_list.append(list(label[label["address"]==i1]['label'])[0])
			if i2 not in list(label["address"]):
				temp_list.append(0)
			else:
				temp_list.append(list(label[label["address"]==i2]['label'])[0])
			list_all.append(tuple(temp_list))
		return list_all
	

def get_data_fromdb(address):
	try:
		g=Graph('bolt://localhost:7687',auth=("neo4j", "bao20011127"),secure=False)
	except:
		return "error"
	cql_str="match(n1)-[r]->(n2) where n1.name='"+address+"'or n2.name='"+address+"'return n1,n2"
	result=g.run(cql_str)
	list_all=[]
	for item in result:
		temp_list=[]
		f_node=str(item[0]).split("'")[1]
		temp_list.append(f_node)
		t_node=str(item[1]).split("'")[1]
		temp_list.append(t_node)
		if str(item[0]).split(":")[1][0]=='n':
			temp_list.append(0)
		else:
			temp_list.append(1)
		if str(item[1]).split(":")[1][0]=='n':
			temp_list.append(0)
		else:
			temp_list.append(1)
		list_all.append(tuple(temp_list))
	return list_all
def drawing(input_list,address):
	g=nx.DiGraph()
	node_list=[]
	color_list=[]
	for tup in input_list:
		node_list.append([tup[0],tup[2]])
		node_list.append([tup[1],tup[3]])
	print(node_list)
	new_list=[]
	for item in node_list:
		if item not in new_list:
			new_list.append(item)
	node_list=new_list
	for item in node_list:
		item_cut=item[0][0:10]+".."
		g.add_node(item_cut)
		if item[1]==0:
			color_list.append('b')
		else:
			color_list.append('r')
	for tup in input_list:
		g.add_edge(tup[0][0:10]+"..",tup[1][0:10]+"..")
	nx.draw(g,
		    with_labels=True,
		    #pos = nx.sprint_layout(g),
		    #edge_color='k',
		    node_color=color_list,
		    node_size=1400,
		    node_shape='o',
		    linewidths=2,
		    width=1.0,
		    alpha=0.55,
		    style='solid',
		    font_size=6,
		    font_color='k'
	)
	plt.title(
    label = "The Relationship Of Node  "+address,x=0.3,y=0.18,
    fontdict={
        "fontsize":8,  
        "color":"white",
        "family":"Times New Roman",    
        "fontweight":"black",           
        "fontstyle":"italic",           
        "verticalalignment":"center",   
        "horizontalalignment":"center", 
        "rotation":0, 
        "alpha":1,    
        "backgroundcolor":"black",
        
        "bbox":{
            "boxstyle":"round",  
            "facecolor":"black", 
            "edgecolor":"red", 
        	},
    	},
	)

	plt.show()
address="0x0084515449b037205a33d6d3940a5684126aa4b5"
drawing(get_data_fromcsv(address),address)
#print(from_list)	
#print(to_list)
#test_graph.run("UNWIND range(1, 3) AS n RETURN n, n * n as n_sq")
#print(g.schema.node_labels)
#g.run("MATCH (c:Customer) RETURN c.name")
#dumps(g.run("create (n:Person )").data())
#B = Node("Prson", name="buuulo")

#test_graph.create(B)
