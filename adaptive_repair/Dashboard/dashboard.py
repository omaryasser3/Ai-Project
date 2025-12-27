"""
APR Evaluation Dashboard

A Streamlit dashboard for visualizing Automated Program Repair (APR) 
evaluation results across Python and Java programs.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_parser import get_parser

# Page configuration
st.set_page_config(
    page_title="APR Evaluation Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visual appeal
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-metric {
        color: #28a745;
    }
    .failure-metric {
        color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and parse APR evaluation results"""
    parser = get_parser()
    return parser.get_combined_summary()


def render_metrics_overview(data):
    """Render overview metrics cards"""
    st.header("📊 Evaluation Metrics Overview")
    
    # Check for Java data availability
    java_has_data = data['java']['total_tests'] > 0 or data['java']['errors'] > 0
    
    # Language selector
    view_mode = st.radio(
        "Select View:",
        ["Both", "Python", "Java"],
        horizontal=True,
        key="view_mode"
    )
    
    # Show warning if Java selected but no data
    if view_mode == "Java" and not java_has_data:
        st.warning("⚠️ Java test data not available. " + 
                  (data['java']['error_messages'][0] if data['java']['error_messages'] 
                   else "No test results found in Java verification file."))
    
    # Determine which data to show
    if view_mode == "Python":
        metrics_data = data['python']
    elif view_mode == "Java":
        metrics_data = data['java']
    else:
        # For combined view, only use Java if it has data
        if java_has_data:
            metrics_data = data['combined']
        else:
            metrics_data = data['python']
            st.info("ℹ️ Showing Python results only (Java data not available)")
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Tests",
            value=metrics_data['total_tests'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="✅ Passed",
            value=metrics_data['passed'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="❌ Failed",
            value=metrics_data['failed'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="⚠️ Errors",
            value=metrics_data['errors'],
            delta=None
        )
    
    with col5:
        st.metric(
            label="Success Rate",
            value=f"{metrics_data['success_rate']:.1f}%",
            delta=None
        )
    
    return view_mode, java_has_data


def render_comparison_charts(data):
    """Render Python vs Java comparison charts"""
    st.header("📈 Language Comparison")
    
    # Check Java data availability
    java_has_data = data['java']['total_tests'] > 0 or data['java']['errors'] > 0
    
    if not java_has_data:
        st.warning("⚠️ Java test results not available for comparison. " + 
                  (data['java']['error_messages'][0] if data['java']['error_messages'] 
                   else "No test results found in Java verification file."))
        st.info("Showing Python results only:")
        
        # Show Python results only
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Python Tests", data['python']['total_tests'])
            st.metric("Passed", data['python']['passed'])
            st.metric("Failed", data['python']['failed'])
        
        with col2:
            st.metric("Success Rate", f"{data['python']['success_rate']:.1f}%")
            st.metric("Errors", data['python']['errors'])
        
        return
    
    # Show Java algorithm info
    total_files = data['java'].get('total_algorithms', 0)
    # Use file counts, not test case counts
    files_passed = data['java'].get('files_passed', 0)
    files_failed = data['java'].get('files_failed', 0)
    compilation_failed = data['java'].get('compilation_failed', 0)
    total_test_cases = data['java']['total_tests']
    
    # Get test case stats
    test_cases_passed = data['java'].get('test_cases_passed', data['java']['passed'])
    test_cases_failed = data['java'].get('test_cases_failed', data['java']['failed'])
    
    st.info(
        f"📌 **Java Results**:\n\n"
        f"**Files**: {total_files} total | {files_passed} passed | {files_failed} failed | {compilation_failed} compilation errors\n\n"
        f"**Test Cases**: {total_test_cases} total | {test_cases_passed} passed | {test_cases_failed} failed"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pass/Fail Comparison")
        
        # Prepare data for comparison
        comparison_df = pd.DataFrame({
            'Language': ['Python', 'Java'],
            'Passed': [data['python']['passed'], data['java']['passed']],
            'Failed': [data['python']['failed'], data['java']['failed']]
        })
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(8, 5))
        x = range(len(comparison_df))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], comparison_df['Passed'], 
               width, label='Passed', color='#28a745')
        ax.bar([i + width/2 for i in x], comparison_df['Failed'], 
               width, label='Failed', color='#dc3545')
        
        ax.set_xlabel('Language')
        ax.set_ylabel('Number of Tests')
        ax.set_title('Test Results by Language')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_df['Language'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("Success Rate Comparison")
        
        # Success rate comparison
        success_df = pd.DataFrame({
            'Language': ['Python', 'Java'],
            'Success Rate': [
                data['python']['success_rate'],
                data['java']['success_rate']
            ]
        })
        
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(success_df['Language'], success_df['Success Rate'], 
                      color=['#007bff', '#ffc107'])
        
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Success Rate by Language')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom')
        
        st.pyplot(fig)
    
    # Error distribution
    st.subheader("Error Distribution")
    error_df = pd.DataFrame({
        'Language': ['Python', 'Java'],
        'Errors': [data['python']['errors'], data['java']['errors']]
    })
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(error_df['Language'], error_df['Errors'], color='#ff6b6b')
    ax.set_ylabel('Number of Errors')
    ax.set_title('Error Count by Language')
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)


