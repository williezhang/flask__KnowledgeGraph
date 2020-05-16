#!/usr/bin/env python
# coding=utf-8

import os
from random import choice
from flask import Flask, request, Response, render_template,jsonify,redirect,url_for



def process(x):
    ret1={
			  "nodes": 
                  [{"name": '操作系统集团',"category": 0}, {"name": '浏览器有限公司',"category": 0}, 
                   {"name": 'HTML科技',"category": 0}, {"name": 'JavaScript科技',"category": 0}, 
                   {"name": 'CSS科技',"category": 0}, {"name": 'Chrome',"category": 1},
                   {"name": 'IE',"category": 1}, {"name": 'Firefox',"category": 1},
                   {"name": 'Safari',"category": 1}],			  
			  "links": [{"source": '浏览器有限公司',"target": '操作系统集团',"name": '参股'}, 
                       {"source": 'HTML科技',"target": '浏览器有限公司',"name": '参股'},
                       {"source": 'CSS科技',"target": '浏览器有限公司',"name": '参股'}, 
                       {"source": 'JavaScript科技',"target": '浏览器有限公司',"name": '参股'}, 
                       {"source": 'Chrome',"target": '浏览器有限公司',"name": '董事'}, 
                       {"source": 'IE',"target": '浏览器有限公司',"name": '董事'},
                       {"source": 'Firefox',"target": '浏览器有限公司',"name": '董事'}, 
                       {"source": 'Safari',"target": '浏览器有限公司',"name": '董事'}, 
                       {"source": 'Chrome',"target": 'JavaScript科技',"name": '法人'}]
			}
    ret2={
			  "nodes": 
                  [{"name": '操作系统集团',"category": 0}, {"name": '浏览器有限公司',"category": 0}],			  
			  "links": [{"source": '浏览器有限公司',"target": '操作系统集团',"name": '参股'}]
			}
    
    return choice([ret1,ret2])


def process_xiazuan(x):
    if x=='操作系统集团' or x=='浏览器有限公司':
        return {
			  "nodes": 
                  [{"name": '操作系统集团',"category": 0}, {"name": '浏览器有限公司',"category": 0}],			  
			  "links": [{"source": '浏览器有限公司',"target": '操作系统集团',"name": '参股'}]
			}
    if x=='HTML科技':
        return {
			  "nodes": 
                  [{"name": 'HTML科技',"category": 0}, {"name": 'JavaScript科技',"category": 0},
                   {"name": '浏览器有限公司',"category": 0}],			  
			  "links": [{"source": 'HTML科技',"target": '浏览器有限公司',"name": '参股'}]
			}
    else:
        return {
			  "nodes": 
                  [{"name": 'HTML科技',"category": 0}, {"name": 'JavaScript科技',"category": 0},
                  {"name": '浏览器有限公司',"category": 0}],			  
			  "links": [{"source": 'HTML科技',"target": '浏览器有限公司',"name": '参股'}]
			}

def process_shangjuan(x):
    return 





app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    '''
    初始界面:文件上传界面
    '''
    return render_template('index.html')


@app.route('/click/', methods=['GET'])
def click():
    '''
    跳转界面:搜索界面
    '''
    return render_template('search.html')


@app.route('/search_input/', methods=['GET', 'POST'])
def search_input():
    '''
    前后端交互：前端搜索框传来的数据，
    ret待process函数解析并处理为json格式数据
    '''    
    ret=  request.args.getlist('name')[0]
    print('ret',ret)
    return jsonify(process(ret))


  
@app.route('/xiazuan/', methods=['GET', 'POST'])
def xiazuan():
    '''
    前后端交互：下钻选择的节点，双击该节点完成下钻
    ret待process_xiazuan函数解析并处理为json格式数据
    '''        
    ret=  request.args.getlist('name')
    print('ret',ret)
    xiazuan_node=ret[1]
    return jsonify(process_xiazuan(xiazuan_node))
 
    


@app.route('/shangjuan/', methods=['GET', 'POST'])
def shangjuan():
    '''
    前后端交互：上卷选择的节点，单击该节点完成下钻
    ret待process_shangjuan函数解析并处理为json格式数据
    '''        
    ret=  request.args.getlist('name')
    print('ret',ret)
    xiazuan_node=ret[1]
    return jsonify(process_shangjuan(xiazuan_node))   
    



@app.route('/checkChunk', methods=['POST'])
def checkChunk():
    return jsonify({'ifExist':False})


@app.route('/mergeChunks', methods=['POST'])
def mergeChunks():
    fileName=request.form.get('fileName')
    print(fileName)
    md5=request.form.get('fileMd5')
    chunk = 0  # 分片序号
    with open(u'./upload/{}'.format(fileName), 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = './upload/{}-{}'.format(md5, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except:
                break
            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间
    return jsonify({'upload':True})


@app.route('/upload', methods=['POST'])
def upload():  # 接收前端上传的一个分片
    md5=request.form.get('fileMd5')
    chunk_id=request.form.get('chunk',0,type=int)
    filename = '{}-{}'.format(md5,chunk_id)
    upload_file = request.files['file']
    upload_file.save('./upload/{}'.format(filename))
    return jsonify({'upload_part':True})



@app.route('/file/list', methods=['GET'])
def file_list():
    files = os.listdir('./upload/')  # 获取文件目录
   # files = map(lambda x: x if isinstance(x, unicode) else x.decode('utf-8'), files)  # 注意编码
    return render_template('./list.html', files=files)


@app.route('/file/download/<filename>', methods=['GET'])
def file_download(filename):
    def send_chunk():  # 流式读取
        store_path = './upload/%s' % filename
        with open(store_path, 'rb') as target_file:
            while True:
                chunk = target_file.read(20 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk

    return Response(send_chunk(), content_type='application/octet-stream')


if __name__ == '__main__':
    app.run(debug=False, threaded=True,port=5000)
