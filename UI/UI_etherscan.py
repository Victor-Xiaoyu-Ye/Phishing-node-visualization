import tkinter as tk
from abc import abstractmethod
import csv
import pandas as pd
from json import dump
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import requests as r
from tkinter import scrolledtext
import tkinter.messagebox
import networkx as nx
import matplotlib.pyplot as plt
class GUI_begain():
    def __init__(self,master):
        self.root = master
       # self.root.config()#设置主题
        self.root.title('钓鱼节点查询')
        self.root.geometry('400x400')
        self.canvas = tk.Canvas(self.root,width=400,height=400,bd=0, highlightthickness=0)
        # imgpath = '1.png'
        # img = Image.open(imgpath)
        # photo = ImageTk.PhotoImage(img)
        # self.canvas.create_image(400, 400, image=photo)
        # self.canvas.grid()
        # self.canvas.create_window(200,100,width=200,height=60)
        # imgpath = '1.png'
        # img = Image.open(imgpath)
        # img = img.resize((400, 400))
        # photo = ImageTk.PhotoImage(img)
        # text = tk.Label(self.root, image=photo, compound='bottom')
        # text.grid()
        screenWidth = self.root.winfo_screenwidth()  # 获取显示区域的宽度
        screenHeight = self.root.winfo_screenheight()  # 获取显示区域的高度
        width = 450  # 设定窗口宽度
        height = 400  # 设定窗口高度
        left = (screenWidth - width) / 2
        top = (screenHeight - height) / 4
        self.root.geometry("%dx%d+%d+%d" % (width, height, left, top))
        GUI_node_input(self.root)

class GUI_node_input():
    def __init__(self,master):
        self.master = master    #窗口
        #建立一个组件
        # self.back = tk.Frame(self.master)
        # self.back.grid()
        # photo = ImageTk.PhotoImage(file='1.png')
        # theLabel = tk.Label(self.master, image=photo, compound=tk.CENTER)
        # theLabel.grid(padx=100,pady=100)
        self.initface = tk.Frame(self.master)
        self.initface.grid()
        button1 = tk.Button(self.initface, text='本地查询', command=lambda:self.change1(), width=8, height=2)
        button1.grid(padx=250,pady=200)
        button2 = tk.Button(self.initface, text='数据库查询', command=lambda: self.change2(), width=8, height=2)
        button2.place(x=120, y=200)
        text = tk.Label(self.initface, bd=5, fg='black', text='请输入要查询的节点')
        text.place(x=30, y=75)  # 文本框的创建
        text = tk.Label(self.initface, bd=5, fg='black', text='输入节点示例：0x037686814eff0f3b8c96a235a3f77e6e8e3aecb8')
        text.place(x=30, y=100)  # 文本框的创建
        self.entry = tk.Entry(self.initface, width=40)
        self.entry.place(x=150, y=80)
        # self.master.mainloop()
    def change1(self):
        node = self.entry.get()
        # print(node)
        self.initface.destroy()
        GUI_judge_localquery(self.master , node)
    def change2(self):
        node = self.entry.get()
        # print(node)
        self.initface.destroy()
        GUI_judge_databasequery(self.master, node)

