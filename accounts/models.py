from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
	pass 



class PromptTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template = models.TextField()
    default_parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_default_templates(cls):
        # Create balance sheet template if it doesn't exist
        if not cls.objects.filter(name="Balance Sheet Analysis").exists():
            cls.objects.create(
                name="Balance Sheet Analysis",
                description="Analyze balance sheet data with key ratios and insights",
                template="""Analyze the following balance sheet data:
								Company: {company_name}
								Period: {period}

								Assets:
								{assets}

								Liabilities:
								{liabilities}

								Equity:
								{equity}

								Please provide:
								1. Key Financial Ratios
								2. Working Capital Analysis
								3. Key Insights
								4. Recommendations""",
                default_parameters={
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 0.95
                }
            )

class QueryHistory(models.Model):
    template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    input_data = models.JSONField()
    parameters = models.JSONField()
    prompt = models.TextField()
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    error = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Query histories'




from django.core.validators import MinValueValidator, MaxValueValidator

class Company(models.Model):
    """Company profile and metadata"""
    name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=10, unique=True)
    cik = models.CharField(max_length=10, unique=True)
    industry = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'Companies'
        
    def __str__(self):
        return f"{self.name} ({self.ticker})"

class Document10K(models.Model):
    """Store 10-K document metadata and content"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    filing_date = models.DateField()
    fiscal_year = models.IntegerField()
    document_url = models.URLField()
    raw_content = models.TextField()
    parsed_content = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['company', 'fiscal_year']
        ordering = ['-filing_date']

class AnalysisTemplate(models.Model):
    """Templates for different types of 10-K analysis"""
    TEMPLATE_TYPES = [
        ('financial', 'Financial Analysis'),
        ('risk', 'Risk Analysis'),
        ('md_and_a', 'MD&A Analysis'),
        ('business', 'Business Overview'),
        ('legal', 'Legal Proceedings'),
        ('market', 'Market Analysis'),
        ('custom', 'Custom Analysis')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    prompt_template = models.TextField()
    default_parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def create_default_templates(cls):
        default_templates = [
            {
                'name': 'Financial Statement Analysis',
                'template_type': 'financial',
                'description': 'Analyze key financial statements and metrics',
                'prompt_template': '''
                Analyze the financial statements for {company_name} ({fiscal_year}):

                Income Statement:
                {income_statement}

                Balance Sheet:
                {balance_sheet}

                Cash Flow:
                {cash_flow}

                Please provide:
                1. Key Financial Metrics and Ratios
                2. Year-over-Year Trends
                3. Industry Comparison
                4. Red Flags or Areas of Concern
                5. Growth Opportunities
                6. Recommendations
                '''
            },
            {
                'name': 'Risk Factor Analysis',
                'template_type': 'risk',
                'description': 'Analyze risk factors and their potential impact',
                'prompt_template': '''
                Analyze the risk factors for {company_name} ({fiscal_year}):

                Risk Factors:
                {risk_factors}

                Please provide:
                1. Key Risk Categories
                2. Risk Severity Assessment
                3. New Risks vs Previous Year
                4. Mitigation Strategies
                5. Industry-Specific Risks
                6. Recommendations for Risk Management
                '''
            },
            {
                'name': "MD&A Deep Dive",
                'template_type': 'md_and_a',
                'description': "Analyze Management's Discussion and Analysis",
                'prompt_template': '''
                Analyze the MD&A for {company_name} ({fiscal_year}):

                MD&A Content:
                {mda_content}

                Please provide:
                1. Key Business Drivers
                2. Management's Strategic Focus
                3. Operational Challenges
                4. Future Outlook
                5. Capital Allocation Strategy
                6. Key Performance Indicators
                '''
            }
        ]
        
        for template in default_templates:
            cls.objects.get_or_create(
                name=template['name'],
                defaults={
                    'template_type': template['template_type'],
                    'description': template['description'],
                    'prompt_template': template['prompt_template'],
                    'default_parameters': {
                        'temperature': 0.7,
                        'max_tokens': 2000,
                        'top_p': 0.95
                    }
                }
            )

class Analysis(models.Model):
    """Store analysis results and metadata"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document = models.ForeignKey(Document10K, on_delete=models.CASCADE)
    template = models.ForeignKey(AnalysisTemplate, on_delete=models.CASCADE)
    input_data = models.JSONField()
    parameters = models.JSONField()
    analysis_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Analyses'
        ordering = ['-created_at']

