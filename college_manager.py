import json
import os
import streamlit as st

class CollegeManager:
    def __init__(self):
        self.file_path = 'data/colleges.json'
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def get_colleges(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"خطأ في قراءة بيانات الكليات: {str(e)}")
            return []

    def add_college(self, name, students_count, foreign_students, graduate_students, 
                   dorm_students, evening_students, evening_hosted_students, departments=None):
        colleges = self.get_colleges()
        college = {
            "name": name,
            "students_count": students_count,
            "foreign_students": foreign_students,
            "graduate_students": graduate_students,
            "dorm_students": dorm_students,
            "evening_students": evening_students,
            "evening_hosted_students": evening_hosted_students,
            "departments": departments or []
        }
        colleges.append(college)
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(colleges, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"خطأ في حفظ بيانات الكلية: {str(e)}")

    def update_college(self, old_name, name, students_count, foreign_students, 
                      graduate_students, dorm_students, evening_students, evening_hosted_students,
                      departments=None):
        colleges = self.get_colleges()
        for college in colleges:
            if college['name'] == old_name:
                college.update({
                    "name": name,
                    "students_count": students_count,
                    "foreign_students": foreign_students,
                    "graduate_students": graduate_students,
                    "dorm_students": dorm_students,
                    "evening_students": evening_students,
                    "evening_hosted_students": evening_hosted_students,
                })
                if departments is not None:
                    college["departments"] = departments
                break
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(colleges, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"خطأ في تحديث بيانات الكلية: {str(e)}")
            return False

    def get_department_stats(self, college_name=None):
        """
        احصل على إحصائيات الطلاب مصنفة حسب الأقسام
        """
        colleges = self.get_colleges()
        stats = {}

        for college in colleges:
            if college_name and college['name'] != college_name:
                continue

            for dept in college.get('departments', []):
                if dept not in stats:
                    stats[dept] = {
                        'total_students': 0,
                        'foreign_students': 0,
                        'graduate_students': 0,
                        'dorm_students': 0,
                        'evening_students': 0,
                        'evening_hosted_students': 0
                    }

                # احتساب نسبة الطلاب لكل قسم
                dept_count = len(college.get('departments', []))
                if dept_count > 0:
                    students_per_dept = {
                        'total_students': college['students_count'] / dept_count,
                        'foreign_students': college.get('foreign_students', 0) / dept_count,
                        'graduate_students': college.get('graduate_students', 0) / dept_count,
                        'dorm_students': college.get('dorm_students', 0) / dept_count,
                        'evening_students': college.get('evening_students', 0) / dept_count,
                        'evening_hosted_students': college.get('evening_hosted_students', 0) / dept_count
                    }

                    for key in stats[dept]:
                        stats[dept][key] += students_per_dept[key]

        return stats

    def add_department(self, college_name, department_name):
        colleges = self.get_colleges()
        for college in colleges:
            if college['name'] == college_name:
                if 'departments' not in college:
                    college['departments'] = []
                if department_name not in college['departments']:
                    college['departments'].append(department_name)
                break
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(colleges, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"خطأ في إضافة القسم: {str(e)}")
            return False

    def remove_department(self, college_name, department_name):
        colleges = self.get_colleges()
        for college in colleges:
            if college['name'] == college_name:
                if 'departments' in college and department_name in college['departments']:
                    college['departments'].remove(department_name)
                break
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(colleges, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"خطأ في حذف القسم: {str(e)}")
            return False

    def delete_college(self, name):
        colleges = self.get_colleges()
        colleges = [c for c in colleges if c['name'] != name]
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(colleges, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"خطأ في حذف الكلية: {str(e)}")