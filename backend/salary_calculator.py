from datetime import datetime, timezone
from typing import Dict, List
import calendar

class SalaryCalculator:
    """
    Government-compliant salary calculator for Indian employees
    Includes ESI, PF, PT calculations as per 2024 regulations
    """
    
    # Government rates (as per 2024 regulations)
    ESI_RATE = 0.0175  # 1.75% of gross salary
    ESI_WAGE_LIMIT = 21000  # ESI applicable only if gross salary <= 21,000
    PF_RATE = 0.12  # 12% of basic salary
    PF_WAGE_LIMIT = 15000  # PF calculated on basic salary, max 15,000
    
    # Professional Tax rates (Karnataka state)
    PT_RATES = [
        (0, 10000, 0),        # No PT for salary <= 10,000
        (10001, 15000, 150),  # ₹150 for salary 10,001-15,000
        (15001, 25000, 200),  # ₹200 for salary 15,001-25,000
        (25001, float('inf'), 200)  # ₹200 for salary > 25,000
    ]
    
    # Standard allowance rates
    HRA_RATE_METRO = 0.50    # 50% of basic in metro cities
    HRA_RATE_NON_METRO = 0.40  # 40% of basic in non-metro cities
    DA_RATE = 0.10           # 10% of basic salary
    
    def __init__(self, is_metro_city: bool = False, state: str = "Karnataka"):
        self.is_metro_city = is_metro_city
        self.state = state
        
    def calculate_monthly_salary(self, basic_salary: float, present_days: int, 
                               total_working_days: int, allowances: Dict = None) -> Dict:
        """
        Calculate monthly salary with all components and deductions
        
        Args:
            basic_salary: Basic salary per month
            present_days: Number of days employee was present
            total_working_days: Total working days in the month
            allowances: Additional allowances (optional)
            
        Returns:
            Complete salary breakdown dictionary
        """
        if allowances is None:
            allowances = {}
            
        # Calculate pro-rated basic salary based on attendance
        attendance_ratio = present_days / total_working_days if total_working_days > 0 else 0
        prorated_basic = basic_salary * attendance_ratio
        
        # Calculate standard allowances
        hra_rate = self.HRA_RATE_METRO if self.is_metro_city else self.HRA_RATE_NON_METRO
        hra = prorated_basic * hra_rate
        da = prorated_basic * self.DA_RATE
        
        # Additional allowances
        medical_allowance = allowances.get('medical', 1250) * attendance_ratio
        transport_allowance = allowances.get('transport', 1600) * attendance_ratio
        special_allowance = allowances.get('special', 0) * attendance_ratio
        
        # Calculate gross salary
        gross_salary = (prorated_basic + hra + da + medical_allowance + 
                       transport_allowance + special_allowance)
        
        # Calculate deductions
        deductions = self.calculate_deductions(prorated_basic, gross_salary)
        
        # Calculate net salary
        net_salary = gross_salary - deductions['total_deductions']
        
        return {
            'employee_details': {
                'present_days': present_days,
                'total_working_days': total_working_days,
                'attendance_percentage': round(attendance_ratio * 100, 2)
            },
            'earnings': {
                'basic_salary': round(prorated_basic, 2),
                'hra': round(hra, 2),
                'da': round(da, 2),
                'medical_allowance': round(medical_allowance, 2),
                'transport_allowance': round(transport_allowance, 2),
                'special_allowance': round(special_allowance, 2),
                'gross_salary': round(gross_salary, 2)
            },
            'deductions': deductions,
            'net_salary': round(net_salary, 2),
            'employer_contributions': {
                'pf_employer': round(deductions['pf_employer'], 2),
                'esi_employer': round(deductions['esi_employer'], 2),
                'total_employer_contribution': round(deductions['pf_employer'] + deductions['esi_employer'], 2)
            }
        }
    
    def calculate_deductions(self, basic_salary: float, gross_salary: float) -> Dict:
        """Calculate all statutory deductions"""
        
        # PF Calculation (12% of basic salary, max on 15,000)
        pf_eligible_salary = min(basic_salary, self.PF_WAGE_LIMIT)
        pf_employee = pf_eligible_salary * self.PF_RATE
        pf_employer = pf_eligible_salary * self.PF_RATE  # Employer contribution
        
        # ESI Calculation (1.75% of gross salary, only if gross <= 21,000)
        if gross_salary <= self.ESI_WAGE_LIMIT:
            esi_employee = gross_salary * self.ESI_RATE
            esi_employer = gross_salary * 0.0475  # 4.75% employer contribution
        else:
            esi_employee = 0
            esi_employer = 0
        
        # Professional Tax calculation
        pt = self.calculate_professional_tax(gross_salary)
        
        # Income Tax (basic calculation - can be enhanced)
        income_tax = self.calculate_income_tax(gross_salary)
        
        total_deductions = pf_employee + esi_employee + pt + income_tax
        
        return {
            'pf_employee': round(pf_employee, 2),
            'pf_employer': round(pf_employer, 2),
            'esi_employee': round(esi_employee, 2),
            'esi_employer': round(esi_employer, 2),
            'professional_tax': round(pt, 2),
            'income_tax': round(income_tax, 2),
            'total_deductions': round(total_deductions, 2)
        }
    
    def calculate_professional_tax(self, gross_salary: float) -> float:
        """Calculate Professional Tax based on state regulations"""
        monthly_salary = gross_salary
        
        for min_sal, max_sal, pt_amount in self.PT_RATES:
            if min_sal <= monthly_salary <= max_sal:
                return pt_amount
        
        return 0
    
    def calculate_income_tax(self, gross_salary: float) -> float:
        """Basic Income Tax calculation (simplified)"""
        annual_salary = gross_salary * 12
        
        # Basic exemption limit for FY 2024-25 (New Tax Regime)
        if annual_salary <= 300000:
            return 0
        elif annual_salary <= 600000:
            # 5% on income between 3-6 lakhs
            taxable = annual_salary - 300000
            annual_tax = taxable * 0.05
        elif annual_salary <= 900000:
            # 5% on 3-6 lakhs + 10% on 6-9 lakhs
            annual_tax = 300000 * 0.05 + (annual_salary - 600000) * 0.10
        elif annual_salary <= 1200000:
            # Previous + 15% on 9-12 lakhs
            annual_tax = 300000 * 0.05 + 300000 * 0.10 + (annual_salary - 900000) * 0.15
        else:
            # Previous + 20% on above 12 lakhs
            annual_tax = 300000 * 0.05 + 300000 * 0.10 + 300000 * 0.15 + (annual_salary - 1200000) * 0.20
        
        # Monthly income tax
        monthly_tax = annual_tax / 12
        return monthly_tax
    
    def get_working_days_in_month(self, year: int, month: int) -> int:
        """Calculate working days in a month (excluding Sundays)"""
        # Get total days in month
        total_days = calendar.monthrange(year, month)[1]
        
        # Count working days (excluding Sundays)
        working_days = 0
        for day in range(1, total_days + 1):
            date_obj = datetime(year, month, day)
            # Skip Sundays (weekday 6)
            if date_obj.weekday() != 6:
                working_days += 1
                
        return working_days
    
    def calculate_annual_salary(self, monthly_calculations: List[Dict]) -> Dict:
        """Calculate annual salary summary from monthly calculations"""
        annual_gross = sum(month['earnings']['gross_salary'] for month in monthly_calculations)
        annual_deductions = sum(month['deductions']['total_deductions'] for month in monthly_calculations)
        annual_net = sum(month['net_salary'] for month in monthly_calculations)
        
        total_present_days = sum(month['employee_details']['present_days'] for month in monthly_calculations)
        total_working_days = sum(month['employee_details']['total_working_days'] for month in monthly_calculations)
        
        return {
            'annual_gross_salary': round(annual_gross, 2),
            'annual_deductions': round(annual_deductions, 2),
            'annual_net_salary': round(annual_net, 2),
            'total_present_days': total_present_days,
            'total_working_days': total_working_days,
            'annual_attendance_percentage': round((total_present_days / total_working_days * 100) if total_working_days > 0 else 0, 2),
            'monthly_breakdown': monthly_calculations
        }

