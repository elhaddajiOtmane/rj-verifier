import random
import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path
import itertools
import base64
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

def _calculate_progressive_fed_tax(gross_pay):
    """Calculate federal tax using progressive brackets (2024 tax brackets)"""
    # 2024 tax brackets for single filer
    if gross_pay <= 11000:
        return round(gross_pay * 0.10, 2)
    elif gross_pay <= 44725:
        return round(1100 + (gross_pay - 11000) * 0.12, 2)
    elif gross_pay <= 95375:
        return round(5147 + (gross_pay - 44725) * 0.22, 2)
    elif gross_pay <= 201050:
        return round(16290 + (gross_pay - 95375) * 0.24, 2)
    else:
        # Simplified for higher brackets
        return round(gross_pay * 0.22, 2)

def _generate_consistent_employee_id(first_name: str, last_name: str) -> str:
    """Generate consistent employee ID based on name hash"""
    name_hash = hashlib.md5(f"{first_name.lower()}{last_name.lower()}".encode()).hexdigest()
    # Convert first 7 chars to integer and format
    emp_num = int(name_hash[:7], 16) % 9000000 + 1000000
    return f"E-{emp_num}"

def _get_department_position(school_name: str) -> tuple:
    """Generate department and position based on school"""
    departments = [
        "Mathematics", "Science", "English", "Social Studies", 
        "Language Arts", "Physical Education", "Arts", "Special Education"
    ]
    positions = [
        "Teacher", "Senior Teacher", "Lead Teacher", "Department Chair"
    ]
    # Use school name hash for consistency
    school_hash = hash(school_name) % len(departments)
    pos_hash = hash(school_name + "pos") % len(positions)
    return departments[school_hash], positions[pos_hash]

