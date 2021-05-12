from flask import Flask, redirect, url_for, request, send_file, render_template, Response

import glob

import os
import pandas as pd
import numpy as np
import re
from flaskext.mysql import MySQL
import pymysql
import io
import csv


app = Flask(__name__)

#Database Configuration
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'userdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/")
def index():
   return render_template('new.html')



@app.route('/table',methods = ['POST', 'GET'])
def new():
    #print("entered 0")
    if request.method == 'POST':
        global df
        global description
        global flag
        if request.files:
            file= request.files['csv']
            description = request.form['description']
            
            #save_loc = r'//home//rohit//Desktop//Coneio//tagging_utility//'
            #out_loc = r'//home//rohit//Desktop//Coneio//tagging_utility//outputs'
            # save_loc = r'C:\Users\\Administrator\Documents\update_description\static\file\uploads\\'
            # out_loc =  r'C:\Users\\Administrator\Documents\update_description\static\file\output\\'
            # file.save(save_loc+file.filename)
        fname= file.filename
        if fname[-3:]=='csv':
            df1 = pd.read_csv(file)
        elif fname[-4:]=='xlsx':
            df1 = pd.read_excel(file)
        else :
            return render_template("new.html")
        # df1 =  process1(df[["hsn","description"]])
        # df = df1[["hsn","updated_description"]]
        # df.columns= ["hsn","description"]
        # df= pd.read_excel(save_loc+file.filename)
        # t = [""]*df.shape[0]
        # print(t)
        df = pd.DataFrame()
        try:
            df['hsn'] = df1['hsn'].values
        except:
            df['hsn'] = df1['HSN_Code'].values
        
        try:
            df['description'] = df1['description'].values 
        except:
            df['description'] = df1['Description'].values

        df["user_description"] = [description]*df.shape[0]
        # df['tags'] = t
        
        # df =  tagging(save_loc+file.filename, [description]).get_final_result()
        # df.to_excel(out_loc+'final.xlsx', index= False)
        # df1.to_excel(out_loc+'Quantity.xlsx', index=False)
        return render_template("table.html",df = df ) 
    else:
        return render_template("new.html")

@app.route('/labels',methods = ['POST', 'GET'])
def table():
    #print("entered 0")
    labels = []
    if request.method == 'POST':
        for i in range(df.shape[0]):
            if request.form.get(df.iloc[i][1]) == 'True':
                labels.append(1)
            else:
                labels.append(0)
        df['labels'] = labels
        flag=0
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        string_ints = [str(int) for int in df['labels']]
        slabel = "".join(string_ints)
        cursor.execute("SELECT Description FROM details")
        rows = cursor.fetchall()
        length = len(rows)
        
        if( description in rows):
            sql ="REPLACE INTO details (Id, HSN_Code, Description, Labels) VALUES (%s, %s, %s, %s)"
            val = (length, df['hsn'][0], df['user_description'][0], slabel)
            cursor.execute(sql, val)
            conn.commit()

        else:
            sql ="INSERT INTO details (Id, HSN_Code, Description, Labels) VALUES (%s, %s, %s, %s)"
            val = (length+1, df['hsn'][0], df['user_description'][0], slabel)
            cursor.execute(sql, val)
            flag=1
            conn.commit()
            

        return render_template('labels.html', df = df)
    else:
        return render_template("table.html",df = df )

@app.route('/labels',methods = ['POST', 'GET'])
def label():
    #print("entered 0")  
    if request.method == 'POST':      
        return render_template('new.html')
    else:
        return render_template("label.html")


@app.route('/download/report/csv')
def download_report():

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)


    cursor.execute("SELECT Id, HSN_Code, Description, Labels FROM details")
    #cursor.execute( %(title, content))
    result = cursor.fetchall()
    #sql ="INSERT INTO details (id, HSN_Code, Description) VALUES (%s, %s, %s)"
    #val = ("844.40", "DC motor")
    #mycursor.execute(sql, val)
    output = io.StringIO()
    writer = csv.writer(output)
    line = ['Id', 'HSN_Code, Description', 'Labels']
    writer.writerow(line)
    for row in result:
     line = [str(row['Id']) + ',' + row['HSN_Code'] + ',' + row['Description'] + ',' + row['Labels']]
     writer.writerow(line)
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=employee_report.csv"})
        
@app.route('/return-files/<filename>')
def return_files_tut(filename):
    x=filename
    out_loc =  out_loc =  r'C:\Users\dell\Downloads'
    file_path = out_loc + filename
    return Response(
       df.to_csv(),
       mimetype="text/csv",
       headers={"Content-disposition":
       f"attachment; filename={x}.csv"})
    # return send_file(file_path, as_attachment=True, attachment_filename='')


# Download API
#@app.route('/return-files/<filename>')
#def return_files_tut(filename):
#    out_loc =  out_loc =  r'C:\Users\\Administrator\Documents\update_description\static\file\output\\'
#    file_path = out_loc + filename
#    return send_file(file_path, as_attachment=True, attachment_filename='')
#
if __name__ == '__main__':
   
   app.run(debug = True)      