class GUI_judge_databasequery():
    def __init__(self,master,node):
        self.master = master
        self.node = node
        self.get_data_fromdb(self.node)
        if self.mark == -1:
            tkinter.messagebox.showerror('Error', 'Unable to connect to the database', parent=self.master)
            self.back()
        if self.mark == 0:
            tkinter.messagebox.showinfo('Message', 'Successful connection to the database', parent=self.master)
            self.face1 = tk.Frame(self.master)
            self.face1.grid()
            button = tk.Button(self.face1, text='返回', command=lambda: self.back1(), width=8, height=2)
            button.grid(padx=190, pady=200)
            text = tk.Label(self.face1, bd=6, fg='red', text='Sorry, the node is not found', font=('宋体', 15))
            text.place(x=85, y=75)  # 文本框的创建

        if self.mark == 1:
            tkinter.messagebox.showinfo('Message', 'Successful connection to the database', parent=self.master)
            ##有关节点的信息
            self.face2 = tk.Frame(self.master, width=400, height=400)
            self.face2.grid()
            button1 = tk.Button(self.face2, text='返回', command=lambda: self.back2(), width=8, height=2)
            button1.place(x=100, y=300)
            button2 = tk.Button(self.face2, text='显示交易图谱', command=lambda: self.drawing(self.list_all,self.node), width=10, height=2)
            button2.place(x=250, y=300)
            text1 = tk.Label(self.face2, bd=5, fg='black', text='您选择查询的节点:')
            text1.place(x=30, y=15)  # 文本框的创建
            text2 = tk.Label(self.face2, bd=5, fg='black', text=self.node, bg='white')
            text2.place(x=30, y=35)  # 文本框的创建
            text3 = scrolledtext.ScrolledText(self.face2, width=43, height=10, bd=2, fg='black', bg='white')
            text3.insert("insert", self.result)
            text3.place(x=30, y=125)
            if self.mark1 == 1:
                text4 = tk.Label(self.face2, bd=5, fg='red', text='该 节 点 为 钓 鱼 节 点')
                text4.place(x=100, y=75)
            if self.mark1 == 0:
                text4 = tk.Label(self.face2, bd=5, fg='black', text='该 节 点 为 非 钓 鱼 节 点')
                text4.place(x=100, y=75)
            text5 = tk.Label(self.face2, bd=5, fg='black', text='交易数据如下')
            text5.place(x=30, y=96)

    def drawing(self,input_list, address):
        g = nx.DiGraph()
        node_list = []
        color_list = []
        for tup in input_list:
            node_list.append([tup[0], tup[2]])
            node_list.append([tup[1], tup[3]])
        #print(node_list)
        new_list = []
        for item in node_list:
            if item not in new_list:
                new_list.append(item)
        node_list = new_list
        for item in node_list:
            item_cut = item[0][0:10] + ".."
            g.add_node(item_cut)
            if item[1] == 0:
                color_list.append('b')
            else:
                color_list.append('r')
        for tup in input_list:
            g.add_edge(tup[0][0:10] + "..", tup[1][0:10] + "..")
        nx.draw(g,
                with_labels=True,
                # pos = nx.sprint_layout(g),
                # edge_color='k',
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
            label="The Relationship Of Node  " + address, x=0.5, y=0.5,
            fontdict={
                "fontsize": 8,
                "color": "white",
                "family": "Times New Roman",
                "fontweight": "black",
                "fontstyle": "italic",
                "verticalalignment": "center",
                "horizontalalignment": "center",
                "rotation": 0,
                "alpha": 1,
                "backgroundcolor": "black",

                "bbox": {
                    "boxstyle": "round",
                    "facecolor": "black",
                    "edgecolor": "red",
                },
            },
        )
        plt.show()

    def back(self):
        GUI_node_input(self.master)

    def back1(self):
        self.face1.destroy()
        GUI_node_input(self.master)

    def back2(self):
        self.face2.destroy()
        GUI_node_input(self.master)

    def get_data_fromdb(self,address):
        try:
            g = Graph('bolt://localhost:7687', auth=("neo4j", "bao20011127"), secure=False)
        except:
            self.mark = -1
            return
        cql_str = "match(n1)-[r]->(n2) where n1.name='" + address + "'or n2.name='" + address + "'return n1,n2"
        result = g.run(cql_str)
        list_all = []
        for item in result:
            temp_list = []
            f_node = str(item[0]).split("'")[1]
            temp_list.append(f_node)
            t_node = str(item[1]).split("'")[1]
            temp_list.append(t_node)
            if str(item[0]).split(":")[1][0] == 'n':
                temp_list.append(0)
            else:
                temp_list.append(1)
            if str(item[1]).split(":")[1][0] == 'n':
                temp_list.append(0)
            else:
                temp_list.append(1)
            list_all.append(tuple(temp_list))
        self.list_all = list_all
        if len(list_all) == 0:
            self.mark = 0
        if len(list_all) >0 :
            self.mark = 1
            list1 = list_all[0]
            if (list1[0] == address):
                self.mark1 = list1[2]
            if (list1[1] == address):
                self.mark1 = list1[3]
        # print(self.mark1)
            self.result = ''
            k = 0
            for i in list_all:
                i = list(i)
                # print(type(i))
                k = k + 1
                k1 = str(k)
                self.result = self.result + '第' + k1 + '条交易' + '\n'
                k2 = 0
                for j in i:
                    j = str(j)
                    k2 = k2 + 1
                    if (j == '0'):
                        if (k2 == 3):
                            self.result = self.result + '第一个节点为非钓鱼节点' + '\n'
                            continue
                        if (k2 == 4):
                            self.result = self.result + '第二个节点为非钓鱼节点' + '\n'
                            continue
                    if (j == '1'):
                        if (k2 == 3):
                            self.result = self.result + '第一个节点为钓鱼节点' + '\n'
                        if (k2 == 4):
                            self.result = self.result + '第二个节点为钓鱼节点' + '\n'
                    else:
                        self.result = self.result + ' ' + j
                self.result = self.result + '\n'

