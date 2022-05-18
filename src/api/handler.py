# importando bibliotecas
from flask import Flask, request, Response
from rossmann import RossmannPipeline
import joblib
import pandas as pd

# carregando em memória o modelo serializado
modelo = joblib.load('..\..\models\modelo.pkl')

# instanaciando a variável com o app do flask
app = Flask(__name__)

# definindo o endpoint das predições
@app.route('/rossmann/predict', methods=['POST'])

# definindo a função preditora
def rossmann_predict():
    teste_json = request.get_json()

    if teste_json: # se houver dados
        if isinstance(teste_json, dict): # exemplo único
            df_raw = pd.DataFrame(teste_json, index=[0])
        else: # múltiplos exemplos
            df_raw = pd.DataFrame(teste_json, columns=teste_json[0].keys())
        
        # instanciando a classe que contém todo o pipeline realizado do projeto
        pipeline = RossmannPipeline()

        # data cleaning
        df1 = pipeline.data_cleaning(df_raw)

        # feature engineering
        df2 = pipeline.feature_engineering(df1)

        # data preprocessing
        df3 = pipeline.data_preprocessing(df2)

        # predição
        df_response = pipeline.get_prediction(modelo, df_raw, df3)

        return df_response
    else:
        return Response('{}', status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='192.168.0.17', port=5000, debug=True)