# Utility functions for integration with HRMS
def get_employee_attendance_days(attendance_records: List[Dict], year: int, month: int) -> int:
    """Count present days from attendance records for a specific month"""
    present_days = 0
    
    for record in attendance_records:
        record_date = record.get('date', '')
        if isinstance(record_date, str):
            try:
                date_obj = datetime.fromisoformat(record_date.replace('Z', '+00:00'))
                if date_obj.year == year and date_obj.month == month:
                    present_days += 1
            except:
                # Handle date parsing errors
                continue
    
    return present_days

def calculate_employee_salary(employee_data: Dict, attendance_records: List[Dict], 
                            year: int = None, month: int = None) -> Dict:
    """
    Calculate salary for an employee based on attendance data
    
    Args:
        employee_data: Employee information including basic salary
        attendance_records: List of attendance records
        year: Year for calculation (default: current year)
        month: Month for calculation (default: current month)
        
    Returns:
        Complete salary calculation
    """
    if year is None or month is None:
        now = datetime.now(timezone.utc)
        year = year or now.year
        month = month or now.month
    
    # Initialize salary calculator (assuming Bangalore - metro city)
    calculator = SalaryCalculator(is_metro_city=True, state="Karnataka")
    
    # Get working days for the month
    total_working_days = calculator.get_working_days_in_month(year, month)
    
    # Get present days from attendance
    present_days = get_employee_attendance_days(attendance_records, year, month)
    
    # Get basic salary from employee data
    basic_salary = float(employee_data.get('basic_salary', 0))
    
    # Calculate salary
    salary_calculation = calculator.calculate_monthly_salary(
        basic_salary=basic_salary,
        present_days=present_days,
        total_working_days=total_working_days
    )
    
    # Add employee information
    salary_calculation['employee_info'] = {
        'employee_id': employee_data.get('employee_id', ''),
        'employee_name': employee_data.get('full_name', ''),
        'department': employee_data.get('department', ''),
        'designation': employee_data.get('designation', ''),
        'calculation_month': f"{calendar.month_name[month]} {year}"
    }
    
    return salary_calculation