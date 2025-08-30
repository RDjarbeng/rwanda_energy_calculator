# netlify/functions/app.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from fasthtml.common import *

# Constants
VAT = 0.18
TIER_1, TIER_2, TIER_3 = 89, 212, 249
TIER_1_LIMIT, TIER_2_LIMIT = 15, 35

def calculateAmountFromUnits(units: float) -> tuple[float, dict]:
    """Calculate amount and return detailed breakdown"""
    if units < 0:
        raise ValueError("Units cannot be negative")
    
    # Calculate tier usage
    t1 = units if units <= TIER_1_LIMIT else TIER_1_LIMIT
    t2 = 0 if units <= TIER_1_LIMIT else min(units - TIER_1_LIMIT, TIER_2_LIMIT - TIER_1_LIMIT)
    t3 = 0 if units <= TIER_2_LIMIT else units - TIER_2_LIMIT
    
    # Calculate costs before VAT
    t1_cost = t1 * TIER_1
    t2_cost = t2 * TIER_2
    t3_cost = t3 * TIER_3
    subtotal = t1_cost + t2_cost + t3_cost
    vat_amount = subtotal * VAT
    total = subtotal + vat_amount
    
    breakdown = {
        'tier1_units': t1,
        'tier2_units': t2,
        'tier3_units': t3,
        'tier1_cost': t1_cost,
        'tier2_cost': t2_cost,
        'tier3_cost': t3_cost,
        'subtotal': subtotal,
        'vat_amount': vat_amount,
        'total': round(total, 2)
    }
    
    return round(total, 2), breakdown

def calculateUnitsFromAmount(amount: float, initial_amount: float = 0) -> tuple[float, dict]:
    """Calculate units and return detailed breakdown"""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if initial_amount < 0:
        raise ValueError("Initial amount cannot be negative")
    
    # Add initial amount to total available
    total_available = amount + initial_amount
    
    # Remove VAT first to get subtotal
    subtotal = total_available / (1 + VAT)
    
    TIER_1_COST_LIMIT = TIER_1_LIMIT * TIER_1
    TIER_2_COST_LIMIT = TIER_1_COST_LIMIT + (TIER_2_LIMIT - TIER_1_LIMIT) * TIER_2
    
    if subtotal <= TIER_1_COST_LIMIT:
        # Only tier 1
        units = subtotal / TIER_1
        t1, t2, t3 = units, 0, 0
    elif subtotal <= TIER_2_COST_LIMIT:
        # Tier 1 + some tier 2
        t1 = TIER_1_LIMIT
        t2 = (subtotal - TIER_1_COST_LIMIT) / TIER_2
        t3 = 0
        units = t1 + t2
    else:
        # All tiers
        t1 = TIER_1_LIMIT
        t2 = TIER_2_LIMIT - TIER_1_LIMIT
        t3 = (subtotal - TIER_2_COST_LIMIT) / TIER_3
        units = t1 + t2 + t3
    
    # Calculate breakdown
    t1_cost = t1 * TIER_1
    t2_cost = t2 * TIER_2
    t3_cost = t3 * TIER_3
    calc_subtotal = t1_cost + t2_cost + t3_cost
    vat_amount = calc_subtotal * VAT
    
    breakdown = {
        'tier1_units': round(t1, 2),
        'tier2_units': round(t2, 2),
        'tier3_units': round(t3, 2),
        'tier1_cost': round(t1_cost, 2),
        'tier2_cost': round(t2_cost, 2),
        'tier3_cost': round(t3_cost, 2),
        'subtotal': round(calc_subtotal, 2),
        'vat_amount': round(vat_amount, 2),
        'total': round(total_available, 2),
        'initial_amount': initial_amount,
        'new_amount': amount
    }
    
    return round(units, 2), breakdown

# FastHTML app setup with default Pico CSS
app, rt = fast_app(pico=True, tailwind=False)

def create_breakdown_table(breakdown: dict, is_from_units: bool = True):
    """Create a detailed breakdown table"""
    table_content = [
        Article(
            H4("Tier Breakdown"),
            Table(
                Thead(
                    Tr(
                        Th("Tier"),
                        Th("Rate (RWF/kWh)"),
                        Th("Units Used"),
                        Th("Cost (RWF)")
                    )
                ),
                Tbody(
                    Tr(
                        Td("Tier 1 (0-15 kWh)"),
                        Td(f"{TIER_1}"),
                        Td(f"{breakdown['tier1_units']:.2f}"),
                        Td(f"{breakdown['tier1_cost']:.2f}")
                    ) if breakdown['tier1_units'] > 0 else None,
                    Tr(
                        Td("Tier 2 (15-35 kWh)"),
                        Td(f"{TIER_2}"),
                        Td(f"{breakdown['tier2_units']:.2f}"),
                        Td(f"{breakdown['tier2_cost']:.2f}")
                    ) if breakdown['tier2_units'] > 0 else None,
                    Tr(
                        Td("Tier 3 (35+ kWh)"),
                        Td(f"{TIER_3}"),
                        Td(f"{breakdown['tier3_units']:.2f}"),
                        Td(f"{breakdown['tier3_cost']:.2f}")
                    ) if breakdown['tier3_units'] > 0 else None,
                    Tr(
                        Td(Strong("Subtotal")),
                        Td(""),
                        Td(""),
                        Td(Strong(f"{breakdown['subtotal']:.2f}"))
                    ),
                    Tr(
                        Td(f"VAT ({VAT*100}%)"),
                        Td(""),
                        Td(""),
                        Td(f"{breakdown['vat_amount']:.2f}")
                    ),
                    Tr(
                        Td(Strong("Total")),
                        Td(""),
                        Td(""),
                        Td(Strong(f"{breakdown['total']:.2f}"))
                    )
                )
            )
        )
    ]
    
    # Add payment breakdown if applicable (for units from amount with initial payment)
    if 'initial_amount' in breakdown and breakdown['initial_amount'] > 0:
        table_content.append(
            Article(
                H4("Payment Summary"),
                Table(
                    Tbody(
                        Tr(
                            Td("Initial Payment:"),
                            Td(f"{breakdown['initial_amount']:.2f} RWF")
                        ),
                        Tr(
                            Td("New Payment:"),
                            Td(f"{breakdown['new_amount']:.2f} RWF")
                        ),
                        Tr(
                            Td(Strong("Total Available:")),
                            Td(Strong(f"{breakdown['total']:.2f} RWF"))
                        )
                    )
                )
            )
        )
    
    return Div(*table_content)

