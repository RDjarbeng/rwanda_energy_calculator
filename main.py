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
        'total': round(total, 2),
        'total_units': units
    }
    
    return round(total, 2), breakdown

def calculateUnitsFromAmount(amount: float, initial_amount: float = 0) -> tuple[float, dict]:
    """Calculate units and return detailed breakdown"""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if initial_amount < 0:
        raise ValueError("Initial amount cannot be negative")
    
    # Calculate breakdown for initial payment if it exists
    initial_breakdown = None
    initial_units = 0
    if initial_amount > 0:
        initial_units, initial_breakdown = calculateAmountFromUnits_reverse(initial_amount)
    
    # Calculate what new payment can buy, considering existing tier usage
    new_breakdown = None
    new_units = 0
    if amount > 0:
        new_units, new_breakdown = calculateAmountFromUnits_withOffset(amount, initial_units)
    
    # Calculate total
    total_units = initial_units + new_units
    total_available = amount + initial_amount
    
    # Calculate combined tier usage for total breakdown
    total_result, total_breakdown = calculateAmountFromUnits_reverse(total_available)
    
    breakdown = {
        'tier1_units': total_breakdown['tier1_units'],
        'tier2_units': total_breakdown['tier2_units'],
        'tier3_units': total_breakdown['tier3_units'],
        'tier1_cost': total_breakdown['tier1_cost'],
        'tier2_cost': total_breakdown['tier2_cost'],
        'tier3_cost': total_breakdown['tier3_cost'],
        'subtotal': total_breakdown['subtotal'],
        'vat_amount': total_breakdown['vat_amount'],
        'total': round(total_available, 2),
        'initial_amount': initial_amount,
        'new_amount': amount,
        'total_units': round(total_units, 2),
        'initial_breakdown': initial_breakdown,
        'new_breakdown': new_breakdown,
        'has_both_payments': initial_amount > 0 and amount > 0
    }
    
    return round(total_units, 2), breakdown

def calculateAmountFromUnits_reverse(amount: float) -> tuple[float, dict]:
    """Helper function to calculate units from amount (reverse of calculateAmountFromUnits)"""
    if amount <= 0:
        return 0, {'tier1_units': 0, 'tier2_units': 0, 'tier3_units': 0, 'tier1_cost': 0, 'tier2_cost': 0, 'tier3_cost': 0, 'subtotal': 0, 'vat_amount': 0, 'total': 0}
    
    # Remove VAT first to get subtotal
    subtotal = amount / (1 + VAT)
    
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
        'total': round(amount, 2),
        'total_units': round(units, 2)
    }
    
    return round(units, 2), breakdown

