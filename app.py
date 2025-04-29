import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import os

# Set page config - must be first Streamlit command
st.set_page_config(
    page_title="Prediksi Dropout Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { 
        padding: 2rem; 
        background-color: #f5f5f5; /* Warna latar belakang abu-abu terang */
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .prediction-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .high-risk {
        background-color: #010203;
        border: 2px solid #ef5350;
    }
    .low-risk {
        background-color: #010203;
        border: 2px solid #66bb6a;
    }
    </style>
""", unsafe_allow_html=True)

# Load models with debug info
@st.cache_resource
def load_models():
    try:
        # Add file existence check
        model_path = 'model_dropout_xgboost.pkl'
        scaler_path = 'scaler.pkl'
        encoders_path = 'label_encoders.pkl'
        
        if not all(map(os.path.exists, [model_path, scaler_path, encoders_path])):
            _ = [f for f in [model_path, scaler_path, encoders_path] if not os.path.exists(f)]
            return None, None, None
            
        # Load model with debug info
        model = joblib.load(model_path)
        
        # Load scaler with debug info
        scaler = joblib.load(scaler_path)
        
        # Load encoders with detailed debug info
        label_encoders = joblib.load(encoders_path)
        if not label_encoders:
            return None, None, None
        
        return model, scaler, label_encoders
    except Exception as e:
        return None, None, None

model, scaler, label_encoders = load_models()

# Title
st.title("🎓 Prediksi Dropout Mahasiswa")
st.markdown("""
### Sistem Prediksi Dropout Berbasis Machine Learning
Masukkan data mahasiswa untuk memprediksi kemungkinan dropout.
""")

with st.form("prediction_form"):
    st.subheader("Formulir Input Data Mahasiswa")

    # Kelompok 1: Informasi Dasar Mahasiswa
    with st.expander("📋 Informasi Dasar Mahasiswa"):
        marital_status_mapping = {
            "1 - Single": 1,
            "2 - Married": 2,
            "3 - Widower": 3,
            "4 - Divorced": 4,
            "5 - Facto union": 5,
            "6 - Legally separated": 6,
        }
        marital_status = st.selectbox("Status Pernikahan", options=list(marital_status_mapping.keys()))
        marital_status = marital_status_mapping[marital_status]

        application_mode_mapping = {
            "1 - 1st phase - general contingent": 1,
            "2 - Ordinance No. 612/93": 2,
            "5 - 1st phase - special contingent (Azores Island)": 5,
            "7 - Holders of other higher courses": 7,
            "10 - Ordinance No. 854-B/99": 10,
            "15 - International student (bachelor)": 15,
            "16 - 1st phase - special contingent (Madeira Island)": 16,
            "17 - 2nd phase - general contingent": 17,
            "18 - 3rd phase - general contingent": 18,
            "26 - Ordinance No. 533-A/99, item b2)": 26,
            "27 - Ordinance No. 533-A/99, item b3": 27,
            "39 - Over 23 years old": 39,
            "42 - Transfer": 42,
            "43 - Change of course": 43,
            "44 - Technological specialization diploma holders": 44,
            "51 - Change of institution/course": 51,
            "53 - Short cycle diploma holders": 53,
            "57 - Change of institution/course (International)": 57,
        }
        application_mode = st.selectbox("Mode Pendaftaran", options=list(application_mode_mapping.keys()))
        application_mode = application_mode_mapping[application_mode]

        application_order = st.number_input("Urutan Pendaftaran", min_value=0, max_value=9, value=0)

        course_mapping = {
            "33 - Biofuel Production Technologies": 33,
            "171 - Animation and Multimedia Design": 171,
            "8014 - Social Service (evening attendance)": 8014,
            "9003 - Agronomy": 9003,
            "9070 - Communication Design": 9070,
            "9085 - Veterinary Nursing": 9085,
            "9119 - Informatics Engineering": 9119,
            "9130 - Equinculture": 9130,
            "9147 - Management": 9147,
            "9238 - Social Service": 9238,
            "9254 - Tourism": 9254,
            "9500 - Nursing": 9500,
            "9556 - Oral Hygiene": 9556,
            "9670 - Advertising and Marketing Management": 9670,
            "9773 - Journalism and Communication": 9773,
            "9853 - Basic Education": 9853,
            "9991 - Management (evening attendance)": 9991,
        }
        course = st.selectbox("Program Studi", options=list(course_mapping.keys()))
        course = course_mapping[course]

        daytime_evening_attendance = st.selectbox("Waktu Kehadiran", options={"1 - Daytime": 1, "0 - Evening": 0})

    # Kelompok 2: Kualifikasi dan Latar Belakang
    with st.expander("🎓 Kualifikasi dan Latar Belakang"):
        previous_qualification_mapping = {
            "1 - Secondary education": 1,
            "2 - Higher education - bachelor's degree": 2,
            "3 - Higher education - degree": 3,
            "4 - Higher education - master's": 4,
            "5 - Higher education - doctorate": 5,
            "6 - Frequency of higher education": 6,
            "9 - 12th year of schooling - not completed": 9,
            "10 - 11th year of schooling - not completed": 10,
            "12 - Other - 11th year of schooling": 12,
            "14 - 10th year of schooling": 14,
            "15 - 10th year of schooling - not completed": 15,
            "19 - Basic education 3rd cycle": 19,
            "38 - Basic education 2nd cycle": 38,
            "39 - Technological specialization course": 39,
            "40 - Higher education - degree (1st cycle)": 40,
            "42 - Professional higher technical course": 42,
            "43 - Higher education - master (2nd cycle)": 43,
        }
        previous_qualification = st.selectbox(
            "Kualifikasi Sebelumnya", 
            options=list(previous_qualification_mapping.keys())
        )
        previous_qualification = previous_qualification_mapping[previous_qualification]

        previous_qualification_grade = st.number_input(
            "Nilai Kualifikasi Sebelumnya", 
            min_value=0.0, 
            max_value=200.0, 
            value=100.0
        )

        nationality_mapping = {
            "1 - Portuguese": 1,
            "2 - German": 2,
            "6 - Spanish": 6,
            "11 - Italian": 11,
            "13 - Dutch": 13,
            "14 - English": 14,
            "17 - Lithuanian": 17,
            "21 - Angolan": 21,
            "22 - Cape Verdean": 22,
            "24 - Guinean": 24,
            "25 - Mozambican": 25,
            "26 - Santomean": 26,
            "32 - Turkish": 32,
            "41 - Brazilian": 41,
            "62 - Romanian": 62,
            "100 - Moldova (Republic of)": 100,
            "101 - Mexican": 101,
            "103 - Ukrainian": 103,
            "105 - Russian": 105,
            "108 - Cuban": 108,
            "109 - Colombian": 109,
        }
        nationality = st.selectbox("Kewarganegaraan", options=list(nationality_mapping.keys()))
        nationality = nationality_mapping[nationality]

        mothers_qualification_mapping = {
            "1 - Secondary Education": 1,
            "2 - Higher Education - Bachelor's Degree": 2,
            "3 - Higher Education - Degree": 3,
            "4 - Higher Education - Master's": 4,
            "5 - Higher Education - Doctorate": 5,
            "6 - Frequency of Higher Education": 6,
            "9 - 12th Year of Schooling - Not Completed": 9,
            "10 - 11th Year of Schooling - Not Completed": 10,
            "12 - Other - 11th Year of Schooling": 12,
            "14 - 10th Year of Schooling": 14,
            "15 - 10th Year of Schooling - Not Completed": 15,
            "19 - Basic Education 3rd Cycle": 19,
            "38 - Basic Education 2nd Cycle": 38,
            "39 - Technological Specialization Course": 39,
            "40 - Higher Education - Degree (1st Cycle)": 40,
            "42 - Professional Higher Technical Course": 42,
            "43 - Higher Education - Master (2nd Cycle)": 43,
        }
        mothers_qualification = st.selectbox("Kualifikasi Ibu", options=list(mothers_qualification_mapping.keys()))
        mothers_qualification = mothers_qualification_mapping[mothers_qualification]

        fathers_qualification_mapping = {
            "1 - Secondary Education": 1,
            "2 - Higher Education - Bachelor's Degree": 2,
            "3 - Higher Education - Degree": 3,
            "4 - Higher Education - Master's": 4,
            "5 - Higher Education - Doctorate": 5,
            "6 - Frequency of Higher Education": 6,
            "9 - 12th Year of Schooling - Not Completed": 9,
            "10 - 11th Year of Schooling - Not Completed": 10,
            "12 - Other - 11th Year of Schooling": 12,
            "14 - 10th Year of Schooling": 14,
            "15 - 10th Year of Schooling - Not Completed": 15,
            "19 - Basic Education 3rd Cycle": 19,
            "38 - Basic Education 2nd Cycle": 38,
            "39 - Technological Specialization Course": 39,
            "40 - Higher Education - Degree (1st Cycle)": 40,
            "42 - Professional Higher Technical Course": 42,
            "43 - Higher Education - Master (2nd Cycle)": 43,
        }
        fathers_qualification = st.selectbox("Kualifikasi Ayah", options=list(fathers_qualification_mapping.keys()))
        fathers_qualification = fathers_qualification_mapping[fathers_qualification]

        mothers_occupation_mapping = {
            "0 - Not Available": 0,
            "1 - Executives and Managers": 1,
            "2 - Professionals": 2,
            "3 - Technicians and Associate Professionals": 3,
            "4 - Administrative Staff": 4,
            "5 - Personal Services, Protection, Security": 5,
            "6 - Sellers": 6,
            "7 - Farmers and Skilled Workers in Agriculture": 7,
            "8 - Skilled Workers in Industry, Construction, Artisans": 8,
            "9 - Machine Operators and Assembly Workers": 9,
            "10 - Unskilled Workers": 10,
            "90 - Other Situation": 90,
        }
        mothers_occupation = st.selectbox("Pekerjaan Ibu", options=list(mothers_occupation_mapping.keys()))
        mothers_occupation = mothers_occupation_mapping[mothers_occupation]

        fathers_occupation_mapping = {
            "0 - Not Available": 0,
            "1 - Executives and Managers": 1,
            "2 - Professionals": 2,
            "3 - Technicians and Associate Professionals": 3,
            "4 - Administrative Staff": 4,
            "5 - Personal Services, Protection, Security": 5,
            "6 - Sellers": 6,
            "7 - Farmers and Skilled Workers in Agriculture": 7,
            "8 - Skilled Workers in Industry, Construction, Artisans": 8,
            "9 - Machine Operators and Assembly Workers": 9,
            "10 - Unskilled Workers": 10,
            "90 - Other Situation": 90,
        }
        fathers_occupation = st.selectbox("Pekerjaan Ayah", options=list(fathers_occupation_mapping.keys()))
        fathers_occupation = fathers_occupation_mapping[fathers_occupation]

    # Kelompok 3: Informasi Akademik
    with st.expander("📚 Informasi Akademik"):
        admission_grade = st.number_input("Nilai Masuk", min_value=0.0, max_value=200.0, value=100.0)

        curricular_units_1st_sem_credited = st.number_input("Jumlah SKS Terakreditasi Semester 1", min_value=0)
        curricular_units_1st_sem_enrolled = st.number_input("Jumlah SKS Diambil Semester 1", min_value=0)
        curricular_units_1st_sem_evaluations = st.number_input("Jumlah Evaluasi Semester 1", min_value=0)
        curricular_units_1st_sem_approved = st.number_input("Jumlah SKS Lulus Semester 1", min_value=0)
        curricular_units_1st_sem_grade = st.number_input("Rata-rata Nilai Semester 1", min_value=0.0, max_value=20.0)
        curricular_units_1st_sem_without_evaluations = st.number_input("SKS Tanpa Evaluasi Semester 1", min_value=0)

        curricular_units_2nd_sem_credited = st.number_input("Jumlah SKS Terakreditasi Semester 2", min_value=0)
        curricular_units_2nd_sem_enrolled = st.number_input("Jumlah SKS Diambil Semester 2", min_value=0)
        curricular_units_2nd_sem_evaluations = st.number_input("Jumlah Evaluasi Semester 2", min_value=0)
        curricular_units_2nd_sem_approved = st.number_input("Jumlah SKS Lulus Semester 2", min_value=0)
        curricular_units_2nd_sem_grade = st.number_input("Rata-rata Nilai Semester 2", min_value=0.0, max_value=20.0)
        curricular_units_2nd_sem_without_evaluations = st.number_input("SKS Tanpa Evaluasi Semester 2", min_value=0)

    # Kelompok 4: Informasi Ekonomi dan Sosial
    with st.expander("💼 Informasi Ekonomi dan Sosial"):
        boolean_mapping = {
            "Tidak": 0,
            "Ya": 1
        }
        displaced = st.selectbox("Apakah Mahasiswa Terdampak (Displaced)?", options=list(boolean_mapping.keys()))
        displaced = boolean_mapping[displaced]

        educational_special_needs = st.selectbox("Kebutuhan Khusus Pendidikan?", options=list(boolean_mapping.keys()))
        educational_special_needs = boolean_mapping[educational_special_needs]

        debtor = st.selectbox("Memiliki Tunggakan?", options=list(boolean_mapping.keys()))
        debtor = boolean_mapping[debtor]

        tuition_fees_up_to_date = st.selectbox("Biaya Kuliah Terbayar Tepat Waktu?", options=list(boolean_mapping.keys()))
        tuition_fees_up_to_date = boolean_mapping[tuition_fees_up_to_date]

        gender_mapping = {
            "Laki-laki": 1,
            "Perempuan": 0
        }
        gender = st.selectbox("Jenis Kelamin", options=list(gender_mapping.keys()))
        gender = gender_mapping[gender]

        scholarship_holder = st.selectbox("Penerima Beasiswa?", options=list(boolean_mapping.keys()))
        scholarship_holder = boolean_mapping[scholarship_holder]

        international = st.selectbox("Mahasiswa Internasional?", options=list(boolean_mapping.keys()))
        international = boolean_mapping[international]

        age_at_enrollment = st.number_input("Usia Saat Pendaftaran", min_value=15, max_value=100, value=18)

    # Kelompok 5: Indikator Ekonomi Makro
    with st.expander("📈 Indikator Ekonomi Makro"):
        unemployment_rate = st.number_input("Tingkat Pengangguran (%)", min_value=0.0, max_value=100.0)
        inflation_rate = st.number_input("Tingkat Inflasi (%)", min_value=0.0, max_value=100.0)
        gdp = st.number_input("GDP (miliar Euro)", min_value=0.0)

    # Tombol submit
    submitted = st.form_submit_button("🔍 Prediksi")

# Update the input data creation to use the numeric values directly
if submitted and model and scaler and label_encoders:
    try:
        # Buat DataFrame input
        input_data = pd.DataFrame({
            'Marital_status': [marital_status],
            'Application_mode': [application_mode],
            'Application_order': [application_order],
            'Course': [course],
            'Daytime_evening_attendance': [1],
            'Previous_qualification': [previous_qualification],
            'Previous_qualification_grade': [previous_qualification_grade],
            'Nacionality': [nationality],
            'Mothers_qualification': [mothers_qualification],
            'Fathers_qualification': [fathers_qualification],
            'Mothers_occupation': [mothers_occupation],
            'Fathers_occupation': [fathers_occupation],
            'Admission_grade': [admission_grade],
            'Displaced': [displaced],
            'Educational_special_needs': [educational_special_needs],
            'Debtor': [debtor],
            'Tuition_fees_up_to_date': [tuition_fees_up_to_date],
            'Gender': [gender],
            'Scholarship_holder': [scholarship_holder],
            'Age_at_enrollment': [age_at_enrollment],
            'International': [international],
            'Curricular_units_1st_sem_credited': [curricular_units_1st_sem_credited],
            'Curricular_units_1st_sem_enrolled': [curricular_units_1st_sem_enrolled],
            'Curricular_units_1st_sem_evaluations': [curricular_units_1st_sem_evaluations],
            'Curricular_units_1st_sem_approved': [curricular_units_1st_sem_approved],
            'Curricular_units_1st_sem_grade': [curricular_units_1st_sem_grade],
            'Curricular_units_1st_sem_without_evaluations': [curricular_units_1st_sem_without_evaluations],
            'Curricular_units_2nd_sem_credited': [curricular_units_2nd_sem_credited],
            'Curricular_units_2nd_sem_enrolled': [curricular_units_2nd_sem_enrolled],
            'Curricular_units_2nd_sem_evaluations': [curricular_units_2nd_sem_evaluations],
            'Curricular_units_2nd_sem_approved': [curricular_units_2nd_sem_approved],
            'Curricular_units_2nd_sem_grade': [curricular_units_2nd_sem_grade],
            'Curricular_units_2nd_sem_without_evaluations': [curricular_units_2nd_sem_without_evaluations],
            'GDP': [gdp],
            'Inflation_rate': [inflation_rate],
            'Unemployment_rate': [unemployment_rate]
        })

        input_data['avg_grade'] = (input_data['Curricular_units_1st_sem_grade'] + input_data['Curricular_units_2nd_sem_grade']) / 2
        input_data['approval_rate'] = (input_data['Curricular_units_1st_sem_approved'] + input_data['Curricular_units_2nd_sem_approved']) / \
                        (input_data['Curricular_units_1st_sem_enrolled'] + input_data['Curricular_units_2nd_sem_enrolled'] + 1e-5)
        input_data['Age_at_enrollment'] = input_data['Age_at_enrollment']
        input_data['Debtor'] = input_data['Debtor']
        input_data['Scholarship_holder'] = input_data['Scholarship_holder']
        input_data['Tuition_fees_up_to_date'] = input_data['Tuition_fees_up_to_date']

        # Urutkan kolom sesuai dengan fitur yang digunakan saat pelatihan
        input_data = input_data[scaler.feature_names_in_]

        # Scale features
        input_data_scaled = scaler.transform(input_data)

        # Make prediction
        prediction = model.predict(input_data_scaled)
        probability = model.predict_proba(input_data_scaled)[0][1]

        # Display results
        st.markdown("---")
        st.header("📊 Hasil Prediksi")
        
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            if prediction[0] == 1:
                st.markdown(f"""
                    <div class='prediction-box high-risk'>
                        <h3>⚠️ Status: BERISIKO DROPOUT</h3>
                        <p style='font-size: 20px;'>Probabilitas: {probability:.2%}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='prediction-box low-risk'>
                        <h3>✅ Status: TIDAK BERISIKO</h3>
                        <p style='font-size: 20px;'>Probabilitas Bertahan: {1-probability:.2%}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        with col_result2:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = probability * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Risiko Dropout (%)"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkred" if prediction[0] == 1 else "green"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "salmon"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            st.plotly_chart(fig)

    except Exception as e:
        st.error("❌ Terjadi kesalahan dalam pemrosesan")
        st.error(f"Detail error: {str(e)}")

# Footer
st.markdown("""
---
### ℹ️ Informasi
* Model prediksi menggunakan XGBoost dengan akurasi ~88%
* Hasil prediksi bersifat indikatif dan memerlukan validasi lebih lanjut

Made by Yosia
""")