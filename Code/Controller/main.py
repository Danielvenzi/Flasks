from flask import Flask, request, jsonify, redirect, url_for

app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

@app.route('/register',methods=['POST'])
def registApi():
    data = request.data
    print("Dados do post: {}, Endereço de origem: {}".format(data,request.remote_addr))

    key = "da7d87ad8ya87dggairuia3rga"
    return jsonify({"Controller Key": key})

@app.route('/unregister',methods=['POST'])
def unregisterApi():
    data = request.data
    print("Ddados do post: {}, Endereço de origem: {}".format(data,request.remote_addr))

    return "Success"

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=80)