def calculateAmountFromUnits_withOffset(amount: float, existing_units: float) -> tuple[float, dict]:
    """Calculate what new amount can buy considering existing tier usage"""
    if amount <= 0:
        return 0, {'tier1_units': 0, 'tier2_units': 0, 'tier3_units': 0, 'tier1_cost': 0, 'tier2_cost': 0, 'tier3_cost': 0, 'subtotal': 0, 'vat_amount': 0, 'total': 0}
    
    # Remove VAT first to get subtotal
    subtotal = amount / (1 + VAT)
    
    # Determine where we start based on existing units
    remaining_t1 = max(0, TIER_1_LIMIT - existing_units)
    remaining_t2 = max(0, TIER_2_LIMIT - existing_units) if existing_units < TIER_2_LIMIT else 0
    
    t1_new = t2_new = t3_new = 0
    remaining_subtotal = subtotal
    
    # Fill tier 1 first if there's remaining capacity
    if remaining_t1 > 0 and remaining_subtotal > 0:
        t1_cost_available = remaining_subtotal
        t1_units_affordable = t1_cost_available / TIER_1
        t1_new = min(remaining_t1, t1_units_affordable)
        remaining_subtotal -= t1_new * TIER_1
    
    # Fill tier 2 if there's remaining capacity and budget
    if remaining_t2 > 0 and remaining_subtotal > 0:
        t2_cost_available = remaining_subtotal
        t2_units_affordable = t2_cost_available / TIER_2
        t2_new = min(remaining_t2, t2_units_affordable)
        remaining_subtotal -= t2_new * TIER_2
    
    # Fill tier 3 with remaining budget
    if remaining_subtotal > 0:
        t3_new = remaining_subtotal / TIER_3
    
    new_units = t1_new + t2_new + t3_new
    
    # Calculate breakdown
    t1_cost = t1_new * TIER_1
    t2_cost = t2_new * TIER_2
    t3_cost = t3_new * TIER_3
    calc_subtotal = t1_cost + t2_cost + t3_cost
    vat_amount = calc_subtotal * VAT
    
    breakdown = {
        'tier1_units': round(t1_new, 2),
        'tier2_units': round(t2_new, 2),
        'tier3_units': round(t3_new, 2),
        'tier1_cost': round(t1_cost, 2),
        'tier2_cost': round(t2_cost, 2),
        'tier3_cost': round(t3_cost, 2),
        'subtotal': round(calc_subtotal, 2),
        'vat_amount': round(vat_amount, 2),
        'total': round(amount, 2),
        'total_units': round(new_units, 2)
    }
    
    return round(new_units, 2), breakdown

# FastHTML app setup with default Pico CSS
app, rt = fast_app(pico=True, tailwind=False)

