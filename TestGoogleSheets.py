credentials_path = r'C:\Users\aidan\PycharmProjects\RandomProjects2\TAModBot\team-australia-admin-db24c213971f.json'
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.service_account(filename=credentials_path)
spreadsheet = client.create('FilteredMembersUSA')
rows, cols = filtered_members.shape
spreadsheet.add_worksheet('AllMembers', rows=rows + 1, cols=cols)
spreadsheet.add_worksheet('ByAdmin', rows=rows + 1, cols=cols)  # TODO

worksheet = spreadsheet.sheet1
worksheet.clear()
worksheet.update([filtered_members.columns.values.tolist()] + filtered_members.values.tolist())
print(spreadsheet.url)