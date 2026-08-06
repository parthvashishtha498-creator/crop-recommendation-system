from django.test import TestCase

# Create your tests here.
import joblib
import numpy as np

model = joblib.load(r"C:\crop_site\recommender\ml\Crop_Recommendation_model.pkl")

sample1 = np.array([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]])
sample2 = np.array([[22, 36, 16, 30.5, 35.0, 6.8, 50.0]])

print(model.predict(sample1))
print(model.predict(sample2))