def create_breakdown_table(breakdown: dict, is_from_units: bool = True):
    """Create a detailed breakdown table"""
    
    # If we have both payments, show separate breakdowns
    if breakdown.get('has_both_payments', False):
        return create_dual_breakdown_table(breakdown)
    
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
                        Td(Strong("Subtotal (Units)")),
                        Td(""),
                        Td(Strong(f"{breakdown['total_units']:.2f} kWh")),
                        Td("")
                    ),
                    Tr(
                        Td(Strong("Subtotal (Cost)")),
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
    if 'initial_amount' in breakdown and breakdown['initial_amount'] > 0 and not breakdown.get('has_both_payments', False):
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

def create_dual_breakdown_table(breakdown: dict):
    """Create separate breakdown tables for initial and new payments"""
    tables = []
    
    # Payment Summary first
    tables.append(
        Article(
            H4("Payment Summary"),
            Table(
                Tbody(
                    Tr(
                        Td("Initial Payment:"),
                        Td(f"{breakdown['initial_amount']:.2f} RWF"),
                        Td(f"→ {breakdown['initial_breakdown']['total_units']:.2f} kWh")
                    ),
                    Tr(
                        Td("New Payment:"),
                        Td(f"{breakdown['new_amount']:.2f} RWF"),
                        Td(f"→ {breakdown['new_breakdown']['total_units']:.2f} kWh")
                    ),
                    Tr(
                        Td(Strong("Total:")),
                        Td(Strong(f"{breakdown['total']:.2f} RWF")),
                        Td(Strong(f"→ {breakdown['total_units']:.2f} kWh"))
                    )
                )
            )
        )
    )
    
     # New Payment Breakdown
    if breakdown['new_breakdown'] and breakdown['new_amount'] > 0:
        new = breakdown['new_breakdown']
        tables.append(
            Article(
                H4("New Payment Tier Breakdown"),
                Table(
                    Thead(
                        Tr(
                            Th("Tier"),
                            Th("Rate (RWF/kWh)"),
                            Th("Units Added"),
                            Th("Cost (RWF)")
                        )
                    ),
                    Tbody(
                        Tr(
                            Td("Tier 1 (0-15 kWh)"),
                            Td(f"{TIER_1}"),
                            Td(f"{new['tier1_units']:.2f}"),
                            Td(f"{new['tier1_cost']:.2f}")
                        ) if new['tier1_units'] > 0 else None,
                        Tr(
                            Td("Tier 2 (15-35 kWh)"),
                            Td(f"{TIER_2}"),
                            Td(f"{new['tier2_units']:.2f}"),
                            Td(f"{new['tier2_cost']:.2f}")
                        ) if new['tier2_units'] > 0 else None,
                        Tr(
                            Td("Tier 3 (35+ kWh)"),
                            Td(f"{TIER_3}"),
                            Td(f"{new['tier3_units']:.2f}"),
                            Td(f"{new['tier3_cost']:.2f}")
                        ) if new['tier3_units'] > 0 else None,
                        Tr(
                            Td(Strong("Subtotal (Units)")),
                            Td(""),
                            Td(Strong(f"{new['total_units']:.2f} kWh")),
                            Td("")
                        ),
                        Tr(
                            Td(Strong("Subtotal (Cost)")),
                            Td(""),
                            Td(""),
                            Td(Strong(f"{new['subtotal']:.2f}"))
                        ),
                        Tr(
                            Td(f"VAT ({VAT*100}%)"),
                            Td(""),
                            Td(""),
                            Td(f"{new['vat_amount']:.2f}")
                        ),
                        Tr(
                            Td(Strong("Total")),
                            Td(""),
                            Td(""),
                            Td(Strong(f"{new['total']:.2f}"))
                        )
                    )
                )
            )
        )
   

    # Initial Payment Breakdown
    if breakdown['initial_breakdown'] and breakdown['initial_amount'] > 0:
        initial = breakdown['initial_breakdown']
        tables.append(
            Article(
                H4("Initial Payment Tier Breakdown"),
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
                            Td(f"{initial['tier1_units']:.2f}"),
                            Td(f"{initial['tier1_cost']:.2f}")
                        ) if initial['tier1_units'] > 0 else None,
                        Tr(
                            Td("Tier 2 (15-35 kWh)"),
                            Td(f"{TIER_2}"),
                            Td(f"{initial['tier2_units']:.2f}"),
                            Td(f"{initial['tier2_cost']:.2f}")
                        ) if initial['tier2_units'] > 0 else None,
                        Tr(
                            Td("Tier 3 (35+ kWh)"),
                            Td(f"{TIER_3}"),
                            Td(f"{initial['tier3_units']:.2f}"),
                            Td(f"{initial['tier3_cost']:.2f}")
                        ) if initial['tier3_units'] > 0 else None,
                        Tr(
                            Td(Strong("Subtotal (Units)")),
                            Td(""),
                            Td(Strong(f"{initial['total_units']:.2f} kWh")),
                            Td("")
                        ),
                        Tr(
                            Td(Strong("Subtotal (Cost)")),
                            Td(""),
                            Td(""),
                            Td(Strong(f"{initial['subtotal']:.2f}"))
                        ),
                        Tr(
                            Td(f"VAT ({VAT*100}%)"),
                            Td(""),
                            Td(""),
                            Td(f"{initial['vat_amount']:.2f}")
                        ),
                        Tr(
                            Td(Strong("Total")),
                            Td(""),
                            Td(""),
                            Td(Strong(f"{initial['total']:.2f}"))
                        )
                    )
                )
            )
        )
    
    
    # Combined Total Breakdown
    tables.append(
        Article(
            H4("Combined Total Breakdown"),
            Table(
                Thead(
                    Tr(
                        Th("Tier"),
                        Th("Rate (RWF/kWh)"),
                        Th("Total Units"),
                        Th("Total Cost (RWF)")
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
                        Td(Strong("Grand Total (Units)")),
                        Td(""),
                        Td(Strong(f"{breakdown['total_units']:.2f} kWh")),
                        Td("")
                    ),
                    Tr(
                        Td(Strong("Grand Total (Cost)")),
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
                        Td(Strong("Final Total")),
                        Td(""),
                        Td(""),
                        Td(Strong(f"{breakdown['total']:.2f}"))
                    )
                )
            )
        )
    )
    
    return Div(*tables)