def render_test_details(data, view_mode, java_has_data):
    """Render detailed test results"""
    st.header("🔍 Detailed Test Results")
    
    # Determine which language(s) to show
    languages_to_show = []
    if view_mode == "Both":
        languages_to_show = [('Python', data['python'])]
        if java_has_data:
            languages_to_show.append(('Java', data['java']))
    elif view_mode == "Python":
        languages_to_show = [('Python', data['python'])]
    else:
        languages_to_show = [('Java', data['java'])]
    
    for lang_name, lang_data in languages_to_show:
        # Check if this is Java data without actual tests
        if lang_name == 'Java' and not java_has_data:
            with st.expander(f"📝 {lang_name} Test Details", expanded=False):
                st.warning("No Java test data available. " + 
                          (lang_data['error_messages'][0] if lang_data['error_messages'] 
                           else "Java verification file does not contain test results."))
            continue
        
        # Get the total test count for the header
        total_test_count = lang_data.get('total_tests', len(lang_data['test_details']))
        
        with st.expander(f"📝 {lang_name} Test Details ({total_test_count} tests)", 
                        expanded=False):
            
            if not lang_data['test_details']:
                st.info(f"No detailed test information available for {lang_name}")
                continue
            
            # Filter options
            filter_option = st.selectbox(
                f"Filter {lang_name} tests:",
                ["All", "Passed Only", "Failed Only"],
                key=f"filter_{lang_name}"
            )
            
            # Filter tests based on selection
            filtered_tests = lang_data['test_details']
            if filter_option == "Passed Only":
                filtered_tests = [t for t in filtered_tests if t['status'] == 'PASSED']
            elif filter_option == "Failed Only":
                filtered_tests = [t for t in filtered_tests if t['status'] == 'FAILED']
            
            # Display tests in a dataframe
            if filtered_tests:
                df = pd.DataFrame(filtered_tests)
                
                # Style the dataframe
                def highlight_status(row):
                    if row['status'] == 'PASSED':
                        return ['background-color: #d4edda'] * len(row)
                    elif row['status'] == 'FAILED':
                        return ['background-color: #f8d7da'] * len(row)
                    return [''] * len(row)
                
                styled_df = df.style.apply(highlight_status, axis=1)
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"Download {lang_name} Test Results as CSV",
                    data=csv,
                    file_name=f"{lang_name.lower()}_test_results.csv",
                    mime="text/csv",
                    key=f"download_{lang_name}"
                )
            else:
                st.info(f"No tests match the selected filter")


