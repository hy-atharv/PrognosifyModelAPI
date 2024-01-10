import json
import sklearn
import pickle
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

model = pickle.load(open('model2.pkl', 'rb'))


@app.route('/')
def home():
    return "API Server Running"


@app.route('/prognosify', methods=['GET', 'POST'])
def prognosis():
    """API Receiving Input from the endpoint and returning the Prognosis Data"""
    try:
        """API Receiving Input from the endpoint and returning the Prognosis Data"""
        fever = request.form.get('fever')
        cough = request.form.get('cough')
        fatigue = request.form.get('fatigue')
        diff_in_breathing = request.form.get('difficulty in breathing')
        age = request.form.get('age')
        gender = request.form.get('gender')
        blood_pressure = request.form.get('blood pressure')
        cholestrol_level = request.form.get('cholestrol level')

        input = {
            'Fever': fever,
            'Cough': cough,
            'Fatigue': fatigue,
            'Difficulty Breathing': diff_in_breathing,
            'Age': age,
            'Gender': gender,
            'Blood Pressure': blood_pressure,
            'Cholesterol Level': cholestrol_level,
        }

        model_input = preprocess_user_input(input)
        pred_dis = predict(model_input)
        dis_data = FetchData(pred_dis)
        result_dict = {'Results': dis_data.to_dict(orient='records')}
        result_json = jsonify(result_dict)

        return result_json

    except Exception as e:
        print(f"Error in API: {str(e)}")
        return "API Error"


def preprocess_user_input(user_input):
    """Preprocess user input to numeric values."""
    # Assuming user_input is a dictionary with keys as column names
    # Convert categorical values to numeric
    user_input['Fever'] = 1 if user_input['Fever'].lower() == 'yes' else 0
    user_input['Cough'] = 1 if user_input['Cough'].lower() == 'yes' else 0
    user_input['Fatigue'] = 1 if user_input['Fatigue'].lower() == 'yes' else 0
    user_input['Difficulty Breathing'] = 1 if user_input['Difficulty Breathing'].lower() == 'yes' else 0
    user_input['Gender'] = 1 if user_input['Gender'].lower() == 'male' else 0
    user_input['Blood Pressure'] = {'high': 0, 'low': 1, 'normal': 2}.get(user_input['Blood Pressure'].lower(), -1)
    user_input['Cholesterol Level'] = {'high': 0, 'low': 1, 'normal': 2}.get(user_input['Cholesterol Level'].lower(),
                                                                             -1)
    # 'Age' remains as it is
    # Create a DataFrame from the preprocessed user input
    user_df = pd.DataFrame([user_input])

    return user_df


def predict(input):
    """Predicting using Input."""
    # Likelihood of each Disease/Class
    probabilities = model.predict_proba(input)

    # Get the class labels from the model
    classes = model.classes_

    # Map the probabilities to each class
    disease_probabilities = dict(zip(classes, probabilities.ravel()))

    # Get the top 3 diseases with highest probabilities
    top_diseases = sorted(disease_probabilities.items(), key=lambda x: x[1], reverse=True)[:10]

    numerical_data = pd.read_csv('Numerical_Data.csv')
    existing_diseases = set()
    result_dfs = []  # List to store individual DataFrames

    for disease, likelihood in top_diseases:
        disease_name = numerical_data.loc[numerical_data['Num_Dis'] == disease, 'Disease'].iloc[0]

        # Avoiding Disease Repetition
        if disease_name not in existing_diseases:
            result_dfs.append(pd.DataFrame({'Disease': [disease_name], 'Likelihood': [likelihood * 100]}))
            existing_diseases.add(disease_name)

    result_df = pd.concat(result_dfs, ignore_index=True)
    return result_df


def FetchData(result_df):
    """Fetching the Diseases Data from Disease_Data.json."""
    # Load the JSON file
    with open('Disease_Data.json', 'r') as file:
        data = json.load(file)

    # Check if "diseases" key is present and is a list
    if isinstance(data.get("diseases"), list):
        diseases_data = data["diseases"]

        # Iterate through the rows of result_df
        for index, row in result_df.iterrows():
            disease_name = row['Disease']
            likelihood = row['Likelihood']

            # Find the disease information in the JSON data
            disease_info = next((item for item in diseases_data if item["name"] == disease_name), None)

            # If disease information is found, update the corresponding row in result_df
            if disease_info:
                result_df.at[index, 'Symptoms'] = json.dumps(disease_info.get("symptoms", []))
                result_df.at[index, 'Precautions'] = json.dumps(disease_info.get("precautions", []))
                result_df.at[index, 'Daily_Health_Routine'] = json.dumps(disease_info.get("daily_health_routine", []))
                result_df.at[index, 'Likelihood'] = likelihood

        return result_df
    else:
        print("Error: JSON data is not in the expected format.")


if __name__ == '__main__':
    app.run(debug=True)