@rt('/')
def get():
    return Title('Rwanda Electricity Calculator'), Main(
        Header(
            H1('Rwanda Energy Group Calculator'),
            P('Calculate electricity costs and units with detailed tier breakdown'),
            P(A('View Official REG Tariffs', href='https://www.reg.rw/customer-service/tariffs/', target='_blank')),
            P(A('See this announcement for new tariffs', href='https://rdjarbeng.com/rura-announces-revised-electricity-end-user-tariffs-effective-october-2025/', target='_blank'))
        ),
        
        Div(
            Div(
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
                        )
                    ),
                    cls='input-section'
                ),
                
                Div(
                    Div(id='units-result', cls='result-container'),
                    Div(id='cost-result', cls='result-container'),
                    cls='results-section'
                ),
                cls='calculator-container'
            ),
            cls='main-container'
        ),
        
        Style("""
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .calculator-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                align-items: start;
            }
            
            .input-section {
                background-color: var(--background-color);
                padding: 1.5rem;
                border-radius: var(--border-radius);
                border: 1px solid var(--muted-border-color);
            }
            
            .results-section {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            
            .result-container {
                padding: 1rem;
                background-color: var(--background-color);
                border: 1px solid var(--muted-border-color);
                border-radius: var(--border-radius);
                min-height: 100px;
            }
            
            .result-container:empty {
                display: none;
            }
            
            .highlight {
                background-color: var(--primary-background);
                padding: 0.75rem;
                border-radius: var(--border-radius);
                margin: 0.5rem 0;
                font-size: 1.1em;
                font-weight: bold;
            }
            
            table {
                margin-top: 1rem;
                width: 100%;
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
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .calculator-container {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .input-section {
                    padding: 1rem;
                }
                
                .main-container {
                    padding: 0 1rem;
                }
            }
            
            /* Ensure tables look good */
            table th, table td {
                text-align: left;
                padding: 0.5rem;
            }
            
            table th:last-child, table td:last-child {
                text-align: right;
            }
            
            table th:nth-child(2), table td:nth-child(2) {
                text-align: center;
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
                H3("Cost Calculation Result"),
                P(f"{units_val} kWh = {result} RWF", cls='highlight'),
                cls='result-summary'
            ),
            create_breakdown_table(breakdown)
        )
    except (ValueError, TypeError) as e:
        return Div(P(f"Invalid input: Please enter a valid number", cls='error'))

@rt('/calculate-units-live')
def get(amount: str = "", initial_amount: str = ""):
    # Show calculation even if only initial_amount is provided
    if (not amount or amount == "") and (not initial_amount or initial_amount == ""):
        return Div()
    
    try:
        amount_val = float(amount) if amount and amount != "" else 0
        initial_val = float(initial_amount) if initial_amount and initial_amount != "" else 0
        
        # Show result if either amount or initial amount has a value
        if amount_val == 0 and initial_val == 0:
            return Div()
            
        result, breakdown = calculateUnitsFromAmount(amount_val, initial_val)
        
        # Create result text based on what was entered
        if initial_val > 0 and amount_val > 0:
            result_text = f"{result} kWh (Total: {breakdown['total']} RWF = {initial_val} + {amount_val})"
            title = "Units Calculation Result"
        elif initial_val > 0 and amount_val == 0:
            result_text = f"{result} kWh from initial payment of {initial_val} RWF"
            title = "Units from Initial Payment"
        else:
            result_text = f"{result} kWh = {amount_val} RWF"
            title = "Units Calculation Result"
        
        return Div(
            Div(
                H3(title),
                P(result_text, cls='highlight'),
                cls='result-summary'
            ),
            create_breakdown_table(breakdown, False)
        )
    except (ValueError, TypeError) as e:
        return Div(P(f"Invalid input: Please enter valid numbers", cls='error'))

if __name__ == '__main__':
    serve()