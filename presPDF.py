from fpdf import FPDF


class PDF(FPDF):
    def add_nested_json_to_string(self, data, indent=0, result=""):
        for key, value in data.items():
            if isinstance(value, dict):
                result += f"\n{'                          ' * indent}{key}:\n"
                result = self.add_nested_json_to_string(value, indent + 1, result)
            else:
                result += f"{'                                        ' * indent}{key}: {value}\n"
        return result


def Pres(doc_name, data):
    # Create instance of FPDF class
    pdf = PDF()
    pdf.add_page()

    # Generate formatted string
    formatted_string = pdf.add_nested_json_to_string(data)

    # Write the string to the PDF

    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, "PROGNOSIFY REGISTERED DOCTOR PRESCRIPTION", align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", "BI", 14)
    pdf.multi_cell(0, 10, f'Prescribed by {doc_name}', align='C')
    pdf.ln(-5)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 10, formatted_string)

    # Output PDF
    pdf.output("output.pdf")
    return "output.pdf"
