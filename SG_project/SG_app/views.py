from django.shortcuts import render
from django.http import HttpResponse
from collections import Counter
import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
from django.conf import settings


# 데이터 불러오기 및 전처리
file_path = os.path.join(os.path.dirname(__file__), 'full_data.csv')
df = pd.read_csv(file_path)
# 'ever_married'와 'gender'를 이진 변수로 변환
df['ever_married'] = [0 if i != 'Yes' else 1 for i in df['ever_married']]
df['gender'] = [0 if i != 'Female' else 1 for i in df['gender']]
df = pd.get_dummies(df, columns=['work_type', 'Residence_type', 'smoking_status'])

# 특성과 레이블 분리
X = df.drop(['stroke'], axis=1)
y = df['stroke']

# 언더샘플링 적용
undersample = RandomUnderSampler(sampling_strategy='majority')
X_under, y_under = undersample.fit_resample(X, y)

# 데이터 분할 (훈련 세트 67%, 테스트 세트 33%)
X_train_rs, X_test_rs, y_train_rs, y_test_rs = train_test_split(X_under, y_under, test_size=0.33, random_state=43)

# 랜덤 포레스트 모델 학습
rfc = RandomForestClassifier()
rfc.fit(X_train_rs, y_train_rs)

# 모델 학습 시 사용한 열 순서를 저장
feature_names = X_train_rs.columns

def main(request):
    return render(request, 'SG_app/main.html')

def submit(request):
    if request.method == 'POST':
        # POST 요청으로부터 데이터 가져오기
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        hypertension = request.POST.get('hypertension')
        heart_disease = request.POST.get('heart_disease')
        avg_glucose_level = request.POST.get('avg_glucose_level')
        bmi = request.POST.get('bmi')
        smoking_status = request.POST.get('smoking_status')

        # 값 콘솔에 출력
        print(f"나이: {age}")
        print(f"성별: {gender}")
        print(f"고혈압 여부: {hypertension}")
        print(f"심장병 여부: {heart_disease}")
        print(f"평균 혈당 수치: {avg_glucose_level}")
        print(f"BMI: {bmi}")
        print(f"흡연 상태: {smoking_status}")

        # 데이터 프레임으로 변환
        user_data = {'age': [age], 'gender': [gender], 'hypertension': [hypertension], 'heart_disease': [heart_disease],
                     'ever_married': [0], 'avg_glucose_level': [avg_glucose_level], 'bmi': [bmi],
                     'work_type_Govt_job': [0], 'work_type_Private': [0], 'work_type_Self-employed': [0],
                     'work_type_children': [0], 'Residence_type_Rural': [0], 'Residence_type_Urban': [0],
                     'smoking_status_Unknown': [0], 'smoking_status_formerly smoked': [0],
                     'smoking_status_never smoked': [0], 'smoking_status_smokes': [0],
                     'smoking_status_' + smoking_status: [1]}

        # 입력 데이터를 학습 시 사용한 열 순서에 맞추기
        user_input_df = pd.DataFrame(user_data)
        user_input_df = user_input_df.reindex(columns=feature_names, fill_value=0)

        # 머신러닝 모델을 사용하여 예측 수행
        prediction = rfc.predict(user_input_df)
        probability = rfc.predict_proba(user_input_df)

        # 결과를 템플릿에 전달하여 웹 페이지에 표시
        return render(request, 'SG_app/result.html', {'prediction': prediction[0], 'probability': probability[0][1] * 100})
    else:
        # POST 요청이 아닌 경우 처리할 수 있는 로직 추가
        return HttpResponse("POST 요청이 아닙니다.")