def render_error_details(data, view_mode, java_has_data):
    """Render error messages and details"""
    st.header("⚠️ Error Details")
    
    # Determine which language(s) to show
    languages_to_show = []
    if view_mode == "Both":
        languages_to_show = [('Python', data['python'])]
        if java_has_data:
            languages_to_show.append(('Java', data['java']))
    elif view_mode == "Python":
        languages_to_show = [('Python', data['python'])]
    else:
        languages_to_show = [('Java', data['java'])]
    
    for lang_name, lang_data in languages_to_show:
        # Special handling for Java without data
        if lang_name == 'Java' and not java_has_data:
            with st.expander(f"🐛 {lang_name} Errors", expanded=False):
                st.warning("No Java test data available to show errors.")
                if lang_data['error_messages']:
                    st.info("File reading note: " + lang_data['error_messages'][0])
            continue
        
        with st.expander(f"🐛 {lang_name} Errors ({lang_data['errors']} total)", 
                        expanded=False):
            
            if not lang_data['error_messages']:
                st.success(f"No errors found in {lang_name} results!")
                continue
            
            st.write(f"Found {len(lang_data['error_messages'])} error messages:")
            
            # Display error messages
            for idx, error in enumerate(lang_data['error_messages'], 1):
                st.code(f"{idx}. {error}", language="text")


def render_summary_stats(data):
    """Render summary statistics table"""
    st.header("📋 Summary Statistics")
    
    summary_df = pd.DataFrame({
        'Metric': ['Total Tests', 'Passed', 'Failed', 'Errors', 'Success Rate (%)'],
        'Python': [
            data['python']['total_tests'],
            data['python']['passed'],
            data['python']['failed'],
            data['python']['errors'],
            f"{data['python']['success_rate']:.2f}"
        ],
        'Java': [
            data['java']['total_tests'],
            data['java']['passed'],
            data['java']['failed'],
            data['java']['errors'],
            f"{data['java']['success_rate']:.2f}"
        ],
        'Combined': [
            data['combined']['total_tests'],
            data['combined']['passed'],
            data['combined']['failed'],
            data['combined']['errors'],
            f"{data['combined']['success_rate']:.2f}"
        ]
    })
    
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Export summary
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="Export Summary as CSV",
        data=csv,
        file_name="apr_evaluation_summary.csv",
        mime="text/csv"
    )


def main():
    """Main application"""
    
    # Title
    st.title("🔧 APR Evaluation Dashboard")
    st.markdown("**Automated Program Repair Results Visualization**")
    st.markdown("---")
    
    # Load data
    try:
        with st.spinner("Loading evaluation results..."):
            data = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        st.markdown("Use this dashboard to explore APR evaluation results.")
        
        section = st.radio(
            "Select Section:",
            ["Overview", "Comparisons", "Test Details", "Error Details", "Summary Table"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "This dashboard visualizes results from Automated Program Repair "
            "evaluations on Python and Java test suites."
        )
        
        # Data info
        st.markdown("### Data Info")
        st.metric("Python Tests", data['python']['total_tests'])
        java_alg = data['java'].get('total_algorithms', data['java']['total_tests'])
        st.metric("Java Algorithms", java_alg)
        if java_alg > 0:
            st.caption(f"{data['java']['total_tests']} total test cases")
    
    # Check Java data availability
    java_has_data = data['java']['total_tests'] > 0 or data['java']['errors'] > 0
    
    # Main content based on selection
    if section == "Overview":
        view_mode, java_has_data = render_metrics_overview(data)
    elif section == "Comparisons":
        render_comparison_charts(data)
        view_mode = "Both"
    elif section == "Test Details":
        view_mode = st.radio(
            "Select Language:",
            ["Both", "Python", "Java"],
            horizontal=True
        )
        render_test_details(data, view_mode, java_has_data)
    elif section == "Error Details":
        view_mode = st.radio(
            "Select Language:",
            ["Both", "Python", "Java"],
            horizontal=True
        )
        render_error_details(data, view_mode, java_has_data)
    else:  # Summary Table
        render_summary_stats(data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "APR Evaluation Dashboard | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
