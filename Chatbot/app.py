from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS
import os
# Load the dataset
data = pd.read_csv('./data/processed_file.csv')
numerical = ['Area', 'Frontage', 'Access Road', 'Floors', 'Bedrooms', 'Bathrooms','Price']
categorical = ['House direction','Balcony direction', 'Legal status','Furniture state', 'Province','Project']

# Flask app setup
app = Flask(__name__)
CORS(app)

# Route for chatbot interface
@app.route('/')
def chatbot_interface():
    return render_template('chatbot.html')  # Render giao diện chatbot từ folder templates

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

    elif intent == 'Phân bố theo tỉnh':
        province = parameters['Province']
        column = parameters['attribute']
        print(column)
        if column in numerical:
            response = get_numerical_satistics_by_province(province, column)
        elif column in categorical:
            response = get_category_statistics_by_province(province, column)

    elif intent == "Phân bố":
        result = parameters['attribute']
        if result in numerical:
            response = get_numerical_satistics(result)
        elif result in categorical:
            response = get_category_statistics(result)

    elif intent == 'MinPriceByProvince':
        province = parameters.get('Province')
        response = get_min_price(province)

    elif intent == 'Danh sách các thuộc tính':
        response = (
            "Tập dữ liệu bao gồm 14 thuộc tính có ý nghĩa như sau:\n"
            "- Address: địa chỉ nhà ở\n"
            "- Area: diện tích nhà ở (đơn vị: m²)\n"
            "- Frontage: diện tích mặt tiền của nhà ở (đơn vị: m²)\n"
            "- Access Road: diện tích lối vào nhà ở (đơn vị: m²)\n"
            "- House direction: hướng của nhà ở\n"
            "- Balcony direction: hướng của ban công\n"
            "- Floors: số tầng\n"
            "- Bedrooms: số phòng ngủ\n"
            "- Bathrooms: số phòng tắm\n"
            "- Legal status: tình trạng pháp lý\n"
            "- Furniture state: tình trạng nội thất\n"
            "- Price: giá của căn nhà\n"
            "- Province: tỉnh/thành\n"
            "- Project: ngôi nhà có đang thuộc dự án không (Yes/No)"
        )

    elif intent == "Thông tin về tập dữ liệu":
        response = (
            "- Tập dữ liệu: dữ liệu về nhà ở tại Việt Nam\n"
            "- Nguồn: thu thập từ Kaggle\n"
            "- Kích thước: Bao gồm 21904 mẫu và 14 thuộc tính\n"
            "- Mỗi dòng dữ liệu cho biết thông tin của một căn nhà tại Việt Nam ở một tỉnh/thành\n"
            "- Ứng dụng: tập dữ liệu được sử dụng để phân tích giá nhà ở các tỉnh/thành Việt Nam, các yếu tố ảnh hưởng đến thuộc tính như thế nào."
        )
    
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
    
    
def get_category_statistics(column_name):
    if column_name in data.columns:
        value_counts = data[column_name].value_counts()
        total_count = len(data)
        category_stats = "Thống kê cho thuộc tính {}:\n".format(column_name)
        category_stats += f"- Số giá trị khác nhau: {len(value_counts)}\n"

        for category, count in value_counts.items():
            percentage = (count / total_count) * 100
            category_stats += f"- {category}: {count} giá trị ({percentage:.2f}%)\n"

        return category_stats
    else:
        return f"Cột {column_name} không tồn tại trong dữ liệu."
    
def get_numerical_satistics(column_name):
    if column_name in data.columns:
        min_area = data[column_name].min()
        max_area = data[column_name].max()
        avg_area = data[column_name].mean()
        median_area = data[column_name].median()
        q1_area = data[column_name].quantile(0.25)
        q3_area = data[column_name].quantile(0.75)
        iqr_area = q3_area - q1_area

        # Định dạng kết quả
        result = (
            f"Thống kê cho thuộc tính {column_name}\n"
            f"- Thấp nhất: {min_area:.2f}\n"
            f"- Cao nhất: {max_area:.2f}\n"
            f"- Trung bình: {avg_area:.2f}\n"
            f"- Trung vị: {median_area:.2f}\n"
            f"- Tứ phân vị (Q1): {q1_area:.2f}\n"
            f"- Tứ phân vị (Q3): {q3_area:.2f}\n"
            f"- Khoảng tứ phân vị(IQR): {iqr_area:.2f}"
        )
        return result
    else:
        return f"Không có dữ liệu cho {column_name}."
    
def get_numerical_satistics_by_province(province, column_name):
    # Lọc dữ liệu theo tỉnh thành
    filtered_data = data[data['Province'] == province]

    if column_name in data.columns:
        min_area = filtered_data[column_name].min()
        max_area = filtered_data[column_name].max()
        avg_area = filtered_data[column_name].mean()
        median_area = filtered_data[column_name].median()
        q1_area = filtered_data[column_name].quantile(0.25)
        q3_area = filtered_data[column_name].quantile(0.75)
        iqr_area = q3_area - q1_area

        # Định dạng kết quả
        result = (
            f"Thống kê cho thuộc tính {column_name} tại {province}\n"
            f"- Thấp nhất: {min_area:.2f}\n"
            f"- Cao nhất: {max_area:.2f}\n"
            f"- Trung bình: {avg_area:.2f}\n"
            f"- Trung vị: {median_area:.2f}\n"
            f"- Tứ phân vị (Q1): {q1_area:.2f}\n"
            f"- Tứ phân vị (Q3): {q3_area:.2f}\n"
            f"- Khoảng tứ phân vị(IQR): {iqr_area:.2f}"
        )
        return result
    else:
        return f"Không có dữ liệu cho {column_name}."
    
def get_category_statistics_by_province(province, column_name):
    # Lọc dữ liệu theo tỉnh thành
    filtered_data = data[data['Province'] == province]

    if column_name in data.columns:
        value_counts = filtered_data[column_name].value_counts()
        total_count = len(filtered_data)
        category_stats = f"Thống kê cho thuộc tính {column_name} tại {province}:\n"

        category_stats += f"- Số giá trị khác nhau: {len(value_counts)}\n"

        for category, count in value_counts.items():
            percentage = (count / total_count) * 100
            category_stats += f"- {category}: {count} giá trị ({percentage:.2f}%)\n"

        return category_stats
    else:
        return f"Cột {column_name} không tồn tại trong dữ liệu."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Sử dụng cổng từ biến môi trường hoặc 5000 mặc định
    app.run(host="0.0.0.0", port=port)