def _render_template(html: str, first_name: str, last_name: str, school_name: str, address: str, logo_path: str = None) -> str:
    full_name = f"{first_name} {last_name}"
    # Check if this is NYC style template or Hudson County (which uses NYC format)
    is_nyc_style = "TEACHER'S PAYSTUB" in html or "NYCAPS" in html.upper() or "__NYC_STYLE__" in html or "Hudson County" in school_name
    
    # Generate consistent employee ID from name
    employee_id_base = _generate_consistent_employee_id(first_name, last_name)
    employee_id_num = employee_id_base.replace("E-", "")
    
    # For NYC style, use numeric ID only (7 digits)
    if is_nyc_style:
        employee_id_str = employee_id_num
    else:
        employee_id_str = employee_id_base
    # Generate advice ID based on date and employee ID for consistency
    now = datetime.now()
    advice_id = int(employee_id_num) + (now.year * 10000) + (now.month * 100) + now.day
    
    pay_date = now.strftime("%m/%d/%Y")
    period_end = now.strftime("%m/%d/%Y")
    
    from datetime import timedelta
    if is_nyc_style:
        # Semi-monthly: typically 1st-15th and 16th-end of month
        if now.day <= 15:
            period_start_dt = datetime(now.year, now.month, 1)
            period_end_dt = datetime(now.year, now.month, 15)
        else:
            period_start_dt = datetime(now.year, now.month, 16)
            # Get last day of month
            if now.month == 12:
                period_end_dt = datetime(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end_dt = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
        period_start = period_start_dt.strftime("%m/%d/%Y")
        period_end = period_end_dt.strftime("%m/%d/%Y")
        # Calculate pay period (1-24 for semi-monthly)
        pay_period_num = (now.month - 1) * 2 + (2 if now.day > 15 else 1)
    else:
        period_start_dt = now - timedelta(days=14)
        period_start = period_start_dt.strftime("%m/%d/%Y")
        # Calculate pay period number (bi-weekly, assuming 26 periods per year)
        day_of_year = now.timetuple().tm_yday
        pay_period_num = (day_of_year // 14) + 1
        if pay_period_num > 26:
            pay_period_num = 26
    
    pay_month = now.strftime("%B %Y")
    
    # Get department and position
    department, position = _get_department_position(school_name)
    
    if logo_path:
         final_logo_path = Path(logo_path)
    else:
        if is_nyc_style or "Hudson County" in school_name or "Jersey City" in school_name:
            # Use NYC DOE logo for NYC style or Hudson County
            logo_filename = "NYC_DOE_Logo.png"
        elif "Malcolm X" in school_name or "Chicago" in school_name:
            logo_filename = "MXC.png"
        else:
            logo_filename = "SHS.png"
        
        try:
             from . import config
        except ImportError:
             import config
             
        assets_dir = config.get_assets_dir()
        possible_paths = [
            assets_dir / logo_filename,
            assets_dir / "NYC_DOE_Logo.png",  # Fallback to NYC logo
            assets_dir / "aassetlogo.png"
        ]
        
        final_logo_path = None
        for p in possible_paths:
            if p.exists():
                final_logo_path = p
                break
                
    # Use consistent random seed based on employee ID for consistent salary
    random.seed(int(employee_id_num))
    
    # Check template style from function signature - we'll determine based on template selection
    # For now, default to bi-weekly, but can be overridden by template style
    pay_frequency_default = "Bi-weekly"
    
    # More realistic teacher salary
    if is_nyc_style:
        # NYC teachers typically earn $55k-$85k annually, semi-monthly pay
        annual_salary_base = random.uniform(70000, 90000)
        pay_frequency = "Semi-monthly"
        
        # Regular gross - base salary divided by 24 (semi-monthly)
        regular_gross = round(annual_salary_base / 24, 2)
        # Regular gross hours (typically 75-80 hours per semi-monthly period)
        regular_hours = round(random.uniform(75.0, 80.0), 2)
        
        # Additional earnings for NYC teachers
        random.seed(int(employee_id_num) + 3000)
        # Per session work (after school, weekends) - typically 10-15 hours
        per_session_hours = round(random.uniform(10.0, 15.0), 2)
        per_session_rate = round(random.uniform(48.0, 52.0), 2)
        per_session_pay = round(per_session_hours * per_session_rate, 2)
        
        # Coverage pay (covering other classes) - typically 4-6 hours
        coverage_hours = round(random.uniform(4.0, 6.0), 2)
        coverage_rate = round(random.uniform(38.0, 42.0), 2)
        coverage_pay = round(coverage_hours * coverage_rate, 2)
        
        # MA Differential (Masters degree differential)
        ma_differential = round(random.uniform(140, 160), 2)
        
        # Longevity pay (based on years of service)
        longevity_pay = round(random.uniform(70, 80), 2)
        random.seed()
        
        gross_pay = round(regular_gross + per_session_pay + coverage_pay + ma_differential + longevity_pay, 2)
        regular_pay = regular_gross  # For backwards compatibility
        hours_worked = regular_hours
        hourly_rate = round(regular_gross / regular_hours, 2)
        stipend = per_session_pay + coverage_pay + ma_differential + longevity_pay
    else:
        # Other districts: $55k-$75k annually, bi-weekly
        annual_salary_base = random.uniform(55000, 75000)
        pay_frequency = "Bi-weekly"
        biweekly_gross_base = annual_salary_base / 26
        # Calculate hourly equivalent for display (80 hours per pay period)
        hours_worked = 80.0
        hourly_rate = round(biweekly_gross_base / hours_worked, 2)
        regular_pay = round(hourly_rate * hours_worked, 2)
        # Stipend (consistent based on employee)
        stipend_choices = [0, 75, 100, 150, 200]
        stipend = stipend_choices[int(employee_id_num) % len(stipend_choices)]
        gross_pay = round(regular_pay + stipend, 2)
        # Initialize NYC-specific variables for non-NYC
        regular_gross = regular_pay
        regular_hours = hours_worked
        per_session_hours = 0
        per_session_pay = 0
        coverage_hours = 0
        coverage_pay = 0
        ma_differential = 0
        longevity_pay = 0
        qpp_pension = 0
        trs_414h = 0
        nys_pfl = 0
        union_welfare = 0
    
    # Reset random seed for other calculations
    random.seed()
    
    # Tax calculations
    ss_tax_rate = 0.062  # Social Security (6.2%)
    med_tax_rate = 0.0145  # Medicare (1.45%)
    
    # Progressive federal tax
    fed_tax = _calculate_progressive_fed_tax(gross_pay)
    
    # State tax (3-5% typical range, consistent per employee)
    random.seed(int(employee_id_num) + 1000)
    
    if is_nyc_style:
        # NYC tax rates are different
        # NY State tax: ~4-5% for NYC teachers
        state_tax_rate = random.uniform(0.042, 0.048)
        state_tax = round(gross_pay * state_tax_rate, 2)
        # NYC City tax: ~3-4% of gross
        city_tax_rate = random.uniform(0.03, 0.04)
        city_tax = round(gross_pay * city_tax_rate, 2)
    else:
        state_tax_rate = random.uniform(0.035, 0.048)
        state_tax = round(gross_pay * state_tax_rate, 2)
        city_tax = 0  # No city tax for non-NYC
    
    random.seed()
    
    ss_tax = round(gross_pay * ss_tax_rate, 2)
    med_tax = round(gross_pay * med_tax_rate, 2)
    
    # Benefits deductions (consistent per employee)
    random.seed(int(employee_id_num) + 2000)
    
    if is_nyc_style:
        # NYC specific deductions
        # Health benefits GHI-CBP - typically $90-100 per pay period
        health_insurance = round(random.uniform(90, 100), 2)
        dental_insurance = 0  # Usually included in health for NYC
        vision_insurance = 0  # Usually included in health for NYC
        # TDA (Tax-Deferred Annuity) - typically 5% of gross for NYC
        tda_rate = random.uniform(0.065, 0.075)
        tda_contribution = round(gross_pay * tda_rate, 2)
        # UFT DUES (United Federation of Teachers) - typically $48-50 per pay period
        uft_dues = round(random.uniform(48, 50), 2)
        # QPP PENSION (Qualified Pension Plan) - typically 4-5% of gross
        qpp_rate = random.uniform(0.040, 0.045)
        qpp_pension = round(gross_pay * qpp_rate, 2)
        # TRS 414H (Teachers Retirement System) - typically $50-60 per pay period
        trs_414h = round(random.uniform(50, 60), 2)
        # NYS Paid Family Leave - small amount, typically $20-25
        nys_pfl = round(random.uniform(20, 25), 2)
        # Union Welfare Fund - typically $35 per pay period
        union_welfare = round(random.uniform(35, 36), 2)
    else:
        health_insurance = round(random.uniform(120, 180), 2)
        dental_insurance = round(random.uniform(15, 30), 2)
        vision_insurance = round(random.uniform(8, 15), 2)
        # TDA/Retirement contribution - typically 3-5% of gross
        tda_rate = random.uniform(0.03, 0.05)
        tda_contribution = round(gross_pay * tda_rate, 2)
        uft_dues = 0  # No union dues for non-NYC
        qpp_pension = 0
        trs_414h = 0
        nys_pfl = 0
        union_welfare = 0
    
    random.seed()
    
    # Total deductions
    tax_deductions = fed_tax + ss_tax + med_tax + state_tax + city_tax
    if is_nyc_style:
        benefits_deductions = health_insurance + tda_contribution + uft_dues + qpp_pension + trs_414h + nys_pfl + union_welfare
    else:
        benefits_deductions = health_insurance + dental_insurance + vision_insurance + tda_contribution + uft_dues
    total_deductions = round(tax_deductions + benefits_deductions, 2)
    net_pay = round(gross_pay - total_deductions, 2)
    
    # Year-to-Date calculations
    if is_nyc_style:
        # Semi-monthly: 24 periods per year
        pay_period_num_ytd = min(pay_period_num, 24)
    else:
        # Bi-weekly: 26 periods per year
        pay_period_num_ytd = min(pay_period_num, 26)
    
    ytd_gross = round(gross_pay * pay_period_num_ytd, 2)
    ytd_regular_gross = round(regular_gross * pay_period_num_ytd, 2)
    ytd_per_session = round(per_session_pay * pay_period_num_ytd, 2)
    ytd_coverage = round(coverage_pay * pay_period_num_ytd, 2)
    ytd_ma_diff = round(ma_differential * pay_period_num_ytd, 2)
    ytd_longevity = round(longevity_pay * pay_period_num_ytd, 2)
    ytd_fed_tax = round(fed_tax * pay_period_num_ytd, 2)
    ytd_ss_tax = round(ss_tax * pay_period_num_ytd, 2)
    ytd_med_tax = round(med_tax * pay_period_num_ytd, 2)
    ytd_state_tax = round(state_tax * pay_period_num_ytd, 2)
    ytd_city_tax = round(city_tax * pay_period_num_ytd, 2)
    ytd_health_ins = round(health_insurance * pay_period_num_ytd, 2)
    ytd_tda = round(tda_contribution * pay_period_num_ytd, 2)
    ytd_uft_dues = round(uft_dues * pay_period_num_ytd, 2)
    ytd_qpp = round(qpp_pension * pay_period_num_ytd, 2)
    ytd_trs = round(trs_414h * pay_period_num_ytd, 2)
    ytd_nys_pfl = round(nys_pfl * pay_period_num_ytd, 2)
    ytd_union_welfare = round(union_welfare * pay_period_num_ytd, 2)
    ytd_benefits = round(benefits_deductions * pay_period_num_ytd, 2)
    ytd_deductions = round(total_deductions * pay_period_num_ytd, 2)
    ytd_net = round(net_pay * pay_period_num_ytd, 2)
    
    # Leave balances (for NYC style)
    if is_nyc_style:
        random.seed(int(employee_id_num) + 5000)
        car_days = round(random.uniform(15.0, 20.0), 2)
        annual_leave = round(random.uniform(5.0, 10.0), 2)
        random.seed()
    else:
        car_days = 0
        annual_leave = 0
    
    # File number (for NYC style) - consistent based on employee
    if is_nyc_style:
        random.seed(int(employee_id_num) + 6000)
        file_number = f"{random.randint(800000, 999999)}"
        random.seed()
    else:
        file_number = ""
    
    # Job title
    job_title = f"{position} - {department.upper()}" if not is_nyc_style else f"TEACHER - {department.upper()}"
    def fmt(val):
        return f"{val:,.2f}"
    
    if final_logo_path and final_logo_path.exists():
        encoded_logo = base64.b64encode(final_logo_path.read_bytes()).decode('utf-8')
        logo_data_uri = f"data:image/png;base64,{encoded_logo}"
    else:
        logo_data_uri = "" 

    # Replace all template placeholders
    html = html.replace("__LOGO_DATA_URI__", logo_data_uri)
    html = html.replace("LOGO_DATA_URI_PLACEHOLDER", logo_data_uri) 
    html = html.replace("__SCHOOL_NAME__", school_name)
    html = html.replace("__SCHOOL_ADDRESS__", address)
    
    # For NYC style template, use NYC DOE as employer if not specified
    if is_nyc_style and "__EMPLOYER__" in html:
        employer_name = "NYC DEPARTMENT OF EDUCATION" if "Hudson County" not in school_name else school_name.upper()
        html = html.replace("__EMPLOYER__", employer_name)
    html = html.replace("__EMP_NAME__", full_name)
    html = html.replace("__EMP_ID__", employee_id_str)
    html = html.replace("__ADVICE_ID__", str(advice_id))
    html = html.replace("__PAY_DATE__", pay_date)
    html = html.replace("__PAY_MONTH__", pay_month)
    html = html.replace("__PERIOD_START__", period_start)
    html = html.replace("__PERIOD_END__", period_end)
    html = html.replace("__PAY_FREQUENCY__", pay_frequency)
    html = html.replace("__DEPARTMENT__", department)
    html = html.replace("__POSITION__", position)
    
    # Current period earnings and deductions
    html = html.replace("__REG_PAY__", fmt(regular_pay))
    html = html.replace("__OTHER_PAY__", fmt(stipend))
    html = html.replace("__GROSS_PAY__", fmt(gross_pay))
    html = html.replace("__FED_TAX__", fmt(fed_tax))
    html = html.replace("__SS_TAX__", fmt(ss_tax))
    html = html.replace("__MED_TAX__", fmt(med_tax))
    html = html.replace("__STATE_TAX__", fmt(state_tax))
    html = html.replace("__CITY_TAX__", fmt(city_tax))
    html = html.replace("__HEALTH_INS__", fmt(health_insurance))
    html = html.replace("__DENTAL_INS__", fmt(dental_insurance))
    html = html.replace("__VISION_INS__", fmt(vision_insurance))
    html = html.replace("__RETIREMENT__", fmt(tda_contribution))
    html = html.replace("__TDA_CONTRIBUTION__", fmt(tda_contribution))
    html = html.replace("__UFT_DUES__", fmt(uft_dues))
    html = html.replace("__TOTAL_DED__", fmt(total_deductions))
    html = html.replace("__NET_PAY__", fmt(net_pay))
    html = html.replace("__HOURLY_RATE__", fmt(hourly_rate))
    html = html.replace("__HOURS_WORKED__", fmt(hours_worked))
    html = html.replace("__REGULAR_SALARY__", fmt(regular_pay))
    html = html.replace("__REGULAR_GROSS__", fmt(regular_gross))
    html = html.replace("__REGULAR_HOURS__", fmt(regular_hours))
    html = html.replace("__PER_SESSION_HOURS__", fmt(per_session_hours))
    html = html.replace("__PER_SESSION_PAY__", fmt(per_session_pay))
    html = html.replace("__COVERAGE_HOURS__", fmt(coverage_hours))
    html = html.replace("__COVERAGE_PAY__", fmt(coverage_pay))
    html = html.replace("__MA_DIFFERENTIAL__", fmt(ma_differential))
    html = html.replace("__LONGEVITY_PAY__", fmt(longevity_pay))
    html = html.replace("__QPP_PENSION__", fmt(qpp_pension))
    html = html.replace("__TRS_414H__", fmt(trs_414h))
    html = html.replace("__NYS_PFL__", fmt(nys_pfl))
    html = html.replace("__UNION_WELFARE__", fmt(union_welfare))
    html = html.replace("__FILE_NUMBER__", file_number)
    html = html.replace("__JOB_TITLE__", job_title)
    html = html.replace("__CAR_DAYS__", fmt(car_days))
    html = html.replace("__ANNUAL_LEAVE__", fmt(annual_leave))
    
    # Year-to-Date values
    html = html.replace("__YTD_GROSS__", fmt(ytd_gross))
    html = html.replace("__YTD_FED_TAX__", fmt(ytd_fed_tax))
    html = html.replace("__YTD_SS_TAX__", fmt(ytd_ss_tax))
    html = html.replace("__YTD_MED_TAX__", fmt(ytd_med_tax))
    html = html.replace("__YTD_STATE_TAX__", fmt(ytd_state_tax))
    html = html.replace("__YTD_CITY_TAX__", fmt(ytd_city_tax))
    html = html.replace("__YTD_HEALTH_INS__", fmt(ytd_health_ins))
    html = html.replace("__YTD_TDA_CONTRIBUTION__", fmt(ytd_tda))
    html = html.replace("__YTD_UFT_DUES__", fmt(ytd_uft_dues))
    html = html.replace("__YTD_REGULAR_GROSS__", fmt(ytd_regular_gross))
    html = html.replace("__YTD_PER_SESSION__", fmt(ytd_per_session))
    html = html.replace("__YTD_COVERAGE__", fmt(ytd_coverage))
    html = html.replace("__YTD_MA_DIFF__", fmt(ytd_ma_diff))
    html = html.replace("__YTD_LONGEVITY__", fmt(ytd_longevity))
    html = html.replace("__YTD_QPP__", fmt(ytd_qpp))
    html = html.replace("__YTD_TRS__", fmt(ytd_trs))
    html = html.replace("__YTD_NYS_PFL__", fmt(ytd_nys_pfl))
    html = html.replace("__YTD_UNION_WELFARE__", fmt(ytd_union_welfare))
    html = html.replace("__YTD_DEDUCTIONS__", fmt(ytd_deductions))
    html = html.replace("__YTD_NET__", fmt(ytd_net))

    return html


def generate_teacher_pdf(first_name: str, last_name: str, school_name: str = "Springfield High School") -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright required for PDF generation") from exc
import itertools
_TEMPLATE_CYCLE = None

def _get_template_file_by_style(templates_dir: Path, style: str) -> Path:
    """Select template based on style name"""
    style_map = {
        'modern': 'template_modern.html',
        'original': 'template_original.html',
        'simple': 'template_simple.html',
        'portal': 'template_portal.html',
        'nyc': 'template_nyc.html'
    }
    filename = style_map.get(style, 'template_modern.html')
    return templates_dir / filename

def generate_teacher_pdf(first_name: str, last_name: str, school_name: str = "Springfield High School", address: str = "640 A St, Springfield, OR 97477", style: str = "modern", logo_path: str = None) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright required for PDF generation") from exc
        
    try:
        from . import config
    except ImportError:
        import config
    templates_dir = config.get_templates_dir()
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
        
    template_file = _get_template_file_by_style(templates_dir, style)
    if not template_file.exists():
        template_file = templates_dir / "template_modern.html"
        
    html_content = template_file.read_text(encoding="utf-8")
    
    html = _render_template(html_content, first_name, last_name, school_name, address, logo_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 816, "height": 1056}) 
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(500)
        pdf_bytes = page.pdf(format="Letter", print_background=True, margin={"top": "0.4in", "right": "0.4in", "bottom": "0.4in", "left": "0.4in"})
        browser.close()
        
    return pdf_bytes


def generate_teacher_png(first_name: str, last_name: str, school_name: str = "Springfield High School", address: str = "640 A St, Springfield, OR 97477", style: str = "modern", logo_path: str = None) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright required") from exc
        
    try:
        from . import config
    except ImportError:
        import config
    templates_dir = config.get_templates_dir()
    template_file = _get_template_file_by_style(templates_dir, style)
    if not template_file.exists():
         template_file = templates_dir / "template_modern.html"
    
    html_content = template_file.read_text(encoding="utf-8")
    html = _render_template(html_content, first_name, last_name, school_name, address, logo_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1000, "height": 1200})
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(500)
        card = page.locator("body") 
        png_bytes = card.screenshot(type="png")
        browser.close()
    
    return png_bytes
def generate_teacher_image(first_name: str, last_name: str, school_name: str = "Springfield High School") -> bytes:
    return generate_teacher_pdf(first_name, last_name, school_name)
