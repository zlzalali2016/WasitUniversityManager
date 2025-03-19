import streamlit as st
import json
import os
import time
from auth import check_login, init_auth
from college_manager import CollegeManager
from file_manager import FileManager
import pandas as pd
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="نظام إدارة كليات جامعة واسط",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .college-card {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .college-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .student-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .departments-section {
        margin-top: 1rem;
    }
    @media print {
        .streamlit-expanderHeader {
            display: block !important;
        }
        .streamlit-expanderContent {
            display: block !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=True, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">{text}</a>'

def export_stats_to_excel(stats_df, filename):
    """تصدير الإحصائيات إلى ملف Excel"""
    excel_data = to_excel(stats_df)
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">تحميل التقرير بصيغة Excel</a>'
    return href

# Initialize managers
if 'college_manager' not in st.session_state:
    st.session_state.college_manager = CollegeManager()
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

# Initialize authentication
init_auth()

def show_department_dialog(college_name=None, departments=None):
    departments = departments or []
    st.markdown("### إدارة الأقسام")

    new_departments = st.text_area(
        "أدخل الأقسام (قسم واحد في كل سطر)",
        value="\n".join(departments)
    ).strip().split("\n")

    new_departments = [dept.strip() for dept in new_departments if dept.strip()]
    return new_departments

def create_stats_dataframe(colleges):
    """إنشاء DataFrame للإحصائيات العامة"""
    data = []
    for college in colleges:
        data.append({
            "الكلية": college['name'],
            "إجمالي الطلاب": college['students_count'],
            "الطلاب الأجانب": college.get('foreign_students', 0),
            "طلاب الدراسات العليا": college.get('graduate_students', 0),
            "طلاب الأقسام الداخلية": college.get('dorm_students', 0),
            "طلاب المسائي": college.get('evening_students', 0),
            "طلاب المسائي المستضافين": college.get('evening_hosted_students', 0),
            "عدد الأقسام": len(college.get('departments', []))
        })
    return pd.DataFrame(data)

def main():
    if not st.session_state.authenticated:
        with st.container():
            st.title("تسجيل الدخول")
            with st.form("login_form"):
                username = st.text_input("اسم المستخدم")
                password = st.text_input("كلمة المرور", type="password")
                submitted = st.form_submit_button("دخول")
                if submitted:
                    with st.spinner("جاري التحقق..."):
                        time.sleep(0.5)
                        if check_login(username, password):
                            st.session_state.authenticated = True
                            st.success("تم تسجيل الدخول بنجاح!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("خطأ في اسم المستخدم أو كلمة المرور")
        return

    # Main application interface
    with st.spinner("جاري تحميل النظام..."):
        st.title("نظام إدارة كليات جامعة واسط")

        menu = st.sidebar.selectbox(
            "القائمة الرئيسية",
            ["الرئيسية", "إدارة الكليات", "إدارة الملفات", "الإحصائيات"],
            key="menu_select"
        )

        if menu == "الرئيسية":
            st.header("الصفحة الرئيسية")
            st.write("مرحباً بكم في نظام إدارة كليات جامعة واسط")

            st.markdown("""
                <div style='text-align: center; padding: 2rem;'>
                    <h2 style='color: #1f77b4;'>👋 أهلاً بك في نظام إدارة الكليات</h2>
                    <p style='font-size: 1.2rem;'>اختر من القائمة الجانبية للبدء</p>
                </div>
            """, unsafe_allow_html=True)

        elif menu == "إدارة الكليات":
            st.header("إدارة الكليات")

            tab1, tab2 = st.tabs(["عرض الكليات", "إضافة كلية جديدة"])

            with tab1:
                colleges = st.session_state.college_manager.get_colleges()
                if not colleges:
                    st.info("لا توجد كليات مضافة حالياً")
                else:
                    for college in colleges:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""
                                    <div class='college-card'>
                                        <h3>{college['name']} 🏛️</h3>
                                        <div class='student-stats'>
                                            <div class='stat-card'>
                                                <h4>إجمالي الطلاب</h4>
                                                <p>👥 {college['students_count']}</p>
                                            </div>
                                            <div class='stat-card'>
                                                <h4>الطلاب الأجانب</h4>
                                                <p>🌍 {college.get('foreign_students', 0)}</p>
                                            </div>
                                            <div class='stat-card'>
                                                <h4>طلاب الدراسات العليا</h4>
                                                <p>📚 {college.get('graduate_students', 0)}</p>
                                            </div>
                                            <div class='stat-card'>
                                                <h4>طلاب الأقسام الداخلية</h4>
                                                <p>🏠 {college.get('dorm_students', 0)}</p>
                                            </div>
                                            <div class='stat-card'>
                                                <h4>طلاب المسائي</h4>
                                                <p>🌙 {college.get('evening_students', 0)}</p>
                                            </div>
                                            <div class='stat-card'>
                                                <h4>طلاب المسائي المستضافين</h4>
                                                <p>📝 {college.get('evening_hosted_students', 0)}</p>
                                            </div>
                                        </div>
                                        <div class='departments-section'>
                                            <h4>الأقسام 📚</h4>
                                            <ul>
                                                {" ".join([f"<li>{dept}</li>" for dept in college.get('departments', [])])}
                                            </ul>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if st.button("تعديل", key=f"edit_{college['name']}"):
                                    st.session_state.editing_college = college
                                    st.rerun()
                                if st.button(f"حذف", key=f"del_{college['name']}"):
                                    with st.spinner("جاري الحذف..."):
                                        st.session_state.college_manager.delete_college(college['name'])
                                        time.sleep(0.3)
                                        st.success("تم حذف الكلية بنجاح")
                                        time.sleep(0.3)
                                        st.rerun()

                                st.write("---")
                                st.write("إدارة الأقسام")
                                if st.button("تعديل الأقسام", key=f"edit_dept_{college['name']}"):
                                    new_departments = show_department_dialog(
                                        college['name'],
                                        college.get('departments', [])
                                    )
                                    if new_departments:
                                        success = st.session_state.college_manager.update_college(
                                            college['name'],
                                            college['name'],
                                            college['students_count'],
                                            college.get('foreign_students', 0),
                                            college.get('graduate_students', 0),
                                            college.get('dorm_students', 0),
                                            college.get('evening_students', 0),
                                            college.get('evening_hosted_students', 0),
                                            new_departments
                                        )
                                        if success:
                                            st.success("تم تحديث الأقسام بنجاح")
                                            time.sleep(0.3)
                                            st.rerun()

            with tab2:
                with st.form("add_college_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("اسم الكلية")
                        students_count = st.number_input("إجمالي عدد الطلاب", min_value=0)
                        foreign_students = st.number_input("عدد الطلاب الأجانب", min_value=0)
                        graduate_students = st.number_input("عدد طلاب الدراسات العليا", min_value=0)
                    with col2:
                        dorm_students = st.number_input("عدد طلاب الأقسام الداخلية", min_value=0)
                        evening_students = st.number_input("عدد طلاب المسائي", min_value=0)
                        evening_hosted_students = st.number_input("عدد طلاب المسائي المستضافين", min_value=0)

                    st.write("---")
                    departments = show_department_dialog()

                    submitted = st.form_submit_button("إضافة كلية")
                    if submitted:
                        with st.spinner("جاري إضافة الكلية..."):
                            st.session_state.college_manager.add_college(
                                name, students_count, foreign_students,
                                graduate_students, dorm_students, evening_students,
                                evening_hosted_students, departments
                            )
                            time.sleep(0.3)
                            st.success("تمت إضافة الكلية بنجاح")
                            time.sleep(0.3)
                            st.rerun()

        elif menu == "إدارة الملفات":
            st.header("إدارة الملفات")

            college_names = [c['name'] for c in st.session_state.college_manager.get_colleges()]
            if not college_names:
                st.warning("الرجاء إضافة كلية أولاً")
            else:
                selected_college = st.selectbox("اختر الكلية", college_names)

                with st.container():
                    uploaded_file = st.file_uploader("رفع ملف", type=['pdf', 'docx', 'txt'])
                    if uploaded_file is not None:
                        with st.spinner("جاري رفع الملف..."):
                            st.session_state.file_manager.save_file(uploaded_file, selected_college)
                            time.sleep(0.3)
                            st.success("تم رفع الملف بنجاح")

                files = st.session_state.file_manager.get_files(selected_college)
                if files:
                    st.write("الملفات المتوفرة:")
                    for file in files:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"📄 {file}")
                        with col2:
                            if st.button("تحميل", key=f"download_{file}"):
                                with st.spinner("جاري تحضير الملف للتحميل..."):
                                    st.session_state.file_manager.download_file(file, selected_college)

        elif menu == "الإحصائيات":
            st.header("إحصائيات الكليات")
            with st.spinner("جاري تحميل الإحصائيات..."):
                colleges = st.session_state.college_manager.get_colleges()

                # إحصائيات عامة
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_students = sum(c['students_count'] for c in colleges)
                    st.metric("إجمالي عدد الطلاب", total_students, "👥")
                with col2:
                    total_foreign = sum(c.get('foreign_students', 0) for c in colleges)
                    st.metric("إجمالي الطلاب الأجانب", total_foreign, "🌍")
                with col3:
                    total_graduate = sum(c.get('graduate_students', 0) for c in colleges)
                    st.metric("إجمالي طلاب الدراسات العليا", total_graduate, "📚")

                col4, col5, col6 = st.columns(3)
                with col4:
                    total_dorm = sum(c.get('dorm_students', 0) for c in colleges)
                    st.metric("إجمالي طلاب الأقسام الداخلية", total_dorm, "🏠")
                with col5:
                    total_evening = sum(c.get('evening_students', 0) for c in colleges)
                    st.metric("إجمالي طلاب المسائي", total_evening, "🌙")
                with col6:
                    total_hosted = sum(c.get('evening_hosted_students', 0) for c in colleges)
                    st.metric("إجمالي طلاب المسائي المستضافين", total_hosted, "📝")

                # تصدير الإحصائيات العامة
                st.markdown("### تصدير الإحصائيات العامة")
                stats_df = create_stats_dataframe(colleges)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(export_stats_to_excel(stats_df, "احصائيات_الكليات.xlsx"), unsafe_allow_html=True)
                with col2:
                    if st.button("تحضير للطباعة"):
                        st.markdown("""
                            <style>
                            @media print {
                                .stApp { display: block !important; }
                                .stButton, .stSelectbox { display: none !important; }
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        st.dataframe(stats_df)
                        st.markdown("""
                            <script>
                            window.print();
                            </script>
                        """, unsafe_allow_html=True)

                # إحصائيات حسب الأقسام
                st.subheader("إحصائيات الأقسام")

                college_filter = st.selectbox(
                    "اختر الكلية لعرض إحصائيات أقسامها",
                    ["جميع الكليات"] + [c['name'] for c in colleges]
                )

                college_name = None if college_filter == "جميع الكليات" else college_filter
                dept_stats = st.session_state.college_manager.get_department_stats(college_name)

                if dept_stats:
                    stats_df = pd.DataFrame(dept_stats).T
                    stats_df.columns = [
                        "إجمالي الطلاب",
                        "الطلاب الأجانب",
                        "طلاب الدراسات العليا",
                        "طلاب الأقسام الداخلية",
                        "طلاب المسائي",
                        "طلاب المسائي المستضافين"
                    ]

                    st.markdown("### جدول إحصائيات الأقسام")
                    st.dataframe(stats_df.round(2))

                    # تصدير إحصائيات الأقسام
                    st.markdown(export_stats_to_excel(stats_df, "احصائيات_الاقسام.xlsx"), unsafe_allow_html=True)

                    # رسوم بيانية للمقارنة
                    st.markdown("### مقارنة الأقسام")
                    chart_metric = st.selectbox(
                        "اختر المعيار للمقارنة",
                        stats_df.columns.tolist()
                    )

                    chart_data = stats_df[chart_metric]
                    st.bar_chart(chart_data)

                else:
                    st.info("لا توجد أقسام مضافة حالياً")

                # Animated charts 
                st.subheader("توزيع الطلاب حسب الكليات")
                with st.container():
                    st.markdown("""
                        <style>
                        .chart-container {
                            transition: all 0.3s ease;
                        }
                        .chart-container:hover {
                            transform: scale(1.01);
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    chart_data = {
                        "إجمالي الطلاب": [c['students_count'] for c in colleges],
                        "الطلاب الأجانب": [c.get('foreign_students', 0) for c in colleges],
                        "طلاب الدراسات العليا": [c.get('graduate_students', 0) for c in colleges],
                        "طلاب الأقسام الداخلية": [c.get('dorm_students', 0) for c in colleges],
                        "طلاب المسائي": [c.get('evening_students', 0) for c in colleges],
                        "طلاب المسائي المستضافين": [c.get('evening_hosted_students', 0) for c in colleges]
                    }

                    for category, values in chart_data.items():
                        st.bar_chart(
                            data={c['name']: v for c, v in zip(colleges, values)},
                            use_container_width=True
                        )
                        st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()