class FinancialMetrics(models.Model):
    """Store extracted financial metrics"""
    document = models.OneToOneField(Document10K, on_delete=models.CASCADE)
    
    # Profitability
    revenue = models.DecimalField(max_digits=20, decimal_places=2)
    net_income = models.DecimalField(max_digits=20, decimal_places=2)
    operating_income = models.DecimalField(max_digits=20, decimal_places=2)
    gross_margin = models.DecimalField(max_digits=5, decimal_places=2)
    operating_margin = models.DecimalField(max_digits=5, decimal_places=2)
    net_margin = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Balance Sheet
    total_assets = models.DecimalField(max_digits=20, decimal_places=2)
    total_liabilities = models.DecimalField(max_digits=20, decimal_places=2)
    total_equity = models.DecimalField(max_digits=20, decimal_places=2)
    current_assets = models.DecimalField(max_digits=20, decimal_places=2)
    current_liabilities = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Cash Flow
    operating_cash_flow = models.DecimalField(max_digits=20, decimal_places=2)
    investing_cash_flow = models.DecimalField(max_digits=20, decimal_places=2)
    financing_cash_flow = models.DecimalField(max_digits=20, decimal_places=2)
    free_cash_flow = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Key Ratios
    current_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    quick_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    debt_to_equity = models.DecimalField(max_digits=5, decimal_places=2)
    return_on_equity = models.DecimalField(max_digits=5, decimal_places=2)
    return_on_assets = models.DecimalField(max_digits=5, decimal_places=2)
    asset_turnover = models.DecimalField(max_digits=5, decimal_places=2)

class RiskMetrics(models.Model):
    """Store risk-related metrics and assessments"""
    document = models.OneToOneField(Document10K, on_delete=models.CASCADE)
    risk_categories = models.JSONField()  # Store categorized risks
    risk_scores = models.JSONField()      # Store risk severity scores
    year_over_year_changes = models.JSONField()  # Track changes in risks
    key_risk_indicators = models.JSONField()
    mitigation_strategies = models.JSONField()


# models.py or metrics.py
from pydantic import BaseModel, Field

class FinancialMetrics(BaseModel):
    revenue: float = Field(..., description="Total revenue of the company")
    cost_of_goods_sold: float = Field(..., description="Cost of goods sold")
    operating_expenses: float = Field(..., description="Total operating expenses")
    net_income: float = Field(..., description="Net income after all expenses")
    total_assets: float = Field(..., description="Total assets of the company")
    total_liabilities: float = Field(..., description="Total liabilities of the company")
    equity: float = Field(..., description="Total equity of the company")


from pydantic import BaseModel, Field

class PromptFormat(BaseModel):
    text_input: str = Field(..., description="The input prompt for the model")
    max_tokens: int = Field(..., description="The maximum number of tokens to generate")
    bad_words: str = Field("", description="Words to avoid in the generated output")
    stop_words: str = Field("", description="Words at which generation should stop")

    class Config:
        # Set extra validation options if needed
        extra = "forbid"


class TextGenerationRequest(models.Model):
    text_input = models.TextField()
    max_tokens = models.PositiveIntegerField()
    bad_words = models.TextField(blank=True, null=True)
    stop_words = models.TextField(blank=True, null=True)
    pad_id = models.IntegerField(default=2)
    end_id = models.IntegerField(default=2)

    def __str__(self):
        return f"Request: {self.text_input[:50]}..."

class ChatHistory(models.Model):
    user_input = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)