@rt('/')
def get():
    return Title('Rwanda Electricity Calculator'), Main(
        Header(
            H1('Rwanda Energy Group Calculator'),
            P('Calculate electricity costs and units with detailed tier breakdown'),
            P(A('View Official REG Tariffs', href='https://www.reg.rw/customer-service/tariffs/', target='_blank'))
        ),
        
        Section(
            H2('Calculate Units from Cost'),
            Form(
                Div(
                    Label('Enter amount (RWF):', For='amount-input'),
                    Input(
                        type='number', 
                        id='amount-input',
                        name='amount', 
                        placeholder='0.00', 
                        min='0', 
                        step='0.01',
                        hx_get='/calculate-units-live',
                        hx_trigger='input changed delay:300ms',
                        hx_target='#units-result',
                        hx_include='this, #initial-amount-input',
                        style='max-width: 300px;'
                    ),
                    Small('Enter the amount you want to spend on electricity')
                ),
                Div(
                    Label('Initial payment already made (optional):', For='initial-amount-input'),
                    Input(
                        type='number', 
                        id='initial-amount-input',
                        name='initial_amount', 
                        placeholder='0.00', 
                        min='0', 
                        step='0.01',
                        hx_get='/calculate-units-live',
                        hx_trigger='input changed delay:300ms',
                        hx_target='#units-result',
                        hx_include='#amount-input, this',
                        style='max-width: 300px;'
                    ),
                    Small('Enter any amount already paid at the beginning of the month')
                )
            ),
            Div(id='units-result', cls='result-container')
        ),
        
        Hr(),
        
        Section(
            H2('Calculate Cost from Units'),
            Form(
                Div(
                    Label('Enter units (kWh):', For='units-input'),
                    Input(
                        type='number', 
                        id='units-input',
                        name='units', 
                        placeholder='0.00', 
                        min='0', 
                        step='0.01',
                        hx_get='/calculate-cost-live',
                        hx_trigger='input changed delay:300ms',
                        hx_target='#cost-result',
                        hx_include='this',
                        style='max-width: 300px;'
                    ),
                    Small('Enter the number of kilowatt-hours (kWh) consumed')
                )
            ),
            Div(id='cost-result', cls='result-container')
        ),
        
        Style("""
            .result-container {
                margin-top: 1rem;
                padding: 1rem;
                background-color: var(--background-color);
                border: 1px solid var(--muted-border-color);
                border-radius: var(--border-radius);
            }
            
            .highlight {
                background-color: var(--primary-background);
                padding: 0.5rem;
                border-radius: var(--border-radius);
                margin: 0.5rem 0;
            }
            
            table {
                margin-top: 1rem;
            }
            
            .error {
                color: var(--del-color);
                background-color: var(--del-background);
                padding: 0.5rem;
                border-radius: var(--border-radius);
            }
            
            form > div {
                margin-bottom: 1rem;
            }
        """)
    )

@rt('/calculate-cost-live')
def get(units: str = ""):
    if not units or units == "":
        return Div()
    
    try:
        units_val = float(units)
        
        if units_val == 0:
            return Div()
            
        result, breakdown = calculateAmountFromUnits(units_val)
        
        return Div(
            Div(
                H3("Result"),
                P(f"{units_val} kWh = {result} RWF", cls='highlight'),
                cls='result-summary'
            ),
            create_breakdown_table(breakdown)
        )
    except (ValueError, TypeError) as e:
        return Div(P(f"Invalid input: Please enter a valid number", cls='error'))

@rt('/calculate-units-live')
def get(amount: str = "", initial_amount: str = ""):
    if not amount or amount == "":
        return Div()
    
    try:
        amount_val = float(amount)
        initial_val = float(initial_amount) if initial_amount and initial_amount != "" else 0
        
        if amount_val == 0:
            return Div()
            
        result, breakdown = calculateUnitsFromAmount(amount_val, initial_val)
        
        result_text = f"{result} kWh"
        if initial_val > 0:
            result_text += f" (Total: {breakdown['total']} RWF = {initial_val} + {amount_val})"
        else:
            result_text += f" = {amount_val} RWF"
        
        return Div(
            Div(
                H3("Result"),
                P(result_text, cls='highlight'),
                cls='result-summary'
            ),
            create_breakdown_table(breakdown, False)
        )
    except (ValueError, TypeError) as e:
        return Div(P(f"Invalid input: Please enter valid numbers", cls='error'))

# Netlify handler
def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)