import sys
from dataclasses import dataclass

import numpy as np 
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging
import os

from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts',"preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

        # ✅ DEFINE ONCE (no duplication mistake)
        self.numerical_columns = ["writing_score", "reading_score"]
        self.categorical_columns = [
            "gender",
            "race_ethnicity",
            "parental_level_of_education",
            "lunch",
            "test_preparation_course",
        ]
        self.target_column = "math_score"

    def get_data_transformer_object(self):
        try:
            num_pipeline= Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="median")),
                ("scaler",StandardScaler())
                ]
            )

            cat_pipeline=Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="most_frequent")),
                ("one_hot_encoder",OneHotEncoder(handle_unknown="ignore")),  # ✅ important fix
                ("scaler",StandardScaler(with_mean=False))
                ]
            )

            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,self.numerical_columns),
                ("cat_pipelines",cat_pipeline,self.categorical_columns)
                ]
            )

            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_data_transformation(self,train_path,test_path):

        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            # ✅ STRONG NORMALIZATION (handles space + / + any special char)
            train_df.columns = (
                train_df.columns
                .str.strip()
                .str.lower()
                .str.replace(r"[^a-z0-9]+", "_", regex=True)
            )

            test_df.columns = (
                test_df.columns
                .str.strip()
                .str.lower()
                .str.replace(r"[^a-z0-9]+", "_", regex=True)
            )

            # ✅ DEBUG ONCE (remove later if you want)
            print("Columns:", train_df.columns.tolist())

            logging.info("Read train and test data completed")
            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()

            # ✅ VALIDATION (this prevents silent crashes)
            required_cols = self.numerical_columns + self.categorical_columns + [self.target_column]
            missing_cols = [col for col in required_cols if col not in train_df.columns]

            if missing_cols:
                raise Exception(f"Missing columns: {missing_cols}")

            input_feature_train_df = train_df.drop(columns=[self.target_column])
            target_feature_train_df=train_df[self.target_column]

            input_feature_test_df = test_df.drop(columns=[self.target_column])
            target_feature_test_df=test_df[self.target_column]

            logging.info(
                "Applying preprocessing object on training and testing data."
            )

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[
                input_feature_train_arr, np.array(target_feature_train_df)
            ]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            raise CustomException(e,sys)