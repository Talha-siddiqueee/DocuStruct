
from openpyxl import Workbook

from extractors.excel_extractor import ExcelExtractor


# Create sample workbook
workbook = Workbook()

# First sheet
sheet1 = workbook.active
sheet1.title = "Employees"

sheet1.append(["Name", "Age", "Department"])
sheet1.append(["John", 25, "IT"])
sheet1.append(["Sarah", 23, "HR"])
sheet1.append([None, None, None])
sheet1.append(["David", 28, "Finance"])


# Second sheet
sheet2 = workbook.create_sheet("Salaries")

sheet2.append(["Employee", "Salary"])
sheet2.append(["John", 50000])
sheet2.append(["Sarah", 45000])
sheet2.append(["David", 60000])


# Save workbook
workbook.save("sample.xlsx")


# Extract Excel data
extractor = ExcelExtractor("sample.xlsx")

result = extractor.extract_data()


# Display results
print("EXCEL EXTRACTION SUCCESSFUL")

print("File:", result["file_name"])

print("Total sheets:", result["total_sheets"])


for sheet in result["sheets"]:

    print("\nSheet:", sheet["sheet_name"])

    print("Total rows:", sheet["total_rows"])

    for row in sheet["data"]:

        print(row)
