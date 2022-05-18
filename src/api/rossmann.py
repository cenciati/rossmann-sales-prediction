import os
import joblib
import pandas as pd
import numpy as np
import datetime
from inflection import underscore

class RossmannPipeline(object):
    def __init__(self):
        # definindo variável com o caminho padrão do projeto
        self.home_path = os.getcwd().replace('\\src\\api', '')
        
        # carregando o modelo
        self.model = joblib.load(self.home_path + '\\models\\modelo.pkl')
        
        # carregando parâmetros de pré-processamento
        ## minmax
        self.mms_promo_time_week = joblib.load(self.home_path + '\\parameters\\mms_promo_time_week.pkl')
        self.mms_year = joblib.load(self.home_path + '\\parameters\\mms_year.pkl')
        
        # robust
        self.rs_competition_distance = joblib.load(self.home_path + '\\parameters\\rs_competition_distance.pkl')
        self.rs_competition_time_month = joblib.load(self.home_path + '\\parameters\\rs_competition_time_month.pkl')


    def data_cleaning(self, df):
        # renomeando as colunas
        df.columns = [underscore(coluna) for coluna in df.columns]
        
        # tipo dos dados
        colunas_para_category = ['store', 'open', 'promo', 'state_holiday', 'school_holiday', 'store_type', 'assortment', 'promo2']
        df[colunas_para_category]= df[colunas_para_category].apply(lambda coluna: coluna.astype('category'))
        df['date'] = pd.to_datetime(df['date'])

        # dados faltantes
        df['competition_distance'] = df['competition_distance'].apply(lambda x: 200_000.0 if pd.isna(x) else x)
        df['competition_open_since_month'] = df.apply(lambda x: x['date'].month if pd.isna(x['competition_open_since_month']) else x['competition_open_since_month'], axis=1)
        df['competition_open_since_year'] = df.apply(lambda x: x['date'].year if pd.isna(x['competition_open_since_year']) else x['competition_open_since_year'], axis=1)
        df['promo2_since_week'] = df.apply(lambda x: x['date'].week if pd.isna(x['promo2_since_week']) else x['promo2_since_week'], axis=1)
        df['promo2_since_year'] = df.apply(lambda x: x['date'].year if pd.isna(x['promo2_since_year']) else x['promo2_since_year'], axis=1)
        df['promo_interval'].fillna(0, inplace=True)
        dic_month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        df['month_map'] = df['date'].dt.month.map(dic_month_map)
        df['is_promo'] = df[['promo_interval', 'month_map']].apply(lambda x: 0 if x['promo_interval'] == 0 else 1 if x['month_map'] in x['promo_interval'].split(',') else 0, axis=1)
        colunas_para_int = ['competition_open_since_month', 'competition_open_since_year', 'promo2_since_week', 'promo2_since_year']
        df[colunas_para_int]= df[colunas_para_int].apply(lambda coluna: coluna.astype('int64'))
        
        return df
    
    
    def feature_engineering(self, df):
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['week_of_year'] = df['date'].dt.weekofyear
        df['year_week'] = df['date'].dt.strftime('%Y-%W')
        
        df['competition_since'] = df.apply(lambda x: datetime.datetime(year=x['competition_open_since_year'], month=x['competition_open_since_month'], day=1), axis=1)
        df['competition_time_month'] = ((df['date'] - df['competition_since']) / 30).apply(lambda x: x.days).astype('int64')
        df['promo_since'] = df['promo2_since_year'].astype(str) + '-' + df['promo2_since_week'].astype(str)
        df['promo_since'] = df['promo_since'].apply(lambda x: datetime.datetime.strptime(x+'-1', '%Y-%W-%w') - datetime.timedelta(days=7))
        df['promo_time_week'] = ((df['date'] - df['promo_since']) / 7).apply(lambda x: x.days).astype('int64')
        
        df['assortment'] = df['assortment'].apply(lambda x: 'basic' if x=='a' else 'extra' if x=='b' else 'extended')
        df['state_holiday'] = df['state_holiday'].apply(lambda x: 'public_holiday' if x=='a' else 'easter_holiday' if x=='b' else 'christmas' if x=='c'else 'regular_day')

        colunas_dropar = ['open', 'promo_interval', 'month_map']
        df.drop(colunas_dropar, axis=1, inplace=True)
        
        return df
    
    
    def data_preprocessing(self, df):
        # min max        
        df.loc[:, 'promo_time_week'] = self.mms_promo_time_week.transform(df[['promo_time_week']])
        df.loc[:, 'year'] = self.mms_year.transform(df[['year']])
        
        # robust
        df.loc[:, 'competition_distance'] = self.rs_competition_distance.transform(df[['competition_distance']])
        df.loc[:, 'competition_time_month'] = self.rs_competition_time_month.transform(df[['competition_time_month']])
        
        # one-hot
        df = pd.get_dummies(df, columns=['state_holiday', 'store_type'])

        # ordinal
        df['assortment'] = df['assortment'].map({'basic': 1, 'extra': 2, 'extended': 3})

        # sin and cosine
        df['month_sin'] = df['month'].apply(lambda x: np.sin(x * (2. * np.pi/12)))
        df['month_cos'] = df['month'].apply(lambda x: np.cos(x * (2. * np.pi/12)))
        df['day_sin'] = df['day'].apply(lambda x: np.sin(x * (2. * np.pi/30)))
        df['day_cos'] = df['day'].apply(lambda x: np.cos(x * (2. * np.pi/30)))
        df['week_of_year_sin'] = df['week_of_year'].apply(lambda x: np.sin(x * (2. * np.pi/52)))
        df['week_of_year_cos'] = df['week_of_year'].apply(lambda x: np.cos(x * (2. * np.pi/52)))
        df['day_of_week_sin'] = df['day_of_week'].apply(lambda x: np.sin(x * (2. * np.pi/7)))
        df['day_of_week_cos'] = df['day_of_week'].apply(lambda x: np.cos(x * (2. * np.pi/7)))
        
        # feature selection
        colunas_finais = ['assortment', 'competition_distance', 'promo', 'store', 'competition_time_month',
                          'competition_open_since_month', 'competition_open_since_year', 'day_of_week_sin',
                          'day_of_week_cos', 'promo2_since_week', 'promo2_since_year']
        
        return df.loc[:, colunas_finais]
    
    
    def get_prediction(self, model, original_data, test_data):
        # predict
        y_hat = model.predict(test_data)

        # prediction column
        original_data['prediction'] = y_hat

        return original_data.to_json(orient='records', date_format='iso')
