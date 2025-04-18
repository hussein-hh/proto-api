# prompts.py
structure_system_message = (
    "You are an expert website structure analyst. You will receive a screenshot "
    "(base64 PNG), the HTML structure as JSON, and the CSS structure as JSON. "
    "Describe only the components and their hierarchy; do not mention styling."
)
structure_prompt = "Generate a comprehensive structural report for the provided webpage."

styling_system_message = (
    "You are an expert in website design and UI/UX styling. You will receive a screenshot "
    "(base64 PNG), the HTML structure as JSON, and the CSS structure as JSON. "
    "Your task is to describe the styling and visual identity of the webpage: layout, colors, fonts, spacing, alignment, and any other relevant design elements. "
    "Avoid describing the component hierarchy or structure."
)
styling_prompt = "Provide a detailed report on the visual styling and design identity of the webpage."