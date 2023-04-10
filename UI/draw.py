import networkx as nx
import matplotlib.pyplot as plt
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