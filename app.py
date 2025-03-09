import gradio as gr
import pandas as pd
import torch
import json
import re
import os
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import logging

# Configure logging for debugging (users can enable if needed)
logging.basicConfig(level=logging.INFO)

# Device and model configuration
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
logging.info(f"Using device: {device}")

model_name = "google/gemma-7b-it"  # Default model; users can change to any compatible model
tokenizer = AutoTokenizer.from_pretrained(model_name)

if device == "cuda":
    quant_config = BitsAndBytesConfig(load_in_4bit=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")
else:
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
logging.info("Model loaded successfully")

# Global variables for data state
current_df = pd.DataFrame()
original_df = pd.DataFrame()
last_ai_response = ""  # Store the latest AI response

def load_sheet(file, selected_sheet):
    """Load an Excel, CSV, or TSV file and return a preview and sheet names."""
    global current_df, original_df, last_ai_response
    if file is None:
        return pd.DataFrame({"Error": ["Please upload a file."]}), ["No file uploaded"], "No file uploaded"

    file_name = file.name if hasattr(file, 'name') else "Unknown file"
    file_extension = os.path.splitext(file_name)[1].lower()
    logging.info(f"Loading file: {file_name} (extension: {file_extension})")

    sheet_names = []
    current_sheet = "No file uploaded"
    try:
        if file_extension in ('.csv', '.tsv'):
            if file_extension == '.csv':
                current_df = pd.read_csv(file.name)
            else:  # .tsv
                current_df = pd.read_csv(file.name, sep='\t')
            sheet_names = ["No sheets available"]
            current_sheet = "No sheets available"
        elif file_extension in ('.xlsx', '.xls', '.xlsm', '.ods'):
            sheets = pd.read_excel(file.name, sheet_name=None)
            unique_sheet_names = list(set(sheets.keys()))
            sheet_names = ["ALL"] if "ALL" not in unique_sheet_names else []
            sheet_names.extend([name for name in unique_sheet_names if name != "ALL"])
            current_sheet = selected_sheet if selected_sheet in sheet_names else "ALL"
            if current_sheet == "ALL":
                current_df = pd.concat(
                    [df.assign(Sheet=name) for name, df in sheets.items()], ignore_index=True
                )
            else:
                current_df = sheets[current_sheet]
        else:
            return pd.DataFrame({"Error": [f"Unsupported file type: {file_extension}. Please upload a .csv, .tsv, .xlsx, .xls, .xlsm, or .ods file."]}), ["Unsupported file"], "Unsupported file"

        original_df = current_df.copy()
        last_ai_response = f"Loaded sheet successfully: {current_sheet}"
        logging.info(f"Loaded sheet(s): {current_sheet}")
        return current_df.head(20), sheet_names, current_sheet
    except Exception as e:
        logging.error(f"Sheet loading failed: {str(e)}")
        return pd.DataFrame({"Error": [f"Error loading file: {str(e)}. Ensure the file is a valid CSV, TSV, Excel, or ODS file."]}), sheet_names, current_sheet

def filter_data(question):
    """Process a natural language query to filter, sort, or aggregate data."""
    global current_df, last_ai_response

    if current_df.empty:
        last_ai_response = "Load a sheet first."
        return last_ai_response, pd.DataFrame()

    # Summarize DataFrame columns for the prompt or prompt
    column_summary = ""
    for col in current_df.columns:
        unique_vals = current_df[col].dropna().unique()[:5]
        vals_str = ", ".join([str(v) for v in unique_vals])
        column_summary += f"Column '{col}': sample values = [{vals_str}]\n"

    # Create prompt for the language model
    prompt = f"""
Given this summary of an Excel DataFrame:

{column_summary}

Convert this user request into structured JSON following this exact format:
{{
  "operations": [
    {{
      "type": "filter",
      "conditions": [
        {{"column": "ColumnName", "operator": "==", "value": "ExactValue"}},
        {{"column": "AnotherColumn", "operator": "in", "value": ["Value1", "Value2"]}},
        {{"column": "NumberColumn", "operator": ">", "value": 100}},
        {{"column": "TextColumn", "operator": "!=", "value": "ExcludeThis"}}
      ]
    }},
    {{
      "type": "sort",
      "columns": [
        {{"column": "ColumnName", "direction": "desc"}},
        {{"column": "AnotherColumn", "direction": "asc"}}
      ]
    }},
    {{
      "type": "select",
      "columns": ["ColumnName", "AnotherColumn"]
    }},
    {{
      "type": "aggregate",
      "calculations": [
        {{"function": "average", "column": "ColumnName"}},
        {{"function": "sum", "column": "AnotherColumn"}},
        {{"function": "max", "column": "ThirdColumn"}},
        {{"function": "min", "column": "FourthColumn"}}
      ]
    }}
  ]
}}

Rules:
- "operations" is a list of actions to perform in order on the current dataset.
- "filter" narrows rows:
  - "==" for exact match, "in" for multiple values, ">" or "<" for numbers, "!=" for exclusion.
  - Use "in" when the request lists multiple values for one column (e.g., "show X, Y, Z").
- "sort" orders rows: "desc" (highest to lowest), "asc" (lowest to highest).
  - Use "sort" for requests like "highest", "lowest", or "sort by".
- "select" picks columns to display: list the requested columns.
- "aggregate" calculates stats: "average", "sum", "max", "min" (e.g., "calculate average X").
- Match column names exactly as in the summary (case-sensitive).
- If the request implies working on the current filtered data, omit "filter" unless new conditions are specified.
- If no operation matches, return {{"operations": []}} and do nothing.
- Use only columns from the summary; guess the best column if ambiguous but log your choice.

User request: "{question}"

Return ONLY the JSON object, nothing else. Do not include explanations, extra text, or the prompt itself.
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=500, do_sample=False)
    raw_output = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    logging.info("Generated raw model output")

    # Extract JSON from the model's output
    prompt_end = raw_output.rindex("Return ONLY the JSON object, nothing else. Do not include explanations, extra text, or the prompt itself.") + len("Return ONLY the JSON object, nothing else. Do not include explanations, extra text, or the prompt itself.")
    json_part = raw_output[prompt_end:].strip()

    json_match = re.search(r'\{[\s\S]*\}', json_part)
    if not json_match:
        error_msg = "No valid JSON found in model output."
        logging.error(error_msg)
        last_ai_response = f"Error: {error_msg}\nRaw output: {raw_output}"
        return last_ai_response, current_df.head(20)

    json_content = json_match.group(0).strip()
    logging.info("Extracted JSON from model output")

    try:
        structured_json = json.loads(json_content)
        logging.info("Parsed JSON successfully")

        operations = structured_json.get("operations", [])
        result_df = current_df.copy()
        output_message = []
        aggregates = {}

        # Process each operation (filter, sort, select, aggregate)
        for op in operations:
            op_type = op["type"]

            if op_type == "filter":
                conditions = op.get("conditions", [])
                for cond in conditions:
                    col = cond["column"]
                    operator = cond["operator"]
                    val = cond["value"]

                    if col not in result_df.columns:
                        raise ValueError(f"Column '{col}' not found in DataFrame.")

                    if operator == "in":
                        if not isinstance(val, list):
                            raise ValueError("Operator 'in' requires a list of values.")
                        result_df = result_df[result_df[col].isin(val)]
                    elif operator == "==":
                        result_df = result_df[result_df[col] == val]
                    elif operator == ">":
                        result_df = result_df[result_df[col] > val]
                    elif operator == "<":
                        result_df = result_df[result_df[col] < val]
                    elif operator == "!=":
                        result_df = result_df[result_df[col] != val]
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")
                conditions_str = ' and '.join([f'{c["column"]} {c["operator"]} {c["value"]}' for c in conditions])
                output_message.append(f"Filtered by: {conditions_str}")

            elif op_type == "sort":
                columns = op.get("columns", [])
                sort_cols = [s["column"] for s in columns]
                sort_orders = [s["direction"] == "desc" for s in columns]
                for col in sort_cols:
                    if col not in result_df.columns:
                        raise ValueError(f"Sort column '{col}' not found in DataFrame.")
                result_df = result_df.sort_values(by=sort_cols, ascending=[not o for o in sort_orders])
                output_message.append(f"Sorted by: {', '.join([f'{s['column']} {'desc' if s['direction'] == 'desc' else 'asc'}' for s in columns])}")

            elif op_type == "select":
                columns = op.get("columns", [])
                for col in columns:
                    if col not in result_df.columns:
                        raise ValueError(f"Column '{col}' not found in DataFrame.")
                result_df = result_df[columns]
                output_message.append(f"Selected columns: {', '.join(columns)}")

            elif op_type == "aggregate":
                calculations = op.get("calculations", [])
                for calc in calculations:
                    func = calc["function"]
                    col = calc["column"]
                    if col not in result_df.columns:
                        raise ValueError(f"Column '{col}' not found in DataFrame.")
                    if func == "average":
                        aggregates[f"{col}_avg"] = result_df[col].mean()
                    elif func == "sum":
                        aggregates[f"{col}_sum"] = result_df[col].sum()
                    elif func == "max":
                        aggregates[f"{col}_max"] = result_df[col].max()
                    elif func == "min":
                        aggregates[f"{col}_min"] = result_df[col].min()
                    else:
                        raise ValueError(f"Unsupported function: {func}")
                output_message.append(f"Aggregates: {', '.join([f'{k}: {v}' for k, v in aggregates.items()])}")

        current_df = result_df
        if not output_message:
            output_message.append("No operations applied.")
        
        logging.info(f"Operations applied: {'; '.join(output_message)}")
        if aggregates:
            last_ai_response = f"Operations successful: {'; '.join(output_message)}\nAggregates: {aggregates}"
            return last_ai_response, current_df.head(20)
        last_ai_response = f"Operations successful: {'; '.join(output_message)}"
        return last_ai_response, current_df.head(20)

    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing failed: {str(e)}")
        last_ai_response = f"Error parsing JSON:\n{json_content}\nDetails: {str(e)}"
        return last_ai_response, current_df.head(20)
    except Exception as e:
        logging.error(f"Operation failed: {str(e)}")
        last_ai_response = f"Error applying operations:\n{json_content}\nDetails: {str(e)}"
        return last_ai_response, current_df.head(20)

def export_data(format_choice):
    """Export the processed data to Excel or CSV with the AI response."""
    global current_df, last_ai_response
    if current_df.empty:
        return "No data to export.", None

    output_folder = "output"  # Configurable output folder
    os.makedirs(output_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if format_choice.lower() == "excel":
        filename = f"export_{timestamp}.xlsx"
        full_path = os.path.join(output_folder, filename)
        try:
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                current_df.to_excel(writer, sheet_name='Data', index=False)
                summary_data = []
                summary_data.append(["AI Response", last_ai_response])
                if "Aggregates:" in last_ai_response:
                    summary_data.append([])
                    summary_data.append(["Aggregates Table", ""])
                    summary_data.append(["Metric", "Value"])
                    aggregates_start = last_ai_response.find("Aggregates: {")
                    if aggregates_start != -1:
                        aggregates_str = last_ai_response[aggregates_start + 11:].strip()
                        aggregates = eval(aggregates_str.split('\n')[0])
                        for metric, value in aggregates.items():
                            summary_data.append([metric, value])
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)
            return f"Data exported to {full_path}", full_path
        except Exception as e:
            logging.error(f"Excel export failed: {str(e)}")
            return f"Error exporting to Excel: {str(e)}", None
    elif format_choice.lower() == "csv":
        filename = f"export_{timestamp}.csv"
        full_path = os.path.join(output_folder, filename)
        try:
            with open(full_path, 'w', newline='') as f:
                f.write(f"# AI Response:\n")
                f.write(f"# {last_ai_response.replace('\n', '\n# ')}\n")
                current_df.to_csv(f, index=False)
                if "Aggregates:" in last_ai_response:
                    f.write("# Aggregates:\n")
                    aggregates_start = last_ai_response.find("Aggregates: {")
                    if aggregates_start != -1:
                        aggregates_str = last_ai_response[aggregates_start + 11:].strip()
                        aggregates = eval(aggregates_str.split('\n')[0])
                        for metric, value in aggregates.items():
                            f.write(f"# {metric},{value}\n")
            return f"Data exported to {full_path}", full_path
        except Exception as e:
            logging.error(f"CSV export failed: {str(e)}")
            return f"Error exporting to CSV: {str(e)}", None
    else:
        return "Invalid format selected. Choose 'Excel' or 'CSV'.", None

def reset_data():
    """Reset the current data to the original uploaded dataset."""
    global current_df, original_df, last_ai_response
    if original_df.empty:
        last_ai_response = "No data loaded to reset."
        return last_ai_response, pd.DataFrame()
    current_df = original_df.copy()
    last_ai_response = "Reset to full dataset."
    return last_ai_response, current_df.head(20)

# Gradio UI setup
with gr.Blocks() as app:
    gr.Markdown("## Intelligent Excel Analyzer with Gemma-7B 📊🤖")
    gr.Markdown("Gemma-7B-Driven Excel/CSV Analyzer: Filter, Sort, Aggregate, Export with Natural Language")
    with gr.Row():
        file_input = gr.File(label="Upload Excel or CSV File")
        sheet_state = gr.State(value=["No file uploaded"])
        current_sheet = gr.State(value="No file uploaded")
        sheet_dropdown = gr.Dropdown(
            choices=["No file uploaded"],
            label="Sheet Name",
            value="No file uploaded",
            interactive=True
        )
        load_btn = gr.Button("Load Sheet")
    data_preview = gr.DataFrame(label="Data Preview (20 rows)")
    filter_input = gr.Textbox(label="Enter your request (e.g., 'show items X, Y', 'sort Price desc', 'average Quantity')")
    with gr.Row():
        filter_btn = gr.Button("Process Request")
        reset_btn = gr.Button("Reset to Full Data")
        export_btn = gr.Button("Export Results")
    export_format = gr.Dropdown(choices=["Excel", "CSV"], label="Export Format", value="Excel")
    ai_response = gr.Textbox(label="AI Response")
    export_file = gr.File(label="Download Exported Data")

    load_btn.click(
        load_sheet,
        inputs=[file_input, sheet_dropdown],
        outputs=[data_preview, sheet_state, current_sheet]
    ).then(
        lambda sheets, current: gr.update(choices=["ALL"] + [s for s in sheets if s not in ["No file uploaded", "No sheets available", "Unsupported file"] and s != "ALL"] if sheets else ["No file uploaded"], value=current),
        inputs=[sheet_state, current_sheet],
        outputs=[sheet_dropdown]
    )
    filter_btn.click(filter_data, inputs=filter_input, outputs=[ai_response, data_preview])
    reset_btn.click(reset_data, inputs=None, outputs=[ai_response, data_preview])
    export_btn.click(export_data, inputs=export_format, outputs=[ai_response, export_file])

app.launch()  # Removed debug=True for production