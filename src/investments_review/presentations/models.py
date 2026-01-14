from llama_cloud.types.classifier.classifier_rule_param import ClassifierRuleParam
from pydantic import BaseModel, Field

rules: list[ClassifierRuleParam] = [
    {
        "type": "management_presentation",
        "description": "A slide deck prepared by a company's management team to present operational performance, strategic initiatives, and key metrics to external parties such as investors, potential acquirers, or analysts. Typically promotional in tone and focused on highlighting growth opportunities, achievements, and the company’s value proposition.",
    },
    {
        "type": "board_update_deck",
        "description": "An internal slide deck prepared to inform the company's board of directors about current operations, financial performance, risks, and strategic decisions. Focused on accurate reporting, governance, and decision support rather than promotion, often including sensitive internal metrics and risk assessments.",
    },
]


class ManagementPresentation(BaseModel):
    company_name: str = Field(description="Name of the company being presented")
    presentation_date: str = Field(
        description="Date the presentation was created or delivered (ISO string)"
    )
    key_metrics: list[str] = Field(
        description="Top KPIs or metrics highlighted, e.g., revenue growth, EBITDA"
    )
    strategic_goals: list[str] = Field(
        description="List of strategic initiatives or growth plans"
    )
    target_audience: str = Field(
        description="Intended audience, e.g., investors or acquirers"
    )

    def to_string(self) -> str:
        return (
            f"Management Presentation for {self.company_name} (Date: {self.presentation_date})\n"
            f"Target Audience: {self.target_audience}\n"
            f"Key Metrics: {', '.join(self.key_metrics)}\n"
            f"Strategic Goals: {', '.join(self.strategic_goals)}"
        )


class FinancialSummary(BaseModel):
    revenue: float = Field(description="Revenue as reported in the board update deck")
    expenses: float = Field(description="Expenses as reported in the board update deck")
    net_profit: float = Field(
        description="Net profit as reported in the board update deck"
    )

    def to_string(self) -> str:
        return (
            f"Revenue: ${self.revenue:,.2f}, "
            f"Expenses: ${self.expenses:,.2f}, "
            f"Net Profit: ${self.net_profit:,.2f}"
        )


class BoardUpdateDeck(BaseModel):
    company_name: str = Field(description="Name of the company")
    reporting_period_start: str = Field(
        description="Start of the reporting period (ISO string)"
    )
    reporting_period_end: str = Field(
        description="End of the reporting period (ISO string)"
    )
    risks_and_issues: list[str] = Field(
        description="Key risks, challenges, or operational issues"
    )
    financial_summary: FinancialSummary = Field(
        description="Summary of financial performance for what concerns revenue, expenses, net profit",
    )

    def to_string(self) -> str:
        return (
            f"Board Update Deck for {self.company_name} "
            f"(Reporting Period: {self.reporting_period_start} to {self.reporting_period_end})\n"
            f"Risks and Issues: {', '.join(self.risks_and_issues)}\n"
            f"Financial Summary: {self.financial_summary.to_string()}"
        )
