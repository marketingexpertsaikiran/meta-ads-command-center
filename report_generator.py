from fpdf import FPDF

def generate_report(spend,ctr,cpc):

    pdf=FPDF()
    pdf.add_page()

    pdf.set_font("Arial",size=12)

    pdf.cell(200,10,"Meta Ads Report",ln=True)

    pdf.cell(200,10,f"Total Spend: {spend}",ln=True)
    pdf.cell(200,10,f"Average CTR: {ctr}",ln=True)
    pdf.cell(200,10,f"Average CPC: {cpc}",ln=True)

    pdf.output("report.pdf")

    return "report.pdf"