class GUI_judge_localquery():
    def __init__(self,master,node):
        self.master = master
        self.node = node
        # print(node)
        self.get_data_fromcsv(self.node)
        if self.mark == 0:
            self.face1 = tk.Frame(self.master)
            self.face1.grid()
            button = tk.Button(self.face1, text='返回', command=lambda: self.back1(), width=8, height=2)
            button.grid(padx=190, pady=200)
            text = tk.Label(self.face1, bd=6, fg='red', text='Sorry, the node is not found',font=('宋体',15) )
            text.place(x=85, y=75)  # 文本框的创建
        if self.mark == 1:
            ##有关节点的信息
            self.face2 = tk.Frame(self.master,width=400,height=400)
            self.face2.grid()
            button1 = tk.Button(self.face2, text='返回', command=lambda: self.back2(), width=8, height=2)
            button1.place(x=100, y=300)
            button2 = tk.Button(self.face2, text='显示交易图谱', command=lambda: self.drawing(self.list_all,self.node), width=10, height=2)
            button2.place(x=250, y=300)
            text1 = tk.Label(self.face2, bd=5, fg='black', text='您选择查询的节点:')
            text1.place(x=30, y=15)  # 文本框的创建
            text2 = tk.Label(self.face2, bd=5, fg='black', text=self.node, bg = 'white')
            text2.place(x=30, y=35)  # 文本框的创建
            text3 = scrolledtext.ScrolledText(self.face2,width=43, height=10,bd=2,fg='black',bg='white')
            text3.insert("insert",self.result)
            text3.place(x=30,y=125)
            if self.mark1 == 1:
                text4 = tk.Label(self.face2, bd=5, fg='red', text='该 节 点 为 钓 鱼 节 点')
                text4.place(x=100, y=75)
            if self.mark1 == 0:
                text4 = tk.Label(self.face2, bd=5, fg='black', text='该 节 点 为 非 钓 鱼 节 点')
                text4.place(x=100, y=75)
            text5 = tk.Label(self.face2, bd=5, fg='black', text='交易数据如下')
            text5.place(x=30, y=96)

    def drawing(self,input_list, address):
        g = nx.DiGraph()
        node_list = []
        color_list = []
        for tup in input_list:
            node_list.append([tup[0], tup[2]])
            node_list.append([tup[1], tup[3]])
        #print(node_list)
        new_list = []
        for item in node_list:
            if item not in new_list:
                new_list.append(item)
        node_list = new_list
        for item in node_list:
            item_cut = item[0][0:10] + ".."
            g.add_node(item_cut)
            if item[1] == 0:
                color_list.append('b')
            else:
                color_list.append('r')
        for tup in input_list:
            g.add_edge(tup[0][0:10] + "..", tup[1][0:10] + "..")
        nx.draw(g,
                with_labels=True,
                # pos = nx.sprint_layout(g),
                # edge_color='k',
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
            label="The Relationship Of Node  " + address, x=0.3, y=0.18,
            fontdict={
                "fontsize": 8,
                "color": "white",
                "family": "Times New Roman",
                "fontweight": "black",
                "fontstyle": "italic",
                "verticalalignment": "center",
                "horizontalalignment": "center",
                "rotation": 0,
                "alpha": 1,
                "backgroundcolor": "black",

                "bbox": {
                    "boxstyle": "round",
                    "facecolor": "black",
                    "edgecolor": "red",
                },
            },
        )
        plt.show()

    def back1(self):
        self.face1.destroy()
        GUI_node_input(self.master)
    def back2(self):
        self.face2.destroy()
        GUI_node_input(self.master)

    def get_data_fromcsv(self,address):
        # data=pd.read_csv("./predict_data")
        label = pd.read_csv('predict_label.csv')
        # print(label["address"])
        address = address
        if (address not in list(label["address"])):
            self.mark = 0
            #print(self.mark)
        else:
            self.mark = 1
            data = pd.read_csv('predict_data.csv')
            data_to = data[data['to'] == address]
            data_from = data[data['from'] == address]
            search_data = pd.concat([data_from, data_to])
            search_data.drop_duplicates()
            # return list(search_data['from']),list(search_data['to'])
            list_all = []
            for i1, i2 in zip(list(search_data['from']), list(search_data['to'])):
                temp_list = []
                temp_list.append(i1)
                temp_list.append(i2)
                if i1 not in list(label["address"]):
                    temp_list.append(0)
                else:
                    temp_list.append(list(label[label["address"] == i1]['label'])[0])
                if i2 not in list(label["address"]):
                    temp_list.append(0)
                else:
                    temp_list.append(list(label[label["address"] == i2]['label'])[0])
                list_all.append(temp_list)
                #print(type(list_all))
            self.list_all = list_all
            list1 = list_all[0]
            if(list1[0] == address):
                self.mark1 = list1[2]
            if (list1[1] == address):
                self.mark1 = list1[3]
            #print(self.mark1)
            self.result=''
            k = 0
            for i in list_all:
                i = list(i)
                #print(type(i))
                k = k + 1
                k1 = str(k)
                self.result=self.result+'第'+k1+'条交易'+'\n'
                k2 = 0
                for j in i:
                    j = str(j)
                    k2 = k2 + 1
                    if(j == '0'):
                        if(k2==3):
                            self.result = self.result+'第一个节点为非钓鱼节点'+'\n'
                            continue
                        if(k2 == 4):
                            self.result = self.result + '第二个节点为非钓鱼节点'+'\n'
                            continue
                    if(j == '1'):
                        if(k2 == 3):
                            self.result = self.result + '第一个节点为钓鱼节点'+'\n'
                        if(k2 == 4):
                            self.result = self.result + '第二个节点为钓鱼节点'+'\n'
                    else:
                        self.result =self.result+' '+j
                self.result=self.result+'\n'
            #print(self.result)

if __name__ == '__main__':
    root = tk.Tk()
    GUI_begain(root)
    root.mainloop()


