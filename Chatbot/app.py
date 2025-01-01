from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
# Load the dataset
data = pd.read_csv('./data/processed_file.csv')

# Flask app setup
app = Flask(__name__)
CORS(app)

# Endpoint to handle Dialogflow webhook requests
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    response = {
        "fulfillmentText": "Webhook hoạt động!"
    }

    # Extract intent and parameters from the request
    intent = req['queryResult']['intent']['displayName']
    parameters = req['queryResult']['parameters']

    if intent == 'AveragePriceByProvince':
        province = parameters.get('Province')
        response = get_average_price(province)

    elif intent == 'AverageAreaByProvince':
        province = parameters.get('Province')
        response = get_average_area(province)

    elif intent == 'MaxPriceByProvince':
        province = parameters.get('Province')
        response = get_max_price(province)

    elif intent == 'MinPriceByProvince':
        province = parameters.get('Province')
        response = get_min_price(province)

    else:
        response = "Tôi không hiểu yêu cầu của bạn."

    return jsonify({"fulfillmentText": response})

# Helper functions to compute required metrics
def get_average_price(province):
    filtered_data = data[data['Province'] == province]
    if not filtered_data.empty:
        avg_price = filtered_data['Price'].mean()
        return f"Mức giá trung bình tại {province} là {avg_price:.2f} triệu đồng."
    else:
        return f"Không có dữ liệu cho {province}."

def get_average_area(province):
    filtered_data = data[data['Province'] == province]
    if not filtered_data.empty:
        avg_area = filtered_data['Area'].mean()
        return f"Diện tích trung bình tại {province} là {avg_area:.2f} m²."
    else:
        return f"Không có dữ liệu cho {province}."

def get_max_price(province):
    filtered_data = data[data['Province'] == province]
    if not filtered_data.empty:
        max_price = filtered_data['Price'].max()
        return f"Mức giá cao nhất tại {province} là {max_price:.2f} triệu đồng."
    else:
        return f"Không có dữ liệu cho {province}."

def get_min_price(province):
    filtered_data = data[data['Province'] == province]
    if not filtered_data.empty:
        min_price = filtered_data['Price'].min()
        return f"Mức giá thấp nhất tại {province} là {min_price:.2f} triệu đồng."
    else:
        return f"Không có dữ liệu cho {province}."

if __name__ == '__main__':
    app.run(port=5000)
