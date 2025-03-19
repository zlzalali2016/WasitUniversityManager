import os
import streamlit as st
import base64

class FileManager:
    def __init__(self):
        self.base_path = 'data/files'
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def save_file(self, uploaded_file, college_name):
        college_path = os.path.join(self.base_path, college_name)
        if not os.path.exists(college_path):
            os.makedirs(college_path)
            
        try:
            file_path = os.path.join(college_path, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
        except Exception as e:
            st.error(f"خطأ في حفظ الملف: {str(e)}")

    def get_files(self, college_name):
        college_path = os.path.join(self.base_path, college_name)
        if not os.path.exists(college_path):
            return []
        try:
            return os.listdir(college_path)
        except Exception as e:
            st.error(f"خطأ في قراءة الملفات: {str(e)}")
            return []

    def download_file(self, filename, college_name):
        try:
            file_path = os.path.join(self.base_path, college_name, filename)
            with open(file_path, 'rb') as f:
                bytes_data = f.read()
                b64 = base64.b64encode(bytes_data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">اضغط هنا للتحميل</a>'
                st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"خطأ في تحميل الملف: {str(e)}")
